"""Allowlisted public requests and offline clients for the development pilot.

This module has no fixture, evaluator, file, network, or provider-state input.
The Python caller remains trusted: process isolation belongs to the adapter.
Only direct_artifact_tags is implemented; held-out renderers remain gated.
"""

from __future__ import annotations

import json

from artifact_workflow import Config, Receipt, visible_records
from recovery_frontier import reference_plan


VERSION = "pilot_public_request_v1"
RENDER_MODES = ("explicit_labels", "inferred_dependencies")
CONFIG_FIELDS = (
    "jobs", "candidate_count", "first_capacity", "second_capacity",
    "probe_available", "probe_cost", "revise", "delay", "cost_budget",
    "call_limit", "recovery_available", "recovery_cost",
)
PROPERTIES = ("amber", "cobalt", "ivory", "jade", "plum", "sienna")
COMMON_INSTRUCTIONS = (
    "Manage exact artifact receipt records through two irreversible memory boundaries. "
    "All subsets of candidate_count distinct jobs are equally likely; the final required job "
    "is uniform within that subset and is disclosed only after the second boundary. "
    "Early inspection costs probe_cost synthetic units and reveals the manifest before the "
    "first boundary. Otherwise the same manifest appears just after that boundary. "
    "If revise is true, the build then supplies revision two of the lexicographically first "
    "candidate job, even if its old receipt was discarded. Other jobs are not refreshed. "
    "The second boundary follows the build. After delay mandatory steps, the final requirement "
    "is disclosed. When recovery_available is true, a scripted controller reliably recovers "
    "a missing required latest receipt for recovery_cost synthetic units, then submits it. "
    "Each other mandatory tool action costs one synthetic unit; there are 7 + delay such "
    "actions. Record slots, synthetic units, serialized bytes, and model tokens are different "
    "quantities. Static public job metadata remains available at every request. Past "
    "observations, discarded receipts, explanations, and previous model responses do not. "
)
INSPECTION_INSTRUCTIONS = (
    "Choose whether to buy early inspection to minimize expected total synthetic completion "
    "cost. Return only the JSON object {\"inspect\": true} or {\"inspect\": false}."
)
CALIBRATION_INSTRUCTIONS = (
    "For this decision only, subsequent record selection is guaranteed to be optimal under "
    "the declared capacities and public revision rule, with reliable recovery of any miss. "
)
RETENTION_INSTRUCTIONS = (
    "Select at most capacity_records distinct keys from visible_records. The host retains "
    "exactly those current records in canonical key order; all other observations and memory "
    "are deleted at this boundary. Preserve evidence useful for the eventual completion, "
    "accounting for future refresh and recovery. Return only {\"keys\": [selected keys]}; "
    "do not include explanations, receipt values, extra fields, or invented keys."
)


def public_metadata(config: Config) -> dict:
    """Static all-job properties; accepts no route, target, payload, or seed."""
    if not 1 <= config.jobs <= len(PROPERTIES):
        raise ValueError("Development renderer supports one to six jobs")
    return {"jobs": [{"key": f"job-{i}", "artifact_property": PROPERTIES[i]}
                     for i in range(config.jobs)]}


def _config_dict(config):
    values = {name: getattr(config, name) for name in CONFIG_FIELDS}
    Config(**values)
    return values


def _metadata(config, metadata):
    expected = public_metadata(config)
    if metadata is not None and metadata != expected:
        raise ValueError("Metadata must be the static all-job development mapping")
    return expected


def render_manifest(candidates, metadata, render_mode):
    """Render just the paid/mandatory visible clue, never the final target."""
    if render_mode not in RENDER_MODES:
        raise ValueError("Unknown render mode")
    keys = tuple(row["key"] for row in metadata["jobs"])
    if (not candidates or tuple(candidates) != tuple(sorted(set(candidates)))
            or not set(candidates) <= set(keys)):
        raise ValueError("Manifest must contain distinct sorted known keys")
    if render_mode == "explicit_labels":
        return {"kind": "manifest", "candidate_keys": list(candidates)}
    properties = {row["key"]: row["artifact_property"] for row in metadata["jobs"]}
    return {"kind": "manifest",
            "task": "The eventual handoff will require a receipt for one of the requested artifact properties.",
            "requested_properties": [properties[key] for key in candidates]}


