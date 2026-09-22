"""Constructed tool traces. This file and its grader precede extractor development.

The evaluator's seeds are disjoint from development seeds. Tool schemas expose
opaque identifiers, references, and explicitly ephemeral prose. No instance
identifier is embedded in a schema or in the extractor.
"""
from __future__ import annotations

from copy import deepcopy
from hashlib import sha256
import json
import random


FAMILIES = ("retry", "ci_handoff", "data_job")
DEV_SEEDS = (41011, 41012)
EVAL_SEEDS = (94121, 94122)
PARENT_CAP = 2600
CHILD_CAP = 1300
SCHEMA_VERSION = "tool_trace_v1"


def compact(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def opaque(seed, label):
    return sha256(f"{seed}:{label}".encode()).hexdigest()[:10]


def field(*, identity=False, reference=False, ephemeral=False, enum=None):
    result = {"type": "string"}
    if identity:
        result["format"] = "opaque-id"
    if reference:
        result["x-reference"] = True
    if ephemeral:
        result["x-ephemeral"] = True
    if enum:
        result["enum"] = enum
    return result


def obj(**properties):
    return {"type": "object", "properties": properties}


SCHEMAS = {
    "retry": obj(
        request_key=field(identity=True), attempt_key=field(identity=True),
        reservation_key=field(identity=True), retry_of=field(reference=True),
        dispatch_state=field(enum=["sent", "not_sent"]),
        result_state=field(enum=["failed", "passed", "pending"]),
        can_retry={"type": "boolean"},
        operator_note=field(ephemeral=True)),
    "ci_handoff": obj(
        service_key=field(identity=True), current_build=field(identity=True),
        approval=obj(approval_key=field(identity=True), covers_build=field(reference=True)),
        check=obj(run_key=field(identity=True), covers_build=field(reference=True),
                  verdict=field(enum=["pass", "fail", "pending"])),
        handoff_note=field(ephemeral=True)),
    "data_job": obj(
        pipeline_key=field(identity=True),
        extract=obj(run_key=field(identity=True), output_key=field(identity=True),
                    state=field(enum=["pass", "fail", "pending"])),
        transform=obj(run_key=field(identity=True), input_key=field(reference=True),
                      output_key=field(identity=True), state=field(enum=["pass", "fail", "pending"])),
        load=obj(run_key=field(identity=True), input_key=field(reference=True),
                 output_key=field(identity=True), state=field(enum=["pass", "fail", "pending"])),
        publish_approval=obj(approval_key=field(identity=True), covers_output=field(reference=True)),
        scheduler_log=field(ephemeral=True)),
}


RULES = {
    "retry": (
        "For the selected request, use dispatch if dispatch_state is not_sent; otherwise "
        "use close if result_state is passed, retry if it is failed and can_retry is true, "
        "or hold. Return target_id=request_key. Work is [] for dispatch/close, "
        "[attempt:<attempt_key>] for retry, or [await:<attempt_key>] for hold. "
        "A retry_of link is historical and never changes the current attempt. Apply the late event first."
    ),
    "ci_handoff": (
        "Handoff only if approval.covers_build and check.covers_build both equal current_build "
        "and check.verdict is pass. Otherwise hold. Return target_id=current_build. "
        "Work is the exact sorted set of approval when its scope is stale, "
        "and ci when CI scope is stale or verdict is not pass. Apply the late event first."
    ),
    "data_job": (
        "Publish only if extract, transform, and load states are pass; transform.input_key "
        "equals extract.output_key; load.input_key equals transform.output_key; and "
        "publish_approval.covers_output equals load.output_key. Otherwise hold. "
        "Return target_id=load.output_key. Work is the exact sorted set drawn from "
        "extract, transform, load, link:transform, link:load, approval for each failed "
        "condition respectively. Apply the late event first."
    ),
}


def _row(family, seed, index):
    tag = f"{family}:{index}"
    ident = lambda label: opaque(seed, tag + ":" + label)
    log = "Worker transcript, elapsed discussion, dashboard colors and unrelated operator notes. " * 7
    if family == "retry":
        row = {"request_key": "rq-" + ident("request"), "attempt_key": "at-" + ident("attempt"),
               "reservation_key": "rs-" + ident("reservation"), "retry_of": "at-" + ident("prior"),
               "dispatch_state": "sent", "result_state": "passed", "can_retry": False,
               "operator_note": log}
        if index == 1:
            row.update(result_state="failed", can_retry=True)
        if index == 2:
            row.update(dispatch_state="not_sent", result_state="pending")
        if index == 3:
            row.update(result_state="failed")
    elif family == "ci_handoff":
        build = "bd-" + ident("build")
        row = {"service_key": "sv-" + ident("service"), "current_build": build,
               "approval": {"approval_key": "ap-" + ident("approval"), "covers_build": build},
               "check": {"run_key": "ci-" + ident("ci"), "covers_build": build, "verdict": "pass"},
               "handoff_note": log}
        if index == 1:
            row["approval"]["covers_build"] = "bd-" + ident("old_approval_build")
        if index == 2:
            row["check"]["verdict"] = "fail"
        if index == 3:
            row["check"]["covers_build"] = "bd-" + ident("old_ci_build")
    else:
        first, second, third = ("ds-" + ident(x) for x in ("raw", "clean", "table"))
        row = {"pipeline_key": "pl-" + ident("pipeline"),
               "extract": {"run_key": "ex-" + ident("extract"), "output_key": first, "state": "pass"},
               "transform": {"run_key": "tr-" + ident("transform"), "input_key": first,
                             "output_key": second, "state": "pass"},
               "load": {"run_key": "ld-" + ident("load"), "input_key": second,
                        "output_key": third, "state": "pass"},
               "publish_approval": {"approval_key": "ap-" + ident("approval"), "covers_output": third},
               "scheduler_log": log}
        if index == 1:
            row["transform"]["input_key"] = "ds-" + ident("stale_raw")
        if index == 2:
            row["load"]["state"] = "fail"
        if index == 3:
            row["publish_approval"]["covers_output"] = "ds-" + ident("old_table")
    return row


def _target(row, family):
    return row[{"retry": "request_key", "ci_handoff": "service_key", "data_job": "pipeline_key"}[family]]


def make_case(family, seed, split):
    if family not in FAMILIES or split not in {"development", "evaluation"}:
        raise ValueError("Unknown family or split")
    if seed not in (DEV_SEEDS if split == "development" else EVAL_SEEDS):
        raise ValueError("Seed outside split")
    rows = [_row(family, seed, i) for i in range(4)]
    chosen = [1, 3] if seed % 2 else [0, 2]
    candidates = [_target(rows[i], family) for i in chosen]
    shuffled = deepcopy(rows)
    random.Random(seed).shuffle(shuffled)
    futures = []
    for position, index in enumerate(chosen):
        if family == "retry":
            event = {"path": "result_state", "value": "passed"} if index == 1 else {"path": "can_retry", "value": True}
        elif family == "ci_handoff":
            event = {"path": "approval.covers_build", "value": rows[index]["current_build"]} if index == 1 else {"path": "check.verdict", "value": "pass"}
        else:
            event = {"path": "transform.input_key", "value": rows[index]["extract"]["output_key"]} if index == 1 else {"path": "load.state", "value": "pass"}
        # The second continuation changes a scoped fact only in odd-seed cases.
        # Even cases use a public note event to test needless invalidation.
        if position == 1 and seed % 2 == 0:
            event = {"path": "note", "value": "Schedule title corrected; state unchanged."}
        futures.append({"id": f"{family}-{split}-{seed}-{position}",
                        "target": _target(rows[index], family), "event": event})
    return {"id": f"{family}-{split}-{seed}", "family": family, "split": split,
            "schema_version": SCHEMA_VERSION, "tool_schema": deepcopy(SCHEMAS[family]),
            "tool_results": shuffled, "candidates": candidates, "futures": futures}


def apply_event(row, event):
    updated = deepcopy(row)
    if event["path"] != "note":
        keys = event["path"].split(".")
        cursor = updated
        for key in keys[:-1]:
            cursor = cursor[key]
        cursor[keys[-1]] = event["value"]
    return updated


def terminal(family, row, event):
    row = apply_event(row, event)
    if family == "retry":
        if row["dispatch_state"] == "not_sent":
            action, work = "dispatch", []
        elif row["result_state"] == "passed":
            action, work = "close", []
        elif row["result_state"] == "failed" and row["can_retry"]:
            action, work = "retry", ["attempt:" + row["attempt_key"]]
        else:
            action, work = "hold", ["await:" + row["attempt_key"]]
        target_id = row["request_key"]
    elif family == "ci_handoff":
        work = []
        if row["approval"]["covers_build"] != row["current_build"]:
            work.append("approval")
        if row["check"]["covers_build"] != row["current_build"] or row["check"]["verdict"] != "pass":
            work.append("ci")
        action, target_id = ("hold" if work else "handoff"), row["current_build"]
    else:
        work = [name for name in ("extract", "transform", "load") if row[name]["state"] != "pass"]
        if row["transform"]["input_key"] != row["extract"]["output_key"]:
            work.append("link:transform")
        if row["load"]["input_key"] != row["transform"]["output_key"]:
            work.append("link:load")
        if row["publish_approval"]["covers_output"] != row["load"]["output_key"]:
            work.append("approval")
        action, target_id = ("hold" if work else "publish"), row["load"]["output_key"]
    return {"action": action, "target_id": target_id, "work": sorted(work)}


def truth(case, future):
    row = next(x for x in case["tool_results"] if _target(x, case["family"]) == future["target"])
    return terminal(case["family"], row, future["event"])


def grade(response, expected):
    if not isinstance(response, dict) or set(response) != {"action", "target_id", "work"}:
        return False
    if not isinstance(response["work"], list) or any(not isinstance(x, str) for x in response["work"]):
        return False
    return response == expected
