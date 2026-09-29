"""Allowlisted request envelope for the observed-workflow development run."""
import json

VERSION = "workflow_observed_luna6_dev_v1"
MEMORY_SCHEMA = {"type": "object", "properties": {"memory": {"type": "string"}},
                 "required": ["memory"], "additionalProperties": False}


def request_bytes(request):
    if set(request) != {"version", "stage", "instruction", "observation", "response_schema"}:
        raise ValueError("Unexpected request field")
    if request["version"] != VERSION or request["stage"] not in {"parent", "child", "execute"}:
        raise ValueError("Unknown public request")
    raw = json.dumps(request, ensure_ascii=True, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()
    if len(raw) > 100000:
        raise ValueError("Public request exceeds cap")
    return raw
