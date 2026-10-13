"""Independent complete episodes; failure-triggered deletion matches v5 exactly."""
from copy import deepcopy
import time

from .common import STUDY, wire, sha, stage_packet
from .contexts import render, fits, parse_action, parse_writer
from .tasks import public_check, terminal_check
from ..rollback_development_v5.accounting import Identity, Stopped
from ..rollback_development_v5.engine import initial_state, apply_intervention, outcome
from ..rollback_pilot.records import strict_loads


def run_episode(task, arm, invoke):
    state = initial_state(task); started = time.monotonic()
    def call(kind, step):
        request = render(task, state, kind, "F" if arm == "F" else "K")
        if not fits(request): raise OverflowError("context_capacity")
        identity = Identity(STUDY, task["task_id"], "policy", arm, step, kind)
        response = invoke(identity, request)
        state["call_ids"].append(identity.key)
        if response.capped: raise ValueError("capped_output")
        return response.text
    def finish(disposition, score):
        result = outcome(task, state, "policy", arm, disposition, score, started)
        result.pop("prior_requirement_failures")  # This diagnostic is not defined for revised ledger balances.
        return result
    try:
        while state["used"] < task["action_allowance"]:
            history_bytes = len(wire(state["history"]).encode("utf-8")) if arm != "F" else 2
            text = call("action", state["used"] + 1)
            state["used"] += 1
            value = parse_action(strict_loads(text))
            if task["contract"].get("require_candidates", False) and value["status"] != "candidate":
                raise ValueError("candidate_required")
            packet = stage_packet(task, state["stage"])
            receipt = {"status": "no_candidate"} if value["status"] == "continue" else public_check(task, state["stage"], value["candidate"])
            if value["status"] == "candidate":
                h = sha(value["candidate"])
                if h in state["rejected_hashes"]: state["repeated_candidates"] += 1
                if receipt["status"] == "public_mismatch": state["rejected_hashes"].append(h)
            state["history"].append({"packet": packet, "action": value, "receipt": receipt})
            state["feedback"] = receipt
            state["events"].append({"step": state["used"], "stage": state["stage"] + 1,
                                    "status": receipt["status"], "check": receipt.get("check"),
                                    "input_history_bytes": history_bytes,
                                    "history_bytes": len(wire(state["history"]).encode("utf-8")),
                                    "retained_memory_bytes": len(wire(state["memory"]).encode("utf-8")),
                                    "checkpoint_artifact_bytes": len(wire(state["artifact"]).encode("utf-8")),
                                    "public_packet_bytes": len(wire(packet).encode("utf-8"))})
            if receipt["status"] == "public_pass":
                state["artifact"] = value["candidate"]; state["stage"] += 1
                if state["stage"] == len(task["stages"]):
                    grade = terminal_check(task, state["artifact"])
                    return finish(grade["disposition"], grade["score"])
            elif receipt["status"] not in {"public_mismatch", "no_candidate"}:
                return finish(receipt["status"], 0)
            if receipt["status"] == "public_mismatch" and state["used"] < task["action_allowance"]:
                lesson = summary = None
                if arm in {"K", "R"}: lesson = parse_writer(call("lesson", state["used"]), "lesson")
                if arm == "G": summary = parse_writer(call("summary", state["used"]), "summary")
                apply_intervention(state, arm, lesson, summary)
        return finish("action_budget_exhausted", 0)
    except Stopped:
        return finish("infrastructure_stop", None)
    except OverflowError:
        return finish("context_capacity", 0)
    except (ValueError, KeyError, TypeError):
        return finish("invalid_record", 0)
