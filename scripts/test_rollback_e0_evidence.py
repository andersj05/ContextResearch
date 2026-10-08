"""Bounded negative probes of archived E0 evidence, outside the model cohorts."""
import json
from pathlib import Path
import shutil
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from scripts.verify_rollback_e0 import ARCHIVE, inventory, seal, verify
from experiments.dependency_memory.rollback_pilot.records import wire
from experiments.dependency_memory.rollback_pilot.test_controller import workspace_temp

SOURCE = ROOT / "experiments/dependency_memory/results/rollback_e0_2026-10-08"


class E0EvidenceTests(unittest.TestCase):
    def copy_fixture(self):
        temp = workspace_temp()
        self.addCleanup(temp.cleanup)
        folder = Path(temp.name) / "evidence"
        shutil.copytree(SOURCE, folder)
        if not (folder / ARCHIVE).exists():
            seal(folder)
        return folder

    def reseal_changed_binding(self, folder):
        path = folder / ARCHIVE
        data = json.loads(path.read_text())
        data["files"] = inventory(folder)
        path.write_text(wire(data))

    def test_current_evidence_verifies_without_modification(self):
        checked = verify(SOURCE, require_seal=False)
        self.assertEqual(checked["independent_math_candidates"], 210656)
        self.assertEqual(checked["verified_dispatches"], 144)
        self.assertEqual(checked["model_calls"], 0)

    def test_changed_saved_response_is_rejected_by_archive_hash(self):
        folder = self.copy_fixture()
        response = next((folder / "scripted_controller" / "responses").glob("*.json"))
        response.write_text(response.read_text() + " ")
        with self.assertRaisesRegex(ValueError, "archive"):
            verify(folder)

    def test_falsified_math_counts_are_rejected_even_with_updated_archive_hashes(self):
        folder = self.copy_fixture()
        path = folder / "math_certificates.json"
        certificates = json.loads(path.read_text())
        certificates[0]["valid_assignments"] += 1
        path.write_text(wire(certificates))
        path = folder / "summary.json"
        summary = json.loads(path.read_text())
        summary["math_certificates"] = certificates
        path.write_text(wire(summary))
        self.reseal_changed_binding(folder)
        with self.assertRaisesRegex(ValueError, "mathematical certificate"):
            verify(folder)

    def test_dispatch_without_reservation_is_rejected_even_with_updated_archive_hashes(self):
        folder = self.copy_fixture()
        path = folder / "scripted_controller" / "usage_events.jsonl"
        events = [json.loads(line) for line in path.read_text().splitlines()]
        events.pop(1)
        for i, event in enumerate(events):
            event["seq"] = i + 1
        path.write_text("".join(wire(row) + "\n" for row in events))
        self.reseal_changed_binding(folder)
        with self.assertRaisesRegex(ValueError, "reservation"):
            verify(folder)

    def test_unregistered_extra_archive_file_is_rejected(self):
        folder = self.copy_fixture()
        (folder / "unregistered.json").write_text("{}")
        with self.assertRaisesRegex(ValueError, "archive"):
            verify(folder)


if __name__ == "__main__":
    unittest.main()
