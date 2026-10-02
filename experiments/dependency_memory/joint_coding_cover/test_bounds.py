"""Direct coordinate checks of cover ingredients and the decoder restriction."""
from collections import Counter
from fractions import Fraction
from itertools import product
import unittest

from experiments.dependency_memory.joint_coding_cover import bounds
from experiments.dependency_memory.joint_coding_finite3 import witness


def direct(source, decision):
    source_bits, decisions = list(reversed(f"{source:04b}")), list(reversed(f"{decision:04b}"))
    return sum(source_bits[j] != decisions[o] for o in range(4) for j in range(4) if j != o)


class CoverBoundTests(unittest.TestCase):
    def test_oracle_and_score_profiles_against_every_direct_one_block_route(self):
        for source in range(16):
            loss = [direct(source, a) for a in range(16)]
            self.assertEqual(bounds.oracle(source), min(loss))
            self.assertEqual(loss.count(min(loss)), 1)
            for decision in range(16):
                self.assertEqual(bounds.score(source, decision), int(source.bit_count() == 2) - (loss[decision] - min(loss)))
        expected = {0: {-12: 1, -6: 4, -1: 6, 0: 5},
                    1: {-9: 1, -5: 3, -3: 3, -2: 3, -1: 3, 0: 3},
                    2: {-6: 2, -4: 4, -3: 1, -2: 4, -1: 4, 1: 1}}
        for word in range(16):
            group = min(word.bit_count(), 4 - word.bit_count())
            self.assertEqual(dict(Counter(bounds.score(x, word) for x in range(16))), expected[group])

    def test_all_column_rewards_by_source_enumeration_without_histogram_convolution(self):
        data = bounds.certificate()
        one = [[int(x.bit_count() == 2) - (direct(x, a) - min(direct(x, q) for q in range(16)))
                for x in range(16)] for a in range(16)]
        two = {(a, b): [one[a][x] + one[b][y] for x, y in product(range(16), repeat=2)]
               for a, b in product(range(16), repeat=2)}
        histogram = Counter()
        for c, b, a in product(range(16), repeat=3):
            total = 0
            for left in two[a, b]:
                for right in one[c]:
                    if left + right > 0:
                        total += left + right
            self.assertEqual(total, data["all_4096_column_rewards"][a + 16*b + 256*c])
            histogram[total] += 1
        self.assertEqual(histogram, {0: 1000, 9: 2016, 15: 792, 16: 216, 25: 72})

    def test_missing_constant_fibers_and_saved_upper_witness(self):
        fibers = Counter()
        for source in range(4096):
            words = witness.decode_id(source)
            if all(x.bit_count() != 2 for x in words):
                center = tuple(15 if x.bit_count() > 2 else 0 for x in words)
                fibers[center] += 1
        self.assertEqual(len(fibers), 8)
        self.assertEqual(set(fibers.values()), {125})
        data = bounds.certificate()
        self.assertEqual(min(r["lower_errors"] for r in data["lower_bound_by_constant_count"]), 40072)
        book = witness.selected_book()
        self.assertGreaterEqual(witness.grade(witness.parent_table(book), book)["errors"], data["lower_errors"])
        self.assertEqual(Fraction(data["upper_errors"] - data["lower_errors"], data["outcomes"]), Fraction(457, 147456))

    def test_public_bit_relabellings_allowed_but_coordinate_dependent_prediction_rejected(self):
        for endpoints in (((0, 0, 0), (1, 1, 1)), ((1, 1, 1), (0, 0, 0)), ((0, 0, 0), (0, 0, 0))):
            self.assertEqual(bounds.lower_bound([endpoints] * 4), Fraction(5009, 18432))
        with self.assertRaisesRegex(ValueError, "outside the proved family"):
            bounds.lower_bound([((0, 1, 0), (1, 0, 1))] * 4)


if __name__ == "__main__":
    unittest.main()
