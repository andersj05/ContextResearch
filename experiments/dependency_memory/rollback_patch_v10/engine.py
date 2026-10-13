"""A naturally failed patch, then a matched 2x2 repair experiment."""
from copy import deepcopy
import ast
import difflib
import time
from .common import STUDY, ARMS, ATTEMPTS, MIN_CHANGED_LINES, sha, wire
from .contexts import render, visible, fits, parse_action, parse_lesson
from .tasks import public_task, public_check, terminal_check
from ..rollback_development_v5.accounting import Identity, Stopped
from ..rollback_development_v5_continuation.accounting import CallUnknown


class ContractError(RuntimeError):
    pass


class Capacity(ValueError):
    pass


def identity(task, arm, step, kind="action"):
    return Identity(STUDY, task["task_id"], "patch_factorial", arm, step, kind)


def patch(base_files, files):
    before = {f["path"]: f["text"] for f in base_files}
    chunks, changed = [], 0
    for entry in sorted(files, key=lambda f: f["path"]):
        path = entry["path"]
        lines = list(difflib.unified_diff(before[path].splitlines(keepends=True),
                                         entry["text"].splitlines(keepends=True),
                                         fromfile="a/" + path, tofile="b/" + path))
        changed += sum(bool(line[1:].strip()) for line in lines
                       if line.startswith(("+", "-")) and not line.startswith(("+++", "---")))
        chunks.append("".join(line if line.endswith("\n") else line + "\n\\ No newline at end of file\n"
                              for line in lines))
    return {"diff": "\n".join(chunks), "changed_nonempty_lines": changed}


def structure_changed(base_files, files):
    """Parse bounded text only; never evaluate or execute candidate code on host.

    Ignore positions, comments, whitespace and standalone string expressions.
    This rejects cosmetic patches; an AST change is not proof of behavior change.
    """
    class WithoutStrings(ast.NodeTransformer):
        def visit_Expr(self, node):
            if isinstance(node.value, ast.Constant) and isinstance(node.value.value, str):
                return None
            return self.generic_visit(node)
    def shape(text):
        return ast.dump(WithoutStrings().visit(ast.parse(text)), include_attributes=False)
    before = {f["path"]: f["text"] for f in base_files}
    try:
        return any(shape(before[f["path"]]) != shape(f["text"]) for f in files)
    except (SyntaxError, ValueError, RecursionError):
        return False


def _call(task, arm, step, kind, invoke, prefix=None, records=()):
    request = render(task, arm=arm, prefix=prefix, records=records, kind=kind)
    if not fits(request):
        raise Capacity("context_capacity")
    result = invoke(identity(task, arm, step, kind), request)
    if result.capped:
        raise ValueError("capped_output")
    return result.text


def _attempt(task, arm, step, invoke, runtime, prefix=None, records=()):
    try:
        text = _call(task, arm, step, "action", invoke, prefix, records)
        action = parse_action(text)
    except Capacity:
        raise
    except (ValueError, KeyError, TypeError):
        return {"step": step, "public": {"status": "invalid_candidate", "score": 0,
                                           "disposition": "invalid_action"},
                "terminal": {"score": 0, "disposition": "invalid_action"},
                "visible_work": {"patch": "", "note": "The submitted response was invalid."},
                "changed_nonempty_lines": 0, "candidate": None}
    candidate = {"files": action["files"]}
    delta = patch(task["base_files"], action["files"])
    receipt = public_check(task, candidate, runtime)
    terminal = terminal_check(task, candidate, runtime)
    return {"step": step, "public": receipt, "terminal": terminal, "candidate": candidate,
            "visible_work": {"patch": delta["diff"], "note": action["note"]},
            "changed_nonempty_lines": delta["changed_nonempty_lines"]}


def _record_view(record):
    return {"step": record["step"], "public": deepcopy(record["public"]),
            "work": deepcopy(record["visible_work"])}


def run_prefix(task, invoke, runtime):
    start = time.monotonic()
    result = {"task_id": task["task_id"], "task_sha256": sha(task), "eligible": False,
              "reason": None, "failed_record": None, "lesson": None,
              "lesson_disposition": "not_needed", "attempts": [], "outcome": {"score": None}}
    try:
        record = _attempt(task, "prefix", 1, invoke, runtime)
        result["attempts"].append(record)
        result["outcome"] = record["terminal"]
        if record["public"]["status"] != "public_mismatch":
            result["reason"] = record["public"]["status"]
            return result
        if (record["changed_nonempty_lines"] < MIN_CHANGED_LINES or
                not structure_changed(task["base_files"], record["candidate"]["files"])):
            result["reason"] = "insubstantial_patch"
            return result
        result.update(eligible=True, reason="natural_substantive_patch_mismatch", failed_record=record)
        try:
            result["lesson"] = parse_lesson(_call(task, "prefix", 1, "lesson", invoke, result))
            result["lesson_disposition"] = "valid"
        except CallUnknown:
            result["lesson_disposition"] = "unknown_dispatch"
        except Stopped:
            result["lesson_disposition"] = "infrastructure_stop"
        except (ValueError, KeyError, TypeError):
            result["lesson_disposition"] = "invalid_lesson"
        result["contract"] = factorial_contract(task, result)
        return result
    except CallUnknown:
        result["reason"] = "unknown_dispatch"
    except Stopped:
        result["reason"] = "infrastructure_stop"
    except Capacity:
        result["reason"] = "context_capacity"
    finally:
        result["elapsed_seconds"] = time.monotonic() - start
    return result


