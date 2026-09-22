"""One-shot, prospectively frozen 126-call schema-transfer comparison."""
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
from .casebook import CHILD_CAP, EVAL, PARENT_CAP, RULES, compact, target
from . import direct, memory

ARMS = ("prompt", "checked", "automatic", "direct", "indexed", "full")
EXEC_SCHEMA = {"type": "object", "properties": {
    "action": {"type": "string", "enum": ["submit", "hold", "publish", "retry", "close", "promote"]},
    "target_id": {"type": "string"}, "work": {"type": "array", "items": {"type": "string"}}},
    "required": ["action", "target_id", "work"], "additionalProperties": False}
PROMPT_GUIDANCE = (
    "Only the memory string survives this boundary. The public decision rule and output schema repeat "
    "at execution. Use the allowance for instance facts across all possible later targets. Preserve "
    "every exact opaque identifier, status, and the field/record to which each reference belongs. "
    "Do not abbreviate values or collapse an approval of one artifact into generic approval. "
    "A compact table is allowed: JSON f lists full field paths and r lists rows in that order. "
    "Return {\"memory\":\"...\"}. "
)


def fixture_paths():
    folder = Path(__file__).parent / "fixtures"
    manifest = json.loads((folder / "manifest.json").read_text(encoding="utf-8"))
    paths = [folder / item["file"] for item in manifest["cases"] if item["split"] == "evaluation"]
    if len(paths) != 6:
        raise ValueError("Expected six frozen evaluation traces")
    for item in manifest["cases"]:
        path = folder / item["file"]
        if sha256(path.read_bytes()).hexdigest() != item["sha256"]:
            raise ValueError("Frozen fixture changed")
    return paths


def fingerprints():
    folder = Path(__file__).parent
    paths = list(folder.glob("*.py")) + [folder / "FROZEN_PROTOCOL.md"] + list((folder / "fixtures").glob("*.json"))
    return {path.relative_to(ROOT).as_posix(): sha256(path.read_bytes()).hexdigest() for path in sorted(paths)}


def memory_request(case, stage, observation, cap, *, checked=False):
    instruction = ("Continue from the certified bounded parent table. " if checked else "") + PROMPT_GUIDANCE
    instruction += f"Limit memory to {cap} UTF-8 bytes. "
    instruction += "Keep enough for any later target. " if stage == "parent" else "Retain only the named candidates. "
    instruction += RULES[case["family"]]
    return prior_study.request(stage, instruction, observation)


def execution_request(case, retained, future):
    instruction = ("Use only supplied memory, target and late event. Memory may be prose, one original "
                   "tool result, a list of results, or a JSON table with f=full field paths and "
                   "r=rows in that field order. Apply the event to the named target, then return one "
                   "exact terminal decision with sorted work. Do not call tools. " + RULES[case["family"]])
    return prior_study.request("execute", instruction,
        {"memory": retained, "target": future["target"], "late_event": future["event"]}, EXEC_SCHEMA)


def complete(client, identity, request):
    if client.attempts >= 132 or client.spent + RESERVATION > Decimal("10"):
        raise RuntimeError("Second-study allocation exhausted")
    return client.complete(identity, request)


def meter():
    return {"cpu_ns": 0, "bytes_read": 0}


def add(local, arm, *, cpu_ns=0, bytes_read=0):
    local[arm]["cpu_ns"] += cpu_ns
    local[arm]["bytes_read"] += bytes_read


def add_projection(local, arm, details):
    add(local, arm, cpu_ns=details["cpu_ns"], bytes_read=details["source_bytes_read"])


def add_check(local, arm, verdict):
    add(local, arm, cpu_ns=verdict["cpu_ns"],
        bytes_read=verdict["source_bytes_read"] + verdict["candidate_bytes_read"])


def add_select(local, arm, details):
    add(local, arm, cpu_ns=details["cpu_ns"], bytes_read=details["source_bytes_read"])


def admit(response, cap, local, arm):
    start = perf_counter_ns()
    retained, bounds = prior_study.admit(response, cap)
    add(local, arm, cpu_ns=perf_counter_ns() - start, bytes_read=bounds["proposed_bytes"])
    return retained, bounds


