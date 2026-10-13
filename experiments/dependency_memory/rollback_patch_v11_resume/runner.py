"""Continue only unsent healthy v11 identities while preserving the old phase."""

from copy import deepcopy
from pathlib import Path
import shutil
import time

from experiments.dependency_memory.rollback_patch_v11.common import ROOT, read, save_new, sha, now, wire
from experiments.dependency_memory.rollback_patch_v11.prepare import identities
from experiments.dependency_memory.rollback_patch_v11.engine import run_prefix, run_continuation, factorial_contract
from experiments.dependency_memory.rollback_patch_v11.runtime import PatchRuntime
from experiments.dependency_memory.rollback_patch_v11.scheduler import execute
from experiments.dependency_memory.rollback_patch_v11.analysis import analyze
from experiments.dependency_memory.rollback_patch_v11.runner import client_preflight, ScriptedTransport
from experiments.dependency_memory.rollback_patch_v11.transport import live_factory
from experiments.dependency_memory.rollback_development_v5_continuation.accounting import Ledger
from experiments.dependency_memory.rollback_development_v5_continuation.dispatch import Dispatcher
from experiments.dependency_memory.rollback_development_v5.audit import ledger_rows
from experiments.dependency_memory.rollback_patch_v11_resume.recovery import select_jobs, copy_history, copy_exact


