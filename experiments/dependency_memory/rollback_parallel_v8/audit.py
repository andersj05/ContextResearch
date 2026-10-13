"""Replay every archived request, public grade, matched checkpoint and meter.

No live transport is instantiated. Unknown responses remain missing, and the
replay distinguishes their local stop from a global admission failure.
"""
from dataclasses import asdict
from decimal import Decimal
from pathlib import Path

from .accounting import Identity, Stopped, CallUnknown, check_workers
from .common import read, sha
from .prepare import check_bundle, identities
from .engine import run_prefix, run_continuation, pair_contract
from ..rollback_checkpoint_v7.contexts import parse_action
from .analysis import analyze
from .trace_audit import verify_trace
from .client import RESOURCE_HELPERS, REGISTRY_SHA256, NAMESPACE_SHA256
from ..rollback_challenge_v6.verification import independent
from ..rollback_development_v5.audit import ReplayMismatch, ledger_rows
from ..rollback_pilot.records import strict_loads
from ..rollback_pilot.subscription.accounting import Usage, RESERVATION
from ..rollback_pilot.subscription.transport import Response


EMPTY_MCP_INVENTORY = {"server_count": 1, "disabled_server_count": 1,
                       "tool_count": 0, "resource_count": 0,
                       "resource_template_count": 0, "complete_inventory": True}


def comparable(value):
    """Only nondeterministic runtime measurements are excluded from replay."""
    if type(value) is dict:
        return {key: comparable(item) for key, item in value.items()
                if key not in {"elapsed_seconds", "wall_seconds"}}
    if type(value) is list:
        return [comparable(item) for item in value]
    return value


class Replay:
    def __init__(self, folder, calls, stop):
        self.folder = Path(folder)
        self.calls = {call["call_id"]: call for call in calls}
        self.used = set()
        self.stop = stop

    def __call__(self, identity, request):
        key = identity.key
        call = self.calls.get(key)
        if call is None:
            if self.stop:
                raise Stopped("recorded_global_stop")
            raise ReplayMismatch("unrecorded expected call")
        if key in self.used:
            raise ReplayMismatch("repeated replay identity")
        self.used.add(key)
        if call["identity"] != asdict(identity) or call["request_hash"] != sha(request.json_text):
            raise ReplayMismatch("canonical request or identity mismatch")
        path = self.folder / "requests" / (key + ".json")
        if not path.is_file() or read(path) != request.data():
            raise ReplayMismatch("saved request differs from reconstructed public state")
        if call["state"] == "unknown":
            if call.get("failure_scope") == "trajectory":
                raise CallUnknown("recorded_unknown_dispatch")
            raise Stopped("recorded_global_stop")
        if call["state"] != "completed":
            raise ReplayMismatch("unfinished admitted call")
        value = read(self.folder / "responses" / (key + ".json"))
        if value["usage"] != call["usage"] or value["metadata"] != call["metadata"]:
            raise ReplayMismatch("response and ledger disagree")
        return Response(value["text"], Usage(**value["usage"]),
                        value["metadata"], value["capped"])


def _inventory(folder):
    inventory = read(folder / "evidence_manifest.json")
    expected = {row["path"] for row in inventory["files"]}
    observed = {path.relative_to(folder).as_posix() for path in folder.rglob("*.json")
                if "scratch" not in path.relative_to(folder).parts
                and path.name != "evidence_manifest.json"}
    if len(expected) != len(inventory["files"]) or expected != observed:
        raise ReplayMismatch("sealed JSON evidence inventory mismatch")
    for row in inventory["files"]:
        path = (folder / row["path"]).resolve()
        if not path.is_relative_to(folder.resolve()) or sha(path.read_bytes()) != row["sha256"]:
            raise ReplayMismatch("sealed evidence changed")
    if sha((folder / "ledger.sqlite").read_bytes()) != inventory["ledger_sha256"]:
        raise ReplayMismatch("ledger changed after sealing")


