"""Load registered command evidence and generate separately stored evaluator data."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from experiments.dependency_memory.evidence_use.observe import verify
from experiments.dependency_memory.workflow_eval.grader import CHECKS, expected_answer, validate_records, validate_task, wire
from experiments.dependency_memory.workflow_eval.packet import direct_records
from .views import PARENT_CAP, CHILD_CAP, actor_view

HERE = Path(__file__).parent


def read(path):
    return json.loads(path.read_text(encoding="utf-8"))


def load_episode(directory):
    directory = Path(directory)
    observed = []
    for checkpoint in ("A", "B"):
        root = directory / checkpoint
        capture = verify(root, artifacts_required=False)
        if capture["checkpoint"] != checkpoint or capture["origin"] != "observed_local_development_task":
            raise ValueError("Wrong checkpoint or observation origin")
        records = []
        for row in capture["records"]:
            public = {k: row[k] for k in ("check", "snapshot", "run_id", "returncode", "artifacts", "argv")}
            for stream in ("stdout", "stderr"):
                public[stream] = (root / row[stream]["path"]).read_bytes().decode("utf-8")
            records.append(public)
        validate_records(records)
        observed.append((capture, records))
    if observed[0][0]["episode"] != observed[1][0]["episode"]:
        raise ValueError("Checkpoints belong to different tasks")
    a, b = (pair[0] for pair in observed)
    if a["completed_at_utc"] > b["started_at_utc"]:
        raise ValueError("Checkpoints do not preserve observed order")
    task = {"snapshot": b["source"]["tree"], "required_checks": list(CHECKS),
            "artifacts": b["records"][-1]["artifacts"]}
    validate_task(task)
    return {"id": directory.name, "task_name": a["episode"], "origin": "observed_single_repository_development_task",
            "initial": observed[0][1], "between": observed[1][1], "scope": list(CHECKS), "task": task,
            "source_commits": [a["source"]["commit"], b["source"]["commit"]], "held_out": False,
            "inspection": "author_and_implementer_observed"}


def evaluator_manifest(episode):
    full = episode["initial"] + episode["between"]
    parent = direct_records(episode["initial"])
    child = direct_records(parent + episode["between"], episode["scope"])
    return {"version": "single_repository_evaluator_manifest_v1", "episode": episode["id"],
            "source_commits": episode["source_commits"], "expected": expected_answer(full, episode["task"]),
            "model_calls": 0, "model_result": "unperformed", "held_out": False,
            "direct_all_possible_snapshots_diagnostic": {"parent_bytes": len(wire(parent)), "child_bytes": len(wire(child)),
                "parent_cap": PARENT_CAP, "child_cap": CHILD_CAP,
                "parent_fits": len(wire(parent)) <= PARENT_CAP, "child_fits": len(wire(child)) <= CHILD_CAP,
                "meaning": "Feasibility if all observed source snapshots remain possible; not a measured actor result or a launch task-distribution contract."}}


def validate_registered():
    ledger = read(HERE / "ledger.json")
    if (ledger["version"] != "single_repository_intake_v1" or ledger["repository"] != "ContextResearch"
            or ledger["model_calls"] != 0 or ledger["private_held_out_episodes"] != 0):
        raise ValueError("Invalid intake scope or outcome claim")
    completed = []
    expected_files = {checkpoint + "/" + filename for checkpoint in ("A", "B")
                      for filename in ("capture.json", "tests.stdout.txt", "tests.stderr.txt",
                                       "repository.stdout.txt", "repository.stderr.txt", "paper.stdout.txt", "paper.stderr.txt")}
    for index, item in enumerate(ledger["episodes"], 1):
        if item["sequence"] != index or item["id"] != f"E{index:04d}":
            raise ValueError("Nonconsecutive intake ledger")
        if item["split"] != "development" or item["status"] not in {
                "awaiting_first_checkpoint", "awaiting_second_checkpoint", "capture_incomplete", "excluded", "complete"}:
            raise ValueError("Unsupported intake split or task disposition")
        if item["status"] == "excluded" and not item["exclusion_reason"]:
            raise ValueError("An excluded task needs an explicit reason")
        if item["status"] != "complete":
            continue
        if set(item["sha256"]) != expected_files:
            raise ValueError("Completed task must pin both complete command checkpoints")
        directory = HERE / "development" / item["id"]
        for name, expected in item["sha256"].items():
            path = directory / name
            if not path.resolve().is_relative_to(directory.resolve()) or hashlib.sha256(path.read_bytes()).hexdigest() != expected:
                raise ValueError("Registered command evidence changed")
        episode = load_episode(directory)
        expected_manifest = evaluator_manifest(episode)
        if expected_manifest != read(HERE / "evaluator" / (item["id"] + ".json")):
            raise ValueError("Evaluator manifest differs from raw observed receipts")
        parent = actor_view(episode, "parent")
        child = actor_view(episode, "child", "[]")
        final = actor_view(episode, "final", "[]")
        if set(parent) != {"tool_observations"} or set(child) != {"previous_memory", "new_observations", "scope"} or set(final) != {"memory", "final_public_state"}:
            raise ValueError("Unexpected actor view fields")
        completed.append(episode)
    return {"status": "PASS", "registered_tasks": len(ledger["episodes"]),
            "incomplete_tasks": sum(item["status"].startswith("awaiting_") or item["status"] == "capture_incomplete"
                                    for item in ledger["episodes"]),
            "excluded_tasks": sum(item["status"] == "excluded" for item in ledger["episodes"]),
            "observed_development_episodes": len(completed),
            "observed_commands": sum(len(e["initial"]) + len(e["between"]) for e in completed),
            "prospective_evaluation_episodes": 0, "private_held_out_episodes": 0, "model_calls": 0,
            "independent_grader_review": "pending", "launch_ready": False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write-evaluator-manifests", action="store_true")
    args = parser.parse_args()
    if args.write_evaluator_manifests:
        for item in read(HERE / "ledger.json")["episodes"]:
            if item["status"] == "complete":
                value = evaluator_manifest(load_episode(HERE / "development" / item["id"]))
                (HERE / "evaluator" / (item["id"] + ".json")).write_bytes(wire(value) + b"\n")
    print(json.dumps(validate_registered(), indent=2))


if __name__ == "__main__":
    main()
