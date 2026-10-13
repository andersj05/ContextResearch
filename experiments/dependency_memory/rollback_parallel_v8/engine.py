"""Natural-failure prefix and matched, fact-preserving K/R continuations.

Each eligible task has one shared prefix and one shared lesson.  The sole
intervention removes the first failed generated record.  Later records are
retained in both arms without further interventions or lesson calls.
"""
from copy import deepcopy
import time

from .common import STUDY, wire, sha, stage_packet, public_task
from ..rollback_checkpoint_v7.contexts import actor_state, render, fits, parse_action, parse_writer
from ..rollback_challenge_v6.tasks import public_check, terminal_check
from ..rollback_development_v5.accounting import Identity, Stopped
from ..rollback_development_v5_continuation.accounting import CallUnknown
from ..rollback_pilot.records import strict_loads


class Capacity(ValueError):
    pass


class CappedOutput(ValueError):
    pass


class PairContractError(ValueError):
    """Controller invariant failure; never a model-scored invalid record."""


def initial_state(task):
    if not task["stages"] or task["action_allowance"] < len(task["stages"]):
        raise ValueError("invalid_stage_or_action_allowance")
    return {
        "stage": 0, "used": 0, "artifact": deepcopy(task["initial_artifact"]),
        "checkpoint_artifact": deepcopy(task["initial_artifact"]), "checkpoint_records": [],
        "public_dossier": [deepcopy(stage_packet(task, 0))],
        "trial": [], "continuation_records": [], "feedback": None, "lesson": None,
        "call_ids": [], "events": [], "rejected_hashes": [], "repeated_candidates": 0,
        "prefix_actions_used": 0,
    }


def _call(task, state, arm, kind, invoke):
    step = state["used"] + 1 if kind == "action" else state["used"]
    request = render(task, state, kind)
    if not fits(request):
        raise Capacity("complete_client_body_capacity")
    identity = Identity(STUDY, task["task_id"], "mechanism", arm, step, kind)
    response = invoke(identity, request)
    state["call_ids"].append(identity.key)
    # Every received action, including malformed/capped output, consumes an action.
    if kind == "action":
        state["used"] += 1
    if response.capped:
        raise CappedOutput("capped_output")
    return response.text


def _action(task, state, arm, invoke):
    prior_visible = actor_state(task, state)
    value = parse_action(strict_loads(_call(task, state, arm, "action", invoke)))
    if value["status"] != "candidate":
        raise ValueError("candidate_required")
    receipt = public_check(task, state["stage"], value["candidate"])
    candidate_hash = sha(value["candidate"])
    if candidate_hash in state["rejected_hashes"]:
        state["repeated_candidates"] += 1
    if receipt["status"] == "public_mismatch":
        state["rejected_hashes"].append(candidate_hash)
    record = {"step": state["used"], "stage": state["stage"] + 1,
              "action": deepcopy(value), "receipt": deepcopy(receipt)}
    if arm == "prefix":
        if receipt["status"] == "public_pass":
            state["checkpoint_records"].append(record)
            state["checkpoint_artifact"] = deepcopy(value["candidate"])
        else:
            state["trial"] = [record]
    else:
        state["continuation_records"].append(record)
    state["feedback"] = deepcopy(receipt)
    state["events"].append({
        "step": state["used"], "stage": state["stage"] + 1,
        "status": receipt["status"], "check": receipt.get("check"),
        "public_dossier_bytes": len(wire(prior_visible["public_dossier"]).encode("utf-8")),
        "checkpoint_bytes": len(wire(prior_visible["checkpoint"]).encode("utf-8")),
        "input_trial_bytes": len(wire(prior_visible["trial"]).encode("utf-8")),
        "input_continuation_records_bytes": len(wire(prior_visible["continuation_records"]).encode("utf-8")),
    })
    if receipt["status"] == "public_pass":
        state["artifact"] = deepcopy(value["candidate"])
        state["stage"] += 1
        if state["stage"] < len(task["stages"]):
            state["public_dossier"].append(deepcopy(stage_packet(task, state["stage"])))
    return receipt


def _outcome(task, state, arm, disposition, score, started, shared_call_ids=()):
    return {
        "task_id": task["task_id"], "family": task["family"], "domain": task["domain"],
        "horizon": task["horizon"], "difficulty": task["difficulty"], "track": "mechanism", "arm": arm,
        "score": score, "disposition": disposition, "actions_used": state["used"],
        "prefix_actions_used": state["used"] if arm == "prefix" else state["prefix_actions_used"],
        "continuation_actions_used": state["used"] - state["prefix_actions_used"] if arm != "prefix" else 0,
        "action_allowance": task["action_allowance"], "stages_passed": min(state["stage"], len(task["stages"])),
        "elapsed_seconds": time.monotonic() - started,
        "call_ids": list(state["call_ids"]), "shared_prefix_call_ids": list(shared_call_ids),
        "repeated_candidates": state["repeated_candidates"], "events": deepcopy(state["events"]),
        "terminal_artifact": deepcopy(state["artifact"]),
    }