def _metering(calls, events, stop, manifest, settings):
    planned = {Identity(**item).key: item for item in manifest["schedule"]}
    if len(calls) > manifest["generation_ceiling"]:
        raise ReplayMismatch("generation ceiling exceeded")
    if any(planned.get(call["call_id"]) != call["identity"] for call in calls):
        raise ReplayMismatch("unallocated identity")
    states, active, peak, fatal_seen = {}, set(), 0, False
    for event in events:
        key, state = event["call_id"], event["state"]
        states.setdefault(key, []).append(state)
        if state == "dispatched":
            if key in active or len(states[key]) != 1 or fatal_seen:
                raise ReplayMismatch("repeated admission or admission after fatal failure")
            if event["payload"].get("reserve_credits") != str(RESERVATION):
                raise ReplayMismatch("missing full admission reservation")
            active.add(key)
            peak = max(peak, len(active))
        else:
            if key not in active or state not in {"completed", "unknown"}:
                raise ReplayMismatch("unadmitted or invalid completion")
            active.remove(key)
            fatal_seen |= state == "unknown" and event["payload"].get("failure_scope") == "global"
    if active or peak > settings["workers"] or set(states) != {call["call_id"] for call in calls}:
        raise ReplayMismatch("inflight, identity or concurrency invariant")
    threads = set()
    for call in calls:
        if states.get(call["call_id"]) != ["dispatched", call["state"]]:
            raise ReplayMismatch("invalid durable call transitions")
        if call["state"] == "completed":
            usage = Usage(**call["usage"]).validate()
            if str(usage.cost) != call["planning_credits"] or usage.cost > RESERVATION:
                raise ReplayMismatch("metering or reservation mismatch")
            metadata = call["metadata"]
            thread = metadata.get("thread_id")
            if type(thread) is not str or not thread or thread in threads:
                raise ReplayMismatch("missing or reused provider thread")
            threads.add(thread)
            if settings["live"] and (metadata.get("model") != manifest["model"]
                                      or metadata.get("reasoning_effort") != manifest["effort"]
                                      or metadata.get("harness_termination") != "sessionBudgetExceeded"
                                      or metadata.get("usage_events") != 1
                                      or metadata.get("tool_items") != 0):
                raise ReplayMismatch("model, effort or one-generation isolation evidence mismatch")
            if settings["live"] and (metadata.get("mcp_resource_isolation") != EMPTY_MCP_INVENTORY
                                      or metadata.get("preflight_registry_sha256") != REGISTRY_SHA256):
                raise ReplayMismatch("live MCP inventory or pinned registry evidence mismatch")
        elif call["state"] == "unknown":
            if call.get("reserve_credits") != str(RESERVATION):
                raise ReplayMismatch("unknown reservation lost")
            if call.get("failure_scope") not in {"trajectory", "global"}:
                raise ReplayMismatch("unknown failure scope missing")
            if call["failure_scope"] == "global" and not stop:
                raise ReplayMismatch("systemic fault did not stop admissions")
        else:
            raise ReplayMismatch("unresolved inflight admission")
    known = [call for call in calls if call["state"] == "completed"]
    unknown = len(calls) - len(known)
    accounting = {
        "calls": calls, "completed_calls": len(known), "unknown_or_inflight_calls": unknown,
        "planning_credits": str(sum((Usage(**call["usage"]).cost for call in known), Decimal(0))),
        "locked_planning_credits": str(unknown * RESERVATION), "stop": stop,
        "usage": {key: sum(call["usage"][key] for call in known)
                  for key in ("input_tokens", "cached_input", "output", "reasoning")},
        "actual_account_charge": None, "API_key_calls": 0,
    }
    return accounting, peak


def independent_action_regrading(tasks, execution, calls, folder):
    """Compare every graded action with the independent sorted-ledger checker.

    Engine replay alone could reproduce the same checker defect. This pass uses
    archived candidates and the stage declared in the reconstructed request,
    then compares the independent formulation with the *recorded* receipt.
    Capped and malformed records stay charged evidence but are not relabeled as
    mathematical candidate failures. Unknown calls are never imputed.
    """
    folder = Path(folder)
    by_id = {task["task_id"]: task for task in tasks}
    receipts = {}
    for row in execution["jobs"]:
        job, result = row["job"], row["result"]
        outcome = result["outcome"] if job["arm"] == "prefix" else result
        for event in outcome["events"]:
            key = (job["task_id"], job["arm"], event["step"])
            if key in receipts:
                raise ReplayMismatch("duplicate graded action receipt")
            receipts[key] = event
    counts = {"checked": 0, "public_pass": 0, "public_mismatch": 0,
              "invalid_candidate": 0, "capped_records_preserved": 0,
              "malformed_or_disallowed_records_preserved": 0,
              "unknown_actions_preserved": 0}
    consumed = set()
    for call in calls:
        identity = call["identity"]
        if identity["stage"] != "action":
            continue
        key = (identity["task_id"], identity["arm"], identity["step"])
        receipt = receipts.get(key)
        if call["state"] != "completed":
            if receipt is not None:
                raise ReplayMismatch("unknown action has a grading receipt")
            counts["unknown_actions_preserved"] += 1
            continue
        value = read(folder / "responses" / (call["call_id"] + ".json"))
        if value["capped"]:
            if receipt is not None:
                raise ReplayMismatch("capped action has a grading receipt")
            counts["capped_records_preserved"] += 1
            continue
        try:
            action = parse_action(strict_loads(value["text"]))
            if action["status"] != "candidate":
                raise ValueError("candidate_required")
        except (ValueError, KeyError, TypeError):
            if receipt is not None:
                raise ReplayMismatch("malformed action has a grading receipt") from None
            counts["malformed_or_disallowed_records_preserved"] += 1
            continue
        request = read(folder / "requests" / (call["call_id"] + ".json"))
        visible = strict_loads(request["messages"][1]["content"])
        stage = visible["current_stage"] - 1
        task = by_id[identity["task_id"]]
        if task["family"] != "revision_ledger":
            raise ReplayMismatch("v8 independent audit requires the declared ledger family")
        if receipt is None or receipt["stage"] != stage + 1:
            raise ReplayMismatch("valid candidate lacks its stage grading receipt")
        candidate = action["candidate"]
        if candidate["order"] or candidate["files"]:
            expected = "invalid_candidate"
        else:
            expected = ("public_pass" if independent(task, stage, candidate["values"])
                        else "public_mismatch")
        if receipt["status"] != expected:
            raise ReplayMismatch("independent action grader disagreement")
        consumed.add(key)
        counts["checked"] += 1
        counts[expected] += 1
    if consumed != set(receipts):
        raise ReplayMismatch("unreconciled graded action receipt")
    return counts


