"""Closed public-request envelope. No seeds, evaluator truth, or session state."""
import json

VERSION = "luna6_delayed_revision_v1"
MEMORY_SCHEMA = {"type": "object", "properties": {"memory": {"type": "string"}}, "required": ["memory"], "additionalProperties": False}


def request_bytes(request):
    if set(request) != {"version", "stage", "instruction", "observation", "response_schema"}:
        raise ValueError("Unexpected request field")
    if request["version"] != VERSION or request["stage"] not in {"smoke", "parent", "child", "execute"}:
        raise ValueError("Unknown public request")
    raw = json.dumps(request, ensure_ascii=True, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()
    if len(raw) > 16000:
        raise ValueError("Public request exceeds cap")
    return raw


def smoke_request():
    return {"version": VERSION, "stage": "smoke", "instruction": 'Return {"memory":"ready"}.', "observation": {}, "response_schema": MEMORY_SCHEMA}
