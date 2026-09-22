"""Offline CPU calibration for the frozen gate adapters; zero model calls."""
import hashlib
import json
from pathlib import Path
import statistics
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "experiments/dependency_memory"))
from luna6_revision import study


def main():
    fixtures = study.fixtures()
    results = {}
    for method in ("direct", "repair", "indexed"):
        elapsed = []
        for _ in range(7):
            start = time.process_time_ns()
            for _ in range(250):
                for fixture in fixtures:
                    if method == "indexed":
                        index = {row["service"]: row for row in fixture["records"]}
                        for future in fixture["futures"]:
                            study.compact(index[future["target"]])
                    else:
                        if method == "direct":
                            parent = study.projection(fixture["records"])
                        else:
                            parent, _ = study.repair("", fixture["records"], study.PARENT_CAP)
                        child = [row for row in study.decode(parent) if row["service"] in fixture["pair"]]
                        if method == "direct":
                            study.projection(child)
                        else:
                            study.repair("", child, study.CHILD_CAP)
            elapsed.append((time.process_time_ns()-start)/250)
        results[method] = {"cpu_ns_per_four_histories_batches": elapsed,
                           "median_cpu_ns_per_four_histories": statistics.median(elapsed)}
    report = {"scope": "Offline local CPU calibration: seven batches of 250 repetitions, four histories each; no model calls. Indexed includes building the index and serializing four target reads; repair uses an empty proposal and whole replacement. Disk storage, arbitrary text extraction and provider compute are excluded.",
              "timer": time.get_clock_info("process_time").implementation,
              "timer_resolution_seconds": time.get_clock_info("process_time").resolution,
              "script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
              "study_sha256": hashlib.sha256(Path(study.__file__).read_bytes()).hexdigest(),
              "methods": results}
    destination = ROOT / "experiments/dependency_memory/results/luna6_revision_2026-09-22/local_cost_calibration.json"
    destination.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps({key: row["median_cpu_ns_per_four_histories"] for key, row in results.items()}))


if __name__ == "__main__":
    main()
