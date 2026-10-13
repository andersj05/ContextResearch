"""Allowlisted public contexts; deletion and diagnostic lesson vary independently."""
from copy import deepcopy
from .common import MODEL, EFFORT, FOCUS, ARMS, ATTEMPTS, MAX_BODY_BYTES, MAX_INPUT_TEXT_BYTES, wire
from .tasks import public_task
from ..rollback_pilot.contexts import Request
from ..rollback_pilot.subscription import profile
from ..rollback_pilot.records import strict_loads


def obj(properties):
    return {"type": "object", "properties": properties, "required": list(properties),
            "additionalProperties": False}


ACTION = obj({"files": {"type": "array", "minItems": 2, "maxItems": 2,
                       "items": obj({"path": {"enum": ["engine.py", "rules.py"]},
                                     "text": {"type": "string"}})},
              "note": {"type": "string", "maxLength": 240}})
LESSON = obj({
    "focus": {"enum": list(FOCUS)},
    "location": {"enum": ["engine.py", "rules.py", "both", "uncertain"]},
    "diagnosis": {"enum": ["wrong_selection", "missing_constraint", "wrong_state_update",
                             "wrong_order", "wrong_boundary", "wrong_rounding", "wrong_tie_break",
                             "incomplete_search", "uncertain"]},
    "next_check": {"enum": ["trace_failed_example", "check_all_constraints", "check_update_order",
                              "enumerate_small_cases", "check_boundary_and_ties", "rederive_from_contract"]},
    "confidence": {"enum": ["low", "medium", "high"]},
})
COMMON = (
    "Use only the supplied public specification, original files, examples and feedback. "
    "Do not call tools or access files, archives, earlier sessions or hidden tests. "
    "Submit your best correction; never intentionally make a failed attempt. "
    "All task requirements and public examples remain available. "
    "The original checkpoint files are supplied on every attempt. A failed patch is unaccepted work. "
    "Diagnostic lessons are fallible hints, not established facts. Return only the required JSON."
)
ACTOR = (
    "Repair the Python project to satisfy the entire contract for arbitrary valid inputs. "
    "Return complete replacements for exactly engine.py and rules.py, preserving the solve(case) interface. "
    "The public checker runs the supplied examples. Additional private examples instantiate the same "
    "published rules; their results are never provided to you. The note is a brief description of the "
    "change, not private reasoning. A public pass ends this trajectory. "
    "If failed_work is present, it is a unified diff against the original checkpoint. "
    "All continuation_records are your own subsequent patches, also against that checkpoint."
)
WRITER = (
    "Inspect the failed patch and its public test feedback. Select one concise diagnostic lesson "
    "using the closed categories. Indicate the suspected source of the error and the best next check. "
    "Do not treat a failed example as disproving an entire method. Choose uncertain/low when warranted. "
    "These are diagnostic categories only: you cannot emit source code, a replacement patch, "
    "new facts, private tests, free-form prose or numeric answers."
)


def visible(task, *, arm="prefix", prefix=None, records=()):
    if arm not in (*ARMS, "prefix"):
        raise ValueError("unknown_arm")
    supplied = public_task(task)
    data = {"task": supplied, "checkpoint_files": deepcopy(task["base_files"]),
            "failed_work": None, "feedback": None, "initial_feedback": None, "lesson": None,
            "continuation_records": deepcopy(list(records)),
            "remaining_attempts": 1 if arm == "prefix" else ATTEMPTS - len(records)}
    if prefix is not None:
        data["feedback"] = deepcopy(prefix["failed_record"]["public"])
        data["initial_feedback"] = deepcopy(prefix["failed_record"]["public"])
        if arm.startswith("K") or arm == "prefix":
            data["failed_work"] = deepcopy(prefix["failed_record"]["visible_work"])
        if arm.endswith("L"):
            data["lesson"] = deepcopy(prefix["lesson"])
    if records:
        data["feedback"] = deepcopy(records[-1]["public"])
    return data


def render(task, *, arm="prefix", prefix=None, records=(), kind="action"):
    if kind not in {"action", "lesson"}:
        raise ValueError("request_kind")
    data = visible(task, arm=arm, prefix=prefix, records=records)
    schema = ACTION if kind == "action" else LESSON
    prompt = COMMON + "\n" + (ACTOR if kind == "action" else WRITER)
    prompt += "\nOutput schema: " + wire(schema) + "\nSupplied source IDs: []"
    payload = {"settings": {"model": MODEL, "reasoning_effort": EFFORT, "processing": "standard",
                            "transport": "codex_subscription",
                            "output_limit": "provider_default_unverified_configurable_cap"},
               "messages": [{"role": "system", "content": prompt},
                            {"role": "user", "content": wire(data)}]}
    request = Request(kind, wire(payload), 0, "v11-complete-client-body-byte-bound")
    return Request(kind, request.json_text, profile.body_bound(request), request.counter_id)


def fits(request):
    return (profile.body_bound(request) <= MAX_BODY_BYTES and
            len(request.json_text.encode("utf-8")) <= MAX_INPUT_TEXT_BYTES)


def parse_action(text):
    value = strict_loads(text)
    if type(value) is not dict or set(value) != {"files", "note"}:
        raise ValueError("action_fields")
    if type(value["note"]) is not str or len(value["note"]) > 240:
        raise ValueError("action_note")
    files = value["files"]
    if (type(files) is not list or len(files) != 2 or
            any(type(f) is not dict or set(f) != {"path", "text"} or
                type(f["path"]) is not str or type(f["text"]) is not str for f in files) or
            sorted(f["path"] for f in files) != ["engine.py", "rules.py"] or
            sum(len(f["text"].encode("utf-8")) for f in files) > 32768):
        raise ValueError("action_files")
    return value


def parse_lesson(text):
    value = strict_loads(text)
    if type(value) is not dict or set(value) != set(LESSON["properties"]):
        raise ValueError("lesson_fields")
    for key, schema in LESSON["properties"].items():
        if type(value[key]) is not str or value[key] not in schema["enum"]:
            raise ValueError("lesson_category")
    return value
