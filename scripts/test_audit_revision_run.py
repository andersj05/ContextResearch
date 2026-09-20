"""Synthetic evidence tests; neither installed clients nor network are used."""
from copy import deepcopy
from decimal import Decimal
import json
from pathlib import Path
import tempfile
import unittest

from audit_revision_run import audit
from luna_appserver import LunaClient, ResponseFormatError
from luna_budget import CreditBudget
from luna_isolation import wire_body_byte_bound
from revision_diagnostic import FakeClient, digest, make_plan
from run_revision_diagnostic import atomic_json, execute


class SyntheticLive(LunaClient):
    """Budget/ledger fixture only; override initialization and all generation."""
    def __init__(self, cap=24, mode="optimal", fail=None):
        self.audit = {"launch_ready": True}
        self.budget = CreditBudget(12, cap)
        self.control = FakeClient(mode)
        self.fail = fail
        self.last_metadata = {}
        self.metadata = {"model": "gpt-5.6-luna", "experiment_version": "revision_parent_diagnostic_v1",
            "approved_plan_sha256": digest(make_plan()),
            "source_sha256": {"historical.py": "0" * 64}, "cli_sha256": "1" * 64,
            "isolation_profile_sha256": "2" * 64, "global_instructions_sha256": "3" * 64,
            "advertised_model": {"model": "gpt-5.6-luna"},
            "advertised_model_sha256": digest({"model": "gpt-5.6-luna"}),
            "provider": "luna_research", "reasoning_effort": "low", "service_tier": "default",
            "http_and_stream_retries": 0, "maximum_wire_body_bytes": 32768, "budget": self.budget.snapshot()}

    def complete(self, request):
        self.last_metadata = {"dispatched": False}
        if self.fail == "preflight":
            raise RuntimeError("synthetic preflight failure")
        ticket = self.budget.reserve()
        self.last_metadata.update(dispatched=True, attempt_ticket=ticket,
                                  wire_body_byte_bound=wire_body_byte_bound(request))
        if self.fail == "generation":
            self.last_metadata["credit_accounting"] = self.budget.fail(ticket, "generation_failure")
            raise RuntimeError("synthetic generation failure")
        usage = {"inputTokens": 1200, "cachedInputTokens": 200,
                 "outputTokens": 100, "reasoningOutputTokens": 80, "totalTokens": 1300}
        self.last_metadata.update(usage={"input_tokens": 1200, "cached_input_tokens": 200,
            "output_tokens": 100, "reasoning_output_tokens": 80, "cache_write_input_tokens": None},
            credit_accounting=self.budget.settle(ticket, usage), harness_termination="session_budget_exceeded",
            status="completed", model="gpt-5.6-luna", provider="luna_research", tool_events_observed=0,
            provider_generation_count_observed=1)
        if self.fail == "postsettlement":
            self.last_metadata["status"] = "failed"
            raise RuntimeError("synthetic post-settlement failure")
        if self.fail == "invalid_json":
            self.last_metadata["response_status"] = "invalid_json"
            raise ResponseFormatError("invalid_json")
        return self.control.complete(request)


class RevisionRunAuditTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.directory = Path(self.temporary.name) / "evidence"

    def run_fake(self, cap=24, mode="optimal"):
        execute(FakeClient(mode), output=self.directory, cap=cap)

    def run_live(self, cap=24, mode="optimal", fail=None):
        execute(SyntheticLive(cap, mode, fail), fake=False, cap=cap,
                output=self.directory, authorization="Synthetic test fixture, not a user allocation")

    def load(self):
        return [json.loads((self.directory / name).read_text(encoding="utf-8"))
                for name in ("manifest.json", "requests.json", "summary.json")]

    def save(self, manifest, ledger, summary):
        # Rehash after semantic tampering, so tests reach substantive checks.
        manifest["plan_sha256"] = digest(manifest["plan"])
        summary["manifest_sha256"] = digest(manifest)
        summary["request_audit_sha256"] = digest(ledger)
        for name, value in zip(("manifest.json", "requests.json", "summary.json"), (manifest, ledger, summary)):
            atomic_json(self.directory / name, value)

    def test_complete_fake_requires_explicit_opt_in_and_keeps_24_denominators(self):
        self.run_fake()
        with self.assertRaisesRegex(ValueError, "allow_fake"):
            audit(self.directory)
        result = audit(self.directory, allow_fake=True)
        self.assertEqual((result["planned_cases_checked"], result["requests_checked"], result["new_model_requests"]), (24, 24, 0))

    def test_partial_fake_has_all_scheduled_rows_without_imputation(self):
        self.run_fake(cap=3)
        self.assertEqual(audit(self.directory, allow_fake=True)["requests_checked"], 3)
        manifest, ledger, summary = self.load()
        summary["rows"][3]["grade"] = deepcopy(summary["rows"][0]["grade"])
        self.save(manifest, ledger, summary)
        with self.assertRaisesRegex(ValueError, "imputed"):
            audit(self.directory, allow_fake=True)

    def test_invalid_policy_is_not_treated_as_empty_valid_selection(self):
        self.run_fake(mode="invalid")
        result = audit(self.directory, allow_fake=True)
        self.assertEqual(result["status_counts"]["policy_failure"], 24)
        _, _, summary = self.load()
        self.assertTrue(all(row["mean_availability"] is None for row in summary["by_rule"]))

    def test_synthetic_live_usage_and_budget_reconcile(self):
        self.run_live()
        result = audit(self.directory)
        self.assertEqual(Decimal(result["settled_credit_equivalent"]), Decimal("0.252"))
        self.assertEqual(result["usage_totals"]["input_tokens"], 28800)

    def test_failed_generation_retains_full_reservation(self):
        self.run_live(fail="generation")
        result = audit(self.directory)
        self.assertEqual(result["retained_credit_equivalent"], "10.4025")
        self.assertEqual(result["status_counts"]["transport_failure"], 1)
        self.assertEqual(result["planned_cases_checked"], 24)

    def test_unknown_cache_write_count_cannot_be_replaced_with_zero(self):
        self.run_live(cap=1)
        manifest, ledger, summary = self.load()
        accounting = ledger[0]["provider_metadata"]["credit_accounting"]
        self.assertIsNone(accounting["usage"]["cacheWriteInputTokens"])
        self.assertIs(accounting["cache_write_tokens_reported"], False)
        self.assertIs(accounting["cache_write_pricing_unresolved"], True)
        accounting["usage"]["cacheWriteInputTokens"] = 0
        self.save(manifest, ledger, summary)
        with self.assertRaisesRegex(ValueError, "Token accounting differs"):
            audit(self.directory)

    def test_malformed_completed_answers_are_charged_and_do_not_stop_schedule(self):
        self.run_live(cap=3, fail="invalid_json")
        result = audit(self.directory)
        self.assertEqual(result["status_counts"]["policy_failure"], 3)
        self.assertEqual(result["status_counts"]["transport_failure"], 0)
        self.assertEqual(Decimal(result["settled_credit_equivalent"]), Decimal("0.0315"))
        manifest, ledger, summary = self.load()
        ledger[0]["provider_metadata"]["response_status"] = "completed"
        self.save(manifest, ledger, summary)
        with self.assertRaisesRegex(ValueError, "response-format evidence"):
            audit(self.directory)

    def test_preflight_failure_has_no_generation_or_charge(self):
        self.run_live(fail="preflight")
        result = audit(self.directory)
        self.assertEqual(result["settled_credit_equivalent"], "0")
        self.assertEqual(result["retained_credit_equivalent"], "0")

    def test_postsettlement_failure_retains_valid_usage_without_imputing_grade(self):
        self.run_live(fail="postsettlement")
        result = audit(self.directory)
        self.assertEqual(result["settled_credit_equivalent"], "0.0105")
        self.assertEqual(result["status_counts"]["transport_failure"], 1)

    def test_hash_and_byte_count_tampering_are_detected(self):
        self.run_fake()
        manifest, ledger, summary = self.load()
        summary["manifest_sha256"] = "0" * 64
        atomic_json(self.directory / "summary.json", summary)
        with self.assertRaisesRegex(ValueError, "Manifest hash"):
            audit(self.directory, allow_fake=True)
        ledger[0]["request_bytes"] += 1
        self.save(manifest, ledger, summary)
        with self.assertRaisesRegex(ValueError, "byte count"):
            audit(self.directory, allow_fake=True)

    def test_public_input_cannot_change_even_when_ledger_hash_is_updated(self):
        self.run_fake()
        manifest, ledger, summary = self.load()
        request = json.loads(ledger[0]["request_utf8"])
        request["evaluator_answer"] = ["job-4", "job-5"]
        ledger[0]["request_utf8"] = json.dumps(request)
        self.save(manifest, ledger, summary)
        with self.assertRaisesRegex(ValueError, "frozen public input"):
            audit(self.directory, allow_fake=True)

    def test_grade_and_positions_are_recomputed_independently(self):
        self.run_fake()
        initial = self.load()
        for field, value in (("grade", {"availability": "1"}), ("displayed_positions", [99, 100])):
            with self.subTest(field=field):
                manifest, ledger, summary = deepcopy(initial)
                summary["rows"][0][field] = value
                self.save(manifest, ledger, summary)
                with self.assertRaises(ValueError):
                    audit(self.directory, allow_fake=True)

    def test_accounting_tampering_is_rejected_after_hashes_are_updated(self):
        self.run_live()
        initial = self.load()
        for field, value in (("input_tokens", 0), ("reasoning_output_tokens", 101), ("output_tokens", 180)):
            with self.subTest(field=field):
                manifest, ledger, summary = deepcopy(initial)
                ledger[0]["provider_metadata"]["usage"][field] = value
                self.save(manifest, ledger, summary)
                with self.assertRaises(ValueError):
                    audit(self.directory)

    def test_larger_caps_or_missing_schedule_rows_cannot_be_hidden_by_hashes(self):
        self.run_fake()
        initial = self.load()
        manifest, ledger, summary = deepcopy(initial)
        manifest["request_cap"] = summary["request_cap"] = 25
        self.save(manifest, ledger, summary)
        with self.assertRaisesRegex(ValueError, "request cap"):
            audit(self.directory, allow_fake=True)
        manifest, ledger, summary = deepcopy(initial)
        summary["rows"].pop()
        summary["planned_cases"] = 23
        self.save(manifest, ledger, summary)
        with self.assertRaisesRegex(ValueError, "24 scheduled"):
            audit(self.directory, allow_fake=True)

    def test_historical_source_hashes_need_not_match_current_checkout(self):
        self.run_live()
        manifest, ledger, summary = self.load()
        manifest["plan"]["source_sha256"] = {"older_revision.py": "a" * 64}
        manifest["transport"]["approved_plan_sha256"] = digest(manifest["plan"])
        summary["transport_manifest"]["approved_plan_sha256"] = digest(manifest["plan"])
        self.save(manifest, ledger, summary)
        self.assertTrue(audit(self.directory)["passed"])
        manifest["plan"]["source_sha256"]["older_revision.py"] = "not-a-hash"
        self.save(manifest, ledger, summary)
        with self.assertRaisesRegex(ValueError, "provenance hash"):
            audit(self.directory)

    def test_budget_cap_inflation_and_guard_removal_are_rejected(self):
        self.run_live()
        initial = self.load()
        manifest, ledger, summary = deepcopy(initial)
        summary["credit_budget"]["cap_credit_equivalent"] = 20
        summary["credit_budget"]["cap_credit_equivalent_exact"] = "20"
        self.save(manifest, ledger, summary)
        with self.assertRaisesRegex(ValueError, "cap_credit_equivalent"):
            audit(self.directory)
        manifest, ledger, summary = deepcopy(initial)
        ledger[0]["provider_metadata"]["harness_termination"] = "completed"
        self.save(manifest, ledger, summary)
        with self.assertRaisesRegex(ValueError, "generation guard"):
            audit(self.directory)

    def test_saved_run_must_match_the_approved_plan_hash(self):
        self.run_live()
        manifest, ledger, summary = self.load()
        manifest["transport"]["approved_plan_sha256"] = "a" * 64
        summary["transport_manifest"]["approved_plan_sha256"] = "a" * 64
        self.save(manifest, ledger, summary)
        with self.assertRaisesRegex(ValueError, "Approved plan hash"):
            audit(self.directory)


if __name__ == "__main__":
    unittest.main()
