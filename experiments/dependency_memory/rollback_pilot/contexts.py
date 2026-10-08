"""Allowlist renderer and frozen prompt extraction. Transport-neutral E0 requests."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .records import ActorTask, InterfaceError, Record, digest, strict_loads, wire


FIELDS = ("task", "checkpoint", "trial", "feedback", "lesson", "summary")
ARMS = ("K", "R", "Z", "G")
HEADINGS = {"common": "Common instruction", "checkpoint": "Checkpoint", "branch": "Branch step",
            "lesson": "Lesson writer", "summary": "Generic compactor", "terminal": "Continuation"}


def load_prompts(path=None):
    path = path or Path(__file__).with_name("PROMPTS.md")
    sections, current = {}, None
    for line in Path(path).read_text(encoding="utf-8").splitlines():
        if line.startswith("## "):
            current = line[3:]
        elif line.startswith("> "):
            sections.setdefault(current, []).append(line[2:])
    result = {key: " ".join(sections[heading]) for key, heading in HEADINGS.items()}
    if any(not text for text in result.values()):
        raise InterfaceError("missing prompt section")
    return result


def schema(kind, task, options=()):
    """Schema text is part of the counted request; strict parsing is independent."""
    text = {"type": "string"}
    array = lambda item: {"type": "array", "items": item}
    obj = lambda props: {"type": "object", "properties": props, "required": list(props), "additionalProperties": False}
    ss = array(text)
    observation = obj({"statement": text, "source_ids": ss})
    candidate = (obj({"values": {"type": "array", "items": {"type": "integer"},
                                "minItems": len(task.data()["variables"]),
                                "maxItems": len(task.data()["variables"])}})
                 if task.domain == "math" else obj({"code": text}))
    if kind == "checkpoint":
        return obj({"facts": array(observation), "open_requirements": ss,
                    "tentative_options": {**array(obj({"id": text, "method": text, "unverified_assumptions": ss})), "maxItems": 3},
                    "possible_checks": ss})
    if kind == "branch":
        return obj({"status": {"enum": ["candidate", "continue"]},
                    "chosen_option": {"enum": [*options, "new"]}, "assumptions": ss,
                    "observations": array(observation), "artifact": {"anyOf": [candidate, {"type": "null"}]}})
    if kind == "lesson":
        return obj({"failure_kind": text, "evidence_ids": ss, "refuted_claims": ss,
                    "retained_observations": ss, "uncertainties": ss})
    if kind == "summary":
        return obj({"summary": text})
    if kind == "terminal":
        return candidate
    raise InterfaceError("unknown request stage")


def record_data(value, kind):
    if value is None:
        return None
    if type(value) is not Record or value.kind != kind:
        raise InterfaceError(f"expected {kind} Record")
    return value.data()


def context(task, checkpoint=None, branches=(), feedback=None, lesson=None, summary=None):
    if type(task) is not ActorTask:
        raise InterfaceError("renderer accepts ActorTask only")
    # Revalidate at the channel boundary, even if trusted code constructed a
    # dataclass directly rather than using its checked factory.
    task = ActorTask.from_dict(task.task_id, task.stratum, task.data())
    from .grading import PublicReceipt
    if feedback is not None and type(feedback) is not PublicReceipt:
        raise InterfaceError("renderer accepts PublicReceipt only")
    if feedback is not None:
        from .records import obj
        obj(feedback.data(), ("receipt_id", "candidate_id", "status", "check_id", "observed", "expected", "detail", "truncated"))
    return wire({"task": task.data(), "checkpoint": record_data(checkpoint, "checkpoint"),
                 "trial": [record_data(x, "branch") for x in branches] if branches else None,
                 "feedback": feedback.data() if feedback else None,
                 "lesson": record_data(lesson, "lesson"), "summary": record_data(summary, "summary")})


@dataclass(frozen=True)
class Request:
    """An offline envelope, deliberately not a provider endpoint adapter."""
    stage: str
    json_text: str
    input_units: int
    counter_id: str

    @property
    def hash(self):
        return digest(self.json_text)

    def data(self):
        return strict_loads(self.json_text)


class ByteCounter:
    """Conservative UTF-8-byte units for fixtures; NOT audited provider tokens."""
    counter_id = "e0-utf8-bytes-plus-256-overhead-not-provider-tokenizer"

    def visible(self, text):
        return len(text.encode("utf-8"))

    def request(self, text):
        return self.visible(text) + 256


class Renderer:
    def __init__(self, counter=None, input_cap=32768, output_cap=16384, prompts=None):
        self.counter = counter or ByteCounter()
        self.input_cap, self.output_cap = input_cap, output_cap
        self.prompts = prompts or load_prompts()

    def render(self, stage, task, checkpoint=None, branches=(), feedback=None, lesson=None, summary=None):
        content = context(task, checkpoint, branches, feedback, lesson, summary)
        options = [x["id"] for x in checkpoint.data()["tentative_options"]] if checkpoint else []
        instruction = self.prompts["common"] + "\n" + self.prompts[stage] + "\nOutput schema: " + wire(schema(stage, task, options))
        if stage != "terminal":
            ids = task.source_ids()
            if checkpoint:
                ids.update(f"C.fact{i + 1}" for i in range(len(checkpoint.data()["facts"])))
            for index, branch in enumerate(branches):
                ids.add(f"B{index + 1}")
                ids.update(f"B{index + 1}.observation{i + 1}" for i in range(len(branch.data()["observations"])))
            if feedback:
                ids.add(feedback.data()["receipt_id"])
            instruction += "\nSupplied source IDs (C.fact and B.observation numbers refer to list order): " + wire(sorted(ids))
        payload = {"settings": {"model": "gpt-6-luna", "reasoning_effort": "medium", "processing": "standard",
                                "max_output_tokens_including_reasoning": self.output_cap, "store": False},
                   "messages": [{"role": "system", "content": instruction}, {"role": "user", "content": content}]}
        serialized = wire(payload)
        return Request(stage, serialized, self.counter.request(serialized), self.counter.counter_id)

    def continuation(self, arm, task, checkpoint, branches, feedback, lesson=None, summary=None):
        if arm not in ARMS:
            raise InterfaceError("unknown condition")
        return self.render("terminal", task, checkpoint, branches if arm == "K" else (), feedback,
                           lesson if arm in {"K", "R"} else None, summary if arm == "G" else None)

    def fits(self, request):
        return request.input_units <= self.input_cap


def shared_hashes(request):
    data = strict_loads(request.data()["messages"][1]["content"])
    return {key: digest(wire(data[key])) for key in ("task", "checkpoint", "feedback", "lesson")}
