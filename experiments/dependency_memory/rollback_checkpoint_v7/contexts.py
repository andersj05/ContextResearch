"""Fact-preserving contexts for a single matched failed-branch intervention.

Public packets have their own immutable channel.  Only ``trial`` is removed
between the first K and R continuation requests; neither request names its arm.
"""
from copy import deepcopy

from .common import MODEL, EFFORT, WRITER_BYTES, MAX_BODY_BYTES, public_task, wire
from ..rollback_development_v5.contexts import ACTION, LESSON, parse_action, parse_writer
from ..rollback_pilot.contexts import Request
from ..rollback_pilot.subscription import profile


COMMON = (
    "Use only supplied public data. No external tools, files, prior sessions, or hidden tests. "
    "Treat trial notes and unverified observations as unverified. Return only the JSON schema. "
    "Do not intentionally make a wrong attempt."
)
PROMPTS = {
    "action": (
        "Solve the current stage using every released packet in public_dossier. "
        "The checkpoint contains accepted earlier work; accepted_artifact is the latest accepted candidate. "
        "Later packets can revise earlier transactions, so retain and apply all released task data. "
        "Every action must submit your best complete candidate, even if uncertain whether it passes. "
        "Every response consumes one action. The note is a brief artifact/change description, not "
        "a request for private reasoning. A public pass may reveal another packet. "
        "Finish as early as possible and use the specified output format."
    ),
    "lesson": (
        "Summarize what the public feedback establishes about the failed attempt in trial. "
        "The public task, all packets released so far, and successful checkpoint records will remain "
        "available unchanged for continuation. Retain useful observations from the failed attempt "
        "and separate verified evidence from uncertainty. A failed candidate does not disprove "
        "a whole method. Do not solve the task or add new facts."
    ),
}


def actor_state(task, state):
    """Allowlisted visible state; bookkeeping and evaluator data never enter it."""
    if not 0 <= state["stage"] < len(task["stages"]):
        raise ValueError("no_current_stage")
    return deepcopy({
        "task": public_task(task),
        "current_stage": state["stage"] + 1,
        "public_dossier": state["public_dossier"],
        "checkpoint": {"artifact": state["checkpoint_artifact"], "records": state["checkpoint_records"]},
        "accepted_artifact": state["artifact"],
        "trial": state["trial"],
        "continuation_records": state["continuation_records"],
        "feedback": state["feedback"],
        "lesson": state["lesson"],
        "remaining_actions": task["action_allowance"] - state["used"],
    })


def render(task, state, kind="action"):
    if kind not in PROMPTS:
        raise ValueError("unknown_request_kind")
    schema = deepcopy(ACTION if kind == "action" else LESSON)
    if kind == "action":
        schema["properties"]["status"] = {"enum": ["candidate"]}
    prompt = COMMON + "\n" + PROMPTS[kind]
    if kind == "lesson":
        prompt += f" Keep the entire JSON response within {WRITER_BYTES} visible UTF-8 bytes."
    # Preserve the pinned subscription client's schema extraction contract.
    prompt += "\nOutput schema: " + wire(schema) + "\nSupplied source IDs: []"
    payload = {
        "settings": {"model": MODEL, "reasoning_effort": EFFORT, "processing": "standard",
                     "transport": "codex_subscription", "output_limit": "provider_default_unverified_configurable_cap"},
        "messages": [{"role": "system", "content": prompt},
                     {"role": "user", "content": wire(actor_state(task, state))}],
    }
    raw = wire(payload)
    request = Request(kind, raw, 0, "v7-complete-client-body-byte-bound")
    return Request(kind, raw, profile.body_bound(request), request.counter_id)


def fits(request):
    return profile.body_bound(request) <= MAX_BODY_BYTES
