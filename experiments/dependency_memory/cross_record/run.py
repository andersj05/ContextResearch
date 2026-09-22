"""One-shot 348-call cross-record comparison with durable per-call accounting."""
from __future__ import annotations

import argparse
from decimal import Decimal
from hashlib import sha256
import json
from pathlib import Path
import random
import sys
from time import perf_counter_ns

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "experiments/dependency_memory"))

from luna6_revision.audit import run_case
from luna6_revision import study as prior_study
from luna6_revision.protocol import request_bytes
from luna6_revision.transport import Client, RESERVATION, save
from experiments.dependency_memory.schema_transfer import memory as base
from .casebook import CHILD_CAP, EVAL, PARENT_CAP, compact, grade, truth
from . import direct, memory

ARMS = ("prompt", "structured", "checked", "automatic", "direct",
        "indexed_raw", "indexed_projected", "full")
EXEC_SCHEMA = {"type": "object", "properties": {
    "action": {"type": "string", "enum": ["submit", "hold", "publish", "retry", "close", "promote"]},
    "target_id": {"type": "string"}, "work": {"type": "array", "items": {"type": "string"}}},
    "required": ["action", "target_id", "work"], "additionalProperties": False}
CALL_SCHEDULE = 348
CALL_CAP = 356
CREDIT_CAP = Decimal("50")

PROMPT_GUIDANCE = (
    "Only the memory string survives this boundary. The decision rule repeats at execution. "
    "Write a compact, data-first prose handoff. Copy every workflow's exact root ID, component ID, "
    "status and scoped reference. State which workflow each tool result belongs to; do not collapse "
    "an approval or result into a generic 'passed'. Preserve facts for any later target and event. "
    "Ignore operator notes. Return {\"memory\":\"...\"}. ")
STRUCTURED_GUIDANCE = (
    "Only the memory string survives this boundary. The decision rule repeats at execution. "
    "Write a compact JSON table string: f is the ordered list of full field paths, r is a list of "
    "value rows for joined workflows. Root fields are unprefixed; component fields use tool.field. "
    "Include every exact root and record ID, join key, reference, enum status, and boolean needed "
    "for a later target/event. Use no abbreviations, ellipses, or omitted rows. Ignore operator notes. "
    "Return {\"memory\":\"...\"}. ")


def bytes_len(value):
    return len(value.encode() if isinstance(value, str) else compact(value).encode())


def fixture_paths():
    folder = Path(__file__).parent / "fixtures"
    manifest = json.loads((folder / "manifest.json").read_text(encoding="utf-8"))
    if manifest.get("version") != "cross_record_v1" or not manifest.get("implementation_commit"):
        raise ValueError("Evaluation fixtures not frozen")
    if len(manifest.get("development", [])) != 4 or len(manifest.get("evaluation", [])) != 12:
        raise ValueError("Wrong frozen sample size")
    for item in manifest["development"] + manifest["evaluation"]:
        path = folder / item["file"]
        if sha256(path.read_bytes()).hexdigest() != item["sha256"] or path.stat().st_size != item["bytes"]:
            raise ValueError("Frozen fixture changed")
    paths = [folder / item["file"] for item in manifest["evaluation"]]
    if {json.loads(p.read_text(encoding="utf-8"))["family"] for p in paths} != set(EVAL):
        raise ValueError("Evaluation families changed")
    return paths, manifest


def fingerprints():
    folder = Path(__file__).parent
    paths = list(folder.glob("*.py")) + [folder / "FROZEN_PROTOCOL.md"] + list((folder / "fixtures").glob("*.json"))
    return {path.relative_to(ROOT).as_posix(): sha256(path.read_bytes()).hexdigest() for path in sorted(paths)}


def parent_request(case, arm):
    guidance = PROMPT_GUIDANCE if arm == "prompt" else STRUCTURED_GUIDANCE
    instruction = guidance + f"Memory limit: {PARENT_CAP} UTF-8 bytes. " + case["rule"]
    return prior_study.request("parent", instruction, {
        "tool_schemas": case["tool_schemas"], "tool_results": case["tool_results"]})


