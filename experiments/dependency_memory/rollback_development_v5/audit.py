"""Offline evidence reconciliation and replay. Never instantiates live transport."""
from dataclasses import asdict
from decimal import Decimal
from pathlib import Path
import sqlite3

from .common import read, sha, wire, IMAGE
from .accounting import Identity, Stopped
from .prepare import check_bundle
from .engine import run_episode, run_prefix
from .simulation import OracleRunner
from .calibration import cases, validate
from .analysis import analyze
from ..rollback_pilot.subscription.accounting import Usage, RESERVATION
from ..rollback_pilot.subscription.transport import Response
from ..rollback_pilot.code_runner import DockerRunner


def ledger_rows(path):
    db = sqlite3.connect(Path(path).resolve().as_uri() + "?mode=ro", uri=True)
    try:
        import json
        calls = [{"call_id": k, "identity": json.loads(i), "request_hash": h, "state": s, **json.loads(p)}
                 for k, i, h, s, p in db.execute("SELECT * FROM calls ORDER BY id")]
        events = [{"call_id": k, "state": s, "payload": json.loads(p)} for k, s, p in db.execute("SELECT call_id,state,payload FROM events ORDER BY seq")]
        stop = db.execute("SELECT reason FROM stops LIMIT 1").fetchone()
        return calls, events, stop[0] if stop else None
    finally:
        db.close()


class ReplayMismatch(RuntimeError):
    pass


class Replay:
    def __init__(self, folder, calls, stopped):
        self.folder = Path(folder); self.calls = {c["call_id"]: c for c in calls}
        self.used = set(); self.stopped = stopped

    def __call__(self, identity, request):
        key = identity.key
        call = self.calls.get(key)
        if call is None:
            if self.stopped:
                raise Stopped("recorded_global_stop")
            raise ReplayMismatch("unrecorded expected call")
        if key in self.used:
            raise ReplayMismatch("duplicate replay identity")
        self.used.add(key)
        if call["identity"] != asdict(identity) or call["request_hash"] != sha(request.json_text):
            raise ReplayMismatch("canonical request or identity mismatch")
        path = self.folder / "requests" / (key + ".json")
        if path.exists() and read(path) != request.data():
            raise ReplayMismatch("saved request differs from reconstructed public state")
        if call["state"] != "completed":
            raise Stopped("recorded_unknown_dispatch")
        if not path.is_file():
            raise ReplayMismatch("completed call lacks request")
        value = read(self.folder / "responses" / (key + ".json"))
        if value["usage"] != call["usage"] or value["metadata"] != call["metadata"]:
            raise ReplayMismatch("response and ledger disagree")
        return Response(value["text"], Usage(**value["usage"]), value["metadata"], value["capped"])


def comparable(result):
    return {k: v for k, v in result.items() if k != "elapsed_seconds"}


def reconcile_report(tasks, execution, saved, calls, stop, simulated):
    known = [c for c in calls if c["state"] == "completed"]
    unresolved = sum(c["state"] in {"unknown", "dispatched"} for c in calls)
    accounting = {"calls": calls, "completed_calls": len(known), "unknown_or_inflight_calls": unresolved,
                  "planning_credits": str(sum((Usage(**c["usage"]).cost for c in known), Decimal(0))),
                  "locked_planning_credits": str(unresolved * RESERVATION), "stop": stop,
                  "usage": {k: sum(c["usage"][k] for c in known) for k in ("input_tokens", "cached_input", "output", "reasoning")},
                  "actual_account_charge": None, "API_key_calls": 0}
    if sha(saved["accounting"]) != sha(accounting):
        raise ReplayMismatch("reported accounting differs from durable ledger")
    if sha(saved) != sha(analyze(tasks, execution, accounting, simulated=simulated)):
        raise ReplayMismatch("saved analysis differs from recorded outcomes")


