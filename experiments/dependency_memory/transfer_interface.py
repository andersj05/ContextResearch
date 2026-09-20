"""Allowlisted public requests for the matched parent-retention transfer study.

This is a new public contract, separate from both earlier pilot interfaces. It
accepts no future candidate pair, target, evaluator answer, request identifier,
or previous response. Priorities and receipt/order blocks are public inputs;
their route independence belongs to the separately frozen evaluator schedule.

Factor labels select fixed wording but are not serialized. Unspecified later
selection makes no optimality promise. An ideal-child grade in that condition
measures conditional retention potential, not the behavior of a tested child.
"""

from __future__ import annotations

from itertools import product
import json
import re


VERSION = "transfer_parent_request_v1"
JOB_COUNTS = (6, 12)
FRAMINGS = ("compact", "workflow")
GUARANTEES = ("explicit_optimal", "unspecified")
GUIDANCE = ("generic", "prospective")
RULES = ("first", "last", "none")
_MODEL_FIELDS = {"jobs", "candidate_count", "parent_capacity_records", "child_capacity_records"}
_PREFIX = {
    "compact": "You are selecting receipt records for a two-stage retention task. ",
    "workflow": "You are maintaining receipt records for a completed-build handoff. ",
}
_COMMON = (
    "All jobs' initial revision-one receipt records are currently visible. Public metadata "
    "assigns each job a unique refresh_priority; smaller integers mean lower priority. "
    "Key names and display order do not define this priority. The priority assignment is "
    "fixed before the candidate pair is drawn. After your first-boundary selection, a "
    "candidate pair is sampled uniformly from all unordered pairs of distinct jobs and "
    "disclosed to the later selector. "
)
_REFRESH = {
    "first": (
        "The build then supplies revision two of the candidate with the minimum "
        "refresh_priority, even if its old receipt was discarded. Other jobs are not refreshed. "
    ),
    "last": (
        "The build then supplies revision two of the candidate with the maximum "
        "refresh_priority, even if its old receipt was discarded. Other jobs are not refreshed. "
    ),
    "none": "The build does not refresh any job. No additional receipt is supplied. ",
}
_CHILD = (
    "The later selector sees the candidate pair, public metadata, your retained records, "
    "and any newly supplied receipt. At the second boundary it may retain at most two "
    "current records. It cannot retrieve discarded original receipts, view this request, "
    "or read previous responses. "
)
_GUARANTEE = {
    "explicit_optimal": (
        "The later selector is guaranteed to choose optimally from those available records "
        "to maximize required-latest-receipt availability. "
    ),
    "unspecified": (
        "The later selector makes its own selection from those available records and "
        "returns the records retained at that boundary. "
    ),
}
_OBJECTIVE = (
    "After the second boundary, the required job is sampled uniformly from the candidate "
    "pair. Completion needs that job's latest receipt. Choose at most two distinct keys "
    "to maximize the probability that the required latest receipt is available immediately "
    "after the second boundary, before any optional recovery. "
)
_GUIDANCE = {
    "generic": (
        "Review the stated task carefully when choosing what to retain. Consider the "
        "available evidence and memory limits, and select records that support eventual "
        "completion under the described sequence of events. "
    ),
    "prospective": (
        "Review future information arrivals when choosing what to retain. Consider which "
        "evidence will be supplied again and which will not, and protect records that must "
        "survive the described sequence of events. "
    ),
}
_OUTPUT = (
    "The host keeps exactly your selected records; all other initial receipts and your "
    "response text are discarded. Return only the JSON object {\"keys\": [selected keys]}. "
    "Do not return explanations, receipt values, or extra fields."
)
_WORKFLOW_CONTEXT = (
    ("collection_complete", "The scheduled jobs finished and their initial revision-one receipts are now visible."),
    ("checkpoint_due", "The workflow is waiting at its first memory boundary; no candidate manifest is available yet."),
    ("build_pending", "After this checkpoint, a build applies the public refresh rule and a second memory boundary follows."),
)


def job_keys(jobs):
    if type(jobs) is not int or jobs not in JOB_COUNTS:
        raise ValueError("The transfer interface supports exactly six or twelve jobs")
    return tuple(f"job-{index:02d}" for index in range(jobs))


def response_schema(jobs):
    return {"type": "object", "properties": {"keys": {
        "type": "array", "maxItems": 2, "uniqueItems": True,
        "items": {"type": "string", "enum": list(job_keys(jobs))}}},
        "required": ["keys"], "additionalProperties": False}


def _instructions(rule, framing, guarantee, guidance):
    return (_PREFIX[framing] + _COMMON + _REFRESH[rule] + _CHILD + _GUARANTEE[guarantee]
            + _OBJECTIVE + _GUIDANCE[guidance] + _OUTPUT)


def _context(framing):
    return ([{"event": event, "description": description} for event, description in _WORKFLOW_CONTEXT]
            if framing == "workflow" else [])


def _priorities(priorities, keys):
    if (type(priorities) is not dict or set(priorities) != set(keys)
            or any(type(value) is not int for value in priorities.values())
            or set(priorities.values()) != set(range(len(keys)))):
        raise ValueError("Priorities must map every canonical key to a distinct integer from zero to jobs minus one")


