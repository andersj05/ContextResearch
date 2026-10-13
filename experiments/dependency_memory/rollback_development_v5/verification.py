"""Independent task checks and real isolated reference execution; zero generations."""
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
import itertools
import random
import time

from .common import IMAGE, SEED, sha, wire
from .tasks import requirements, public_check, terminal_check
from .coding_tasks import run_tests
from .math_tasks import violation
from ..rollback_pilot.code_runner import DockerRunner


def independent_math(task, candidate, records):
    c = task["contract"]
    if task["family"] == "scheduling":
        starts = candidate["values"]; durations = c["durations"]
        if candidate["files"] or candidate["order"] or len(starts) != len(durations): return False
        if any(type(v) is not int or v < c["start_bounds"][0] or v > c["start_bounds"][1] for v in starts): return False
        intervals = [(v, v + d) for v, d in zip(starts, durations)]
        checks = []
        for r in records:
            if r["kind"] == "window": checks += [intervals[r["job"]][0] >= r["release"], intervals[r["job"]][1] <= r["deadline"]]
            if r["kind"] == "precedence": checks += [intervals[r["b"]][0] - intervals[r["a"]][1] >= r["lag"]]
            if r["kind"] == "linear":
                dot = sum(map(lambda p: p[0] * p[1], zip(r["coefficients"], starts)))
                checks += [r["minimum"] <= dot <= r["maximum"]]
            if r["kind"] == "machines":
                for i, j in itertools.combinations(range(len(starts)), 2):
                    if r["assignment"][i] == r["assignment"][j]: checks += [max(intervals[i][0], intervals[j][0]) >= min(intervals[i][1], intervals[j][1])]
        return all(checks)
    tour = candidate["order"]; n = c["node_count"]
    if candidate["files"] or candidate["values"] or any(type(i) is not int for i in tour) or sorted(tour) != list(range(1, n)): return False
    rows = {r["from"]: r["costs"] for r in records if r["kind"] == "travel"}
    path = [0] + tour + [0]; times = {}; edges = list(zip(path, path[1:]))
    for pos, node in enumerate(path[1:], 1):
        prefix = edges[:pos]
        if all(a in rows for a, b in prefix): times[node] = sum(rows[a][b] for a, b in prefix)
    for r in records:
        if r["kind"] == "before" and tour.index(r["a"]) >= tour.index(r["b"]): return False
        if r["kind"] == "visit_window" and r["node"] in times and not r["earliest"] <= times[r["node"]] <= r["latest"]: return False
        if r["kind"] == "route_budget" and 0 in times and times[0] > r["maximum"]: return False
    return True


def check_math(task):
    rng = random.Random(task["evaluator"]["seed"] + 90)
    reference = task["evaluator"]["reference"]; candidates = [reference]
    if task["family"] == "scheduling":
        n = len(reference["values"]); bound = task["contract"]["start_bounds"][1]
        candidates += [{"values": [rng.randint(-1, bound + 1) for _ in range(n)], "order": [], "files": []} for _ in range(500)]
        # Local perturbations near a witness exercise individual constraint failures.
        for j in range(n):
            for delta in (-2, -1, 1, 2):
                v = list(reference["values"]); v[j] += delta
                candidates.append({"values": v, "order": [], "files": []})
        exhaustive = False
    else:
        candidates += [{"values": [], "order": list(v), "files": []} for v in itertools.permutations(reference["order"])]
        exhaustive = True
    checked = 0; final_solutions = 0
    for stage in range(len(task["stages"])):
        rs = requirements(task, stage)
        for candidate in candidates:
            expected = independent_math(task, candidate, rs)
            actual = violation(task, candidate, rs) is None
            if expected != actual: raise ValueError("independent mathematical grader disagreement")
            checked += 1
        if not independent_math(task, reference, rs): raise ValueError("witness does not pass all stages")
    if exhaustive:
        final_solutions = sum(independent_math(task, x, requirements(task, len(task["stages"]) - 1)) for x in candidates[1:])
    return {"task_id": task["task_id"], "task_sha256": task["sha256"], "checks": checked,
            "independent_agreement": True, "exhaustive_routes": exhaustive,
            "final_route_solutions": final_solutions if exhaustive else None,
            "scheduling_scope": "witness, random assignments and local perturbations; no exhaustive scheduling claim" if not exhaustive else None}


def check_code(task, runner):
    reference = task["evaluator"]["reference"]
    public = [t for r in requirements(task, len(task["stages"]) - 1) for t in r["tests"]]
    private = task["evaluator"]["reserved_tests"]
    result = run_tests(reference, public + private, runner)
    if result["status"] != "public_pass": raise ValueError("isolated reference disagrees with independent evaluator: " + task["task_id"] + ": " + wire(result))
    negative = run_tests(task["initial_artifact"], public + private, runner)
    if negative["status"] == "public_pass": raise ValueError("initial buggy project passes complete test suite")
    return {"task_id": task["task_id"], "task_sha256": task["sha256"], "isolated_reference_pass": True,
            "public_tests": len(public), "reserved_tests": len(private), "initial_bug_detected": True}


def verify_tasks(tasks, *, real_docker=True, workers=4):
    started = time.monotonic()
    counts = Counter((t["family"], t["horizon"], t["difficulty"]) for t in tasks)
    if len(tasks) != 48 or len(counts) != 24 or set(counts.values()) != {2} or len({t["sha256"] for t in tasks}) != 48:
        raise ValueError("48-task factorial balance or uniqueness failed")
    math = [check_math(t) for t in tasks if t["domain"] == "math"]
    code, runtime = [], None
    if real_docker:
        runner = DockerRunner(IMAGE); runtime = runner.audit()
        with ThreadPoolExecutor(max_workers=workers) as pool:
            code = list(pool.map(lambda t: check_code(t, runner), [t for t in tasks if t["domain"] == "coding"]))
    return {"evidence_kind": "offline_task_and_grader_verification", "model_calls": 0,
            "tasks_sha256": sha(tasks), "mathematics": math, "coding": code, "runtime": runtime,
            "all_passed": len(math) == 24 and len(code) == 24, "elapsed_seconds": time.monotonic() - started}
