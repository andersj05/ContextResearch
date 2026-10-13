"""V11 fixed allocation, provenance and disjoint public-context checks."""

from collections import Counter
import unittest

from experiments.dependency_memory.rollback_patch_v11 import tasks
from experiments.dependency_memory.rollback_patch_v10 import tasks as v10
from experiments.dependency_memory.rollback_patch_v9 import tasks as v9


class DevelopmentTaskTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.study = tasks.generate()

    def test_fixed_study_seed_ids_hashes_and_development_provenance(self):
        self.assertEqual(tasks.DEFAULT_SEED, 2026101312)
        self.assertEqual(len(self.study), 256)
        self.assertEqual(Counter(task["family"] for task in self.study), dict.fromkeys(tasks.FAMILIES, 64))
        self.assertEqual(len({task["task_id"] for task in self.study}), 256)
        for task in self.study:
            self.assertTrue(task["task_id"].startswith("v11-study-"))
            self.assertEqual(task["sha256"], tasks.sha({key: value for key, value in task.items() if key != "sha256"}))
            self.assertIn("UNPLANNED DEVELOPMENT", task["evaluator"]["provenance"])
            self.assertIn("below its frozen four-failure gate", task["evaluator"]["provenance"])
            self.assertIn("recur across tasks", task["evaluator"]["provenance"])

    def test_all_public_contexts_unique_and_disjoint_from_both_closed_calibrations(self):
        fingerprint = lambda task: tasks.sha({key: task[key] for key in ("family", "contract", "base_files", "public_tests")})
        current = {fingerprint(task) for task in self.study}
        self.assertEqual(len(current), 256)
        for calibration in (v9.generate(), v10.generate()):
            self.assertFalse(current & {fingerprint(task) for task in calibration})
        component_hashes = {row["sha256"] for task in self.study for row in task["evaluator"]["component_bindings"]}
        prior_hashes = {row["sha256"] for task in v10.generate() for row in task["evaluator"]["component_bindings"]}
        self.assertFalse(component_hashes & prior_hashes)

    def test_fixture_has_four_tasks_and_unchanged_component_oracles_verify(self):
        fixture = tasks.generate(split="fixture")
        self.assertEqual(len(fixture), 4)
        self.assertTrue(all(task["task_id"].startswith("v11-fixture-") for task in fixture))
        report = tasks.verify_tasks(fixture)
        self.assertTrue(report["passed"])
        self.assertEqual(report["component_case_comparisons"], 768)
        self.assertFalse(report["candidate_code_executed_on_host"])
        self.assertEqual(report["model_calls"], 0)

    def test_unsupported_calibration_cohort_or_seed_is_rejected(self):
        for settings in ({"split": "calibration"}, {"per_family": 4},
                         {"split": "fixture", "per_family": 4},
                         {"seed": tasks.DEFAULT_SEED + 1}, {"per_family": True}):
            with self.subTest(settings=settings), self.assertRaises(ValueError):
                tasks.generate(**settings)


if __name__ == "__main__":
    unittest.main()
