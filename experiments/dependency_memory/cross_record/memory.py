"""Generic joins and narrow exact-ID/relationship certificates for tool results.

The module has no workflow-family names or evaluator field lists. A join is
certified only if each workflow has one root and one result of every declared
component tool. This does not certify that a status is semantically sufficient.
"""
from __future__ import annotations

from collections import defaultdict
from time import perf_counter_ns

from experiments.dependency_memory.schema_transfer import memory as base
from .casebook import CHILD_CAP, PARENT_CAP, compact


def joined_schema(tool_schemas):
    if "root" not in tool_schemas or len(tool_schemas) < 2:
        raise ValueError("Expected a root and component tools")
    root = tool_schemas["root"]
    props = {key: spec for key, spec in root["properties"].items() if key != "operator_notes"}
    if "workflow_key" not in props:
        raise ValueError("Missing join key")
    for name, schema in sorted(tool_schemas.items()):
        if name == "root":
            continue
        required = schema["properties"]
        if "workflow_key" not in required or "record_id" not in required:
            raise ValueError("Missing component join or identity")
        props[name] = {"type": "object", "properties": {
            key: spec for key, spec in required.items() if key != "workflow_key"}}
    return {"type": "object", "properties": props}


def join(tool_schemas, tool_results):
    """Reject missing/duplicate tools and join by exact workflow_key bytes."""
    names = set(tool_schemas)
    groups = defaultdict(dict)
    for item in tool_results:
        if not isinstance(item, dict) or set(item) != {"tool", "data"}:
            raise ValueError("Malformed tool result")
        name, data = item["tool"], item["data"]
        if name not in names or not isinstance(data, dict):
            raise ValueError("Unknown tool result")
        key = data.get("workflow_key")
        if not isinstance(key, str) or name in groups[key]:
            raise ValueError("Missing key or duplicate component")
        groups[key][name] = data
    rows = []
    for key, group in sorted(groups.items()):
        if set(group) != names:
            raise ValueError("Incomplete joined workflow")
        root = group["root"]
        row = {field: value for field, value in root.items() if field != "operator_notes"}
        for name in sorted(names - {"root"}):
            row[name] = {field: value for field, value in group[name].items()
                         if field != "workflow_key"}
        rows.append(row)
    schema = joined_schema(tool_schemas)
    # Enforce declared leaves, catching silently missing component values.
    for row in rows:
        for path, _ in base.leaves(schema):
            base.value_at(row, path)
    return schema, rows


def project(tool_schemas, tool_results, *, cap=PARENT_CAP):
    start = perf_counter_ns()
    schema, rows = join(tool_schemas, tool_results)
    fields, identifiers, owner = base.selected(schema, rows)
    candidate = base.encode(fields, rows)
    if len(candidate.encode()) > cap:
        raise ValueError("Generic cross-record projection exceeds cap")
    return candidate, {"cpu_ns": perf_counter_ns() - start,
                       "source_bytes_read": len(compact(tool_schemas).encode()) + len(compact(tool_results).encode()),
                       "memory_bytes_written": len(candidate.encode()),
                       "fields": len(fields), "identifier_fields": len(identifiers), "owner_path": owner}


def check(candidate, tool_schemas, tool_results):
    start = perf_counter_ns()
    schema, rows = join(tool_schemas, tool_results)
    result = base.check(candidate, schema, rows)
    result["cpu_ns"] += perf_counter_ns() - start - result["cpu_ns"]
    result["source_bytes_read"] += len(compact(tool_schemas).encode()) + len(compact(tool_results).encode())
    return result


def select(parent, candidates, *, cap=CHILD_CAP):
    return base.select(parent, candidates, cap=cap)


def check_child(candidate, parent, candidates, tool_schemas):
    start = perf_counter_ns()
    expected, details = select(parent, candidates)
    joined = joined_schema(tool_schemas)
    restricted = base.retained_schema(joined, parent)
    result = base.check(candidate, restricted, base.decode(expected))
    result["cpu_ns"] += perf_counter_ns() - start - result["cpu_ns"]
    result["source_bytes_read"] += len(parent.encode()) + len(compact(candidates).encode()) + len(compact(tool_schemas).encode())
    return result, expected, details