def factorial_contract(task, prefix):
    def require(condition, name):
        if not condition:
            raise ContractError(name)
    require(prefix["eligible"] and prefix["task_sha256"] == sha(task), "eligible_task_identity")
    failed = prefix["failed_record"]
    require(failed["public"]["status"] == "public_mismatch", "natural_executable_mismatch")
    require(failed["changed_nonempty_lines"] >= MIN_CHANGED_LINES, "substantive_patch")
    require(structure_changed(task["base_files"], failed["candidate"]["files"]), "noncosmetic_patch")
    require(patch(task["base_files"], failed["candidate"]["files"])["diff"] ==
            failed["visible_work"]["patch"], "diff_matches_submitted_files")
    requests = {arm: render(task, arm=arm, prefix=prefix) for arm in ARMS}
    normalized, hashes = [], {}
    for arm, request in requests.items():
        require(fits(request), "all_contexts_fit")
        data = request.data()
        import json
        state = json.loads(data["messages"][1]["content"])
        require(state["task"] == public_task(task), "all_task_facts_preserved")
        require(state["checkpoint_files"] == task["base_files"], "same_original_workspace")
        require(state["feedback"] == failed["public"], "same_public_feedback")
        require(state["initial_feedback"] == failed["public"], "initial_feedback_retained")
        require(state["remaining_attempts"] == ATTEMPTS and not state["continuation_records"], "same_allowance")
        require(state["failed_work"] == (failed["visible_work"] if arm.startswith("K") else None), "deletion_factor")
        require(state["lesson"] == (prefix["lesson"] if arm.endswith("L") else None), "lesson_factor")
        state["failed_work"] = state["lesson"] = None
        data["messages"][1]["content"] = wire(state)
        normalized.append(wire(data))
        hashes[arm] = {"sha256": sha(request.json_text), "body_bound_bytes": request.input_units}
    require(len(set(normalized)) == 1, "only_two_factors_differ")
    if prefix["lesson"] is not None:
        parse_lesson(wire(prefix["lesson"]))
    return {"passed": True, "task_id": task["task_id"], "requests": hashes,
            "common_request_sha256": sha(normalized[0]), "task_facts_sha256": sha(public_task(task)),
            "failed_patch_bytes": len(failed["visible_work"]["patch"].encode("utf-8")),
            "changed_nonempty_lines": failed["changed_nonempty_lines"],
            "lesson_bytes": len(wire(prefix["lesson"]).encode("utf-8")),
            "lesson_schema": "closed_categories_no_free_text", "remaining_attempts": ATTEMPTS}


def run_continuation(task, arm, prefix, invoke, runtime):
    start = time.monotonic()
    result = {"task_id": task["task_id"], "family": task["family"], "arm": arm, "score": None,
              "disposition": None, "attempts": [], "first_pass": None}
    if not prefix["eligible"]:
        result["disposition"] = "not_eligible:" + str(prefix["reason"])
        return result
    factorial_contract(task, prefix)
    if arm.endswith("L") and prefix["lesson"] is None:
        result["disposition"] = "lesson_unavailable:" + prefix["lesson_disposition"]
        return result
    try:
        for step in range(1, ATTEMPTS + 1):
            records = [_record_view(record) for record in result["attempts"]]
            record = _attempt(task, arm, step, invoke, runtime, prefix, records)
            result["attempts"].append(record)
            if record["public"]["status"] == "public_pass":
                result.update(score=record["terminal"]["score"], disposition=record["terminal"]["disposition"],
                              first_pass=step)
                return result
        result.update(score=0, disposition="repair_budget_exhausted")
    except CallUnknown:
        result["disposition"] = "unknown_dispatch"
    except Stopped:
        result["disposition"] = "infrastructure_stop"
    except Capacity:
        result.update(score=0, disposition="context_capacity")
    finally:
        result["elapsed_seconds"] = time.monotonic() - start
    return result
