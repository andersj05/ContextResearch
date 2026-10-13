"""Resume the fixed DAG; unknown calls stop their own jobs, not independent work."""
from concurrent.futures import ThreadPoolExecutor, wait, FIRST_COMPLETED
from copy import deepcopy
from pathlib import Path
import threading
import time

from .engine import run_prefix, run_episode
from ..rollback_development_v5.common import save_new, sha
from ..rollback_development_v5.engine import apply_intervention
from ..rollback_development_v5.contexts import actor_state, render, fits


def calls_for_job(job, calls):
    arms = {job["arm"]} | ({"shared"} if job["arm"] == "prefix" else set())
    return [c for c in calls if c["identity"]["task_id"] == job["task_id"]
            and c["identity"]["track"] == job["track"] and c["identity"]["arm"] in arms]


def retain(job, result, calls):
    if any(c["state"] != "completed" for c in calls_for_job(job, calls)):
        return True
    if job["arm"] == "prefix":
        return "eligible" in result and result.get("reason") != "infrastructure_stop"
    disposition = result.get("disposition", "")
    return disposition not in {"unstarted_global_stop", "infrastructure_stop", "infrastructure_error"}


def child_dispositions(task, parent, children, ledger):
    infeasible = set()
    if parent.get("eligible"):
        for pair in (("K", "R"), ("KE", "RE")):
            if pair == ("K", "R") and parent["shared"]["lesson"] is None:
                continue
            states = []
            for arm in pair:
                state = deepcopy(parent["state"])
                apply_intervention(state, arm, **parent["shared"])
                states.append(state)
            a, b = (actor_state(task, state) for state in states)
            if {k: v for k, v in a.items() if k != "history"} != {k: v for k, v in b.items() if k != "history"}:
                ledger.stop("paired_context_invariant_failed")
                infeasible.update(pair)
            if not all(fits(render(task, state)) for state in states):
                infeasible.update(pair)
    result = []
    for child in children:
        reason = None
        if not parent.get("eligible"):
            reason = "ineligible_prefix:" + parent.get("reason", "infrastructure_error")
        elif child["arm"] in {"K", "R"} and parent["shared"]["lesson"] is None:
            reason = "unusable_common_lesson"
        elif child["arm"] == "G" and parent["shared"]["summary"] is None:
            reason = "unusable_common_summary"
        elif child["arm"] in infeasible:
            reason = "paired_capacity_infeasible"
        result.append((child, reason))
    return result


def execute(tasks, manifest, dispatcher, runner, folder, workers, prior_execution, historical):
    by_id = {t["task_id"]: t for t in tasks}
    planned = manifest["jobs"]
    old = {r["job"]["job_id"]: r for r in prior_execution["jobs"]}
    if set(old) != {j["job_id"] for j in planned}:
        raise ValueError("prior job denominator differs from the original allocation")
    order = {j["job_id"]: i for i, j in enumerate(planned)}
    results, origins, prefixes, pending, running = {}, {}, {}, {}, {}
    ready = []; active = 0; peak = 0; lock = threading.Lock()
    children = {}
    for job in planned:
        if job["dependency"]:
            children.setdefault(job["dependency"], []).append(job)

    def record(job, result, kind):
        row = {"job": job, "result": result}
        results[job["job_id"]] = row
        origins[job["job_id"]] = {"kind": kind, "prior_result_sha256": sha(old[job["job_id"]])}
        save_new(Path(folder) / "jobs" / (job["job_id"] + ".json"), row)

    for job in planned:
        previous = old[job["job_id"]]["result"]
        if retain(job, previous, historical):
            record(job, previous, "retained_previous_phase")
            if job["arm"] == "prefix":
                prefixes[job["job_id"]] = previous
        else:
            pending[job["job_id"]] = job
            if job["dependency"] is None:
                ready.append(job)

    def release(parent_job, parent):
        selected = [j for j in children.get(parent_job, []) if j["job_id"] in pending]
        if not selected:
            return
        for child, reason in child_dispositions(by_id[selected[0]["task_id"]], parent, selected, dispatcher.ledger):
            if reason:
                record(child, {"score": None, "disposition": reason, "call_ids": []}, "dependency_disposition")
                pending.pop(child["job_id"], None)
            else:
                ready.append(child)
        ready.sort(key=lambda j: order[j["job_id"]])

    for parent_job, parent in prefixes.items():
        release(parent_job, parent)

    def work(job):
        nonlocal active, peak
        with lock:
            active += 1; peak = max(peak, active)
        try:
            task = by_id[job["task_id"]]
            parent = prefixes.get(job["dependency"])
            if job["arm"] == "prefix":
                result = run_prefix(task, dispatcher, runner)
            else:
                result = run_episode(task, job["track"], job["arm"], dispatcher, runner,
                                     prefix=parent["state"] if parent else None,
                                     shared=parent["shared"] if parent else None)
            prior = old[job["job_id"]]["result"]
            target = result.get("outcome", result)
            previous = prior.get("outcome", prior)
            if calls_for_job(job, historical) and "elapsed_seconds" in target:
                target["elapsed_seconds"] += previous.get("elapsed_seconds", 0)
            return result
        finally:
            with lock:
                active -= 1

    started = time.monotonic()
    with ThreadPoolExecutor(max_workers=workers, thread_name_prefix="v5-continuation") as pool:
        while ready or running:
            while ready and len(running) < workers and not dispatcher.ledger.stopped():
                job = ready.pop(0)
                pending.pop(job["job_id"], None)
                running[pool.submit(work, job)] = job
            if not running:
                break
            finished, _ = wait(running, timeout=1, return_when=FIRST_COMPLETED)
            for future in finished:
                job = running.pop(future)
                try:
                    result = future.result()
                except Exception as error:
                    dispatcher.ledger.stop("job_infrastructure_error")
                    result = {"score": None, "disposition": "infrastructure_error", "error_type": type(error).__name__}
                kind = "resumed_from_verified_receipts" if calls_for_job(job, historical) else "newly_executed"
                record(job, result, kind)
                if job["arm"] == "prefix":
                    prefixes[job["job_id"]] = result
                    release(job["job_id"], result)
                print(f"resolved_jobs={len(results)}/{len(planned)} active={len(running)} global_stop={dispatcher.ledger.stopped()}", flush=True)
    for job in planned:
        if job["job_id"] not in results:
            record(job, {"score": None, "disposition": "unstarted_global_stop", "call_ids": []}, "global_stop_not_started")
    return {"jobs": [results[j["job_id"]] for j in planned], "worker_count": workers,
            "peak_active_jobs": max(peak, prior_execution.get("peak_active_jobs", 0)),
            "wall_seconds": prior_execution.get("wall_seconds", 0) + time.monotonic() - started,
            "phase_wall_seconds": time.monotonic() - started, "stopped": dispatcher.ledger.stopped(), "origins": origins}