def run(bundle, output, *, live=False, executable=None, global_instructions=None):
    from experiments.dependency_memory.rollback_patch_v11_resume.prepare import check_bundle
    manifest, tasks = check_bundle(bundle)
    recovery = manifest["recovery"]
    prior = (ROOT / recovery["prior_output"]).resolve()
    bundle, output = Path(bundle).resolve(), Path(output).resolve()
    if not output.is_relative_to(ROOT) or output.exists():
        raise ValueError("new_workspace_output_required")
    prior_settings = read(prior / "run_settings.json")
    if live is not prior_settings["live"]:
        raise ValueError("live and scripted phases must not be mixed")
    if live and manifest["split"] == "fixture":
        raise ValueError("fixture_cannot_dispatch_models")
    marker = bundle / ("launch_started.json" if live else "simulation_started.json")
    if marker.exists():
        raise ValueError("never_relaunch_recovery_allocation")
    historical, _, old_stop = ledger_rows(prior / "ledger.sqlite")
    if old_stop != recovery["inherited_stop"]:
        raise ValueError("inherited global stop differs from frozen recovery")
    prior_execution = read(prior / "execution.json")
    plan = select_jobs(manifest, prior_execution, historical)
    if recovery.get("selection_sha256") is not None and sha(plan) != recovery["selection_sha256"]:
        raise ValueError("recovery selection differs from frozen plan")
    workers = manifest["workers"]
    output.mkdir(parents=True)
    runtime = PatchRuntime()
    save_new(output / "runtime_audit.json", runtime.audit())
    if live:
        executable = executable or shutil.which("codex.exe") or shutil.which("codex")
        global_instructions = Path(global_instructions or Path.home() / ".codex" / "AGENTS.md")
        checked = client_preflight(executable, global_instructions, output / "scratch", tasks, workers)
        previous = read(prior / "preflight.json")
        stable_fields = ("executable_sha256", "configuration_sha256", "global_instructions_sha256",
                         "registry_sha256", "namespace_metadata_sha256")
        if any(checked.get(key) != previous.get(key) for key in stable_fields):
            raise ValueError("pinned client or instruction contract changed across recovery")
        save_new(output / "preflight.json", checked)
        factory = live_factory(executable, global_instructions, checked, output / "scratch")
    else:
        factory = lambda: ScriptedTransport(tasks)
    check_bundle(bundle)
    copied = copy_history(prior, output, historical)
    save_new(output / "historical_receipt_import.json", copied)
    save_new(output / "recovery_plan.json", plan)
    save_new(output / "manifest.json", manifest)
    save_new(output / "run_settings.json", {
        "live": live, "workers": workers, "started_utc": now(), "retries": 0,
        "evidence_kind": "live_model_operational_continuation" if live else "scripted_offline_continuation",
        "prior": recovery["prior_output"], "recovery_manifest_sha256": sha(manifest),
    })
    save_new(marker, {"output": str(output), "started_utc": now(), "manifest_sha256": sha(manifest)})
    ledger = Ledger(output / "ledger.sqlite", identities(tasks, manifest["split"]), workers,
                    prior=prior / "ledger.sqlite", generation_ceiling=manifest["generation_ceiling"])
    dispatcher = Dispatcher(output, manifest, ledger, factory, historical=historical)
    by_task = {task["task_id"]: task for task in tasks}
    prior_rows = {row["job"]["job_id"]: row for row in prior_execution["jobs"]}
    choices = {row["job_id"]: row for row in plan["jobs"]}
    prefixes, results, origins = {}, {}, {}
    started = time.monotonic()

    def work(job):
        if choices[job["job_id"]]["decision"] == "retain":
            return deepcopy(prior_rows[job["job_id"]])
        task = by_task[job["task_id"]]
        if job["arm"] == "prefix":
            result = run_prefix(task, dispatcher, runtime)
        else:
            result = run_continuation(task, job["arm"], prefixes[job["task_id"]], dispatcher, runtime)
        return {"job": job, "result": result}

    def completed(future, job):
        choice = choices[job["job_id"]]
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
            path = output / "jobs" / (job["job_id"] + ".json")
            if choice["decision"] == "retain":
                source = prior / "jobs" / path.name
                if row != prior_rows[job["job_id"]] or read(source) != row:
                    raise ValueError("retained job changed")
                copy_exact(source, path)
            else:
                save_new(path, row)
            results[job["job_id"]] = row
            origins[job["job_id"]] = {
                "decision": choice["decision"], "reason": choice["reason"],
                "prior_row_sha256": choice["prior_row_sha256"],
                "historical_call_ids": choice["historical_call_ids"],
                "kind": ("retained_exact_prior_bytes" if choice["decision"] == "retain"
                         else "resumed_from_verified_receipts" if choice["historical_call_ids"]
                         else "previously_unadmitted_job"),
            }
            if job["arm"] == "prefix":
                prefixes[job["task_id"]] = row["result"]
                if row["result"].get("eligible"):
                    contract = factorial_contract(by_task[job["task_id"]], row["result"])
                    target = output / "factorial_contracts" / (job["job_id"] + ".json")
                    if choice["decision"] == "retain":
                        source = prior / "factorial_contracts" / target.name
                        if read(source) != contract:
                            raise ValueError("retained factorial contract changed")
                        copy_exact(source, target)
                    else:
                        save_new(target, contract)
        except Exception:
            ledger.stop("persistence_or_recovery_contract_error")
            raise
        snapshot = ledger.snapshot()
        print(wire({"jobs_done": len(results), "jobs_total": len(manifest["jobs"]),
                    "new_admissions": len(snapshot["calls"]) - len(historical),
                    "calls": len(snapshot["calls"]), "unknown": snapshot["unknown_or_inflight_calls"],
                    "phase_stop": snapshot["stop"]}), flush=True)

    trace = execute(manifest["jobs"], work, completed, workers)
    phase_seconds = time.monotonic() - started
    inherited_stops = list(recovery.get("inherited_stops", [old_stop] if old_stop else []))
    execution = {
        "jobs": [results[job["job_id"]] for job in manifest["jobs"]],
        "stopped": bool(inherited_stops) or prior_execution.get("stopped", False) or ledger.stopped(),
        "phase_stopped": ledger.stopped(), "inherited_stops": inherited_stops,
        "wall_seconds": prior_execution.get("wall_seconds", 0) + phase_seconds,
        "phase_wall_seconds": phase_seconds,
    }
    accounting = ledger.snapshot()
    historical_ids = {call["call_id"] for call in historical}
    cumulative_ids = {call["call_id"] for call in accounting["calls"]}
    expected_replays = {call_id for choice in plan["jobs"] if choice["decision"] == "resume"
                        for call_id in choice["historical_call_ids"]}
    if dispatcher.replay_used != expected_replays:
        ledger.stop("historical_replay_coverage_mismatch")
        raise ValueError("healthy historical receipt replay coverage differs")
    retained_owners = {(choice["task_id"], choice["arm"]) for choice in plan["jobs"] if choice["decision"] == "retain"}
    if any(call["call_id"] not in historical_ids and (call["identity"]["task_id"], call["identity"]["arm"]) in retained_owners
           for call in accounting["calls"]):
        ledger.stop("retained_job_received_new_admission")
        raise ValueError("retained job received a new provider admission")
    save_new(output / "scheduler_trace.json", trace)
    save_new(output / "job_origins.json", origins)
    save_new(output / "recovery_execution.json", {
        "selection_sha256": sha(plan), "historical_admissions": len(historical),
        "historical_replayed_call_ids": sorted(dispatcher.replay_used),
        "new_admission_ids": sorted(cumulative_ids - historical_ids),
        "inherited_stops": inherited_stops, "phase_stop": accounting["stop"],
        "retained_jobs_received_no_new_admissions": True,
    })
    save_new(output / "execution.json", execution)
    save_new(output / "accounting.json", accounting)
    save_new(output / "runtime_statistics.json", runtime.statistics())
    dispatched = {call["call_id"]: call["state"] for call in accounting["calls"]}
    save_new(output / "slot_dispositions.json", [{"call_id": item.key,
        "disposition": dispatched.get(item.key, "never_dispatched")} for item in identities(tasks, manifest["split"])])
    analysis = analyze(tasks, execution, accounting, manifest, simulated=not live)
    save_new(output / "analysis.json", analysis)
    save_new(output / "evidence_manifest.json", {
        "files": [{"path": path.relative_to(output).as_posix(), "sha256": sha(path.read_bytes())}
                  for path in sorted(output.rglob("*.json")) if "scratch" not in path.relative_to(output).parts],
        "ledger_sha256": sha((output / "ledger.sqlite").read_bytes()),
    })
    return {"folder": str(output), "jobs": len(results),
            "model_calls": len(cumulative_ids - historical_ids) if live else 0,
            "new_admissions": len(cumulative_ids - historical_ids),
            "cumulative_admissions": len(cumulative_ids), "known": accounting["completed_calls"],
            "unknown": accounting["unknown_or_inflight_calls"], "phase_stop": accounting["stop"],
            "inherited_stops": inherited_stops,
            "causal_interpretation_gate_passed": analysis["capacity_interpretation_gate"]["passed"]}
