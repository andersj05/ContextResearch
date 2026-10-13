"""Reconcile unique test coverage without hiding unsuccessful command attempts."""
import json
from pathlib import Path
import re
from experiments.dependency_memory.rollback_development_v5.common import now, read, save_new, sha
from experiments.dependency_memory.rollback_development_v5.prepare import check_bundle

root = Path("experiments/dependency_memory/results/rollback_development_v5_2026-10-08")
checks = root / "launch_checks"
original = (checks / "repository_unit_tests.txt").read_text(encoding="utf-8")
pattern = r"^\s*test_\S+ \(([\w.]+)\)"
ids = set(re.findall(pattern, original, re.MULTILINE))
failed = set(read(checks / "repository_rechecks_selection.json")["test_ids"])
skipped = set(re.findall(r"^\s*test_\S+ \(([\w.]+)\).*\.\.\. skipped ", original, re.MULTILINE))
assert len(ids) == 744 and len(failed) == 61 and len(skipped) == 9
recheck_record = read(checks / "repository_rechecks_outside_sandbox.json")
assert recheck_record["exit_code"] == 0
rechecks = (checks / "repository_rechecks_outside_sandbox.txt").read_text(encoding="utf-8")
assert set(re.findall(pattern, rechecks, re.MULTILINE)) == failed
assert re.search(r"^Ran 61 tests in ", rechecks, re.MULTILINE)
assert re.search(r"^OK\s*$", rechecks, re.MULTILINE)
docker = (checks / "docker_tests.txt").read_text(encoding="utf-8")
normalize = lambda name: name.removeprefix("experiments.dependency_memory.")
assert {normalize(i) for i in re.findall(pattern, docker, re.MULTILINE)} == {normalize(i) for i in skipped}
assert read(checks / "docker_tests.json")["exit_code"] == 0
manifest, tasks = check_bundle(root / "prepared")
record = {"checked_utc": now(), "unique_tests": 744, "unique_tests_passed": 744,
          "remaining_unexecuted_tests": 0, "remaining_failed_test_ids": [], "model_calls": 0,
          "source_manifest_sha256": sha(manifest), "scientific_code_changed": False,
          "discovery": {"tests": 744, "initially_passed": len(ids - failed - skipped),
                        "unique_affected_test_ids": len(failed), "skipped": 9,
                        "subtest_failure_events": 2, "error_events": 75,
                        "record": "repository_unit_tests.json", "console": "repository_unit_tests.txt"},
          "recheck": {"tests": 61, "passed": 61, "record": "repository_rechecks_outside_sandbox.json",
                      "selected_exactly_original_affected_ids": True,
                      "reason": "Windows sandbox temp cleanup and atomic-replace access failures",
                      "workspace_temp_probe": "mock_cleanup_workspace_probe.json",
                      "earlier_incomplete_recheck": "repository_rechecks.json",
                      "earlier_recheck_limitation": "Scratch helper lacked the repository import root; sandbox also denied atomic replacement. Corrected helper and outside-sandbox run preserve every earlier attempt."},
          "docker_supplement": {"tests": 9, "passed": 9, "covers_exactly_original_skips": True,
                                "record": "docker_tests.json"},
          "v5_invariant_tests": sum("rollback_development_v5.test_design." in name for name in ids),
          "test_ids_sha256": sha(sorted(ids)), "passed": True}
save_new(checks / "repository_test_coverage.json", record)
print(json.dumps({k: record[k] for k in ("unique_tests_passed", "remaining_unexecuted_tests", "model_calls", "v5_invariant_tests", "passed")}, sort_keys=True))
