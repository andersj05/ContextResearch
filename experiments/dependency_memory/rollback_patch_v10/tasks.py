"""Eight-component authored repair projects; never execute source on the host.

This development cohort increases project size after v9's observed ceiling.
Components reuse the frozen v9 semantics and independent checkers. A finite
seeded pool is reused across composite tasks, so instances are related and are
not eight independent trials or new real-world repositories.
"""

import ast
from collections import Counter
from copy import deepcopy
from functools import lru_cache
from textwrap import indent

from ..rollback_patch_v9 import tasks as component_tasks


FAMILIES = tuple("composite_" + family for family in component_tasks.FAMILIES)
FILES = component_tasks.FILES
FOCUS_CATEGORIES = component_tasks.FOCUS_CATEGORIES
PUBLIC_CASES = component_tasks.PUBLIC_CASES
PRIVATE_CASES = component_tasks.PRIVATE_CASES
DEFAULT_SEED = 2026101310
COMPONENTS = 8
SOURCE_BYTES = 32768
canonical = component_tasks.canonical
sha = component_tasks.sha
candidate = component_tasks.candidate
initial_candidate = component_tasks.initial_candidate
reference_candidate = component_tasks.reference_candidate
public_task = component_tasks.public_task
public_check = component_tasks.public_check
terminal_check = component_tasks.terminal_check


def _without_rules_import(source):
    """Remove only top-level imports from the original shared rules module."""
    tree = ast.parse(source)
    remove = set()
    for node in tree.body:
        if isinstance(node, ast.ImportFrom) and node.module == "rules" and node.level == 0:
            remove.update(range(node.lineno - 1, node.end_lineno))
    return "\n".join(line for index, line in enumerate(source.splitlines()) if index not in remove) + "\n"


def _project(components, *, reference):
    blocks = []
    ids = []
    for index, component in enumerate(components, 1):
        component_id = "component_" + str(index).zfill(2)
        ids.append(component_id)
        records = component["evaluator"]["reference_files"] if reference else component["base_files"]
        files = {record["path"]: record["text"] for record in records}
        body = files["rules.py"].rstrip() + "\n\n" + _without_rules_import(files["engine.py"]).rstrip()
        blocks.append("def _build_" + component_id + "():\n" + indent(body, "    ") + "\n    return solve\n")
    mapping = ",\n".join("    " + repr(component_id) + ": _build_" + component_id + "()" for component_id in ids)
    rules = "\n\n".join(blocks) + "\n\nSOLVERS = {\n" + mapping + "\n}\n"
    engine = ("from rules import SOLVERS\n\n"
              "def solve(data):\n"
              "    return {component_id: solver(data[component_id])\n"
              "            for component_id, solver in SOLVERS.items()}\n")
    result = candidate({"engine.py": engine, "rules.py": rules})["files"]
    if sum(len(row["text"].encode("utf-8")) for row in result) > SOURCE_BYTES:
        raise ValueError("composite reference or base exceeds declared source limit")
    for row in result:
        ast.parse(row["text"], filename=row["path"])
    return result


@lru_cache(maxsize=8)
def _pool(seed, per_family):
    # The component generator's fixture label permits more than four instances
    # per family without mislabelling them as v9 model observations.
    tasks = component_tasks.generate(split="fixture", seed=seed, per_family=max(16, per_family))
    return {family: tuple(sorted((task for task in tasks if task["family"] == family),
                                 key=lambda task: task["replicate"]))
            for family in component_tasks.FAMILIES}


def _components(pool, lead_family, replicate):
    count = len(pool[lead_family])
    start = (replicate - 1) * 5
    result = [pool[lead_family][(start + offset) % count] for offset in range(5)]
    for offset, family in enumerate(family for family in component_tasks.FAMILIES if family != lead_family):
        result.append(pool[family][((replicate - 1) * (2 * offset + 1) + offset) % count])
    return result


