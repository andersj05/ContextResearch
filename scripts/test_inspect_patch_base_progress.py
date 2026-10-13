"""Constructed subset-attribution tests without candidate execution."""
import unittest
from scripts.inspect_patch_base_progress import classify, verified_comparison


class BaseProgressTests(unittest.TestCase):
    def test_new_partial_fixes_are_separate_from_already_visible_checkpoint_code(self):
        base = [{"component_id": key, "all_24_cases_correct": value}
                for key, value in (("new_fix", False), ("already", True), ("unknown", None), ("lost", True))]
        initial = [{"component_id": key, "all_24_cases_correct": value}
                   for key, value in (("new_fix", True), ("already", True), ("unknown", True), ("lost", False))]
        result = classify(base, initial)
        self.assertEqual(result["verified_partial_fixes"], ["new_fix"])
        self.assertEqual(result["already_correct_checkpoint"], ["already"])
        self.assertEqual(result["initially_correct_with_unassessed_base"], ["unknown"])
        self.assertEqual(result["checkpoint_regressions_in_initial_patch"], ["lost"])

    def test_regressions_count_only_verified_new_fixes_and_missing_remains_unassessed(self):
        result = verified_comparison(["fix_a", "fix_b", "fix_c"], {
            "preserved": ["fix_a"], "regressed": ["fix_b", "preexisting_code"], "unassessed": ["fix_c"]})
        self.assertEqual(result, {"preserved": ["fix_a"], "regressed": ["fix_b"], "unassessed": ["fix_c"]})


if __name__ == "__main__":
    unittest.main()