def run_prefix(task, invoke):
    """Run until the first natural public mismatch, then write exactly one lesson."""
    started = time.monotonic()
    state = initial_state(task)
    checkpoint = None

    def finish(eligible, reason, disposition, score):
        result = {"eligible": eligible, "reason": reason, "disposition": disposition,
                  "task_id": task["task_id"], "task_sha256": sha(task), "state": deepcopy(state),
                  "checkpoint": deepcopy(checkpoint), "trial": deepcopy(state["trial"]),
                  "lesson": deepcopy(state["lesson"]),
                  "outcome": _outcome(task, state, "prefix", disposition, score, started)}
        if eligible:
            result["pair_contract"] = pair_contract(task, result)
        return result

    phase = "action"
    try:
        while state["used"] < task["action_allowance"]:
            before = deepcopy(state)
            receipt = _action(task, state, "prefix", invoke)
            if state["stage"] == len(task["stages"]):
                grade = terminal_check(task, state["artifact"])
                return finish(False, "all_stages_passed", grade["disposition"], grade["score"])
            if receipt["status"] == "public_mismatch":
                checkpoint = before
                if state["used"] >= task["action_allowance"]:
                    return finish(False, "no_remaining_actions", "action_budget_exhausted", 0)
                phase = "lesson"
                state["lesson"] = parse_writer(_call(task, state, "prefix", "lesson", invoke), "lesson")
                return finish(True, "first_public_mismatch", "public_mismatch", None)
            if receipt["status"] != "public_pass":
                return finish(False, receipt["status"], receipt["status"], 0)
        return finish(False, "action_budget_exhausted", "action_budget_exhausted", 0)
    except PairContractError:
        raise
    except CallUnknown:
        return finish(False, "unknown_dispatch", "unknown_dispatch", None)
    except Stopped:
        return finish(False, "infrastructure_stop", "infrastructure_stop", None)
    except Capacity:
        return finish(False, phase + "_context_capacity", "context_capacity", 0)
    except CappedOutput:
        return finish(False, phase + "_capped_output", "capped_output", 0)
    except (ValueError, KeyError, TypeError):
        return finish(False, "invalid_" + phase, "invalid_record", 0)


def continuation_state(task, arm, prefix):
    """Construct an independent arm without modifying the shared prefix object."""
    if arm not in {"K", "R"}:
        raise ValueError("unknown_continuation_arm")
    state = deepcopy(prefix["state"])
    state["prefix_actions_used"] = state["used"]
    state["call_ids"] = []
    state["events"] = []
    state["repeated_candidates"] = 0
    if arm == "R":
        state["trial"] = []
    return state


