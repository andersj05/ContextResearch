"""Read-only sealed-evidence reconciliation and isolated response replay.

ReplayMismatch deliberately is not a ValueError: malformed model output may be
scored by the engine, but a missing or changed evidence record must abort audit.
"""
from concurrent.futures import ThreadPoolExecutor
from copy import deepcopy
from dataclasses import asdict
from pathlib import Path
import json
import sqlite3

from .common import read, save_new, sha, now, RUNTIME_WORKERS
from .prepare import check_bundle, identities
from .engine import run_prefix, run_continuation, factorial_contract
from .analysis import analyze
from .runtime import PatchRuntime
from .scheduler import TRACE_SCHEMA
from ..rollback_checkpoint_v7.audit import (
    Replay as BaseReplay, comparable, _inventory, _metering, EMPTY_MCP_INVENTORY,
)
from ..rollback_parallel_v8.audit import verify_live_preflight as verify_old_preflight
from ..rollback_parallel_v8.trace_audit import verify_trace as verify_old_trace
from ..rollback_development_v5.audit import ReplayMismatch, ledger_rows


class Replay(BaseReplay):
    def __init__(self, folder, calls, stop):
        if len({call["call_id"] for call in calls}) != len(calls):
            raise ReplayMismatch("duplicate saved call")
        super().__init__(folder, calls, stop)


def verify_trace(trace, jobs, workers):
    """The v8 ordering proof is arm-name independent; retain the v9 schema gate."""
    if trace.get("schema") != TRACE_SCHEMA:
        raise ReplayMismatch("scheduler schema differs")
    translated = deepcopy(trace)
    translated["schema"] = "rollback-v8-dependency-scheduler-trace-v1"
    try:
        return verify_old_trace(translated, jobs, workers)
    except (ValueError, KeyError, TypeError) as error:
        raise ReplayMismatch("scheduler trace differs: " + str(error)) from error


def verify_live_preflight(checked, workers):
    parallel = checked.get("v9_parallel_checks", [])
    payloads = checked.get("v9_payload_checks", [])
    if (checked.get("v9_factorial_serialization_passed") is not True
            or checked.get("v9_verified_workers") != workers
            or len(parallel) != workers or not payloads
            or len(checked.get("v9_request_hashes", [])) != len(payloads)):
        raise ReplayMismatch("v9 serialization coverage differs")
    for case in payloads + parallel:
        if (case.get("http_attempts") != 1 or case.get("accepted_transport") is not True
                or case.get("authorization_present") is not False
                or case.get("real_model_generations") != 0
                or case.get("mcp_resource_isolation") != EMPTY_MCP_INVENTORY):
            raise ReplayMismatch("v9 payload isolation differs")
    translated = deepcopy(checked)
    translated.update(v8_parallel_payload_checks=parallel, v8_payload_schema_audit_passed=True,
                      v8_verified_workers=checked["v9_verified_workers"])
    verify_old_preflight(translated, workers)


def reconcile_ledger(folder, manifest, settings):
    """Use durable SQLite rows, then independently verify event payloads/config."""
    calls, events, stop = ledger_rows(folder / "ledger.sqlite")
    if len({call["call_id"] for call in calls}) != len(calls):
        raise ReplayMismatch("duplicate durable call")
    accounting, peak = _metering(calls, events, stop, manifest, settings)
    if accounting != read(folder / "accounting.json"):
        raise ReplayMismatch("saved accounting differs from durable ledger")
    by_id = {call["call_id"]: call for call in calls}
    for event in events:
        if event["state"] == "dispatched":
            if set(event["payload"]) != {"admitted_utc", "reserve_credits"}:
                raise ReplayMismatch("admission payload differs")
        else:
            payload = {key: value for key, value in by_id[event["call_id"]].items()
                       if key not in {"call_id", "identity", "request_hash", "state"}}
            if payload != event["payload"]:
                raise ReplayMismatch("terminal event payload differs from call")
    db = sqlite3.connect((folder / "ledger.sqlite").resolve().as_uri() + "?mode=ro", uri=True)
    try:
        planned = {item.key: asdict(item) for item in identities_from_manifest(manifest)}
        config = [json.loads(row[0]) for row in db.execute("SELECT payload FROM config")]
        ceiling = [json.loads(row[0]) for row in db.execute("SELECT payload FROM continuation_config")]
        threads = set(db.execute("SELECT thread_id,call_id FROM threads"))
        expected_threads = {(call["metadata"]["thread_id"], call["call_id"])
                            for call in calls if call["state"] == "completed"}
        if config != [{"identities": sha(planned), "max_inflight": settings["workers"]}]:
            raise ReplayMismatch("ledger allocation or worker binding differs")
        if ceiling != [{"generation_ceiling": manifest["generation_ceiling"]}]:
            raise ReplayMismatch("ledger ceiling differs")
        if threads != expected_threads or db.execute("SELECT 1 FROM inherited_stops").fetchone():
            raise ReplayMismatch("thread inventory or fresh-allocation contract differs")
    finally:
        db.close()
    request_ids = {path.stem for path in (folder / "requests").glob("*.json")}
    response_ids = {path.stem for path in (folder / "responses").glob("*.json")}
    completed_ids = {call["call_id"] for call in calls if call["state"] == "completed"}
    if request_ids != set(by_id) or not completed_ids <= response_ids <= set(by_id):
        raise ReplayMismatch("request/response inventory differs from admissions")
    # A response written before a completion-accounting failure remains unknown.
    # It is preserved as evidence, never promoted into a received-call replay.
    for path in (folder / "diagnostics").glob("*.json"):
        call = by_id.get(path.stem)
        if call is None or call["state"] != "unknown" or read(path) != call.get("diagnostic"):
            raise ReplayMismatch("unknown diagnostic differs")
    return calls, accounting, peak, stop


