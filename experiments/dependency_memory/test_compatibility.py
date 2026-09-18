import unittest
from fractions import Fraction

from compatibility import best_child_codes, certificate, project
from experiment import exact_codebook


class CompatibilityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.result = certificate()

    def test_child_optima_agree_with_independent_frontier_enumeration(self):
        score, codes = best_child_codes()
        self.assertEqual(score / 24, exact_codebook(3, 1)[0])
        self.assertEqual(len(codes), 4)
        self.assertTrue(all(a ^ b == 7 for a, b in codes))

    def test_every_choice_of_optimal_branch_code_was_enumerated(self):
        self.assertEqual(self.result["branch_code_assignments_examined"], 4**4)
        self.assertEqual(self.result["necessary_parent_states_histogram"],
                         {8: 56, 10: 96, 12: 96, 16: 8})

    def test_two_bits_cannot_reach_child_optimum(self):
        self.assertGreater(self.result["minimum_parent_states_to_attain_child_optimum"], 4)
        self.assertEqual(self.result["minimum_parent_bits_to_attain_child_optimum"], 3)
        self.assertGreater(Fraction(self.result["two_stage_2_bit_then_1_bit_error_lower_bound"]),
                           Fraction(1, 4))

    def test_three_bit_witness_directly_attains_optimum(self):
        self.assertEqual(Fraction(self.result["three_bit_parent_witness_error"]), Fraction(1, 4))
        self.assertEqual(self.result["uniform_source_subset_query_outcomes"], 192)
        self.assertEqual(len({row["parent_state"] for row in self.result["witness_encoder_table"]}), 8)

    def test_projection_positions(self):
        self.assertEqual(project(0b1010, (0, 2, 3)), 0b100)


if __name__ == "__main__":
    unittest.main()