def prepare_memories(client, case, directory):
    cid = case["id"]
    source, schema, candidates = case["tool_results"], case["tool_schema"], case["candidate_ids"]
    episode = {"case_id": cid, "family": case["family"], "memories": {},
               "local": {arm: meter() for arm in ARMS}, "checks": {}, "infeasible": {}}

    response = complete(client, cid + "-prompt-parent", memory_request(case, "parent",
        {"tool_schema": schema, "tool_results": source}, PARENT_CAP))
    prompt_parent, parent_bounds = admit(response, PARENT_CAP, episode["local"], "prompt")
    # The same actual parent call is fully charged to each hypothetical model-writer method.
    add(episode["local"], "checked", cpu_ns=episode["local"]["prompt"]["cpu_ns"],
        bytes_read=episode["local"]["prompt"]["bytes_read"])
    response = complete(client, cid + "-prompt-child", memory_request(case, "child",
        {"previous_memory": prompt_parent, "candidates": candidates}, CHILD_CAP))
    prompt_child, child_bounds = admit(response, CHILD_CAP, episode["local"], "prompt")
    episode["memories"]["prompt"] = {"parent": prompt_parent, "child": prompt_child,
        "parent_bounds": parent_bounds, "child_bounds": child_bounds}

    auto_parent = auto_child = ""
    try:
        auto_parent, details = memory.project(schema, source)
        add_projection(episode["local"], "automatic", details)
        verdict = memory.check(auto_parent, schema, source)
        add_check(episode["local"], "automatic", verdict)
        episode["checks"]["automatic_parent"] = verdict
        if not verdict["passed"]:
            raise ValueError("Automatic parent failed its certificate")
        auto_child, details = memory.select(auto_parent, candidates)
        add_select(episode["local"], "automatic", details)
        bounded_rows = memory.decode(auto_child)
        start = perf_counter_ns()
        bounded_schema = memory.retained_schema(schema, auto_parent)
        add(episode["local"], "automatic", cpu_ns=perf_counter_ns() - start,
            bytes_read=len(auto_parent.encode()) + len(compact(schema).encode()))
        verdict = memory.check(auto_child, bounded_schema, bounded_rows)
        add_check(episode["local"], "automatic", verdict)
        episode["checks"]["automatic_child"] = verdict
        if not verdict["passed"]:
            raise ValueError("Automatic child failed its certificate")
    except ValueError as error:
        episode["infeasible"]["automatic"] = str(error)
        auto_parent = auto_child = ""
    episode["memories"]["automatic"] = {"parent": auto_parent, "child": auto_child}

    verdict = memory.check(prompt_parent, schema, source)
    add_check(episode["local"], "checked", verdict)
    episode["checks"]["proposed_parent"] = verdict
    if verdict["passed"]:
        checked_parent, parent_fallback = prompt_parent, False
    else:
        checked_parent, parent_fallback = auto_parent, True
        # Shared computation saves physical work, but a standalone checked arm pays for it.
        add(episode["local"], "checked", cpu_ns=episode["local"]["automatic"]["cpu_ns"],
            bytes_read=episode["local"]["automatic"]["bytes_read"])
    episode["checks"]["parent_fallback"] = parent_fallback
    response = complete(client, cid + "-checked-child", memory_request(case, "child",
        {"previous_memory": checked_parent, "candidates": candidates}, CHILD_CAP, checked=True))
    proposed_child, checked_child_bounds = admit(response, CHILD_CAP, episode["local"], "checked")
    checked_child, child_fallback = proposed_child, False
    if checked_parent:
        try:
            bounded_expected, details = memory.select(checked_parent, candidates)
            add_select(episode["local"], "checked", details)
            start = perf_counter_ns()
            bounded_schema = memory.retained_schema(schema, checked_parent)
            add(episode["local"], "checked", cpu_ns=perf_counter_ns() - start,
                bytes_read=len(checked_parent.encode()) + len(compact(schema).encode()))
            verdict = memory.check(proposed_child, bounded_schema, memory.decode(bounded_expected))
            add_check(episode["local"], "checked", verdict)
            episode["checks"]["proposed_child"] = verdict
            if not verdict["passed"]:
                checked_child, child_fallback = bounded_expected, True
        except ValueError as error:
            episode["infeasible"]["checked"] = str(error)
            checked_child, child_fallback = "", True
    else:
        episode["infeasible"]["checked"] = "No certified parent projection"
        checked_child, child_fallback = "", True
    episode["checks"]["child_fallback"] = child_fallback
    episode["memories"]["checked"] = {"parent": checked_parent, "child": checked_child,
        "child_bounds": checked_child_bounds}

    try:
        direct_parent, details = direct.project(case["family"], source)
        add_projection(episode["local"], "direct", details)
        direct_child, details = direct.child(direct_parent, candidates)
        add_select(episode["local"], "direct", details)
    except ValueError as error:
        episode["infeasible"]["direct"] = str(error)
        direct_parent = direct_child = ""
    episode["memories"]["direct"] = {"parent": direct_parent, "child": direct_child}

    # Explicit archive index construction is part of the indexed method's local cost.
    start = perf_counter_ns()
    episode["index"] = {target(case["family"], row): compact(row) for row in source}
    add(episode["local"], "indexed", cpu_ns=perf_counter_ns() - start,
        bytes_read=len(compact(source).encode()))
    save(directory / (cid + "-episode.json"), episode)
    return episode


