"""Post-run high-resolution local CPU sensitivity check on development traces.

The live runner used process_time_ns, whose Windows resolution reported zero for
short operations. This separate calibration never makes model calls and does not
change the frozen study implementation or evaluation traces.
"""
from __future__ import annotations

from hashlib import sha256
import json
from pathlib import Path
import platform
from statistics import median
import sys
from time import perf_counter_ns

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from experiments.dependency_memory.schema_checks.cases import DEV_SEEDS, FAMILIES, compact, make_case
from experiments.dependency_memory.schema_checks.memory import check, decode, direct, project, select

OUT = ROOT / "experiments/dependency_memory/results/schema_checks_2026-09-22/local_calibration.json"
BATCHES = 7
REPEATS = 1000


def measure(operation):
    values = []
    for _ in range(BATCHES):
        start = perf_counter_ns()
        for _ in range(REPEATS):
            operation()
        values.append((perf_counter_ns() - start) / REPEATS)
    return {"median_ns_per_operation": round(median(values)), "max_batch_ns_per_operation": round(max(values)),
            "batches": BATCHES, "repeats_per_batch": REPEATS}


def main():
    rows = []
    for family in FAMILIES:
        for seed in DEV_SEEDS:
            case = make_case(family, seed, "development")
            schema, records, candidates = case["tool_schema"], case["tool_results"], case["candidates"]

            def automatic():
                parent = project(schema, records)
                if not check(parent, schema, records)["passed"]:
                    raise ValueError("Calibration parent check failed")
                child = select(parent, candidates)
                expected = decode(select(parent, candidates))
                if not check(child, schema, expected)["passed"]:
                    raise ValueError("Calibration child check failed")

            def authored():
                parent = direct(family, records)
                select(parent, candidates)

            def indexed():
                for target in candidates:
                    record = next(row for row in records if target in row.values())
                    compact(record)

            def full():
                for _ in candidates:
                    compact(records)

            rows.append({"family": family, "seed": seed, "automatic": measure(automatic),
                         "direct": measure(authored), "indexed_two_reads": measure(indexed),
                         "full_two_reads": measure(full)})
    source = Path(__file__)
    result = {"version": "schema_checks_local_calibration_v1", "script_sha256": sha256(source.read_bytes()).hexdigest(),
              "python": platform.python_version(), "platform": platform.platform(),
              "method": "perf_counter_ns; seven 1000-repetition batches on development traces after the live run",
              "rows": rows,
              "estimated_six_case_cpu_ns": {
                  arm: sum(max(row[arm]["median_ns_per_operation"] for row in rows if row["family"] == family)
                           for family in FAMILIES) * 2
                  for arm in ("automatic", "direct")},
              "limitations": "Calibration is post-run on same-schema development traces; wall-clock CPU proxy, not per-call measured launch CPU or provider bill."}
    OUT.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result["estimated_six_case_cpu_ns"], indent=2))


if __name__ == "__main__":
    main()