def audit(bundle, folder):
    folder = Path(folder); manifest, tasks = check_bundle(bundle)
    if read(folder / "manifest.json") != manifest:
        raise ReplayMismatch("run manifest changed")
    inventory = read(folder / "evidence_manifest.json")
    actual_files = {p.relative_to(folder).as_posix() for p in folder.rglob("*.json") if p != folder / "evidence_manifest.json"}
    if len(inventory["files"]) != len(actual_files) or {r["path"] for r in inventory["files"]} != actual_files:
        raise ReplayMismatch("sealed JSON inventory is incomplete")
    for row in inventory["files"]:
        path = (folder / row["path"]).resolve()
        if not path.is_relative_to(folder.resolve()) or sha(path.read_bytes()) != row["sha256"]:
            raise ReplayMismatch("sealed evidence changed")
    if sha((folder / "ledger.sqlite").read_bytes()) != inventory["ledger_sha256"]:
        raise ReplayMismatch("ledger changed after sealing")
    calls, events, stop = ledger_rows(folder / "ledger.sqlite")
    planned = {Identity(**i).key for i in manifest["schedule"]} | {Identity(**c["identity"]).key for c in manifest["calibration"]}
    if any(c["call_id"] not in planned or Identity(**c["identity"]).key != c["call_id"] for c in calls):
        raise ReplayMismatch("unallocated call")
    active = set(); peak = 0; history = {}; unknown_seen = False
    for e in events:
        key = e["call_id"]; history.setdefault(key, []).append(e["state"])
        if e["state"] == "dispatched":
            if unknown_seen: raise ReplayMismatch("new admission after unknown dispatch")
            if key in active: raise ReplayMismatch("duplicate admission")
            active.add(key); peak = max(peak, len(active))
        else:
            if key not in active: raise ReplayMismatch("unadmitted completion")
            active.remove(key)
            unknown_seen |= e["state"] == "unknown"
    settings = read(folder / "run_settings.json")
    if peak > settings["workers"]:
        raise ReplayMismatch("global concurrency limit exceeded")
    threads = set()
    for c in calls:
        if history.get(c["call_id"]) != ["dispatched", c["state"]]:
            raise ReplayMismatch("invalid durable call transition")
        if c["state"] == "completed":
            usage = Usage(**c["usage"]).validate()
            if str(usage.cost) != c["planning_credits"]:
                raise ReplayMismatch("metering mismatch")
            thread = c["metadata"].get("thread_id")
            if not thread or thread in threads: raise ReplayMismatch("missing or reused provider thread")
            threads.add(thread)
    all_tasks = tasks + [c["task"] for c in cases()]
    runner = DockerRunner(IMAGE) if settings["live"] else OracleRunner(all_tasks)
    replay = Replay(folder, calls, stop)
    calibration = read(folder / "calibration.json")
    if settings["live"]:
        for c, row in zip(cases(), calibration["rows"]):
            if row["disposition"] == "passed":
                validate(c, replay(c["identity"], c["request"]).text, runner)
            else:
                # Invalid received calibration remains a known, charged call.
                try: replay(c["identity"], c["request"])
                except Stopped: pass
    execution = read(folder / "execution.json")
    if [r["job"] for r in execution["jobs"]] != manifest["jobs"]:
        raise ReplayMismatch("job denominator/order changed")
    by_id = {t["task_id"]: t for t in tasks}; prefixes = {}; replayed = 0
    ordered = sorted(execution["jobs"], key=lambda row: row["job"]["dependency"] is not None)
    for row in ordered:
        job, saved = row["job"], row["result"]
        if read(folder / "jobs" / (job["job_id"] + ".json")) != row:
            raise ReplayMismatch("job files disagree")
        if saved.get("disposition") in {"unstarted_global_stop", "infrastructure_error"}:
            if any(c["identity"]["task_id"] == job["task_id"] and c["identity"]["track"] == job["track"] and c["identity"]["arm"] == job["arm"] for c in calls):
                if saved["disposition"] == "unstarted_global_stop": raise ReplayMismatch("unstarted job has calls")
            continue
        if job["arm"] == "prefix":
            actual = run_prefix(by_id[job["task_id"]], replay, runner)
            if comparable(actual["outcome"]) != comparable(saved["outcome"]): raise ReplayMismatch("prefix replay mismatch")
            if {k: v for k, v in actual.items() if k != "outcome"} != {k: v for k, v in saved.items() if k != "outcome"}: raise ReplayMismatch("shared state replay mismatch")
            prefixes[job["job_id"]] = actual
        elif job["dependency"]:
            parent = prefixes.get(job["dependency"])
            if saved.get("disposition", "").startswith("ineligible_prefix:") or saved.get("disposition") in {"unusable_common_lesson", "unusable_common_summary", "paired_capacity_infeasible"}:
                continue
            if not parent or not parent.get("eligible"): raise ReplayMismatch("continuation without eligible prefix")
            actual = run_episode(by_id[job["task_id"]], job["track"], job["arm"], replay, runner, parent["state"], parent["shared"])
            if comparable(actual) != comparable(saved): raise ReplayMismatch("continuation replay mismatch")
        else:
            actual = run_episode(by_id[job["task_id"]], job["track"], job["arm"], replay, runner)
            if comparable(actual) != comparable(saved): raise ReplayMismatch("policy replay mismatch")
        replayed += 1
    if {c["call_id"] for c in calls if c["state"] == "completed"} - replay.used:
        raise ReplayMismatch("known generation omitted from replay")
    slot_rows = read(folder / "slot_dispositions.json")
    if len(slot_rows) != len(planned) or {s["call_id"] for s in slot_rows} != planned:
        raise ReplayMismatch("call-slot denominator changed")
    actual = {c["call_id"]: c["state"] for c in calls}
    if any(s["disposition"] != actual.get(s["call_id"], "never_dispatched") for s in slot_rows):
        raise ReplayMismatch("slot disposition mismatch")
    reconcile_report(tasks, execution, read(folder / "analysis.json"), calls, stop, simulated=not settings["live"])
    return {"all_passed": True, "evidence_kind": "offline_replay_and_accounting_verification", "model_calls": 0,
            "tasks": len(tasks), "jobs": len(execution["jobs"]), "replayed_jobs": replayed,
            "known_generations_replayed": sum(c["state"] == "completed" for c in calls),
            "peak_admitted_calls": peak, "live_evidence": settings["live"], "reported_analysis_and_usage_reconciled": True,
            "source_manifest_sha256": sha(manifest)}
