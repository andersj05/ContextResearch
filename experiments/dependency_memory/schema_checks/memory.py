"""Generic schema-derived projection and two narrow, fail-closed checks.

The extractor contains no workflow-family identifiers or field names. Its input
contract requires JSON-schema-like object properties with opaque-ID, reference,
and ephemeral annotations. It retains other scalar fields without certifying
their semantics. The checker certifies only exact annotated IDs and owned refs.
"""
from __future__ import annotations

import json
from time import process_time_ns

from .cases import CHILD_CAP, PARENT_CAP, compact


def leaf_paths(schema, prefix=""):
    if schema.get("type") == "object":
        for name, child in sorted(schema.get("properties", {}).items()):
            yield from leaf_paths(child, prefix + "." + name if prefix else name)
    elif not schema.get("x-ephemeral", False):
        if schema.get("type") not in {"string", "boolean", "integer", "number"}:
            raise ValueError("Unsupported retained schema leaf")
        yield prefix, schema


def value_at(record, path):
    if path in record:
        return record[path]
    cursor = record
    for key in path.split("."):
        cursor = cursor[key]
    return cursor


def annotated(schema):
    paths = list(leaf_paths(schema))
    identities = [path for path, spec in paths if spec.get("format") == "opaque-id"]
    references = [path for path, spec in paths if spec.get("x-reference") is True]
    owners = [path for path in identities if "." not in path]
    if not identities or not references or not owners:
        raise ValueError("Unknown ID/reference coverage in schema")
    return paths, identities, references, owners[0]


def encode(paths, records):
    fields = [name for name, _ in paths]
    return compact({"fields": fields, "rows": [[value_at(record, path) for path in fields] for record in records]})


def decode(memory):
    data = json.loads(memory)
    if set(data) != {"fields", "rows"} or len(data["fields"]) != len(set(data["fields"])):
        raise ValueError("Invalid memory envelope")
    if any(len(row) != len(data["fields"]) for row in data["rows"]):
        raise ValueError("Invalid memory row")
    return [dict(zip(data["fields"], row, strict=True)) for row in data["rows"]]


def project(schema, records, *, cap=PARENT_CAP):
    paths, _, _, _ = annotated(schema)
    memory = encode(paths, records)
    if len(memory.encode()) > cap:
        raise ValueError("Schema-derived projection exceeds cap")
    return memory


def _signature(schema, records):
    _, identities, references, owner_path = annotated(schema)
    result = {}
    for record in records:
        owner = record[owner_path]
        if not isinstance(owner, str) or owner in result:
            raise ValueError("Missing or duplicate owner identity")
        result[owner] = {
            "ids": {path: record[path] for path in identities},
            "refs": {path: record[path] for path in references},
        }
    return result


def check(memory, schema, records):
    """Check owned ID and reference tuples, including field roles and row owner."""
    start = process_time_ns()
    decoded = decode(memory)
    expected = _signature(schema, [{path: value_at(row, path) for path, _ in leaf_paths(schema)} for row in records])
    observed = _signature(schema, decoded)
    missing_id = sum(1 for owner, fields in expected.items() for path, value in fields["ids"].items()
                     if observed.get(owner, {}).get("ids", {}).get(path) != value)
    missing_ref = sum(1 for owner, fields in expected.items() for path, value in fields["refs"].items()
                      if observed.get(owner, {}).get("refs", {}).get(path) != value)
    exact = expected == observed
    return {"passed": exact, "identity_errors": missing_id, "relation_errors": missing_ref,
            "source_bytes_read": len(compact(records).encode()),
            "memory_bytes_read": len(memory.encode()), "cpu_ns": process_time_ns() - start}


def select(memory, candidates, *, cap=CHILD_CAP):
    data = json.loads(memory)
    fields = data["fields"]
    rows = []
    for candidate in candidates:
        matches = [row for row in data["rows"] if candidate in row]
        if len(matches) != 1:
            raise ValueError("Candidate not uniquely retained")
        rows.append(matches[0])
    result = compact({"fields": fields, "rows": rows})
    if len(result.encode()) > cap:
        raise ValueError("Selected projection exceeds cap")
    return result


# A deliberately authored ideal control: these choices are per-workflow and
# exclude all fields not required by the frozen terminal grader.
DIRECT_PATHS = {
    "retry": ("request_key", "attempt_key", "dispatch_state", "result_state", "can_retry"),
    "ci_handoff": ("service_key", "current_build", "approval.covers_build",
                   "check.covers_build", "check.verdict"),
    "data_job": ("pipeline_key", "extract.output_key", "extract.state",
                 "transform.input_key", "transform.output_key", "transform.state",
                 "load.input_key", "load.output_key", "load.state",
                 "publish_approval.covers_output"),
}


def direct(family, records, *, cap=PARENT_CAP):
    paths = [(name, {}) for name in DIRECT_PATHS[family]]
    memory = encode(paths, records)
    if len(memory.encode()) > cap:
        raise ValueError("Direct memory exceeds cap")
    return memory
