"""Frozen constructed tool traces and independent terminal rules.

Development uses escrow and package schemas. Evaluation uses structurally
different retry, CI promotion, and data-pipeline schemas. No custom critical-
field or reference annotations appear in the public schemas.
"""
from __future__ import annotations

from copy import deepcopy
from hashlib import sha256
import json
import random

DEV = ("escrow", "package")
EVAL = ("retry_queue", "ci_promotion", "data_pipeline")
DEV_SEEDS = (52011, 52012)
EVAL_SEEDS = (97031, 97032)
PARENT_CAP = 3000
CHILD_CAP = 1050
ROWS = 7


def compact(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def token(seed, family, index, label):
    return sha256(f"{seed}:{family}:{index}:{label}".encode()).hexdigest()[:16]


def scalar(*, pattern=False, enum=None, description=""):
    field = {"type": "string"}
    if pattern:
        field["pattern"] = "^[a-f0-9]{16}$"
    if enum is not None:
        field["enum"] = list(enum)
    if description:
        field["description"] = description
    return field


def obj(**fields):
    return {"type": "object", "properties": fields}


def flag():
    return {"type": "boolean"}


SCHEMAS = {
    "escrow": obj(invoice_id=scalar(pattern=True), current_receipt=scalar(pattern=True),
        authorization=obj(approval_id=scalar(pattern=True), for_receipt=scalar(),
                          state=scalar(enum=("accepted", "pending"))),
        operator_notes=scalar(description="Free-form diagnostic transcript.")),
    "package": obj(package_id=scalar(pattern=True), release_digest=scalar(pattern=True),
        scan=obj(run_id=scalar(pattern=True), subject_digest=scalar(),
                 state=scalar(enum=("pass", "fail"))),
        signature=obj(key_id=scalar(pattern=True), subject_digest=scalar(),
                      state=scalar(enum=("pass", "missing"))),
        operator_notes=scalar(description="Free-form diagnostic transcript.")),
    "retry_queue": obj(request_token=scalar(pattern=True),
        dispatch=obj(attempt_uuid=scalar(pattern=True), idempotency_key=scalar(),
                     state=scalar(enum=("sent", "not_sent"))),
        result=obj(attempt_uuid=scalar(), state=scalar(enum=("passed", "failed", "pending"))),
        billing=obj(charge_token=scalar(pattern=True), for_attempt=scalar(),
                    state=scalar(enum=("settled", "none"))),
        retry_policy=obj(retry_allowed=flag(), prior_attempt=scalar()),
        operator_notes=scalar(description="Free-form diagnostic transcript.")),
    "ci_promotion": obj(deployment_slot=scalar(pattern=True),
        build=obj(digest=scalar(pattern=True), channel=scalar(enum=("stable", "candidate"))),
        authorization=obj(ticket=scalar(pattern=True), approved_digest=scalar(),
                          state=scalar(enum=("approved", "pending"))),
        verification=obj(run=scalar(pattern=True), subject=scalar(),
                         unit=scalar(enum=("pass", "fail")),
                         integration=scalar(enum=("pass", "fail"))),
        handoff=obj(environment=scalar(enum=("prod", "staging"))),
        operator_notes=scalar(description="Free-form diagnostic transcript.")),
    "data_pipeline": obj(pipeline_run=scalar(pattern=True),
        extract=obj(run=scalar(pattern=True), output_dataset=scalar(pattern=True),
                    state=scalar(enum=("pass", "fail"))),
        transform=obj(run=scalar(pattern=True), input_dataset=scalar(),
                      output_dataset=scalar(pattern=True), state=scalar(enum=("pass", "fail"))),
        load=obj(run=scalar(pattern=True), input_dataset=scalar(),
                 output_dataset=scalar(pattern=True), state=scalar(enum=("pass", "fail"))),
        quality=obj(check=scalar(pattern=True), subject_dataset=scalar(),
                    state=scalar(enum=("pass", "fail"))),
        consent=obj(approval=scalar(pattern=True), approved_output=scalar(),
                    state=scalar(enum=("approved", "pending"))),
        operator_notes=scalar(description="Free-form diagnostic transcript.")),
}


RULES = {
    "escrow": "Submit only if authorization.state is accepted and authorization.for_receipt equals current_receipt. Return target_id=invoice_id and work=[] or the sorted set of approval and receipt_scope for failed conditions.",
    "package": "Publish only if scan and signature states pass and both subject_digest values equal release_digest. Return target_id=release_digest and work=[] or the sorted set of scan, signature, scan_scope, signature_scope for failed conditions.",
    "retry_queue": "For the selected request: if dispatch.state is not_sent, action=submit and work=[]; otherwise require result.attempt_uuid and billing.for_attempt to match dispatch.attempt_uuid. If a scope mismatches, hold with result_scope or billing_scope. Otherwise close if result.state is passed and billing.state is settled; retry if result.state is failed and retry_policy.retry_allowed is true; otherwise hold with result, billing or retry_policy for the applicable failed conditions. Return target_id=request_token. Apply the late event first.",
    "ci_promotion": "Promote only if build.channel=stable, authorization.state=approved, authorization.approved_digest=build.digest, verification.subject=build.digest, verification.unit and integration both pass, and handoff.environment=prod. Otherwise hold with the exact sorted set of channel, approval, approval_scope, ci_scope, unit, integration, environment for each failed condition. Return target_id=build.digest. Apply the late event first.",
    "data_pipeline": "Publish only if extract, transform, load, quality states pass, transform.input_dataset=extract.output_dataset, load.input_dataset=transform.output_dataset, quality.subject_dataset=load.output_dataset, consent.state=approved, and consent.approved_output=load.output_dataset. Otherwise hold with the exact sorted set of extract, transform, load, quality, link_transform, link_load, quality_scope, approval, approval_scope for failed conditions. Return target_id=load.output_dataset. Apply the late event first.",
}


def _notes(seed, family, index):
    distractor = token(seed, family, index, "old")
    return (f"Worker log archived an earlier draft {distractor}; dashboard labels, timing and operator chat are not gate evidence. " * 7)


def _row(family, seed, index):
    t = lambda label: token(seed, family, index, label)
    if family == "escrow":
        current = t("receipt")
        row = {"invoice_id": t("invoice"), "current_receipt": current,
               "authorization": {"approval_id": t("approval"), "for_receipt": current,
                                 "state": "accepted"}, "operator_notes": _notes(seed, family, index)}
        if index in (1, 5):
            row["authorization"]["for_receipt"] = t("old_receipt")
        if index in (2, 6):
            row["authorization"]["state"] = "pending"
    elif family == "package":
        digest = t("digest")
        row = {"package_id": t("package"), "release_digest": digest,
               "scan": {"run_id": t("scan"), "subject_digest": digest, "state": "pass"},
               "signature": {"key_id": t("key"), "subject_digest": digest, "state": "pass"},
               "operator_notes": _notes(seed, family, index)}
        if index in (1, 5):
            row["scan"]["subject_digest"] = t("old_digest")
        if index in (2, 6):
            row["signature"]["state"] = "missing"
    elif family == "retry_queue":
        attempt = t("attempt")
        row = {"request_token": t("request"),
               "dispatch": {"attempt_uuid": attempt, "idempotency_key": t("idempotency"), "state": "sent"},
               "result": {"attempt_uuid": attempt, "state": "passed"},
               "billing": {"charge_token": t("charge"), "for_attempt": attempt, "state": "settled"},
               "retry_policy": {"retry_allowed": False, "prior_attempt": t("prior")},
               "operator_notes": _notes(seed, family, index)}
        if index in (1, 5):
            row["result"]["state"] = "failed"
            row["retry_policy"]["retry_allowed"] = True
        if index in (2, 6):
            row["billing"]["for_attempt"] = t("old_attempt")
        if index == 3:
            row["dispatch"]["state"] = "not_sent"
    elif family == "ci_promotion":
        digest = t("digest")
        row = {"deployment_slot": t("slot"),
               "build": {"digest": digest, "channel": "stable"},
               "authorization": {"ticket": t("ticket"), "approved_digest": digest, "state": "approved"},
               "verification": {"run": t("run"), "subject": digest, "unit": "pass", "integration": "pass"},
               "handoff": {"environment": "prod"},
               "operator_notes": _notes(seed, family, index)}
        if index in (1, 5):
            row["authorization"]["approved_digest"] = t("old_digest")
        if index in (2, 6):
            row["verification"]["integration"] = "fail"
        if index == 3:
            row["verification"]["subject"] = t("old_ci_digest")
    else:
        raw, clean, table = t("raw"), t("clean"), t("table")
        row = {"pipeline_run": t("pipeline"),
               "extract": {"run": t("extract"), "output_dataset": raw, "state": "pass"},
               "transform": {"run": t("transform"), "input_dataset": raw,
                             "output_dataset": clean, "state": "pass"},
               "load": {"run": t("load"), "input_dataset": clean, "output_dataset": table, "state": "pass"},
               "quality": {"check": t("quality"), "subject_dataset": table, "state": "pass"},
               "consent": {"approval": t("consent"), "approved_output": table, "state": "approved"},
               "operator_notes": _notes(seed, family, index)}
        if index in (1, 5):
            row["consent"]["approved_output"] = t("old_table")
        if index in (2, 6):
            row["transform"]["input_dataset"] = t("old_raw")
        if index == 3:
            row["quality"]["state"] = "fail"
    return row


TARGET_PATH = {"escrow": "invoice_id", "package": "package_id", "retry_queue": "request_token",
               "ci_promotion": "deployment_slot", "data_pipeline": "pipeline_run"}


def target(family, row):
    return row[TARGET_PATH[family]]


def apply(row, event):
    result = deepcopy(row)
    if event["path"] != "note":
        parts = event["path"].split(".")
        cursor = result
        for part in parts[:-1]:
            cursor = cursor[part]
        cursor[parts[-1]] = event["value"]
    return result


def terminal(family, original, event):
    row = apply(original, event)
    work = []
    if family == "escrow":
        if row["authorization"]["state"] != "accepted": work.append("approval")
        if row["authorization"]["for_receipt"] != row["current_receipt"]: work.append("receipt_scope")
        action, target_id = ("hold" if work else "submit"), row["invoice_id"]
    elif family == "package":
        for name in ("scan", "signature"):
            if row[name]["state"] != "pass": work.append(name)
            if row[name]["subject_digest"] != row["release_digest"]: work.append(name + "_scope")
        action, target_id = ("hold" if work else "publish"), row["release_digest"]
    elif family == "retry_queue":
        attempt = row["dispatch"]["attempt_uuid"]
        target_id = row["request_token"]
        if row["dispatch"]["state"] == "not_sent":
            action = "submit"
        else:
            if row["result"]["attempt_uuid"] != attempt: work.append("result_scope")
            if row["billing"]["for_attempt"] != attempt: work.append("billing_scope")
            if work:
                action = "hold"
            elif row["result"]["state"] == "passed" and row["billing"]["state"] == "settled":
                action = "close"
            elif row["result"]["state"] == "failed" and row["retry_policy"]["retry_allowed"]:
                action = "retry"
            else:
                action = "hold"
                if row["result"]["state"] != "passed": work.append("result")
                if row["billing"]["state"] != "settled": work.append("billing")
                if row["result"]["state"] == "failed" and not row["retry_policy"]["retry_allowed"]:
                    work.append("retry_policy")
    elif family == "ci_promotion":
        build = row["build"]["digest"]
        if row["build"]["channel"] != "stable": work.append("channel")
        if row["authorization"]["state"] != "approved": work.append("approval")
        if row["authorization"]["approved_digest"] != build: work.append("approval_scope")
        if row["verification"]["subject"] != build: work.append("ci_scope")
        for name in ("unit", "integration"):
            if row["verification"][name] != "pass": work.append(name)
        if row["handoff"]["environment"] != "prod": work.append("environment")
        action, target_id = ("hold" if work else "promote"), build
    else:
        for name in ("extract", "transform", "load", "quality"):
            if row[name]["state"] != "pass": work.append(name)
        if row["transform"]["input_dataset"] != row["extract"]["output_dataset"]: work.append("link_transform")
        if row["load"]["input_dataset"] != row["transform"]["output_dataset"]: work.append("link_load")
        table = row["load"]["output_dataset"]
        if row["quality"]["subject_dataset"] != table: work.append("quality_scope")
        if row["consent"]["state"] != "approved": work.append("approval")
        if row["consent"]["approved_output"] != table: work.append("approval_scope")
        action, target_id = ("hold" if work else "publish"), table
    return {"action": action, "target_id": target_id, "work": sorted(work)}


def make_case(family, seed, split):
    allowed = DEV if split == "development" else EVAL if split == "evaluation" else ()
    seeds = DEV_SEEDS if split == "development" else EVAL_SEEDS
    if family not in allowed or seed not in seeds:
        raise ValueError("Family or seed outside split")
    rows = [_row(family, seed, i) for i in range(ROWS)]
    valid_index, invalid_index = ((0, 1) if seed % 2 else (4, 5))
    candidate_ids = [target(family, rows[i]) for i in (valid_index, invalid_index)]
    shuffled = deepcopy(rows)
    random.Random(seed).shuffle(shuffled)
    invalid = rows[invalid_index]
    if family == "escrow":
        fix = {"path": "authorization.for_receipt", "value": invalid["current_receipt"]}
        break_event = {"path": "current_receipt", "value": token(seed, family, valid_index, "revised_receipt")}
    elif family == "package":
        fix = {"path": "scan.subject_digest", "value": invalid["release_digest"]}
        break_event = {"path": "release_digest", "value": token(seed, family, valid_index, "revised_digest")}
    elif family == "retry_queue":
        fix = {"path": "result.state", "value": "passed"}
        break_event = {"path": "dispatch.attempt_uuid", "value": token(seed, family, valid_index, "new_attempt")}
    elif family == "ci_promotion":
        fix = {"path": "authorization.approved_digest", "value": invalid["build"]["digest"]}
        break_event = {"path": "build.digest", "value": token(seed, family, valid_index, "rebuilt")}
    else:
        fix = {"path": "consent.approved_output", "value": invalid["load"]["output_dataset"]}
        break_event = {"path": "load.output_dataset", "value": token(seed, family, valid_index, "reloaded")}
    futures = [
        {"id": f"{family}-{seed}-0", "target": candidate_ids[1],
         "event": {"path": "note", "value": "Schedule title updated; gate fields unchanged."}},
        {"id": f"{family}-{seed}-1", "target": candidate_ids[1], "event": fix},
        {"id": f"{family}-{seed}-2", "target": candidate_ids[0], "event": break_event},
    ]
    return {"id": f"{family}-{seed}", "family": family, "split": split,
            "tool_schema": deepcopy(SCHEMAS[family]), "tool_results": shuffled,
            "candidate_ids": candidate_ids, "futures": futures}


def truth(case, future):
    row = next(row for row in case["tool_results"] if target(case["family"], row) == future["target"])
    return terminal(case["family"], row, future["event"])


def grade(response, expected):
    return isinstance(response, dict) and set(response) == {"action", "target_id", "work"} and response == expected
