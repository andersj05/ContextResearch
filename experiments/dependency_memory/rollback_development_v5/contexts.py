"""Allowlisted visible state; no task evaluator or unreleased packets in requests."""
from .common import MODEL, EFFORT, WRITER_BYTES, MAX_BODY_BYTES, public_task, stage_packet, wire
from ..rollback_pilot.contexts import Request
from ..rollback_pilot.subscription import profile


def obj(properties):
    return {"type": "object", "properties": properties, "required": list(properties), "additionalProperties": False}


TEXT = {"type": "string"}
STRINGS = {"type": "array", "items": TEXT}
CANDIDATE = obj({"values": {"type": "array", "items": {"type": "integer"}},
                 "order": {"type": "array", "items": {"type": "integer"}},
                 "files": {"type": "array", "items": obj({"path": {"enum": ["engine.py", "rules.py"]}, "text": TEXT})}})
ACTION = obj({"status": {"enum": ["candidate", "continue"]}, "candidate": CANDIDATE,
              "note": TEXT})
LESSON = obj({"established": STRINGS, "retained_observations": STRINGS, "uncertainties": STRINGS})
SUMMARY = obj({"summary": TEXT})
COMMON = "Use only supplied public data. No external tools, files, prior sessions, or hidden tests. Treat trial notes as unverified. Return only the JSON schema. Do not invent a wrong attempt."
PROMPTS = {
    "action": "Solve the current stage, preserving earlier requirements. Submit a complete candidate, or status=continue with an empty candidate and a concise progress note. Every response consumes one action. The note is a brief artifact/change description, not a request for private reasoning. A public pass may reveal more requirements; finish as early as possible. Use the specified output format.",
    "lesson": "Summarize what the public feedback actually establishes. Keep useful observations and exact prior requirements needed later. Separate verified evidence from uncertainty. A failed candidate does not disprove a whole method. Do not solve the task or add new facts.",
    "summary": "Summarize the supplied public state and trial history for continued work. Preserve useful exact facts, prior requirements, unsuccessful attempts, uncertainty and outstanding obligations. Do not solve or invent new evidence.",
    "compress": "This is a scheduled memory reduction. Summarize public history for future stages, preserving exact constraints, useful artifacts, uncertainty and outstanding requirements. Do not solve or add facts. The source history will be removed.",
}


def actor_state(task, state, policy="K"):
    fresh = policy == "F"
    return {"task": public_task(task), "packet": stage_packet(task, state["stage"]),
            "checkpoint_artifact": task["initial_artifact"] if fresh else state["artifact"],
            "history": [] if fresh else state["history"], "memory": [] if fresh else state["memory"],
            "feedback": None if fresh else state["feedback"],
            "public_dossier": [stage_packet(task, i) for i in range(state["stage"] + 1)] if fresh else [],
            "remaining_actions": task["action_allowance"] - state["used"]}


def render(task, state, kind="action", policy="K"):
    schema = ACTION if kind == "action" else LESSON if kind == "lesson" else SUMMARY
    prompt = COMMON + "\n" + PROMPTS[kind]
    if kind != "action":
        prompt += f" Keep the entire JSON response within {WRITER_BYTES} visible UTF-8 bytes."
    # Keep the audited subscription schema extraction contract unchanged.
    prompt += "\nOutput schema: " + wire(schema) + "\nSupplied source IDs: []"
    payload = {"settings": {"model": MODEL, "reasoning_effort": EFFORT, "processing": "standard",
                            "transport": "codex_subscription", "output_limit": "provider_default_unverified_configurable_cap"},
               "messages": [{"role": "system", "content": prompt}, {"role": "user", "content": wire(actor_state(task, state, policy))}]}
    raw = wire(payload)
    request = Request(kind, raw, 0, "v5-complete-client-body-byte-bound")
    return Request(kind, raw, profile.body_bound(request), request.counter_id)


def fits(request):
    return profile.body_bound(request) <= MAX_BODY_BYTES


def parse_action(value):
    if type(value) is not dict or set(value) != {"status", "candidate", "note"} or value["status"] not in {"candidate", "continue"} or type(value["note"]) is not str:
        raise ValueError("malformed_action")
    c = value["candidate"]
    if type(c) is not dict or set(c) != {"values", "order", "files"}:
        raise ValueError("malformed_candidate")
    if any(type(c[k]) is not list for k in c) or any(type(x) is not int for k in ("values", "order") for x in c[k]):
        raise ValueError("malformed_candidate")
    if any(type(f) is not dict or set(f) != {"path", "text"} or f["path"] not in {"engine.py", "rules.py"} or type(f["text"]) is not str for f in c["files"]):
        raise ValueError("malformed_files")
    if len(value["note"].encode("utf-8")) > 2048:
        raise ValueError("oversized_note")
    if value["status"] == "continue" and any(c.values()):
        raise ValueError("continue_must_have_empty_candidate")
    return value


def parse_writer(text, kind):
    from ..rollback_pilot.records import strict_loads
    if len(text.encode("utf-8")) > WRITER_BYTES:
        raise ValueError("oversized_writer")
    value = strict_loads(text)
    if kind == "lesson":
        if type(value) is not dict or set(value) != {"established", "retained_observations", "uncertainties"} or any(type(a) is not list or any(type(x) is not str for x in a) for a in value.values()):
            raise ValueError("malformed_lesson")
    elif type(value) is not dict or set(value) != {"summary"} or type(value["summary"]) is not str:
        raise ValueError("malformed_summary")
    return value