def verify_live_preflight(checked, workers):
    checks = checked.get("v8_parallel_payload_checks", [])
    if (checked.get("serialization_and_retry_audit_passed") is not True
            or checked.get("v8_payload_schema_audit_passed") is not True
            or checked.get("v8_verified_workers") != workers
            or len(checks) != workers
            or checked.get("real_model_generations") != 0
            or any(case.get("http_attempts") != 1 or not case.get("accepted_transport")
                   or case.get("authorization_present") is not False
                   or case.get("real_model_generations") != 0 for case in checks)):
        raise ReplayMismatch("parallel client preflight evidence mismatch")
    if (checked.get("registry_sha256") != REGISTRY_SHA256
            or checked.get("namespace_metadata_sha256") != NAMESPACE_SHA256
            or checked.get("declared_inert_mcp_helpers") != list(RESOURCE_HELPERS)
            or checked.get("mcp_inventory_checked_before_every_generation") is not True):
        raise ReplayMismatch("client compatibility contract differs")
    for helper in RESOURCE_HELPERS:
        probes = [case for case in checked.get("cases", []) if case.get("case") == helper]
        if (len(probes) != 1 or probes[0].get("accepted_transport") is not False
                or probes[0].get("http_attempts") != 1
                or probes[0].get("authorization_present") is not False
                or probes[0].get("real_model_generations") != 0
                or probes[0].get("safe_failure_reason") != {"reason_code": "tool_or_external_information_attempt"}
                or probes[0].get("mcp_resource_isolation") != EMPTY_MCP_INVENTORY):
            raise ReplayMismatch("resource helper negative probe differs")
    if any(case.get("mcp_resource_isolation") != EMPTY_MCP_INVENTORY for case in checks):
        raise ReplayMismatch("parallel client MCP inventory differs")
    diagnostics = checked.get("compatibility_diagnostics", [])
    if len(diagnostics) != 1:
        raise ReplayMismatch("client observation-limit diagnostic missing")
    diagnostic = diagnostics[0]
    observation = diagnostic.get("protocol_observation", {})
    if (diagnostic.get("case") != "clock_with_answer"
            or diagnostic.get("diagnostic_only") is not True
            or diagnostic.get("accepted_transport") is not True
            or diagnostic.get("http_attempts") != 1
            or diagnostic.get("authorization_present") is not False
            or diagnostic.get("real_model_generations") != 0
            or diagnostic.get("mcp_resource_isolation") != EMPTY_MCP_INVENTORY
            or "sessionBudgetExceeded" not in observation.get("server_error_codes", [])
            or observation.get("method_counts", {}).get("thread/tokenUsage/updated") != 1):
        raise ReplayMismatch("client observation-limit diagnostic differs")