def launch(directory, executable, global_instructions):
    if directory.exists():
        raise ValueError("Output directory already exists; never resume or retry implicitly")
    paths = fixture_paths()
    frozen = fingerprints()
    audit_path = ROOT / "experiments/dependency_memory/results/luna6_revision_2026-09-22/preflight.json"
    audit = json.loads(audit_path.read_text(encoding="utf-8"))
    if audit.get("isolation_passed") is not True:
        raise ValueError("Previous fresh-thread audit absent")
    development = json.loads((Path(__file__).parent / "fixtures/development-escrow-52011.json").read_text())
    public = memory_request(development, "parent",
        {"tool_schema": development["tool_schema"], "tool_results": development["tool_results"]}, PARENT_CAP)
    loopback = run_case(str(executable), global_instructions.read_text(encoding="utf-8"), "final_message", public)
    directory.mkdir(parents=True)
    (directory / "calls").mkdir()
    audit["schema_transfer_loopback"] = loopback
    save(directory / "preflight.json", audit)
    save(directory / "manifest.json", {"version": "schema_transfer_v1", "status": "frozen-before-evaluation-answers",
        "case_ids": [path.stem for path in paths], "fingerprints": frozen,
        "model": "gpt-6-luna", "effort": "medium", "scheduled_calls": 126,
        "call_cap": 132, "planning_credit_cap": "10", "parent_cap": PARENT_CAP,
        "child_cap": CHILD_CAP, "arms": ARMS, "prompt_guidance": PROMPT_GUIDANCE,
        "prior_preflight_sha256": sha256(audit_path.read_bytes()).hexdigest()})
    client = Client(executable, global_instructions, directory, audit)
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
                    if arm in ("prompt", "checked", "automatic", "direct"):
                        retained = episode["memories"][arm]["child"]
                        recovery_bytes = recovery_ns = 0
                    elif arm == "indexed":
                        start = perf_counter_ns()
                        retained = episode["index"][future["target"]]
                        recovery_ns = perf_counter_ns() - start
                        recovery_bytes = len(retained.encode())
                    else:
                        start = perf_counter_ns()
                        retained = compact(case["tool_results"])
                        recovery_ns = perf_counter_ns() - start
                        recovery_bytes = len(retained.encode())
                    add(episode["local"], arm, cpu_ns=recovery_ns, bytes_read=recovery_bytes)
                    identity = future["id"] + "-" + arm
                    complete(client, identity, execution_request(case, retained, future))
                    episode["decisions"].append({"identity": identity, "arm": arm,
                        "future_id": future["id"], "memory_bytes": len(retained.encode()),
                        "recovery_bytes": recovery_bytes, "recovery_cpu_ns": recovery_ns})
                    save(directory / (case["id"] + "-episode.json"), episode)
        if fingerprints() != frozen or client.attempts != 126:
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