def infer_candidates(manifest, metadata):
    """Independent reverse mapping used by the scripted public-input client."""
    if "candidate_keys" in manifest:
        return tuple(sorted(manifest["candidate_keys"]))
    by_property = {row["artifact_property"]: row["key"] for row in metadata["jobs"]}
    return tuple(sorted(by_property[prop] for prop in manifest["requested_properties"]))


def _record_dict(receipt, config):
    if (receipt.key not in {f"job-{i}" for i in range(config.jobs)}
            or type(receipt.revision) is not int or receipt.revision < 1
            or type(receipt.token) is not str or not receipt.token):
        raise ValueError("Invalid visible receipt")
    return {"key": receipt.key, "revision": receipt.revision, "token": receipt.token}


def _public_observations(config, metadata, window, render_mode):
    result = []
    for event in window:
        if event.kind == "manifest":
            if len(event.candidates) != config.candidate_count:
                raise ValueError("Wrong manifest size")
            result.append(render_manifest(event.candidates, metadata, render_mode))
        elif event.kind in ("receipts", "build"):
            # Current values occur only once in visible_records. These events
            # describe timing without reintroducing superseded receipt values.
            records = [_record_dict(r, config) for r in event.receipts]
            result.append({"kind": event.kind,
                           "observed_keys": sorted(r["key"] for r in records)})
        elif event.kind == "checkpoint" and event.checkpoint in (1, 2):
            result.append({"kind": "checkpoint", "boundary": event.checkpoint})
        else:
            raise ValueError("Observation is not permitted before a manager boundary")
    return result


def _response_schema(kind, records=(), capacity=0):
    if kind == "inspection":
        field, spec = "inspect", {"type": "boolean"}
    else:
        field, spec = "keys", {"type": "array", "maxItems": min(capacity, len(records)),
                               "uniqueItems": True,
                               "items": ({"type": "string", "enum": [r["key"] for r in records]}
                                         if records else {"type": "string"})}
    return {"type": "object", "properties": {field: spec}, "required": [field],
            "additionalProperties": False}


def _base(config, metadata, memory, window, render_mode):
    if render_mode not in RENDER_MODES:
        raise ValueError("Unknown render mode")
    metadata = _metadata(config, metadata)
    records = [_record_dict(r, config) for r in visible_records(memory, window)]
    records.sort(key=lambda r: r["key"])
    return {"version": VERSION, "config": _config_dict(config),
            "public_metadata": metadata, "render_mode": render_mode,
            "visible_records": records,
            "observations": _public_observations(config, metadata, window, render_mode)}


def inspection_request(config, metadata=None, memory=(), window=(), *,
                       calibration=False, render_mode="explicit_labels"):
    if type(calibration) is not bool:
        raise ValueError("Calibration flag must be Boolean")
    if calibration and (memory or window):
        raise ValueError("Calibration must not receive realized observations")
    if memory or any(event.kind != "receipts" for event in window):
        raise ValueError("Inspection decision must precede the first manifest/boundary")
    request = _base(config, metadata, memory, window, render_mode)
    request.update(kind="inspection", calibration=calibration,
                   instructions=COMMON_INSTRUCTIONS + (CALIBRATION_INSTRUCTIONS if calibration else "")
                   + INSPECTION_INSTRUCTIONS, response_schema=_response_schema("inspection"))
    return request


