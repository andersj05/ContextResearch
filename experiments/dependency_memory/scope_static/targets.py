"""Evaluator/source adapters for inspected repository programs; no model client."""
import ast
from decimal import Decimal, InvalidOperation
import hashlib
from pathlib import Path
from typing import Any

from experiments.dependency_memory.scope_inference import study
from experiments.dependency_memory.workflow_replay import evidence

ROOT = Path(__file__).resolve().parents[3]


class InvalidUsage(ValueError):
    pass


def functions(path, names):
    raw = (ROOT / path).read_bytes()
    tree = ast.parse(raw)
    nodes = [n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name in names]
    if {n.name for n in nodes} != set(names):
        raise ValueError("Missing selected repository functions")
    return raw, tree, nodes


def compile_functions(nodes, namespace):
    # Only trusted, inspected repository functions are executed by the grader.
    # Source analysis itself never compiles or executes its input.
    exec(compile(ast.Module(body=nodes, type_ignores=[]), "inspected_scope_target", "exec"), namespace)
    return namespace


def programs():
    dispatch = {"name": "dispatch", "entry": "classify_attempt", "parameter": "attempt",
                "source": study.public_program(), "original": evidence.historical_classifier(),
                "source_path": "scripts/prepare_transfer_continuation.py", "evidence_class": "inspected historical program"}
    path = "experiments/dependency_memory/luna_budget.py"
    raw, tree, nodes = functions(path, ("_tokens", "_credit_fields", "usage_estimates"))
    names = {"LONG_CONTEXT_THRESHOLD", "MAX_OUTPUT_TOKENS", "MILLION", "CONSERVATIVE_INPUT_RATE",
             "INPUT_RATE", "CACHED_INPUT_RATE", "OUTPUT_RATE"}
    constants, namespace = [], {"Decimal": Decimal, "InvalidUsage": InvalidUsage, "Any": Any}
    for n in tree.body:
        if isinstance(n, ast.Assign) and len(n.targets) == 1 and isinstance(n.targets[0], ast.Name) and n.targets[0].id in names:
            key = n.targets[0].id
            constants.append(ast.unparse(n))
            v = n.value
            namespace[key] = (Decimal(ast.literal_eval(v.args[0])) if isinstance(v, ast.Call)
                              and isinstance(v.func, ast.Name) and v.func.id == "Decimal" else ast.literal_eval(v))
    if not names <= namespace.keys():
        raise ValueError("Missing pinned arithmetic constants")
    source = ("from decimal import Decimal\nfrom typing import Any\nclass InvalidUsage(ValueError):\n    pass\n"
              + "\n".join(constants) + "\n\n" + "\n\n".join(ast.unparse(n) for n in nodes))
    namespace = compile_functions(nodes, namespace)
    tokens = {"name": "tokens", "entry": "usage_estimates", "parameter": "usage", "source": source,
              "original": namespace["usage_estimates"], "source_path": path,
              "source_file_sha256": hashlib.sha256(raw).hexdigest(),
              "evidence_class": "inspected repository arithmetic validator; its historical rates are not current provider claims"}
    path = "scripts/audit_transfer_run.py"
    raw, _, nodes = functions(path, ("quota_allows_generation",))
    namespace = compile_functions(nodes, {})
    quota = {"name": "quota", "entry": "quota_allows_generation", "parameter": "snapshot",
             "source": "\n\n".join(ast.unparse(n) for n in nodes), "original": namespace["quota_allows_generation"],
             "source_path": path, "source_file_sha256": hashlib.sha256(raw).hexdigest(),
             "evidence_class": "inspected repository normalized-quota validator; no live account observation"}
    late_source = "def lookup(record, key):\n    values = record.get('values', {})\n    return values.get(key)\n"
    namespace = {}
    exec(compile(late_source, "constructed_late_key_control", "exec"), namespace)
    late = {"name": "late_key", "entry": "lookup", "parameter": "record", "source": late_source,
            "original": namespace["lookup"], "source_path": None,
            "evidence_class": "constructed late-key family, not another actual repository program or natural task"}
    return (dispatch, tokens, quota, late)


def outcome(program, record, argument=None):
    try:
        if program["name"] == "dispatch":
            return evidence.original_decision(record, program["original"])
        result = program["original"](record, argument) if program["name"] in ("quota", "late_key") else program["original"](record)
        return ["value", result]
    except (ValueError, TypeError, KeyError, AttributeError) as error:
        return ["error", type(error).__name__, str(error)]
