"""Fixed cross-record distribution, disclosure order, and exact terminal grader.

This adapts the earlier synthetic workflow rows but splits every component into
a separate tool result. Evaluation seeds are derived only after implementation
freeze from its commit ID; no new model result is used to choose them.
"""
from __future__ import annotations

from copy import deepcopy
from hashlib import sha256
import json
import random

from experiments.dependency_memory.schema_transfer.casebook import (
    DEV, EVAL, ROWS, RULES, SCHEMAS, _row, scalar, target, terminal, token,
)

DEV_SEEDS = (61011, 61012)
EVAL_REPETITIONS = 4
PARENT_CAP = 7000
CHILD_CAP = 2600
EXEC_ACTIONS = ("submit", "hold", "publish", "retry", "close", "promote")


def compact(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def _notes(seed, family, index):
    draft = token(seed, family, index, "old_draft")
    return (f"Worker log mentions obsolete draft {draft}. Dashboard labels and timings are not gate evidence. " * 3)


def _schema_and_results(family, seed, originals):
    tool_schemas = {}
    results = []
    schema_props = SCHEMAS[family]["properties"]
    root_keys = [key for key, value in schema_props.items() if value.get("type") != "object" and key != "operator_notes"]
    components = [key for key, value in schema_props.items() if value.get("type") == "object"]
    tool_schemas["root"] = {"type": "object", "properties": {
        **{key: deepcopy(schema_props[key]) for key in root_keys},
        "workflow_key": scalar(pattern=True),
        "operator_notes": scalar(description="Diagnostic text; old drafts are not gate evidence.")}}
    for component in components:
        tool_schemas[component] = {"type": "object", "properties": {
            "record_id": scalar(pattern=True), "workflow_key": scalar(pattern=True),
            **deepcopy(schema_props[component]["properties"])}}
    for index, row in enumerate(originals):
        workflow = token(seed, family, index, "workflow_key")
        root = {key: row[key] for key in root_keys}
        root.update(workflow_key=workflow, operator_notes=_notes(seed, family, index))
        results.append({"tool": "root", "data": root})
        for component in components:
            data = {"record_id": token(seed, family, index, component + "_record"),
                    "workflow_key": workflow, **deepcopy(row[component])}
            results.append({"tool": component, "data": data})
    random.Random(seed).shuffle(results)
    return tool_schemas, results


def _events(family, seed, originals, valid_index, invalid_index):
    bad, good = originals[invalid_index], originals[valid_index]
    if family == "escrow":
        fix = {"path": "authorization.for_receipt", "value": bad["current_receipt"]}
        break_event = {"path": "current_receipt", "value": token(seed, family, valid_index, "revised_receipt")}
    elif family == "package":
        fix = {"path": "scan.subject_digest", "value": bad["release_digest"]}
        break_event = {"path": "release_digest", "value": token(seed, family, valid_index, "revised_digest")}
    elif family == "retry_queue":
        fix = {"path": "result.state", "value": "passed"}
        break_event = {"path": "dispatch.attempt_uuid", "value": token(seed, family, valid_index, "new_attempt")}
    elif family == "ci_promotion":
        fix = {"path": "authorization.approved_digest", "value": bad["build"]["digest"]}
        break_event = {"path": "build.digest", "value": token(seed, family, valid_index, "rebuilt")}
    else:
        fix = {"path": "consent.approved_output", "value": bad["load"]["output_dataset"]}
        break_event = {"path": "load.output_dataset", "value": token(seed, family, valid_index, "reloaded")}
    return [
        {"id": f"{family}-{seed}-0", "target": target(family, bad),
         "event": {"path": "note", "value": "Schedule title updated; gate fields unchanged."}},
        {"id": f"{family}-{seed}-1", "target": target(family, bad), "event": fix},
        {"id": f"{family}-{seed}-2", "target": target(family, good), "event": break_event},
    ]


def make_case(family, seed, split):
    if family not in (DEV if split == "development" else EVAL if split == "evaluation" else ()):
        raise ValueError("Family outside split")
    if split == "development" and seed not in DEV_SEEDS:
        raise ValueError("Unreserved development seed")
    if type(seed) is not int or seed < 0 or seed >= 2**32:
        raise ValueError("Seed outside fixed 32-bit domain")
    originals = [_row(family, seed, i) for i in range(ROWS)]
    valid_index, invalid_index = ((0, 1) if seed % 2 else (4, 5))
    schemas, results = _schema_and_results(family, seed, originals)
    root_field = next(key for key in SCHEMAS[family]["properties"]
                      if key in {"invoice_id", "package_id", "request_token", "deployment_slot", "pipeline_run"})
    rule = ("Select the root record whose " + root_field + " equals target; join component records by "
            "the identical workflow_key. A component path such as approval.state means the state field "
            "of the approval tool result in that joined workflow. Apply the late event to the named "
            "path of the selected workflow first. Ignore operator_notes and other workflows. " + RULES[family])
    ids = [target(family, originals[i]) for i in (valid_index, invalid_index)]
    return {"id": f"{family}-{seed}", "family": family, "split": split,
            "tool_schemas": schemas, "tool_results": results, "candidate_ids": ids,
            "futures": _events(family, seed, originals, valid_index, invalid_index),
            "rule": rule,
            "private_truth_rows": {target(family, row): row for row in originals}}


def truth(case, future):
    return terminal(case["family"], case["private_truth_rows"][future["target"]], future["event"])


def grade(response, expected):
    return isinstance(response, dict) and set(response) == {"action", "target_id", "work"} and response == expected


def evaluation_seeds(implementation_commit):
    """Commit-conditioned, deterministic seeds unavailable before code freeze."""
    if not isinstance(implementation_commit, str) or len(implementation_commit) != 40 or any(
            char not in "0123456789abcdef" for char in implementation_commit):
        raise ValueError("Expected full lowercase implementation commit")
    return {family: [int(sha256(f"cross-record-v1:{implementation_commit}:{family}:{i}".encode()).hexdigest()[:8], 16)
                     for i in range(EVAL_REPETITIONS)] for family in EVAL}
