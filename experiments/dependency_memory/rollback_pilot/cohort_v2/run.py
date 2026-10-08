"""Freeze, launch and verify the disclosed authored subscription engineering pilot."""
from __future__ import annotations

import argparse
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

from ..accounting import Identity
from ..code_runner import DockerRunner
from ..controller import write_new
from ..grading import PublicReceipt, MathChecker, terminal_grade, CodeChecker
from ..math_tasks import generate_math
from ..prepare import ROOT
from ..records import ActorTask, EvaluatorTask, Record, digest, strict_loads, wire, InterfaceError
from ..schedule import ordered_tasks, task_slots
from ..subscription.accounting import Ledger, Usage, RESERVATION
from ..subscription.calibration import bindings as prior_bindings, check_bindings, verify as verify_e1
from ..subscription.profile import Renderer, source_ids
from ..subscription.transport import SubscriptionTransport
from .authored import generate
from ..cohort_v1.analysis import analyze, markdown
from ..cohort_v1.controller import Controller, RecordingCodeChecker

PACKAGE = Path(__file__).resolve().parent
LAUNCH_ID = "ROLLBACK_AUTHORED_E2_SUBSCRIPTION_2026-10-08_V2"


def read(path):
    return strict_loads(Path(path).read_text(encoding="utf-8"))


def lines(path):
    return [strict_loads(x) for x in Path(path).read_text(encoding="utf-8").splitlines()]


def bindings():
    from ..cohort_v1.run import bindings as first_bindings
    return first_bindings() + [{"path": p.relative_to(ROOT).as_posix(), "sha256": digest(p.read_bytes())}
                              for p in sorted(PACKAGE.iterdir()) if p.is_file() and p.suffix in {".py", ".md"}]


def cohort():
    pairs = generate_math() + generate()
    by_id = {t.task_id: (t,e) for t,e in pairs}
    return [by_id[t.task_id] for t in ordered_tasks([t for t,e in pairs])]


def schedule(tasks, launch_id):
    indices, rows = {"math":0, "coding":0}, []
    for task in tasks:
        rows.extend(vars(x) for x in task_slots(launch_id, task, indices[task.domain]))
        indices[task.domain] += 1
    return rows


