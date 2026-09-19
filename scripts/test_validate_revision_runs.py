"""Independent aggregation checks for separate revision allocations."""
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from validate_context_repo import validate_revision_runs


def audited(*, requests=1, settled="0.01", retained="0"):
    return {"passed": True, "fake": False, "model_requests": requests,
            "requests_checked": requests, "settled_credit_equivalent": settled,
            "retained_credit_equivalent": retained}


class RevisionRunAggregationTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.results = Path(self.temporary.name)

    def runs(self, count):
        for index in range(count):
            (self.results / f"revision_luna_{index}").mkdir()

    def test_no_runs_does_not_reuse_initial_tranche_or_offline_artifacts(self):
        (self.results / "luna_development_old").mkdir()
        (self.results / "revision_diagnostic_plan.json").write_text("{}")
        (self.results / "revision_luna_note.txt").write_text("not a directory")
        with patch("audit_revision_run.audit") as check:
            counts, errors = validate_revision_runs(self.results)
        check.assert_not_called()
        self.assertEqual(errors, [])
        self.assertEqual(counts["revision_luna_runs"], 0)
        self.assertEqual(counts["completed_revision_model_requests"], 0)
        self.assertEqual(counts["revision_credit_equivalent_committed"], "0")

    def test_aggregate_dispatch_overflow_cannot_be_split_across_runs(self):
        self.runs(2)
        with patch("audit_revision_run.audit", side_effect=[audited(requests=13), audited(requests=12)]):
            counts, errors = validate_revision_runs(self.results)
        self.assertEqual(counts["completed_revision_model_requests"], 25)
        self.assertEqual(counts["revision_luna_validated_runs"], 2)
        self.assertTrue(any("24-request" in error for error in errors))

    def test_aggregate_credit_cap_includes_uncertain_failure_reservations(self):
        self.runs(2)
        with patch("audit_revision_run.audit", side_effect=[audited(settled="2"),
                audited(settled="0", retained="10.4025")]):
            counts, errors = validate_revision_runs(self.results)
        self.assertEqual(counts["revision_credit_equivalent_committed"], "12.4025")
        self.assertTrue(any("12-credit" in error for error in errors))

    def test_missing_and_malformed_evidence_are_errors_not_silently_skipped(self):
        self.runs(2)
        (self.results / "revision_luna_1/manifest.json").write_text("{")
        counts, errors = validate_revision_runs(self.results)
        self.assertEqual(counts["revision_luna_runs"], 2)
        self.assertEqual(counts["revision_luna_validated_runs"], 0)
        self.assertEqual(len(errors), 2)
        self.assertTrue(any("revision_luna_0" in error for error in errors))
        self.assertTrue(any("revision_luna_1" in error for error in errors))

    def test_fake_evidence_cannot_enter_live_allocation_totals(self):
        self.runs(1)
        with patch("audit_revision_run.audit", return_value={**audited(), "fake": True}):
            counts, errors = validate_revision_runs(self.results)
        self.assertEqual(counts["revision_luna_validated_runs"], 0)
        self.assertTrue(any("live evidence" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
