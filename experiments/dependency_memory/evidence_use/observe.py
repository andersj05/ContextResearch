"""Capture actual offline repository checks at a clean, pinned checkpoint.

This collector is evaluator-side. The final-decision guard never imports it.
Its outputs are inspected local development evidence, not private held-out data.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import subprocess
import sys
from time import perf_counter_ns

ROOT = Path(__file__).resolve().parents[3]
COMMANDS = (
    ("tests", ("-m", "unittest", "discover", "-s", "experiments/dependency_memory", "-v")),
    ("repository", ("scripts/validate_context_repo.py",)),
    ("paper", ("scripts/build_paper.py",)),
)
ARTIFACTS = ("build/paper/manuscript.md", "build/paper/preview.html")


def wire(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()


def git(*arguments):
    result = subprocess.run(["git", "-c", "safe.directory=" + ROOT.as_posix(), *arguments], cwd=ROOT,
                            capture_output=True, check=True)
    return result.stdout.decode("utf-8").strip()


def source():
    if git("status", "--porcelain"):
        raise ValueError("Checkpoint capture requires a clean committed source tree")
    return {"commit": git("rev-parse", "HEAD"), "tree": git("rev-parse", "HEAD^{tree}")}


def capture(destination, episode, checkpoint):
    destination = Path(destination).resolve()
    allowed = (ROOT / "build").resolve()
    if not destination.is_relative_to(allowed) or destination == allowed:
        raise ValueError("New raw capture must be inside this repository's ignored build directory")
    if destination.exists():
        raise ValueError("Refuse to overwrite an existing checkpoint")
    pinned = source()
    destination.mkdir(parents=True)
    manifest = {"version": "evidence_use_observed_checkpoint_v1", "episode": episode, "checkpoint": checkpoint,
                "origin": "observed_local_development_task", "inspection": "author_and_implementer_observed",
                "started_at_utc": datetime.now(timezone.utc).isoformat(), "source": pinned,
                "python": sys.version, "records": [], "model_calls": 0, "held_out": False}
    for check, arguments in COMMANDS:
        if source() != pinned:
            raise ValueError("Source changed before command execution")
        argv = [sys.executable, *arguments]
        start = perf_counter_ns()
        observed = subprocess.run(argv, cwd=ROOT, capture_output=True, timeout=300)
        elapsed = perf_counter_ns() - start
        streams = {}
        for name, raw in (("stdout", observed.stdout), ("stderr", observed.stderr)):
            filename = check + "." + name + ".txt"
            (destination / filename).write_bytes(raw)
            streams[name] = {"path": filename, "bytes": len(raw), "sha256": hashlib.sha256(raw).hexdigest()}
        artifacts = {}
        if check == "paper" and observed.returncode == 0:
            artifacts = {name: hashlib.sha256((ROOT / name).read_bytes()).hexdigest() for name in ARTIFACTS}
            artifact_directory = destination / "artifacts"
            artifact_directory.mkdir()
            for name in ARTIFACTS:
                (artifact_directory / Path(name).name).write_bytes((ROOT / name).read_bytes())
        record = {"check": check, "snapshot": pinned["tree"], "returncode": observed.returncode,
                  "artifacts": artifacts, "argv": argv, "elapsed_ns": elapsed, **streams}
        record["run_id"] = hashlib.sha256(wire(record)).hexdigest()
        manifest["records"].append(record)
        (destination / "capture.json").write_bytes(wire(manifest) + b"\n")
        try:
            unchanged = source() == pinned
        except ValueError:
            unchanged = False
        if not unchanged:
            manifest.update(status="incomplete_source_changed", error="Source changed during command execution")
            (destination / "capture.json").write_bytes(wire(manifest) + b"\n")
            raise ValueError("Source changed during command execution; raw outputs retained")
        print(f"Observed {check}: exit {observed.returncode}; source {pinned['commit'][:12]}", flush=True)
    manifest["completed_at_utc"] = datetime.now(timezone.utc).isoformat()
    manifest["status"] = "complete"
    (destination / "capture.json").write_bytes(wire(manifest) + b"\n")
    return manifest


def verify(directory, *, artifacts_required=True):
    """Portable receipts omit generated previews; verify those at registration."""
    directory = Path(directory)
    manifest = json.loads((directory / "capture.json").read_text(encoding="utf-8"))
    if (manifest.get("version") != "evidence_use_observed_checkpoint_v1" or manifest.get("status") != "complete"
            or manifest.get("model_calls") != 0 or manifest.get("held_out") is not False
            or [r["check"] for r in manifest["records"]] != [c for c, _ in COMMANDS]):
        raise ValueError("Incomplete or misclassified development checkpoint")
    if git("rev-parse", manifest["source"]["commit"] + "^{tree}") != manifest["source"]["tree"]:
        raise ValueError("Pinned source commit/tree mismatch")
    for row, (check, arguments) in zip(manifest["records"], COMMANDS):
        if (row["snapshot"] != manifest["source"]["tree"] or row["argv"][1:] != list(arguments)
                or type(row["returncode"]) is not int or type(row["elapsed_ns"]) is not int or row["elapsed_ns"] < 0
                or hashlib.sha256(wire({k: v for k, v in row.items() if k != "run_id"})).hexdigest() != row["run_id"]):
            raise ValueError("Command/receipt identity mismatch")
        for stream in ("stdout", "stderr"):
            item = row[stream]
            if item["path"] != check + "." + stream + ".txt":
                raise ValueError("Unexpected output path")
            raw = (directory / item["path"]).read_bytes()
            if len(raw) != item["bytes"] or hashlib.sha256(raw).hexdigest() != item["sha256"]:
                raise ValueError("Observed output bytes changed")
        if check == "paper" and row["returncode"] == 0:
            if set(row["artifacts"]) != set(ARTIFACTS):
                raise ValueError("Incomplete observed artifact bindings")
            if artifacts_required:
                for name, expected in row["artifacts"].items():
                    if hashlib.sha256((directory / "artifacts" / Path(name).name).read_bytes()).hexdigest() != expected:
                        raise ValueError("Observed artifact bytes changed")
    return manifest


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("destination", type=Path)
    parser.add_argument("--episode", required=True)
    parser.add_argument("--checkpoint", required=True, choices=("A", "B"))
    args = parser.parse_args()
    capture(args.destination, args.episode, args.checkpoint)
    verify(args.destination)


if __name__ == "__main__":
    main()
