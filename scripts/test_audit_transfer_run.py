"""Independent saved-transfer evidence regressions; no model calls or clients."""
from copy import deepcopy
from decimal import Decimal
from fractions import Fraction
import hashlib
from itertools import combinations
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

import audit_transfer_run as audit_module
from audit_transfer_run import (audit, digest, independent_grade, live_accounting,
                               verify_source_commit)
from luna_isolation import wire_body_byte_bound
from run_revision_diagnostic import atomic_json
from run_transfer_study import TransferCreditBudget, execute
from transfer_interface import request_bytes
import transfer_study as study


class TransferSavedAuditTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.directory = Path(temporary.name) / "evidence"

    def fake(self, mode="optimal", cap=1):
        execute([study.FakeClient(mode) for _ in range(4)], output=self.directory,
                limit_per_worker=cap)

    def load(self, worker=None):
        directory = self.directory if worker is None else self.directory / f"worker-{worker}"
        names = ("manifest.json", "summary.json") if worker is None else ("manifest.json", "requests.json", "summary.json")
        return [json.loads((directory / name).read_text(encoding="utf-8")) for name in names]

    def save(self, worker, manifest, ledger, summary):
        directory = self.directory / f"worker-{worker}"
        summary["manifest_sha256"] = digest(manifest)
        summary["request_audit_sha256"] = digest(ledger)
        for name, value in zip(("manifest.json", "requests.json", "summary.json"), (manifest, ledger, summary)):
            atomic_json(directory / name, value)

    def test_fake_opt_in_and_all_1536_denominators(self):
        self.fake()
        with self.assertRaisesRegex(ValueError, "allow_fake"):
            audit(self.directory)
        result = audit(self.directory, allow_fake=True)
        self.assertEqual((result["planned_cases_checked"], result["requests_checked"], result["model_requests"]), (1536, 4, 0))
        self.assertEqual(result["source_blobs_checked"], 0)

    def test_invalid_policy_answers_remain_failures(self):
        self.fake("invalid")
        result = audit(self.directory, allow_fake=True)
        self.assertEqual(result["status_counts"]["policy_failure"], 4)
        _, summary = self.load()
        self.assertTrue(all(r["grade"] is None for r in summary["rows"]))

    def test_zero_request_fake_preserves_empty_usage_measurement(self):
        self.fake(cap=0)
        result = audit(self.directory, allow_fake=True)
        self.assertEqual(result["requests_checked"], 0)
        self.assertEqual(result["usage_totals"]["input_tokens"], {"reported": None, "measured_attempts": 0})

    def test_rehashed_input_and_grade_tampering_are_detected(self):
        self.fake()
        original = self.load(0)
        for mutation in ("input", "grade", "positions", "bytes"):
            with self.subTest(mutation=mutation):
                manifest, ledger, summary = deepcopy(original)
                if mutation == "input":
                    value = json.loads(ledger[0]["request_utf8"])
                    value["evaluator_answer"] = ["job-00"]
                    ledger[0]["request_utf8"] = json.dumps(value)
                elif mutation == "grade":
                    summary["rows"][0]["grade"]["availability"] = "1"
                elif mutation == "positions":
                    summary["rows"][0]["displayed_positions"] = [99, 100]
                else:
                    ledger[0]["request_bytes"] += 1
                self.save(0, manifest, ledger, summary)
                with self.assertRaises(ValueError):
                    audit(self.directory, allow_fake=True)

    def test_missing_outcome_cannot_be_imputed(self):
        self.fake()
        manifest, ledger, summary = self.load(0)
        summary["rows"][1]["grade"] = deepcopy(summary["rows"][0]["grade"])
        self.save(0, manifest, ledger, summary)
        with self.assertRaisesRegex(ValueError, "imputed"):
            audit(self.directory, allow_fake=True)

    def test_worker_attempt_count_and_cap_cannot_inflate(self):
        self.fake()
        manifest, ledger, summary = self.load(0)
        manifest["request_cap"] = summary["request_cap"] = 385
        self.save(0, manifest, ledger, summary)
        with self.assertRaisesRegex(ValueError, "allocation"):
            audit(self.directory, allow_fake=True)

    def test_aggregate_analysis_and_report_are_recomputed(self):
        self.fake()
        _, summary = self.load()
        summary["primary"]["scheduled_pairs"] = 127
        atomic_json(self.directory / "summary.json", summary)
        with self.assertRaisesRegex(ValueError, "analysis mismatch"):
            audit(self.directory, allow_fake=True)
        summary["primary"]["scheduled_pairs"] = 128
        atomic_json(self.directory / "summary.json", summary)
        with (self.directory / "report.md").open("a", encoding="utf-8") as output:
            output.write("unsupported conclusion\n")
        with self.assertRaisesRegex(ValueError, "report differs"):
            audit(self.directory, allow_fake=True)

    def test_frozen_commit_checks_raw_blobs_not_current_files(self):
        root = self.directory
        root.mkdir()
        args = ["git", "-c", "safe.directory=" + root.as_posix()]
        for command in (["init"], ["config", "user.email", "fixture@example.invalid"],
                        ["config", "user.name", "Test Fixture"], ["config", "core.autocrlf", "false"]):
            subprocess.run([*args, *command], cwd=root, capture_output=True, check=True)
        source = root / "source.py"
        frozen_bytes = b"# exact CRLF bytes\r\nvalue = 1\r\n"
        source.write_bytes(frozen_bytes)
        subprocess.run([*args, "add", "source.py"], cwd=root, capture_output=True, check=True)
        subprocess.run([*args, "commit", "-m", "Synthetic provenance fixture"], cwd=root, capture_output=True, check=True)
        commit = subprocess.run([*args, "rev-parse", "HEAD"], cwd=root, capture_output=True, check=True).stdout.decode().strip()
        hashes = {"source.py": hashlib.sha256(frozen_bytes).hexdigest()}
        source.write_text("changed checkout\n", encoding="utf-8")
        result = verify_source_commit(hashes, commit, root)
        self.assertEqual(result["source_blobs_checked"], 1)
        with self.assertRaisesRegex(ValueError, "hash mismatch"):
            verify_source_commit({"source.py": "0" * 64}, commit, root)
        with self.assertRaisesRegex(ValueError, "Missing frozen"):
            verify_source_commit({"missing.py": "0" * 64}, commit, root)
        with self.assertRaisesRegex(ValueError, "requires --source-commit"):
            verify_source_commit(hashes, None, root)


class IndependentTransferGradeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        plan = study.make_plan()
        cls.cases = [next(c for c in plan["cases"] if c["jobs"] == n and c["refresh_rule"] == rule)
                     for n in (6, 12) for rule in ("first", "last", "none")]

    def test_exhaustive_parent_choices_match_declared_grader(self):
        for case in self.cases:
            keys = [r["key"] for r in case["request"]["public_metadata"]["jobs"]]
            for size in range(3):
                for selected in combinations(keys, size):
                    with self.subTest(jobs=case["jobs"], rule=case["refresh_rule"], selected=selected):
                        self.assertEqual(independent_grade(selected, case), study.grade(selected, case))

    def test_underfilling_can_exceed_full_pair_normalization_range(self):
        case = next(c for c in self.cases if c["jobs"] == 12 and c["refresh_rule"] == "first")
        grade = independent_grade((), case)
        self.assertEqual(Fraction(grade["availability"]), Fraction(1, 2))
        self.assertGreater(Fraction(grade["normalized_regret"]), 1)


class IndependentTransferAccountingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.plan = study.make_plan()

    def fixture(self, statuses=("completed",), *, writes=None):
        plan = self.plan
        budget = TransferCreditBudget()
        transport = {"worker": 0, "model": "gpt-5.6-luna", "experiment_version": "transfer_study_v1",
            "approved_plan_sha256": digest(plan), "source_sha256": plan["source_sha256"],
            "cli_sha256": "1" * 64, "isolation_profile_sha256": "2" * 64,
            "global_instructions_sha256": "3" * 64, "advertised_model": {"model": "gpt-5.6-luna"},
            "advertised_model_sha256": digest({"model": "gpt-5.6-luna"}), "provider": "luna_research",
            "reasoning_effort": "low", "service_tier": "default", "http_and_stream_retries": 0,
            "maximum_wire_body_bytes": 32768, "budget": budget.snapshot()}
        manifest = {"worker": 0, "transport": transport, "authorization": "Synthetic fixture; no model allocation"}
        ledger = []
        for index, status in enumerate(statuses):
            request = plan["cases"][index]["request"]
            meta = {"dispatched": False}
            if status != "preflight":
                ticket = budget.reserve()
                meta.update(dispatched=True, thread_id=f"synthetic-thread-{index}", attempt_ticket=ticket,
                            wire_body_byte_bound=wire_body_byte_bound(request))
                if status == "uncertain":
                    meta["credit_accounting"] = budget.fail(ticket, "generation_failure")
                else:
                    usage = {"inputTokens": 1200, "cachedInputTokens": 200, "outputTokens": 100,
                             "reasoningOutputTokens": 80, "totalTokens": 1300}
                    if writes is not None:
                        usage["cacheWriteInputTokens"] = writes
                    meta.update(usage={"input_tokens": 1200, "cached_input_tokens": 200,
                        "output_tokens": 100, "reasoning_output_tokens": 80, "cache_write_input_tokens": writes},
                        credit_accounting=budget.settle(ticket, usage), harness_termination="session_budget_exceeded",
                        status="completed", model="gpt-5.6-luna", provider="luna_research",
                        tool_events_observed=0, provider_generation_count_observed=1)
                    if status == "postsettlement":
                        meta["status"] = "failed"
                    if status == "malformed":
                        meta["response_status"] = "invalid_json"
            row_status = ("transport_failure" if status in ("preflight", "uncertain", "postsettlement")
                          else "policy_failure" if status == "malformed" else "completed")
            ledger.append({"status": row_status, "provider_metadata": meta,
                           "request_utf8": request_bytes(request).decode("utf-8")})
        summary = {"transport_manifest": transport, "credit_budget": budget.snapshot(),
                   "model_requests": budget.attempts}
        return ledger, summary, manifest, plan

    def test_settled_malformed_outputs_are_charged_without_stopping(self):
        fixture = self.fixture(("malformed", "completed", "malformed"))
        threads = set()
        spent, uncertain = live_accounting(*fixture, threads)
        self.assertEqual((spent, uncertain, len(threads)), (Decimal("0.0315"), Decimal(0), 3))

    def test_preflight_uncertainty_and_postsettlement_preserve_distinct_costs(self):
        for status, expected in (("preflight", (Decimal(0), Decimal(0))),
                ("uncertain", (Decimal(0), Decimal("10.4025"))),
                ("postsettlement", (Decimal("0.0105"), Decimal(0)))):
            with self.subTest(status=status):
                self.assertEqual(live_accounting(*self.fixture((status,)), set()), expected)

    def test_missing_cache_measurement_cannot_be_changed_to_zero(self):
        ledger, summary, manifest, plan = self.fixture()
        ledger[0]["provider_metadata"]["credit_accounting"]["usage"]["cacheWriteInputTokens"] = 0
        with self.assertRaisesRegex(ValueError, "differs from provider"):
            live_accounting(ledger, summary, manifest, plan, set())

    def test_cross_worker_duplicate_thread_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "duplicate thread"):
            live_accounting(*self.fixture(), {"synthetic-thread-0"})

    def test_accounting_and_guard_tampering_fail_after_valid_hashes(self):
        for field, value in (("input_tokens", 0), ("reasoning_output_tokens", 101), ("output_tokens", 101)):
            with self.subTest(field=field):
                ledger, summary, manifest, plan = self.fixture()
                ledger[0]["provider_metadata"]["usage"][field] = value
                with self.assertRaises(ValueError):
                    live_accounting(ledger, summary, manifest, plan, set())
        ledger, summary, manifest, plan = self.fixture()
        ledger[0]["provider_metadata"]["harness_termination"] = "completed"
        with self.assertRaisesRegex(ValueError, "generation guard"):
            live_accounting(ledger, summary, manifest, plan, set())

    def test_credit_cap_and_generation_ceiling_cannot_be_enlarged(self):
        for field, value in (("cap_credit_equivalent", 200), ("generation_attempt_ceiling", 1536)):
            ledger, summary, manifest, plan = self.fixture()
            summary["credit_budget"][field] = value
            if field + "_exact" in summary["credit_budget"]:
                summary["credit_budget"][field + "_exact"] = str(value)
            with self.assertRaises(ValueError):
                live_accounting(ledger, summary, manifest, plan, set())

    def amended_fixture(self, status="completed", used=85):
        ledger, summary, manifest, plan = self.fixture((status,))
        manifest["transport"].update(quota_guard_used_percent=100, account_quota_stop_used_percent=100)
        quota = {"codex": {"primary": {"usedPercent": used}, "secondary": None,
                 "rateLimitReachedType": None, "individualLimit": None, "spendControlReached": False}}
        ledger[0]["provider_metadata"].update(quota_guard_used_percent=100,
            quota_before=deepcopy(quota), quota_after=deepcopy(quota))
        return ledger, summary, manifest, plan

    def test_amended_ceiling_accepts_85_percent_with_both_recorded_checks(self):
        self.assertEqual(live_accounting(*self.amended_fixture(), set()), (Decimal("0.0105"), Decimal(0)))

    def test_amended_ceiling_rejects_exhaustion_provider_denial_and_missing_snapshots(self):
        for mutation in ("exhausted", "denied", "missing", "wrong_ceiling"):
            with self.subTest(mutation=mutation):
                ledger, summary, manifest, plan = self.amended_fixture()
                meta = ledger[0]["provider_metadata"]
                if mutation == "exhausted":
                    meta["quota_before"]["codex"]["primary"]["usedPercent"] = 100
                elif mutation == "denied":
                    meta["quota_before"]["codex"]["rateLimitReachedType"] = "usage"
                elif mutation == "missing":
                    meta.pop("quota_after")
                else:
                    meta["quota_guard_used_percent"] = 80
                with self.assertRaises(ValueError):
                    live_accounting(ledger, summary, manifest, plan, set())

    def test_after_generation_exhaustion_preserves_settled_failure_usage(self):
        ledger, summary, manifest, plan = self.amended_fixture(status="postsettlement")
        ledger[0]["provider_metadata"]["quota_after"]["codex"]["primary"]["usedPercent"] = 100
        self.assertEqual(live_accounting(ledger, summary, manifest, plan, set()), (Decimal("0.0105"), Decimal(0)))

    def test_zero_generation_preflight_and_new_run_share_one_allocation(self):
        with tempfile.TemporaryDirectory() as temporary:
            directories = [Path(temporary) / name for name in ("old", "new")]
            for directory in directories:
                directory.mkdir()
                atomic_json(directory / "manifest.json", {"plan": {"cases": [
                    {"case_id": "same-public-case", "request_sha256": "a" * 64}]}})
            old = {"model_requests": 0, "requests_checked": 4,
                   "settled_credit_equivalent": "0", "retained_credit_equivalent": "0"}
            new = {"model_requests": 1536, "requests_checked": 1536,
                   "settled_credit_equivalent": "50", "retained_credit_equivalent": "0"}
            with patch.object(audit_module, "audit", side_effect=[old, new]):
                result = audit_module.audit_allocation(directories)
            self.assertEqual((result["model_requests"], result["requests_checked"]), (1536, 1540))
            with patch.object(audit_module, "audit", side_effect=[{**old, "model_requests": 1}, new]):
                with self.assertRaisesRegex(ValueError, "zero-generation"):
                    audit_module.audit_allocation(directories)


if __name__ == "__main__":
    unittest.main()
