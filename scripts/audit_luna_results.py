"""Reproduce the completed Luna development checks without model or network calls."""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from dataclasses import replace
from fractions import Fraction
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "experiments/dependency_memory"))

from artifact_workflow import run_episode
from pilot_interface import request_bytes, validate_inspection_response, validate_retention_response
from pilot_plan import build_plan
from recovery_frontier import executable_policy
from run_recovery_frontier import route_fixtures, scenarios


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def digest(value):
    return hashlib.sha256(canonical(value)).hexdigest()


def require(condition, message):
    if not condition:
        raise ValueError(message)


def audit(run_dir):
    run_dir = Path(run_dir)
    summary = json.loads((run_dir / "summary.json").read_text(encoding="utf-8"))
    manifest = json.loads((run_dir / "manifest.json").read_text(encoding="utf-8"))
    ledger = [json.loads(line) for line in (run_dir / "requests.jsonl").read_text(encoding="utf-8").splitlines() if line.strip()]
    require(digest(manifest) == summary["manifest_sha256"], "Manifest content hash mismatch")
    require(digest(ledger) == summary["request_audit_sha256"], "Request-audit content hash mismatch")
    require(len(ledger) == summary["request_attempts"] == summary["model_requests"] == 96,
            "This audit requires the completed 96-request live development tranche")
    require(summary["heldout_requests"] == 0 and summary["fake"] is False, "Unexpected run condition")
    require(len(summary["stage_a"]) == 12 and len(summary["stage_b"]) == 36, "Unexpected stage counts")
    require(all(row["status"] == "completed" for row in ledger), "An attempt did not complete")
    require(Counter(row["status"] for row in ledger) == +Counter(summary["attempt_status_counts"]),
            "Attempt status accounting mismatch")
    by_id = {row["evaluator_id"]: row for row in ledger}
    require(len(by_id) == len(ledger), "Duplicate evaluator request ID")
    forbidden = ("cheap_recovery", "costly_recovery", "scenario", "route_index", "payload_root",
                 "episode_id", "pair_id", "fixed_policy_reference", "reference_cost", "excess_cost")
    for number, row in enumerate(ledger, 1):
        require(row["attempt"] == number, "Request sequence mismatch")
        raw = row["request_utf8"].encode("utf-8")
        request = json.loads(raw)
        require(request_bytes(request) == raw, "Noncanonical public request")
        require(hashlib.sha256(raw).hexdigest() == row["request_sha256"], "Public request hash mismatch")
        require(not any(label in row["request_utf8"] for label in forbidden), "Evaluator label in public request")
        metadata = row["provider_metadata"]
        require(metadata.get("harness_termination") == "session_budget_exceeded", "Missing required guard stop")
        require(metadata.get("tool_events_observed") == 0, "Tool event observed")
        if request["kind"] == "inspection":
            validate_inspection_response(row["response"])
        else:
            validate_retention_response(row["response"], request)

    calibration = {row["scenario"]: row for row in build_plan()["calibration"]}
    decisions = []
    for row in summary["stage_a"]:
        actual = by_id[row["decision_id"]]["response"]["inspect"]
        cell = calibration[row["scenario"]]
        cost = Fraction(cell["inspection_extra_cost" if actual else "no_inspection_extra_cost"])
        regret = cost - Fraction(cell["optimal_extra_cost"])
        require(actual == row["inspection"] and str(cost) == row["expected_extra_cost"]
                and str(regret) == row["excess_cost"], "Stage-A summary does not match independent arithmetic")
        decisions.append({"scenario": row["scenario"], "replicate": row["replicate"],
                          "inspection": actual, "exact_regret": str(regret)})

    configs = scenarios()
    deletion_checks = 0
    arms = defaultdict(lambda: defaultdict(int))
    for row in summary["stage_b"]:
        require(row["status"] == "completed" and row["success"] is True, "Incomplete or unsuccessful episode")
        first = by_id[row["episode_id"] + "/retain-1"]
        second = by_id[row["episode_id"] + "/retain-2"]
        before, after = json.loads(first["request_utf8"]), json.loads(second["request_utf8"])
        fixture = manifest["fixtures"][row["scenario"]]
        original = next(r for r in fixture["receipts"] if r["key"] == fixture["target"])
        revision = fixture.get("revision")
        latest = revision if revision and revision["key"] == fixture["target"] else original
        available = any(r == latest for r in after["visible_records"] if r["key"] in second["response"]["keys"])
        config = configs[row["scenario"]]
        expected_cost = 7 + config.delay + int(row["inspection"]) * config.probe_cost
        expected_cost += 0 if available else config.recovery_cost
        require(available == row["pre_recovery_available"] and (not available) == row["recovery_attempted"],
                "Availability/recovery differs from selected latest receipt")
        require(expected_cost == row["synthetic_cost_units"], "Synthetic cost differs from independent arithmetic")
        for receipt in before["visible_records"]:
            if receipt["key"] not in first["response"]["keys"]:
                deletion_checks += 1
                require(receipt["token"] not in second["request_utf8"], "Deleted original receipt reappeared")
        total = arms[row["arm"]]
        total["episodes"] += 1
        total["pre_recovery_available"] += int(available)
        total["recoveries"] += int(not available)
        total["synthetic_cost_units"] += expected_cost

    # Independent public-rule formula: refreshed smaller target occurs with
    # probability 1/2; retained larger key j contributes j of 30 routes.
    config = configs["revision_cheap_recovery"]
    require((config.jobs, config.candidate_count, config.first_capacity, config.second_capacity)
            == (6, 2, 2, 2) and config.revise, "Fixed-pair formula assumptions changed")
    pairs = []
    for indices in ((0, 1), (1, 2), (4, 5)):
        keys = tuple(f"job-{index}" for index in indices)
        policy = replace(executable_policy(config, inspect=False, recover=True), first_keys=keys)
        results = [run_episode(config, fixture, policy) for fixture in route_fixtures(config)]
        require(len(results) == 30 and all(r.success for r in results), "Unexpected fixed-pair route outcomes")
        enumerated = Fraction(sum(not r.recovery_attempted for r in results), len(results))
        formula = Fraction(1, 2) + Fraction(sum(indices), 30)
        require(enumerated == formula, "Fixed-pair formula differs from route enumeration")
        pairs.append({"parent_keys": list(keys), "routes": len(results),
                      "enumerated_availability": str(enumerated), "formula_availability": str(formula)})

    return {"version": "luna_development_independent_result_audit_v1", "passed": True,
            "scope": "Read-only saved public requests and evaluator outcomes; no model calls or production-wire capture",
            "script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            "manifest_sha256": summary["manifest_sha256"], "request_audit_sha256": summary["request_audit_sha256"],
            "canonical_hash_schema_guard_and_tool_checks": len(ledger),
            "stage_a_decisions_checked": len(decisions), "stage_a_decisions": decisions,
            "stage_a_reference_matches": sum(Fraction(r["exact_regret"]) == 0 for r in decisions),
            "stage_a_total_exact_regret": str(sum((Fraction(r["exact_regret"]) for r in decisions), Fraction())),
            "stage_b_latest_receipt_and_cost_checks": len(summary["stage_b"]),
            "discarded_original_token_checks": deletion_checks, "stage_b_arms": dict(arms),
            "fixed_parent_pair_formula_checks": pairs, "new_model_requests": 0}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-dir", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = audit(args.run_dir)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps({"passed": result["passed"], "requests_checked": result["canonical_hash_schema_guard_and_tool_checks"],
                      "deletion_checks": result["discarded_original_token_checks"], "new_model_requests": 0}))


if __name__ == "__main__":
    main()