def identities_from_manifest(manifest):
    from ..rollback_development_v5.accounting import Identity
    values = [Identity(**item) for item in manifest["schedule"]]
    if len({item.key for item in values}) != len(values):
        raise ReplayMismatch("duplicate frozen generation slot")
    return values


def audit(bundle, output, destination):
    manifest, tasks = check_bundle(bundle)
    output, destination = Path(output).resolve(), Path(destination).resolve()
    if destination.is_relative_to(output):
        raise ValueError("audit_report_must_be_outside_sealed_run")
    if read(output / "manifest.json") != manifest:
        raise ReplayMismatch("run manifest changed")
    _inventory(output)
    settings = read(output / "run_settings.json")
    if (settings["workers"] != manifest["workers"] or settings["retries"] != 0
            or settings.get("prior") is not None or type(settings["live"]) is not bool):
        raise ReplayMismatch("worker, retry, live or fresh-allocation contract differs")
    if settings["live"]:
        verify_live_preflight(read(output / "preflight.json"), settings["workers"])
    calls, accounting, peak, stop = reconcile_ledger(output, manifest, settings)
    execution = read(output / "execution.json")
    if execution["stopped"] != bool(stop):
        raise ReplayMismatch("execution and global stop differ")
    if [row["job"] for row in execution["jobs"]] != manifest["jobs"]:
        raise ReplayMismatch("fixed job denominator or order differs")
    schedule_audit = verify_trace(read(output / "scheduler_trace.json"), manifest["jobs"], settings["workers"])
    rows = {(row["job"]["task_id"], row["job"]["arm"]): row for row in execution["jobs"]}
    if len(rows) != len(execution["jobs"]):
        raise ReplayMismatch("duplicate job result")
    for row in execution["jobs"]:
        job = row["job"]
        if read(output / "jobs" / (job["job_id"] + ".json")) != row:
            raise ReplayMismatch("durable job differs")
        if row["result"].get("disposition") == "controller_error" or row["result"].get("reason") == "controller_error":
            raise ReplayMismatch("controller error prevents faithful replay")
    runtime = PatchRuntime()
    runtime_audit = runtime.audit()

    def replay(task):
        received = [call for call in calls if call["identity"]["task_id"] == task["task_id"]]
        invoke = Replay(output, received, stop)
        prefix = run_prefix(task, invoke, runtime)
        prefix_row = rows[(task["task_id"], "prefix")]
        if comparable(prefix) != comparable(prefix_row["result"]):
            raise ReplayMismatch("prefix replay disagrees: " + task["task_id"])
        proof_path = output / "factorial_contracts" / (prefix_row["job"]["job_id"] + ".json")
        if prefix["eligible"]:
            if read(proof_path) != factorial_contract(task, prefix):
                raise ReplayMismatch("factorial contract differs")
        elif proof_path.exists():
            raise ReplayMismatch("ineligible prefix has factorial contract")
        for arm in manifest["arms"]:
            actual = run_continuation(task, arm, prefix, invoke, runtime)
            if comparable(actual) != comparable(rows[(task["task_id"], arm)]["result"]):
                raise ReplayMismatch("continuation replay disagrees: " + task["task_id"] + ":" + arm)
        if invoke.used != {call["call_id"] for call in received}:
            raise ReplayMismatch("admitted generation omitted from replay")
        return {"task_id": task["task_id"], "eligible": prefix["eligible"],
                "requests": sorted(invoke.used), "passed": True}

    with ThreadPoolExecutor(max_workers=RUNTIME_WORKERS) as pool:
        results = list(pool.map(replay, tasks))
    checked = [key for row in results for key in row["requests"]]
    if set(checked) != {call["call_id"] for call in calls} or len(checked) != len(calls):
        raise ReplayMismatch("replay call coverage differs")
    statuses = {call["call_id"]: call["state"] for call in calls}
    slots = [{"call_id": item.key, "disposition": statuses.get(item.key, "never_dispatched")}
             for item in identities(tasks, manifest["split"])]
    if read(output / "slot_dispositions.json") != slots:
        raise ReplayMismatch("fixed generation-slot denominator or disposition differs")
    if analyze(tasks, execution, accounting, manifest, simulated=not settings["live"]) != read(output / "analysis.json"):
        raise ReplayMismatch("analysis does not reproduce")
    report = {"passed": True, "checked_utc": now(), "evidence_kind": "offline_received_response_replay",
              "manifest_sha256": sha(manifest),
              "evidence_manifest_sha256": sha(read(output / "evidence_manifest.json")),
              "model_calls": 0, "all_admissions_reconstructed": len(checked),
              "complete_responses": accounting["completed_calls"],
              "unknowns_preserved": accounting["unknown_or_inflight_calls"],
              "tasks": len(tasks), "factorial_contracts": sum(row["eligible"] for row in results),
              "peak_model_admissions": peak, "runtime_regrading": runtime.statistics(),
              "runtime_audit": runtime_audit, "scheduler": schedule_audit,
              "accounting_reconciled": True, "live_evidence": settings["live"], "results": results}
    save_new(destination, report)
    return {key: report[key] for key in ("passed", "model_calls", "all_admissions_reconstructed", "tasks", "factorial_contracts", "peak_model_admissions", "manifest_sha256", "evidence_manifest_sha256")}
