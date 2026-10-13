"""V5 state transitions, with shared-writer unknowns confined to dependent arms."""
import time

from .accounting import CallUnknown
from ..rollback_development_v5.engine import initial_state, action, call, outcome, Capacity, run_episode
from ..rollback_development_v5.accounting import Stopped
from ..rollback_development_v5.contexts import parse_writer
from ..rollback_development_v5.tasks import terminal_check


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
                    except CallUnknown:
                        shared[kind] = None; failed[kind] = "unknown_dispatch"
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
