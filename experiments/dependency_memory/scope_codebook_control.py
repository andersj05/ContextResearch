"""Separate zero-model serialization control; does not alter the frozen Luna method."""
import hashlib
from itertools import combinations
import json
from pathlib import Path
from time import perf_counter_ns, process_time_ns

from experiments.dependency_memory.workflow_replay import evidence
from experiments.dependency_memory.scope_inference import codec, study
from experiments.dependency_memory.scope_inference.run import RESULTS as LAUNCH, stable, verify

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
OUTPUT = HERE / "results/scope_codebook_control_2026-10-01.json"


def encode_rows(records):
    return [{"case_id": row["case_id"], "worker": row["worker"], "request_sha256": row["request_sha256"],
             "data": evidence.encode_fields(evidence.project(row))} for row in records]


def child_rows(parent_memory, workers):
    # Empty/infeasible parent is final: no access to deleted original records.
    rows = json.loads(parent_memory) if parent_memory else []
    return [row for row in rows if row["worker"] in workers]


def readout(child_memory, case_id, request_sha256, original):
    rows = json.loads(child_memory) if child_memory else []
    matches = [row for row in rows if row["case_id"] == case_id and row["request_sha256"] == request_sha256]
    if len(matches) != 1:
        return ["unknown", None, None]
    return evidence.original_decision(evidence.decode_fields(matches[0]["data"]), original)


def analysis():
    manifest = json.loads((LAUNCH / "manifest.json").read_text())
    verify(manifest)
    original = evidence.historical_classifier()
    records, provenance = evidence.load_snapshot()
    cpu, wall = process_time_ns(), perf_counter_ns()
    encoded = encode_rows(records)
    parent, admission = codec.admit(encoded, codec.PARENT_CAP)
    children, queries, correct = [], 0, 0
    for workers in combinations(range(4), 2):
        child, child_admission = codec.admit(child_rows(parent, workers), codec.CHILD_CAP)
        for query in records:
            if query["worker"] in workers:
                observed = readout(child, query["case_id"], query["request_sha256"], original)
                correct += observed == evidence.original_decision(query, original)
                queries += 1
        children.append({"workers": list(workers), **child_admission})
    catalog_cases, disagreements = 0, 0
    for row in study.control_catalog():
        decoded = evidence.decode_fields(evidence.encode_fields(evidence.project(row)))
        disagreements += evidence.original_decision(row, original) != evidence.original_decision(decoded, original)
        catalog_cases += 1
    baselines = json.loads((LAUNCH / "offline-controls.json").read_text())
    return {"version": "scope_schema_serialization_control_v1", "date": "2026-10-01",
        "evidence_class": "separate pre-generation offline control; constructed timing on eight inspected records",
        "source_sha256": {p.relative_to(ROOT).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest() for p in
            (Path(__file__), HERE / "test_scope_codebook_control.py", HERE / "workflow_replay/evidence.py")},
        "frozen_launch_manifest_sha256": hashlib.sha256((LAUNCH / "manifest.json").read_bytes()).hexdigest(),
        "historical_record_sha256": [row["record_sha256"] for row in provenance],
        "schema_source": "Existing public evidence.SCHEMA/encode_fields/decode_fields; unchanged since the earlier replay.",
        "schema_instance_dependent": False, "catalog_cases": catalog_cases, "catalog_disagreements": disagreements,
        "parent": admission, "children": children, "final_queries": queries, "correct": correct,
        "hand_json": stable(baselines["hand"]["staged"]), "cached_results": stable(baselines["cached"]["staged"]),
        "measurement": {"cpu_ns": process_time_ns() - cpu, "wall_ns": perf_counter_ns() - wall,
                        "priced_total_cost": None}, "new_model_calls": 0,
        "limits": "No information-theoretic obstruction inferred from one JSON encoding. Fixed public codebook is not new. No model gain, natural-task prevalence or production savings."}


def main():
    result = analysis()
    OUTPUT.write_bytes((json.dumps(result, indent=2, sort_keys=True) + "\n").encode())
    print(json.dumps({k: result[k] for k in ("catalog_cases", "catalog_disagreements", "parent", "children", "correct", "final_queries", "new_model_calls")}, indent=2))


if __name__ == "__main__":
    main()
