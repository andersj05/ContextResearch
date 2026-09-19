"""Strict public interface for the cold revision-aware parent diagnostic.

No candidate pair, target, evaluator label, expected answer, or previous model
response is an input. This contract is separate from pilot_public_request_v1.
"""
from __future__ import annotations

import json
import re

VERSION = "revision_parent_request_v1"
KEYS = tuple(f"job-{index}" for index in range(6))
RULES = ("lexicographic_first", "lexicographic_last", "none")
PUBLIC_MODEL = {"jobs": 6, "candidate_count": 2,
                "parent_capacity_records": 2, "child_capacity_records": 2}
REFRESH_TEXT = {
    "lexicographic_first": "The build supplies revision two of the lexicographically first candidate job, even if its old receipt was discarded. Other jobs are not refreshed. ",
    "lexicographic_last": "The build supplies revision two of the lexicographically last candidate job, even if its old receipt was discarded. Other jobs are not refreshed. ",
    "none": "The build does not refresh any job. No additional receipt is supplied. ",
}
PREFIX = (
    "Select receipt records to keep at the first of two irreversible memory boundaries. "
    "All six initial records are currently visible. After this selection, a candidate pair "
    "is sampled uniformly from all unordered pairs of distinct jobs and disclosed to a later selector. "
)
SUFFIX = (
    "The later selector is guaranteed to choose optimally from your retained records and any "
    "newly supplied receipt, subject to the two-record child capacity. It cannot recover discarded "
    "original receipts or read this conversation. After the second boundary, the required job "
    "is sampled uniformly from the candidate pair. Completion needs that job's latest receipt. "
    "Choose at most two distinct keys to maximize the probability that the required latest "
    "receipt is available after the second boundary. The host keeps exactly the selected records; "
    "all other initial receipts and your response text are discarded. Return only the JSON object "
    "{\"keys\": [selected keys]}. Do not return explanations, receipt values, or extra fields."
)


def response_schema():
    return {"type": "object", "properties": {"keys": {
        "type": "array", "maxItems": 2, "uniqueItems": True,
        "items": {"type": "string", "enum": list(KEYS)}}},
        "required": ["keys"], "additionalProperties": False}


def _records(records):
    if type(records) is not list or len(records) != len(KEYS):
        raise ValueError("Exactly six initial receipts are required")
    seen = set()
    for row in records:
        if type(row) is not dict or set(row) != {"key", "revision", "token"}:
            raise ValueError("Unexpected receipt fields")
        if type(row["key"]) is not str or row["key"] not in KEYS or row["key"] in seen:
            raise ValueError("Unknown or duplicate key")
        if type(row["revision"]) is not int or row["revision"] != 1:
            raise ValueError("Only initial revision-one receipts are permitted")
        if type(row["token"]) is not str or re.fullmatch(r"[0-9a-f]{32}", row["token"]) is None:
            raise ValueError("Receipt payload must be an opaque 32-digit hex value")
        seen.add(row["key"])


def build_request(refresh_rule, record_order, records):
    _records(records)
    if refresh_rule not in RULES:
        raise ValueError("Unknown refresh rule")
    if (type(record_order) not in (list, tuple) or len(record_order) != 6
            or any(type(key) is not str for key in record_order)
            or set(record_order) != set(KEYS)):
        raise ValueError("Record order must be a permutation of all six keys")
    by_key = {row["key"]: row for row in records}
    request = {"version": VERSION, "kind": "parent_retention",
        "refresh_rule": refresh_rule, "public_model": dict(PUBLIC_MODEL),
        "public_metadata": {"job_keys": list(KEYS)},
        "visible_records": [dict(by_key[key]) for key in record_order],
        "instructions": PREFIX + REFRESH_TEXT[refresh_rule] + SUFFIX,
        "response_schema": response_schema()}
    validate_request(request)
    return request


def validate_request(request):
    fields = {"version", "kind", "refresh_rule", "public_model", "public_metadata",
              "visible_records", "instructions", "response_schema"}
    if type(request) is not dict or set(request) != fields:
        raise ValueError("Unexpected request fields")
    if request["version"] != VERSION or request["kind"] != "parent_retention":
        raise ValueError("Unknown public request contract")
    rule = request["refresh_rule"]
    if type(rule) is not str or rule not in RULES:
        raise ValueError("Unknown public refresh rule")
    model = request["public_model"]
    if (type(model) is not dict or set(model) != set(PUBLIC_MODEL)
            or any(type(model[k]) is not int or model[k] != v for k, v in PUBLIC_MODEL.items())):
        raise ValueError("Changed public model")
    if request["public_metadata"] != {"job_keys": list(KEYS)}:
        raise ValueError("Unexpected static metadata")
    _records(request["visible_records"])
    if request["instructions"] != PREFIX + REFRESH_TEXT[rule] + SUFFIX:
        raise ValueError("Unexpected instruction text")
    if json.dumps(request["response_schema"], sort_keys=True) != json.dumps(response_schema(), sort_keys=True):
        raise ValueError("Unexpected output schema")


def request_bytes(request):
    validate_request(request)
    return json.dumps(request, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=False, allow_nan=False).encode("utf-8")


def validate_response(response, request):
    validate_request(request)
    if type(response) is not dict or set(response) != {"keys"} or type(response["keys"]) is not list:
        raise ValueError("Expected exactly one keys array")
    keys = response["keys"]
    if (any(type(key) is not str for key in keys) or len(keys) > 2
            or len(set(keys)) != len(keys) or not set(keys) <= set(KEYS)):
        raise ValueError("Unknown, duplicate, or excess selected keys")
    return tuple(sorted(keys))
