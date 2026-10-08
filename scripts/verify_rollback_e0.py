"""Seal and independently verify the bounded, offline rollback E0 evidence."""
from __future__ import annotations

import argparse
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from experiments.dependency_memory.rollback_pilot.accounting import Identity, Usage
from experiments.dependency_memory.rollback_pilot.contexts import ByteCounter
from experiments.dependency_memory.rollback_pilot.independent_math import exhaustive_solutions
from experiments.dependency_memory.rollback_pilot.math_tasks import generate_math
from experiments.dependency_memory.rollback_pilot.offline import verify_evidence
from experiments.dependency_memory.rollback_pilot.records import digest, strict_loads, wire


ARCHIVE = "archive_manifest.json"


def inventory(folder):
    folder = Path(folder).resolve()
    result = []
    for path in sorted(folder.rglob("*")):
        if path.is_symlink() or not path.resolve().is_relative_to(folder):
            raise ValueError("archive contains a symlink or escaped path")
        if path.is_file() and path != folder / ARCHIVE:
            result.append({"path": path.relative_to(folder).as_posix(), "bytes": path.stat().st_size,
                           "sha256": digest(path.read_bytes())})
    return result


def seal(folder):
    from experiments.dependency_memory.rollback_pilot.controller import write_new
    folder = Path(folder)
    record = {"schema_version": "rollback-e0-archive-1", "kind": "controlled_scripted_engineering_evidence",
              "model_calls": 0, "verifier_source": "scripts/verify_rollback_e0.py",
              "verifier_sha256": digest(Path(__file__).read_bytes()), "files": inventory(folder)}
    write_new(folder / ARCHIVE, wire(record) + "\n")
    return record


def verify(folder, *, require_seal=True):
    folder = Path(folder)
    if require_seal:
        sealed = strict_loads((folder / ARCHIVE).read_text(encoding="utf-8"))
        if sealed["files"] != inventory(folder) or sealed["model_calls"] != 0 or sealed["verifier_sha256"] != digest(Path(__file__).read_bytes()):
            raise ValueError("E0 archive or verifier binding mismatch")
    checked = verify_evidence(folder)
    summary = strict_loads((folder / "summary.json").read_text(encoding="utf-8"))
    certificates = strict_loads((folder / "math_certificates.json").read_text(encoding="utf-8"))
    expected_certificates = []
    for task, evaluator in generate_math():
        universe, solutions = exhaustive_solutions(task.data())
        if not solutions or tuple(evaluator.data()["witness"]["values"]) not in solutions:
            raise ValueError("generated math task lacks independent feasibility")
        expected_certificates.append({"task_id": task.task_id, "public_sha256": task.hash, "enumerated_candidates": len(universe),
                                      "valid_assignments": len(solutions), "solution_set_sha256": digest(wire(sorted(solutions))),
                                      "independent_grader_agreement": True})
    if certificates != expected_certificates or summary["independently_enumerated_math_candidates"] != sum(x["enumerated_candidates"] for x in certificates):
        raise ValueError("independent E0 mathematical certificate mismatch")
    events = [strict_loads(line) for line in (folder / "scripted_controller" / "usage_events.jsonl").read_text(encoding="utf-8").splitlines()]
    by_call = {}
    if [x["seq"] for x in events] != list(range(1, len(events) + 1)):
        raise ValueError("E0 ledger event sequence changed")
    for event in events:
        by_call.setdefault(event["call_id"], []).append(event)
    for call_id, history in by_call.items():
        if [x["state"] for x in history] != ["planned", "reserved", "dispatched", "completed"]:
            raise ValueError("E0 dispatch is missing a prior reservation or completion")
        identity = Identity(**history[0]["identity"])
        if identity.key != call_id:
            raise ValueError("E0 call identity changed")
        completed = history[-1]
        usage = Usage(**completed["usage"])
        if str(usage.cost) != completed["cost_usd"]:
            raise ValueError("E0 exclusive-bucket cost mismatch")
        request = strict_loads((folder / "scripted_controller" / "requests" / (call_id + ".json")).read_text(encoding="utf-8"))
        if usage.input_tokens != ByteCounter().request(wire(request)):
            raise ValueError("E0 synthetic input accounting changed")
        response = strict_loads((folder / "scripted_controller" / "responses" / (call_id + ".json")).read_text(encoding="utf-8"))
        if response["usage"] != completed["usage"] or response["capped"] or usage.output != len(response["text"].encode()):
            raise ValueError("E0 response/usage mismatch")
    if checked["scripted_tasks"] != 12 or checked["scripted_calls"] != 144 or summary["scripted_calls"] != 144 or summary["scripted_tasks"] != 12:
        raise ValueError("E0 authored controller population changed")
    if summary["E0_engineering_acceptance"]:
        checks = strict_loads((folder / "package_checks.json").read_text(encoding="utf-8"))
        if not checks["successful"] or checks["skipped"] or checks["errors"] or checks["failures"] or checks["source_bindings"] != summary["source_bindings"]:
            raise ValueError("E0 engineering acceptance lacks passing bound checks")
        if checks["docker_image"] != summary["runtime_image"]:
            raise ValueError("E0 runtime digest differs from integration checks")
    return {**checked, "independent_math_candidates": sum(x["enumerated_candidates"] for x in certificates),
            "verified_dispatches": len(by_call), "archive_files": len(inventory(folder)),
            "model_calls": 0, "provider_spend_usd": "0"}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--directory", type=Path, required=True)
    parser.add_argument("--seal", action="store_true", help="Create one immutable archive manifest; refuses an existing seal")
    parser.add_argument("--unsealed", action="store_true", help="Verify a development directory before its final seal")
    args = parser.parse_args()
    if args.seal:
        seal(args.directory)
    print(wire(verify(args.directory, require_seal=not args.unsealed)))


if __name__ == "__main__":
    main()
