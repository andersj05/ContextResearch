"""New-seed, unplanned development allocation after the closed v10 gate.

Task semantics and component-pool dependence are inherited unchanged. V10's
three eligible failures did not satisfy its four-failure gate: v11 is explicitly
a separate calibration-informed development study, not its confirmation.
"""

from experiments.dependency_memory.rollback_patch_v10 import tasks as inherited


DEFAULT_SEED = 2026101312
FAMILIES = inherited.FAMILIES
FILES = inherited.FILES
FOCUS_CATEGORIES = inherited.FOCUS_CATEGORIES
PUBLIC_CASES = inherited.PUBLIC_CASES
PRIVATE_CASES = inherited.PRIVATE_CASES
COMPONENTS = inherited.COMPONENTS
SOURCE_BYTES = inherited.SOURCE_BYTES
canonical = inherited.canonical
sha = inherited.sha
candidate = inherited.candidate
initial_candidate = inherited.initial_candidate
reference_candidate = inherited.reference_candidate
public_task = inherited.public_task
public_check = inherited.public_check
terminal_check = inherited.terminal_check
verify_tasks = inherited.verify_tasks


def generate(*, split="study", seed=DEFAULT_SEED, per_family=None):
    if split not in {"study", "fixture"}:
        raise ValueError("v11 permits only study or fixture; no new calibration")
    expected = 64 if split == "study" else 1
    if per_family is None:
        per_family = expected
    if type(per_family) is not int or per_family != expected:
        raise ValueError("v11 fixes 256 study tasks or four fixture tasks")
    if type(seed) is not int or seed != DEFAULT_SEED:
        raise ValueError("v11 seed is frozen at 2026101312")
    result = inherited.generate(split=split, seed=seed, per_family=per_family)
    for task in result:
        task["task_id"] = task["task_id"].replace("v10-", "v11-", 1)
        task["evaluator"]["provenance"] = (
            "UNPLANNED DEVELOPMENT: v10 calibration produced three eligible natural failures, below its frozen four-failure gate; that allocation remains closed. This separate fixed v11 cohort was selected after those control-only observations and before any deletion or lesson-arm result. No confirmatory inference is claimed. "
            + task["evaluator"]["provenance"])
        task["sha256"] = sha({key: value for key, value in task.items() if key != "sha256"})
    return result
