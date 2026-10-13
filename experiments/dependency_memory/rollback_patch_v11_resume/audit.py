"""Independent cumulative audit of the frozen unsent-work continuation.

The inherited fatal stop is checked within phase zero. New admissions are
checked as a second drained phase, without rewriting any historical event.
"""
from concurrent.futures import ThreadPoolExecutor
from dataclasses import asdict
from decimal import Decimal
from pathlib import Path
import json
import sqlite3

from .common import read, save_new, sha, now, RUNTIME_WORKERS
from .prepare import check_bundle, identities, workspace_path
from .recovery import select_jobs
from ..rollback_patch_v11.engine import run_prefix, run_continuation, factorial_contract
from ..rollback_patch_v11.analysis import analyze
from ..rollback_patch_v11.runtime import PatchRuntime
from ..rollback_patch_v11.audit import Replay, verify_trace, verify_live_preflight, identities_from_manifest
from ..rollback_checkpoint_v7.audit import comparable, _inventory, _metering
from ..rollback_development_v5.audit import ReplayMismatch, ledger_rows
from ..rollback_pilot.subscription.accounting import Usage, RESERVATION


def _require(condition, reason):
    if not condition:
        raise ReplayMismatch(reason)


def cumulative_accounting(calls, stop):
    known = [call for call in calls if call["state"] == "completed"]
    unknown = len(calls) - len(known)
    return {"calls": calls, "completed_calls": len(known), "unknown_or_inflight_calls": unknown,
            "planning_credits": str(sum((Usage(**call["usage"]).cost for call in known), Decimal(0))),
            "locked_planning_credits": str(unknown * RESERVATION), "stop": stop,
            "usage": {key: sum(call["usage"][key] for call in known)
                      for key in ("input_tokens", "cached_input", "output", "reasoning")},
            "actual_account_charge": None, "API_key_calls": 0}


def partition_phases(calls, events, old_calls, old_events):
    """Exact event prefix and immutable prior rows; no normalization of faults."""
    by_id = {call["call_id"]: call for call in calls}
    old_ids = {call["call_id"] for call in old_calls}
    _require(len(by_id) == len(calls) and len(old_ids) == len(old_calls), "duplicate cumulative call")
    _require(events[:len(old_events)] == old_events, "historical events changed")
    _require(all(by_id.get(call["call_id"]) == call for call in old_calls), "historical call row changed")
    suffix = events[len(old_events):]
    _require(all(event["call_id"] not in old_ids for event in suffix), "historical identity repeated after recovery")
    return [call for call in calls if call["call_id"] not in old_ids], suffix