def freeze(folder, e1_folder, reference_path):
    folder, e1_folder = Path(folder), Path(e1_folder)
    verified = verify_e1(e1_folder)
    e1 = read(e1_folder / "summary.json")
    if e1["known_format_valid"] != 8 or e1["transport_stopped"]:
        raise ValueError("eight successful E1 interfaces required")
    references = read(reference_path)
    if not references["all_references_passed"] or references["model_calls"] != 0 or references["retained_test_executions"] != 156:
        raise ValueError("complete isolated reference validation required")
    pairs = cohort()
    coding = {t.task_id:(t,e) for t,e in pairs if t.domain=="coding"}
    if len(references["tasks"]) != 12 or len({r["task_id"] for r in references["tasks"]}) != 12:
        raise ValueError("twelve distinct validated references required")
    for row in references["tasks"]:
        t,e = coding[row["task_id"]]
        if row["actor_sha256"] != t.hash or row["evaluator_sha256"] != digest(e.material_json) or row["grade"]["score"] != 1 or len(row["grade"]["tests"]) != 13:
            raise ValueError("reference material or complete grade mismatch")
    # Bind the original independent finite certification instead of relabelling it as new.
    math_path = ROOT / "experiments/dependency_memory/results/rollback_e0_2026-10-08/math_certificates.json"
    e0_public = lines(ROOT / "experiments/dependency_memory/results/rollback_e0_2026-10-08/launch_review/tasks_public.jsonl")
    if {t.task_id:t.hash for t,e in pairs if t.domain=="math"} != {r["task_id"]:r["actor_sha256"] for r in e0_public}:
        raise ValueError("math tasks differ from independently checked E0 cohort")
    runtime = DockerRunner(references["runtime"]["configuration"]["image"]).audit()
    renderer = Renderer()
    if any(not renderer.fits(renderer.render("checkpoint",t)) for t,e in pairs):
        raise ValueError("initial task body fails admission")
    folder.mkdir(parents=True, exist_ok=False)
    write_new(folder / "tasks_public.jsonl", "".join(wire({"task_id":t.task_id,"domain":t.domain,"stratum":t.stratum,"public":t.data(),"actor_sha256":t.hash})+"\n" for t,e in pairs))
    write_new(folder / "tasks_evaluator.jsonl", "".join(wire({"task_id":t.task_id,"actor_sha256":t.hash,"material":e.data()})+"\n" for t,e in pairs))
    planned = schedule([t for t,e in pairs], LAUNCH_ID)
    write_new(folder / "schedule.jsonl", "".join(wire(x)+"\n" for x in planned))
    write_new(folder / "reference_checks.json", wire(references)+"\n")
    write_new(folder / "runtime_audit.json", wire(runtime)+"\n")
    write_new(folder / "preflight.json", (e1_folder / "preflight.json").read_text(encoding="utf-8"))
    manifest = {"version":"rollback-authored-subscription-E2-2", "frozen_at_utc":datetime.now(timezone.utc).isoformat(),
                "launch_id":LAUNCH_ID, "scope":"corrected Python-language retest of the same 24 tasks; not independent confirmation or LiveCodeBench v0.2",
                "model":"gpt-6-luna", "reasoning_effort":"medium", "speed":"standard", "immutable_model_revision":None,
                "provider_sampling_seed":None, "local_order_seed":20261007, "math_base_seed":20261008,"coding_base_seed":2026100803,
                "authorization":"User selected existing Codex subscription and removed token/cost budget constraints for finishing implementation and tests.",
                "source_amendment":"Explicit Python 3.11 requirement on every original coding task. Same 24-task cohort, references and tests as version 1; post-observation engineering retest.",
                "allocation":{"generation_attempt_ceiling":312,"planning_credit_ceiling":None,"automatic_retries":False,
                              "per_attempt_conditional_reservation_credits":str(RESERVATION),"API_dollars_authorized":"0","credit_fallback":False,"credit_purchase":False},
                "limits":{"complete_client_body_max_UTF8_bytes":32768,"writer_visible_UTF8_byte_cap":1024,"provider_configurable_output_cap":None},
                "runtime_image":runtime["configuration"]["image"], "task_ids":[t.task_id for t,e in pairs], "schedule":planned,
                "task_counts":dict(Counter(t.domain for t,e in pairs)),"source_bindings":bindings(),
                "calibration_evidence":{"path":e1_folder.resolve().relative_to(ROOT).as_posix(),"manifest_sha256":digest((e1_folder/"evidence_manifest.json").read_bytes()),"verified":verified},
                "independent_math_certificate":{"path":math_path.relative_to(ROOT).as_posix(),"sha256":digest(math_path.read_bytes()),"candidates":210656},
                "frozen_artifacts":[{"path":p.name,"sha256":digest(p.read_bytes())} for p in sorted(folder.iterdir())]}
    write_new(folder / "manifest.json",wire(manifest)+"\n")
    check_frozen(folder)
    return manifest


