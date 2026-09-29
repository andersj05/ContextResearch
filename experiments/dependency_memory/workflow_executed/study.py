"""Fixed input capture and reused memory/decision interface, scoped at B."""
import json
import random

from experiments.dependency_memory.workflow_eval_live.study import (
    ARMS, PARENT_CAP, CHILD_CAP, CHECKS, PACKET, admit_prose, checked_memory,
    final_request, normalize_response, wire,
)
from experiments.dependency_memory.workflow_eval_live.study import memory_request as previous_memory_request
from experiments.dependency_memory.workflow_eval_live.protocol import request_bytes
from .capture import CAPTURE, validate_capture

SEED = 2026092902


def cases():
    return validate_capture(json.loads(CAPTURE.read_text(encoding="utf-8")))


def memory_request(stage, arm, observation):
    request = previous_memory_request(stage, arm, observation)
    if stage == "child":
        request["instruction"] += ("\nThe announced scope lists possible final check names. "
            "Keep only those checks, preserving their latest receipts on every available source snapshot. "
            "The final source snapshot and a subset of scope will be disclosed later.")
    request_bytes(request)
    return request


def order(case_id, arms):
    result = list(arms)
    random.Random(str(SEED) + ":" + case_id + ":" + ",".join(arms)).shuffle(result)
    return result


def schedule():
    result = []
    for case in cases():
        for stage in ("parent", "child"):
            result.extend(f"{case['id']}-{arm}-{stage}" for arm in order(case["id"] + stage, ("checked", "prose")))
        result.extend(f"{case['id']}-{arm}-final" for arm in order(case["id"], ARMS))
    return result


def audit_request():
    candidates = []
    for case in cases():
        candidates.extend(memory_request("parent", arm, {"tool_observations": case["initial"]}) for arm in ("checked", "prose"))
        candidates.append(final_request(wire(case["initial"] + case["between"]).decode(), case["task"]))
        # Audit also covers the largest legal parent string plus new observations.
        candidates.extend(memory_request("child", arm, {"previous_memory": "x" * PARENT_CAP,
            "new_observations": case["between"], "scope": case["scope"]}) for arm in ("checked", "prose"))
    return max(candidates, key=lambda request: len(request_bytes(request)))
