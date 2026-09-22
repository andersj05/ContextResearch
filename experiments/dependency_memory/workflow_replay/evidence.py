"""Pinned evidence, an independent historical grader, and a public-rule adapter.

Only the AST bodies of two pure historical functions are compiled. Imports,
runner entry points, provider clients, and filesystem helpers are never run.
"""
from __future__ import annotations

import ast
from copy import deepcopy
from decimal import Decimal, InvalidOperation
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
PREFIX = "experiments/dependency_memory/results/transfer_luna_2026-09-19_authorized"
HISTORICAL_COMMIT = "04141984d56fa0f80429d19dc45f589fef8ac5a6"
HASHES = {
    "scripts/prepare_transfer_continuation.py": "345c3f52e52d8e210394d236dd5c4d2671fd476fc50cca8fddec22095a91fc92",
    "experiments/dependency_memory/results/transfer_continuation_plan.json": "32312a03ee43f66870a7893abaee2518c1653d403a2fcdd2d69e89f168a93d41",
    **{f"{PREFIX}/worker-{w}/requests.json": h for w, h in enumerate((
        "45fa109db723d148998ae66182c3d3d7450e363de92191ac54692508683ac0bb",
        "64e7d18b166cd831502c41a613de4b40191bb59140d45e4d225ab71888bc9600",
        "e82a34b826069007e75933a1ff7876a44832eecb3fc424e6164b3fe77a1d30d2",
        "30685f0b0c4770c8f289da77b595801279566d5e5b27fee10a01dddde4d8b10c"))},
}


def wire(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=False, allow_nan=False).encode("utf-8")


def digest(value):
    return hashlib.sha256(wire(value)).hexdigest()


def pinned_bytes(name):
    raw = (ROOT / name).read_bytes()
    if hashlib.sha256(raw).hexdigest() != HASHES[name]:
        raise ValueError("Pinned historical evidence changed: " + name)
    return raw


def historical_classifier():
    """Independent original function, without executing its module."""
    raw = pinned_bytes("scripts/prepare_transfer_continuation.py")
    tree = ast.parse(raw)
    nodes = [n for n in tree.body if isinstance(n, ast.FunctionDef)
             and n.name in ("exact", "classify_attempt")]
    if {n.name for n in nodes} != {"exact", "classify_attempt"}:
        raise ValueError("Historical pure functions not found")

    def require(condition, message):
        if not condition:
            raise ValueError(message)

    namespace = {"Decimal": Decimal, "InvalidOperation": InvalidOperation,
                 "RESERVATION": Decimal("10.4025"), "require": require}
    exec(compile(ast.Module(body=nodes, type_ignores=[]), "pinned_historical_classifier", "exec"), namespace)
    return namespace["classify_attempt"]


def original_decision(record, classifier):
    try:
        kind, spent, reserved = classifier(record)
        result = [kind, str(spent), str(reserved)]
    except ValueError:
        result = ["unknown", None, None]
    return result


def load_snapshot():
    records, provenance = [], []
    plan = json.loads(pinned_bytes("experiments/dependency_memory/results/transfer_continuation_plan.json"))
    dispositions = {r["case_id"]: r for r in plan["case_dispositions"]}
    reference = historical_classifier()
    for worker in range(4):
        name = f"{PREFIX}/worker-{worker}/requests.json"
        ledger = json.loads(pinned_bytes(name))
        for index in range(len(ledger) - 2, len(ledger)):
            row = ledger[index]
            if row["worker"] != worker or row["attempt"] != index + 1:
                raise ValueError("Historical selector identity mismatch")
            if hashlib.sha256(row["request_utf8"].encode("utf-8")).hexdigest() != row["request_sha256"]:
                raise ValueError("Request identity mismatch")
            expected = original_decision(row, reference)
            saved = dispositions[row["case_id"]]["prior_attempt_history"][-1]
            if expected != [saved["classification"], saved["settled_credit_equivalent_exact"],
                            saved["retained_reservation_exact"]]:
                raise ValueError("Independent function and saved continuation disagree")
            records.append(row)
            provenance.append({"source": name, "source_sha256": HASHES[name],
                "array_index": index, "record_sha256": digest(row),
                "case_id": row["case_id"], "request_sha256": row["request_sha256"],
                "worker": worker, "historical_decision": expected,
                "canonical_observation_bytes": len(wire(row))})
    return records, provenance