def _records(records, keys):
    if type(records) is not list or len(records) != len(keys):
        raise ValueError("Exactly one initial receipt is required for every canonical job")
    seen = set()
    for row in records:
        if type(row) is not dict or set(row) != {"key", "revision", "token"}:
            raise ValueError("Unexpected receipt fields")
        if type(row["key"]) is not str or row["key"] not in keys or row["key"] in seen:
            raise ValueError("Unknown or duplicate job key")
        if type(row["revision"]) is not int or row["revision"] != 1:
            raise ValueError("Only initial revision-one receipts are permitted")
        if type(row["token"]) is not str or re.fullmatch(r"[0-9a-f]{32}", row["token"]) is None:
            raise ValueError("Receipt payload must be an opaque 32-digit hex value")
        seen.add(row["key"])


def build_request(*, jobs, refresh_rule, priorities, record_order, records, framing, guarantee, guidance):
    """Build one fresh request from public configuration and initial records.

    Factor labels are used only to select fixed text, never passed through as
    evaluator annotations. The caller must choose priorities/order/payloads
    before any candidate or target information exists.
    """
    keys = job_keys(jobs)
    for value, allowed in ((refresh_rule, RULES), (framing, FRAMINGS),
                           (guarantee, GUARANTEES), (guidance, GUIDANCE)):
        if type(value) is not str or value not in allowed:
            raise ValueError("Unknown public text or refresh condition")
    _priorities(priorities, keys)
    _records(records, keys)
    if (type(record_order) not in (tuple, list) or len(record_order) != jobs
            or any(type(key) is not str for key in record_order) or set(record_order) != set(keys)):
        raise ValueError("Record order must be a permutation of all canonical keys")
    by_key = {row["key"]: row for row in records}
    request = {"version": VERSION, "kind": "parent_retention", "refresh_rule": refresh_rule,
               "public_model": {"jobs": jobs, "candidate_count": 2,
                                "parent_capacity_records": 2, "child_capacity_records": 2},
               "public_metadata": {"jobs": [{"key": key, "refresh_priority": priorities[key]} for key in keys]},
               "visible_records": [dict(by_key[key]) for key in record_order],
               "public_context": _context(framing),
               "instructions": _instructions(refresh_rule, framing, guarantee, guidance),
               "response_schema": response_schema(jobs)}
    validate_request(request)
    return request


def validate_request(request):
    fields = {"version", "kind", "refresh_rule", "public_model", "public_metadata", "visible_records",
              "public_context", "instructions", "response_schema"}
    if type(request) is not dict or set(request) != fields:
        raise ValueError("Unexpected request fields")
    if request["version"] != VERSION or request["kind"] != "parent_retention":
        raise ValueError("Unknown public request contract")
    rule = request["refresh_rule"]
    if type(rule) is not str or rule not in RULES:
        raise ValueError("Unknown refresh rule")
    model = request["public_model"]
    if (type(model) is not dict or set(model) != _MODEL_FIELDS
            or any(type(value) is not int for value in model.values())):
        raise ValueError("Unexpected public model fields or types")
    keys = job_keys(model["jobs"])
    if any(model[field] != 2 for field in _MODEL_FIELDS - {"jobs"}):
        raise ValueError("Candidate count and both record capacities must equal two")
    metadata = request["public_metadata"]
    if (type(metadata) is not dict or set(metadata) != {"jobs"} or type(metadata["jobs"]) is not list
            or len(metadata["jobs"]) != len(keys)):
        raise ValueError("Unexpected public metadata")
    priorities = {}
    for key, row in zip(keys, metadata["jobs"]):
        if (type(row) is not dict or set(row) != {"key", "refresh_priority"}
                or type(row["key"]) is not str or row["key"] != key):
            raise ValueError("Metadata must list canonical job keys in order")
        priorities[key] = row["refresh_priority"]
    _priorities(priorities, keys)
    _records(request["visible_records"], keys)
    if not any(request["instructions"] == _instructions(rule, framing, guarantee, guidance)
               and request["public_context"] == _context(framing)
               for framing, guarantee, guidance in product(FRAMINGS, GUARANTEES, GUIDANCE)):
        raise ValueError("Unexpected instructions or mismatched public context")
    # Serialize for comparison to distinguish booleans from integers in schema
    # fields; ordinary Python dict equality would accept True in place of 1.
    if json.dumps(request["response_schema"], sort_keys=True) != json.dumps(response_schema(len(keys)), sort_keys=True):
        raise ValueError("Unexpected output schema")


def request_bytes(request):
    validate_request(request)
    return json.dumps(request, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=False, allow_nan=False).encode("utf-8")


def validate_response(response, request):
    validate_request(request)
    keys = job_keys(request["public_model"]["jobs"])
    if type(response) is not dict or set(response) != {"keys"} or type(response["keys"]) is not list:
        raise ValueError("Expected exactly one keys array")
    selected = response["keys"]
    if (len(selected) > 2 or any(type(key) is not str for key in selected)
            or len(set(selected)) != len(selected) or not set(selected) <= set(keys)):
        raise ValueError("Unknown, duplicate, or excess selected keys")
    return tuple(sorted(selected))
