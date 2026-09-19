from decimal import Decimal
import json
import unittest

from luna_budget import (
    BudgetExceeded, BudgetStopped, CreditBudget, InvalidUsage,
    PER_ATTEMPT_RESERVATION, usage_estimates,
)


def usage(**overrides):
    result = {"inputTokens": 1000, "cachedInputTokens": 200,
              "outputTokens": 100, "reasoningOutputTokens": 80}
    result.update(overrides)
    return result


class CreditBudgetTests(unittest.TestCase):
    def test_reservation_matches_independent_maximum_calculation(self):
        self.assertEqual(PER_ATTEMPT_RESERVATION, Decimal("10.4025"))
        self.assertEqual(PER_ATTEMPT_RESERVATION,
                         (Decimal(1_050_000) * Decimal(5) * Decimal("1.25")
                          + Decimal(128_000) * Decimal(30)) / 1_000_000)

    def test_decimal_boundary_and_no_dispatch_on_shortfall(self):
        exact = CreditBudget("10.4025")
        self.assertEqual(exact.reserve(), 1)
        short = CreditBudget("10.402499999999999999")
        with self.assertRaises(BudgetExceeded):
            short.reserve()
        self.assertEqual(short.snapshot()["generation_attempts"], 0)
        self.assertIsNone(short.snapshot()["pending_ticket"])

    def test_credit_estimates_keep_reasoning_within_output(self):
        result = usage_estimates(usage())
        self.assertEqual(Decimal(result["conservative_credit_equivalent_exact"]), Decimal("0.00925"))
        self.assertEqual(Decimal(result["basic_rate_credit_estimate_exact"]), Decimal("0.0071"))
        self.assertIsNone(result["observed_dollar_charge"])
        self.assertIsNone(result["observed_credit_balance_debit"])

    def test_unknown_cache_write_price_keeps_conservative_margin(self):
        result = usage_estimates(usage(cacheWriteInputTokens=300))
        self.assertTrue(result["cache_write_pricing_unresolved"])
        self.assertEqual(result["conservative_credit_equivalent"], 0.00925)

    def test_settlement_releases_reservation_then_allows_next(self):
        ledger = CreditBudget()
        first = ledger.reserve()
        with self.assertRaises(BudgetStopped):
            ledger.reserve()
        result = ledger.settle(first, usage())
        self.assertEqual(result["status"], "settled")
        self.assertEqual(ledger.committed, Decimal("0.00925"))
        self.assertEqual(ledger.reserve(), 2)

    def test_failure_retains_full_reservation_and_stops(self):
        ledger = CreditBudget()
        ticket = ledger.reserve()
        ledger.fail(ticket)
        state = ledger.snapshot()
        self.assertEqual(state["committed_credit_equivalent"], 10.4025)
        self.assertEqual(state["failed_attempts"], 1)
        self.assertEqual(state["uncertain_credit_reservations"], 10.4025)
        with self.assertRaises(BudgetStopped):
            ledger.reserve()

    def test_invalid_usage_preserves_reservation_for_failure_accounting(self):
        ledger = CreditBudget()
        ticket = ledger.reserve()
        with self.assertRaises(InvalidUsage):
            ledger.settle(ticket, usage(inputTokens=-1))
        self.assertEqual(ledger.committed, PER_ATTEMPT_RESERVATION)
        self.assertEqual(ledger.snapshot()["pending_ticket"], ticket)
        ledger.fail(ticket, "invalid_usage")
        self.assertTrue(ledger.snapshot()["stopped"])

    def test_settled_and_failed_tickets_cannot_be_reused(self):
        ledger = CreditBudget()
        first = ledger.reserve()
        ledger.settle(first, usage())
        for action in (lambda: ledger.settle(first, usage()), lambda: ledger.fail(first)):
            with self.assertRaises(ValueError):
                action()
        second = ledger.reserve()
        with self.assertRaises(ValueError):
            ledger.settle(first, usage())
        ledger.fail(second)
        with self.assertRaises(ValueError):
            ledger.fail(second)

    def test_attempt_cap_independent_from_credit_cap(self):
        ledger = CreditBudget(20, 96)
        for _ in range(96):
            ledger.settle(ledger.reserve(), usage())
        with self.assertRaises(BudgetExceeded):
            ledger.reserve()
        self.assertEqual(ledger.attempts, 96)
        self.assertEqual(ledger.committed, Decimal("0.88800"))

    def test_credit_cap_can_stop_before_attempt_cap(self):
        ledger = CreditBudget("10.405")
        ledger.settle(ledger.reserve(), usage())
        with self.assertRaises(BudgetExceeded):
            ledger.reserve()
        self.assertEqual(ledger.attempts, 1)

    def test_invalid_token_counts_and_relationships(self):
        invalid = [
            {"inputTokens": -1}, {"cachedInputTokens": -1}, {"outputTokens": -1},
            {"reasoningOutputTokens": -1}, {"cacheWriteInputTokens": -1},
            {"inputTokens": True}, {"outputTokens": 1.0}, {"inputTokens": "1000"},
            {"cachedInputTokens": 1001}, {"cacheWriteInputTokens": 801},
            {"reasoningOutputTokens": 101}, {"inputTokens": 272_000},
            {"outputTokens": 128_001}, {"totalTokens": 1101},
        ]
        for fields in invalid:
            with self.subTest(fields=fields), self.assertRaises(InvalidUsage):
                usage_estimates(usage(**fields))
        for missing in ("inputTokens", "cachedInputTokens", "outputTokens", "reasoningOutputTokens"):
            value = usage()
            del value[missing]
            with self.subTest(missing=missing), self.assertRaises(InvalidUsage):
                usage_estimates(value)

    def test_valid_edges_and_json_roundtrip(self):
        result = usage_estimates(usage(inputTokens=271_999, cachedInputTokens=0,
                                      outputTokens=128_000, reasoningOutputTokens=128_000,
                                      totalTokens=399_999))
        self.assertLess(Decimal(result["conservative_credit_equivalent_exact"]), PER_ATTEMPT_RESERVATION)
        self.assertEqual(json.loads(json.dumps(CreditBudget().snapshot()))["generation_attempt_ceiling"], 96)

    def test_constructor_and_ticket_domains(self):
        for cap in (True, -1, "NaN", "Infinity", "bad"):
            with self.subTest(cap=cap), self.assertRaises(ValueError):
                CreditBudget(cap)
        for cap in (True, -1, 97, 1.0):
            with self.subTest(attempts=cap), self.assertRaises(ValueError):
                CreditBudget(max_attempts=cap)
        for ledger in (CreditBudget(0), CreditBudget(max_attempts=0)):
            with self.assertRaises(BudgetExceeded):
                ledger.reserve()
        ledger = CreditBudget()
        ledger.reserve()
        with self.assertRaises(ValueError):
            ledger.settle(True, usage())


if __name__ == "__main__":
    unittest.main()
