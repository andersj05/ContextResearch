"""Reproducible descriptions of audited final pooled transfer evidence.

No provider calls, additional tests of significance, or inferred model mechanisms
are introduced. Primary estimates are copied from the frozen analysis after a
consistency check. Key-selection patterns are explicitly exploratory and may
overlap. Use only after the phase has ended and the pooled audit has passed.
"""
from __future__ import annotations

import argparse
from copy import deepcopy
from fractions import Fraction
import hashlib
from itertools import combinations, product
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "experiments/dependency_memory"))
from audit_transfer_run import digest, require
from luna_appserver import strict_json
from transfer_interface import validate_response
import transfer_study as study

VERSION = "transfer_final_descriptive_findings_v1"
FLAGS = ("lowest_two_key_names", "highest_two_key_names", "opposite_refresh_optimum")
FACTORS = ("jobs", "framing", "guarantee", "guidance", "refresh_rule")
PRIMARY_ESTIMATES = ("scheduled_pairs", "valid_pairs", "transport_complete_pairs", "complete_blocks",
    "planned_blocks", "mean_normalized_regret_benefit", "complete_block_mean_normalized_regret_benefit",
    "block_bootstrap_95_percent_interval", "bootstrap_resamples", "mean_valid_and_optimal_benefit",
    "raw_regret_benefit_by_size", "coverage_warning")


def counts(rows):
    valid = [row for row in rows if row["status"] == "completed"]
    return {"scheduled":len(rows), "valid":len(valid),
        "optimal":sum(row["grade"]["optimal_parent"] for row in valid),
        "strict_suboptimal":sum(not row["grade"]["optimal_parent"] for row in valid),
        "underfilled":sum(row["grade"]["selected_count"] < 2 for row in valid),
        "policy_failures":sum(row["status"] == "policy_failure" for row in rows),
        "transport_failures":sum(row["status"] == "transport_failure" for row in rows),
        "incomplete":sum(row["status"] == "incomplete" for row in rows),
        "valid_and_optimal_denominator":sum(row["status"] in ("completed", "policy_failure") for row in rows)}


def selection_patterns(row, case):
    """Describe one valid choice using original public priorities, not key order."""
    require(row["status"] == "completed" and type(row.get("grade")) is dict, "Patterns require a valid selection")
    grade, request = row["grade"], case["request"]
    selected = validate_response({"keys":grade["keys"]}, request)
    require(list(selected) == grade["keys"] and grade["selected_count"] == len(selected), "Saved selected keys/count disagree")
    priorities = {item["key"]:item["refresh_priority"] for item in request["public_metadata"]["jobs"]}
    require(grade["selected_priorities"] == [priorities[key] for key in selected], "Saved priorities differ from original public metadata")
    all_keys = sorted(priorities)
    rule = case["refresh_rule"]
    # These are whole-pair matches; an underfilled answer is never promoted to
    # matching an entire extreme pair merely because its one key is extreme.
    opposite = None
    if rule != "none":
        by_priority = sorted(priorities, key=priorities.get)
        opposite = set(by_priority[:2] if rule == "first" else by_priority[-2:])
    return {"lowest_two_key_names":list(selected) == all_keys[:2],
        "highest_two_key_names":list(selected) == all_keys[-2:],
        "opposite_refresh_optimum":opposite is not None and set(selected) == opposite}


def pattern_summary(suboptimal_cases):
    """Keep every Boolean overlap instead of assuming mutually exclusive labels."""
    marginal = {flag:sum(row["patterns"][flag] for row in suboptimal_cases) for flag in FLAGS}
    intersections = {" & ".join(group):sum(all(row["patterns"][flag] for flag in group) for row in suboptimal_cases)
                     for size in (2,3) for group in combinations(FLAGS,size)}
    signatures = [{**dict(zip(FLAGS, signature)), "count":sum(
        tuple(row["patterns"][flag] for flag in FLAGS) == signature for row in suboptimal_cases)}
        for signature in product((False,True), repeat=3)]
    union = sum(any(row["patterns"].values()) for row in suboptimal_cases)
    return {"strict_suboptimal_valid_choices":len(suboptimal_cases), "marginal_matches":marginal,
        "intersection_matches":intersections, "all_eight_boolean_signatures":signatures,
        "union_matches":union, "other_choices":len(suboptimal_cases)-union,
        "underfilled":sum(row["underfilled"] for row in suboptimal_cases),
        "overlap_note":"Marginal and intersection counts may overlap; union plus other equals the denominator."}