def _pair_contract(task, prefix):
    """Verify the intervention before admitting either continuation request.

This is a controller invariant, not an empirical outcome.  It raises on drift
so the runner can stop globally instead of treating a broken pair as a loss.
"""
    def require(condition, name):
        if not condition:
            raise PairContractError("pair_contract:" + name)

    require(prefix.get("eligible") is True, "eligible_prefix_required")
    require(prefix["task_id"] == task["task_id"] and prefix["task_sha256"] == sha(task), "task_identity")
    state = prefix["state"]
    before = prefix["checkpoint"]
    require(type(before) is dict, "saved_checkpoint")
    require(1 <= state["used"] < task["action_allowance"], "positive_remaining_allowance")
    require(before["used"] == state["used"] - 1 and before["stage"] == state["stage"], "pre_failure_boundary")
    require(before["used"] == before["stage"], "only_successful_prefix_actions")
    require(before["trial"] == [] and before["continuation_records"] == [] and before["lesson"] is None,
            "untreated_checkpoint")
    require(state["continuation_records"] == [], "no_prefilled_continuation")
    expected_dossier = [stage_packet(task, i) for i in range(state["stage"] + 1)]
    require(wire(before["public_dossier"]) == wire(expected_dossier), "checkpoint_public_packets")
    require(wire(state["public_dossier"]) == wire(expected_dossier), "post_failure_public_packets")
    require(state["checkpoint_records"] == before["checkpoint_records"], "successful_records_preserved")
    require(len(state["checkpoint_records"]) == before["stage"], "successful_record_count")
    for index, record in enumerate(state["checkpoint_records"]):
        action = parse_action(record["action"])
        require(record["step"] == index + 1 and record["stage"] == index + 1, "prefix_record_order")
        require(action["status"] == "candidate", "prefix_candidate")
        receipt = public_check(task, index, action["candidate"])
        require(receipt["status"] == "public_pass" and record["receipt"] == receipt, "prefix_pass_receipts")
    expected_artifact = (state["checkpoint_records"][-1]["action"]["candidate"]
                         if state["checkpoint_records"] else task["initial_artifact"])
    require(all(v == expected_artifact for v in (state["artifact"], state["checkpoint_artifact"],
                                                 before["artifact"], before["checkpoint_artifact"])),
            "accepted_checkpoint_artifact")
    require(len(state["trial"]) == 1 and prefix["trial"] == state["trial"], "single_failed_branch")
    failed = state["trial"][0]
    require(failed["step"] == state["used"] and failed["stage"] == state["stage"] + 1, "failed_branch_position")
    action = parse_action(failed["action"])
    require(action["status"] == "candidate", "failed_candidate")
    receipt = public_check(task, state["stage"], action["candidate"])
    require(receipt["status"] == "public_mismatch" and failed["receipt"] == receipt and state["feedback"] == receipt,
            "first_public_mismatch_verified")
    require(prefix["lesson"] == state["lesson"] and state["lesson"] is not None, "shared_lesson")
    parse_writer(wire(state["lesson"]), "lesson")
    requests = {arm: render(task, continuation_state(task, arm, prefix)) for arm in ("K", "R")}
    require(all(fits(request) for request in requests.values()), "both_requests_fit")
    data = {arm: requests[arm].data() for arm in requests}
    visible = {arm: strict_loads(data[arm]["messages"][1]["content"]) for arm in data}
    for arm in visible:
        # Verify the serialized boundary against source data independently of
        # between-arm equality: two equally corrupted requests are still wrong.
        expected_visible = {
            "task": public_task(task), "current_stage": state["stage"] + 1,
            "public_dossier": expected_dossier,
            "checkpoint": {"artifact": expected_artifact, "records": state["checkpoint_records"]},
            "accepted_artifact": expected_artifact,
            "trial": state["trial"] if arm == "K" else [], "continuation_records": [],
            "feedback": receipt, "lesson": state["lesson"],
            "remaining_actions": task["action_allowance"] - state["used"],
        }
        require(wire(visible[arm]) == wire(expected_visible), "rendered_" + arm + "_channels_match_source")
    require(visible["K"]["trial"] == state["trial"] and visible["R"]["trial"] == [], "only_trial_removed")
    shared_hashes = {}
    for arm in data:
        visible[arm]["trial"] = []
        data[arm]["messages"][1]["content"] = wire(visible[arm])
        shared_hashes[arm] = sha(wire(data[arm]))
    require(wire(data["K"]) == wire(data["R"]), "byte_identical_except_trial")
    return {
        "passed": True, "task_id": task["task_id"], "failure_step": state["used"],
        "failure_stage": state["stage"] + 1, "remaining_actions": task["action_allowance"] - state["used"],
        "checks": {name: True for name in (
            "saved_pre_failure_checkpoint", "successful_prefix_verified", "released_public_packets_preserved",
            "first_public_mismatch_verified", "same_checkpoint_feedback_lesson_allowance", "only_trial_removed",
            "byte_identical_except_trial", "both_requests_fit")},
        "released_packet_sha256": [sha(packet) for packet in expected_dossier],
        "trial_bytes": len(wire(state["trial"]).encode("utf-8")),
        "failed_record_bytes": len(wire(failed).encode("utf-8")),
        "checkpoint_bytes": len(wire(visible["K"]["checkpoint"]).encode("utf-8")),
        "public_dossier_bytes": len(wire(expected_dossier).encode("utf-8")),
        "checkpoint_sha256": sha(visible["K"]["checkpoint"]), "lesson_sha256": sha(state["lesson"]),
        "trial_sha256": sha(state["trial"]), "common_request_sha256": shared_hashes["K"],
        "requests": {arm: {"sha256": request.hash, "body_bound_bytes": request.input_units}
                     for arm, request in requests.items()},
    }


def pair_contract(task, prefix):
    """Turn malformed contract structure into an explicit controller fault."""
    try:
        return _pair_contract(task, prefix)
    except PairContractError:
        raise
    except (ValueError, KeyError, TypeError, IndexError) as error:
        raise PairContractError("pair_contract:malformed_contract") from error


def run_continuation(task, arm, prefix, invoke):
    started = time.monotonic()
    state = continuation_state(task, arm, prefix)
    shared_ids = prefix["outcome"]["call_ids"]
    if not prefix["eligible"]:
        return _outcome(task, state, arm, "not_eligible:" + prefix["reason"], None, started, shared_ids)
    # Deliberately outside policy failure handling: invalid contracts are controller errors.
    pair_contract(task, prefix)
    try:
        while state["used"] < task["action_allowance"]:
            receipt = _action(task, state, arm, invoke)
            if state["stage"] == len(task["stages"]):
                grade = terminal_check(task, state["artifact"])
                return _outcome(task, state, arm, grade["disposition"], grade["score"], started, shared_ids)
            if receipt["status"] not in {"public_pass", "public_mismatch"}:
                return _outcome(task, state, arm, receipt["status"], 0, started, shared_ids)
        disposition, score = "action_budget_exhausted", 0
    except CallUnknown:
        disposition, score = "unknown_dispatch", None
    except Stopped:
        disposition, score = "infrastructure_stop", None
    except Capacity:
        disposition, score = "context_capacity", 0
    except CappedOutput:
        disposition, score = "capped_output", 0
    except (ValueError, KeyError, TypeError):
        disposition, score = "invalid_record", 0
    return _outcome(task, state, arm, disposition, score, started, shared_ids)
