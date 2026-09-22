"""Frozen release-state generation, projections, disclosure, and exact scoring."""
from copy import deepcopy
import hashlib
import json
import random

from .protocol import VERSION, MEMORY_SCHEMA

PARENT_CAP, CHILD_CAP = 900, 440
ARMS = ("prose", "structured", "repair", "direct", "indexed", "full")
PAIRS = ((0, 1), (2, 4), (3, 5), (0, 4))
RULES = (
    "Release only when approval equals the current artifact, every required CI test has result pass, "
    "and there are no open blockers. CI is bound to the artifact in ci_artifact; all required tests "
    "need rerunning when that differs. Optional failing tests do not block. Work names are exactly "
    "approval (missing/stale approval), ci:<test> (required test absent/failing/stale), and blocker:<id> "
    "(one per open blocker). Work is a set. If work is empty choose release; otherwise hold. "
    "Notes, owners, and elapsed discussion do not change gates. Apply the late event before deciding. "
    "If necessary facts were forgotten, choose inspect, with the facts you can recover from memory."
)
EXEC_SCHEMA = {"type": "object", "properties": {
    "action": {"type": "string", "enum": ["release", "hold", "inspect"]},
    "artifact": {"type": "string"}, "work": {"type": "array", "items": {"type": "string"}}},
    "required": ["action", "artifact", "work"], "additionalProperties": False}
PROJECTION_FORMAT = "rows=[service,artifact,approval,ci_artifact,required,ci,blockers]"