def _composite_tests(components, private):
    tests = []
    count = PRIVATE_CASES if private else PUBLIC_CASES
    for index in range(count):
        inputs, expected = {}, {}
        for component_index, component in enumerate(components, 1):
            cases = component["evaluator"]["reserved_tests"] if private else component["public_tests"]
            case = cases[index]
            component_id = "component_" + str(component_index).zfill(2)
            inputs[component_id] = deepcopy(case["input"])
            expected[component_id] = deepcopy(case["expected"])
        tests.append({"id": ("private-" if private else "public-") + str(index + 1).zfill(2),
                      "input": inputs, "expected": expected})
    return tests


def generate(*, split="calibration", seed=DEFAULT_SEED, per_family=4):
    if split not in {"calibration", "study", "fixture"}:
        raise ValueError("calibration, study or fixture split required")
    if type(seed) is not int or type(per_family) is not int or not 1 <= per_family <= 64:
        raise ValueError("integer seed and one through 64 instances per family required")
    if split == "calibration" and per_family > 4:
        raise ValueError("calibration is capped at sixteen tasks")
    pool_seed = int(sha(["rollback-patch-v10-components", split, seed])[:16], 16)
    pool = _pool(pool_seed, per_family)
    result = []
    for family, lead_family in zip(FAMILIES, component_tasks.FAMILIES):
        for replicate in range(1, per_family + 1):
            components = _components(pool, lead_family, replicate)
            component_contracts = [{"component_id": "component_" + str(index).zfill(2),
                                    "family": component["family"],
                                    "policy": deepcopy(component["contract"]["policy"]),
                                    "requirements": deepcopy(component["contract"]["requirements"])}
                                   for index, component in enumerate(components, 1)]
            task = {
                "task_id": "v10-" + split + "-" + family + "-" + sha([seed, family, replicate, split])[:16],
                "family": family, "domain": "coding", "split": split, "replicate": replicate,
                "contract": {
                    "instruction": "Repair the entire supplied two-module Python3.11 project. It contains eight independent components and every component must satisfy its complete specification. Return complete replacement contents for both files; the full specification, original base files and all public examples remain available on every attempt.",
                    "entrypoint": "engine.solve(case) -> JSON object mapping each component ID to its result",
                    "files": list(FILES),
                    "candidate_format": {"files": [{"path": "engine.py", "text": "complete source"},
                                                     {"path": "rules.py", "text": "complete source"}]},
                    "source_limit_utf8_bytes": SOURCE_BYTES,
                    "execution": "Python3.11 standard library only; no network, subprocess requirements, host workspace access or third-party packages. Tests call solve repeatedly in one fresh isolated process per suite. Results must not depend on prior cases. All suite inputs are visible to the program, but expected outputs are never provided to it. Public and private suites use separate containers.",
                    "requirements": [
                        "Each input is an object with exactly component_01 through component_08. Return an object with exactly the same keys; each value is that component's specified result. JSON object key order is irrelevant.",
                        "The eight components are independent. Their complete policies and requirements are listed in component_contracts. Apply each policy only to its named component; names and local variables may overlap between components.",
                        "Every component must be correct in every case. Keep the engine.solve entry point and return JSON-serializable values. Internal structure may be changed, but both complete source files must be returned and the total source limit applies to them together.",
                    ],
                    "component_contracts": component_contracts,
                    "lesson_focus_categories": list(FOCUS_CATEGORIES),
                    "public_feedback": "Public receipts refer only to the listed full compound public examples. Private terminal results never enter actor or lesson requests.",
                },
                "base_files": _project(components, reference=False),
                "public_tests": _composite_tests(components, False),
                "evaluator": {
                    "reference_files": _project(components, reference=True),
                    "reserved_tests": _composite_tests(components, True),
                    "component_bindings": [{"component_id": "component_" + str(index).zfill(2),
                                            "task_id": component["task_id"], "sha256": component["sha256"]}
                                           for index, component in enumerate(components, 1)],
                    "component_pool_seed": pool_seed,
                    "component_pool_per_family": len(pool[lead_family]),
                    "provenance": "Repository-authored composite repair tasks developed after v9 calibration had no naturally failed eligible patches. Eight components reuse v9 semantics and checkers, with five from the leading family and one from each other family. Seeded components recur across tasks; tasks are related instances from four composite families, not independent real repositories or eight separate trials. Calibration and study use different seeded pools.",
                },
            }
            task["sha256"] = sha(task)
            result.append(task)
    return sorted(result, key=lambda task: sha([seed, split, "order", task["task_id"]]))


