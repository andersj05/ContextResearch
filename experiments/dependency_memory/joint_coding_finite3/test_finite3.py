"""Independent formulations and timing/capacity checks for the finite witness."""
from fractions import Fraction
import hashlib
import json
import unittest

from experiments.dependency_memory.joint_coding_finite3 import witness as finite


def route_loss(source, word):
    truth = dict(enumerate(reversed(f"{source:04b}")))
    decisions = dict(enumerate(reversed(f"{word:04b}")))
    return sum(truth[j] != decisions[o] for o in range(4) for j in range(4) if j != o)


class FiniteThreeBlockTests(unittest.TestCase):
    def test_generator_against_each_direct_route_and_all_nearest_assignments(self):
        costs = [[route_loss(x, a) for a in range(16)] for x in range(16)]
        for x in range(16):
            for a in range(16):
                self.assertEqual(finite.loss(x, a), costs[x][a])
        book = finite.selected_book()
        table = finite.parent_table(book)
        error = 0
        for source in range(4096):
            words = [int(f"{source:012b}"[8 - 4 * r:12 - 4 * r], 2) for r in range(3)]
            values = [sum(costs[words[r]][candidate[r]] for r in range(3)) for candidate in book]
            self.assertEqual(table[source], values.index(min(values)))
            error += min(values)
        self.assertEqual(error, 40529)
        self.assertEqual(set(table), set(range(64)))
        self.assertEqual(finite.grade(table, book)["errors"], error)

    def test_historical_concatenation_and_independent_product_control(self):
        book = finite.concatenation_book()
        graded = finite.grade(finite.parent_table(book), book)
        self.assertEqual(graded["errors"], 40992)
        self.assertEqual(Fraction(graded["errors"], graded["outcomes"]), Fraction(427, 1536))
        product = tuple((a, b, c) for a in (0, 1, 14, 15) for b in (0, 1, 14, 15) for c in (0, 1, 14, 15))
        self.assertEqual(finite.grade(finite.parent_table(product), product)["errors"], 41472)

    def test_public_relabelling_block_permutation_and_complement_keep_error(self):
        book = finite.selected_book()
        for renamed in (book[::-1], tuple((c, a, b) for a, b, c in book),
                        tuple((a ^ 15, b ^ 15, c ^ 15) for a, b, c in book)):
            self.assertEqual(finite.grade(finite.parent_table(renamed), renamed)["errors"], 40529)

    def test_child_is_one_bit_and_fixed_before_every_late_coordinate(self):
        book = finite.selected_book()
        for message in range(64):
            for block in range(3):
                for omitted in range(4):
                    child = finite.update(message, block, omitted, book)
                    self.assertIn(child, (0, 1))
                    self.assertEqual([finite.predict(child, block, omitted, j) for j in range(4) if j != omitted], [child] * 3)

    def test_capacity_and_malformed_states_rejected(self):
        for book in ((), ((0, 0, 0),) * 2, ((0, 0, True),), ((0, 0, 16),),
                     ((0, 0),), ([0, 0, 0],), tuple((i & 15, i >> 4, 0) for i in range(65))):
            with self.assertRaises(ValueError):
                finite.parent_table(book)
        book = finite.selected_book()
        for table in ([0] * 4095, [64] * 4096, [True] * 4096):
            with self.assertRaises(ValueError):
                finite.grade(table, book)
        with self.assertRaises(ValueError):
            finite.predict(0, 0, 1, 1)

    def test_discovery_source_binding_and_bounded_search_disposition(self):
        discovery = json.loads(finite.DISCOVERY.read_text())
        self.assertEqual(discovery["search_source_sha256"], hashlib.sha256((finite.HERE / "search.c").read_bytes()).hexdigest())
        self.assertEqual(discovery["discovery_script_sha256"], hashlib.sha256((finite.HERE / "discover.py").read_bytes()).hexdigest())
        greedy, control = discovery["runs"]["greedy"], discovery["runs"]["concatenation"]
        self.assertEqual(len(greedy["greedy_steps"]), 64)
        self.assertEqual(len(greedy["accepted_swaps"]), 8)
        self.assertFalse(greedy["single_swap_exhausted"])
        self.assertEqual(control["accepted_swaps"], [])
        self.assertTrue(control["single_swap_exhausted"])
        self.assertEqual(discovery["new_model_requests"], 0)


if __name__ == "__main__":
    unittest.main()