def reconcile_ledger(folder, manifest, settings):
    prior = workspace_path(manifest["recovery"]["prior_output"])
    _inventory(prior)
    original = read(prior / "manifest.json")
    old_calls, old_events, old_stop = ledger_rows(prior / "ledger.sqlite")
    calls, events, stop = ledger_rows(folder / "ledger.sqlite")
    new_calls, new_events = partition_phases(calls, events, old_calls, old_events)
    old_accounting, old_peak = _metering(old_calls, old_events, old_stop, original,
                                        read(prior / "run_settings.json"))
    _require(old_accounting == read(prior / "accounting.json"), "historical accounting differs")
    new_accounting, new_peak = _metering(new_calls, new_events, stop, manifest, settings)
    _require(len(calls) <= manifest["generation_ceiling"], "cumulative allocation exceeded")
    accounting = cumulative_accounting(calls, stop)
    _require(accounting == read(folder / "accounting.json"), "cumulative accounting differs")
    by_id = {call["call_id"]: call for call in calls}
    for event in events:
        if event["state"] == "dispatched":
            _require(set(event["payload"]) == {"admitted_utc", "reserve_credits"}, "admission payload differs")
        else:
            payload = {key: value for key, value in by_id[event["call_id"]].items()
                       if key not in {"call_id", "identity", "request_hash", "state"}}
            _require(payload == event["payload"], "terminal event payload differs from call")
    db = sqlite3.connect((folder / "ledger.sqlite").resolve().as_uri() + "?mode=ro", uri=True)
    try:
        planned = {item.key: asdict(item) for item in identities_from_manifest(manifest)}
        config = [json.loads(row[0]) for row in db.execute("SELECT payload FROM config")]
        ceiling = [json.loads(row[0]) for row in db.execute("SELECT payload FROM continuation_config")]
        threads = set(db.execute("SELECT thread_id,call_id FROM threads"))
        expected_threads = {(call["metadata"]["thread_id"], call["call_id"])
                            for call in calls if call["state"] == "completed"}
        _require(config == [{"identities": sha(planned), "max_inflight": settings["workers"]}],
                 "cumulative allocation or worker binding differs")
        _require(ceiling == [{"generation_ceiling": manifest["generation_ceiling"]}], "cumulative ceiling differs")
        _require(threads == expected_threads and len({thread for thread, _ in expected_threads}) == len(expected_threads),
                 "provider thread reused or inventory differs")
        inherited = [row[0] for row in db.execute("SELECT reason FROM inherited_stops")]
        _require(inherited == manifest["recovery"]["inherited_stops"] == [old_stop], "inherited stop changed")
    finally:
        db.close()
    request_ids = {path.stem for path in (folder / "requests").glob("*.json")}
    response_ids = {path.stem for path in (folder / "responses").glob("*.json")}
    completed_ids = {call["call_id"] for call in calls if call["state"] == "completed"}
    _require(request_ids == set(by_id) and completed_ids <= response_ids <= set(by_id),
             "cumulative request/response inventory differs")
    for directory in ("requests", "responses", "diagnostics"):
        for path in (prior / directory).glob("*.json"):
            copied = folder / directory / path.name
            _require(copied.is_file() and copied.read_bytes() == path.read_bytes(), "historical receipt bytes changed")
    for path in (folder / "diagnostics").glob("*.json"):
        call = by_id.get(path.stem)
        _require(call is not None and call["state"] == "unknown" and read(path) == call.get("diagnostic"),
                 "unknown diagnostic differs")
    phases = {"historical_admissions": len(old_calls), "new_admissions": len(new_calls),
              "historical_completed": old_accounting["completed_calls"],
              "historical_unknowns": old_accounting["unknown_or_inflight_calls"],
              "new_completed": new_accounting["completed_calls"],
              "new_unknowns": new_accounting["unknown_or_inflight_calls"],
              "historical_peak": old_peak, "new_peak": new_peak,
              "inherited_stop": old_stop, "phase_stop": stop,
              "historical_events_unchanged": True, "historical_receipts_unchanged": True}
    return calls, accounting, max(old_peak, new_peak), stop, old_calls, phases


