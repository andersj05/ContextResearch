"""Scientific invariants of the reporting contract, using explicit dev mutations."""
from copy import deepcopy
from itertools import combinations
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from .grader import CHECKS, expected_answer, grade, wire
from .packet import HERE, direct_records, hashes, preflight, validate_capture, validate_lock


class PacketTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.capture = validate_capture()

    def setUp(self):
        self.records = deepcopy(self.capture["records"])
        self.task = {"snapshot": self.capture["source"]["tree"],
                     "required_checks": list(CHECKS),
                     "artifacts": deepcopy(self.records[-1]["artifacts"])}
        # Expected answers are written from the observation positions, not the
        # memory implementation or the grader under test.
        self.success = {"ready": True, "needs_work": [], "evidence": {
            "tests": self.records[0]["run_id"],
            "repository": self.records[1]["run_id"],
            "paper": self.records[2]["run_id"]}}

    def test_actual_development_commands_support_exact_ready_answer(self):
        self.assertEqual([0, 0, 0], [r["returncode"] for r in self.records])
        self.assertEqual(self.success, expected_answer(self.records, self.task))
        self.assertTrue(grade(self.records, self.task, json.dumps(self.success))["exact"])

    def test_later_failure_supersedes_success_on_same_snapshot(self):
        failed = deepcopy(self.records[0])
        failed.update(run_id="f" * 64, returncode=1)
        self.records.append(failed)  # Constructed control, not a historical run.
        expected = deepcopy(self.success)
        expected.update(ready=False, needs_work=["tests"])
        del expected["evidence"]["tests"]
        self.assertEqual(expected, expected_answer(self.records, self.task))
        self.assertTrue(grade(self.records, self.task, json.dumps(self.success))["false_ready"])
        self.assertEqual("f" * 64, direct_records(self.records)[-1]["run_id"])

    def test_new_source_snapshot_requires_new_evidence(self):
        self.task["snapshot"] = "a" * 40
        expected = {"ready": False, "needs_work": list(CHECKS), "evidence": {}}
        self.assertEqual(expected, expected_answer(self.records, self.task))

    def test_return_to_identical_source_can_use_that_snapshots_receipts(self):
        other = deepcopy(self.records[0])
        other.update(snapshot="b" * 40, run_id="c" * 64, returncode=1)
        self.records.append(other)
        self.assertEqual(self.success, expected_answer(self.records, self.task))

    def test_build_artifact_change_or_deletion_only_invalidates_build(self):
        path = "build/paper/preview.html"
        for replacement in ("d" * 64, None):
            with self.subTest(replacement=replacement):
                task = deepcopy(self.task)
                if replacement is None:
                    del task["artifacts"][path]
                else:
                    task["artifacts"][path] = replacement
                expected = deepcopy(self.success)
                expected.update(ready=False, needs_work=["paper"])
                del expected["evidence"]["paper"]
                self.assertEqual(expected, expected_answer(self.records, task))

    def test_unrequested_failure_does_not_poison_requested_check(self):
        self.records[0]["returncode"] = 1
        self.task["required_checks"] = ["paper"]
        expected = {"ready": True, "needs_work": [],
                    "evidence": {"paper": self.records[2]["run_id"]}}
        self.assertEqual(expected, expected_answer(self.records, self.task))

    def test_fabricated_receipt_and_always_abstain_are_not_success(self):
        forged = deepcopy(self.success)
        forged["evidence"]["tests"] = "e" * 64
        self.assertFalse(grade(self.records, self.task, json.dumps(forged))["exact"])
        abstain = {"ready": False, "needs_work": list(CHECKS), "evidence": {}}
        self.assertFalse(grade(self.records, self.task, json.dumps(abstain))["exact"])

    def test_strict_json_rejects_ambiguous_or_wrongly_typed_answers(self):
        for raw in ('{"ready":true,"ready":false,"needs_work":[],"evidence":{}}',
                    '{"ready":1,"needs_work":[],"evidence":{}}',
                    '{"ready":true,"needs_work":[[]],"evidence":{}}',
                    '{"ready":true,"needs_work":[],"evidence":{},"score":NaN}',
                    '[]', 'null', '```json\n{}\n```'):
            with self.subTest(raw=raw):
                self.assertTrue(grade(self.records, self.task, raw)["malformed"])

    def test_invalid_evaluator_input_raises_instead_of_scoring_model_failure(self):
        self.records.append(deepcopy(self.records[0]))
        with self.assertRaisesRegex(ValueError, "Duplicate run"):
            grade(self.records, self.task, "{}")
        with self.assertRaises(ValueError):
            expected_answer([], {**self.task, "required_checks": ["unknown"]})

    def test_successful_build_cannot_silently_omit_artifact_bindings(self):
        self.records[-1]["artifacts"] = {}
        with self.assertRaisesRegex(ValueError, "bind both artifacts"):
            expected_answer(self.records, self.task)

    def test_direct_retention_preserves_all_subset_answers_across_two_boundaries(self):
        # Add a different revision and a later failed run. Cross-check the
        # projection against independent raw-ledger grading for every scope.
        revision = "1" * 40
        changed = deepcopy(self.records[0])
        changed.update(snapshot=revision, run_id="2" * 64)
        failed = deepcopy(changed)
        failed.update(run_id="3" * 64, returncode=1)
        self.records.extend([changed, failed])
        parent = direct_records(self.records)
        for size in range(1, len(CHECKS) + 1):
            for scope in combinations(CHECKS, size):
                child = direct_records(parent, scope)
                for snapshot in (self.task["snapshot"], revision):
                    task = {**self.task, "snapshot": snapshot, "required_checks": list(scope)}
                    self.assertEqual(expected_answer(self.records, task), expected_answer(child, task))

    def test_lock_detects_changed_and_unlisted_packet_inputs(self):
        with TemporaryDirectory() as name:
            root = Path(name)
            (root / "example.txt").write_text("observed", encoding="utf-8")
            lock = {"packet_version": 1, "sha256": hashes(root)}
            (root / "packet-lock.json").write_bytes(wire(lock))
            self.assertEqual(1, validate_lock(root))
            (root / "example.txt").write_text("edited", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "differ"):
                validate_lock(root)
            (root / "example.txt").write_text("observed", encoding="utf-8")
            (root / "new.json").write_text("{}", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "differ"):
                validate_lock(root)

    def test_capture_output_tampering_is_detected_independently_of_lock(self):
        with TemporaryDirectory() as name:
            root = Path(name)
            for path in (HERE / "development").iterdir():
                if path.is_file():
                    (root / path.name).write_bytes(path.read_bytes())
            (root / "tests.stderr.txt").write_bytes(b"forged success")
            with self.assertRaisesRegex(ValueError, "output changed"):
                validate_capture(root)

    def test_packet_cannot_be_mistaken_for_live_authorization(self):
        report = preflight()
        self.assertEqual("PASS", report["packet_status"])
        self.assertFalse(report["launch_ready"])
        self.assertEqual(0, report["authorized_dispatches"])
        self.assertEqual(0, report["model_calls"])
        self.assertEqual(0, report["held_out_evaluation_episodes"])
        self.assertEqual(144, report["proposed_max_dispatches"])
        self.assertTrue(report["parent_fits"])
        self.assertTrue(report["child_fits"])


if __name__ == "__main__":
    unittest.main()