def check_frozen(folder, check_sources=True):
    folder = Path(folder).resolve()
    manifest = read(folder / "manifest.json")
    if manifest["launch_id"] != LAUNCH_ID or manifest["model"] != "gpt-6-luna" or manifest["reasoning_effort"] != "medium":
        raise ValueError("launch identity/model mismatch")
    if manifest["allocation"] != {"generation_attempt_ceiling":312,"planning_credit_ceiling":None,"automatic_retries":False,
         "per_attempt_conditional_reservation_credits":str(RESERVATION),"API_dollars_authorized":"0","credit_fallback":False,"credit_purchase":False}:
        raise ValueError("allocation changed")
    if check_sources:
        check_bindings(manifest["source_bindings"])
    for row in manifest["frozen_artifacts"]:
        p = (folder / row["path"]).resolve()
        if not p.is_relative_to(folder) or p.is_symlink() or digest(p.read_bytes()) != row["sha256"]:
            raise ValueError("frozen task artifact changed")
    pairs = []
    public, private = lines(folder / "tasks_public.jsonl"), lines(folder / "tasks_evaluator.jsonl")
    for a,e in zip(public,private,strict=True):
        task=ActorTask.from_dict(a["task_id"],a["stratum"],a["public"])
        evaluator=EvaluatorTask(e["task_id"],e["actor_sha256"],wire(e["material"]))
        evaluator.check_binding(task)
        if task.hash != a["actor_sha256"] or task.domain != a["domain"]:
            raise ValueError("actor material changed")
        pairs.append((task,evaluator))
    expected=cohort()
    if [(t.task_id,t.hash,e.material_json) for t,e in pairs] != [(t.task_id,t.hash,e.material_json) for t,e in expected]:
        raise ValueError("cohort differs from independent construction")
    planned=schedule([t for t,e in pairs],LAUNCH_ID)
    if manifest["task_ids"] != [t.task_id for t,e in pairs] or manifest["schedule"] != planned or lines(folder/"schedule.jsonl") != planned or len(planned)!=312:
        raise ValueError("frozen schedule changed")
    for row in (manifest["independent_math_certificate"],):
        p=(ROOT/row["path"]).resolve()
        if not p.is_relative_to(ROOT) or digest(p.read_bytes()) != row["sha256"]:
            raise ValueError("independent certificate changed")
    cal=manifest["calibration_evidence"]
    if digest((ROOT/cal["path"]/"evidence_manifest.json").read_bytes()) != cal["manifest_sha256"]:
        raise ValueError("calibration evidence changed")
    return manifest,pairs


def slot_dispositions(manifest, rows, ledger_rows):
    tasks={r["task_id"]:r for r in rows}
    result=[]
    for slot in manifest["schedule"]:
        identity=Identity(**slot)
        latest=ledger_rows.get(identity.key)
        row={"call_id":identity.key,"identity":slot,"dispatch_state":latest["state"] if latest else "not_dispatched"}
        if slot["stage"]=="terminal":
            task=tasks[slot["task_id"]]
            row.update(disposition=task["terminal_dispositions"][slot["arm"]][slot["draw"]-1],score=task["grades"][slot["arm"]][slot["draw"]-1])
        result.append(row)
    return result


def launch(folder, executable, global_instructions, scratch_root):
    folder=Path(folder)
    manifest,pairs=check_frozen(folder)
    verify_e1(ROOT/manifest["calibration_evidence"]["path"])
    write_new(folder/"launch_started.json",wire({"started_at_utc":datetime.now(timezone.utc).isoformat(),"manifest_sha256":digest((folder/"manifest.json").read_bytes())})+"\n")
    transport=SubscriptionTransport(executable,global_instructions,read(folder/"preflight.json"),scratch_root)
    controller=Controller(folder,manifest,transport,RecordingCodeChecker(DockerRunner(manifest["runtime_image"])))
    try:
        rows=controller.run(pairs)
        result=analyze(rows,controller.ledger.events())
        write_new(folder/"analysis.json",wire(result)+"\n")
        write_new(folder/"report.md",markdown(result))
        write_new(folder/"slot_dispositions.jsonl","".join(wire(x)+"\n" for x in slot_dispositions(manifest,rows,controller.ledger.rows())))
        controller.ledger.close()
        seal(folder)
        return result
    except BaseException:
        controller.ledger.close()
        raise


def seal(folder):
    folder=Path(folder)
    write_new(folder/"evidence_manifest.json",wire({"files":[{"path":p.relative_to(folder).as_posix(),"bytes":p.stat().st_size,"sha256":digest(p.read_bytes())}
              for p in sorted(folder.rglob("*")) if p.is_file() and p.name!="ledger.sqlite"]})+"\n")


