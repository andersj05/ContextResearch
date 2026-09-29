"""Fixed observed development capture plus three explicitly constructed controls."""
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import random

from experiments.dependency_memory.workflow_eval.grader import CHECKS, RECEIPT_FIELDS, strict_json, validate_records, wire
from experiments.dependency_memory.workflow_eval.packet import HERE as PACKET, direct_records, validate_capture, validate_lock
from .protocol import VERSION, MEMORY_SCHEMA, request_bytes

ARMS = ("checked", "direct", "indexed", "prose", "full")
PARENT_CAP, CHILD_CAP = 4096, 1536
SEED = 20260929
PROMPTS = json.loads((PACKET / "prompts.json").read_text(encoding="utf-8"))
FINAL_SCHEMA = {"type": "object", "properties": {
    "ready": {"type": "boolean"},
    "needs_work": {"type": "array", "items": {"type": "string", "enum": list(CHECKS)}},
    "evidence": {"type": "object", "properties": {c: {"type": ["string", "null"]} for c in CHECKS},
                 "required": list(CHECKS), "additionalProperties": False}},
    "required": ["ready", "needs_work", "evidence"], "additionalProperties": False}


def cases():
    validate_lock()
    capture = validate_capture()
    observations = []
    for row in capture["records"]:
        public = {key: deepcopy(row[key]) for key in RECEIPT_FIELDS}
        public["argv"] = row["argv"]
        for stream in ("stdout", "stderr"):
            # Exact Windows newline bytes are decoded, never normalized.
            public[stream] = (PACKET / "development" / row[stream]["path"]).read_bytes().decode("utf-8")
        observations.append(public)
    task = {"snapshot": capture["source"]["tree"], "required_checks": list(CHECKS),
            "artifacts": deepcopy(observations[-1]["artifacts"])}
    result = []
    for name in ("unchanged", "new_snapshot", "later_failure", "replaced_artifact"):
        row = {"id": name, "origin": "observed_local_capture" if name == "unchanged" else "constructed_control",
               "initial": deepcopy(observations), "between": [], "scope": list(CHECKS), "task": deepcopy(task)}
        if name == "new_snapshot":
            row["task"]["snapshot"] = hashlib.sha256(b"workflow-eval-v1-constructed-source-change").hexdigest()
        if name == "later_failure":
            failed = deepcopy(observations[0])
            failed.update(returncode=1, stdout="", stderr="Constructed control: a later test attempt failed.\n")
            failed["run_id"] = hashlib.sha256(wire({k: v for k, v in failed.items() if k != "run_id"})).hexdigest()
            row["between"] = [failed]
        if name == "replaced_artifact":
            row["task"]["artifacts"]["build/paper/preview.html"] = hashlib.sha256(b"constructed replacement artifact").hexdigest()
        result.append(row)
    return result


def normalize_response(response):
    if not isinstance(response, dict) or set(response) != {"ready", "needs_work", "evidence"}:
        return response
    evidence = response["evidence"]
    if not isinstance(evidence, dict) or set(evidence) != set(CHECKS):
        return response
    return {**response, "evidence": {k: v for k, v in evidence.items() if v is not None}}


def request(stage, instruction, observation, schema):
    result = {"version": VERSION, "stage": stage, "instruction": instruction,
              "observation": observation, "response_schema": schema}
    request_bytes(result)
    return result


def memory_request(stage, arm, observation):
    cap = PARENT_CAP if stage == "parent" else CHILD_CAP
    extra = ("Use a JSON list of receipt objects with exactly the fields check, snapshot, run_id, returncode, artifacts. "
             if arm == "checked" else "")
    instruction = (PROMPTS["public_rule"] + "\n" + PROMPTS["candidate_writer" if arm == "checked" else "prose_writer"]
                   + f"\n{extra}Return an object with one string field memory. Its decoded UTF-8 bytes must be <= {cap}.")
    return request(stage, instruction, observation, MEMORY_SCHEMA)


def final_request(memory, task):
    instruction = (PROMPTS["public_rule"] + "\n" + PROMPTS["final"]
                   + "\nSerialization: include all three evidence keys paper, repository, tests; use null for absent evidence.")
    return request("execute", instruction, {"memory": memory, "final_public_state": task}, FINAL_SCHEMA)


def admit_prose(response, cap):
    memory = response.get("memory") if isinstance(response, dict) and set(response) == {"memory"} else None
    if not isinstance(memory, str):
        return "", {"accepted": False, "reason": "invalid_memory_response", "proposal_bytes": None}
    size = len(memory.encode("utf-8"))
    return (memory if size <= cap else ""), {"accepted": size <= cap,
        "reason": "accepted" if size <= cap else "over_cap", "proposal_bytes": size}


def checked_memory(response, available, cap):
    memory, audit = admit_prose(response, cap)
    required = direct_records(available)
    passed = False
    if audit["accepted"]:
        try:
            decoded = strict_json(memory)
            validate_records(decoded)
            passed = (all(set(r) == set(RECEIPT_FIELDS) for r in decoded)
                      and len(decoded) == len(required)
                      and {r["run_id"]: r for r in decoded} == {r["run_id"]: r for r in required})
        except (ValueError, TypeError, KeyError, RecursionError):
            passed = False
    if passed:
        return memory, {**audit, "certificate_passed": True, "fallback": False}
    fallback = wire(required).decode()
    if len(fallback.encode()) > cap:
        return "", {**audit, "certificate_passed": False, "fallback": True, "infeasible": True}
    return fallback, {**audit, "certificate_passed": False, "fallback": True, "infeasible": False}


def order(case_id, arms):
    result = list(arms)
    random.Random(str(SEED) + ":" + case_id + ":" + ",".join(arms)).shuffle(result)
    return result


def schedule():
    result = []
    for case in cases():
        for stage in ("parent", "child"):
            for arm in order(case["id"] + stage, ("checked", "prose")):
                result.append(f"{case['id']}-{arm}-{stage}")
        result.extend(f"{case['id']}-{arm}-final" for arm in order(case["id"], ARMS))
    return result


def audit_request():
    candidates = []
    for case in cases():
        candidates.extend(memory_request("parent", a, {"tool_observations": case["initial"]}) for a in ("checked", "prose"))
        candidates.append(final_request(wire(case["initial"] + case["between"]).decode(), case["task"]))
    return max(candidates, key=lambda r: len(request_bytes(r)))
