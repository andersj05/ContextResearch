"""Opt-in, fixed 72-call matched comparison on frozen evaluation traces."""
from __future__ import annotations

import argparse
from hashlib import sha256
import json
from pathlib import Path
import random
import sys
from time import process_time_ns

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "experiments/dependency_memory"))

from luna6_revision.audit import run_case
from luna6_revision import study as prior_study
from luna6_revision.transport import Client, RESERVATION, save
from .cases import CHILD_CAP, EVAL_SEEDS, FAMILIES, PARENT_CAP, RULES, compact, truth
from .memory import check, decode, direct, project, select

ARMS = ("prompt", "automatic", "direct", "indexed", "full")
EXEC_SCHEMA = {"type": "object", "properties": {
    "action": {"type": "string", "enum": ["dispatch", "close", "retry", "hold", "handoff", "publish"]},
    "target_id": {"type": "string"}, "work": {"type": "array", "items": {"type": "string"}}},
    "required": ["action", "target_id", "work"], "additionalProperties": False}
PROMPT_GUIDANCE = (
    "The complete public decision rule and output schema will be supplied again at execution. "
    "Use the whole memory allowance for instance-specific facts. Preserve complete opaque "
    "identifiers, state values, and who or what each reference covers. Do not shorten IDs "
    "or replace a scoped reference with a generic ready/done claim. Only the memory string "
    "survives this boundary. Return a JSON object with that memory string. "
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


def memory_request(case, stage, observation, cap):
    return prior_study.request(stage, PROMPT_GUIDANCE + f"Limit memory to {cap} UTF-8 bytes. " +
                               ("Keep enough for any later target. " if stage == "parent" else
                                "Retain only the named candidates. ") + RULES[case["family"]], observation)


def execution_request(case, memory, future):
    return prior_study.request("execute", "Use only the supplied memory, target, and late event. " +
                               RULES[case["family"]] +
                               " Memory may be a field/rows table or prose. Return one exact terminal decision. Do not call tools.",
                               {"memory": memory, "target": future["target"], "late_event": future["event"]},
                               EXEC_SCHEMA)


def bounded_complete(client, identity, request):
    if client.attempts >= 80 or client.spent + RESERVATION > 10:
        raise RuntimeError("New study call or planning-credit ceiling reached")
    return client.complete(identity, request)


def prepare_memories(client, case, directory):
    episode = {"case_id": case["id"], "family": case["family"], "memories": {}, "local": {}}
    cid = case["id"]
    response = bounded_complete(client, cid + "-prompt-parent", memory_request(case, "parent",
        {"tool_schema": case["tool_schema"], "tool_results": case["tool_results"]}, PARENT_CAP))
    prompt_parent, parent_bounds = prior_study.admit(response, PARENT_CAP)
    response = bounded_complete(client, cid + "-prompt-child", memory_request(case, "child",
        {"previous_memory": prompt_parent, "candidates": case["candidates"]}, CHILD_CAP))
    prompt_child, child_bounds = prior_study.admit(response, CHILD_CAP)
    episode["memories"]["prompt"] = {"parent": prompt_parent, "child": prompt_child,
        "parent_bounds": parent_bounds, "child_bounds": child_bounds}

    start = process_time_ns()
    auto_parent = project(case["tool_schema"], case["tool_results"], cap=PARENT_CAP)
    extraction_ns = process_time_ns() - start
    parent_check = check(auto_parent, case["tool_schema"], case["tool_results"])
    if not parent_check["passed"]:
        raise ValueError("Automatic parent check failed")
    start = process_time_ns()
    auto_child = select(auto_parent, case["candidates"], cap=CHILD_CAP)
    selection_ns = process_time_ns() - start
    # The second checker receives only the retained parent and public candidate pair.
    parent_selected = decode(select(auto_parent, case["candidates"], cap=CHILD_CAP))
    child_check = check(auto_child, case["tool_schema"], parent_selected)
    if not child_check["passed"]:
        raise ValueError("Automatic child check failed")
    episode["memories"]["automatic"] = {"parent": auto_parent, "child": auto_child}
    episode["local"]["automatic"] = {"cpu_ns": extraction_ns + parent_check["cpu_ns"] + selection_ns + child_check["cpu_ns"],
        "bytes_read": len(compact(case["tool_results"]).encode()) + parent_check["source_bytes_read"] +
                      parent_check["memory_bytes_read"] + len(auto_parent.encode()) +
                      child_check["source_bytes_read"] + child_check["memory_bytes_read"],
        "parent_check": parent_check, "child_check": child_check}

    start = process_time_ns()
    direct_parent = direct(case["family"], case["tool_results"], cap=PARENT_CAP)
    direct_child = select(direct_parent, case["candidates"], cap=CHILD_CAP)
    direct_ns = process_time_ns() - start
    episode["memories"]["direct"] = {"parent": direct_parent, "child": direct_child}
    episode["local"]["direct"] = {"cpu_ns": direct_ns,
        "bytes_read": len(compact(case["tool_results"]).encode()) + len(direct_parent.encode())}
    save(directory / (cid + "-episode.json"), episode)
    return episode


def launch(directory, executable, global_instructions):
    if directory.exists():
        raise ValueError("Output directory already exists; never resume or retry implicitly")
    paths = fixture_paths()
    frozen = fingerprints()
    prior_audit_path = ROOT / "experiments/dependency_memory/results/luna6_revision_2026-09-22/preflight.json"
    audit = json.loads(prior_audit_path.read_text(encoding="utf-8"))
    if audit.get("isolation_passed") is not True:
        raise ValueError("Prior isolation audit absent")
    development = json.loads((Path(__file__).parent / "fixtures/development-retry-41011.json").read_text())
    extra = run_case(str(executable), global_instructions.read_text(encoding="utf-8"), "final_message",
                     memory_request(development, "parent", {"tool_schema": development["tool_schema"],
                                                        "tool_results": development["tool_results"]}, PARENT_CAP))
    directory.mkdir(parents=True)
    (directory / "calls").mkdir()
    audit["new_request_loopback"] = extra
    save(directory / "preflight.json", audit)
    manifest = {"version": "schema_checks_v1", "status": "frozen-before-evaluation-answers",
        "case_ids": [path.stem for path in paths], "fingerprints": frozen,
        "model": "gpt-6-luna", "reasoning_effort": "medium", "scheduled_calls": 72,
        "call_cap": 80, "planning_credit_cap": "10", "parent_cap": PARENT_CAP, "child_cap": CHILD_CAP,
        "prior_preflight_sha256": sha256(prior_audit_path.read_bytes()).hexdigest(),
        "prompt_guidance": PROMPT_GUIDANCE, "arms": ARMS}
    save(directory / "manifest.json", manifest)
    client = Client(executable, global_instructions, directory, audit)
    try:
        for path in paths:
            case = json.loads(path.read_text(encoding="utf-8"))
            if case["split"] != "evaluation" or case["family"] not in FAMILIES or len(case["futures"]) != 2:
                raise ValueError("Frozen case shape changed")
            episode = prepare_memories(client, case, directory)
            episode["decisions"] = []
            for future in case["futures"]:
                arms = list(ARMS)
                random.Random(future["id"] + ":frozen-order").shuffle(arms)
                for arm in arms:
                    recovery_cpu_ns = 0
                    if arm in ("prompt", "automatic", "direct"):
                        memory = episode["memories"][arm]["child"]
                        recovery_bytes = 0
                    elif arm == "indexed":
                        start = process_time_ns()
                        target = next(row for row in case["tool_results"] if future["target"] in row.values())
                        memory = compact(target)
                        recovery_bytes = len(memory.encode())
                        recovery_cpu_ns = process_time_ns() - start
                    else:
                        start = process_time_ns()
                        memory = compact(case["tool_results"])
                        recovery_bytes = len(memory.encode())
                        recovery_cpu_ns = process_time_ns() - start
                    identity = future["id"] + "-" + arm
                    bounded_complete(client, identity, execution_request(case, memory, future))
                    episode["decisions"].append({"identity": identity, "arm": arm, "future_id": future["id"],
                        "recovery_bytes": recovery_bytes, "recovery_cpu_ns": recovery_cpu_ns,
                        "memory_bytes": len(memory.encode())})
                    save(directory / (case["id"] + "-episode.json"), episode)
        if fingerprints() != frozen:
            raise ValueError("Study code or frozen fixture drift during launch")
        if client.attempts != 72:
            raise ValueError("Incomplete fixed schedule")
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
