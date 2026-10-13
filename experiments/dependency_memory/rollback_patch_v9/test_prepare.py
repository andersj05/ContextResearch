"""Frozen allocation and calibration-gate invariants; no model or code execution."""
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase
from unittest.mock import patch
from experiments.dependency_memory.rollback_patch_v9.common import ROOT, SEED, sha, save_new
from experiments.dependency_memory.rollback_patch_v9.prepare import identities, jobs, prepare, check_bundle, calibration_gate
from experiments.dependency_memory.rollback_patch_v9.tasks import generate


class TrustedFixtureRuntime:
    """An explicitly fake reference checker for bundle mutation tests only."""
    def check(self, candidate, tests, *, public):
        return {"score": 1, "status": "public_pass" if public else "private_pass", "disposition": "correct"}


class AllocationTests(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tasks = generate(split="fixture", seed=SEED, per_family=1)
        (ROOT / "tmp").mkdir(exist_ok=True)

    def test_exact_call_caps_and_distinct_four_arm_identities(self):
        schedule = identities(self.tasks, "study")
        self.assertEqual(len(schedule), 14 * len(self.tasks))
        self.assertEqual(len({item.key for item in schedule}), len(schedule))
        calibration = identities(self.tasks, "calibration")
        self.assertEqual(len(calibration), 5 * len(self.tasks))
        self.assertEqual({item.arm for item in calibration}, {"prefix", "K0"})

    def test_deterministic_jobs_depend_only_on_own_prefix(self):
        schedule = jobs(self.tasks, SEED, "study")
        self.assertEqual(schedule, jobs(self.tasks, SEED, "study"))
        by_id = {job["job_id"]: job for job in schedule}
        for job in schedule:
            if job["arm"] != "prefix":
                parent = by_id[job["depends_on"]]
                self.assertEqual(parent["task_id"], job["task_id"])
                self.assertEqual(parent["arm"], "prefix")
        self.assertEqual(len(schedule), 5 * len(self.tasks))

    def test_freeze_roundtrip_and_tamper_rejection(self):
        with TemporaryDirectory(dir=ROOT / "tmp") as temp:
            folder = Path(temp) / "bundle"
            manifest = prepare(folder, runtime=TrustedFixtureRuntime(), split="fixture", per_family=1)
            self.assertEqual(check_bundle(folder)[0], manifest)
            with self.assertRaises(ValueError):
                prepare(folder, runtime=TrustedFixtureRuntime(), split="fixture", per_family=1)
            with (folder / "source_snapshot.zip").open("ab") as stream:
                stream.write(b"tamper")
            with self.assertRaisesRegex(ValueError, "snapshot_changed"):
                check_bundle(folder)

    def test_fixed_live_cohort_and_seed_cannot_silently_change(self):
        with TemporaryDirectory(dir=ROOT / "tmp") as temp:
            folder = Path(temp) / "bundle"
            for settings in ({"split": "study", "per_family": 4},
                             {"split": "study", "per_family": 64, "seed": SEED},
                             {"split": "calibration", "per_family": 5},
                             {"split": "calibration", "per_family": 4, "seed": SEED + 1}):
                with self.assertRaises(ValueError):
                    prepare(folder, runtime=TrustedFixtureRuntime(), **settings)
            self.assertFalse(folder.exists())


class CalibrationGateTests(TestCase):
    def make_evidence(self, parent, *, correct=1, live=True, bad_binding=False):
        folder = parent / "calibration_live"
        folder.mkdir()
        rows = []
        for index in range(16):
            task_id = "test" + str(index)
            eligible = index < 4
            for arm in ("prefix", "K0"):
                job = {"task_id": task_id, "arm": arm, "job_id": task_id + arm}
                result = ({"eligible": eligible, "reason": "natural_substantive_patch_mismatch" if eligible else "public_pass",
                           "lesson_disposition": "valid" if eligible else "not_needed"} if arm == "prefix" else
                          {"first_pass": 1 if eligible else None, "score": correct if eligible else None})
                rows.append({"job": job, "result": result})
        manifest = {"split": "calibration", "per_family": 4, "jobs": [row["job"] for row in rows]}
        values = {"manifest.json": manifest, "execution.json": {"jobs": rows, "stopped": False},
                  "run_settings.json": {"live": live}}
        for filename, value in values.items():
            save_new(folder / filename, value)
        evidence = {"files": [{"path": filename, "sha256": sha((folder / filename).read_bytes())} for filename in values]}
        save_new(folder / "evidence_manifest.json", evidence)
        save_new(folder.with_name(folder.name + "_replay_audit.json"),
                 {"passed": True, "manifest_sha256": "wrong" if bad_binding else sha(manifest),
                  "evidence_manifest_sha256": sha(evidence)})
        return folder

    def test_public_repair_alone_cannot_pass_primary_endpoint_gate(self):
        with TemporaryDirectory(dir=ROOT / "tmp") as temp:
            gate = calibration_gate(self.make_evidence(Path(temp), correct=0))
            self.assertFalse(gate["passed"])
            self.assertFalse(gate["checks"]["one_correct_ordinary_repair"])

    def test_simulation_and_unbound_audit_cannot_authorize_main(self):
        for settings in ({"live": False}, {"bad_binding": True}):
            with TemporaryDirectory(dir=ROOT / "tmp") as temp:
                self.assertFalse(calibration_gate(self.make_evidence(Path(temp), **settings))["passed"])

    def test_bound_positive_control_gate(self):
        with TemporaryDirectory(dir=ROOT / "tmp") as temp:
            gate = calibration_gate(self.make_evidence(Path(temp)))
            self.assertTrue(gate["passed"])
            self.assertEqual(gate["eligible"], 4)
            self.assertEqual(gate["control_correct"], 4)
