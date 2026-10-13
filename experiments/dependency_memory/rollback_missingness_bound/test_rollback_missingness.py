"""Scientific invariants for conservative incomplete-pair inference."""
from fractions import Fraction
import unittest

from .rollback_missingness import analyze, exact_p, verify_small


class MissingnessTests(unittest.TestCase):
    def test_invalid_scores_and_counts_cannot_enter_the_test(self):
        exact_p(1, 0)
        for counts in ((True, 0), (1.0, 0), (-1, 0)):
            with self.assertRaises(ValueError): exact_p(*counts)
        for pairs in (([2, 0],), ([True, 0],), ([1, "missing"],)):
            with self.assertRaises(ValueError): analyze(pairs)

    def test_complete_data_reduces_to_the_existing_exact_test(self):
        from experiments.dependency_memory.rollback_challenge_v6.statistics import mcnemar
        for a in range(20):
            for b in range(20):
                result = analyze([(1, 0)] * a + [(0, 1)] * b + [(1, 1), (0, 0)])
                self.assertAlmostEqual(result["worst_case_completion_p"], mcnemar(a, b))
                self.assertEqual(Fraction(**result["worst_case_p_fraction"]), exact_p(a, b))

    def test_one_unknown_can_preserve_or_remove_a_rejection(self):
        complete = [(1, 0)] * 6
        self.assertEqual(exact_p(6, 0), Fraction(1, 32))
        safe = analyze(complete + [(None, 0)])
        unsafe = analyze(complete + [(None, 1)])
        self.assertTrue(safe["reject_for_every_completion"])
        self.assertFalse(unsafe["reject_for_every_completion"])
        self.assertEqual(unsafe["known_complete_pairs"], 6)
        self.assertEqual(unsafe["effect_bounds_numerators"], [5, 6])

    def test_effect_direction_is_symmetric_and_all_missing_is_uninformative(self):
        pairs = [(1, 0)] * 12 + [(0, None), (None, None), (1, None)]
        r = analyze(pairs); k = analyze([(b, a) for a, b in pairs])
        self.assertEqual(r["worst_case_p_fraction"], k["worst_case_p_fraction"])
        self.assertEqual(r["effect_bounds_numerators"], [-x for x in reversed(k["effect_bounds_numerators"])])
        self.assertEqual(r["direction_if_rejected"], "R_higher")
        self.assertEqual(k["direction_if_rejected"], "R_lower")
        missing = analyze([(None, None)] * 20)
        self.assertEqual(missing["worst_case_completion_p"], 1)
        self.assertEqual(missing["effect_missingness_bounds"], [-1, 1])
        self.assertFalse(analyze([])["reject_for_every_completion"])

    def test_exhaustive_small_completion_enumeration(self):
        checked = verify_small(4)
        self.assertEqual(checked["observed_patterns"], 7381)
        self.assertEqual(checked["complete_assignments"], 69905)


if __name__ == "__main__":
    unittest.main()
