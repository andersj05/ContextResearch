"""Independent comparisons and assumption-sensitive checks for the reduction."""
from copy import deepcopy
import unittest

from experiments.dependency_memory.collision_audit.engine import Problem
from experiments.dependency_memory.collision_audit.fixtures import (
    compatibility, diagnostic_specs, rollback, tool)
from .representations import minimal_obstructions, strategy_outputs, weak_coloring
from .run import check_fixture, check_small_tables


class NoveltyAuditTests(unittest.TestCase):
    def test_forward_strategies_and_colorings_all_small_relations(self):
        result = check_small_tables()
        self.assertEqual(result["nonempty_subset_budget_checks"], 7203)
        self.assertEqual(result["coloring_checks"], 1029)
        self.assertEqual(result["distinct_strategy_output_vectors_by_budget"], [3, 15, 27])

    def test_all_existing_fixtures_match_partition_optimizer(self):
        for spec in diagnostic_specs():
            with self.subTest(name=spec["name"]):
                result = check_fixture(spec)
                self.assertGreaterEqual(result["extra_message_states"], 1)

    def test_triple_is_weak_not_strong_or_pair_only_coloring(self):
        self.assertEqual(minimal_obstructions(3, set(range(7))), (7,))
        self.assertEqual(len(set(weak_coloring(3, [7]))), 2)
        self.assertEqual(len(set(weak_coloring(3, [3, 5, 6]))), 3)
        self.assertEqual(len(set(weak_coloring(3, []))), 1)

    def test_reject_nonhereditary_safe_family_and_impossible_singleton(self):
        with self.assertRaises(ValueError):
            minimal_obstructions(3, {0, 7})
        self.assertIsNone(weak_coloring(3, [1]))

    def test_public_cells_allow_reusing_labels(self):
        spec = rollback(False)
        for i, world in enumerate(spec["worlds"]):
            world["public"]["receipt"] = ["cedar", "birch"][i]
        result = check_fixture(spec)
        self.assertEqual(len(result["cells"]), 2)
        self.assertEqual(result["extra_message_states"], 1)

    def test_repair_precedes_future_task(self):
        spec = compatibility()
        spec["tools"] = []
        spec["tasks"] = [{"name": "first", "trace": [],
                          "accepted": {"w0": ["A"], "w1": ["B"], "w2": ["B"]}},
                         {"name": "second", "trace": [],
                          "accepted": {"w0": ["B"], "w1": ["A"], "w2": ["B"]}}]
        self.assertEqual(check_fixture(spec)["extra_message_states"], 3)
        for task in spec["tasks"]:
            one = deepcopy(spec)
            one["tasks"] = [task]
            self.assertEqual(check_fixture(one)["extra_message_states"], 2)

    def test_strategy_alphabet_respects_cost_and_useless_tools(self):
        spec = compatibility()
        spec["tools"] = [tool("constant", 1, [0, 0, 0]), tool("read", 2, [0, 1, 1])]
        p = Problem(spec)
        self.assertEqual(len(strategy_outputs(3, "ABC", p.tools, 1)), 3)
        self.assertEqual(len(strategy_outputs(3, "ABC", p.tools, 2)), 9)


if __name__ == "__main__":
    unittest.main()
