"""Staged episodes, exact common-prefix forks, and independently started policies."""
from copy import deepcopy
import json
import time

from .common import STUDY, MEMORY_BOUNDARIES, stage_packet, sha, wire
from .contexts import render, fits, parse_action, parse_writer
from .accounting import Identity, Stopped
from .tasks import public_check, terminal_check
from ..rollback_pilot.records import strict_loads


class Capacity(ValueError):
    pass


def initial_state(task):
    return {"stage": 0, "used": 0, "artifact": deepcopy(task["initial_artifact"]), "history": [], "memory": [],
            "feedback": None, "rejected_hashes": [], "repeated_candidates": 0, "prior_requirement_failures": 0,
            "compression_count": 0, "history_bytes_before_removal": [], "call_ids": [], "events": []}


def call(task, state, track, arm, kind, invoke, step=None):
    identity = Identity(STUDY, task["task_id"], track, arm, state["used"] if step is None else step, kind)
    request = render(task, state, kind, "F" if arm == "F" else "K")
    if not fits(request):
        raise Capacity("complete_client_body_capacity")
    response = invoke(identity, request)
    state["call_ids"].append(identity.key)
    if response.capped:
        raise ValueError("capped_output")
    return response.text


def evidence_lesson(state):
    """Mechanical public-receipt record: no new solution, hypothesis, or oracle."""
    return {"established": [wire(state["feedback"])], "retained_observations": [], "uncertainties": []}


def apply_intervention(state, arm, lesson=None, summary=None):
    policy = {"KE": "K", "RE": "R"}.get(arm, arm)
    if arm in {"KE", "RE"}:
        lesson = evidence_lesson(state)
    if policy in {"K", "R"}:
        if lesson is None:
            raise ValueError("missing_common_lesson")
        state["memory"].append({"kind": "lesson", "content": deepcopy(lesson)})
    elif policy == "G":
        if summary is None:
            raise ValueError("missing_common_summary")
        state["memory"] = [{"kind": "summary", "content": deepcopy(summary)}]
    if policy in {"R", "Z", "G", "F"}:
        state["history_bytes_before_removal"].append(len(wire(state["history"]).encode("utf-8")))
        state["history"] = []
    if policy == "F":
        state["memory"] = []


def outcome(task, state, track, arm, disposition, score, started):
    return {"task_id": task["task_id"], "family": task["family"], "domain": task["domain"],
            "horizon": task["horizon"], "difficulty": task["difficulty"], "track": track, "arm": arm,
            "score": score, "disposition": disposition, "actions_used": state["used"],
            "action_allowance": task["action_allowance"], "stages_passed": min(state["stage"], len(task["stages"])),
            "elapsed_seconds": time.monotonic() - started, "call_ids": list(state["call_ids"]),
            "repeated_candidates": state["repeated_candidates"], "prior_requirement_failures": state["prior_requirement_failures"],
            "compression_count": state["compression_count"], "history_bytes_before_removal": state["history_bytes_before_removal"],
            "events": state["events"], "terminal_artifact": state["artifact"]}


def action(task, state, track, arm, invoke, runner):
    input_history_bytes = len(wire(state["history"]).encode("utf-8")) if arm != "F" else 2
    text = call(task, state, track, arm, "action", invoke, step=state["used"] + 1)
    state["used"] += 1
    value = parse_action(strict_loads(text))
    packet = stage_packet(task, state["stage"])
    if value["status"] == "continue":
        receipt = {"status": "no_candidate"}
    else:
        h = sha(value["candidate"])
        if h in state["rejected_hashes"]:
            state["repeated_candidates"] += 1
        receipt = public_check(task, state["stage"], value["candidate"], runner)
        if receipt["status"] == "public_mismatch":
            state["rejected_hashes"].append(h)
            old_ids = {r["id"] for p in task["stages"][:state["stage"]] for r in p["requirements"]}
            old_ids |= {t["id"] for p in task["stages"][:state["stage"]] for r in p["requirements"] for t in r.get("tests", [])}
            state["prior_requirement_failures"] += int(receipt.get("check") in old_ids)
    state["history"].append({"packet": packet, "action": value, "receipt": receipt})
    state["feedback"] = receipt
    state["events"].append({"step": state["used"], "stage": state["stage"] + 1, "status": receipt["status"],
                            "input_history_bytes": input_history_bytes,
                            "history_bytes": len(wire(state["history"]).encode("utf-8")),
                            "checkpoint_artifact_bytes": len(wire(state["artifact"]).encode("utf-8")),
                            "retained_memory_bytes": len(wire(state["memory"]).encode("utf-8")),
                            "public_packet_bytes": len(wire(packet).encode("utf-8")), "check": receipt.get("check")})
    if receipt["status"] == "public_pass":
        state["artifact"] = value["candidate"]
        state["stage"] += 1
    return receipt