def compact(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def token(seed, label):
    return hashlib.sha256(f"{seed}:{label}".encode()).hexdigest()[:8]


def fixtures():
    answer = []
    for index, seed in enumerate(range(9201, 9205)):
        records = []
        for j, name in enumerate(("atlas", "birch", "cedar", "delta", "ember", "fjord")):
            artifact = token(seed, name)
            row = {"service": f"{name}-{token(seed, 'name'+name)[:3]}", "artifact": artifact,
                   "approval": artifact, "ci_artifact": artifact, "required": ["unit", "integ"],
                   "ci": {"unit": "pass", "integ": "pass", "perf": "fail"}, "blockers": [],
                   "owner": f"team-{j+1}", "build_log": []}
            if j == 1:
                row["approval"] = token(seed, "old-approval")
            if j == 2:
                row["ci"]["integ"] = "fail"
            if j == 3:
                row["blockers"] = ["REL-" + token(seed, name)[:4]]
            if j == 5:
                row["ci_artifact"] = token(seed, "old-ci")
            row["build_log"] = [
                f"Build worker {j+21} uploaded {artifact}; image scanning finished; tracking labels refreshed.",
                "Optional performance job is red on the shared runner; release policy follows required membership.",
                "The release page says validation work completed. Keep exact check scope from the tool fields.",
                "Release notes were copyedited; screenshot snapshots and changelog links are filed in the task.",
                "Artifact labels, dashboard colors, and team ownership were checked for consistency.",
                "A later operator will select services and may update a gate. No deployment has occurred.",
            ]
            records.append(row)
        pair = [records[j]["service"] for j in PAIRS[index]]
        ordered = deepcopy(records)
        random.Random(seed).shuffle(ordered)
        futures = []
        for position, j in enumerate(PAIRS[index]):
            row = records[j]
            irrelevant = {"kind": "note", "value": "Release page typography corrected; gate fields unchanged."}
            if j == 1:
                relevant = {"kind": "approve", "value": row["artifact"]}
            elif j == 2:
                relevant = {"kind": "test", "name": "integ", "value": "pass", "artifact": row["artifact"]}
            elif j == 3:
                relevant = {"kind": "close_blocker", "value": row["blockers"][0]}
            elif j == 5:
                relevant = {"kind": "ci_artifact", "value": row["artifact"]}
            elif index == 3 and position == 1:
                relevant = {"kind": "require_test", "value": "perf"}
            elif index == 0:
                relevant = {"kind": "artifact", "value": token(seed, "rebuilt")}
            else:
                relevant = {"kind": "add_blocker", "value": "REL-" + token(seed, "new")[:4]}
            for event_index, event in enumerate((irrelevant, relevant)):
                futures.append({"id": f"w{index}-t{position}-e{event_index}", "target": row["service"], "event": event})
        answer.append({"id": f"w{index}", "seed": seed, "records": ordered, "pair": pair, "futures": futures})
    return answer


def apply_event(record, event):
    row = deepcopy(record)
    kind, value = event["kind"], event["value"]
    if kind == "note":
        pass
    elif kind in {"artifact", "ci_artifact"}:
        row[kind] = value
    elif kind == "approve":
        row["approval"] = value
    elif kind == "test":
        # A scoped test result cannot silently refresh the whole CI artifact.
        if row["ci_artifact"] == event["artifact"]:
            row["ci"][event["name"]] = value
    elif kind == "add_blocker":
        row["blockers"] = sorted(set(row["blockers"]) | {value})
    elif kind == "close_blocker":
        row["blockers"] = [x for x in row["blockers"] if x != value]
    elif kind == "require_test":
        row["required"] = sorted(set(row["required"]) | {value})
    else:
        raise ValueError("Unknown event")
    return row


def expected(record, event):
    row = apply_event(record, event)
    work = []
    if row["approval"] != row["artifact"]:
        work.append("approval")
    for name in row["required"]:
        if row["ci_artifact"] != row["artifact"] or row["ci"].get(name) != "pass":
            work.append("ci:" + name)
    work += ["blocker:" + x for x in row["blockers"]]
    return {"action": "hold" if work else "release", "artifact": row["artifact"], "work": sorted(set(work))}


def grade(response, truth):
    valid = isinstance(response, dict) and set(response) == {"action", "artifact", "work"} and isinstance(response.get("work"), list) and all(isinstance(x, str) for x in response["work"])
    if not valid:
        return {"success": False, "schema_valid": False, "unsafe_release": False}
    normalized = {**response, "work": sorted(set(response["work"]))}
    return {"success": normalized == truth and len(response["work"]) == len(set(response["work"])),
            "schema_valid": True, "unsafe_release": response["action"] == "release" and truth["action"] == "hold",
            "artifact_correct": response["artifact"] == truth["artifact"],
            "work_correct": normalized["work"] == truth["work"], "action_correct": response["action"] == truth["action"]}


def projection(records):
    rows = [[r[k] for k in ("service", "artifact", "approval", "ci_artifact", "required", "ci", "blockers")] for r in sorted(records, key=lambda r: r["service"])]
    return compact({"format": PROJECTION_FORMAT, "rows": rows})


def decode(memory):
    data = json.loads(memory)
    if set(data) != {"format", "rows"} or data["format"] != PROJECTION_FORMAT:
        raise ValueError("Not a dependency projection")
    names = ("service", "artifact", "approval", "ci_artifact", "required", "ci", "blockers")
    return [dict(zip(names, row, strict=True)) for row in data["rows"]]


def admit(response, cap):
    memory = response.get("memory", "") if isinstance(response, dict) else ""
    if not isinstance(memory, str):
        memory = ""
    raw = memory.encode("utf-8")
    return raw[:cap].decode("utf-8", errors="ignore"), {"proposed_bytes": len(raw), "admitted_bytes": len(raw[:cap].decode("utf-8", errors="ignore").encode()), "clipped": len(raw) > cap}


def repair(memory, records, cap):
    checked = projection(records)
    if len(checked.encode()) > cap:
        raise ValueError("Dependency projection exceeds memory cap")
    return checked, {"changed": checked != memory, "checked_source_bytes": len(compact(records).encode()), "replacement_bytes": len(checked.encode())}


def request(stage, instruction, observation, schema=MEMORY_SCHEMA):
    return {"version": VERSION, "stage": stage, "instruction": instruction, "observation": observation, "response_schema": schema}


def memory_request(stage, arm, observation, cap):
    style = ("Write a concise prose handoff of the current task state and important remaining work. " if arm == "prose" else
             "Write a compact structured handoff. Preserve exact artifact identifiers, approval and CI scope, required versus optional tests, explicit absence of blockers, unresolved blockers, and revision-sensitive dependencies. Do not replace scoped evidence with just done/ready. ")
    return request(stage, style + f"Your entire retained memory string must fit {cap} UTF-8 bytes. Only that string survives. "
                   "The future target and event are not yet revealed; keep enough for every candidate. You may use compact notation and must define it in memory. " + RULES,
                   observation)


def execute_request(memory, future):
    return request("execute", "Continue the release workflow using only the supplied evidence. " + RULES +
                   " Return the exact current artifact and all outstanding work. The event applies only to the target. Do not call tools.",
                   {"memory": memory, "target": future["target"], "late_event": future["event"]}, EXEC_SCHEMA)
