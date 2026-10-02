"""Separate offline finite audit and uniform-codec replay; zero model requests."""
import hashlib
from itertools import combinations
import json
from pathlib import Path
from time import perf_counter_ns, process_time_ns

from experiments.dependency_memory.scope_inference import codec, study
from experiments.dependency_memory.workflow_replay import evidence
from . import cases, infer, packing, targets

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
OUTPUT = HERE.parent / "results/scope_static_2026-10-01.json"
SAVED_ANALYSES = tuple(HERE.parent / "results" / n / "analysis.json" for n in
                       ("scope_luna_v2_2026-10-01", "scope_luna_suffix_2026-10-01"))


def stable(value):
    if isinstance(value, dict):
        return {k: stable(v) for k, v in value.items() if k not in ("cpu_ns", "wall_ns")}
    if isinstance(value, list):
        return [stable(v) for v in value]
    return value


def evaluate(program, contract):
    public_schema = packing.schema(contract)
    counts, distinct, witnesses, disagreements, false_preflight = 0, set(), [], 0, 0
    input_digest, expected_digest, observed_digest = (hashlib.sha256() for _ in range(3))
    raw_bytes = retained_bytes = packed_bytes = 0
    cpu, wall = process_time_ns(), perf_counter_ns()
    for record, argument in cases.catalog(program["name"]):
        expected = targets.outcome(program, record, argument)
        projected = codec.project(record, contract)
        encoded = packing.encode(record, contract, public_schema)
        restored = packing.decode(encoded, public_schema)
        if restored != projected:
            raise ValueError("Public codec does not round-trip its projected input")
        observed = targets.outcome(program, restored, argument)
        raw = codec.wire([record, argument])
        distinct.add(raw)
        input_digest.update(raw + b"\n")
        expected_digest.update(codec.wire(expected) + b"\n")
        observed_digest.update(codec.wire(observed) + b"\n")
        different = expected != observed
        disagreements += different
        false_preflight += (program["name"] == "dispatch" and observed[0] == "preflight_only" and expected[0] != "preflight_only")
        if different and len(witnesses) < 6:
            witnesses.append({"record": record, "argument": argument, "retained": restored, "expected": expected, "observed": observed})
        counts += 1
        raw_bytes += len(codec.wire(record))
        retained_bytes += len(codec.wire(projected))
        packed_bytes += len(codec.wire(encoded))
    return {"cases": counts, "distinct_input_queries": len(distinct), "disagreements": disagreements,
            "false_preflight_only": false_preflight, "input_query_sha256": input_digest.hexdigest(),
            "expected_output_sha256": expected_digest.hexdigest(), "observed_output_sha256": observed_digest.hexdigest(),
            "raw_input_bytes_sum": raw_bytes, "projected_json_bytes_sum": retained_bytes, "packed_input_bytes_sum": packed_bytes,
            "witnesses": witnesses, "cpu_ns": process_time_ns()-cpu, "wall_ns": perf_counter_ns()-wall}


def child_rows(parent_memory, workers):
    return [r for r in json.loads(parent_memory or "[]") if r["worker"] in workers]


def readout(child_memory, case_id, request_sha256, program, public_schema, cached=False):
    found = [r for r in json.loads(child_memory or "[]") if r["case_id"] == case_id and r["request_sha256"] == request_sha256]
    if len(found) != 1:
        return ["unknown", None, None]
    return found[0]["data"] if cached else targets.outcome(program, packing.decode(found[0]["data"], public_schema))


def staged(records, program, contract=None, *, cached=False):
    public_schema = None if cached else packing.schema(contract)
    cpu, wall = process_time_ns(), perf_counter_ns()
    proposed = [{"case_id": r["case_id"], "worker": r["worker"], "request_sha256": r["request_sha256"],
                 "data": targets.outcome(program, r) if cached else packing.encode(r, contract, public_schema)} for r in records]
    parent, admission = codec.admit(proposed, codec.PARENT_CAP)
    children, correct, queries = [], 0, 0
    for workers in combinations(range(4), 2):
        available = child_rows(parent, workers)
        child, child_admission = codec.admit(available, codec.CHILD_CAP)
        for query in records:
            if query["worker"] in workers:
                observed = readout(child, query["case_id"], query["request_sha256"], program, public_schema, cached)
                correct += observed == targets.outcome(program, query)
                queries += 1
        children.append({"workers": list(workers), **child_admission})
    return {"parent": admission, "children": children, "correct": correct, "final_queries": queries,
            "public_schema_bytes": len(codec.wire(public_schema)), "public_schema_sha256": hashlib.sha256(codec.wire(public_schema)).hexdigest(),
            "parent_read_bytes": len(codec.wire(records)), "parent_proposal_write_bytes": len(codec.wire(proposed)),
            "cpu_ns": process_time_ns()-cpu, "wall_ns": perf_counter_ns()-wall,
            "limits": "Constructed timing on eight inspected historical records; schema/public program uncharged as instance memory, separately reported. Source disappears after parent, parent after child. Scripted final decoder."}


