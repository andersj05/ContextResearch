"""Checks for mathematical claims, independent enumeration, and information flow."""

import unittest

from experiment import (
    Event,
    RecordMemory,
    entropy_error_lower_bound,
    exact_codebook,
    make_workflow,
    one_bit_partition_optimum,
    run_workflow,
)


class ExactChannelTests(unittest.TestCase):
    def test_no_memory_and_full_memory(self):
        for n in range(1, 5):
            self.assertEqual(exact_codebook(n, 0)[0], 0.5)
            self.assertEqual(exact_codebook(n, n)[0], 0.0)

    def test_independent_encoder_enumeration(self):
        for n in range(1, 4):
            self.assertEqual(exact_codebook(n, 1)[0], one_bit_partition_optimum(n))

    def test_coding_can_beat_fixed_coordinate_retention(self):
        self.assertEqual(exact_codebook(3, 1)[0], 0.25)
        self.assertLess(exact_codebook(3, 1)[0], (1 - 1 / 3) / 2)

    def test_finite_optimum_respects_information_lower_bound(self):
        for n in range(1, 5):
            for budget in range(n + 1):
                self.assertGreaterEqual(
                    exact_codebook(n, budget)[0] + 1e-12,
                    entropy_error_lower_bound(n, budget),
                )

    def test_information_timing_changes_optimum(self):
        self.assertEqual(exact_codebook(1, 1)[0], 0.0)
        self.assertEqual(exact_codebook(4, 1)[0], 0.3125)


class RecordStreamTests(unittest.TestCase):
    def test_revision_and_retirement(self):
        memory = RecordMemory(2, True)
        memory.update(Event("value", "a", 7))
        memory.update(Event("value", "a", 9))
        self.assertEqual(memory.update(Event("query", "a")), 9)
        memory.update(Event("retire", "a"))
        self.assertIsNone(memory.update(Event("query", "a")))

    def test_eviction_cannot_recover_from_identifier(self):
        memory = RecordMemory(1, True)
        memory.update(Event("value", "a", 7))
        memory.update(Event("value", "b", 8))
        memory.update(Event("retire", "b"))
        self.assertIsNone(memory.update(Event("query", "a")))

    def test_repeated_exact_compaction_does_not_cause_decay(self):
        memory = RecordMemory(1, True)
        memory.update(Event("value", "a", 2**64 - 1))
        before = memory.serialized()
        for _ in range(100):
            memory.update(Event("checkpoint"))
        self.assertEqual(memory.serialized(), before)

    def test_lifecycle_policy_matches_width_upper_bound(self):
        for width in (2, 4, 8):
            for batches in (4, 16):
                events = make_workflow(7, width, batches)
                result = run_workflow(events, width, True)
                self.assertTrue(result["all_correct"])
                self.assertEqual(result["max_live_records"], width)
                self.assertLessEqual(result["peak_records"], width)

    def test_lru_can_lose_long_lived_fact_with_same_record_budget(self):
        events = make_workflow(3, 2, 8)
        self.assertTrue(run_workflow(events, 2, True)["anchor_correct"])
        self.assertFalse(run_workflow(events, 2, False)["anchor_correct"])

    def test_insufficient_capacity_breaks_the_upper_bound_assumption(self):
        self.assertFalse(run_workflow(make_workflow(2, 4, 4), 3, True)["all_correct"])

    def test_query_events_do_not_expose_grading_values(self):
        events = make_workflow(4, 4, 8)
        self.assertTrue(all(e.value is None for e in events if e.kind == "query"))


if __name__ == "__main__":
    unittest.main()
