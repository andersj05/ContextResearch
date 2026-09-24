"""Check that a certified parent can be selected and decoded after the next boundary.

The v1 exact-ID check did not inspect extra table columns. It could therefore
accept a model proposal containing component workflow_key columns that the
joined-schema child decoder rejected. This module adds a *format and handoff*
certificate. It does not certify state semantics or terminal decisions.
"""
from __future__ import annotations

from itertools import combinations
import json
from time import perf_counter_ns

from experiments.dependency_memory.cross_record import memory as frozen
from experiments.dependency_memory.schema_transfer import memory as table


def _parse(memory):
    data = json.loads(memory)
    rows = table.decode(memory)
    return data["f"], rows


def _schema_values_valid(fields, rows, schema):
    known = dict(table.leaves(schema))
    for path in fields:
        if path not in known:
            return False, "unsupported_path"
        spec = known[path]
        kind = spec["type"]
        for row in rows:
            value = row[path]
            valid_type = (isinstance(value, str) if kind == "string" else
                          isinstance(value, bool) if kind == "boolean" else
                          type(value) is int if kind == "integer" else
                          type(value) in (int, float))
            if not valid_type or ("enum" in spec and value not in spec["enum"]):
                return False, "schema_type_or_enum"
    return True, "passed"


def select_by_owner(parent, owner_path, candidates, *, cap=2600):
    """Select exact root identities, never a match in an unrelated field."""
    fields, rows = _parse(parent)
    if owner_path not in fields:
        raise ValueError("Owner field absent")
    if not isinstance(candidates, (list, tuple)) or len(candidates) != 2 or any(
            not isinstance(value, str) for value in candidates) or len(set(candidates)) != 2:
        raise ValueError("Expected two distinct string candidate IDs")
    selected = []
    for candidate in candidates:
        matching = [row for row in rows if row[owner_path] == candidate]
        if len(matching) != 1:
            raise ValueError("Candidate owner is missing or ambiguous")
        selected.append(matching[0])
    child = table.encode(fields, selected)
    if len(child.encode("utf-8")) > cap:
        raise ValueError("Child memory exceeds cap")
    return child


def certify_parent(candidate, tool_schemas, tool_results, *, parent_cap=7000,
                   child_cap=2600):
    """Require v1 ID coverage plus paths and capacity usable by the child.

    The two-candidate count is public at the parent boundary. Every possible
    pair of source owners must fit the later child cap, before their identities
    are disclosed. No future event or private grader is inspected here.
    """
    start = perf_counter_ns()
    verdict = {"passed": False, "reason": "unknown", "owner_path": None,
               "max_child_bytes": None, "identifier_check": None,
               "parent_bytes": len(candidate.encode("utf-8")), "cpu_ns": 0}
    try:
        schema, source_rows = frozen.join(tool_schemas, tool_results)
        _, _, owner = table.selected(schema, source_rows)
        verdict["owner_path"] = owner
        fields, rows = _parse(candidate)
        valid_shape, shape_reason = _schema_values_valid(fields, rows, schema)
        if verdict["parent_bytes"] > parent_cap:
            verdict["reason"] = "parent_capacity"
        elif not valid_shape:
            verdict["reason"] = ("unsupported_parent_path" if shape_reason == "unsupported_path"
                                 else shape_reason)
        else:
            id_check = table.check(candidate, schema, source_rows)
            verdict["identifier_check"] = id_check["passed"]
            if not id_check["passed"]:
                verdict["reason"] = "identifier_or_relationship_loss"
            else:
                owners = [row[owner] for row in rows]
                if len(owners) < 2:
                    verdict["reason"] = "too_few_owners"
                else:
                    largest = 0
                    for pair in combinations(owners, 2):
                        # Use an unbounded selector to measure the actual child.
                        largest = max(largest, len(select_by_owner(
                            candidate, owner, pair, cap=2**63).encode("utf-8")))
                    verdict["max_child_bytes"] = largest
                    verdict["reason"] = "child_capacity" if largest > child_cap else "passed"
                    verdict["passed"] = largest <= child_cap
    except (ValueError, KeyError, TypeError, json.JSONDecodeError):
        verdict["reason"] = "unstructured_or_ambiguous_parent"
    verdict["cpu_ns"] = perf_counter_ns() - start
    return verdict


def certify_child(candidate, parent, candidates, owner_path, tool_schemas, *,
                  child_cap=2600):
    """Check a proposed child against only the certified parent and public schema."""
    start = perf_counter_ns()
    verdict = {"passed": False, "reason": "unknown", "cpu_ns": 0}
    try:
        expected = select_by_owner(parent, owner_path, candidates, cap=child_cap)
        parent_schema = table.retained_schema(frozen.joined_schema(tool_schemas), parent)
        fields, rows = _parse(candidate)
        valid_shape, shape_reason = _schema_values_valid(fields, rows, parent_schema)
        if len(candidate.encode("utf-8")) > child_cap:
            verdict["reason"] = "child_capacity"
        elif not valid_shape:
            verdict["reason"] = ("unsupported_child_path" if shape_reason == "unsupported_path"
                                 else shape_reason)
        else:
            id_check = table.check(candidate, parent_schema, table.decode(expected))
            verdict["reason"] = "passed" if id_check["passed"] else "identifier_or_relationship_loss"
            verdict["passed"] = id_check["passed"]
    except (ValueError, KeyError, TypeError, json.JSONDecodeError):
        verdict["reason"] = "unstructured_or_ambiguous_child"
    verdict["cpu_ns"] = perf_counter_ns() - start
    return verdict


def admit_or_project(proposal, tool_schemas, tool_results, *, parent_cap=7000,
                     child_cap=2600):
    """Fall back before deleting source evidence if the proposal is incompatible."""
    proposal_check = certify_parent(proposal, tool_schemas, tool_results,
                                    parent_cap=parent_cap, child_cap=child_cap)
    if proposal_check["passed"]:
        return proposal, proposal_check, False
    fallback, _ = frozen.project(tool_schemas, tool_results, cap=parent_cap)
    fallback_check = certify_parent(fallback, tool_schemas, tool_results,
                                    parent_cap=parent_cap, child_cap=child_cap)
    if not fallback_check["passed"]:
        raise ValueError("No decoder-compatible parent fallback: " + fallback_check["reason"])
    return fallback, fallback_check, True
