"""Audit failures must remain evidence errors, never candidate outcomes."""
from copy import deepcopy
from contextlib import closing
from dataclasses import asdict
from pathlib import Path
import json
import sqlite3
import tempfile
import unittest

from experiments.dependency_memory.rollback_patch_v9.audit import (
    Replay, ReplayMismatch, reconcile_ledger, _inventory,
)
from experiments.dependency_memory.rollback_patch_v9.common import ROOT, MODEL, EFFORT, read, save_new, sha
from experiments.dependency_memory.rollback_patch_v9.contexts import render
from experiments.dependency_memory.rollback_patch_v9.engine import run_prefix
from experiments.dependency_memory.rollback_patch_v9.prepare import identities
from experiments.dependency_memory.rollback_patch_v9.tasks import generate
from experiments.dependency_memory.rollback_parallel_v8.accounting import Ledger
from experiments.dependency_memory.rollback_development_v5.accounting import Stopped
from experiments.dependency_memory.rollback_development_v5_continuation.accounting import CallUnknown
from experiments.dependency_memory.rollback_pilot.subscription.accounting import Usage, RESERVATION


class EvidenceAuditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.task = generate(split="fixture", per_family=1)[0]

    def setUp(self):
        scratch = ROOT / "tmp"
        scratch.mkdir(exist_ok=True)
        self.temporary = tempfile.TemporaryDirectory(prefix="v9-audit-test-", dir=scratch)
        self.addCleanup(self.temporary.cleanup)
        self.folder = Path(self.temporary.name)
        self.slots = identities([self.task], "calibration")
        self.manifest = {"schedule": [asdict(item) for item in self.slots],
                         "generation_ceiling": len(self.slots), "model": MODEL, "effort": EFFORT}
        self.settings = {"workers": 2, "live": False}
        self.request = render(self.task)

    def ledger(self, unknown=False):
        ledger = Ledger(self.folder / "ledger.sqlite", self.slots, 2,
                        generation_ceiling=len(self.slots))
        first = self.slots[0]
        ledger.admit(first, sha(self.request.json_text))
        save_new(self.folder / "requests" / (first.key + ".json"), self.request.data())
        usage, metadata = Usage(100, 20, 15, 0), {"thread_id": "fixture-one"}
        save_new(self.folder / "responses" / (first.key + ".json"),
                 {"text": "{}", "usage": vars(usage), "metadata": metadata, "capped": False})
        ledger.complete(first, usage, metadata, 0.1)
        if unknown:
            second = self.slots[1]
            ledger.admit(second, sha(self.request.json_text))
            save_new(self.folder / "requests" / (second.key + ".json"), self.request.data())
            ledger.unknown(second, "fixture unknown", diagnostic={"fixture": True}, fatal=False)
            save_new(self.folder / "diagnostics" / (second.key + ".json"), {"fixture": True})
        save_new(self.folder / "accounting.json", ledger.snapshot())
        return ledger

    def replace_json(self, name, value):
        (self.folder / name).write_text(json.dumps(value), encoding="utf-8")

    def test_unadmitted_request_without_stop_is_not_swallowed_by_engine(self):
        replay = Replay(self.folder, [], None)
        with self.assertRaisesRegex(ReplayMismatch, "unrecorded expected call"):
            run_prefix(self.task, replay, runtime=None)

    def test_unadmitted_request_after_global_stop_preserves_stop(self):
        replay = Replay(self.folder, [], "systemic_transport_failure")
        with self.assertRaises(Stopped):
            replay(self.slots[0], self.request)

    def test_duplicate_saved_calls_are_rejected_before_dictionary_collapse(self):
        with self.assertRaisesRegex(ReplayMismatch, "duplicate saved call"):
            Replay(self.folder, [{"call_id": "same"}, {"call_id": "same"}], None)

    def test_completed_and_unknown_calls_reconcile_without_imputation(self):
        self.ledger(unknown=True)
        calls, accounting, peak, stop = reconcile_ledger(self.folder, self.manifest, self.settings)
        self.assertEqual((len(calls), accounting["completed_calls"], accounting["unknown_or_inflight_calls"]), (2, 1, 1))
        self.assertEqual(accounting["locked_planning_credits"], str(RESERVATION))
        self.assertEqual(peak, 1)
        self.assertIsNone(stop)
        replay = Replay(self.folder, calls, stop)
        self.assertEqual(replay(self.slots[0], self.request).text, "{}")
        with self.assertRaises(CallUnknown):
            replay(self.slots[1], self.request)
        self.assertEqual(replay.used, {item.key for item in self.slots[:2]})

    def test_request_tampering_and_duplicate_replay_cannot_be_candidate_failures(self):
        ledger = self.ledger()
        replay = Replay(self.folder, ledger.snapshot()["calls"], None)
        replay(self.slots[0], self.request)
        with self.assertRaisesRegex(ReplayMismatch, "repeated replay identity"):
            replay(self.slots[0], self.request)
        self.replace_json("requests/" + self.slots[0].key + ".json", {"messages": []})
        with self.assertRaisesRegex(ReplayMismatch, "saved request differs"):
            Replay(self.folder, ledger.snapshot()["calls"], None)(self.slots[0], self.request)

    def test_changed_saved_accounting_is_rejected(self):
        self.ledger()
        accounting = read(self.folder / "accounting.json")
        accounting["calls"].append(deepcopy(accounting["calls"][0]))
        self.replace_json("accounting.json", accounting)
        with self.assertRaisesRegex(ReplayMismatch, "saved accounting differs"):
            reconcile_ledger(self.folder, self.manifest, self.settings)

    def test_terminal_sqlite_event_payload_must_equal_call_payload(self):
        self.ledger()
        with closing(sqlite3.connect(self.folder / "ledger.sqlite")) as db, db:
            value = json.loads(db.execute("SELECT payload FROM events WHERE state='completed'").fetchone()[0])
            value["planning_credits"] = "0"
            db.execute("UPDATE events SET payload=? WHERE state='completed'", (json.dumps(value),))
        with self.assertRaisesRegex(ReplayMismatch, "terminal event payload differs"):
            reconcile_ledger(self.folder, self.manifest, self.settings)

    def test_reservation_loss_or_thread_table_tampering_is_rejected(self):
        self.ledger()
        with closing(sqlite3.connect(self.folder / "ledger.sqlite")) as db, db:
            db.execute("DELETE FROM threads")
        with self.assertRaisesRegex(ReplayMismatch, "thread inventory"):
            reconcile_ledger(self.folder, self.manifest, self.settings)

    def test_extra_unadmitted_response_is_rejected(self):
        self.ledger()
        save_new(self.folder / "responses" / "unallocated.json", {})
        with self.assertRaisesRegex(ReplayMismatch, "inventory differs"):
            reconcile_ledger(self.folder, self.manifest, self.settings)

    def test_seal_rejects_extra_missing_and_changed_json_evidence(self):
        self.ledger()
        evidence = {"files": [{"path": path.relative_to(self.folder).as_posix(), "sha256": sha(path.read_bytes())}
                              for path in self.folder.rglob("*.json")],
                    "ledger_sha256": sha((self.folder / "ledger.sqlite").read_bytes())}
        save_new(self.folder / "evidence_manifest.json", evidence)
        _inventory(self.folder)
        save_new(self.folder / "extra.json", {})
        with self.assertRaisesRegex(ReplayMismatch, "inventory mismatch"):
            _inventory(self.folder)
        (self.folder / "extra.json").unlink()
        self.replace_json("accounting.json", {})
        with self.assertRaisesRegex(ReplayMismatch, "sealed evidence changed"):
            _inventory(self.folder)


if __name__ == "__main__":
    unittest.main()
