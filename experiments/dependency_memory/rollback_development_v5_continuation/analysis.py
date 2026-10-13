"""Cumulative v5 analysis with explicit amendment and missing-prefix counts."""
from collections import Counter

from .schedule import calls_for_job
from ..rollback_development_v5.analysis import analyze as original_analyze


def analyze(tasks, execution, accounting, manifest, *, simulated=False):
    result = original_analyze(tasks, execution, accounting, simulated=simulated)
    prefixes = [r["result"] for r in execution["jobs"] if r["job"]["arm"] == "prefix"]
    if "mechanism" in result["tracks"]:
        result["tracks"]["mechanism"]["prefix_dispositions"] = dict(Counter(
            p.get("reason") or p.get("disposition") or
            ("eligible_public_mismatch" if p.get("eligible") else "unclassified") for p in prefixes))
    inherited = manifest["continuation"]["prior"]
    result["continuation"] = {
        "failure_handling_amended_after_observation": True,
        "original_phase": manifest["continuation"]["prior_phase"],
        "original_admissions": inherited["admissions"],
        "new_admissions": len(accounting["calls"]) - inherited["admissions"],
        "retained_unknown_calls": inherited["unknown"],
        "new_unknown_calls": accounting["unknown_or_inflight_calls"] - inherited["unknown"],
        "job_origins": dict(Counter(o["kind"] for o in execution["origins"].values())),
        "generation_ceiling": manifest["continuation"]["generation_ceiling"],
        "phase_wall_seconds": execution["phase_wall_seconds"],
        "latency_scope": "cumulative phase execution time; resumed jobs include original partial time and receipt reconstruction",
        "calibration_reused_without_generations": inherited["live"],
        "unknown_trajectory_scores_remain_missing": True,
        "experimental_payloads_and_denominators_unchanged": True,
    }
    result["limitations"] += " Failure handling and execution timing were explicitly amended after the first stopped phase; this remains a development study."
    return result
