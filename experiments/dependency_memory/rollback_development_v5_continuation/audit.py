"""Independent zero-generation reconciliation of the cumulative amended study."""
from dataclasses import asdict
from decimal import Decimal
from pathlib import Path
import json
import sqlite3

from .prepare import check_prepared, sealed_prior
from .accounting import CallUnknown
from .engine import run_prefix, run_episode
from .schedule import child_dispositions, calls_for_job
from .analysis import analyze
from ..rollback_development_v5.common import ROOT, read, sha, IMAGE
from ..rollback_development_v5.accounting import Identity, Stopped
from ..rollback_development_v5.audit import Replay as OriginalReplay, ReplayMismatch, comparable
from ..rollback_development_v5.calibration import cases, validate
from ..rollback_development_v5.simulation import OracleRunner
from ..rollback_pilot.subscription.accounting import Usage, RESERVATION
from ..rollback_pilot.code_runner import DockerRunner


class Replay(OriginalReplay):
    def __call__(self, identity, request):
        call = self.calls.get(identity.key)
        if call and call["state"] == "unknown":
            # The original checker verifies request bytes and identity before throwing.
            try:
                super().__call__(identity, request)
            except Stopped:
                if call.get("failure_scope") == "global":
                    raise Stopped("recorded_systemic_failure") from None
                raise CallUnknown("recorded_trajectory_unknown") from None
        return super().__call__(identity, request)


class AuditGate:
    def stop(self, reason):
        raise ReplayMismatch("dependency invariant: " + reason)


def accounting_from(calls, stop):
    known = [c for c in calls if c["state"] == "completed"]
    unresolved = sum(c["state"] != "completed" for c in calls)
    return {"calls": calls, "completed_calls": len(known), "unknown_or_inflight_calls": unresolved,
            "planning_credits": str(sum((Usage(**c["usage"]).cost for c in known), Decimal(0))),
            "locked_planning_credits": str(unresolved * RESERVATION), "stop": stop,
            "usage": {k: sum(c["usage"][k] for c in known) for k in ("input_tokens", "cached_input", "output", "reasoning")},
            "actual_account_charge": None, "API_key_calls": 0}


