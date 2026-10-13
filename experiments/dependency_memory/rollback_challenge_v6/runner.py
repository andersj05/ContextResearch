"""Four-worker durable execution, receipt replay and no duplicate dispatches."""
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from decimal import Decimal
import shutil
import time

from .common import ROOT, read, save_new, sha, now, wire
from .prepare import check_bundle, identities
from .engine import run_episode
from .analysis import analyze
from .contexts import render
from ..rollback_development_v5.engine import initial_state
from ..rollback_development_v5.dispatch import live_factory
from ..rollback_development_v5_continuation.dispatch import Dispatcher
from ..rollback_development_v5_continuation.accounting import Ledger
from ..rollback_development_v5.audit import ledger_rows
from ..rollback_development_v5.preflight import preflight
from ..rollback_math_followup_v4.client_audit import run_case
from ..rollback_pilot.subscription.transport import Response
from ..rollback_pilot.subscription.accounting import Usage


class ScriptedTransport:
    """A deliberately disclosed fixture: wrong once, then reference, never evidence."""
    def __init__(self,tasks): self.tasks={t["task_id"]:t for t in tasks}
    def generate(self,identity,request):
        data=read_request(request); t=self.tasks[identity.task_id]
        if identity.stage == "action":
            c={"values":[],"order":[],"files":[]} if identity.step==1 else t["evaluator"]["stage_references"][data["packet"]["stage"]-1]
            value={"status":"candidate","candidate":c,"note":"Scripted offline fixture."}
        elif identity.stage == "lesson":
            value={"established":[wire(data["feedback"])],"retained_observations":[],"uncertainties":[]}
        else: value={"summary":"Scripted offline summary fixture."}
        return Response(wire(value),Usage(max(1,len(request.json_text)//4),0,len(wire(value))//4+1,0),
                        {"thread_id":"fixture-"+identity.key,"model":"offline-scripted"},False)


def read_request(request):
    import json
    return json.loads(request.data()["messages"][1]["content"])


def run(bundle, output, *, live=False, workers=4, prior=None, executable=None, global_instructions=None):
    if type(workers) is not int or not 1<=workers<=4: raise ValueError("one through four workers")
    manifest,tasks=check_bundle(bundle)
    if live and manifest["split"]=="fixture": raise ValueError("fixture allocations cannot dispatch live generations")
    output=Path(output).resolve(); bundle=Path(bundle).resolve()
    if not output.is_relative_to(ROOT) or output.exists(): raise ValueError("new workspace result directory required")
    historical=[]
    if prior is not None:
        from .audit import audit
        prior=Path(prior).resolve(); audit(bundle,prior)
        old_settings=read(prior/"run_settings.json")
        if old_settings["live"] != live: raise ValueError("cannot mix fixture/live evidence")
        if not read(prior/"execution.json")["stopped"]: raise ValueError("completed allocation cannot be extended")
        historical,_,_=ledger_rows(prior/"ledger.sqlite")
        if any(c["state"]=="dispatched" for c in historical): raise ValueError("live calls must drain first")
        marker=prior/"continuation_started.json"
    else:
        marker=bundle/("launch_started.json" if live else "simulation_started.json")
    if marker.exists(): raise ValueError("allocation already started; inspect its existing result, never relaunch")
    output.mkdir(parents=True)
    if live:
        executable=executable or shutil.which("codex.exe") or shutil.which("codex")
        global_instructions=Path(global_instructions or Path.home()/".codex"/"AGENTS.md")
        checked=preflight(executable,global_instructions,output/"scratch")
        global_text=global_instructions.read_text(encoding="utf-8")
        samples=[render(next(t for t in tasks if t["family"]==f),initial_state(next(t for t in tasks if t["family"]==f))) for f in sorted({t["family"] for t in tasks})]
        checked["v6_payload_checks"]=[run_case(executable,global_text,r,"final_message",output/"scratch") for r in samples]
        if prior is not None:
            previous=read(prior/"preflight.json")
            if any(checked[k]!=previous[k] for k in ("executable_sha256","configuration_sha256","global_instructions_sha256","registry_sha256")):
                raise ValueError("client changed since prior phase")
        save_new(output/"preflight.json",checked)
        factory=live_factory(executable,global_instructions,checked,output/"scratch")
    else: factory=lambda:ScriptedTransport(tasks)
    save_new(marker,{"output":str(output),"started_utc":now(),"manifest_sha256":sha(manifest)})
    if prior:
        for name in ("requests","responses","diagnostics"):
            if (prior/name).exists(): shutil.copytree(prior/name,output/name)
    save_new(output/"manifest.json",manifest)
    save_new(output/"run_settings.json",{"live":live,"workers":workers,"started_utc":now(),"prior":str(prior) if prior else None})
    ledger=Ledger(output/"ledger.sqlite",identities(tasks,manifest["arms"]),workers,
                  prior=prior/"ledger.sqlite" if prior else None,generation_ceiling=manifest["generation_ceiling"])
    dispatcher=Dispatcher(output,manifest,ledger,factory,historical=historical)
    by_id={t["task_id"]:t for t in tasks}; results={}; started=time.monotonic()
    def work(job):
        # Replaying a known result/unknown is local and cannot send that identity.
        return {"job":job,"result":run_episode(by_id[job["task_id"]],job["arm"],dispatcher)}
    with ThreadPoolExecutor(max_workers=workers,thread_name_prefix="rollback-v6") as pool:
        futures={pool.submit(work,j):j for j in manifest["jobs"]}
        for future in as_completed(futures):
            job=futures[future]
            try: row=future.result()
            except Exception as error:
                ledger.stop("controller_error")
                row={"job":job,"result":{"score":None,"disposition":"controller_error","error_type":type(error).__name__}}
            results[job["job_id"]]=row
            save_new(output/"jobs"/(job["job_id"]+".json"),row)
            snapshot=ledger.snapshot()
            print(wire({"jobs_done":len(results),"jobs_total":len(futures),"completions":snapshot["completed_calls"],
                        "unknown":sum(c["state"]=="unknown" for c in snapshot["calls"]),
                        "inflight":sum(c["state"]=="dispatched" for c in snapshot["calls"]),"stop":snapshot["stop"]}),flush=True)
    execution={"jobs":[results[j["job_id"]] for j in manifest["jobs"]],"stopped":ledger.stopped(),"wall_seconds":time.monotonic()-started}
    save_new(output/"execution.json",execution)
    report=analyze(tasks,execution,ledger.snapshot(),manifest,simulated=not live)
    save_new(output/"analysis.json",report)
    save_new(output/"evidence_manifest.json",{"files":[{"path":p.relative_to(output).as_posix(),"sha256":sha(p.read_bytes())}
              for p in sorted(output.rglob("*.json")) if "scratch" not in p.relative_to(output).parts],"ledger_sha256":sha((output/"ledger.sqlite").read_bytes())})
    return {"folder":str(output),"jobs":len(results),"model_calls":len(report["accounting"]["calls"])-len(historical) if live else 0,
            "completed":report["accounting"]["completed_calls"],"stop":report["accounting"]["stop"]}
