"""Read a sealed run and write descriptive diagnostics outside its inventory."""
from collections import Counter
from decimal import Decimal
import json
from pathlib import Path
from statistics import mean, median
from experiments.dependency_memory.rollback_development_v5.common import read, save_new, sha

root = Path("experiments/dependency_memory/results/rollback_development_v5_2026-10-08")
folder = root / "live"
assert (folder / "evidence_manifest.json").is_file(), "wait for sealed execution"
analysis = read(folder / "analysis.json")
execution = read(folder / "execution.json")
audit = read(root / "launch_checks/live_audit_result.json")
assert audit["all_passed"] and audit["reported_analysis_and_usage_reconciled"]
calls = [c for c in analysis["accounting"]["calls"] if c["state"] == "completed"]
rows = execution["jobs"]
prefixes = [r for r in rows if r["job"]["arm"] == "prefix"]
episodes = [r for r in rows if r["job"]["arm"] != "prefix"]

def resources(selected):
    return {"calls": len(selected), "input_tokens": sum(c["usage"]["input_tokens"] for c in selected),
            "cached_input_tokens": sum(c["usage"]["cached_input"] for c in selected),
            "output_tokens_including_reasoning": sum(c["usage"]["output"] for c in selected),
            "reasoning_tokens_subset_of_output": sum(c["usage"]["reasoning"] for c in selected),
            "planning_credits": str(sum((Decimal(c["planning_credits"]) for c in selected), Decimal(0)))}

matched = {}
for track in analysis["tracks"]:
    by_arm = {arm: {r["job"]["task_id"]: r["result"] for r in episodes
                     if r["job"]["track"] == track and r["job"]["arm"] == arm} for arm in ("K", "R")}
    complete = [task for task in by_arm["K"] if task in by_arm["R"]
                and by_arm["K"][task]["score"] is not None and by_arm["R"][task]["score"] is not None]
    arm_resources = {arm: resources([c for c in calls if c["identity"]["track"] == track
                                     and c["identity"]["arm"] == arm and c["identity"]["task_id"] in complete])
                     for arm in ("K", "R")}
    k_input = arm_resources["K"]["input_tokens"]
    matched[track] = {"complete_pairs": len(complete), "task_ids": sorted(complete), "resources": arm_resources,
                      "R_input_reduction_fraction": 1 - arm_resources["R"]["input_tokens"] / k_input if k_input else None,
                      "scope": "all actual arm calls in complete task pairs; mechanism shared preparation excluded and reported separately"}

diagnostics = []
for track in analysis["tracks"]:
    for arm in sorted({r["job"]["arm"] for r in episodes if r["job"]["track"] == track}):
        selected = [r["result"] for r in episodes if r["job"]["track"] == track and r["job"]["arm"] == arm]
        realized = [r for r in selected if "actions_used" in r]
        events = [event for r in realized for event in r["events"]]
        diagnostics.append({"track": track, "arm": arm, "scheduled": len(selected), "realized_outcomes": len(realized),
                            "median_actions_used": median(r["actions_used"] for r in realized) if realized else None,
                            "maximum_actions_used": max((r["actions_used"] for r in realized), default=None),
                            "median_stages_passed": median(r["stages_passed"] for r in realized) if realized else None,
                            "compression_count_distribution": dict(Counter(r["compression_count"] for r in realized)),
                            "repeated_rejected_candidates": sum(r["repeated_candidates"] for r in realized),
                            "earlier_requirement_violations": sum(r["prior_requirement_failures"] for r in realized),
                            "median_action_input_history_bytes": median(e["input_history_bytes"] for e in events) if events else None,
                            "maximum_action_input_history_bytes": max((e["input_history_bytes"] for e in events), default=None),
                            "total_visible_history_bytes_removed": sum(sum(r["history_bytes_before_removal"]) for r in realized),
                            "dispositions": dict(Counter(r["disposition"] for r in selected))})

report = {"evidence_kind": "post_run_descriptive_diagnostics", "source_analysis_sha256": sha(analysis),
          "source_execution_sha256": sha(execution), "verified_audit_sha256": sha(audit),
          "diagnostic_source_sha256": sha(Path(__file__).read_bytes()),
          "calibration_resources": resources([c for c in calls if c["identity"]["track"] == "calibration"]),
          "study_resources": resources([c for c in calls if c["identity"]["track"] != "calibration"]),
          "common_prefix_reasons": dict(Counter(r["result"].get("reason") or r["result"].get("disposition")
                                                  or ("eligible_public_mismatch" if r["result"].get("eligible") else "unclassified_prefix")
                                                  for r in prefixes)),
          "eligible_common_prefixes": sum(bool(r["result"].get("eligible")) for r in prefixes),
          "matched_pair_resources": matched, "trajectory_diagnostics": diagnostics,
          "control_calibration": analysis["control_calibration"], "actual_account_charge": None,
          "saved_analysis_prefix_label_limitation": "The frozen analysis defaults every prefix without a reason to eligible_public_mismatch, including unstarted prefixes. The corrected classification here uses explicit disposition and eligibility; primary eligibility filters and pair denominators in the frozen analysis are unaffected.",
          "mechanism_counter_scope": "Actions, stages and accumulated failure counters include the copied common prefix. Event-based input byte measurements and metered arm calls describe the continuation only.",
          "scope": "Post-run descriptive summaries of the frozen cohort; no new dispatch, exclusion, confirmatory test or semantic rating"}
save_new(root / "live_diagnostics.json", report)
print(json.dumps({"accounting": {k: v for k, v in analysis["accounting"].items() if k != "calls"},
                  "contrasts": {track: value["R_minus_K"] for track, value in analysis["tracks"].items()},
                  "eligible_common_prefixes": report["eligible_common_prefixes"], "diagnostic_rows": len(diagnostics)}, sort_keys=True))