def verify_tasks(tasks):
    """Recompute composed expectations through independent v9 host oracles."""
    identities, contexts, oracle_cache = set(), set(), {}
    public_count = private_count = logical_components = 0
    expected_ids = {"component_" + str(index).zfill(2) for index in range(1, COMPONENTS + 1)}
    for task in tasks:
        if task["task_id"] in identities or task["family"] not in FAMILIES:
            raise ValueError("duplicate or unknown task")
        identities.add(task["task_id"])
        if task["sha256"] != sha({key: value for key, value in task.items() if key != "sha256"}):
            raise ValueError("task binding changed")
        context = sha({key: task[key] for key in ("family", "contract", "base_files", "public_tests")})
        if context in contexts:
            raise ValueError("duplicate full public context")
        contexts.add(context)
        for files in (task["base_files"], task["evaluator"]["reference_files"]):
            if len(files) != 2 or {row["path"] for row in files} != set(FILES):
                raise ValueError("two-file project required")
            if sum(len(row["text"].encode("utf-8")) for row in files) > SOURCE_BYTES:
                raise ValueError("project exceeds source limit")
            for row in files:
                ast.parse(row["text"], filename=row["path"])
        contracts = task["contract"]["component_contracts"]
        if len(contracts) != COMPONENTS or {row["component_id"] for row in contracts} != expected_ids:
            raise ValueError("eight component contracts required")
        lead_family = task["family"].removeprefix("composite_")
        expected_families = Counter({family: 1 for family in component_tasks.FAMILIES})
        expected_families[lead_family] = 5
        if Counter(row["family"] for row in contracts) != expected_families:
            raise ValueError("component family balance changed")
        if len(task["public_tests"]) != PUBLIC_CASES or len(task["evaluator"]["reserved_tests"]) != PRIVATE_CASES:
            raise ValueError("fixed test denominator changed")
        seen = set()
        for case in task["public_tests"] + task["evaluator"]["reserved_tests"]:
            fingerprint = sha(case["input"])
            if fingerprint in seen:
                raise ValueError("public/private compound cases overlap")
            seen.add(fingerprint)
            if set(case["input"]) != expected_ids or set(case["expected"]) != expected_ids:
                raise ValueError("compound case component inventory changed")
            for contract in contracts:
                component_id = contract["component_id"]
                key = sha([contract["family"], contract["policy"], case["input"][component_id]])
                if key not in oracle_cache:
                    oracle_cache[key] = component_tasks.ORACLES[contract["family"]](case["input"][component_id], contract["policy"])
                if canonical(case["expected"][component_id]) != canonical(oracle_cache[key]):
                    raise ValueError("independent expected output differs")
                logical_components += 1
        public_count += len(task["public_tests"])
        private_count += len(task["evaluator"]["reserved_tests"])
    return {"passed": True, "scope": "offline composite structure and independent component oracle values; Docker reference execution is a separate required gate",
            "tasks": len(tasks), "public_cases": public_count, "private_cases": private_count,
            "component_case_comparisons": logical_components, "unique_oracle_inputs": len(oracle_cache),
            "unique_public_contexts": len(contexts), "model_calls": 0,
            "candidate_code_executed_on_host": False}