def retention_request(config, metadata, memory, window, boundary, render_mode):
    if type(boundary) is not int or boundary not in (1, 2):
        raise ValueError("Boundary must be one or two")
    if not window or window[-1].kind != "checkpoint" or window[-1].checkpoint != boundary:
        raise ValueError("Retention requires the declared terminal checkpoint")
    if any(event.kind == "checkpoint" for event in window[:-1]):
        raise ValueError("Earlier checkpoint/window must have been deleted")
    if boundary == 2 and any(event.kind == "receipts" for event in window):
        raise ValueError("Initial receipt observations must have been deleted")
    capacity = config.first_capacity if boundary == 1 else config.second_capacity
    request = _base(config, metadata, memory, window, render_mode)
    request.update(kind="retention", boundary=boundary, capacity_records=capacity,
                   instructions=COMMON_INSTRUCTIONS + RETENTION_INSTRUCTIONS,
                   response_schema=_response_schema("retention", request["visible_records"], capacity))
    return request


def validate_request(request):
    """Reject added channels before bytes enter a fake or provider adapter."""
    if type(request) is not dict:
        raise ValueError("Request must be an object")
    kind = request.get("kind")
    shared = {"version", "kind", "instructions", "config", "public_metadata", "render_mode",
              "visible_records", "observations", "response_schema"}
    extra = {"calibration"} if kind == "inspection" else {"boundary", "capacity_records"}
    if kind not in ("inspection", "retention") or set(request) != shared | extra:
        raise ValueError("Request contains missing or undeclared fields")
    if request["version"] != VERSION or request["render_mode"] not in RENDER_MODES:
        raise ValueError("Unknown request version/rendering")
    if type(request["config"]) is not dict or set(request["config"]) != set(CONFIG_FIELDS):
        raise ValueError("Configuration contains undeclared fields")
    config = Config(**request["config"])
    metadata = _metadata(config, request["public_metadata"])
    records = request["visible_records"]
    if type(records) is not list:
        raise ValueError("Visible records must be an array")
    for record in records:
        if type(record) is not dict or set(record) != {"key", "revision", "token"}:
            raise ValueError("Record contains undeclared fields")
        _record_dict(Receipt(**record), config)
    keys = [r["key"] for r in records]
    if keys != sorted(set(keys)):
        raise ValueError("Visible records must have unique canonical keys")
    if type(request["observations"]) is not list:
        raise ValueError("Observations must be an array")
    observations = request["observations"]
    known_keys = {row["key"] for row in metadata["jobs"]}
    for event in observations:
        if type(event) is not dict:
            raise ValueError("Observation must be an object")
        event_kind = event.get("kind")
        if event_kind == "manifest":
            try:
                candidates = infer_candidates(event, metadata)
                expected = render_manifest(candidates, metadata, request["render_mode"])
            except (KeyError, TypeError) as error:
                raise ValueError("Malformed manifest") from error
            if event != expected or len(candidates) != config.candidate_count:
                raise ValueError("Manifest contains undeclared or invalid fields")
        elif event_kind in ("receipts", "build"):
            event_keys = event.get("observed_keys")
            if (set(event) != {"kind", "observed_keys"} or type(event_keys) is not list
                    or any(type(k) is not str for k in event_keys)
                    or event_keys != sorted(set(event_keys)) or not set(event_keys) <= known_keys):
                raise ValueError("Invalid receipt observation")
        elif event_kind == "checkpoint":
            if (set(event) != {"kind", "boundary"} or type(event["boundary"]) is not int
                    or event["boundary"] not in (1, 2)):
                raise ValueError("Invalid checkpoint")
        else:
            raise ValueError("Undeclared observation kind")
    if kind == "inspection":
        calibration = request["calibration"]
        if type(calibration) is not bool or (calibration and (records or observations)):
            raise ValueError("Invalid calibration view")
        if any(event["kind"] != "receipts" for event in observations):
            raise ValueError("Inspection already has a manifest or checkpoint")
        instructions = COMMON_INSTRUCTIONS + (CALIBRATION_INSTRUCTIONS if calibration else "") + INSPECTION_INSTRUCTIONS
        schema = _response_schema(kind)
    else:
        boundary = request["boundary"]
        if type(boundary) is not int or boundary not in (1, 2):
            raise ValueError("Invalid boundary")
        capacity = config.first_capacity if boundary == 1 else config.second_capacity
        if type(request["capacity_records"]) is not int or request["capacity_records"] != capacity:
            raise ValueError("Capacity disagrees with public configuration")
        if not observations or observations[-1] != {"kind": "checkpoint", "boundary": boundary}:
            raise ValueError("Missing terminal checkpoint")
        if any(e["kind"] == "checkpoint" for e in observations[:-1]):
            raise ValueError("Undeleted earlier observation window")
        if boundary == 2 and any(e["kind"] == "receipts" for e in observations):
            raise ValueError("Initial receipts reintroduced after first boundary")
        instructions = COMMON_INSTRUCTIONS + RETENTION_INSTRUCTIONS
        schema = _response_schema(kind, records, capacity)
    if request["instructions"] != instructions or request["response_schema"] != schema:
        raise ValueError("Instructions/schema contain undeclared content")


