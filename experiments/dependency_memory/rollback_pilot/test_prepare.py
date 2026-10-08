"""Frozen preparation identity and explicit incomplete-cohort launch gates."""
from pathlib import Path
import unittest

from .contexts import Renderer
from .prepare import calibration_requests, prepare_bundle, verify_bundle
from .records import strict_loads, wire
from .test_controller import workspace_temp


class PreparationTests(unittest.TestCase):
    def test_bundle_freezes_twelve_real_generated_math_tasks_and_no_substitute_coding_cohort(self):
        with workspace_temp() as tmp:
            folder = Path(tmp) / "bundle"
            manifest = prepare_bundle(folder)
            checked = verify_bundle(folder)
            self.assertEqual(manifest["prepared_math_tasks"], 12)
            self.assertEqual(manifest["prepared_coding_tasks"], 0)
            self.assertEqual(checked["verified_schedule_slots"], 156)
            self.assertEqual(checked["verified_calibration_requests"], 8)
            self.assertFalse(checked["live_ready"])
            self.assertIn("coding_cohort_12_with_reviewed_provenance", manifest["open_gates"])
            self.assertIn("provider_tokenizer_and_overhead_audit", manifest["open_gates"])
            self.assertFalse(manifest["launch_authorized"])

    def test_all_eight_calibration_requests_are_independent_and_fixture_excluded(self):
        requests = calibration_requests(Renderer())
        self.assertEqual([r["stage"] for r in requests], ["checkpoint", "checkpoint", "branch", "branch", "lesson", "summary", "terminal", "terminal"])
        self.assertIn("ROUTING_MARKER_7Q9", wire(requests[6]["request"]))
        self.assertNotIn("CODE_BRANCH_ONLY_CANARY", wire(requests[7]["request"]))
        for row in requests:
            self.assertTrue(row["excluded_from_all_model_study_cohorts"])
            self.assertEqual([m["role"] for m in row["request"]["messages"]], ["system", "user"])
            self.assertNotIn("excluded_from_all_model_study_cohorts", wire(row["request"]))
            self.assertNotIn("reserved1", wire(row["request"]))
            self.assertNotIn("previous_response", wire(row["request"]))

    def test_artifact_tampering_is_detected_without_repairing_a_frozen_bundle(self):
        with workspace_temp() as tmp:
            folder = Path(tmp) / "bundle"
            prepare_bundle(folder)
            path = folder / "tasks_public.jsonl"
            path.write_bytes(path.read_bytes() + b" ")
            with self.assertRaisesRegex(ValueError, "artifact binding"):
                verify_bundle(folder)

    def test_source_digest_mismatch_is_detected(self):
        with workspace_temp() as tmp:
            folder = Path(tmp) / "bundle"
            prepare_bundle(folder)
            manifest_path = folder / "manifest.json"
            manifest = strict_loads(manifest_path.read_text())
            manifest["source_bindings"][0]["sha256"] = "0" * 64
            manifest_path.write_text(wire(manifest))
            with self.assertRaisesRegex(ValueError, "source binding"):
                verify_bundle(folder)

    def test_manifest_cannot_turn_itself_into_launch_authorization(self):
        with workspace_temp() as tmp:
            folder = Path(tmp) / "bundle"
            prepare_bundle(folder)
            manifest_path = folder / "manifest.json"
            manifest = strict_loads(manifest_path.read_text())
            manifest["launch_authorized"] = True
            manifest_path.write_text(wire(manifest))
            with self.assertRaises(ValueError):
                verify_bundle(folder)

    def test_second_preparation_never_overwrites_prior_bundle(self):
        with workspace_temp() as tmp:
            folder = Path(tmp) / "bundle"
            prepare_bundle(folder)
            original = (folder / "manifest.json").read_bytes()
            with self.assertRaises(FileExistsError):
                prepare_bundle(folder)
            self.assertEqual(original, (folder / "manifest.json").read_bytes())
