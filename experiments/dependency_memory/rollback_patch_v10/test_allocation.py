"""Changed v10 feasibility gate and version-local execution interfaces.

These synthetic receipts test gate decisions only. They are not calibration
observations, Docker execution or model results.
"""

from copy import deepcopy
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

from experiments.dependency_memory.rollback_patch_v10 import (
    analysis, audit, common, engine, prepare, runner, runtime, tasks, transport,
)


class CompositeAllocationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        (common.ROOT / "tmp").mkdir(exist_ok=True)

    def make_evidence(self, parent, *, eligible=4, correct=1, live=True,
                      bad_manifest_binding=False, bad_evidence_binding=False,
                      stopped=False, unknown_prefix=False, invalid_lesson=False,
                      reorder_jobs=False, audit_passed=True, capacity_kind=None):
        folder = parent / "calibration_live"
        folder.mkdir()
        rows = []
        for index in range(16):
            is_eligible = index < eligible
            task_id = "synthetic-gate-case-" + str(index)
            for arm in ("prefix", "K0"):
                job = {"task_id": task_id, "arm": arm, "job_id": task_id + arm}
                result = ({"eligible": is_eligible,
                           "reason": "natural_substantive_patch_mismatch" if is_eligible else "public_pass",
                           "lesson_disposition": "valid" if is_eligible else "not_needed"}
                          if arm == "prefix" else
                          {"first_pass": 1 if is_eligible else None,
                           "score": int(index < correct) if is_eligible else None})
                rows.append({"job": job, "result": result})
        manifest = {"split": "calibration", "per_family": 4,
                    "jobs": deepcopy([row["job"] for row in rows])}
        if unknown_prefix:
            rows[-2]["result"]["reason"] = "unknown_dispatch"
        if invalid_lesson:
            rows[0]["result"]["lesson_disposition"] = "invalid_lesson"
        if capacity_kind == "prefix":
            rows[8]["result"].update(reason="context_capacity")
        elif capacity_kind == "K0":
            rows[3]["result"].update(disposition="context_capacity", first_pass=None, score=0)
        if reorder_jobs:
            rows.reverse()
        values = {"manifest.json": manifest,
                  "execution.json": {"jobs": rows, "stopped": stopped},
                  "run_settings.json": {"live": live}}
        for filename, value in values.items():
            common.save_new(folder / filename, value)
        evidence = {"files": [{"path": filename,
                               "sha256": common.sha((folder / filename).read_bytes())}
                              for filename in values]}
        common.save_new(folder / "evidence_manifest.json", evidence)
        common.save_new(folder.with_name(folder.name + "_replay_audit.json"),
                        {"passed": audit_passed,
                         "manifest_sha256": "wrong" if bad_manifest_binding else common.sha(manifest),
                         "evidence_manifest_sha256": "wrong" if bad_evidence_binding else common.sha(evidence)})
        return folder

    def gate(self, **settings):
        with TemporaryDirectory(prefix="v10-gate-test-", dir=common.ROOT / "tmp") as temp:
            return prepare.calibration_gate(self.make_evidence(Path(temp), **settings))

    def test_four_natural_failures_and_one_correct_control_are_sufficient(self):
        gate = self.gate(eligible=4, correct=1)
        self.assertTrue(gate["passed"])
        self.assertEqual(gate["eligible"], 4)
        self.assertEqual(gate["control_correct"], 1)

    def test_no_upper_failure_cutoff_for_repairable_composite_projects(self):
        # Unlike v9, v10 does not reject 14..16 failed initial patches merely
        # because this larger project rarely succeeds in its first attempt.
        for eligible in (14, 15, 16):
            with self.subTest(eligible=eligible):
                gate = self.gate(eligible=eligible, correct=1)
                self.assertTrue(gate["passed"])
                self.assertEqual(gate["eligible"], eligible)

    def test_fewer_than_four_natural_failures_cannot_authorize_main(self):
        for eligible in (0, 1, 3):
            with self.subTest(eligible=eligible):
                gate = self.gate(eligible=eligible)
                self.assertFalse(gate["passed"])
                self.assertFalse(gate["checks"]["natural_failure_headroom"])

    def test_public_repair_without_private_correctness_cannot_pass_gate(self):
        gate = self.gate(eligible=16, correct=0)
        self.assertEqual(gate["control_public_repaired"], 16)
        self.assertEqual(gate["control_correct"], 0)
        self.assertFalse(gate["checks"]["one_correct_ordinary_repair"])
        self.assertFalse(gate["passed"])

    def test_audit_must_pass_and_bind_both_manifest_and_sealed_evidence(self):
        for setting in ({"audit_passed": False}, {"bad_manifest_binding": True},
                        {"bad_evidence_binding": True}, {"live": False}):
            with self.subTest(setting=setting):
                self.assertFalse(self.gate(**setting)["passed"])

    def test_changed_sealed_file_cannot_pass_previously_bound_audit(self):
        with TemporaryDirectory(prefix="v10-seal-test-", dir=common.ROOT / "tmp") as temp:
            folder = self.make_evidence(Path(temp))
            with (folder / "execution.json").open("ab") as stream:
                stream.write(b" ")
            gate = prepare.calibration_gate(folder)
            self.assertFalse(gate["checks"]["sealed_evidence_intact"])
            self.assertFalse(gate["passed"])

    def test_unknowns_missing_lessons_stops_and_changed_job_inventory_block_gate(self):
        for setting in ({"unknown_prefix": True}, {"invalid_lesson": True},
                        {"stopped": True}, {"reorder_jobs": True}):
            with self.subTest(setting=setting):
                self.assertFalse(self.gate(**setting)["passed"])

    def test_capacity_stop_closes_gate_even_with_headroom_and_correct_repair(self):
        for kind in ("prefix", "K0"):
            with self.subTest(kind=kind):
                gate = self.gate(eligible=4, correct=1, capacity_kind=kind)
                self.assertEqual(gate["eligible"], 4)
                self.assertEqual(gate["control_correct"], 1)
                self.assertTrue(gate["checks"]["natural_failure_headroom"])
                self.assertTrue(gate["checks"]["one_correct_ordinary_repair"])
                self.assertFalse(gate["checks"]["no_capacity_stop"])
                self.assertFalse(gate["passed"])

    def test_analysis_capacity_qualifier_keeps_all_existing_binary_and_missing_scores(self):
        underlying = {"limitations": [],
                      "arm_scores": {"K0": [1, 0], "R0": [0, 1], "KL": [None, 0], "RL": [1, 1]},
                      "contrasts": {"deletion_without_lesson": 0}}
        execution = {"stopped": False, "jobs": [
            {"job": {"task_id": "one", "arm": "K0"},
             "result": {"score": 0, "disposition": "context_capacity"}},
            {"job": {"task_id": "two", "arm": "prefix"},
             "result": {"score": None, "reason": "context_capacity"}},
        ]}
        original_execution = deepcopy(execution)
        with patch.object(analysis, "inherited_analyze", return_value=deepcopy(underlying)) as inherited:
            result = analysis.analyze([], execution, {}, {}, simulated=False)
        inherited.assert_called_once_with([], execution, {}, {}, simulated=False)
        self.assertEqual(result["arm_scores"], underlying["arm_scores"])
        self.assertEqual(result["contrasts"], underlying["contrasts"])
        self.assertEqual(execution, original_execution)
        gate = result["capacity_interpretation_gate"]
        self.assertFalse(gate["passed"])
        self.assertFalse(gate["global_stop"])
        self.assertEqual(gate["capacity_stops"], [{"task_id": "one", "arm": "K0"},
                                                   {"task_id": "two", "arm": "prefix"}])

    def test_analysis_global_stop_qualifies_existing_outcomes_without_capacity_events(self):
        underlying = {"limitations": [], "arm_scores": {"K0": [1], "R0": [None]},
                      "unknowns": 1}
        for stopped in (False, True):
            execution = {"stopped": stopped, "jobs": [
                {"job": {"task_id": "one", "arm": "K0"}, "result": {"score": 1}},
                {"job": {"task_id": "one", "arm": "R0"}, "result": {"score": None}},
            ]}
            with self.subTest(stopped=stopped), patch.object(analysis, "inherited_analyze", return_value=deepcopy(underlying)):
                result = analysis.analyze([], execution, {}, {})
                self.assertEqual(result["arm_scores"], underlying["arm_scores"])
                self.assertEqual(result["unknowns"], 1)
                gate = result["capacity_interpretation_gate"]
                self.assertEqual(gate["passed"], not stopped)
                self.assertEqual(gate["global_stop"], stopped)
                self.assertEqual(gate["capacity_stops"], [])

    def test_fixed_80_and_3584_caps_use_distinct_new_study_identities(self):
        calibration = prepare.identities([{"task_id": str(index)} for index in range(16)], "calibration")
        study = prepare.identities([{"task_id": str(index)} for index in range(256)], "study")
        self.assertEqual(len(calibration), 80)
        self.assertEqual(len(study), 3584)
        self.assertEqual(len({identity.key for identity in study}), 3584)
        self.assertEqual({identity.study for identity in study}, {common.STUDY})
        self.assertEqual({identity.arm for identity in calibration}, {"prefix", "K0"})
        self.assertEqual({identity.arm for identity in study}, {"prefix", "K0", "R0", "KL", "RL"})

    def test_runner_prepare_and_audit_use_version_local_runtime_and_controller(self):
        self.assertIs(prepare.generate, tasks.generate)
        self.assertIs(prepare.verify_tasks, tasks.verify_tasks)
        self.assertIs(runner.run_prefix, engine.run_prefix)
        self.assertIs(runner.run_continuation, engine.run_continuation)
        self.assertIs(audit.run_prefix, engine.run_prefix)
        self.assertIs(audit.run_continuation, engine.run_continuation)
        self.assertIs(runner.PatchRuntime, runtime.PatchRuntime)
        self.assertIs(audit.PatchRuntime, runtime.PatchRuntime)
        self.assertIs(runner.live_factory, transport.live_factory)
        self.assertIs(runner.preflight, transport.preflight)
        self.assertIs(runner.run_case, transport.run_case)
        self.assertIs(engine.public_check, tasks.public_check)
        self.assertIs(engine.terminal_check, tasks.terminal_check)

    def test_inherited_task_grading_adapter_uses_supplied_v10_runtime(self):
        seen = []
        class Runtime:
            def check(self, proposed, cases, *, public=True):
                seen.append((proposed, cases, public))
                return {"score": 1, "disposition": "correct", "status": "public_pass",
                        "hidden_extra": "PRIVATE_CANARY"}
        public_cases = [{"id": "public-01", "input": {}, "expected": {}}]
        private_cases = [{"id": "private-01", "input": {}, "expected": {}}]
        task = {"public_tests": public_cases, "evaluator": {"reserved_tests": private_cases}}
        proposed = {"files": []}
        checker = Runtime()
        tasks.public_check(task, proposed, checker)
        result = tasks.terminal_check(task, proposed, checker)
        self.assertEqual(seen, [(proposed, public_cases, True),
                                (proposed, public_cases + private_cases, False)])
        self.assertEqual(result, {"score": 1, "disposition": "correct"})


if __name__ == "__main__":
    unittest.main()