def audit(bundle, folder):
    folder = Path(folder).resolve()
    manifest, tasks = check_bundle(bundle)
    if read(folder / "manifest.json") != manifest:
        raise ReplayMismatch("run and frozen bundle differ")
    _inventory(folder)
    settings = read(folder / "run_settings.json")
    check_workers(settings["workers"])
    if settings["workers"] != manifest["workers"] or settings["retries"] != 0 or settings["prior"] is not None:
        raise ReplayMismatch("worker, retry or fresh-allocation contract changed")
    if settings["live"]:
        verify_live_preflight(read(folder / "preflight.json"), settings["workers"])
    calls, events, stop = ledger_rows(folder / "ledger.sqlite")
    accounting, peak = _metering(calls, events, stop, manifest, settings)
    if accounting != read(folder / "accounting.json"):
        raise ReplayMismatch("saved accounting differs from durable ledger")
    replay = Replay(folder, calls, stop)
    execution = read(folder / "execution.json")
    schedule_audit = verify_trace(read(folder / "scheduler_trace.json"), manifest["jobs"], settings["workers"])
    if execution["stopped"] != bool(stop):
        raise ReplayMismatch("execution and global stop differ")
    if [row["job"] for row in execution["jobs"]] != manifest["jobs"]:
        raise ReplayMismatch("fixed job denominator or order changed")
    by_id = {task["task_id"]: task for task in tasks}
    prefixes, contracts = {}, 0
    rows = sorted(execution["jobs"], key=lambda row: row["job"]["arm"] != "prefix")
    for row in rows:
        job, saved = row["job"], row["result"]
        if read(folder / "jobs" / (job["job_id"] + ".json")) != row:
            raise ReplayMismatch("durable job record differs")
        if saved.get("disposition") == "controller_error":
            raise ReplayMismatch("controller error prevents faithful replay")
        task = by_id[job["task_id"]]
        if job["arm"] == "prefix":
            actual = run_prefix(task, replay)
            prefixes[job["task_id"]] = actual
            if read(folder / "prefixes" / (job["job_id"] + ".json")) != saved:
                raise ReplayMismatch("durable prefix record differs")
            path = folder / "pair_contracts" / (job["job_id"] + ".json")
            if actual.get("eligible"):
                proof = pair_contract(task, actual)
                if proof.get("passed") is not True or not path.is_file() or read(path) != proof:
                    raise ReplayMismatch("matched checkpoint contract differs")
                contracts += 1
            elif path.exists():
                raise ReplayMismatch("ineligible prefix has a matched contract")
        else:
            if job["task_id"] not in prefixes:
                raise ReplayMismatch("continuation lacks common prefix")
            actual = run_continuation(task, job["arm"], prefixes[job["task_id"]], replay)
        if comparable(actual) != comparable(saved):
            raise ReplayMismatch("request/state/grader replay differs")
    if replay.used != {call["call_id"] for call in calls}:
        raise ReplayMismatch("admitted generation omitted from replay")
    # This overlap count comes from durable call events, independently of the
    # scheduler's separate monotonic timing trace.
    call_arms = {call["call_id"]: call["identity"]["arm"] for call in calls}
    prefix_ends = [event["payload"].get("completed_utc", event["payload"].get("observed_utc"))
                   for event in events if call_arms[event["call_id"]] == "prefix"
                   and event["state"] in {"completed", "unknown"}]
    last_prefix_call = max(prefix_ends) if prefix_ends else None
    overlap = sum(event["state"] == "dispatched" and call_arms[event["call_id"]] in {"K", "R"}
                  and event["payload"]["admitted_utc"] < last_prefix_call
                  for event in events) if last_prefix_call else 0
    schedule_audit["continuation_admissions_before_last_prefix_completion"] = overlap
    independent_grades = independent_action_regrading(tasks, execution, calls, folder)
    statuses = {call["call_id"]: call["state"] for call in calls}
    slots = [{"call_id": identity.key, "disposition": statuses.get(identity.key, "never_dispatched")}
             for identity in identities(tasks)]
    if read(folder / "slot_dispositions.json") != slots:
        raise ReplayMismatch("call-slot denominator or disposition differs")
    if analyze(tasks, execution, accounting, manifest, simulated=not settings["live"]) != read(folder / "analysis.json"):
        raise ReplayMismatch("analysis does not reproduce")
    return {"all_passed": True, "evidence_kind": "offline_receipt_replay_and_regrading",
            "model_calls": 0, "tasks": len(tasks), "jobs": len(execution["jobs"]),
            "received_calls_replayed": accounting["completed_calls"],
            "unknowns_preserved": accounting["unknown_or_inflight_calls"],
            "independent_action_grades": independent_grades["checked"],
            "independent_action_regrading": independent_grades,
            "matched_context_contracts": contracts, "peak_admitted_calls": peak,
            "live_evidence": settings["live"], "accounting_reconciled": True,
            "scheduler": schedule_audit}