def verify_recovery_records(folder, prior, manifest, execution, calls, historical, stop):
    """Verify copied provenance and the score-blind plan separately from replay."""
    prior_execution = read(prior / "execution.json")
    plan = select_jobs(manifest, prior_execution, historical)
    _require(read(folder / "recovery_plan.json") == plan, "recovery plan does not reproduce")
    binding = manifest["recovery"].get("selection_sha256")
    _require(binding is None or binding == sha(plan), "frozen recovery selection differs")
    copies = []
    for directory in ("requests", "responses", "diagnostics"):
        for source in sorted((prior / directory).glob("*.json")):
            relative = source.relative_to(prior).as_posix()
            copies.append({"prior_path": relative, "path": relative, "sha256": sha(source.read_bytes())})
    for name in ("execution.json", "manifest.json", "accounting.json", "evidence_manifest.json",
                 "scheduler_trace.json", "preflight.json"):
        source = prior / name
        if source.is_file():
            target = folder / ("prior_" + name)
            _require(target.is_file() and target.read_bytes() == source.read_bytes(), "historical phase bytes changed")
            copies.append({"prior_path": name, "path": target.name, "sha256": sha(source.read_bytes())})
    expected_import = {"files": copies, "receipt_bytes_preserved": True,
        "scope": "Original admitted requests, saved responses and diagnostics copied byte-for-byte; no old ledger identity is dispatched again."}
    _require(read(folder / "historical_receipt_import.json") == expected_import, "historical import inventory differs")
    historical_ids = {call["call_id"] for call in historical}
    new_ids = {call["call_id"] for call in calls} - historical_ids
    choices = {choice["job_id"]: choice for choice in plan["jobs"]}
    expected_replays = sorted(call_id for choice in plan["jobs"] if choice["decision"] == "resume"
                              for call_id in choice["historical_call_ids"])
    retained_owners = {(choice["task_id"], choice["arm"]) for choice in plan["jobs"]
                       if choice["decision"] == "retain"}
    _require(all((call["identity"]["task_id"], call["identity"]["arm"]) not in retained_owners
                 for call in calls if call["call_id"] in new_ids), "retained job received new admission")
    unknown_owners = {(call["identity"]["task_id"], call["identity"]["arm"])
                      for call in historical if call["state"] == "unknown"}
    _require(unknown_owners <= retained_owners, "unknown-owning job was resumed")
    expected_execution = {"selection_sha256": sha(plan), "historical_admissions": len(historical),
        "historical_replayed_call_ids": expected_replays, "new_admission_ids": sorted(new_ids),
        "inherited_stops": manifest["recovery"]["inherited_stops"], "phase_stop": stop,
        "retained_jobs_received_no_new_admissions": True}
    _require(read(folder / "recovery_execution.json") == expected_execution, "recovery execution coverage differs")
    origins = {}
    prior_rows = {row["job"]["job_id"]: row for row in prior_execution["jobs"]}
    for row in execution["jobs"]:
        job_id = row["job"]["job_id"]
        choice = choices[job_id]
        retained = choice["decision"] == "retain"
        if retained:
            _require(row == prior_rows[job_id], "retained result changed")
            _require((folder / "jobs" / (job_id + ".json")).read_bytes() ==
                     (prior / "jobs" / (job_id + ".json")).read_bytes(), "retained job bytes changed")
        origins[job_id] = {"decision": choice["decision"], "reason": choice["reason"],
            "prior_row_sha256": choice["prior_row_sha256"], "historical_call_ids": choice["historical_call_ids"],
            "kind": "retained_exact_prior_bytes" if retained else
                    "resumed_from_verified_receipts" if choice["historical_call_ids"] else "previously_unadmitted_job"}
    _require(read(folder / "job_origins.json") == origins, "job provenance differs")
    return plan