def project(record):
    """Keep ALL inputs needed by the historical pure checker, including absence.

    This is an explicitly authored adapter from read source code, not a learned
    natural-language extractor. The marker preserves the empty-metadata test.
    Values of usage/turn_id do not matter, but their presence does.
    """
    result = {k: deepcopy(record[k]) for k in ("status", "error_type") if k in record}
    if "provider_metadata" not in record:
        return result
    meta = record["provider_metadata"]
    if type(meta) is not dict:
        result["provider_metadata"] = deepcopy(meta)
        return result
    selected = {k: deepcopy(meta[k]) for k in ("dispatched", "attempt_ticket") if k in meta}
    for k in ("usage", "turn_id"):
        if k in meta:
            selected[k] = True
    if "credit_accounting" in meta:
        account = meta["credit_accounting"]
        selected["credit_accounting"] = (
            {k: deepcopy(account[k]) for k in ("status", "ticket", "conservative_credit_equivalent_exact") if k in account}
            if type(account) is dict else deepcopy(account))
    if meta and not selected:
        selected["_other_metadata_present"] = True
    result["provider_metadata"] = selected
    return result


SCHEMA = {"status": None, "error_type": None, "provider_metadata": {
    "dispatched": None, "attempt_ticket": None,
    "credit_accounting": {"status": None, "ticket": None, "conservative_credit_equivalent_exact": None},
    "usage": None, "turn_id": None, "_other_metadata_present": None}}


def encode_fields(value, schema=SCHEMA):
    """Fixed public schema, presence mask, and literal values; no instance codebook."""
    if schema is None:
        return value
    if type(value) is not dict:
        return [0, value]
    if set(value) - set(schema):
        raise ValueError("Unexpected projection field")
    mask, values = 0, []
    for i, (key, child) in enumerate(schema.items()):
        if key in value:
            mask |= 1 << i
            values.append(encode_fields(value[key], child))
    return [1, mask, *values]


def decode_fields(value, schema=SCHEMA):
    if schema is None:
        return value
    if value[0] == 0:
        return value[1]
    result, cursor = {}, 2
    for i, (key, child) in enumerate(schema.items()):
        if value[1] & (1 << i):
            result[key] = decode_fields(value[cursor], child)
            cursor += 1
    if cursor != len(value):
        raise ValueError("Trailing schema values")
    return result


def classify(record):
    """Separately implemented public decision rule; refuse incomplete evidence."""
    status = record.get("status")
    meta = record.get("provider_metadata")
    unknown = ["unknown", None, None]
    if status not in ("completed", "policy_failure", "transport_failure") or type(meta) is not dict:
        return unknown
    flag = meta.get("dispatched")
    if flag is True:
        ticket, account = meta.get("attempt_ticket"), meta.get("credit_accounting")
        if type(ticket) is not int or ticket <= 0 or type(account) is not dict or account.get("ticket") != ticket:
            return unknown
        if account.get("status") == "reservation_retained" and status == "transport_failure":
            return ["dispatched_uncertain", "0", "10.4025"]
        if account.get("status") != "settled":
            return unknown
        amount = account.get("conservative_credit_equivalent_exact")
        if type(amount) is not str:
            return unknown
        try:
            spent = Decimal(amount)
        except InvalidOperation:
            return unknown
        if not spent.is_finite() or spent < 0 or spent > Decimal("10.4025"):
            return unknown
        return ["dispatched", str(spent), "0"]
    if status != "transport_failure":
        return unknown
    if flag is False:
        if any(k in meta for k in ("attempt_ticket", "credit_accounting", "usage", "turn_id")):
            return unknown
        return ["preflight_only", "0", "0"]
    if not meta and record.get("error_type") == "StudyStopped":
        return ["preflight_only", "0", "0"]
    return unknown


def dependency_fingerprint(record):
    """Also bind identity and actual request bytes, not only a supplied hash."""
    return digest({"case_id": record.get("case_id"), "request_sha256": record.get("request_sha256"),
                   "request_utf8": record.get("request_utf8"), "evidence": project(record)})


def make_scoped_receipt(record, checker_revision):
    return {"checker_revision": checker_revision, "dependency_sha256": dependency_fingerprint(record),
            "result": classify(record)}


def reuse_receipt(receipt, record, checker_revision):
    # The caller must charge reading/hashing current evidence; no free oracle.
    if (receipt["checker_revision"] != checker_revision or
            receipt["dependency_sha256"] != dependency_fingerprint(record)):
        return None
    return deepcopy(receipt["result"])
