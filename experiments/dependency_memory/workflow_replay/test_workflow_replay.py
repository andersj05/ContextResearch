"""Independent source semantics, deletion, provenance and resource invariants."""
from copy import deepcopy
from itertools import product
import json
import unittest

from experiments.dependency_memory.workflow_replay.evidence import (
    classify, decode_fields, encode_fields, historical_classifier, load_snapshot,
    make_scoped_receipt, original_decision, project, reuse_receipt, wire)
from experiments.dependency_memory.workflow_replay.replay import (
    Archive, Exhausted, METHODS, Meter, continue_route, entry_for, finish,
    narrow, pack, prepare, unpack)
from experiments.dependency_memory.workflow_replay.run import (
    cache_controls, evaluate, expected_action, frontier, routes, status_failure_witness)


def adversarial_records():
    """Cross validity axes independently of the policy implementation."""
    for status, flag, ticket, account_status, amount in product(
            ("completed", "policy_failure", "transport_failure", "unfinished"),
            (True, False, None, 1), (1, 0, True),
            ("settled", "reservation_retained", "missing"),
            ("0", "0.012300", "10.4025", "10.4026", "-1", "NaN", "bad", 0, None)):
        yield {"status": status, "provider_metadata": {
            "dispatched": flag, "attempt_ticket": ticket,
            "credit_accounting": {"ticket": 1, "status": account_status,
                                  "conservative_credit_equivalent_exact": amount}}}
    for status, meta, error in product(
            ("completed", "transport_failure", None),
            ({}, None, [], False, {"unrelated": 1}, {"dispatched": False},
             {"dispatched": False, "usage": None}, {"dispatched": False, "turn_id": None},
             {"dispatched": False, "attempt_ticket": None},
             {"dispatched": False, "credit_accounting": None}),
            ("StudyStopped", "TransportError", None)):
        yield {"status": status, "provider_metadata": deepcopy(meta), "error_type": error}
    yield {}
    yield {"status": "transport_failure", "error_type": "StudyStopped"}


class ReplayTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.records, cls.provenance = load_snapshot()
        original = historical_classifier()
        cls.reference = staticmethod(lambda row: original_decision(row, original))

    def test_mined_records_match_original_classifier_and_saved_certificate(self):
        self.assertEqual(len(self.records), 8)
        self.assertEqual(len({r["request_sha256"] for r in self.records}), 8)
        failures = [r for r in self.records if r["status"] == "transport_failure"]
        self.assertEqual(len(failures), 4)
        self.assertEqual(sorted(self.reference(r)[0] for r in failures),
                         ["dispatched"] * 3 + ["preflight_only"])
        for row, source in zip(self.records, self.provenance):
            self.assertEqual(source["historical_decision"], self.reference(row))
            self.assertEqual(source["array_index"], row["attempt"] - 1)

    def test_status_only_retry_and_hold_plans_have_concrete_delayed_failures(self):
        witness = status_failure_witness(self.records, self.reference)
        self.assertEqual(len(witness["retry_all_duplicate_dispatch_ids"]), 3)
        self.assertEqual(len(witness["hold_all_missed_eligible_ids"]), 1)
        self.assertEqual(set(witness["case_ids"]), set(witness["correct_first_submission_ids"]) |
                         set(witness["retry_all_duplicate_dispatch_ids"]))

    def test_independent_original_semantics_and_lossless_projection(self):
        count = 0
        for row in adversarial_records():
            expected = self.reference(row)
            projected = project(row)
            with self.subTest(row=row):
                self.assertEqual(classify(row), expected)
                self.assertEqual(self.reference(projected), expected)
                self.assertEqual(classify(projected), expected)
                self.assertEqual(decode_fields(encode_fields(projected)), projected)
            count += 1
        self.assertEqual(count, 1388)

    def test_zero_missing_and_uncertain_accounting_are_distinct(self):
        row = deepcopy(self.records[0])
        account = row["provider_metadata"]["credit_accounting"]
        account["conservative_credit_equivalent_exact"] = "0"
        self.assertEqual(classify(row), ["dispatched", "0", "0"])
        del account["conservative_credit_equivalent_exact"]
        self.assertEqual(classify(row), ["unknown", None, None])
        row["status"] = "transport_failure"
        account["status"] = "reservation_retained"
        self.assertEqual(classify(row), ["dispatched_uncertain", "0", "10.4025"])

    def test_first_memory_cannot_depend_on_future_pair_or_target(self):
        before = prepare(self.records, "repair", 1536, 65536, 128, self.reference)
        original_bytes = before[0]
        archive = Archive(self.records, "none")
        for pair, target in routes(self.records):
            continue_route(before, pair, target["case_id"], 768, archive,
                           expected_action(target, self.reference))
        self.assertEqual(before[0], original_bytes)
        self.assertEqual(before, prepare(self.records, "repair", 1536, 65536, 128, self.reference))
        self.assertFalse(any(r["request_utf8"].encode() in original_bytes for r in self.records))

    def test_executor_does_not_recover_evicted_values_without_archive(self):
        # Omit every entry. Only the late case identifier is public.
        target = self.records[0]["case_id"]
        meter = Meter(10000, 128)
        action, available = finish(pack([], 256), target, Archive(self.records, "none"), meter)
        self.assertFalse(available)
        self.assertIsNone(action["request_sha256"])
        self.assertEqual(action["classification"], "unknown")
        self.assertEqual(meter.tools, 0)

    def test_both_byte_limits_are_enforced_on_real_serializations(self):
        for parent_cap, child_cap in ((512, 256), (1024, 512), (1536, 768), (4096, 2048)):
            for method in METHODS:
                parent, meter = prepare(self.records, method, parent_cap, 65536, 128, self.reference)
                self.assertLessEqual(len(parent), parent_cap)
                child = narrow(parent, (1, 3), child_cap, meter)
                self.assertLessEqual(len(child), child_cap)
                self.assertTrue(all(e[0] in (1, 3) for e in unpack(child)))
                self.assertTrue(all(e in unpack(parent) for e in unpack(child)))
        rows = evaluate(self.records, self.reference, "direct_receipts", (1536, 256),
                        65536, 128, Archive(self.records, "none"))
        self.assertLess(sum(r["success"] for r in rows), 24)
        self.assertTrue(all(r["parent_entries"] == 8 for r in rows))

    def test_wide_memory_is_a_null_control_for_lossless_fields(self):
        for method in ("fields", "compact_fields", "repair", "direct_receipts"):
            rows = evaluate(self.records, self.reference, method, (4096, 2048),
                            65536, 128, Archive(self.records, "none"))
            self.assertTrue(all(r["success"] for r in rows))

    def test_exact_identity_and_decimal_amounts_survive_two_deletions(self):
        rows = evaluate(self.records, self.reference, "repair", (1536, 768),
                        16384, 128, Archive(self.records, "none"), detailed=True)
        self.assertTrue(all(r["success"] for r in rows))
        for row in rows:
            self.assertEqual(row["action"], row["expected"])
            self.assertEqual(len(row["action"]["request_sha256"]), 64)
            self.assertEqual(row["tool_calls"], 0)

    def test_event_ledger_independently_reconciles_all_resources(self):
        for method, mode, allowance in product(METHODS, ("none", "full", "projected"), (1024, 16384)):
            rows = evaluate(self.records, self.reference, method, (1536, 768),
                            allowance, 128, Archive(self.records, mode), detailed=True)
            for row in rows:
                self.assertEqual(row["bytes"], sum(e["bytes"] for e in row["events"]))
                self.assertEqual(row["checks"], sum(e["checks"] for e in row["events"]))
                self.assertEqual(row["tool_calls"], sum(e["tools"] for e in row["events"]))
                self.assertEqual(row["cost"], row["bytes"] + 128 * (row["checks"] + row["tool_calls"]))
                self.assertEqual(row["cost"], sum(e["cost"] for e in row["events"]))
                self.assertLessEqual(row["cost"], row["allowance"])
                self.assertEqual(row["events"][0]["bytes"], len(wire(self.records)))
                if row["budget_rejected_at"]:
                    self.assertFalse(row["success"])

    def test_budget_rejection_keeps_prior_cost_without_a_free_answer(self):
        meter = Meter(200, 128)
        meter.charge("already_done", byte_count=100)
        with self.assertRaises(Exhausted):
            meter.charge("too_expensive", checks=1)
        self.assertEqual(meter.spent, 100)
        self.assertEqual(meter.checks, 0)
        self.assertEqual(meter.rejected, "too_expensive")

    def test_archive_modes_recover_same_facts_with_explicit_costs(self):
        target = self.records[0]["case_id"]
        outcomes, costs = [], []
        for mode in ("full", "projected"):
            meter = Meter(100000, 128)
            action, available = finish(pack([], 256), target, Archive(self.records, mode), meter)
            self.assertFalse(available)
            self.assertEqual(meter.tools, 1)
            self.assertEqual(meter.checks, 1 if mode == "full" else 2)
            self.assertTrue(any(e["operation"] == "archive_response" for e in meter.events))
            outcomes.append(action)
            costs.append(meter.spent)
        self.assertEqual(outcomes[0], outcomes[1])
        self.assertLess(costs[1], costs[0])

    def test_allowance_frontier_matches_actual_budget_enforcement(self):
        archive = Archive(self.records, "full")
        unlimited = {m: evaluate(self.records, self.reference, m, (1536, 768),
                                 10**9, 128, archive) for m in METHODS}
        common = len(wire(self.records))
        points = frontier(unlimited, common)
        # Exact threshold and the byte just below each threshold.
        for point in points:
            for offset in (-1, 0):
                extra = point["extra_allowance"] + offset
                for method in METHODS:
                    actual = evaluate(self.records, self.reference, method, (1536, 768), extra, 128, archive)
                    expected = sum(r["success"] and r["cost"] <= common + extra for r in unlimited[method])
                    self.assertEqual(sum(r["success"] for r in actual), expected)

    def test_direct_rule_baseline_matches_repair_and_costs_less(self):
        for mode in ("none", "full", "projected"):
            archive = Archive(self.records, mode)
            repair = evaluate(self.records, self.reference, "repair", (1536, 768), 65536, 128, archive)
            direct = evaluate(self.records, self.reference, "direct_receipts", (1536, 768), 65536, 128, archive)
            for a, b in zip(repair, direct):
                self.assertEqual(a["success"], b["success"])
                self.assertEqual(a["parent_bytes"], b["parent_bytes"])
                self.assertLess(b["cost"], a["cost"])

    def test_receipt_scope_invalidates_relevant_changes_but_reuses_unrelated_edits(self):
        controls = cache_controls(self.records, self.reference)
        reusable = {r["control"] for r in controls if r["reuse"]}
        self.assertEqual(reusable, {"unchanged", "irrelevant_latency", "irrelevant_quota_metadata"})
        self.assertEqual(sum(r["naive_unscoped_result_stale"] for r in controls), 4)
        for row in controls:
            if row["reuse"]:
                self.assertEqual(row["reused_result"], row["current_decision"])
            self.assertGreater(row["current_evidence_read_bytes"], 0)

    def test_new_field_presence_cannot_be_hidden_by_a_cached_projection(self):
        row = deepcopy(next(r for r in self.records if r["provider_metadata"].get("dispatched") is False))
        receipt = make_scoped_receipt(row, "v1")
        row["provider_metadata"]["usage"] = None
        self.assertIsNone(reuse_receipt(receipt, row, "v1"))
        self.assertEqual(self.reference(row), ["unknown", None, None])


if __name__ == "__main__":
    unittest.main()