def audit(bundle, output, destination):
    manifest, tasks = check_bundle(bundle)
    output, destination = Path(output).resolve(), Path(destination).resolve()
    if destination.is_relative_to(output) or destination.exists():
        raise ValueError("new_audit_report_outside_sealed_run_required")
    _require(read(output / "manifest.json") == manifest, "recovery run manifest changed")
    _inventory(output)
    recovery = manifest["recovery"]
    prior = workspace_path(recovery["prior_output"])
    settings = read(output / "run_settings.json")
    _require(settings["workers"] == manifest["workers"] and settings["retries"] == 0
             and type(settings["live"]) is bool and settings["live"] is recovery["prior_live"]
             and workspace_path(settings["prior"]) == prior
             and settings["recovery_manifest_sha256"] == sha(manifest), "recovery run contract differs")
    if settings["live"]:
        checked = read(output / "preflight.json")
        verify_live_preflight(checked, settings["workers"])
        previous = read(prior / "preflight.json")
        fields = ("executable_sha256", "configuration_sha256", "global_instructions_sha256",
                  "registry_sha256", "namespace_metadata_sha256")
        _require(all(checked.get(key) == previous.get(key) for key in fields), "client pins changed across phases")
    calls, accounting, peak, stop, historical, phases = reconcile_ledger(output, manifest, settings)
    execution = read(output / "execution.json")
    _require(execution["stopped"] is True and execution["phase_stopped"] == bool(stop)
             and execution["inherited_stops"] == recovery["inherited_stops"], "inherited or phase stop was hidden")
    _require([row["job"] for row in execution["jobs"]] == manifest["jobs"], "original fixed job inventory differs")
    plan = verify_recovery_records(output, prior, manifest, execution, calls, historical, stop)
    choices = {choice["job_id"]: choice for choice in plan["jobs"]}
    rows = {(row["job"]["task_id"], row["job"]["arm"]): row for row in execution["jobs"]}
    _require(len(rows) == len(execution["jobs"]), "duplicate recovered job result")
    schedule_audit = verify_trace(read(output / "scheduler_trace.json"), manifest["jobs"], settings["workers"])
    for row in execution["jobs"]:
        job = row["job"]
        _require(read(output / "jobs" / (job["job_id"] + ".json")) == row, "durable recovered job differs")
        _require(row["result"].get("disposition") != "controller_error"
                 and row["result"].get("reason") != "controller_error", "controller error prevents faithful replay")
    runtime = PatchRuntime()
    runtime_audit = runtime.audit()

    def replay(task):
        used = []
        prefix = None
        for arm in ("prefix", *manifest["arms"]):
            row = rows[(task["task_id"], arm)]
            choice = choices[row["job"]["job_id"]]
            owned = [call for call in calls if call["identity"]["task_id"] == task["task_id"]
                     and call["identity"]["arm"] == arm]
            replay_stop = phases["inherited_stop"] if choice["decision"] == "retain" else stop
            invoke = Replay(output, owned, replay_stop)
            if arm == "prefix":
                actual = run_prefix(task, invoke, runtime)
                prefix = actual
                contract_path = output / "factorial_contracts" / (row["job"]["job_id"] + ".json")
                if actual["eligible"]:
                    _require(read(contract_path) == factorial_contract(task, actual), "recovered factorial contract differs")
                    if choice["decision"] == "retain":
                        _require(contract_path.read_bytes() ==
                                 (prior / "factorial_contracts" / contract_path.name).read_bytes(),
                                 "retained factorial contract bytes changed")
                else:
                    _require(not contract_path.exists(), "ineligible recovered prefix has factorial contract")
            else:
                actual = run_continuation(task, arm, prefix, invoke, runtime)
            _require(comparable(actual) == comparable(row["result"]), "recovered request/state/grade replay differs")
            _require(invoke.used == {call["call_id"] for call in owned}, "cumulative admission omitted from replay")
            used.extend(sorted(invoke.used))
        return {"task_id": task["task_id"], "eligible": prefix["eligible"], "requests": used, "passed": True}

    with ThreadPoolExecutor(max_workers=RUNTIME_WORKERS) as pool:
        results = list(pool.map(replay, tasks))
    checked = [key for row in results for key in row["requests"]]
    _require(len(checked) == len(calls) and set(checked) == {call["call_id"] for call in calls},
             "cumulative replay call coverage differs")
    statuses = {call["call_id"]: call["state"] for call in calls}
    slots = [{"call_id": item.key, "disposition": statuses.get(item.key, "never_dispatched")}
             for item in identities(tasks, manifest["split"])]
    _require(read(output / "slot_dispositions.json") == slots, "original fixed generation slots differ")
    _require(analyze(tasks, execution, accounting, manifest, simulated=not settings["live"]) ==
             read(output / "analysis.json"), "cumulative analysis does not reproduce")
    report = {"passed": True, "checked_utc": now(), "evidence_kind": "offline_cumulative_received_response_replay",
        "manifest_sha256": sha(manifest), "evidence_manifest_sha256": sha(read(output / "evidence_manifest.json")),
        "prior_audit_sha256": recovery["prior_audit_sha256"], "prior_evidence_manifest_sha256": recovery["prior_evidence_manifest_sha256"],
        "model_calls": 0, "all_admissions_reconstructed": len(checked),
        "complete_responses": accounting["completed_calls"], "unknowns_preserved": accounting["unknown_or_inflight_calls"],
        "tasks": len(tasks), "factorial_contracts": sum(row["eligible"] for row in results),
        "peak_model_admissions": peak, "runtime_regrading": runtime.statistics(), "runtime_audit": runtime_audit,
        "scheduler": schedule_audit, "accounting_reconciled": True, "live_evidence": settings["live"],
        "phases": phases, "recovery_selection_counts": plan["counts"],
        "historical_unknown_jobs_preserved_exactly": True, "fixed_original_allocation_preserved": True,
        "isolated_content_interpretation_gate_permanently_failed": True, "results": results}
    save_new(destination, report)
    return {key: report[key] for key in ("passed", "model_calls", "all_admissions_reconstructed", "tasks",
                                       "factorial_contracts", "peak_model_admissions", "manifest_sha256",
                                       "evidence_manifest_sha256", "phases")}
