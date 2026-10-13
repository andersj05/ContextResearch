"""Eight excluded interface calls; distinct task identities and construction seeds."""
from copy import deepcopy
import random

from .common import SEED, STUDY, FAMILIES, sha
from .tasks import generate, public_check
from . import coding_tasks
from .accounting import Identity
from .contexts import render, parse_action, parse_writer
from .engine import initial_state


def cases():
    tasks = []
    for family in FAMILIES:
        task = {"task_id": "v5-calibration-" + family, "family": family,
                "domain": "coding" if family in {"ledger", "resolver"} else "math", "horizon": "calibration",
                "difficulty": "excluded", "action_allowance": 2, "initial_artifact": {"values": [], "order": [], "files": []}}
        if family == "scheduling":
            task["contract"] = {"instruction": "Return values=[0], with order and files empty.", "durations": [1], "start_bounds": [0, 2]}
            records = [{"id": "window-0", "kind": "window", "job": 0, "release": 0, "deadline": 1}]
            reference = {"values": [0], "order": [], "files": []}
        elif family == "routing":
            task["contract"] = {"instruction": "Return order=[1], with values and files empty. Start at 0, visit 1, return to 0, no waiting.", "node_count": 2}
            records = [{"id": "travel-0", "kind": "travel", "from": 0, "costs": [0, 1]}, {"id": "travel-1", "kind": "travel", "from": 1, "costs": [1, 0]}]
            reference = {"values": [], "order": [1], "files": []}
        else:
            contract, records, reference, initial, reserved = coding_tasks.build(family, random.Random(SEED + 9000000 + len(tasks)), False)
            task["contract"], task["initial_artifact"] = contract, initial
            records = records[:1]
        task["stages"] = [{"requirements": records}]
        task["evaluator"] = {"reference": reference, "reserved_tests": [], "calibration_only": True}
        task["sha256"] = sha(task); tasks.append(task)
    requests = []
    for i, (task, kind) in enumerate([(t, "action") for t in tasks] + [(tasks[0], "lesson"), (tasks[2], "lesson"), (tasks[1], "summary"), (tasks[3], "compress")], 1):
        state = initial_state(task)
        if kind != "action":
            state["feedback"] = {"status": "public_mismatch", "check": "format-example", "detail": "Disclosed interface fixture only; candidate did not meet the declared output format."}
        identity = Identity(STUDY, task["task_id"], "calibration", f"C{i}", 0, kind)
        requests.append({"identity": identity, "task": task, "request": render(task, state, kind)})
    return requests


def validate(case, text, runner):
    from ..rollback_pilot.records import strict_loads
    kind = case["request"].stage
    if kind == "action":
        value = parse_action(strict_loads(text))
        if value["status"] != "candidate" or public_check(case["task"], 0, value["candidate"], runner)["status"] != "public_pass":
            raise ValueError("calibration candidate failed")
    else:
        parse_writer(text, kind)
