"""Pure public-data methods. No evaluator, filesystem, provider or archive client."""
from copy import deepcopy
import json

from experiments.dependency_memory.evidence_use.guard import (
    CHECKS, RECEIPT_RULE, receipt_answer, strict_json,
)
from experiments.dependency_memory.workflow_intake.views import actor_view, PARENT_CAP, CHILD_CAP

VERSION = "single_repository_method_v1"
SEED = 2026100101
MAX_REQUEST_BYTES = 262144
ARMS = ("direct", "indexed", "prose", "full")
FIELDS = ("check", "snapshot", "run_id", "returncode", "artifacts")
MEMORY_SCHEMA = {"type": "object", "properties": {"memory": {"type": "string"}},
                 "required": ["memory"], "additionalProperties": False}
FINAL_SCHEMA = {"type": "object", "properties": {
    "ready": {"type": "boolean"}, "needs_work": {"type": "array", "items": {"type": "string", "enum": list(CHECKS)}},
    "evidence": {"type": "object", "properties": {c: {"type": ["string", "null"]} for c in CHECKS},
                 "required": list(CHECKS), "additionalProperties": False}},
    "required": ["ready", "needs_work", "evidence"], "additionalProperties": False}


def wire(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True, allow_nan=False).encode("utf-8")


def validate_receipts(records):
    # Public-schema validation only; the dummy task carries no instance label.
    receipt_answer(wire(records).decode(), {"snapshot": "0" * 40, "required_checks": list(CHECKS), "artifacts": {}})


def project(records, scope=CHECKS):
    validate_receipts(records)
    if not set(scope) <= set(CHECKS):
        raise ValueError("Unknown announced scope")
    positions = {}
    for position, row in enumerate(records):
        if row["check"] in scope:
            positions[(row["snapshot"], row["check"])] = position
    return [{field: deepcopy(records[position][field]) for field in FIELDS} for position in sorted(positions.values())]


def direct_memory(records, cap, scope=CHECKS):
    encoded = wire(project(records, scope)).decode()
    size = len(encoded.encode("utf-8"))
    return (encoded if size <= cap else ""), {"proposal_bytes": size, "infeasible": size > cap}


def admit_prose(response, cap):
    memory = response.get("memory") if isinstance(response, dict) and set(response) == {"memory"} else None
    size = len(memory.encode("utf-8")) if isinstance(memory, str) else None
    accepted = size is not None and size <= cap
    return (memory if accepted else ""), {"accepted": accepted, "proposal_bytes": size, "infeasible": not accepted}


def checked_shadow(response, available, cap, scope=CHECKS):
    """Canonical exact-table diagnostic, never a paid arm in this method."""
    required = project(available, scope)
    memory, admission = admit_prose(response, cap)
    passed = False
    if admission["accepted"]:
        try:
            proposed = strict_json(memory)
            validate_receipts(proposed)
            passed = (all(set(row) == set(FIELDS) for row in proposed)
                      and len(proposed) == len(required)
                      and {r["run_id"]: r for r in proposed} == {r["run_id"]: r for r in required})
        except (ValueError, TypeError, KeyError, RecursionError):
            pass
    canonical, audit = direct_memory(available, cap, scope)
    return canonical, {**audit, "certificate_passed": passed, "fallback": not passed, "canonicalized": True}


def request_bytes(request):
    if (set(request) != {"version", "stage", "instruction", "observation", "response_schema"}
            or request["version"] != VERSION or request["stage"] not in {"parent", "child", "execute"}):
        raise ValueError("Unknown request envelope")
    stage = request["stage"]
    fields = {"parent": {"tool_observations"}, "child": {"previous_memory", "new_observations", "scope"},
              "execute": {"memory", "final_public_state"}}[stage]
    if set(request["observation"]) != fields:
        raise ValueError("Undeclared actor observation")
    encoded = wire(request)
    if len(encoded) > MAX_REQUEST_BYTES:
        raise ValueError("Public request exceeds the frozen byte cap")
    return encoded


def memory_request(case, stage, parent=None):
    cap = PARENT_CAP if stage == "parent" else CHILD_CAP
    instruction = (RECEIPT_RULE + "\nPreserve exact snapshot/run identifiers, chronological supersession, failures and artifact bindings. "
                   "Keep facts for all possible checks at the parent. At the child keep facts for checks in the announced scope "
                   "on every available snapshot; the final snapshot and a subset of scope are disclosed later. "
                   "Use concise prose. Public rules are repeated. Return one string field memory with at most " + str(cap) + " decoded UTF-8 bytes.")
    request = {"version": VERSION, "stage": stage, "instruction": instruction,
               "observation": actor_view(case, stage, parent), "response_schema": deepcopy(MEMORY_SCHEMA)}
    request_bytes(request)
    return request


def final_request(memory, case):
    request = {"version": VERSION, "stage": "execute", "instruction": RECEIPT_RULE +
               "\nUse only the admitted view. Include all three evidence keys paper, repository, tests; use null for absent evidence.",
               "observation": {"memory": memory, "final_public_state": {k: deepcopy(case["task"][k])
                               for k in ("snapshot", "required_checks", "artifacts")}}, "response_schema": deepcopy(FINAL_SCHEMA)}
    request_bytes(request)
    return request


def normalize(response):
    if (isinstance(response, dict) and set(response) == {"ready", "needs_work", "evidence"}
            and isinstance(response["evidence"], dict) and set(response["evidence"]) == set(CHECKS)):
        return {**response, "evidence": {k: v for k, v in response["evidence"].items() if v is not None}}
    return response