def run_episode(task, track, arm, invoke, runner=None, prefix=None, shared=None):
    started = time.monotonic()
    state = deepcopy(prefix) if prefix is not None else initial_state(task)
    # Continuation accounting excludes shared preparation; its ids are reported separately.
    if prefix is not None:
        state["call_ids"] = []
        state["events"] = []
        apply_intervention(state, arm, **shared)
    try:
        while state["used"] < task["action_allowance"]:
            receipt = action(task, state, track, arm, invoke, runner)
            if state["stage"] == len(task["stages"]):
                grade = terminal_check(task, state["artifact"], runner)
                return outcome(task, state, track, arm, grade["disposition"], grade["score"], started)
            if receipt["status"] not in {"public_pass", "public_mismatch", "no_candidate"}:
                return outcome(task, state, track, arm, receipt["status"], 0, started)
            if state["used"] == task["action_allowance"]:
                break
            if track in {"policy", "memory"} and receipt["status"] == "public_mismatch":
                lesson = summary = None
                if arm in {"K", "R"}:
                    lesson = parse_writer(call(task, state, track, arm, "lesson", invoke), "lesson")
                elif arm == "G":
                    summary = parse_writer(call(task, state, track, arm, "summary", invoke), "summary")
                apply_intervention(state, arm, lesson, summary)
            # Separately labelled repeated-compression condition, never implicit in policy.
            if track == "memory" and receipt["status"] == "public_pass" and state["stage"] in MEMORY_BOUNDARIES:
                summary = parse_writer(call(task, state, track, arm, "compress", invoke), "compress")
                state["history_bytes_before_removal"].append(len(wire(state["history"]).encode("utf-8")))
                state["history"] = []
                state["memory"] = [{"kind": "scheduled_compression", "content": summary}]
                state["compression_count"] += 1
        return outcome(task, state, track, arm, "action_budget_exhausted", 0, started)
    except Stopped:
        return outcome(task, state, track, arm, "infrastructure_stop", None, started)
    except Capacity:
        return outcome(task, state, track, arm, "context_capacity", 0, started)
    except (ValueError, KeyError, TypeError) as error:
        # A received but invalid record is an observed policy failure, not a retry.
        return outcome(task, state, track, arm, "invalid_record:" + type(error).__name__, 0, started)


def run_prefix(task, invoke, runner=None):
    started = time.monotonic(); state = initial_state(task)
    try:
        while state["used"] < task["action_allowance"]:
            receipt = action(task, state, "mechanism", "prefix", invoke, runner)
            if state["stage"] == len(task["stages"]):
                grade = terminal_check(task, state["artifact"], runner)
                return {"eligible": False, "reason": "initial_public_pass", "outcome": outcome(task, state, "mechanism", "prefix", grade["disposition"], grade["score"], started)}
            if receipt["status"] == "public_mismatch":
                if state["used"] == task["action_allowance"]:
                    return {"eligible": False, "reason": "no_remaining_actions", "outcome": outcome(task, state, "mechanism", "prefix", "action_budget_exhausted", 0, started)}
                shared = {}; failed = {}
                for kind in ("lesson", "summary"):
                    try:
                        shared[kind] = parse_writer(call(task, state, "mechanism", "shared", kind, invoke, step=0), kind)
                    except (Capacity, ValueError, KeyError, TypeError):
                        shared[kind] = None; failed[kind] = "unusable_writer"
                return {"eligible": True, "state": state, "shared": shared, "writer_failures": failed,
                        "outcome": outcome(task, state, "mechanism", "prefix", "public_mismatch", None, started)}
            if receipt["status"] not in {"public_pass", "no_candidate"}:
                return {"eligible": False, "reason": receipt["status"], "outcome": outcome(task, state, "mechanism", "prefix", receipt["status"], 0, started)}
        reason, score = "action_budget_exhausted", 0
    except Stopped:
        reason, score = "infrastructure_stop", None
    except Capacity:
        reason, score = "context_capacity", 0
    except (ValueError, KeyError, TypeError):
        reason, score = "invalid_record", 0
    return {"eligible": False, "reason": reason, "outcome": outcome(task, state, "mechanism", "prefix", reason, score, started)}
