"""Evaluator-only reverse-scan receipt specification; no projection or guard import."""
from __future__ import annotations

CHECKS = ("paper", "repository", "tests")
ARTIFACTS = ("build/paper/manuscript.md", "build/paper/preview.html")


def digest(value, sizes=(64,)):
    return isinstance(value, str) and len(value) in sizes and all(c in "0123456789abcdef" for c in value)


def artifacts(value):
    return isinstance(value, dict) and all(name in ARTIFACTS and digest(code) for name, code in value.items())


def specification(records, task):
    """Stop at the first matching run when walking backward, including failures."""
    if not isinstance(records, list) or not isinstance(task, dict) or set(task) != {"snapshot", "required_checks", "artifacts"}:
        raise ValueError("Invalid specification inputs")
    requested = task["required_checks"]
    if (not digest(task["snapshot"], (40, 64)) or not isinstance(requested, list) or not requested
            or any(type(c) is not str or c not in CHECKS for c in requested)
            or requested != sorted(set(requested)) or not artifacts(task["artifacts"])):
        raise ValueError("Invalid reporting task")
    identities = set()
    for row in records:
        if (not isinstance(row, dict) or not {"check", "snapshot", "run_id", "returncode", "artifacts"} <= row.keys()
                or row["check"] not in CHECKS or not digest(row["snapshot"], (40, 64))
                or not digest(row["run_id"]) or row["run_id"] in identities
                or type(row["returncode"]) is not int or not artifacts(row["artifacts"])):
            raise ValueError("Invalid receipt")
        identities.add(row["run_id"])
        if row["check"] == "paper" and row["returncode"] == 0:
            if set(row["artifacts"]) != set(ARTIFACTS):
                raise ValueError("Missing successful build bindings")
        elif row["artifacts"]:
            raise ValueError("Unexpected build binding")
    found = {}
    outstanding = []
    for check in requested:
        latest = next((r for r in reversed(records) if (r["snapshot"], r["check"]) == (task["snapshot"], check)), None)
        if latest is None or latest["returncode"] != 0:
            outstanding.append(check)
            continue
        if any(name not in task["artifacts"] or task["artifacts"][name] != code for name, code in latest["artifacts"].items()):
            outstanding.append(check)
            continue
        found[check] = latest["run_id"]
    return {"ready": len(outstanding) == 0, "needs_work": outstanding, "evidence": found}
