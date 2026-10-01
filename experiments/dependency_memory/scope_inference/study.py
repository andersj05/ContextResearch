"""Evaluator-side original-program grading; never sent to the learner."""
import ast
from copy import deepcopy
from itertools import combinations, product
import hashlib
import json
import random
from time import perf_counter_ns, process_time_ns

from experiments.dependency_memory.workflow_replay import evidence
from . import codec

SEED = 2026100102
MISSING = object()
HAND = {"value_paths": ["status", "error_type", "provider_metadata.dispatched", "provider_metadata.attempt_ticket",
                       "provider_metadata.credit_accounting.status", "provider_metadata.credit_accounting.ticket",
                       "provider_metadata.credit_accounting.conservative_credit_equivalent_exact"],
        "presence_paths": ["provider_metadata.usage", "provider_metadata.turn_id"],
        "nonempty_paths": ["provider_metadata"]}


def public_program():
    tree = ast.parse(evidence.pinned_bytes("scripts/prepare_transfer_continuation.py"))
    nodes = [n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name in {"exact", "classify_attempt"}]
    if {n.name for n in nodes} != {"exact", "classify_attempt"}:
        raise ValueError("Public historical functions missing")
    return ("from decimal import Decimal, InvalidOperation\nRESERVATION = Decimal('10.4025')\n"
            "def require(condition, message):\n    if not condition:\n        raise ValueError(message)\n\n"
            + "\n\n".join(ast.unparse(n) for n in nodes))


def schedule():
    rng, rows = random.Random(SEED), []
    for replicate in range(1, 5):
        variants = ["concise", "closure"]
        rng.shuffle(variants)
        rows += [{"identity": f"scope-r{replicate}-{v}", "replicate": replicate, "variant": v} for v in variants]
    return rows


def control_catalog():
    accounts = [MISSING, None, {}] + [
        {"status": "settled", "ticket": 1, "conservative_credit_equivalent_exact": value}
        for value in ("0.02", "NaN", "-1", "10.4026", 0)] + [
        {"status": "settled", "ticket": 2, "conservative_credit_equivalent_exact": "0.02"},
        {"status": "reservation_retained", "ticket": 1}]
    metadata = [MISSING, None, False, "", [], {}, {"unrelated": 1}]
    for flag, ticket, account, usage, turn in product((MISSING, False, True, 0, 1, None), (MISSING, 1, 0, True),
                                                   accounts, (MISSING, {}), (MISSING, "opaque")):
        meta = {}
        for key, value in (("dispatched", flag), ("attempt_ticket", ticket), ("credit_accounting", account),
                           ("usage", usage), ("turn_id", turn)):
            if value is not MISSING:
                meta[key] = deepcopy(value)
        metadata.append(meta)
    for status, error, meta in product((MISSING, "completed", "policy_failure", "transport_failure", "reserved"),
                                       (MISSING, "StudyStopped", "Other"), metadata):
        row = {}
        for key, value in (("status", status), ("error_type", error), ("provider_metadata", meta)):
            if value is not MISSING:
                row[key] = deepcopy(value)
        yield row


def answer(record, original):
    return evidence.original_decision(record, original)


def evaluate(contract, records, original, limit=6):
    rows, disagreements, dangerous, witnesses = 0, 0, 0, []
    cpu, wall = process_time_ns(), perf_counter_ns()
    for record in records:
        expected, retained = answer(record, original), codec.project(record, contract)
        observed = answer(retained, original)
        different = expected != observed
        false_preflight = observed[0] == "preflight_only" and expected[0] != "preflight_only"
        rows += 1
        disagreements += different
        dangerous += false_preflight
        if different and len(witnesses) < limit:
            witnesses.append({"original": record, "retained": retained, "expected": expected, "observed": observed})
    return {"cases": rows, "disagreements": disagreements, "false_preflight_only": dangerous, "witnesses": witnesses,
            "cpu_ns": process_time_ns() - cpu, "wall_ns": perf_counter_ns() - wall}


def staged(records, original, *, contract=None, kind="projection"):
    operations = []
    def measured(name, inputs, callback):
        cpu, wall = process_time_ns(), perf_counter_ns()
        output = callback()
        operations.append({"name": name, "read_bytes": len(codec.wire(inputs)), "write_bytes": len(codec.wire(output)),
                           "cpu_ns": process_time_ns() - cpu, "wall_ns": perf_counter_ns() - wall})
        return output
    def retained(record):
        value = answer(record, original) if kind == "cached" else codec.project(record, contract)
        return {"case_id": record["case_id"], "worker": record["worker"], "request_sha256": record["request_sha256"], "data": value}
    rows = measured("parent_transform", records, lambda: [retained(r) for r in records])
    parent, admission = codec.admit(rows, codec.PARENT_CAP)
    cases, correct, children = 0, 0, []
    for workers in combinations(range(4), 2):
        # The child reads only admitted parent memory, never the original ledger.
        available = json.loads(parent) if parent else []
        selected = measured("child_select", available, lambda: [r for r in available if r["worker"] in workers])
        child, child_admission = codec.admit(selected, codec.CHILD_CAP)
        data = {r["case_id"]: r for r in json.loads(child)} if child else {}
        for query in [r for r in records if r["worker"] in workers]:
            found = data.get(query["case_id"])
            if found is None or found["request_sha256"] != query["request_sha256"]:
                observed = ["unknown", None, None]
            elif kind == "cached":
                observed = found["data"]
            else:
                observed = measured("final_public_program", found["data"], lambda: answer(found["data"], original))
            cases += 1
            correct += observed == answer(query, original)
        children.append({"workers": list(workers), **child_admission})
    return {"parent": admission, "children": children, "final_queries": cases, "correct": correct,
            "operations": operations, "limits": "Constructed timing on eight inspected historical records; scripted final program."}


def catalog_lock():
    digest = hashlib.sha256()
    distinct = set()
    count = 0
    for row in control_catalog():
        digest.update(codec.wire(row) + b"\n")
        distinct.add(codec.wire(row))
        count += 1
    return {"records": count, "distinct_records": len(distinct), "sha256": digest.hexdigest()}


def offline_controls():
    original = evidence.historical_classifier()
    records, _ = evidence.load_snapshot()
    hand = {"catalog": evaluate(HAND, control_catalog(), original),
            "history": evaluate(HAND, records, original), "staged": staged(records, original, contract=HAND)}
    if hand["catalog"]["disagreements"] or hand["history"]["disagreements"]:
        raise AssertionError("Declared hand contract fails independent original program")
    return {"catalog": catalog_lock(), "hand": hand,
            "literal_ast": {"contract": codec.literal_roots(public_program()),
                "catalog": evaluate(codec.literal_roots(public_program()), control_catalog(), original),
                "staged": staged(records, original, contract=codec.literal_roots(public_program()))},
            "raw": {"staged": staged(records, original, contract={"value_paths": ["$"], "presence_paths": [], "nonempty_paths": []})},
            "cached": {"staged": staged(records, original, kind="cached")}}
