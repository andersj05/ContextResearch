"""Frozen identities and bounded DAG executor; dependencies never race outcomes."""
from concurrent.futures import ThreadPoolExecutor, wait, FIRST_COMPLETED
from dataclasses import dataclass
from pathlib import Path
import threading
import time

from .common import STUDY, SEED, POLICIES, MECHANISM_ARMS, sha, save_new
from .accounting import Identity
from .engine import run_prefix, run_episode
from .engine import apply_intervention
from .contexts import render, actor_state, fits
from copy import deepcopy

TRACKS = ("mechanism", "policy", "memory")


def generation_bound(tasks, tracks=TRACKS):
    # A mechanism prefix requires at least one action, followed by two common
    # writers and at most H-1 actions in each of seven continuations. Policy and
    # memory writers only follow a nonfinal action, with at most one per action.
    return sum({"mechanism": 7 * t["action_allowance"] - 4,
                "policy": 8 * t["action_allowance"] - 3,
                "memory": 6 * t["action_allowance"] - 3}[track] for t in tasks for track in tracks)


def job_id(task_id, track, arm):
    return sha([task_id, track, arm])


def jobs(tasks, tracks=TRACKS):
    result = []
    for task in tasks:
        for track in tracks:
            arms = ("prefix",) + MECHANISM_ARMS if track == "mechanism" else POLICIES if track == "policy" else ("K", "R", "G")
            for arm in arms:
                result.append({"job_id": job_id(task["task_id"], track, arm), "task_id": task["task_id"],
                               "track": track, "arm": arm, "dependency": job_id(task["task_id"], "mechanism", "prefix") if track == "mechanism" and arm != "prefix" else None})
    return sorted(result, key=lambda row: sha([SEED, row["job_id"]]))


def identities(tasks, tracks=TRACKS):
    by_id = {t["task_id"]: t for t in tasks}; result = []
    for job in jobs(tasks, tracks):
        task = by_id[job["task_id"]]
        for step in range(1, task["action_allowance"] + 1):
            kinds = ["action"]
            if job["track"] != "mechanism":
                if job["arm"] in {"K", "R"}: kinds.append("lesson")
                if job["arm"] == "G": kinds.append("summary")
                if job["track"] == "memory": kinds.append("compress")
            for kind in kinds:
                result.append(Identity(STUDY, task["task_id"], job["track"], job["arm"], step, kind))
        if job["track"] == "mechanism" and job["arm"] == "prefix":
            result.extend(Identity(STUDY, task["task_id"], "mechanism", "shared", 0, kind) for kind in ("lesson", "summary"))
    return result


def execute(tasks, manifest, dispatcher, runner, folder, workers):
    """Every frozen job ends with a result or an explicit non-execution disposition."""
    by_id = {t["task_id"]: t for t in tasks}
    planned = manifest["jobs"]
    ready = [j for j in planned if j["dependency"] is None]
    children = {}
    for j in planned:
        if j["dependency"] is not None:
            children.setdefault(j["dependency"], []).append(j)
    results, prefixes, running = {}, {}, {}
    active = 0; peak = 0; lock = threading.Lock()

    def work(job):
        nonlocal active, peak
        with lock:
            active += 1; peak = max(peak, active)
        try:
            task = by_id[job["task_id"]]
            if job["arm"] == "prefix":
                return run_prefix(task, dispatcher, runner)
            parent = prefixes.get(job["dependency"])
            return run_episode(task, job["track"], job["arm"], dispatcher, runner,
                               prefix=parent["state"] if parent else None, shared=parent["shared"] if parent else None)
        finally:
            with lock: active -= 1

    def record(job, result):
        row = {"job": job, "result": result}
        results[job["job_id"]] = row
        save_new(Path(folder) / "jobs" / (job["job_id"] + ".json"), row)

    started = time.monotonic()
    with ThreadPoolExecutor(max_workers=workers, thread_name_prefix="rollback-v5") as pool:
        while ready or running:
            while ready and len(running) < workers and not dispatcher.ledger.stopped():
                job = ready.pop(0)
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
                record(job, result)
                if job["arm"] == "prefix":
                    prefixes[job["job_id"]] = result
                    infeasible = set()
                    if result.get("eligible"):
                        for pair in (("K", "R"), ("KE", "RE")):
                            if pair == ("K", "R") and result["shared"]["lesson"] is None:
                                continue
                            states = []
                            for arm in pair:
                                state = deepcopy(result["state"])
                                apply_intervention(state, arm, **result["shared"])
                                states.append(state)
                            a, b = (actor_state(by_id[job["task_id"]], s) for s in states)
                            if {k: v for k, v in a.items() if k != "history"} != {k: v for k, v in b.items() if k != "history"}:
                                dispatcher.ledger.stop("paired_context_invariant_failed")
                                infeasible.update(pair)
                            if not all(fits(render(by_id[job["task_id"]], s)) for s in states):
                                infeasible.update(pair)
                    for child in children.get(job["job_id"], []):
                        reason = None
                        if not result.get("eligible"):
                            reason = "ineligible_prefix:" + result.get("reason", "infrastructure_error")
                        elif child["arm"] in {"K", "R"} and result["shared"]["lesson"] is None:
                            reason = "unusable_common_lesson"
                        elif child["arm"] == "G" and result["shared"]["summary"] is None:
                            reason = "unusable_common_summary"
                        elif child["arm"] in infeasible:
                            reason = "paired_capacity_infeasible"
                        if reason:
                            record(child, {"score": None, "disposition": reason, "call_ids": []})
                        else:
                            ready.append(child)
                print(f"completed_jobs={len(results)}/{len(planned)} active={len(running)} stopped={dispatcher.ledger.stopped()}", flush=True)
    for job in planned:
        if job["job_id"] not in results:
            record(job, {"score": None, "disposition": "unstarted_global_stop", "call_ids": []})
    return {"jobs": [results[j["job_id"]] for j in planned], "worker_count": workers, "peak_active_jobs": peak,
            "wall_seconds": time.monotonic() - started, "stopped": dispatcher.ledger.stopped()}