def summarize(pooled, original_plan, *, allow_fake=False):
    require(pooled.get("version") == "transfer_pooled_phases_v1", "Expected final pooled phase evidence")
    fake = pooled.get("fake")
    require(type(fake) is bool and (not fake or allow_fake), "Synthetic findings require explicit allow_fake")
    cases = original_plan.get("cases", [])
    rows = pooled.get("rows", [])
    require(len(cases) == len(rows) == 1536 and len({row["case_id"] for row in rows}) == 1536,
            "All original 1536 outcome denominators must be preserved")
    for case, row in zip(cases, rows):
        require(all(row.get(field) == case.get(field) for field in ("case_id", "block", "worker", *FACTORS)),
                "Pooled row differs from original case/factor order")
        require(row["status"] in ("completed", "policy_failure", "transport_failure", "incomplete"), "Unknown final outcome status")
        if row["status"] != "completed":
            require(row.get("grade") is None, "Missing or failed outcome was assigned a grade")
    # Reuse the frozen analysis only to verify the saved values; do not introduce
    # a different bootstrap, sample, endpoint, or significance calculation.
    reproduced = study.aggregate(rows)
    require(pooled.get("primary") == reproduced["primary"]
            and pooled.get("by_condition") == reproduced["by_condition"]
            and pooled.get("status_counts") == reproduced["status_counts"], "Saved frozen analysis does not reproduce")
    require(len(pooled["by_condition"]) == 48, "All 48 conditions must remain visible")
    primary_rows = [row for row in rows if row["framing"] == "workflow"
                    and row["guarantee"] == "unspecified" and row["refresh_rule"] != "none"]
    arm_counts = {guidance:counts([row for row in primary_rows if row["guidance"] == guidance])
                  for guidance in ("generic", "prospective")}
    pairs = pooled["primary"]["pairs"]
    paired_regret_counts = {"prospective_favored":0, "generic_favored":0, "tie":0, "not_both_valid":0}
    paired_optimality_counts = {"prospective_favored":0, "generic_favored":0, "tie":0, "not_both_transport_complete":0}
    for pair in pairs:
        if pair["both_valid"]:
            value = Fraction(pair["normalized_regret_benefit"])
            paired_regret_counts["prospective_favored" if value > 0 else "generic_favored" if value < 0 else "tie"] += 1
        else:
            paired_regret_counts["not_both_valid"] += 1
        if pair["both_transport_complete"]:
            value = pair["valid_and_optimal_benefit"]
            paired_optimality_counts["prospective_favored" if value > 0 else "generic_favored" if value < 0 else "tie"] += 1
        else:
            paired_optimality_counts["not_both_transport_complete"] += 1
    suboptimal = []
    for row, case in zip(rows, cases):
        if row["status"] != "completed":
            continue
        flags = selection_patterns(row, case)
        if row["grade"]["optimal_parent"]:
            continue
        suboptimal.append({**{field:row[field] for field in ("case_id", "block", *FACTORS)},
            "selected_keys":row["grade"]["keys"], "selected_priorities":row["grade"]["selected_priorities"],
            "exact_parent_regret":row["grade"]["exact_parent_regret"],
            "underfilled":row["grade"]["selected_count"] < 2, "patterns":flags})
    primary_patterns = {guidance:pattern_summary([row for row in suboptimal
        if row["framing"] == "workflow" and row["guarantee"] == "unspecified"
        and row["refresh_rule"] != "none" and row["guidance"] == guidance])
        for guidance in ("generic", "prospective")}
    return {"version":VERSION, "fake":fake, "new_model_requests":0,
        "source_pooled_summary_sha256":digest(pooled), "source_original_plan_sha256":digest(original_plan),
        "script_sha256":hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "overall":counts(rows), "refresh_present":counts([row for row in rows if row["refresh_rule"] != "none"]),
        "no_refresh":{**counts([row for row in rows if row["refresh_rule"] == "none"]),
            "interpretation":"Every full two-record choice ties; optimal counts here do not demonstrate refresh-rule understanding."},
        "primary":{"definition":"Workflow, unspecified child, refresh present; generic minus prospective regret.",
            "arm_counts":arm_counts, "paired_regret_counts":paired_regret_counts,
            "paired_valid_and_optimal_counts":paired_optimality_counts,
            "frozen_estimates":{name:deepcopy(pooled["primary"][name]) for name in PRIMARY_ESTIMATES}},
        "all_48_condition_summaries":deepcopy(pooled["by_condition"]),
        "exploratory_suboptimal_patterns":{"scope":"Valid strictly suboptimal choices only; matches are descriptive and can overlap.",
            "all":pattern_summary(suboptimal), "by_primary_guidance":primary_patterns, "cases":suboptimal},
        "interpretation_limits":["No additional significance calculation or causal-mechanism claim is made.",
            "A matching key pair describes an output, not a persistent model policy or internal reasoning.",
            "Failures and incomplete cases retain separate denominators; valid-only regret and complete-block intervals use different populations when data are missing.",
            "Raw regret benefits by size and all primary estimates are the saved frozen estimands, not newly selected endpoints.",
            "Synthetic development results do not establish natural-task, native-compaction, or deployed-agent gains."]}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pooled-summary",type=Path,required=True)
    parser.add_argument("--manifest",type=Path,required=True)
    parser.add_argument("--audit",type=Path,required=True)
    parser.add_argument("--output",type=Path,required=True)
    args = parser.parse_args()
    # Require the completed independent audit artifact before opening answers.
    audited = strict_json(args.audit.read_text(encoding="utf-8"))
    require(audited.get("passed") is True and audited.get("fake") is False,
            "A passed final real-evidence audit is required")
    pooled = strict_json(args.pooled_summary.read_text(encoding="utf-8"))
    manifest = strict_json(args.manifest.read_text(encoding="utf-8"))
    require(audited.get("pooled_summary_sha256") == digest(pooled)
            and audited.get("manifest_sha256") == digest(manifest), "Final audit does not match these artifacts")
    result = summarize(pooled,manifest["original_plan"])
    result["source_final_audit_sha256"] = digest(audited)
    require(not args.output.exists(), "Findings summary must use a new output path")
    args.output.parent.mkdir(parents=True,exist_ok=True)
    with args.output.open("x",encoding="utf-8",newline="\n") as stream:
        json.dump(result,stream,indent=2,sort_keys=True)
        stream.write("\n")
    print(json.dumps({"output":str(args.output),"valid":result["overall"]["valid"],
                     "optimal":result["overall"]["optimal"],"new_model_requests":0}))


if __name__ == "__main__":
    main()
