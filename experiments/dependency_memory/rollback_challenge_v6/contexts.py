"""Visible state and a separately frozen option requiring a candidate per action."""
from copy import deepcopy

from .common import wire
from ..rollback_development_v5.contexts import actor_state, fits, parse_action, parse_writer, ACTION, COMMON
from ..rollback_development_v5.contexts import render as original_render
from ..rollback_pilot.contexts import Request
from ..rollback_pilot.subscription import profile


CANDIDATE_PROMPT = (
    "Solve the current stage, preserving earlier requirements. Every action must submit your best complete candidate, "
    "even if you are uncertain whether it passes. Do not defer submission or return status=continue. "
    "Do not intentionally make a wrong attempt. You may state uncertainty in the brief note. "
    "Every response consumes one action. The note is a brief artifact/change description, not a request for private reasoning. "
    "A public pass may reveal more requirements; finish as early as possible. Use the specified output format."
)


def render(task, state, kind="action", policy="K"):
    request = original_render(task, state, kind, policy)
    if kind != "action" or not task["contract"].get("require_candidates", False):
        return request
    schema = deepcopy(ACTION)
    schema["properties"]["status"] = {"enum": ["candidate"]}
    payload = request.data()
    payload["messages"][0]["content"] = (COMMON + "\n" + CANDIDATE_PROMPT
        + "\nOutput schema: " + wire(schema) + "\nSupplied source IDs: []")
    raw = wire(payload)
    result = Request(kind, raw, 0, "v6-required-candidate-complete-client-body-byte-bound")
    return Request(kind, raw, profile.body_bound(result), result.counter_id)