def verify(folder, regrade=False):
    folder=Path(folder).resolve()
    manifest,pairs=check_frozen(folder)
    evidence=read(folder/"evidence_manifest.json")
    expected=set()
    for row in evidence["files"]:
        p=(folder/row["path"]).resolve()
        if row["path"] in expected or not p.is_relative_to(folder) or p.is_symlink() or p.stat().st_size != row["bytes"] or digest(p.read_bytes()) != row["sha256"]:
            raise ValueError("archive evidence binding mismatch")
        expected.add(row["path"])
    actual={p.relative_to(folder).as_posix() for p in folder.rglob("*") if p.is_file()}-{"ledger.sqlite","evidence_manifest.json"}
    if actual!=expected:
        raise ValueError("unexpected or missing archive evidence")
    if read(folder/"launch_started.json")["manifest_sha256"] != digest((folder/"manifest.json").read_bytes()):
        raise ValueError("launch marker differs from frozen allocation")
    ledger=Ledger(folder/"ledger.sqlite",max_calls=312)
    try:
        events=ledger.events()
        if events != lines(folder/"usage_events.jsonl") or ledger.summary()!=read(folder/"accounting.json"):
            raise ValueError("durable ledger/export mismatch")
        rows=lines(folder/"tasks.jsonl")
        if [r["task_id"] for r in rows]!=manifest["task_ids"]:
            raise ValueError("selected tasks omitted or reordered")
        if any(read(folder/"task_dispositions"/(digest(r["task_id"])+".json"))!=r for r in rows):
            raise ValueError("task disposition mismatch")
        slots=slot_dispositions(manifest,rows,ledger.rows())
        if slots != lines(folder/"slot_dispositions.jsonl"):
            raise ValueError("slot dispositions differ from task/ledger")
        result=analyze(rows,events)
        if result!=read(folder/"analysis.json") or markdown(result)!=(folder/"report.md").read_text(encoding="utf-8"):
            raise ValueError("analysis differs from task-level recomputation")
        valid_ids={x["call_id"] for x in slots}
        thread_ids=set()
        for key,r in ledger.rows().items():
            if key not in valid_ids:
                raise ValueError("unscheduled identity dispatched")
            states=[x["state"] for x in events if x["call_id"]==key]
            if states not in (["planned"],["planned","reserved"],["planned","reserved","dispatched"],["planned","reserved","dispatched","completed"],["planned","reserved","dispatched","unknown"]):
                raise ValueError("invalid dispatch lifecycle")
            if r["state"] not in {"planned","reserved"} and digest(wire(read(folder/"requests"/(key+".json")))) != r["request_hash"]:
                raise ValueError("dispatched request hash mismatch")
            if r["state"]=="completed":
                response=read(folder/"responses"/(key+".json"))
                usage=Usage(**r["usage"])
                if str(usage.cost)!=r["planning_credits"] or response["usage"]!=r["usage"] or response["metadata"]!=r["metadata"]:
                    raise ValueError("saved response/usage/credit mismatch")
                thread=r["metadata"]["thread_id"]
                if thread in thread_ids or r["metadata"]["tool_items"]!=0 or r["metadata"]["model"]!="gpt-6-luna":
                    raise ValueError("shared continuity, tool access or model mismatch")
                thread_ids.add(thread)
        verify_contexts(folder,manifest,pairs,rows,ledger.rows(),regrade)
        return {"verified_tasks":len(rows),"verified_possible_slots":len(slots),"completed_generations":result["resources"]["known_completed_calls"],
                "unknown_or_pending":result["resources"]["unknown_or_pending_calls"],"planning_credits":result["resources"]["shared_experiment_planning_credits"],
                "source_bindings":len(manifest["source_bindings"]),"evidence_files":len(expected),"regraded_in_Docker":regrade}
    finally:
        ledger.close()


