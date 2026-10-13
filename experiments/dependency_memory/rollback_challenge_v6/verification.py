"""Independent formulations and negative controls, never model observations."""
from copy import deepcopy
import random
from .common import sha
from .tasks import candidate, requirements, public_check


def independent(task, stage, value):
    c = task["contract"]; rs = requirements(task, stage)
    if task["family"] == "constraint_grid":
        n = c["size"]
        if len(value) != n*n or any(type(x) is not int or x not in range(1,n+1) for x in value): return False
        units = {}
        for i, x in enumerate(value):
            r, col = divmod(i,n)
            for key in (("r",r), ("c",col), ("b",r//c["box_rows"],col//c["box_cols"])):
                units.setdefault(key, []).append(x)
        if any(sorted(u) != list(range(1,n+1)) for u in units.values()): return False
        for r in rs:
            if r["kind"] == "given" and value[r["cell"]] != r["value"]: return False
            if r["kind"] == "less" and not value[r["a"]] < value[r["b"]]: return False
            if r["kind"] == "sum" and r["total"]-sum(value[i] for i in r["cells"]): return False
        return True
    if task["family"] == "bitvector_program":
        width = c["width"]; modulus = 2**width
        if len(value)%2 or len(value)>2*c["max_instructions"]: return False
        if any(type(x) is not int for x in value): return False
        if any(x not in range(4) for x in value[::2]) or any(x not in range(modulus) for x in value[1::2]): return False
        for record in rs:
            x = record["x"]
            for op, k in zip(value[::2], value[1::2]):
                if op == 0: x = (x+k)%modulus
                elif op == 1: x = sum((((x//2**i)%2+(k//2**i)%2)%2)*2**i for i in range(width))
                elif op == 2: x = (x*k)%modulus
                else:
                    bits = format(x, f"0{width}b"); r = k%width
                    x = int(bits[r:]+bits[:r],2)
            if x != record["y"]: return False
        return True
    if task["family"] == "revision_ledger":
        if len(value) != c["account_count"] or any(type(x) is not int for x in value): return False
        picked = []
        for tx in sorted({r["tx"] for r in rs}):
            revisions = sorted((r for r in rs if r["tx"] == tx), key=lambda r:(r["revision"],r["sequence"]))
            if not revisions[-1]["void"]: picked.append(revisions[-1])
        expected = [sum(r["amount"]*(int(r["destination"]==a)-int(r["source"]==a)) for r in picked) for a in range(len(value))]
        return expected == value
    raise ValueError("unknown family")


def verify_tasks(tasks):
    checks = 0; rows = []
    if not tasks or len({t["task_id"] for t in tasks}) != len(tasks): raise ValueError("empty/duplicate cohort")
    for task in tasks:
        if sha({k:v for k,v in task.items() if k != "sha256"}) != task["sha256"]: raise ValueError("task hash")
        rng = random.Random(task["evaluator"]["seed"] ^ 2026)
        for stage, reference in enumerate(task["evaluator"]["stage_references"]):
            if not independent(task, stage, reference["values"]): raise ValueError("invalid witness")
            if public_check(task,stage,reference)["status"] != "public_pass": raise ValueError("rejected witness")
            mutations = [[], reference["values"]]
            for _ in range(30):
                v = list(reference["values"])
                if v: v[rng.randrange(len(v))] += rng.choice([-2,-1,1,2])
                mutations.append(v)
            for v in mutations:
                if (public_check(task,stage,candidate(v))["status"] == "public_pass") != independent(task,stage,v):
                    raise ValueError("independent grader disagreement")
                checks += 1
        rows.append({"task_id":task["task_id"],"stages":len(task["stages"]),"witnesses_pass":True})
    return {"evidence_kind":"offline_independent_formulation_and_mutation_checks", "model_calls":0,
            "tasks_sha256":sha(tasks),"tasks":rows,"candidate_checks":checks,"all_passed":True,
            "scope":"witness and local mutation checks; not exhaustive search or empirical difficulty calibration"}
