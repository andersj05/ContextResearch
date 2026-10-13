"""Bounded subscription dispatch and durable four-arm dependency scheduling."""
from concurrent.futures import ThreadPoolExecutor
from copy import deepcopy
from pathlib import Path
import shutil
import threading
import time
from .common import ROOT, ARMS, WORKERS, sha, now, wire, read, save_new
from .prepare import check_bundle, identities
from .engine import run_prefix, run_continuation, factorial_contract, patch
from .contexts import render, LESSON
from .runtime import PatchRuntime
from .scheduler import execute
from .analysis import analyze
from ..rollback_parallel_v8.accounting import Ledger
from ..rollback_parallel_v8.client import live_factory, preflight, run_case
from ..rollback_development_v5_continuation.dispatch import Dispatcher
from ..rollback_pilot.subscription.transport import Response
from ..rollback_pilot.subscription.accounting import Usage


def fixture_action(task):
    files = [{"path": "engine.py", "text": "import rules\n\ndef solve(case):\n    value = rules.answer(case)\n    return value\n"},
             {"path": "rules.py", "text": "def answer(case):\n    keys = list(case)\n    result = None\n    return result\n"}]
    return {"files": files, "note": "Manufactured wrong-once controller fixture; never empirical evidence."}


class ScriptedTransport:
    def __init__(self, tasks):
        self.tasks = {task["task_id"]: task for task in tasks}

    def generate(self, identity, request):
        task = self.tasks[identity.task_id]
        if identity.stage == "lesson":
            value = {key: schema["enum"][-1] for key, schema in LESSON["properties"].items()}
        elif identity.arm == "prefix":
            value = fixture_action(task)
        else:
            value = {"files": deepcopy(task["evaluator"]["reference_files"]),
                     "note": "Reference-only scripted fixture; not a model answer."}
        return Response(wire(value), Usage(max(1, len(request.json_text) // 4), 0,
                                          len(wire(value)) // 4 + 1, 0),
                        {"thread_id": "fixture-" + identity.key, "model": "offline-scripted",
                         "reasoning_effort": "medium"}, False)


def client_preflight(executable, instructions, scratch, tasks, workers):
    checked = preflight(executable, instructions, scratch)
    requests = [render(task) for task in sorted(tasks, key=lambda t: len(wire(t)), reverse=True)[:workers]]
    task = tasks[0]
    action = fixture_action(task)
    public = {"status": "public_mismatch", "check_id": task["public_tests"][0]["id"],
              "input": task["public_tests"][0]["input"], "expected": task["public_tests"][0]["expected"],
              "observed": None, "detail": "Disclosed serialization fixture, no execution observation."}
    delta = patch(task["base_files"], action["files"])
    prefix = {"eligible": True, "task_id": task["task_id"], "task_sha256": sha(task),
              "failed_record": {"public": public, "visible_work": {"patch": delta["diff"], "note": action["note"]},
                                "candidate": {"files": action["files"]},
                                "changed_nonempty_lines": delta["changed_nonempty_lines"]},
              "lesson": {key: schema["enum"][-1] for key, schema in LESSON["properties"].items()}}
    factorial_contract(task, prefix)
    requests.append(render(task, prefix=prefix, kind="lesson"))
    requests.extend(render(task, arm=arm, prefix=prefix) for arm in ARMS)
    global_text = Path(instructions).read_text(encoding="utf-8")
    with ThreadPoolExecutor(max_workers=workers) as pool:
        checked["v9_payload_checks"] = list(pool.map(
            lambda request: run_case(executable, global_text, request, "final_message", scratch), requests))
    barrier = threading.Barrier(workers)

    def concurrent(index):
        barrier.wait(timeout=30)
        return run_case(executable, global_text, requests[index % len(requests)], "final_message", scratch)
    with ThreadPoolExecutor(max_workers=workers) as pool:
        checked["v9_parallel_checks"] = list(pool.map(concurrent, range(workers)))
    checked.update(v9_verified_workers=workers, v9_request_hashes=[sha(r.json_text) for r in requests],
                   real_model_generations=0, v9_factorial_serialization_passed=True)
    return checked


def run(bundle, output, *, live=False, executable=None, global_instructions=None):
    manifest, tasks = check_bundle(bundle)
    workers = manifest["workers"]
    if live and manifest["split"] == "fixture":
        raise ValueError("fixture_cannot_dispatch_models")
    output, bundle = Path(output).resolve(), Path(bundle).resolve()
    if not output.is_relative_to(ROOT) or output.exists():
        raise ValueError("new_workspace_output_required")
    marker = bundle / ("launch_started.json" if live else "simulation_started.json")
    if marker.exists():
        raise ValueError("never_relaunch_allocation")
    output.mkdir(parents=True)
    runtime = PatchRuntime()
    save_new(output / "runtime_audit.json", runtime.audit())
    if live:
        executable = executable or shutil.which("codex.exe") or shutil.which("codex")
        global_instructions = Path(global_instructions or Path.home() / ".codex" / "AGENTS.md")
        checked = client_preflight(executable, global_instructions, output / "scratch", tasks, workers)
        save_new(output / "preflight.json", checked)
        factory = live_factory(executable, global_instructions, checked, output / "scratch")
    else:
        factory = lambda: ScriptedTransport(tasks)
    check_bundle(bundle)
    save_new(marker, {"output": str(output), "started_utc": now(), "manifest_sha256": sha(manifest)})
    save_new(output / "manifest.json", manifest)
    save_new(output / "run_settings.json", {"live": live, "workers": workers, "started_utc": now(),
              "evidence_kind": "live_model_observations" if live else "scripted_offline_fixture", "retries": 0})
    ledger = Ledger(output / "ledger.sqlite", identities(tasks, manifest["split"]), workers,
                    generation_ceiling=manifest["generation_ceiling"])
    dispatcher = Dispatcher(output, manifest, ledger, factory)
    by_id = {task["task_id"]: task for task in tasks}
    prefixes, results = {}, {}
    started = time.monotonic()

    def work(job):
        task = by_id[job["task_id"]]
        if job["arm"] == "prefix":
            result = run_prefix(task, dispatcher, runtime)
        else:
            result = run_continuation(task, job["arm"], prefixes[job["task_id"]], dispatcher, runtime)
        return {"job": job, "result": result}

    def completed(future, job):
        try:
            row = future.result()
        except Exception as error:
            ledger.stop("controller_error")
            result = {"score": None, "disposition": "controller_error", "error_type": type(error).__name__,
                      "attempts": [], "first_pass": None}
            if job["arm"] == "prefix":
                result.update(eligible=False, reason="controller_error", lesson_disposition="not_needed")
            row = {"job": job, "result": result}
        try:
            save_new(output / "jobs" / (job["job_id"] + ".json"), row)
            results[job["job_id"]] = row
            if job["arm"] == "prefix":
                prefixes[job["task_id"]] = row["result"]
                if row["result"].get("eligible"):
                    save_new(output / "factorial_contracts" / (job["job_id"] + ".json"),
                             factorial_contract(by_id[job["task_id"]], row["result"]))
        except Exception:
            ledger.stop("persistence_or_contract_error")
            raise
        snapshot = ledger.snapshot()
        print(wire({"jobs_done": len(results), "jobs_total": len(manifest["jobs"]),
                    "eligible": sum(p.get("eligible", False) for p in prefixes.values()),
                    "calls": len(snapshot["calls"]), "unknown": snapshot["unknown_or_inflight_calls"],
                    "stop": snapshot["stop"]}), flush=True)

    trace = execute(manifest["jobs"], work, completed, workers)
    execution = {"jobs": [results[job["job_id"]] for job in manifest["jobs"]],
                 "stopped": ledger.stopped(), "wall_seconds": time.monotonic() - started}
    accounting = ledger.snapshot()
    save_new(output / "scheduler_trace.json", trace)
    save_new(output / "execution.json", execution)
    save_new(output / "accounting.json", accounting)
    save_new(output / "runtime_statistics.json", runtime.statistics())
    dispatched = {call["call_id"]: call["state"] for call in accounting["calls"]}
    save_new(output / "slot_dispositions.json", [{"call_id": item.key,
        "disposition": dispatched.get(item.key, "never_dispatched")} for item in identities(tasks, manifest["split"])])
    report = analyze(tasks, execution, accounting, manifest, simulated=not live)
    save_new(output / "analysis.json", report)
    save_new(output / "evidence_manifest.json", {
        "files": [{"path": path.relative_to(output).as_posix(), "sha256": sha(path.read_bytes())}
                  for path in sorted(output.rglob("*.json")) if "scratch" not in path.relative_to(output).parts],
        "ledger_sha256": sha((output / "ledger.sqlite").read_bytes())})
    return {"folder": str(output), "jobs": len(results), "model_calls": len(accounting["calls"]) if live else 0,
            "known": accounting["completed_calls"], "unknown": accounting["unknown_or_inflight_calls"],
            "eligible": sum(p.get("eligible", False) for p in prefixes.values()), "stop": accounting["stop"]}
