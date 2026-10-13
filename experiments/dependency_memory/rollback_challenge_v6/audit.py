"""Offline replay of every saved call, grader, outcome and metering total."""
from decimal import Decimal
from pathlib import Path

from .common import read, sha
from .prepare import check_bundle
from .engine import run_episode
from .analysis import analyze
from ..rollback_development_v5.audit import Replay, ReplayMismatch, ledger_rows, comparable
from ..rollback_development_v5.accounting import Identity
from ..rollback_pilot.subscription.accounting import Usage, RESERVATION


def audit(bundle,folder):
    folder=Path(folder); m,tasks=check_bundle(bundle)
    if read(folder/"manifest.json") != m: raise ReplayMismatch("run/bundle mismatch")
    inventory=read(folder/"evidence_manifest.json")
    expected={r["path"] for r in inventory["files"]}
    observed={p.relative_to(folder).as_posix() for p in folder.rglob("*.json") if "scratch" not in p.relative_to(folder).parts and p.name not in {"evidence_manifest.json","continuation_started.json"}}
    if len(expected)!=len(inventory["files"]) or expected != observed: raise ReplayMismatch("evidence inventory mismatch")
    for row in inventory["files"]:
        path=(folder/row["path"]).resolve()
        if not path.is_relative_to(folder.resolve()) or sha(path.read_bytes()) != row["sha256"]: raise ReplayMismatch("evidence changed")
    if sha((folder/"ledger.sqlite").read_bytes())!=inventory["ledger_sha256"]: raise ReplayMismatch("ledger changed")
    calls,events,stop=ledger_rows(folder/"ledger.sqlite")
    planned={Identity(**i).key: i for i in m["schedule"]}
    if len(calls)>m["generation_ceiling"] or any(planned.get(c["call_id"])!=c["identity"] for c in calls): raise ReplayMismatch("allocation exceeded")
    states={}; active=set(); threads=set(); peak=0
    for event in events:
        key=event["call_id"]; states.setdefault(key,[]).append(event["state"])
        if event["state"]=="dispatched":
            if key in active: raise ReplayMismatch("repeated admission")
            active.add(key); peak=max(peak,len(active))
        else:
            if key not in active: raise ReplayMismatch("unadmitted result")
            active.remove(key)
    settings=read(folder/"run_settings.json")
    if active or peak>settings["workers"]: raise ReplayMismatch("inflight/concurrency invariant")
    for c in calls:
        if states.get(c["call_id"]) != ["dispatched",c["state"]] or c["state"] not in {"completed","unknown"}: raise ReplayMismatch("invalid call transitions")
        if c["state"]=="completed":
            u=Usage(**c["usage"]).validate()
            if str(u.cost)!=c["planning_credits"]: raise ReplayMismatch("cost mismatch")
            thread=c["metadata"].get("thread_id")
            if not thread or thread in threads: raise ReplayMismatch("thread reused")
            threads.add(thread)
    replay=Replay(folder,calls,stop); execution=read(folder/"execution.json")
    if execution["stopped"] != bool(stop): raise ReplayMismatch("execution/global-stop mismatch")
    if [r["job"] for r in execution["jobs"]] != m["jobs"]: raise ReplayMismatch("fixed job denominator changed")
    by_id={t["task_id"]:t for t in tasks}
    for row in execution["jobs"]:
        job=row["job"]
        if read(folder/"jobs"/(job["job_id"]+".json")) != row: raise ReplayMismatch("job changed")
        result=run_episode(by_id[job["task_id"]],job["arm"],replay)
        if comparable(result)!=comparable(row["result"]): raise ReplayMismatch("episode/grader replay differs")
    if replay.used != {c["call_id"] for c in calls}: raise ReplayMismatch("unreplayed calls")
    known=[c for c in calls if c["state"]=="completed"]; unknown=len(calls)-len(known)
    accounting={"calls":calls,"completed_calls":len(known),"unknown_or_inflight_calls":unknown,
                "planning_credits":str(sum((Usage(**c["usage"]).cost for c in known),Decimal(0))),
                "locked_planning_credits":str(unknown*RESERVATION),"stop":stop,
                "usage":{k:sum(c["usage"][k] for c in known) for k in ("input_tokens","cached_input","output","reasoning")},
                "actual_account_charge":None,"API_key_calls":0}
    if analyze(tasks,execution,accounting,m,simulated=not settings["live"]) != read(folder/"analysis.json"): raise ReplayMismatch("analysis mismatch")
    return {"all_passed":True,"evidence_kind":"offline_receipt_replay_and_regrading","model_calls":0,
            "received_calls_replayed":len(known),"unknowns_preserved":unknown,"jobs":len(execution["jobs"]),
            "peak_admitted_calls":peak,"live_evidence":settings["live"]}
