"""Independent budget and denominator checks for the new development contract."""
import tempfile
import unittest
from pathlib import Path

from experiments.dependency_memory.rollback_checkpoint_v7.common import ROOT
from experiments.dependency_memory.rollback_checkpoint_v7.prepare import (
    generate, generation_bound, identities, jobs, prepare, check_bundle)
from experiments.dependency_memory.rollback_checkpoint_v7.analysis import analyze


class PreparationTests(unittest.TestCase):
    def test_tight_bound_covers_every_failure_location(self):
        for h in range(2, 12):
            task = generate(split="fixture", replicates=1, stages=1, actions=h)[0]
            possible = [h] + [j + 1 + 2 * (h - j) for j in range(1, h)]
            self.assertEqual(generation_bound([task]), max(possible))

    def test_pilot_allocation_is_192_admissions_not_312_observations(self):
        tasks = generate()
        self.assertEqual(len(tasks), 24)
        self.assertEqual(generation_bound(tasks), 192)
        slots = identities(tasks)
        self.assertEqual(len(slots), 312)
        self.assertEqual(len({identity.key for identity in slots}), 312)
        self.assertTrue(all(i.step >= 2 for i in slots if i.arm in {"K", "R"}))
        self.assertTrue(all(i.stage == "action" for i in slots if i.arm in {"K", "R"}))
        self.assertTrue(all(i.arm == "prefix" for i in slots if i.stage == "lesson"))

    def test_cohort_and_schedule_reproduce_and_use_both_orders(self):
        tasks = generate()
        self.assertEqual(tasks, generate())
        self.assertFalse({t["task_id"] for t in tasks} & {t["task_id"] for t in generate(seed=41)})
        scheduled = jobs(tasks, 2026101267)
        orders = {tuple(j["arm"] for j in scheduled if j["task_id"] == task["task_id"])
                  for task in tasks}
        self.assertEqual(orders, {("prefix", "K", "R"), ("prefix", "R", "K")})

    def test_hard_budget_and_worker_contract(self):
        parent = ROOT / "tmp" / "rollback-v7-tests"
        parent.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(dir=parent) as temp:
            folder = Path(temp) / "bundle"
            with self.assertRaises(ValueError):
                prepare(folder, max_calls=191)
            self.assertFalse(folder.exists())
            for workers in (0, 17, True):
                with self.assertRaises(ValueError):
                    prepare(folder, workers=workers)
            manifest = prepare(folder, split="fixture", replicates=2, workers=16)
            self.assertEqual(check_bundle(folder)[0], manifest)
            with self.assertRaises(ValueError):
                prepare(folder)

    def test_conditional_missingness_excludes_ineligible_pairs(self):
        tasks = generate(split="fixture", replicates=3)
        selected = {tasks[0]["task_id"], tasks[1]["task_id"]}
        scores = {tasks[0]["task_id"]: {"R": 1, "K": 0},
                  tasks[1]["task_id"]: {"R": None, "K": 1}}
        rows = []
        for task in tasks:
            task_id = task["task_id"]
            rows.append({"job": {"task_id": task_id, "arm": "prefix"},
                         "result": {"eligible": task_id in selected,
                                    "reason": "eligible" if task_id in selected else "initial_success",
                                    "state": {"stage": 1}}})
            for arm in ("K", "R"):
                score = scores.get(task_id, {}).get(arm)
                rows.append({"job": {"task_id": task_id, "arm": arm},
                             "result": {"score": score, "disposition": "correct" if score == 1 else "missing_or_fail"}})
        manifest = {"seed": 1, "split": "fixture", "minimum_complete_pairs_for_descriptive_interval": 6}
        result = analyze(tasks, {"jobs": rows, "stopped": False}, {"calls": []}, manifest, simulated=True)
        self.assertEqual(result["selected_tasks"], 3)
        self.assertEqual(result["eligible_prefixes"], 2)
        self.assertEqual(result["primary"]["scheduled_pairs"], 2)
        self.assertEqual(result["primary"]["complete_pairs"], 1)
        self.assertEqual(result["primary"]["fixed_denominator_bounds"], [0.0, 0.5])
        self.assertIsNone(result["primary"]["descriptive_task_bootstrap_95"])
        self.assertIsNone(result["primary"]["confirmatory_p"])


if __name__ == "__main__":
    unittest.main()
