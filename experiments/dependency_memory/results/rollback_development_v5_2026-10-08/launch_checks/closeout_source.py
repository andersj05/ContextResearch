"""Seal verified closeout while preserving the incomplete live cohort explicitly."""
from pathlib import Path
import json
from experiments.dependency_memory.rollback_development_v5.common import now, read, save_new, sha
from experiments.dependency_memory.rollback_development_v5.prepare import check_bundle

root = Path("experiments/dependency_memory/results/rollback_development_v5_2026-10-08")
checks = root / "launch_checks"
manifest, tasks = check_bundle(root / "prepared")
analysis = read(root / "live/analysis.json")
audit = read(checks / "live_audit_result.json")
coverage = read(checks / "repository_test_coverage.json")
assert audit["all_passed"] and coverage["passed"] and coverage["unique_tests_passed"] == 744
assert read(checks / "scientific_validation_result.json")["status"] == "PASS"
for name in ("final_catalog_build", "final_catalog_check", "final_navigation_check", "paper_build"):
    assert read(checks / (name + ".json"))["exit_code"] == 0
assert analysis["accounting"]["completed_calls"] == 235
assert analysis["accounting"]["unknown_or_inflight_calls"] == 1
assert all(v["R_minus_K"]["complete_pairs"] == 0 for v in analysis["tracks"].values())
assert read(root / "live_diagnostics.json")["diagnostic_source_sha256"] == sha((checks / "diagnostic_summary_source.py").read_bytes())
files = [{"path": path.relative_to(root).as_posix(), "bytes": path.stat().st_size,
          "sha256": sha(path.read_bytes())} for path in sorted(root.rglob("*")) if path.is_file()]
record = {"closed_utc": now(), "status": "closed_with_gaps_and_verified",
          "live_cohort_complete": False, "verification_complete": True,
          "frozen_sources_and_tasks_intact": True, "source_manifest_sha256": sha(manifest),
          "unique_tasks": len(tasks), "metered_completions": 235, "excluded_calibration_completions": 8,
          "study_metered_completions": 227, "unresolved_dispatches": 1, "complete_primary_pairs": 0,
          "known_planning_credits": analysis["accounting"]["planning_credits"],
          "locked_unknown_planning_credits": analysis["accounting"]["locked_planning_credits"],
          "actual_account_charge": None, "unique_repository_tests_passed": 744,
          "all_affected_tests_rechecked": True, "live_replay_passed": True,
          "fresh_offline_replay_passed": True, "full_scientific_validation_passed": True,
          "catalog_and_navigation_passed": True, "paper_assembly_passed": True,
          "controller_stop": "unknown_dispatch", "dispatched_identities_retried": 0,
          "historical_allocations_reopened": False,
          "next_live_gate": "Separate reviewed allocation after safe exception diagnostic retention and earlier paired coverage; do not reopen this bundle",
          "inventory": files, "file_count": len(files), "inventory_sha256": sha(files)}
save_new(root / "closeout.json", record)
print(json.dumps({k: v for k, v in record.items() if k != "inventory"}, sort_keys=True))
