"""Compare independently formulated proof ingredients and edge cases."""

import unittest
from fractions import Fraction

from audit_scaling import certificate as audited_certificate
from compatibility_scaling import check_block_entropy, check_family


class ScalingAuditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.audit = audited_certificate()

    def test_sign_formulation_covers_all_orientations(self):
        self.assertEqual(self.audit["signed_majority_assignments"], 8**4)
        self.assertEqual(self.audit["signature_state_histogram"],
                         {8: 896, 10: 1536, 12: 1536, 16: 128})

    def test_abstract_antipodal_fibers_match_concrete_extremum(self):
        self.assertEqual(self.audit["abstract_paired_compositions_checked"], 99)
        self.assertEqual(self.audit["abstract_paired_maximum_fiber_product"],
                         check_block_entropy()["maximum_fiber_product"])

    def test_noncomplementary_decoders_including_degenerate_ones(self):
        self.assertEqual(self.audit["ordered_child_decoders_including_repeated_words"], 64)
        self.assertEqual(Fraction(self.audit["noncomplementary_child_error_lower_bound"]), Fraction(1, 3))

    def test_leave_one_out_excludes_two_bit_counterexample(self):
        with self.assertRaises(ValueError):
            check_family(2)
        result = check_family(4)
        self.assertGreater(Fraction(result["two_bit_chain_excess_error_upper_bound"]), 0)


if __name__ == "__main__":
    unittest.main()