def audit(prepared, folder):
    folder = Path(folder).resolve()
    manifest, tasks, historical, prior_events = check_prepared(prepared)
    base = read(ROOT / manifest["continuation"]["original_bundle"] / "manifest.json")
    sealed, calls, events = sealed_prior(folder, base)
    if read(folder / "manifest.json") != manifest:
        raise ReplayMismatch("run amendment manifest differs")
    if read(folder / "prior_execution.json") != read(ROOT / manifest["continuation"]["prior_phase"] / "execution.json"):
        raise ReplayMismatch("saved prior outcomes differ")
    settings = read(folder / "run_settings.json")
    execution = read(folder / "execution.json")
    stop = sealed["previous_stop"]
    expected_calls = {c["call_id"]: c for c in historical}
    current = {c["call_id"]: c for c in calls}
    if any(current.get(k) != c for k, c in expected_calls.items()) or events[:len(prior_events)] != prior_events:
        raise ReplayMismatch("historical receipts or event prefix changed")
    if len(calls) > manifest["continuation"]["generation_ceiling"]:
        raise ReplayMismatch("cumulative admission ceiling exceeded")
    allocation = {Identity(**i).key: i for i in manifest["schedule"] + [c["identity"] for c in manifest["calibration"]]}
    if len(allocation) != manifest["possible_total_call_identities"]:
        raise ReplayMismatch("fixed identity allocation differs")
    if any(c["call_id"] not in allocation or c["identity"] != allocation[c["call_id"]] for c in calls):
        raise ReplayMismatch("unallocated identity")
    active = set(); history = {}; peak = 0; fatal_seen = False
    for index, event in enumerate(events):
        key = event["call_id"]
        history.setdefault(key, []).append(event["state"])
        if event["state"] == "dispatched":
            if fatal_seen or key in active:
                raise ReplayMismatch("admission after systemic failure or duplicate admission")
            active.add(key); peak = max(peak, len(active))
        elif event["state"] in {"completed", "unknown"}:
            if key not in active:
                raise ReplayMismatch("completion without admission")
            active.remove(key)
            if index >= len(prior_events) and event["state"] == "unknown":
                fatal_seen |= event["payload"].get("failure_scope") == "global"
        else:
            raise ReplayMismatch("invalid call state")
    if active or peak > settings["workers"] or settings["workers"] > 4:
        raise ReplayMismatch("inflight calls or concurrency bound differs")
    threads = {}
    for call in calls:
        if history.get(call["call_id"]) != ["dispatched", call["state"]]:
            raise ReplayMismatch("identity dispatched more than once")
        if call["state"] == "completed":
            usage = Usage(**call["usage"]).validate()
            if str(usage.cost) != call["planning_credits"] or usage.cost > RESERVATION:
                raise ReplayMismatch("usage/cost bound differs")
            thread = call["metadata"].get("thread_id")
            if type(thread) is not str or not thread or thread in threads:
                raise ReplayMismatch("missing/reused provider thread")
            threads[thread] = call["call_id"]
        elif call.get("reserve_credits") != str(RESERVATION):
            raise ReplayMismatch("unknown reservation released")
    db = sqlite3.connect((folder / "ledger.sqlite").as_uri() + "?mode=ro", uri=True)
    try:
        if dict(db.execute("SELECT thread_id,call_id FROM threads")) != threads:
            raise ReplayMismatch("thread table differs from durable completions")
        config = json.loads(db.execute("SELECT payload FROM config WHERE id=1").fetchone()[0])
        if config != {"identities": sha(allocation), "max_inflight": settings["workers"]}:
            raise ReplayMismatch("ledger admission configuration differs")
        if json.loads(db.execute("SELECT payload FROM continuation_config WHERE id=1").fetchone()[0]) != {
                "generation_ceiling": manifest["continuation"]["generation_ceiling"]}:
            raise ReplayMismatch("ledger ceiling differs")
    finally:
        db.close()
    all_tasks = tasks + [c["task"] for c in cases()]
    runner = DockerRunner(IMAGE) if settings["live"] else OracleRunner(all_tasks)
    replay = Replay(folder, calls, bool(stop))
    if settings["live"]:
        for case in cases():
            validate(case, replay(case["identity"], case["request"]).text, runner)
    if execution["stopped"] != bool(stop) or [r["job"] for r in execution["jobs"]] != manifest["jobs"]:
        raise ReplayMismatch("global stop or job denominator/order differs")
    old = {r["job"]["job_id"]: r for r in read(folder / "prior_execution.json")["jobs"]}
    by_id = {t["task_id"]: t for t in tasks}; prefixes = {}; replayed = 0
    for row in sorted(execution["jobs"], key=lambda r: r["job"]["dependency"] is not None):
        job, saved = row["job"], row["result"]
        if read(folder / "jobs" / (job["job_id"] + ".json")) != row:
            raise ReplayMismatch("saved job disagrees with aggregate")
        origin = execution["origins"][job["job_id"]]
        if origin["prior_result_sha256"] != sha(old[job["job_id"]]):
            raise ReplayMismatch("prior job binding differs")
        if origin["kind"] == "retained_previous_phase" and row != old[job["job_id"]]:
            raise ReplayMismatch("retained outcome changed")
        if saved.get("disposition") == "unstarted_global_stop":
            if not stop or calls_for_job(job, calls):
                raise ReplayMismatch("unstarted job has calls or no systemic stop")
            continue
        if saved.get("disposition") == "infrastructure_error":
            raise ReplayMismatch("unreplayed controller failure requires a separate diagnostic investigation")
        task = by_id[job["task_id"]]
        if job["arm"] == "prefix":
            actual = run_prefix(task, replay, runner)
            if comparable(actual["outcome"]) != comparable(saved["outcome"]) or {
                    k: v for k, v in actual.items() if k != "outcome"} != {k: v for k, v in saved.items() if k != "outcome"}:
                raise ReplayMismatch("prefix/shared state replay differs: " + job["job_id"])
            prefixes[job["job_id"]] = actual
        elif job["dependency"]:
            parent = prefixes.get(job["dependency"])
            if parent is None:
                if stop and saved.get("disposition", "").startswith("ineligible_prefix:infrastructure"):
                    continue
                raise ReplayMismatch("missing dependency state")
            reason = child_dispositions(task, parent, [job], AuditGate())[0][1]
            if reason:
                if saved != {"score": None, "disposition": reason, "call_ids": []} or calls_for_job(job, calls):
                    raise ReplayMismatch("dependency skip differs")
                continue
            actual = run_episode(task, job["track"], job["arm"], replay, runner, parent["state"], parent["shared"])
            if comparable(actual) != comparable(saved):
                raise ReplayMismatch("child replay differs: " + job["job_id"])
        else:
            actual = run_episode(task, job["track"], job["arm"], replay, runner)
            if comparable(actual) != comparable(saved):
                raise ReplayMismatch("independent episode replay differs: " + job["job_id"])
        replayed += 1
    if replay.used != set(current):
        raise ReplayMismatch("admitted generation omitted from independent replay")
    slots = read(folder / "slot_dispositions.json")
    if len(slots) != len(allocation) or {r["call_id"]: r["identity"] for r in slots} != allocation:
        raise ReplayMismatch("slot denominator differs")
    if any(r["disposition"] != current.get(r["call_id"], {}).get("state", "never_dispatched") for r in slots):
        raise ReplayMismatch("slot disposition differs")
    account = accounting_from(calls, stop)
    if sha(read(folder / "analysis.json")) != sha(analyze(tasks, execution, account, manifest, simulated=not settings["live"])):
        raise ReplayMismatch("analysis and durable usage/outcomes differ")
    return {"all_passed": True, "evidence_kind": "offline_replay_and_accounting_verification", "model_calls": 0,
            "live_evidence": settings["live"], "tasks": len(tasks), "jobs": len(execution["jobs"]),
            "replayed_jobs": replayed, "known_generations_replayed": account["completed_calls"],
            "unknown_generations_reconciled": account["unknown_or_inflight_calls"], "peak_admitted_calls": peak,
            "new_admissions": len(calls) - len(historical), "original_receipts_unchanged": True,
            "reported_analysis_and_usage_reconciled": True, "amendment_manifest_sha256": sha(manifest)}
