"""48 distinct seeded instances, balanced 4 families x 3 horizons x 2 levels x 2."""
import random
from .common import FAMILIES, HORIZONS, SEED, sha
from . import math_tasks, coding_tasks


def generate():
    tasks = []
    for fi, family in enumerate(FAMILIES):
        for hi, (horizon, (allowance, stages)) in enumerate(HORIZONS.items()):
            for hard in (False, True):
                for replicate in (1, 2):
                    seed = SEED + fi * 10000 + hi * 1000 + int(hard) * 100 + replicate
                    rng = random.Random(seed)
                    difficulty = "hard" if hard else "moderate"
                    if family in ("ledger", "resolver"):
                        contract, records, reference, initial, reserved = coding_tasks.build(family, rng, hard)
                    else:
                        contract, records, reference = getattr(math_tasks, family)(rng, hard)
                        initial = {"values": [], "order": [], "files": []}; reserved = []
                    packets = [{"requirements": records[len(records)*i//stages:len(records)*(i+1)//stages]} for i in range(stages)]
                    if any(not p["requirements"] for p in packets):
                        raise ValueError("empty disclosure is not a meaningful stage")
                    task = {"task_id": f"v5-{family}-{horizon}-{difficulty}-{replicate}", "family": family,
                            "domain": "coding" if family in ("ledger", "resolver") else "math", "horizon": horizon,
                            "difficulty": difficulty, "replicate": replicate, "action_allowance": allowance,
                            "contract": contract, "initial_artifact": initial, "stages": packets,
                            "evaluator": {"seed": seed, "reference": reference, "reserved_tests": reserved,
                                          "provenance": "repository-authored development; never a benchmark or held-out confirmation"}}
                    task["sha256"] = sha(task)
                    tasks.append(task)
    return sorted(tasks, key=lambda t: sha([SEED, t["task_id"]]))


def requirements(task, through_stage):
    return [r for p in task["stages"][:through_stage + 1] for r in p["requirements"]]


def public_check(task, stage, candidate, runner=None):
    records = requirements(task, stage)
    if task["domain"] == "coding":
        if runner is None:
            raise ValueError("isolated coding runner required")
        return coding_tasks.run_tests(candidate, [t for r in records for t in r["tests"]], runner)
    result = math_tasks.violation(task, candidate, records)
    return {"status": "public_mismatch", **result} if result else {"status": "public_pass", "checks": len(records)}


def terminal_check(task, candidate, runner=None):
    public = public_check(task, len(task["stages"]) - 1, candidate, runner)
    if public["status"] != "public_pass":
        return {"score": 0, "disposition": "public_failure"}
    if task["domain"] == "coding":
        reserved = coding_tasks.run_tests(candidate, task["evaluator"]["reserved_tests"], runner)
        return {"score": int(reserved["status"] == "public_pass"), "disposition": "correct" if reserved["status"] == "public_pass" else "reserved_failure"}
    return {"score": 1, "disposition": "correct"}
