"""Allowlisted source-only requests; evaluator data cannot enter this envelope."""
import json
from . import codec, study

VERSION = "source_only_scope_luna_v1"
SCHEMA = {"type": "object", "properties": {f: {"type": "array", "items": {"type": "string"}} for f in codec.FIELDS},
          "required": list(codec.FIELDS), "additionalProperties": False}
DSL = ("Return exactly value_paths, presence_paths, nonempty_paths arrays. Paths are dotted JSON object keys. "
       "value_paths preserves literal subtrees; $ preserves the entire input. presence_paths replaces a present key by true, "
       "and omits absent keys. nonempty_paths preserves nonempty dictionaries with the public _scope_nonempty marker "
       "when projection otherwise empties them. Any encountered nondictionary intermediate is preserved unchanged. "
       "Full-value retention overrides presence abstraction. Missing paths stay missing. No clipping or semantic fallback.")


def request(variant):
    if variant not in {"concise", "closure"}:
        raise ValueError("Unknown frozen prompt")
    instruction = "Infer a compact exact retention contract for the supplied public decision program on arbitrary JSON dictionaries. Preserve its output and unknown/error behavior. Use only the supplied program and projection language."
    if variant == "closure":
        instruction += " Check key membership and absence, malformed-container types, and empty/nonempty containers, including unknown keys. A positive-field list alone may not preserve those branches."
    return {"version": VERSION, "stage": "execute", "instruction": instruction,
            "observation": {"public_program": study.public_program(), "projection_language": DSL}, "response_schema": SCHEMA}


def request_bytes(value):
    if (not isinstance(value, dict) or set(value) != {"version", "stage", "instruction", "observation", "response_schema"}
            or value["version"] != VERSION or value["stage"] != "execute"
            or set(value["observation"]) != {"public_program", "projection_language"} or value["response_schema"] != SCHEMA):
        raise ValueError("Undeclared source-only request")
    raw = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True, allow_nan=False).encode()
    if len(raw) > 20000:
        raise ValueError("Public request exceeds frozen limit")
    return raw