def verify_contexts(folder,manifest,pairs,rows,ledger_rows,regrade):
    renderer=Renderer()
    checker=CodeChecker(DockerRunner(manifest["runtime_image"])) if regrade else None
    by_id={r["task_id"]:r for r in rows}
    coding_grades=read(folder/"coding_grades.json")
    for task,evaluator in pairs:
        row=by_id[task.task_id]
        checkpoint,branches,lesson,summary,feedback=None,[],None,None,None
        prep=folder/"preparations"/(digest(task.task_id)+".json")
        prepared=read(prep) if prep.exists() else None
        if prepared:
            feedback=PublicReceipt(wire(prepared["feedback"]))
        relevant=[r for r in ledger_rows.values() if r["identity"]["task_id"]==task.task_id and r["state"]=="completed"]
        # Ledger insertion order equals actual request order; do not replay grades into input.
        for call in relevant:
            identity=Identity(**call["identity"])
            request=(renderer.continuation(identity.arm,task,checkpoint,branches,feedback,lesson,summary) if identity.stage=="terminal"
                     else renderer.render(identity.stage,task,checkpoint,branches if identity.stage!="checkpoint" else (),feedback if identity.stage in {"lesson","summary"} else None))
            if request.hash!=call["request_hash"] or request.data()!=read(folder/"requests"/(identity.key+".json")):
                raise ValueError("canonical input includes unexpected information")
            response=read(folder/"responses"/(identity.key+".json"))
            supplied=source_ids(task)
            if checkpoint:
                supplied.update(f"C.fact{i+1}" for i in range(len(checkpoint.data()["facts"])))
            for i,b in enumerate(branches):
                supplied.add(f"B{i+1}")
                supplied.update(f"B{i+1}.observation{j+1}" for j in range(len(b.data()["observations"])))
            if feedback and identity.stage in {"lesson","summary","terminal"}:
                supplied.add(feedback.data()["receipt_id"])
            try:
                if identity.stage in {"lesson","summary"} and len(response["text"].encode("utf-8"))>1024:
                    raise InterfaceError("writer_visible_byte_cap")
                parsed=Record.parse(identity.stage,response["text"],task,supplied=supplied,
                                    option_ids=[x["id"] for x in checkpoint.data()["tentative_options"]] if checkpoint else [])
            except InterfaceError:
                if identity.stage=="terminal" and row["grades"][identity.arm][identity.draw-1]!=0:
                    raise ValueError("invalid terminal not counted as failure")
                continue
            if identity.stage=="checkpoint": checkpoint=parsed
            elif identity.stage=="branch":
                branches.append(parsed)
                if regrade and parsed.data()["status"]=="candidate":
                    candidate=parsed.data()["artifact"]
                    receipt=(MathChecker(task).receipt(candidate,f"B{identity.slot}",f"F{identity.slot}") if task.domain=="math"
                             else checker.receipt(task,candidate,f"B{identity.slot}",f"F{identity.slot}"))
                    if prepared and receipt.data()!=prepared["feedback"]:
                        raise ValueError("public feedback differs from independent recheck")
                    if "initial_grade" in row:
                        terminal=Record.parse("terminal",wire(candidate),task)
                        grade=terminal_grade(task,evaluator,terminal,checker)
                        if {k:grade[k] for k in ("score","disposition")} != {k:row["initial_grade"][k] for k in ("score","disposition")}:
                            raise ValueError("initial candidate grade differs from recheck")
            elif identity.stage=="lesson": lesson=parsed
            elif identity.stage=="summary": summary=parsed
            elif identity.stage=="terminal":
                if regrade or task.domain=="math":
                    grade=terminal_grade(task,evaluator,parsed,checker)
                    if grade["score"]!=row["grades"][identity.arm][identity.draw-1]:
                        raise ValueError("terminal grade differs from independent recheck")
                elif not any(g["task_id"]==task.task_id and g["code_sha256"]==digest(parsed.data()["code"]) and g["grade"]["score"]==row["grades"][identity.arm][identity.draw-1] for g in coding_grades):
                    raise ValueError("terminal grade lacks saved code execution evidence")
        if prepared and (checkpoint.data()!=prepared["checkpoint"] or [b.data() for b in branches]!=prepared["branch"] or (lesson.data() if lesson else None)!=prepared["lesson"] or (summary.data() if summary else None)!=prepared["summary"]):
            raise ValueError("preparation differs from parsed model records")


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode",choices=("freeze","launch","verify"))
    parser.add_argument("--folder",type=Path,required=True)
    parser.add_argument("--e1-folder",type=Path)
    parser.add_argument("--reference-checks",type=Path)
    parser.add_argument("--executable",type=Path)
    parser.add_argument("--global-instructions",type=Path)
    parser.add_argument("--scratch-root",type=Path)
    parser.add_argument("--regrade",action="store_true")
    args=parser.parse_args()
    if args.mode=="freeze":
        value=freeze(args.folder,args.e1_folder,args.reference_checks)
        value={"frozen_tasks":len(value["task_ids"]),"possible_call_slots":len(value["schedule"])}
    elif args.mode=="launch":
        value=launch(args.folder,args.executable,args.global_instructions,args.scratch_root)["resources"]
    else:
        value=verify(args.folder,args.regrade)
    print(wire(value))


if __name__=="__main__":
    main()
