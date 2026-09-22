"""Generic schema/result projection and conservative ID/relationship checks.

No workflow-family names or evaluator field lists occur in this module.
"""
from __future__ import annotations

from collections import Counter
import json
import re
from time import perf_counter_ns

from .casebook import CHILD_CAP, PARENT_CAP, compact

OPAQUE = re.compile(r"^(?:[a-f0-9]{16}|[a-f0-9]{8}-[a-f0-9-]{27,}|(?:[a-z]{2,5}[-_])?[a-f0-9]{12,64}|sha256:[a-f0-9]{16,64})$", re.I)
NAME = re.compile(r"(?:^|_)(?:id|uuid|key|token|digest|hash|checksum|receipt|artifact|ref|reference|run|subject|scope|dataset|output|input)(?:$|_)", re.I)
OWNER = re.compile(r"(?:^|_)(?:id|token|run|slot)$", re.I)


def leaves(schema, prefix=""):
    if schema.get("type") == "object":
        for key, child in sorted(schema.get("properties", {}).items()):
            yield from leaves(child, prefix + "." + key if prefix else key)
    elif schema.get("type") in {"string", "boolean", "integer", "number"}:
        yield prefix, schema
    else:
        raise ValueError("Unsupported schema leaf or missing type")


def value_at(row, path):
    if path in row:
        return row[path]
    cursor = row
    for key in path.split("."):
        cursor = cursor[key]
    return cursor


def id_like(path, spec, value):
    if spec.get("type") != "string" or not isinstance(value, str):
        return False
    name = path.rsplit(".", 1)[-1]
    return (spec.get("format") in {"uuid", "uri", "uri-reference"} or
            bool(spec.get("pattern")) or bool(NAME.search(name)) or bool(OPAQUE.fullmatch(value)))


def selected(schema, records):
    if not records:
        raise ValueError("No source results")
    fields = []
    ids = []
    uncertain = []
    for path, spec in leaves(schema):
        values = [value_at(row, path) for row in records]
        if spec.get("type") == "string":
            if any(not isinstance(value, str) for value in values):
                raise ValueError("String schema/result mismatch")
            is_id = any(id_like(path, spec, value) for value in values)
            if is_id:
                fields.append(path)
                ids.append(path)
            elif "enum" in spec:
                fields.append(path)
            elif any(len(value.encode()) <= 64 for value in values):
                # A short unconstrained scalar could be a novel identifier.
                uncertain.append(path)
        else:
            fields.append(path)
    if uncertain:
        raise ValueError("Unknown coverage for short untyped strings: " + ",".join(uncertain))
    owners = [path for path in ids if "." not in path]
    preferred = [path for path in owners if OWNER.search(path)]
    if len(preferred) != 1:
        raise ValueError("No unique top-level owner identity")
    if not ids or not fields:
        raise ValueError("No identifier coverage")
    return fields, ids, preferred[0]


def encode(fields, records):
    return compact({"f": fields, "r": [[value_at(row, path) for path in fields] for row in records]})


def decode(memory):
    data = json.loads(memory)
    if not isinstance(data, dict) or set(data) != {"f", "r"}:
        raise ValueError("Memory is not a field/row table")
    fields, rows = data["f"], data["r"]
    if not isinstance(fields, list) or not all(isinstance(x, str) for x in fields) or len(fields) != len(set(fields)):
        raise ValueError("Invalid field list")
    if not isinstance(rows, list) or any(not isinstance(row, list) or len(row) != len(fields) for row in rows):
        raise ValueError("Invalid row list")
    return [dict(zip(fields, row, strict=True)) for row in rows]


def retained_schema(schema, memory):
    """Restrict public type evidence to paths present in bounded parent memory."""
    known = dict(leaves(schema))
    fields = json.loads(memory)["f"]
    if not isinstance(fields, list) or any(path not in known for path in fields):
        raise ValueError("Parent contains unsupported field")
    return {"type": "object", "properties": {path: known[path] for path in fields}}


def project(schema, records, *, cap=PARENT_CAP):
    start = perf_counter_ns()
    fields, ids, owner = selected(schema, records)
    memory = encode(fields, records)
    if len(memory.encode()) > cap:
        raise ValueError("Generic projection exceeds memory cap")
    return memory, {"cpu_ns": perf_counter_ns() - start, "source_bytes_read": len(compact(records).encode()),
                    "memory_bytes_written": len(memory.encode()), "fields": len(fields),
                    "identifier_fields": len(ids), "owner_path": owner}


def select(memory, candidates, *, cap=CHILD_CAP):
    start = perf_counter_ns()
    data = json.loads(memory)
    rows = decode(memory)
    chosen = []
    for candidate in candidates:
        matches = [row for row in rows if candidate in row.values()]
        if len(matches) != 1:
            raise ValueError("Candidate not uniquely retained")
        chosen.append(matches[0])
    result = encode(data["f"], chosen)
    if len(result.encode()) > cap:
        raise ValueError("Child projection exceeds memory cap")
    return result, {"cpu_ns": perf_counter_ns() - start, "source_bytes_read": len(memory.encode()),
                    "memory_bytes_written": len(result.encode())}


def _owned(records, fields, ids, owner):
    result = {}
    for row in records:
        key = value_at(row, owner)
        if not isinstance(key, str) or key in result:
            raise ValueError("Missing or duplicate owner")
        result[key] = {path: value_at(row, path) for path in ids}
    return result


def check(candidate, schema, source):
    """Certify exact detected IDs, then their owner/path/value association.

    Invalid or unstructured model memory receives an explicit failed verdict.
    Unannotated state is not covered. A deterministic projection passes the same
    interface. The check never repairs or reads deleted evidence by itself.
    """
    start = perf_counter_ns()
    fields, ids, owner = selected(schema, source)
    expected = _owned(source, fields, ids, owner)
    try:
        observed_rows = decode(candidate)
        observed = _owned(observed_rows, fields, ids, owner)
        exact_ids = Counter(value for row in expected.values() for value in row.values()) == Counter(
            value for row in observed.values() for value in row.values())
        relationships = expected == observed
        reason = "passed" if exact_ids and relationships else "identifier_or_relationship_loss"
    except (ValueError, KeyError, TypeError, json.JSONDecodeError):
        exact_ids = relationships = False
        reason = "unstructured_or_ambiguous_memory"
    return {"passed": exact_ids and relationships, "exact_ids": exact_ids,
            "relationships": relationships, "reason": reason,
            "source_bytes_read": len(compact(source).encode()),
            "candidate_bytes_read": len(candidate.encode()),
            "required_id_fields": len(ids), "cpu_ns": perf_counter_ns() - start}
