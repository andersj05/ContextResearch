"""Terminal receipt grading, independent of memory extraction and model clients.

This grades a declared reporting contract, not the correctness of arbitrary
source code. Ledger ordering and content come from an evaluator-owned capture.
"""
from __future__ import annotations

import json
import re

CHECKS = ("paper", "repository", "tests")
ARTIFACTS = ("build/paper/manuscript.md", "build/paper/preview.html")
RECEIPT_FIELDS = ("check", "snapshot", "run_id", "returncode", "artifacts")


def strict_json(raw: str):
    def unique(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise ValueError("Duplicate JSON key: " + key)
            result[key] = value
        return result

    def invalid(value):
        raise ValueError("Nonfinite JSON value: " + value)

    return json.loads(raw, object_pairs_hook=unique, parse_constant=invalid)


def wire(value) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"),
                      allow_nan=False).encode("utf-8")


def _hash(value, lengths=(64,)):
    return (isinstance(value, str) and len(value) in lengths
            and re.fullmatch("[0-9a-f]+", value) is not None)


def _artifacts(value):
    return (isinstance(value, dict) and all(
        isinstance(k, str) and k in ARTIFACTS and _hash(v)
        for k, v in value.items()))


def validate_records(records):
    if not isinstance(records, list):
        raise ValueError("Observation ledger must be a list")
    seen = set()
    for row in records:
        if not isinstance(row, dict) or not set(RECEIPT_FIELDS) <= row.keys():
            raise ValueError("Incomplete receipt")
        if (row["check"] not in CHECKS or not _hash(row["snapshot"], (40, 64))
                or not _hash(row["run_id"]) or type(row["returncode"]) is not int
                or not _artifacts(row["artifacts"])):
            raise ValueError("Invalid receipt fields")
        if row["run_id"] in seen:
            raise ValueError("Duplicate run identity")
        seen.add(row["run_id"])
        if row["check"] == "paper" and row["returncode"] == 0:
            if set(row["artifacts"]) != set(ARTIFACTS):
                raise ValueError("Successful paper receipt must bind both artifacts")
        elif row["artifacts"]:
            raise ValueError("Unexpected artifacts on a non-build/failed receipt")


def validate_task(task):
    if not isinstance(task, dict) or set(task) != {"snapshot", "required_checks", "artifacts"}:
        raise ValueError("Invalid task fields")
    required = task["required_checks"]
    if (not _hash(task["snapshot"], (40, 64)) or not isinstance(required, list)
            or not required or any(not isinstance(c, str) or c not in CHECKS for c in required)
            or required != sorted(set(required)) or not _artifacts(task["artifacts"])):
        raise ValueError("Invalid public task")


def expected_answer(records, task):
    """Use the latest observed run for each requested check on the final tree.

    Intentionally scan the raw ledger for each obligation. Do not import a
    compactor, index, projection, model response or compatibility certificate.
    """
    validate_records(records)
    validate_task(task)
    evidence = {}
    needs_work = []
    for check in task["required_checks"]:
        matches = [row for row in records
                   if row["check"] == check and row["snapshot"] == task["snapshot"]]
        latest = matches[-1] if matches else None
        valid = (latest is not None and latest["returncode"] == 0 and all(
            task["artifacts"].get(path) == value
            for path, value in latest["artifacts"].items()))
        if valid:
            evidence[check] = latest["run_id"]
        else:
            needs_work.append(check)
    return {"ready": not needs_work, "needs_work": needs_work, "evidence": evidence}


def grade(records, task, response: str):
    expected = expected_answer(records, task)
    # Programmer/evidence errors above are not swallowed as model failures.
    try:
        answer = strict_json(response)
        if not isinstance(answer, dict) or set(answer) != {"ready", "needs_work", "evidence"}:
            raise ValueError("Answer must contain exactly ready, needs_work and evidence")
        if (type(answer["ready"]) is not bool or not isinstance(answer["needs_work"], list)
                or any(not isinstance(c, str) or c not in task["required_checks"]
                       for c in answer["needs_work"])
                or answer["needs_work"] != sorted(set(answer["needs_work"]))
                or not isinstance(answer["evidence"], dict)
                or any(k not in task["required_checks"] or not _hash(v)
                       for k, v in answer["evidence"].items())):
            raise ValueError("Answer contains invalid field types or identities")
    except (ValueError, TypeError, RecursionError) as error:
        return {"exact": False, "malformed": True, "false_ready": None,
                "reason": str(error), "expected": expected}
    return {"exact": answer == expected, "malformed": False,
            "false_ready": answer["ready"] and not expected["ready"],
            "reason": "match" if answer == expected else "terminal_mismatch",
            "expected": expected}
