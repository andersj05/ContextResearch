"""Synthetic saved-evidence checks; no model calls or historical-source edits."""
from copy import deepcopy
from decimal import Decimal
import hashlib
import json
from pathlib import Path
import tempfile
import unittest

from validate_context_repo import _canonical_hash, validate_luna_runs


def encode(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def budget(generations=0, failed=False):
    committed = Decimal("10.4025") if failed else Decimal("0.00745") * generations
    values = {"cap_credit_equivalent": Decimal(20), "per_attempt_reservation": Decimal("10.4025"),
              "committed_credit_equivalent": committed,
              "settled_credit_equivalent": Decimal(0) if failed else committed,
              "uncertain_credit_reservations": committed if failed else Decimal(0),
              "remaining_credit_equivalent": Decimal(20) - committed}
    result = {key: float(value) for key, value in values.items()}
    result.update({key + "_exact": str(value) for key, value in values.items()})
    result.update(generation_attempts=generations, generation_attempt_ceiling=96,
                  settled_attempts=0 if failed else generations, failed_attempts=int(failed),
                  pending_ticket=None, api_dollar_spend_authorized=0, api_key_fallback=False,
                  credit_purchases=0, reset_redemptions=0)
    return result


def fixture(generations=1, *, preflight_failure=False, failed_generation=False):
    transport = {"model": "gpt-5.6-luna", "budget": budget(),
                 "source_sha256": {"historical_file_does_not_need_to_exist.py": "a" * 64}}
    manifest = {"request_cap": 96, "split": "development", "heldout_requests": 0,
                "stage_b": [], "transport": transport}
    request = '{"kind":"inspection","synthetic":true}'
    rows = []
    for number in range(1, generations + 1):
        current = budget(number, failed_generation)
        accounting = {"ticket": number, "status": "settled", "budget": current,
                      "conservative_credit_equivalent_exact": "0.00745",
                      "conservative_credit_equivalent": 0.00745,
                      "usage": {"inputTokens": 1000, "cachedInputTokens": 100,
                                "cacheWriteInputTokens": 0, "outputTokens": 40,
                                "reasoningOutputTokens": 20, "totalTokens": 1040}}
        if failed_generation:
            accounting = {"ticket": number, "status": "reservation_retained", "budget": current}
        row = {"attempt": number, "evaluator_id": f"calibration/synthetic/{number}",
               "request_utf8": request, "request_bytes": len(request.encode()),
               "request_sha256": hashlib.sha256(request.encode()).hexdigest(),
               "status": "transport_failure" if failed_generation else "completed",
               "latency_seconds": 1,
               "provider_metadata": {"dispatched": True, "model": "gpt-5.6-luna",
                   "harness_termination": "session_budget_exceeded", "credit_accounting": accounting}}
        rows.append(row)
    if preflight_failure:
        rows.append({"attempt": 1, "evaluator_id": "calibration/synthetic/1",
                     "request_utf8": request, "request_bytes": len(request.encode()),
                     "request_sha256": hashlib.sha256(request.encode()).hexdigest(),
                     "status": "transport_failure", "latency_seconds": 1,
                     "provider_metadata": {"dispatched": False}})
    summary = {"fake": False, "manifest_sha256": _canonical_hash(manifest),
               "request_audit_sha256": _canonical_hash(rows), "request_cap": 96,
               "request_attempts": len(rows), "model_requests": generations,
               "heldout_requests": 0, "stage_b": [], "transport_manifest": deepcopy(transport),
               "attempt_status_counts": {key: sum(row["status"] == key for row in rows)
                   for key in ("completed", "policy_failure", "transport_failure", "reserved")},
               "cost_accounting": {"api_dollars": 0, "credit_budget": budget(generations, failed_generation)}}
    return manifest, rows, summary


def save(root, name, values, *, rehash=False):
    manifest, rows, summary = deepcopy(values)
    if rehash:
        summary["manifest_sha256"] = _canonical_hash(manifest)
        summary["request_audit_sha256"] = _canonical_hash(rows)
    directory = root / ("luna_development_" + name)
    directory.mkdir()
    (directory / "manifest.json").write_text(encode(manifest), encoding="utf-8")
    (directory / "requests.jsonl").write_text("".join(encode(row) + "\n" for row in rows), encoding="utf-8")
    (directory / "summary.json").write_text(encode(summary), encoding="utf-8")
    return directory


class LunaEvidenceTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)

    def tearDown(self):
        self.temporary.cleanup()

    def test_valid_run_and_nondispatched_failure_are_counted_separately(self):
        save(self.root, "valid", fixture(2))
        save(self.root, "preflight", fixture(0, preflight_failure=True))
        counts, errors = validate_luna_runs(self.root)
        self.assertEqual(errors, [])
        self.assertEqual(counts["luna_development_runs"], 2)
        self.assertEqual(counts["luna_development_request_rows"], 3)
        self.assertEqual(counts["completed_pilot_model_requests"], 2)
        self.assertEqual(Decimal(counts["luna_credit_equivalent_committed"]), Decimal("0.0149"))

    def test_manifest_and_ledger_outer_hashes_are_checked(self):
        for index, key in enumerate(("manifest_sha256", "request_audit_sha256")):
            values = fixture()
            values[2][key] = "0" * 64
            save(self.root, str(index), values)
        _, errors = validate_luna_runs(self.root)
        self.assertEqual(len(errors), 2)
        self.assertTrue(all("hash mismatch" in error for error in errors))

    def test_request_bytes_and_inner_hash_survive_rehashed_outer_ledger(self):
        for index, key in enumerate(("request_bytes", "request_sha256")):
            values = fixture()
            values[1][0][key] = 1 if key == "request_bytes" else "0" * 64
            save(self.root, str(index), values, rehash=True)
        _, errors = validate_luna_runs(self.root)
        self.assertEqual(len(errors), 2)
        self.assertTrue(any("byte-length" in error for error in errors))
        self.assertTrue(any("request hash" in error for error in errors))

    def test_status_and_generation_counts_are_recomputed(self):
        first = fixture()
        first[2]["attempt_status_counts"]["completed"] = 0
        save(self.root, "status", first)
        second = fixture()
        second[2]["model_requests"] = 0
        save(self.root, "generation", second)
        _, errors = validate_luna_runs(self.root)
        self.assertEqual(len(errors), 2)

    def test_combined_generation_ceiling_applies_across_directories(self):
        save(self.root, "a", fixture(49))
        save(self.root, "b", fixture(48))
        counts, errors = validate_luna_runs(self.root)
        self.assertEqual(counts["completed_pilot_model_requests"], 97)
        self.assertEqual(errors, ["Combined Luna development model dispatches exceed the 96-request tranche"])

    def test_uncertain_generation_retains_budget_and_combined_cap(self):
        for name in ("a", "b"):
            save(self.root, name, fixture(1, failed_generation=True))
        counts, errors = validate_luna_runs(self.root)
        self.assertEqual(counts["completed_pilot_model_requests"], 2)
        self.assertEqual(counts["completed_pilot_model_responses"], 0)
        self.assertEqual(errors, ["Combined Luna development credit equivalents exceed the 20-credit tranche"])

    def test_heldout_data_are_rejected(self):
        values = fixture()
        values[0]["stage_b"] = [{"split": "heldout"}]
        save(self.root, "heldout", values, rehash=True)
        _, errors = validate_luna_runs(self.root)
        self.assertIn("non-development episode", errors[0])

    def test_credit_equivalent_is_recomputed_from_tokens(self):
        values = fixture()
        accounting = values[1][0]["provider_metadata"]["credit_accounting"]
        accounting["conservative_credit_equivalent_exact"] = "0.00001"
        save(self.root, "underpriced", values, rehash=True)
        _, errors = validate_luna_runs(self.root)
        self.assertIn("disagrees with token accounting", errors[0])

    def test_historical_source_hash_need_not_match_current_checkout(self):
        save(self.root, "history", fixture())
        _, errors = validate_luna_runs(self.root)
        self.assertEqual(errors, [])

    def test_in_progress_directory_waits_for_summary(self):
        directory = self.root / "luna_development_in_progress"
        directory.mkdir()
        (directory / "requests.jsonl").write_text("incomplete", encoding="utf-8")
        counts, errors = validate_luna_runs(self.root)
        self.assertEqual(errors, [])
        self.assertEqual(counts["luna_development_runs"], 0)

    def test_completed_summary_requires_ledger_and_manifest(self):
        directory = save(self.root, "missing", fixture())
        (directory / "requests.jsonl").unlink()
        _, errors = validate_luna_runs(self.root)
        self.assertIn("missing manifest, request ledger, or summary", errors[0])


if __name__ == "__main__":
    unittest.main()
