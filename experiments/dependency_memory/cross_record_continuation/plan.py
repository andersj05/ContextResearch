"""Freeze the never-dispatched suffix without reading model response contents."""
from __future__ import annotations

from hashlib import sha256
import json
from pathlib import Path
import random

from experiments.dependency_memory.cross_record.run import ARMS, ROOT, fixture_paths, fingerprints

ORIGINAL = ROOT / "experiments/dependency_memory/results/cross_record_2026-09-22"
PLAN_PATH = Path(__file__).parent / "plan.json"


def schedule():
    ordered = []
    for path in fixture_paths()[0]:
        case = json.loads(path.read_text(encoding="utf-8"))
        cid = case["id"]
        ordered += [cid + suffix for suffix in (
            "-prompt-parent", "-structured-parent", "-prompt-child",
            "-structured-child", "-checked-child")]
        for future in case["futures"]:
            arms = list(ARMS)
            random.Random(future["id"] + ":frozen-order").shuffle(arms)
            ordered += [future["id"] + "-" + arm for arm in arms]
    if len(ordered) != 348 or len(set(ordered)) != 348:
        raise ValueError("Original schedule changed")
    return ordered


def original_files():
    paths = list((ORIGINAL / "calls").glob("*.json"))
    paths += list(ORIGINAL.glob("*-episode.json"))
    paths += [ORIGINAL / name for name in ("manifest.json", "completion.json", "preflight.json")]
    return {path.relative_to(ORIGINAL).as_posix(): sha256(path.read_bytes()).hexdigest()
            for path in sorted(paths)}


def make_plan():
    manifest = json.loads((ORIGINAL / "manifest.json").read_text(encoding="utf-8"))
    completion = json.loads((ORIGINAL / "completion.json").read_text(encoding="utf-8"))
    if manifest["fingerprints"] != fingerprints() or completion["status"] != "stopped":
        raise ValueError("Original run not frozen or not stopped")
    ordered = schedule()
    records = {}
    for path in (ORIGINAL / "calls").glob("*.json"):
        record = json.loads(path.read_text(encoding="utf-8"))
        identity = record["identity"]
        if identity in records or path.stem != identity:
            raise ValueError("Duplicate or mismatched original identity")
        records[identity] = record
    attempted = ordered[:len(records)]
    if len(records) != 199 or set(records) != set(attempted) or completion["calls"] != len(records):
        raise ValueError("Attempted calls are not the fixed prefix")
    failed = [identity for identity, record in records.items() if record["status"] != "completed"]
    if failed != [attempted[-1]] or records[failed[0]]["status"] != "transport_failure" or not records[failed[0]].get("dispatched"):
        raise ValueError("Unexpected original failure pattern")
    if records[failed[0]].get("error") != "Provider generation error":
        raise ValueError("Original failure reason changed")
    pending = ordered[len(records):]
    if len(pending) != 149:
        raise ValueError("Unexpected never-dispatched suffix")
    return {"version": "cross_record_continuation_v1", "original_attempts": len(records),
            "original_completed": len(records)-1, "original_failed_identity": failed[0],
            "original_files": original_files(), "original_source_fingerprints": fingerprints(),
            "ordered_pending": pending, "new_dispatch_cap": 149,
            "planning_credit_cap": "25", "unknown_failure_reservation": "7.65"}


def freeze():
    if PLAN_PATH.exists():
        raise ValueError("Continuation plan already frozen")
    PLAN_PATH.write_text(json.dumps(make_plan(), indent=2) + "\n", encoding="utf-8", newline="\n")


if __name__ == "__main__":
    freeze()
