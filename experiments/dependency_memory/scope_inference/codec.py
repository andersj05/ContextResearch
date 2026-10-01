"""Pure projection DSL: no filesystem, model, evaluator, or generated-code execution."""
import ast
from copy import deepcopy
import json
import re

MARKER = "_scope_nonempty"
FIELDS = ("value_paths", "presence_paths", "nonempty_paths")
PARENT_CAP, CHILD_CAP = 4096, 1536


def wire(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False).encode("utf-8")


def validate(contract):
    if not isinstance(contract, dict) or set(contract) != set(FIELDS):
        raise ValueError("Unknown projection contract")
    for field in FIELDS:
        paths = contract[field]
        if (not isinstance(paths, list) or len(paths) > 40
                or any(not isinstance(p, str) or len(p) > 160 or MARKER in p.split(".")
                       or not (p == "$" and field == "value_paths" or re.fullmatch(r"[A-Za-z_][A-Za-z_0-9]*(\.[A-Za-z_][A-Za-z_0-9]*)*", p)) for p in paths)):
            raise ValueError("Malformed projection path")
        if len(paths) != len(set(paths)):
            raise ValueError("Duplicate projection path")
    return deepcopy(contract)


def project(value, contract):
    contract = validate(contract)
    values, presence, nonempty = (set(contract[f]) for f in FIELDS)
    if "$" in values:
        return deepcopy(value)

    def visit(node, prefix):
        if prefix in values:
            return deepcopy(node)
        if prefix in presence and not any(p.startswith(prefix + ".") for p in values | presence | nonempty):
            return True
        if not isinstance(node, dict):
            return deepcopy(node)
        result = {}
        for key, child in node.items():
            path = prefix + "." + key if prefix else key
            if any(p == path or p.startswith(path + ".") for p in values | presence | nonempty):
                result[key] = visit(child, path)
        if prefix in nonempty and node and not result:
            result[MARKER] = True
        return result
    return visit(value, "")


def literal_roots(public_program):
    """Conservative source baseline: full root subtrees referenced by attempt.get."""
    keys = set()
    for node in ast.walk(ast.parse(public_program)):
        if (isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) and node.func.attr == "get"
                and isinstance(node.func.value, ast.Name) and node.func.value.id == "attempt"
                and node.args and isinstance(node.args[0], ast.Constant) and isinstance(node.args[0].value, str)):
            keys.add(node.args[0].value)
    return {"value_paths": sorted(keys), "presence_paths": [], "nonempty_paths": []}


def admit(rows, cap):
    encoded = wire(rows).decode("utf-8")
    size = len(encoded.encode("utf-8"))
    return (encoded if size <= cap else ""), {"proposal_bytes": size, "infeasible": size > cap}
