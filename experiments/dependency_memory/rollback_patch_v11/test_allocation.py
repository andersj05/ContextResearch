"""Bind the exploratory departure and fixed allocation without model calls."""
from collections import Counter, defaultdict
from copy import deepcopy
from pathlib import Path
import unittest
from unittest.mock import patch

from experiments.dependency_memory.rollback_patch_v11 import common, prepare
from experiments.dependency_memory.rollback_patch_v10 import common as previous_common


class ExploratoryAllocationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.calibration = common.ROOT / "experiments/dependency_memory/results/rollback_patch_v10_2026-10-13/calibration_live"
        cls.original = prepare.original_calibration_gate(cls.calibration)
        cls.manifest = prepare.read(cls.calibration / "manifest.json")

    def test_original_gate_stays_failed_and_exact_audited_departure_is_preserved(self):
        before = deepcopy(self.original)
        gate = prepare.calibration_gate(self.calibration)
        self.assertFalse(self.original["passed"])
        self.assertEqual([key for key, value in self.original["checks"].items() if not value],
                         ["natural_failure_headroom"])
        self.assertEqual((self.original["eligible"], self.original["valid_lessons"],
                          self.original["control_correct"]), (3, 3, 3))
        self.assertTrue(gate["passed"])
        self.assertEqual(gate["original_failed_gate"], self.original)
        self.assertIn("Unplanned exploratory", gate["design_departure"])
        self.assertIn("not a passing v10 gate or confirmation", gate["design_departure"])
        self.assertEqual(gate["calibration_execution_sha256"], self.original["calibration_execution_sha256"])
        self.assertEqual(gate["calibration_audit_sha256"], self.original["calibration_audit_sha256"])
        self.assertEqual(self.original, before)

    def test_other_gate_failures_cannot_be_waived_as_a_headroom_departure(self):
        for key in ("all_sixteen_prefixes_known", "all_lessons_valid", "no_global_stop",
                    "no_capacity_stop", "live_calibration", "independent_replay_passed",
                    "replay_bound_to_manifest", "replay_bound_to_evidence", "exact_job_inventory",
                    "sealed_evidence_intact"):
            original = deepcopy(self.original)
            original["checks"][key] = False
            with self.subTest(key=key), patch.object(prepare, "original_calibration_gate", return_value=original):
                gate = prepare.calibration_gate(self.calibration)
                self.assertFalse(gate["passed"])
                self.assertFalse(gate["checks"]["only_original_failure_is_headroom"])

    def test_different_failure_or_repair_counts_do_not_match_the_observed_departure(self):
        for key, value in (("eligible", 2), ("eligible", 4), ("valid_lessons", 2),
                           ("control_correct", 2), ("passed", True)):
            original = deepcopy(self.original)
            original[key] = value
            with self.subTest(key=key, value=value), patch.object(
                    prepare, "original_calibration_gate", return_value=original):
                self.assertFalse(prepare.calibration_gate(self.calibration)["passed"])
        manifest = {**self.manifest, "study": "an-unrelated-control-study"}
        with patch.object(prepare, "original_calibration_gate", return_value=self.original), \
                patch.object(prepare, "read", return_value=manifest):
            self.assertFalse(prepare.calibration_gate(self.calibration)["passed"])

    def test_all_256_tasks_receive_four_arms_and_a_fixed_3584_identity_ceiling(self):
        # Independent schedule inventory, without regenerating task semantics.
        tasks = [{"task_id": "allocation-fixture-" + str(index)} for index in range(256)]
        identities = prepare.identities(tasks, "study")
        self.assertEqual(len(identities), 3584)
        self.assertEqual(len({identity.key for identity in identities}), 3584)
        by_task = defaultdict(set)
        for identity in identities:
            self.assertEqual(identity.study, common.STUDY)
            self.assertEqual(identity.track, "patch_factorial")
            by_task[identity.task_id].add((identity.arm, identity.step, identity.stage))
        expected = {("prefix", 1, "action"), ("prefix", 1, "lesson")}
        expected.update((arm, step, "action") for arm in ("K0", "R0", "KL", "RL") for step in (1, 2, 3))
        self.assertEqual(len(by_task), 256)
        self.assertTrue(all(rows == expected for rows in by_task.values()))

    def test_schedule_is_outcome_free_reproducible_and_children_match_their_prefix(self):
        tasks = [{"task_id": "allocation-fixture-" + str(index)} for index in range(256)]
        schedule = prepare.jobs(tasks, common.SEED, "study")
        self.assertEqual(schedule, prepare.jobs(list(reversed(tasks)), common.SEED, "study"))
        self.assertEqual(len(schedule), 1280)
        self.assertEqual(Counter(row["arm"] for row in schedule),
                         {arm: 256 for arm in ("prefix", "K0", "R0", "KL", "RL")})
        self.assertEqual(len({row["job_id"] for row in schedule}), 1280)
        prefixes = {row["task_id"]: row["job_id"] for row in schedule if row["arm"] == "prefix"}
        for row in schedule:
            if row["arm"] != "prefix":
                self.assertEqual(row["depends_on"], prefixes[row["task_id"]])
        arm_orders = defaultdict(list)
        for row in schedule:
            if row["arm"] != "prefix":
                arm_orders[row["task_id"]].append(row["arm"])
        self.assertGreater(len({tuple(order) for order in arm_orders.values()}), 1)

    def test_unsupported_cohort_seed_calibration_and_workers_fail_before_grading(self):
        destination = common.ROOT / "tmp" / "v11-must-not-be-created-by-invalid-allocation"
        self.assertFalse(destination.exists())
        settings = ({"per_family": 63}, {"per_family": 65}, {"seed": common.SEED + 1},
                    {"split": "calibration"}, {"workers": 33}, {"workers": True})
        for values in settings:
            with self.subTest(values=values), patch.object(prepare, "verify") as verify, \
                    patch.object(prepare, "calibration_gate") as gate:
                with self.assertRaises(ValueError):
                    prepare.prepare(destination, runtime=None, **values)
                verify.assert_not_called()
                gate.assert_not_called()
        self.assertFalse(destination.exists())

    def test_failed_departure_gate_does_not_generate_or_grade_a_new_allocation(self):
        destination = common.ROOT / "tmp" / "v11-must-not-be-created-by-failed-gate"
        self.assertFalse(destination.exists())
        with patch.object(prepare, "calibration_gate", return_value={"passed": False}), \
                patch.object(prepare, "generate") as generate, patch.object(prepare, "verify") as verify:
            with self.assertRaisesRegex(ValueError, "calibration_gate_not_passed"):
                prepare.prepare(destination, runtime=None, gate_folder=self.calibration)
            generate.assert_not_called()
            verify.assert_not_called()
        self.assertFalse(destination.exists())

    def test_same_engine_and_same_source_capacity_and_attempt_contract(self):
        here = Path(__file__).resolve().parent
        self.assertEqual((here / "engine.py").read_bytes(),
                         (here.parent / "rollback_patch_v10" / "engine.py").read_bytes())
        self.assertEqual(common.SEED, 2026101312)
        self.assertNotEqual(common.STUDY, previous_common.STUDY)
        for key in ("ARMS", "ATTEMPTS", "MAX_BODY_BYTES", "MAX_INPUT_TEXT_BYTES", "MIN_CHANGED_LINES"):
            self.assertEqual(getattr(common, key), getattr(previous_common, key))


if __name__ == "__main__":
    unittest.main()