def request_bytes(request):
    validate_request(request)
    return json.dumps(request, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=False, allow_nan=False).encode("utf-8")


def validate_inspection_response(response):
    if type(response) is not dict or set(response) != {"inspect"} or type(response["inspect"]) is not bool:
        raise ValueError("Expected exactly one Boolean inspect field")
    return response["inspect"]


def validate_retention_response(response, request):
    validate_request(request)
    if request["kind"] != "retention":
        raise ValueError("Retention response requires a retention request")
    if type(response) is not dict or set(response) != {"keys"} or type(response["keys"]) is not list:
        raise ValueError("Expected exactly one keys array")
    keys = response["keys"]
    if any(type(key) is not str for key in keys):
        raise ValueError("All selected keys must be strings")
    if len(keys) > request["capacity_records"] or len(set(keys)) != len(keys):
        raise ValueError("Duplicate keys or capacity exceeded")
    by_key = {row["key"]: row for row in request["visible_records"]}
    if not set(keys) <= set(by_key):
        raise ValueError("Selected key is not currently visible")
    return tuple(Receipt(**by_key[key]) for key in sorted(keys))


class FakeClient:
    """Stateless controls whose sole input is the same validated public request."""

    def __init__(self, mode="optimal"):
        if mode not in ("optimal", "forget_all", "invalid"):
            raise ValueError("Unknown fake-client mode")
        self.mode = mode

    def complete(self, request):
        request = json.loads(request_bytes(request))
        if self.mode == "invalid":
            return {"inspect": "yes"} if request["kind"] == "inspection" else {"keys": ["invented-job"]}
        if self.mode == "forget_all":
            return {"inspect": False} if request["kind"] == "inspection" else {"keys": []}
        config = Config(**request["config"])
        ref = reference_plan(config.jobs, config.candidate_count, config.first_capacity,
                             config.second_capacity, config.revise)
        if request["kind"] == "inspection":
            skip = (1 - ref.hit_without_inspection) * config.recovery_cost
            inspect = config.probe_cost + (1 - ref.hit_with_inspection) * config.recovery_cost
            return {"inspect": bool(config.probe_available and inspect < skip)}
        candidates = None
        for observation in request["observations"]:
            if observation["kind"] == "manifest":
                candidates = infer_candidates(observation, request["public_metadata"])
        keys = [r["key"] for r in request["visible_records"]]
        if candidates is not None:
            keys = [key for key in keys if key in candidates]
            if request["boundary"] == 1 and config.revise:
                keys = [key for key in keys if key != candidates[0]]
        elif request["boundary"] == 1:
            keys = [key for key in keys if key in ref.first_keys]
        capacity = request["capacity_records"]
        return {"keys": sorted(keys[-capacity:] if capacity else [])}