def child_request(case, arm, parent):
    guidance = PROMPT_GUIDANCE if arm == "prompt" else STRUCTURED_GUIDANCE
    instruction = guidance + f"Retain only the two named candidates in at most {CHILD_CAP} UTF-8 bytes. " + case["rule"]
    return prior_study.request("child", instruction, {
        "previous_memory": parent, "candidates": case["candidate_ids"]})


def execution_request(case, retained, future):
    instruction = ("Use only the supplied memory, target and late event. Memory may be prose, a list "
                   "of tool results with tool/data wrappers, or a JSON table with f=full field paths "
                   "and r=rows. Root fields in a table are unprefixed; component fields use tool.field. "
                   "First apply the event only to the selected workflow. Return one exact decision "
                   "and sorted work. Do not call tools. " + case["rule"])
    return prior_study.request("execute", instruction, {
        "memory": retained, "target": future["target"], "late_event": future["event"]}, EXEC_SCHEMA)


def meter():
    return {"cpu_ns": 0, "bytes_read": 0, "bytes_written": 0}


def add(local, arm, *, cpu_ns=0, bytes_read=0, bytes_written=0):
    local[arm]["cpu_ns"] += cpu_ns
    local[arm]["bytes_read"] += bytes_read
    local[arm]["bytes_written"] += bytes_written


def add_details(local, arm, details):
    add(local, arm, cpu_ns=details["cpu_ns"], bytes_read=details["source_bytes_read"],
        bytes_written=details.get("memory_bytes_written", 0))


def admit(response, cap, local, arm):
    start = perf_counter_ns()
    retained, bounds = prior_study.admit(response, cap)
    add(local, arm, cpu_ns=perf_counter_ns() - start,
        bytes_read=bounds["proposed_bytes"], bytes_written=bounds["admitted_bytes"])
    return retained, bounds


class BudgetedClient:
    """Rotate pinned adapters without losing the study-wide call/credit ceiling."""
    def __init__(self, executable, global_instructions, directory, audit):
        self.args = (executable, global_instructions, directory, audit)
        self.clients = [Client(*self.args)]

    @property
    def attempts(self):
        return sum(client.attempts for client in self.clients)

    @property
    def spent(self):
        return sum((client.spent for client in self.clients), Decimal(0))

    def complete(self, identity, request):
        if self.attempts >= CALL_CAP or self.spent + RESERVATION > CREDIT_CAP:
            raise RuntimeError("Cross-record global allocation exhausted")
        current = self.clients[-1]
        if current.attempts >= 120 or current.spent + RESERVATION > Decimal("20"):
            current = Client(*self.args)
            self.clients.append(current)
        return current.complete(identity, request)


def build_index(case, episode):
    start = perf_counter_ns()
    schemas, results = case["tool_schemas"], case["tool_results"]
    joined_schema, rows = memory.join(schemas, results)
    _, _, owner = base.selected(joined_schema, rows)
    by_key = {}
    for item in results:
        by_key.setdefault(item["data"]["workflow_key"], []).append(item)
    index = {base.value_at(row, owner): compact(by_key[row["workflow_key"]]) for row in rows}
    if len(index) != len(rows):
        raise ValueError("Index owner collision")
    index_bytes = bytes_len(index)
    details = {"cpu_ns": perf_counter_ns() - start,
               "source_bytes_read": bytes_len(schemas) + bytes_len(results),
               "memory_bytes_written": index_bytes}
    for arm in ("indexed_raw", "indexed_projected"):
        add_details(episode["local"], arm, details)
    episode["index"] = index
    episode["index_bytes"] = index_bytes


