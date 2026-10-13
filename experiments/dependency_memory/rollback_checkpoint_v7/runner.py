"""Durable shared-prefix execution with independently parallel matched arms.

Each scheduled generation has one frozen identity and at most one admission.
The executor first advances all common prefixes; eligible K/R continuations
then share the same bounded pool. No thread ever waits on a submitted child job.
"""
from concurrent.futures import ThreadPoolExecutor, as_completed
from copy import deepcopy
from pathlib import Path
import json
import shutil
import threading
import time

from .accounting import Ledger, check_workers
from .common import ROOT, read, save_new, sha, now, wire
from .prepare import check_bundle, identities
from .engine import initial_state, run_prefix, run_continuation, pair_contract
from .analysis import analyze
from .contexts import render
from .client import live_factory, preflight, run_case
from ..rollback_development_v5_continuation.dispatch import Dispatcher
from ..rollback_pilot.subscription.transport import Response
from ..rollback_pilot.subscription.accounting import Usage


class ScriptedTransport:
    """Offline fixture: insert one wrong proposal, then return oracle answers.

    This intentionally manufactured failure is a controller exercise, never a
    natural model failure and never an empirical rollback result.
    """

    def __init__(self, tasks, *, failure_step=2):
        self.tasks = {task["task_id"]: task for task in tasks}
        self.failure_step = failure_step

    def generate(self, identity, request):
        data = read_request(request)
        task = self.tasks[identity.task_id]
        if identity.stage == "action":
            if identity.arm == "prefix" and identity.step == self.failure_step:
                candidate = {"values": [], "order": [], "files": []}
            else:
                candidate = deepcopy(task["evaluator"]["stage_references"][data["current_stage"] - 1])
            value = {"status": "candidate", "candidate": candidate,
                     "note": "Disclosed scripted offline fixture; not a model observation."}
        elif identity.stage == "lesson":
            value = {"established": [wire(data["feedback"])],
                     "retained_observations": [], "uncertainties": []}
        else:
            raise ValueError("v7 has only actor and one shared lesson requests")
        return Response(wire(value),
                        Usage(max(1, len(request.json_text) // 4), 0,
                              len(wire(value)) // 4 + 1, 0),
                        {"thread_id": "fixture-" + identity.key,
                         "model": "offline-scripted", "reasoning_effort": "medium"},
                        False)


def read_request(request):
    return json.loads(request.data()["messages"][1]["content"])


def client_preflight(executable, global_instructions, scratch_root, tasks, workers):
    """Read-only account checks and actual-client unauthenticated loopback.

    The old full negative suite is retained. Additional v7 payload checks are
    released concurrently by a barrier with exactly the frozen worker count.
    All answers are synthetic and the checks make zero live model generations.
    """
    check_workers(workers)
    checked = preflight(executable, global_instructions, scratch_root)
    global_text = Path(global_instructions).read_text(encoding="utf-8")
    samples = [render(task, initial_state(task)) for task in tasks[:workers]]
    # Exercise the lesson schema and an actual later-stage matched context from
    # locally scripted receipts, without placing evaluator truth in any actor
    # request. The fixture's oracle remains only inside ScriptedTransport.
    scripted = ScriptedTransport(tasks)
    fixture_requests = []

    def record(identity, request):
        fixture_requests.append(request)
        return scripted.generate(identity, request)

    prefix = run_prefix(tasks[0], record)
    if prefix.get("eligible"):
        for arm in ("K", "R"):
            run_continuation(tasks[0], arm, prefix, record)
    by_hash = {sha(request.json_text): request for request in samples + fixture_requests}
    requests = list(by_hash.values())
    checked["v7_payload_checks"] = [
        run_case(executable, global_text, request, "final_message", scratch_root)
        for request in requests
    ]
    barrier = threading.Barrier(workers)

    def concurrent(index):
        barrier.wait(timeout=30)
        request = requests[index % len(requests)]
        return run_case(executable, global_text, request, "final_message", scratch_root)

    with ThreadPoolExecutor(max_workers=workers, thread_name_prefix="rollback-v7-preflight") as pool:
        checked["v7_parallel_payload_checks"] = list(pool.map(concurrent, range(workers)))
    checked.update(v7_verified_workers=workers, v7_payload_schema_audit_passed=True,
                   v7_request_hashes=list(by_hash), v7_fixture_prefix_eligible=bool(prefix.get("eligible")),
                   v7_fixture_scope="disclosed wrong-once/oracle controller fixture; no empirical observations",
                   checked_utc=now(), real_model_generations=0, verified_effort="medium")
    return checked


def _controller_failure(job, error):
    # Do not serialize exception text, which may carry provider/user content.
    result = {"score": None, "disposition": "controller_error",
              "error_type": type(error).__name__}
    if job["arm"] == "prefix":
        result.update(eligible=False, reason="controller_error",
                      outcome={"score": None, "disposition": "controller_error"})
    return result


def run(bundle, output, *, live=False, workers=None, executable=None,
        global_instructions=None):
    manifest, tasks = check_bundle(bundle)
    workers = manifest["workers"] if workers is None else workers
    check_workers(workers)
    if workers != manifest["workers"]:
        raise ValueError("worker count differs from frozen allocation")
    if live and manifest["split"] == "fixture":
        raise ValueError("fixture allocations cannot dispatch live generations")
    output, bundle = Path(output).resolve(), Path(bundle).resolve()
    if not output.is_relative_to(ROOT) or output.exists():
        raise ValueError("new workspace result directory required")
    marker = bundle / ("launch_started.json" if live else "simulation_started.json")
    if marker.exists():
        raise ValueError("allocation already started; inspect existing results, never relaunch")
    output.mkdir(parents=True)
    if live:
        executable = executable or shutil.which("codex.exe") or shutil.which("codex")
        if not executable:
            raise ValueError("installed Codex executable required")
        global_instructions = Path(global_instructions or Path.home() / ".codex" / "AGENTS.md")
        checked = client_preflight(executable, global_instructions, output / "scratch", tasks, workers)
        save_new(output / "preflight.json", checked)
        factory = live_factory(executable, global_instructions, checked, output / "scratch")
    else:
        factory = lambda: ScriptedTransport(tasks)
    # Exclusive creation is the one-launch guard, including racing controllers.
    # Preflight above is read-only and makes no live model generation.
    save_new(marker, {"output": str(output), "started_utc": now(),
                      "manifest_sha256": sha(manifest)})
    save_new(output / "manifest.json", manifest)
    save_new(output / "run_settings.json", {
        "live": live, "workers": workers, "started_utc": now(),
        "evidence_kind": "live_model_observations" if live else "scripted_offline_fixture",
        "schedule": "shared prefixes, then independently scheduled matched K/R continuations",
        "retries": 0, "prior": None,
    })
    ledger = Ledger(output / "ledger.sqlite", identities(tasks), workers,
                    generation_ceiling=manifest["generation_ceiling"])
    dispatcher = Dispatcher(output, manifest, ledger, factory)
    by_id = {task["task_id"]: task for task in tasks}
    prefixes, results = {}, {}
    prefix_jobs = [job for job in manifest["jobs"] if job["arm"] == "prefix"]
    continuation_jobs = [job for job in manifest["jobs"] if job["arm"] in {"K", "R"}]
    started = time.monotonic()

    def work(job):
        task = by_id[job["task_id"]]
        if job["arm"] == "prefix":
            result = run_prefix(task, dispatcher)
        else:
            result = run_continuation(task, job["arm"], prefixes[job["task_id"]], dispatcher)
        return {"job": job, "result": result}

    def save_completed(future, job):
        try:
            row = future.result()
        except Exception as error:
            ledger.stop("controller_error")
            row = {"job": job, "result": _controller_failure(job, error)}
        result = row["result"]
        results[job["job_id"]] = row
        save_new(output / "jobs" / (job["job_id"] + ".json"), row)
        if job["arm"] == "prefix":
            prefixes[job["task_id"]] = result
            save_new(output / "prefixes" / (job["job_id"] + ".json"), result)
            if result.get("eligible"):
                save_new(output / "pair_contracts" / (job["job_id"] + ".json"),
                         pair_contract(by_id[job["task_id"]], result))
        snapshot = ledger.snapshot()
        print(wire({"jobs_done": len(results), "jobs_total": len(manifest["jobs"]),
                    "eligible_prefixes": sum(bool(p.get("eligible")) for p in prefixes.values()),
                    "completions": snapshot["completed_calls"],
                    "unknown": sum(call["state"] == "unknown" for call in snapshot["calls"]),
                    "inflight": sum(call["state"] == "dispatched" for call in snapshot["calls"]),
                    "stop": snapshot["stop"]}), flush=True)

    with ThreadPoolExecutor(max_workers=workers, thread_name_prefix="rollback-v7") as pool:
        # Separate phases avoid executor starvation/deadlock from workers waiting
        # for their own continuation jobs. Arm order stays frozen in the manifest.
        for phase in (prefix_jobs, continuation_jobs):
            futures = {pool.submit(work, job): job for job in phase}
            for future in as_completed(futures):
                save_completed(future, futures[future])
    execution = {"jobs": [results[job["job_id"]] for job in manifest["jobs"]],
                 "stopped": ledger.stopped(), "wall_seconds": time.monotonic() - started}
    accounting = ledger.snapshot()
    save_new(output / "execution.json", execution)
    save_new(output / "accounting.json", accounting)
    dispatched = {call["call_id"]: call["state"] for call in accounting["calls"]}
    save_new(output / "slot_dispositions.json", [
        {"call_id": identity.key, "disposition": dispatched.get(identity.key, "never_dispatched")}
        for identity in identities(tasks)
    ])
    report = analyze(tasks, execution, accounting, manifest, simulated=not live)
    save_new(output / "analysis.json", report)
    save_new(output / "evidence_manifest.json", {
        "files": [{"path": path.relative_to(output).as_posix(), "sha256": sha(path.read_bytes())}
                  for path in sorted(output.rglob("*.json"))
                  if "scratch" not in path.relative_to(output).parts],
        "ledger_sha256": sha((output / "ledger.sqlite").read_bytes()),
    })
    return {"folder": str(output), "jobs": len(results),
            "eligible_prefixes": sum(bool(p.get("eligible")) for p in prefixes.values()),
            "model_calls": len(accounting["calls"]) if live else 0,
            "completed": accounting["completed_calls"],
            "unknown": accounting["unknown_or_inflight_calls"], "stop": accounting["stop"]}
