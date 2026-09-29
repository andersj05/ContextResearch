"""Read-only preflight and explicit version-lock creation; never dispatches models."""
from __future__ import annotations

import argparse
import hashlib
from pathlib import Path

from .grader import (CHECKS, RECEIPT_FIELDS, expected_answer, strict_json,
                     validate_records, wire)

HERE = Path(__file__).resolve().parent
LOCK = "packet-lock.json"


def read_json(path):
    return strict_json(path.read_text(encoding="utf-8"))


def hashes(directory=HERE):
    return {path.relative_to(directory).as_posix(): hashlib.sha256(path.read_bytes()).hexdigest()
            for path in sorted(directory.rglob("*"))
            if path.is_file() and "__pycache__" not in path.parts
            and path.suffix in {".py", ".md", ".json", ".txt"}
            and path.name != LOCK}


def validate_lock(directory=HERE):
    saved = read_json(directory / LOCK)
    if saved != {"packet_version": 1, "sha256": hashes(directory)}:
        raise ValueError("Packet bytes differ from the reviewed lock")
    return len(saved["sha256"])


def validate_capture(directory=HERE / "development"):
    capture = read_json(directory / "capture.json")
    if (capture["version"] != 1 or capture["split"] != "development"
            or capture["origin"] != "observed_local_commands"):
        raise ValueError("The supplied capture is local development evidence only")
    records = capture["records"]
    validate_records(records)
    if [r["check"] for r in records] != ["tests", "repository", "paper"]:
        raise ValueError("Capture must preserve the three ordered offline commands")
    commands = {
        "tests": ["python", "-m", "unittest", "discover", "-s", "experiments/dependency_memory", "-v"],
        "repository": ["python", "scripts/validate_context_repo.py"],
        "paper": ["python", "scripts/build_paper.py"],
    }
    for row in records:
        unsigned = {key: value for key, value in row.items() if key != "run_id"}
        if hashlib.sha256(wire(unsigned)).hexdigest() != row["run_id"]:
            raise ValueError("Recorded run identity differs from its content")
        if (row["argv"] != commands[row["check"]]
                or row["snapshot"] != capture["source"]["tree"]
                or type(row["elapsed_ns"]) is not int or row["elapsed_ns"] < 0):
            raise ValueError("Command/snapshot/timing mismatch")
        for stream in ("stdout", "stderr"):
            item = row[stream]
            if item["path"] != f"{row['check']}.{stream}.txt":
                raise ValueError("Unexpected capture output path")
            raw = (directory / item["path"]).read_bytes()
            if len(raw) != item["bytes"] or hashlib.sha256(raw).hexdigest() != item["sha256"]:
                raise ValueError("Raw command output changed")
    return capture


def direct_records(records, scope=CHECKS):
    """Hand-written feasibility baseline, not automatic contract inference.

    One latest receipt per (tree, check), in original relative order. This is
    deliberately a different formulation from the grader's per-task scan.
    """
    validate_records(records)
    latest = {}
    for index, row in enumerate(records):
        if row["check"] in scope:
            latest[(row["snapshot"], row["check"])] = (index, row)
    return [{key: row[key] for key in RECEIPT_FIELDS}
            for _, row in sorted(latest.values(), key=lambda value: value[0])]


def preflight(directory=HERE):
    files = validate_lock(directory)
    plan = read_json(directory / "plan.json")
    capture = validate_capture(directory / "development")
    scheduled = ((plan["proposed_development_episodes"] + plan["proposed_evaluation_episodes"])
                 * (plan["writer_calls_per_episode"] + plan["final_calls_per_episode"]))
    if scheduled != plan["proposed_max_dispatches"]:
        raise ValueError("Dispatch budget does not reconcile")
    if (plan["authorized_dispatches"] != 0 or plan["authorized_provider_charge_usd"] != 0
            or plan["evaluation_captures"] or plan["status"] != "offline_packet_only"
            or any(value is not None for value in plan["launch_gates"].values())):
        raise ValueError("Packet v1 cannot be converted into a launch by filling placeholders")
    parent = direct_records(capture["records"])
    child = direct_records(parent)
    task = {"snapshot": capture["source"]["tree"], "required_checks": list(CHECKS),
            "artifacts": capture["records"][-1]["artifacts"]}
    expected = expected_answer(capture["records"], task)
    if expected_answer(child, task) != expected:
        raise ValueError("Development direct projection changed the terminal answer")
    return {
        "packet_status": "PASS", "launch_ready": False, "locked_files": files,
        "observed_development_episodes": 1, "held_out_evaluation_episodes": 0,
        "model_calls": 0, "proposed_max_dispatches": scheduled,
        "authorized_dispatches": 0, "source_commit": capture["source"]["commit"],
        "observed_command_exit_codes": {r["check"]: r["returncode"] for r in capture["records"]},
        "source_log_bytes": sum(r[s]["bytes"] for r in capture["records"] for s in ("stdout", "stderr")),
        "direct_parent_bytes": len(wire(parent)), "direct_child_bytes": len(wire(child)),
        "parent_fits": len(wire(parent)) <= plan["parent_cap_utf8_bytes"],
        "child_fits": len(wire(child)) <= plan["child_cap_utf8_bytes"],
        "development_expected_answer": expected,
        "remaining_launch_gates": list(plan["launch_gates"]),
        "limits": ["One inspected local workflow; not external or held out.",
                   "Mutated test controls are constructed, not observed incidents.",
                   "No live runner, provider isolation, candidate comparison or total-cost result."],
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write-lock", action="store_true",
                        help="Explicitly write the integrity lock after reviewing a packet revision")
    args = parser.parse_args()
    if args.write_lock:
        (HERE / LOCK).write_bytes(wire({"packet_version": 1, "sha256": hashes()}) + b"\n")
    import json
    print(json.dumps(preflight(), indent=2))


if __name__ == "__main__":
    main()