def prepare_memories(client, case, directory):
    cid = case["id"]
    schemas, results, candidates = case["tool_schemas"], case["tool_results"], case["candidate_ids"]
    episode = {"case_id": cid, "family": case["family"], "memories": {},
               "local": {arm: meter() for arm in ARMS}, "checks": {}, "infeasible": {}}
    for arm in ("prompt", "structured"):
        request = parent_request(case, arm)
        add(episode["local"], arm, bytes_read=bytes_len(request["observation"]))
        answer = client.complete(cid + "-" + arm + "-parent", request)
        parent, bounds = admit(answer, PARENT_CAP, episode["local"], arm)
        episode["memories"][arm] = {"parent": parent, "parent_bounds": bounds}
        if arm == "structured":
            # This one physical parent call belongs to both hypothetical methods.
            add(episode["local"], "checked", **episode["local"]["structured"])

    auto_parent = auto_child = ""
    try:
        auto_parent, details = memory.project(schemas, results)
        add_details(episode["local"], "automatic", details)
        verdict = memory.check(auto_parent, schemas, results)
        add_details(episode["local"], "automatic", verdict)
        episode["checks"]["automatic_parent"] = verdict
        if not verdict["passed"]:
            raise ValueError("Automatic parent failed certificate")
        auto_child, details = memory.select(auto_parent, candidates)
        add_details(episode["local"], "automatic", details)
        verdict, expected, details = memory.check_child(auto_child, auto_parent, candidates, schemas)
        add_details(episode["local"], "automatic", verdict)
        add_details(episode["local"], "automatic", details)
        episode["checks"]["automatic_child"] = verdict
        if not verdict["passed"]:
            raise ValueError("Automatic child failed certificate")
    except (ValueError, KeyError) as error:
        episode["infeasible"]["automatic"] = str(error)
        auto_parent = auto_child = ""
    episode["memories"]["automatic"] = {"parent": auto_parent, "child": auto_child}

    parent_verdict = memory.check(episode["memories"]["structured"]["parent"], schemas, results)
    add_details(episode["local"], "checked", parent_verdict)
    episode["checks"]["structured_parent"] = parent_verdict
    fallback_parent = not parent_verdict["passed"]
    checked_parent = auto_parent if fallback_parent else episode["memories"]["structured"]["parent"]
    if fallback_parent:
        # In a standalone checked system this fallback computation is not free.
        auto_meter = episode["local"]["automatic"]
        add(episode["local"], "checked", **auto_meter)
    episode["checks"]["parent_fallback"] = fallback_parent
    episode["memories"]["checked"] = {"parent": checked_parent}

    for arm, parent in (("prompt", episode["memories"]["prompt"]["parent"]),
                        ("structured", episode["memories"]["structured"]["parent"]),
                        ("checked", checked_parent)):
        request = child_request(case, arm, parent)
        add(episode["local"], arm, bytes_read=bytes_len(request["observation"]))
        answer = client.complete(cid + "-" + arm + "-child", request)
        proposed, bounds = admit(answer, CHILD_CAP, episode["local"], arm)
        episode["memories"][arm]["child_bounds"] = bounds
        if arm != "checked":
            episode["memories"][arm]["child"] = proposed
        else:
            if checked_parent:
                try:
                    verdict, expected, details = memory.check_child(proposed, checked_parent, candidates, schemas)
                    add_details(episode["local"], "checked", verdict)
                    add_details(episode["local"], "checked", details)
                    episode["checks"]["checked_child_proposal"] = verdict
                    episode["checks"]["child_fallback"] = not verdict["passed"]
                    episode["memories"][arm]["child"] = proposed if verdict["passed"] else expected
                    if not verdict["passed"]:
                        add(episode["local"], "checked", bytes_read=bytes_len(expected), bytes_written=bytes_len(expected))
                except (ValueError, KeyError) as error:
                    episode["infeasible"]["checked"] = str(error)
                    episode["memories"][arm]["child"] = ""
            else:
                episode["infeasible"]["checked"] = "No certified parent"
                episode["memories"][arm]["child"] = ""

    try:
        direct_parent, details = direct.project(case["family"], schemas, results)
        add_details(episode["local"], "direct", details)
        direct_child, details = direct.child(direct_parent, candidates)
        add_details(episode["local"], "direct", details)
    except (ValueError, KeyError) as error:
        episode["infeasible"]["direct"] = str(error)
        direct_parent = direct_child = ""
    episode["memories"]["direct"] = {"parent": direct_parent, "child": direct_child}
    build_index(case, episode)
    save(directory / (cid + "-episode.json"), episode)
    return episode