def saved_contracts():
    rows, identities = [], set()
    for path in SAVED_ANALYSES:
        data = json.loads(path.read_text(encoding="utf-8"))
        for row in data["calls"]:
            if row.get("contract_valid"):
                if row["identity"] in identities:
                    raise ValueError("Duplicate historical model identity")
                identities.add(row["identity"])
                rows.append({"identity": row["identity"], "contract": codec.validate(row["contract"]),
                             "source_analysis": path.relative_to(ROOT).as_posix()})
    if len(rows) != 7:
        raise ValueError("The permanent eighth-answer gap must remain missing")
    return rows


def analysis():
    rows, programs = [], targets.programs()
    for program in programs:
        cpu, wall = process_time_ns(), perf_counter_ns()
        extracted = infer.infer(program["source"], program["entry"], program["parameter"])
        extraction = {"cpu_ns": process_time_ns()-cpu, "wall_ns": perf_counter_ns()-wall,
                      "read_bytes": len(program["source"].encode("utf-8")), "write_bytes": len(codec.wire(extracted))}
        rows.append({"name": program["name"], "evidence_class": program["evidence_class"],
                     "source_path": program["source_path"], "public_source_sha256": hashlib.sha256(program["source"].encode()).hexdigest(),
                     "entry": program["entry"], "parameter": program["parameter"], "inferred": extracted,
                     "extraction": extraction, "catalog": evaluate(program, extracted["contract"]),
                     "public_schema": packing.schema(extracted["contract"]),
                     "public_schema_bytes": len(codec.wire(packing.schema(extracted["contract"])))})
    dispatch = programs[0]
    records, provenance = evidence.load_snapshot()
    contract = rows[0]["inferred"]["contract"]
    controls = {"static": staged(records, dispatch, contract), "authored": staged(records, dispatch, study.HAND),
                "whole_root_ast": staged(records, dispatch, codec.literal_roots(dispatch["source"])),
                "raw": staged(records, dispatch, {"value_paths": ["$"], "presence_paths": [], "nonempty_paths": []}),
                "cached": staged(records, dispatch, cached=True)}
    replay = [{**r, "catalog": evaluate(dispatch, r["contract"]), "staged": staged(records, dispatch, r["contract"])} for r in saved_contracts()]
    sources = [p for p in sorted(HERE.glob("*.py"))] + [HERE / "PROTOCOL.md"]
    sources += [ROOT / p["source_path"] for p in programs if p["source_path"]]
    sources += [HERE.parent / "scope_inference/codec.py", HERE.parent / "scope_inference/study.py",
                HERE.parent / "workflow_replay/evidence.py", *SAVED_ANALYSES]
    return {"version": "source_static_uniform_codec_control_v1", "date": "2026-10-01", "new_model_calls": 0,
            "evidence_class": "post-hoc offline inspected/constructed development; finite source-analysis and serialization controls",
            "source_sha256": {p.relative_to(ROOT).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest() for p in sources},
            "programs": rows, "catalog_cases": sum(r["catalog"]["cases"] for r in rows),
            "catalog_disagreements": sum(r["catalog"]["disagreements"] for r in rows),
            "historical_record_sha256": [r["record_sha256"] for r in provenance], "dispatch_controls": controls,
            "historical_model_contracts_replayed": replay, "permanent_missing_model_answers": 1,
            "parent_cap_bytes": codec.PARENT_CAP, "child_cap_bytes": codec.CHILD_CAP,
            "current_provider_price_claim": False, "prospective_natural_episodes_added": 0, "priced_total_cost": None,
            "limits": "Three inspected repository programs and one constructed late-key family; correlated finite catalog rows are not trials. Inference is a heuristic, not universal semantic proof or minimal scope. Same existing codec for every projected arm. Model replay is scripted post-hoc, not new LLM results; original incomplete primary criterion unchanged. No general slicing/coding novelty, natural-task prevalence, production performance or fully priced cost claim."}


def main():
    result = analysis()
    OUTPUT.write_text(json.dumps(result, sort_keys=True, indent=2)+"\n", encoding="utf-8", newline="\n")
    print(json.dumps({"catalog_cases": result["catalog_cases"], "catalog_disagreements": result["catalog_disagreements"],
                      "controls": {k:{"parent_bytes":v["parent"]["proposal_bytes"], "correct":v["correct"]} for k,v in result["dispatch_controls"].items()},
                      "model_replay": [{"identity":r["identity"], "correct":r["staged"]["correct"]} for r in result["historical_model_contracts_replayed"]]}))


if __name__ == "__main__":
    main()
