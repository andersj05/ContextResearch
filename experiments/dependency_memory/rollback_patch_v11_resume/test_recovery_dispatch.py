"""Recovery accounting invariants with constructed envelopes and no model calls."""

from dataclasses import dataclass
from contextlib import closing
from pathlib import Path
import sqlite3
import tempfile
import unittest

from experiments.dependency_memory.rollback_patch_v11.common import ROOT, save_new, sha, wire
from experiments.dependency_memory.rollback_patch_v11.engine import identity
from experiments.dependency_memory.rollback_patch_v11_resume.recovery import copy_history
from experiments.dependency_memory.rollback_development_v5.accounting import Stopped
from experiments.dependency_memory.rollback_development_v5.audit import ReplayMismatch, ledger_rows
from experiments.dependency_memory.rollback_development_v5_continuation.accounting import Ledger, CallUnknown
from experiments.dependency_memory.rollback_development_v5_continuation.dispatch import Dispatcher
from experiments.dependency_memory.rollback_pilot.subscription.accounting import Usage, RESERVATION
from experiments.dependency_memory.rollback_pilot.subscription.transport import Response


@dataclass(frozen=True)
class Envelope:
    text: str = "constructed public state"

    def data(self):
        return {"messages": [{"role": "user", "content": self.text}]}

    @property
    def json_text(self):
        return wire(self.data())


class RecoveryDispatchTests(unittest.TestCase):
    def setUp(self):
        (ROOT / "tmp").mkdir(exist_ok=True)
        self.temp = tempfile.TemporaryDirectory(dir=ROOT / "tmp", prefix="v11-resume-dispatch-")
        self.addCleanup(self.temp.cleanup)
        self.folder = Path(self.temp.name)
        task = {"task_id": "constructed-v11-task"}
        self.done, self.unknown, self.next, self.spare = (
            identity(task, "K0", 1), identity(task, "RL", 1),
            identity(task, "K0", 2), identity(task, "K0", 3))
        self.allocation = [self.done, self.unknown, self.next, self.spare]
        self.request = Envelope()
        self.sent = []

    def factory(self):
        sent = self.sent

        class ConstructedTransport:
            def generate(self, item, request):
                sent.append(item.key)
                return Response("constructed response", Usage(9, 0, 3, 1),
                                {"thread_id": "constructed-thread-" + item.key})

        return ConstructedTransport()

    def imported(self, ceiling=4):
        prior = self.folder / "prior"
        ledger = Ledger(prior / "ledger.sqlite", self.allocation, 1, generation_ceiling=4)
        invoke = Dispatcher(prior, {"source_bindings": []}, ledger, self.factory)
        response = invoke(self.done, self.request)
        ledger.admit(self.unknown, sha(self.request.json_text))
        save_new(prior / "requests" / (self.unknown.key + ".json"), self.request.data())
        diagnostic = {"version": 1, "phase": "quota", "reason_code": "rpc_error",
                      "rpc_method": "account/rateLimits/read", "rpc_numeric_code": -32603,
                      "observation": {}}
        save_new(prior / "diagnostics" / (self.unknown.key + ".json"), diagnostic)
        ledger.unknown(self.unknown, "constructed_quota_error", diagnostic=diagnostic, fatal=True)
        calls, events, stop = ledger_rows(prior / "ledger.sqlite")
        self.assertEqual(stop, "systemic_transport_failure")
        prior_hash = sha((prior / "ledger.sqlite").read_bytes())
        current = self.folder / "current"
        copy_history(prior, current, calls)
        cumulative = Ledger(current / "ledger.sqlite", self.allocation, 1,
                            prior=prior / "ledger.sqlite", generation_ceiling=ceiling)
        self.sent.clear()
        return prior, current, cumulative, response, calls, events, prior_hash

    def test_exact_history_import_and_receipt_replay_send_only_next_unsent(self):
        prior, current, ledger, response, old_calls, old_events, prior_hash = self.imported()
        imported_calls, imported_events, stop = ledger_rows(current / "ledger.sqlite")
        self.assertEqual(imported_calls, old_calls)
        self.assertEqual(imported_events, old_events)
        self.assertIsNone(stop)
        with closing(sqlite3.connect(current / "ledger.sqlite")) as db:
            self.assertEqual(db.execute("SELECT reason FROM inherited_stops").fetchall(),
                             [("systemic_transport_failure",)])
        invoke = Dispatcher(current, {"source_bindings": []}, ledger, self.factory, historical=old_calls)
        self.assertEqual(invoke(self.done, self.request), response)
        self.assertEqual(self.sent, [])
        self.assertEqual(ledger_rows(current / "ledger.sqlite")[1], old_events)
        invoke(self.next, self.request)
        self.assertEqual(self.sent, [self.next.key])
        new_calls, new_events, _ = ledger_rows(current / "ledger.sqlite")
        self.assertEqual(new_events[:len(old_events)], old_events)
        by_id = {row["call_id"]: row for row in new_calls}
        self.assertTrue(all(by_id[row["call_id"]] == row for row in old_calls))
        self.assertEqual(len(new_calls), 3)
        self.assertEqual(sha((prior / "ledger.sqlite").read_bytes()), prior_hash)
        with self.assertRaises(ReplayMismatch):
            invoke(self.done, self.request)
        self.assertEqual(self.sent, [self.next.key])

    def test_unknown_admission_stays_unknown_without_transport_or_new_admission(self):
        _, current, ledger, _, calls, events, _ = self.imported()

        def forbidden_factory():
            self.fail("unknown recovery created a transport")

        invoke = Dispatcher(current, {"source_bindings": []}, ledger, forbidden_factory, historical=calls)
        with self.assertRaises(CallUnknown):
            invoke(self.unknown, self.request)
        snapshot = ledger.snapshot()
        self.assertEqual(snapshot["unknown_or_inflight_calls"], 1)
        self.assertEqual(snapshot["locked_planning_credits"], str(RESERVATION))
        self.assertEqual(ledger_rows(current / "ledger.sqlite")[1], events)
        self.assertFalse((current / "responses" / (self.unknown.key + ".json")).exists())

    def test_historical_request_change_stops_before_transport(self):
        _, current, ledger, _, calls, _, _ = self.imported()
        invoke = Dispatcher(current, {"source_bindings": []}, ledger, self.factory, historical=calls)
        with self.assertRaises(ReplayMismatch):
            invoke(self.done, Envelope("changed information"))
        self.assertEqual(self.sent, [])
        self.assertEqual(len(ledger.snapshot()["calls"]), 2)
        self.assertEqual(ledger.snapshot()["stop"], "historical_request_mismatch")

    def test_cumulative_ceiling_includes_completed_and_unknown_original_calls(self):
        _, current, ledger, _, calls, _, _ = self.imported(ceiling=3)
        invoke = Dispatcher(current, {"source_bindings": []}, ledger, self.factory, historical=calls)
        invoke(self.next, self.request)
        with self.assertRaises(Stopped):
            invoke(self.spare, self.request)
        self.assertEqual(self.sent, [self.next.key])
        self.assertEqual(len(ledger.snapshot()["calls"]), 3)
        self.assertEqual(ledger.snapshot()["stop"], "generation_ceiling_reached")
        self.assertEqual(ledger.snapshot()["unknown_or_inflight_calls"], 1)


if __name__ == "__main__":
    unittest.main()