def retained_for(arm, case, episode, future):
    local = episode["local"]
    if arm in ("prompt", "structured", "checked", "automatic", "direct"):
        result = episode["memories"][arm]["child"]
        add(local, arm, bytes_read=bytes_len(result))
        return result
    if arm in ("indexed_raw", "indexed_projected"):
        start = perf_counter_ns()
        raw = episode["index"][future["target"]]
        add(local, arm, cpu_ns=perf_counter_ns() - start, bytes_read=bytes_len(raw))
        if arm == "indexed_raw":
            return raw
        group = json.loads(raw)
        projected, details = memory.project(case["tool_schemas"], group)
        add_details(local, arm, details)
        return projected
    if arm == "full":
        start = perf_counter_ns()
        result = compact(case["tool_results"])
        add(local, arm, cpu_ns=perf_counter_ns() - start, bytes_read=bytes_len(result),
            bytes_written=bytes_len(result))
        return result
    raise ValueError("Unknown arm")


def launch(directory, executable, global_instructions):
    if directory.exists():
        raise ValueError("Output directory exists; never resume or retry implicitly")
    paths, fixture_manifest = fixture_paths()
    frozen = fingerprints()
    audit_path = ROOT / "experiments/dependency_memory/results/luna6_revision_2026-09-22/preflight.json"
    audit = json.loads(audit_path.read_text(encoding="utf-8"))
    if audit.get("isolation_passed") is not True:
        raise ValueError("Fresh-thread isolation audit absent")
    dev = json.loads((Path(__file__).parent / "fixtures/development-escrow-61011.json").read_text(encoding="utf-8"))
    loopback = run_case(str(executable), global_instructions.read_text(encoding="utf-8"),
                        "final_message", parent_request(dev, "structured"))
    directory.mkdir(parents=True)
    (directory / "calls").mkdir()
    audit["cross_record_loopback"] = loopback
    save(directory / "preflight.json", audit)
    save(directory / "manifest.json", {"version": "cross_record_v1", "status": "frozen-before-evaluation-answers",
        "case_ids": [path.stem for path in paths], "fingerprints": frozen,
        "implementation_commit": fixture_manifest["implementation_commit"],
        "model": "gpt-6-luna", "effort": "medium", "scheduled_calls": CALL_SCHEDULE,
        "call_cap": CALL_CAP, "planning_credit_cap": str(CREDIT_CAP),
        "parent_cap": PARENT_CAP, "child_cap": CHILD_CAP, "arms": ARMS,
        "prompt_guidance": PROMPT_GUIDANCE, "structured_guidance": STRUCTURED_GUIDANCE,
        "prior_preflight_sha256": sha256(audit_path.read_bytes()).hexdigest()})
    client = BudgetedClient(executable, global_instructions, directory, audit)
    try:
        for path in paths:
            case = json.loads(path.read_text(encoding="utf-8"))
            if case["split"] != "evaluation" or case["family"] not in EVAL or len(case["futures"]) != 3:
                raise ValueError("Frozen case shape changed")
            episode = prepare_memories(client, case, directory)
            episode["decisions"] = []
            for future in case["futures"]:
                arms = list(ARMS)
                random.Random(future["id"] + ":frozen-order").shuffle(arms)
                for arm in arms:
                    retained = retained_for(arm, case, episode, future)
                    identity = future["id"] + "-" + arm
                    client.complete(identity, execution_request(case, retained, future))
                    episode["decisions"].append({"identity": identity, "arm": arm,
                        "future_id": future["id"], "memory_bytes": bytes_len(retained),
                        "truth": truth(case, future)})
                    save(directory / (case["id"] + "-episode.json"), episode)
        if fingerprints() != frozen or client.attempts != CALL_SCHEDULE:
            raise ValueError("Source drift or incomplete fixed schedule")
        save(directory / "completion.json", {"status": "complete", "calls": client.attempts,
                                           "planning_credits": str(client.spent)})
    except Exception as error:
        save(directory / "completion.json", {"status": "stopped", "calls": client.attempts,
            "planning_credits_settled": str(client.spent), "error_type": type(error).__name__,
            "error": str(error)[:160]})
        raise


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--launch", action="store_true")
    parser.add_argument("--directory", required=True, type=Path)
    parser.add_argument("--executable", required=True, type=Path)
    parser.add_argument("--global-instructions", required=True, type=Path)
    args = parser.parse_args()
    if not args.launch:
        parser.error("Explicit --launch required")
    launch(args.directory.resolve(), args.executable.resolve(), args.global_instructions.resolve())


if __name__ == "__main__":
    main()
