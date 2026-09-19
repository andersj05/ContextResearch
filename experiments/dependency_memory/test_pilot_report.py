"""Scientific accounting and failure-retention checks for the report renderer."""

from copy import deepcopy
import unittest

from pilot_interface import FakeClient
from pilot_report import report
from run_development_pilot import execute


class PilotReportTests(unittest.TestCase):
    def test_complete_control_preserves_stage_counts_and_exact_comparisons(self):
        summary, _ = execute(FakeClient("optimal"))
        text = report(summary)
        self.assertIn("| Request attempts (including failures) | 96 |", text)
        self.assertIn("| Stage A decisions: planned / attempted | 12 / 12 |", text)
        self.assertIn("| Stage B episodes: planned / attempted | 36 / 36 |", text)
        self.assertIn("| Pre-recovery available / reached measurement | 26 / 36 |", text)
        self.assertIn("| Recorded model requests | 0 |", text)
        # One row for every scheduled episode, even if headings change elsewhere.
        outcome_rows = [line for line in text.splitlines() if "| completed |" in line and
                        any("| " + arm + " |" in line for arm in ("never_inspect", "always_inspect", "model_selective"))]
        self.assertEqual(len(outcome_rows), 36)
        self.assertTrue(all(line.endswith("| 0 |") for line in outcome_rows))
        self.assertIn("| cheap_recovery | 0 | completed | no | 2/3 | 0 |", text)
        self.assertIn("| costly_recovery | 21 | 14 | no | 11 | yes |", text)
        self.assertIn("not independent trials", text)
        self.assertEqual(text, report(deepcopy(summary)))

    def test_budget_stop_keeps_partial_and_unstarted_episodes_without_false_cost_gain(self):
        summary, _ = execute(FakeClient("optimal"), cap=13)
        text = report(summary)
        self.assertIn("| Request attempts (including failures) | 13 |", text)
        self.assertIn("| Stage B episodes: planned / attempted | 36 / 1 |", text)
        self.assertIn("| Pre-recovery measurement not reached | 36 |", text)
        self.assertIn("completed=0; policy_failure=0; transport_failure=0; incomplete=36", text)
        outcomes = [line for line in text.splitlines() if "| incomplete |" in line]
        self.assertEqual(len(outcomes), 36)
        self.assertTrue(all(line.endswith("| unknown |") for line in outcomes))
        self.assertIn("| Stage A decisions: planned / attempted | 12 / 12 |", text)

    def test_zero_budget_is_not_thirty_six_failed_completed_episodes(self):
        summary, _ = execute(FakeClient("optimal"), cap=0)
        text = report(summary)
        self.assertIn("| Stage A decisions: planned / attempted | 12 / 0 |", text)
        self.assertIn("| Stage B episodes: planned / attempted | 36 / 0 |", text)
        self.assertIn("| Pre-recovery available / reached measurement | 0 / 0 |", text)
        self.assertIn("| Subscription credits consumed | unknown |", text)

    def test_invalid_schema_failures_are_counted_and_not_dropped(self):
        summary, _ = execute(FakeClient("invalid"))
        text = report(summary)
        self.assertIn("| Request attempts (including failures) | 48 |", text)
        self.assertIn("| Stage B episodes: planned / attempted | 36 / 36 |", text)
        failure_rows = [line for line in text.splitlines() if "| policy_failure |" in line]
        self.assertEqual(len(failure_rows), 48)
        self.assertIn("policy_failure=48", text)
        self.assertIn("| Pre-recovery measurement not reached | 36 |", text)

    def test_transport_failure_stays_in_denominator_and_unknown_usage(self):
        class BrokenClient:
            def complete(self, request):
                raise TimeoutError("no response")
        summary, ledger = execute(BrokenClient())
        summary["request_metrics"] = ledger.rows
        text = report(summary)
        self.assertIn("| Request attempts (including failures) | 1 |", text)
        self.assertIn("| Stage A decisions: planned / attempted | 12 / 1 |", text)
        self.assertIn("transport_failure=1", text)
        self.assertIn("| Input tokens | unknown |", text)
        self.assertIn("| Output tokens | unknown |", text)

    def test_partial_usage_is_a_reported_subtotal_with_coverage(self):
        summary, ledger = execute(FakeClient("optimal"), cap=14)
        summary["request_metrics"] = deepcopy(ledger.rows)
        # One Stage A and one Stage B attempt report usage; all others are unknown.
        for row in (summary["request_metrics"][0], summary["request_metrics"][-1]):
            row["provider_metadata"] = {"usage": {"input_tokens": 100, "cached_input_tokens": 80,
                                                   "output_tokens": 12, "reasoning_output_tokens": 4}}
            row["latency_seconds"] = 1.25
        summary["transport_manifest"] = {"model": "gpt-5.6-luna", "model_revision": None,
                                          "reviewed_cli_version": "test-version", "reasoning_effort": "low"}
        text = report(summary)
        self.assertIn("| Input tokens | 200 reported (2/14 attempts measured) |", text)
        self.assertIn("| Output tokens | 24 reported (2/14 attempts measured) |", text)
        self.assertIn("| Cached input tokens | 160 reported (2/14 attempts measured) |", text)
        self.assertIn("| Total measured request latency (seconds) | 2.5 reported (2/14 attempts measured) |", text)
        self.assertIn("100 reported (1/2 attempts measured)", text)
        self.assertIn("| Immutable model revision | unknown |", text)
        self.assertIn("| Model alias | gpt-5.6-luna |", text)
        self.assertIn("These buckets are not added together", text)

    def test_forget_all_control_makes_success_saturation_explicit(self):
        summary, _ = execute(FakeClient("forget_all"))
        text = report(summary)
        self.assertIn("| Stage B terminal successes / planned | 36 / 36 |", text)
        self.assertIn("| Pre-recovery available / reached measurement | 0 / 36 |", text)
        self.assertIn("even empty retention succeed", text)
        self.assertIn("fake-client software checks, not model-performance results", text)

    def test_luna_contract_aliases_keep_planning_equivalents_separate_from_charges(self):
        summary, ledger = execute(FakeClient("optimal"), cap=1)
        summary["transport_manifest"] = {
            "model": "gpt-5.6-luna", "cli_version": "0.155.0-alpha.9.2",
            "reasoning_effort": "low", "service_tier": "default", "http_and_stream_retries": 0,
            "state": "Fresh process and ephemeral thread", "account_quota_stop_used_percent": 80,
        }
        summary["cost_accounting"]["credit_budget"] = {
            "cap_credit_equivalent": 20, "per_attempt_reservation": 10.4025,
            "settled_credit_equivalent": 0.007, "uncertain_credit_reservations": 0,
            "committed_credit_equivalent": 0.007, "remaining_credit_equivalent": 19.993,
            "reservation_assumptions": {"output_model_maximum": 128000},
        }
        summary["request_metrics"] = ledger.rows
        ledger.rows[0]["provider_metadata"] = {"credit_accounting": {"basic_rate_credit_estimate": 0.005}}
        text = report(summary)
        self.assertIn("| CLI/client version | 0.155.0-alpha.9.2 |", text)
        self.assertIn("| Configured HTTP and stream retries | 0 |", text)
        self.assertIn("| Cross-request state contract | Fresh process and ephemeral thread |", text)
        self.assertIn("| Planning cap, credit equivalents (not an invoice cap) | 20 |", text)
        self.assertIn("| Settled conservative credit equivalents | 0.007 |", text)
        self.assertIn("| Subscription credits consumed | unknown |", text)
        self.assertIn("| Verified subscription charge bound | unknown |", text)
        self.assertIn("| Hard output token cap | unknown |", text)
        self.assertIn("| Published output maximum used for planning | 128000 |", text)
        self.assertIn("0.005 reported (1/1 attempts measured)", text)

    def test_inconsistent_reference_and_accounting_fail_closed(self):
        summary, _ = execute(FakeClient("optimal"), cap=0)
        bad = deepcopy(summary)
        bad["request_attempts"] = 50
        with self.assertRaisesRegex(ValueError, "reconcile"):
            report(bad)
        bad = deepcopy(summary)
        bad["stage_b"][0]["fixed_policy_reference"]["skip"]["synthetic_cost_units"] = 999
        with self.assertRaisesRegex(ValueError, "references disagree"):
            report(bad)
        bad = deepcopy(summary)
        bad["stage_b"][0]["split"] = "heldout"
        with self.assertRaisesRegex(ValueError, "development split"):
            report(bad)
        bad = deepcopy(summary)
        bad["attempt_status_counts"]["reserved"] = 1
        with self.assertRaisesRegex(ValueError, "status counts"):
            report(bad)
        bad = deepcopy(summary)
        bad["request_metrics"] = [{}]
        with self.assertRaisesRegex(ValueError, "Metric coverage"):
            report(bad)


if __name__ == "__main__":
    unittest.main()
