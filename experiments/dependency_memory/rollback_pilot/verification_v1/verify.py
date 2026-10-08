"""Additional grading-evidence checks over the sealed authored pilot verifier."""
import argparse
from collections import Counter
from pathlib import Path

from ..accounting import Identity
from ..controller import write_new
from ..code_runner import DockerRunner
from ..grading import terminal_grade, CodeChecker, MathChecker
from ..records import Record, digest, wire, strict_loads
from ..subscription.accounting import Ledger
from ..cohort_v1.run import read, lines


def execution_module(folder):
    version=read(Path(folder)/"manifest.json")["version"]
    if version=="rollback-authored-subscription-E2-1":
        from ..cohort_v1 import run
    elif version=="rollback-authored-subscription-E2-2":
        from ..cohort_v2 import run
    else:raise ValueError("unknown archived execution version")
    return run


def verify(folder, *, regrade=False):
    folder=Path(folder)
    execution=execution_module(folder)
    result=execution.verify(folder,False)
    manifest,pairs=execution.check_frozen(folder)
    tasks={t.task_id:(t,e) for t,e in pairs}
    ledger=Ledger(folder/"ledger.sqlite",max_calls=312)
    try:
        calls=ledger.rows()
    finally:
        ledger.close()
    expected=[]
    for row in lines(folder/"tasks.jsonl"):
        task,evaluator=tasks[row["task_id"]]
        if "initial_grade" in row:
            candidates=[]
            for call in calls.values():
                identity=Identity(**call["identity"])
                if identity.task_id==task.task_id and identity.stage=="branch" and call["state"]=="completed":
                    branch=read(folder/"responses"/(identity.key+".json"))
                    material=strict_loads(branch["text"])
                    if material.get("status")=="candidate":candidates.append(material["artifact"])
            if len(candidates)!=1 or row["public_failure"] or row["scheduled_arms"] or "public_pass" not in row["flow"]:
                raise ValueError("initial success violated public-pass stopping")
            candidate=candidates[0]
            if task.domain=="math":
                grade=terminal_grade(task,evaluator,Record.parse("terminal",wire(candidate),task))
                if grade!=row["initial_grade"]:
                    raise ValueError("initial math grading evidence mismatch")
            else:
                expected.append((task.task_id,digest(candidate["code"]),row["initial_grade"]["score"]))
        if task.domain=="coding":
            for call in calls.values():
                identity=Identity(**call["identity"])
                if identity.task_id!=task.task_id or identity.stage!="terminal" or call["state"]!="completed":continue
                response=read(folder/"responses"/(identity.key+".json"))
                try:artifact=Record.parse("terminal",response["text"],task).data()
                except Exception:continue
                if row["terminal_dispositions"][identity.arm][identity.draw-1] in {"correct","test_failure"}:
                    expected.append((task.task_id,digest(artifact["code"]),row["grades"][identity.arm][identity.draw-1]))
    grades=read(folder/"coding_grades.json")
    actual=[]
    for item in grades:
        task,evaluator=tasks[item["task_id"]]
        tests=task.data()["public_examples"]+evaluator.data()["private_tests"]
        grade=item["grade"]
        outcomes=grade["tests"]
        if item["actor_sha256"]!=task.hash or [x["id"] for x in outcomes] != [x["id"] for x in tests[:len(outcomes)]] or len(outcomes)>len(tests):
            raise ValueError("reserved coding suite or actor coverage mismatch")
        passed=len(outcomes)==len(tests) and all(x["status"]=="public_pass" for x in outcomes)
        if grade["score"]!=int(passed) or grade["disposition"]!=("correct" if passed else "test_failure"):
            raise ValueError("coding score is inconsistent with retained test outcomes")
        if any(type(x.get("elapsed_seconds")) not in (int,float) or x["elapsed_seconds"]<0 for x in outcomes if "elapsed_seconds" in x):
            raise ValueError("invalid grading elapsed time")
        actual.append((task.task_id,item["code_sha256"],grade["score"]))
    if Counter(actual)!=Counter(expected):
        raise ValueError("missing, duplicate or unsupported coding grade evidence")
    result.update(independent_initial_math_grades=True,complete_coding_grade_evidence_checked=len(grades),
                  archive_identity_authentication="local source/evidence bindings; not authenticated provider server internals")
    if regrade:
        result.update(regraded_in_Docker=True,independent_rechecks=recheck(folder,manifest,pairs,calls))
    return result


def recheck(folder,manifest,pairs,calls):
    """Re-execute every candidate's public check and every scored retained suite."""
    checker=CodeChecker(DockerRunner(manifest["runtime_image"]))
    rows={r["task_id"]:r for r in lines(folder/"tasks.jsonl")}
    tasks={t.task_id:(t,e) for t,e in pairs}
    results=[]
    for call in calls.values():
        identity=Identity(**call["identity"])
        if call["state"]!="completed" or identity.stage not in {"branch","terminal"}:continue
        task,evaluator=tasks[identity.task_id]
        response=read(folder/"responses"/(identity.key+".json"))
        material=strict_loads(response["text"])
        row=rows[identity.task_id]
        if identity.stage=="branch":
            if material.get("status")!="candidate":continue
            candidate=material["artifact"]
            receipt=(MathChecker(task).receipt(candidate,f"B{identity.slot}",f"F{identity.slot}") if task.domain=="math"
                     else checker.receipt(task,candidate,f"B{identity.slot}",f"F{identity.slot}"))
            if receipt.data()["status"] not in row["flow"] or receipt.eligible!=row["public_failure"]:
                raise ValueError("public disposition differs from isolated recheck")
            result={"task_id":task.task_id,"call_id":identity.key,"public_receipt":receipt.data()}
            if receipt.eligible:
                if receipt.data()!=read(folder/"preparations"/(digest(task.task_id)+".json"))["feedback"]:
                    raise ValueError("public failure receipt differs from isolated recheck")
            if "initial_grade" in row:
                grade=terminal_grade(task,evaluator,Record.parse("terminal",wire(candidate),task),checker)
                if {k:grade[k] for k in ("score","disposition")}!={k:row["initial_grade"][k] for k in ("score","disposition")}:
                    raise ValueError("initial retained-suite grade differs from isolated recheck")
                result["retained_grade"]=grade
        else:
            if row["terminal_dispositions"][identity.arm][identity.draw-1] not in {"correct","test_failure","constraint_failure"}:continue
            output=Record.parse("terminal",response["text"],task)
            grade=terminal_grade(task,evaluator,output,checker)
            if grade["score"]!=row["grades"][identity.arm][identity.draw-1]:
                raise ValueError("terminal retained-suite grade differs from isolated recheck")
            result={"task_id":task.task_id,"call_id":identity.key,"arm":identity.arm,"draw":identity.draw,"retained_grade":grade}
        results.append(result)
        print(wire({"independent_recheck":identity.task_id,"stage":identity.stage,"arm":identity.arm}),flush=True)
    return results


if __name__=="__main__":
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--folder",type=Path,required=True)
    parser.add_argument("--output",type=Path)
    parser.add_argument("--regrade",action="store_true")
    args=parser.parse_args()
    value=verify(args.folder,regrade=args.regrade)
    if args.output:write_new(args.output,wire(value)+"\n")
    print(wire(value))
