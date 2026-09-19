import itertools
import unittest
from collections import Counter

from exact_chain import (certificate, child_cuts, cut_gains, grade_witness,
                         parent_partitions, score_partition, search_python,
                         stirling_second_kind)


class ExactChainTests(unittest.TestCase):
    def test_partition_enumerator_matches_labeled_functions_independently(self):
        # Independent formulation: every function from four sources to three
        # labels, canonicalized as a set partition after unused labels vanish.
        expected = set()
        for labels in itertools.product(range(3), repeat=4):
            cells = [sum(1 << x for x in range(4) if labels[x] == c)
                     for c in range(3)]
            if all(cells):
                expected.add(tuple(sorted(cells)))
        actual = [tuple(sorted(cells)) for cells in parent_partitions(4, 3)]
        self.assertEqual(len(actual), len(set(actual)))
        self.assertEqual(set(actual), expected)
        self.assertEqual(len(actual), stirling_second_kind(4, 3))
        self.assertEqual(stirling_second_kind(16, 4), 171798901)

    def test_binary_cuts_cover_all_child_functions_up_to_exchange(self):
        cells = (1, 6, 24, 224)
        full = 255
        expected = {min(sum(cell for cell, label in zip(cells, labels) if label),
                        full ^ sum(cell for cell, label in zip(cells, labels) if label))
                    for labels in itertools.product((0, 1), repeat=4)}
        cuts = list(child_cuts(cells))
        self.assertEqual(len(cuts), 8)
        self.assertEqual({min(mask, full ^ mask) for mask in cuts}, expected)

    def test_gain_identity_matches_all_decoders_on_three_bit_cuts(self):
        # Enumerate reconstruction words explicitly, including repeated words.
        # This does not assume that majority reconstruction is optimal.
        for mask in range(256):
            gains = cut_gains(mask, 3)
            for omitted in range(3):
                coordinates = [j for j in range(3) if j != omitted]
                scores = []
                for words in itertools.product(range(4), repeat=2):
                    scores.append(sum(
                        ((x >> j) & 1) != ((words[int(bool(mask & (1 << x)))] >> i) & 1)
                        for x in range(8) for i, j in enumerate(coordinates)))
                self.assertEqual(8 - gains[omitted], min(scores))

    def test_small_complete_search_matches_outcome_grading(self):
        direct = Counter()
        for cells in parent_partitions(8, 3):
            witness = grade_witness(cells, 3)
            gain = 24 - witness["errors"]
            self.assertEqual(gain, score_partition(cells, 3))
            direct[gain] += 1
        result = search_python(source_bits=3, parent_states=3)
        self.assertEqual(result["gain_histogram"], direct)
        self.assertEqual(result["partitions"], stirling_second_kind(8, 3))
        checked = certificate(result, source_bits=3, parent_states=3)
        self.assertEqual(checked["minimum_errors"], 12)
        self.assertEqual(checked["exact_error"], "1/4")

    def test_four_bit_witness_is_graded_on_all_192_outcomes(self):
        witness = grade_witness((279, 104, 59520, 5632))
        self.assertEqual(witness["outcomes"], 192)
        self.assertEqual(witness["errors"], 54)
        self.assertEqual([b["errors"] for b in witness["branches"]], [14, 14, 14, 12])
        self.assertEqual(score_partition((279, 104, 59520, 5632), 4), 42)

    def test_invalid_and_incomplete_certificates_are_rejected(self):
        with self.assertRaises(ValueError):
            grade_witness((255, 255))
        with self.assertRaises(ValueError):
            certificate({"partitions": 1, "gain_histogram": {42: 1}}, 4, 4)


if __name__ == "__main__":
    unittest.main()
