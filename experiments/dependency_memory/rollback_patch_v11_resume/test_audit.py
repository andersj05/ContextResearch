"""Constructed recovery-audit invariants; no provider or Docker calls."""
from copy import deepcopy
from dataclasses import asdict
import unittest

from experiments.dependency_memory.rollback_patch_v11.engine import identity
from experiments.dependency_memory.rollback_patch_v11_resume.audit import (
    cumulative_accounting, partition_phases,
)
from experiments.dependency_memory.rollback_checkpoint_v7.audit import _metering
from experiments.dependency_memory.rollback_development_v5.audit import ReplayMismatch
from experiments.dependency_memory.rollback_pilot.subscription.accounting import RESERVATION, Usage


def fixture():
    task = {"task_id": "constructed-recovery-audit"}
    old_identity, new_identity = identity(task, "K0", 1), identity(task, "R0", 1)
    old = {"call_id": old_identity.key, "identity": asdict(old_identity),
           "request_hash": "old-hash", "state": "unknown", "failure_scope": "global",
           "reserve_credits": str(RESERVATION), "reason": "constructed_quota_rpc_error"}
    usage = Usage(20, 4, 3, 1)
    new = {"call_id": new_identity.key, "identity": asdict(new_identity),
           "request_hash": "new-hash", "state": "completed", "usage": asdict(usage),
           "planning_credits": str(usage.cost), "metadata": {"thread_id": "new-thread"}}

    def events(call):
        return [{"call_id": call["call_id"], "state": "dispatched",
                 "payload": {"admitted_utc": "constructed", "reserve_credits": str(RESERVATION)}},
                {"call_id": call["call_id"], "state": call["state"],
                 "payload": {key: value for key, value in call.items()
                             if key not in {"call_id", "identity", "request_hash", "state"}}}]

    old_events, new_events = events(old), events(new)
    manifest = {"schedule": [asdict(old_identity), asdict(new_identity)], "generation_ceiling": 2}
    return old, new, old_events, new_events, manifest


class RecoveryAuditTests(unittest.TestCase):
    def test_exact_old_prefix_partitions_without_reclassifying_unknown(self):
        old, new, old_events, new_events, _ = fixture()
        before = deepcopy((old, new, old_events, new_events))
        self.assertEqual(partition_phases([new, old], old_events + new_events, [old], old_events),
                         ([new], new_events))
        self.assertEqual((old, new, old_events, new_events), before)
        self.assertEqual(old["failure_scope"], "global")

    def test_changed_historical_call_is_rejected(self):
        old, new, old_events, new_events, _ = fixture()
        changed = deepcopy(old)
        changed["failure_scope"] = "trajectory"
        with self.assertRaisesRegex(ReplayMismatch, "historical call row changed"):
            partition_phases([changed, new], old_events + new_events, [old], old_events)

    def test_changed_historical_event_is_rejected(self):
        old, new, old_events, new_events, _ = fixture()
        changed = deepcopy(old_events + new_events)
        changed[1]["payload"]["reason"] = "normalized_fault"
        with self.assertRaisesRegex(ReplayMismatch, "historical events changed"):
            partition_phases([old, new], changed, [old], old_events)

    def test_old_identity_cannot_be_readmitted_in_new_phase(self):
        old, new, old_events, new_events, _ = fixture()
        with self.assertRaisesRegex(ReplayMismatch, "historical identity repeated"):
            partition_phases([old, new], old_events + old_events + new_events, [old], old_events)

    def test_duplicate_call_rows_are_not_collapsed(self):
        old, new, old_events, new_events, _ = fixture()
        with self.assertRaisesRegex(ReplayMismatch, "duplicate cumulative call"):
            partition_phases([old, new, deepcopy(new)], old_events + new_events, [old], old_events)

    def test_missing_historical_call_is_rejected(self):
        old, new, old_events, new_events, _ = fixture()
        with self.assertRaisesRegex(ReplayMismatch, "historical call row changed"):
            partition_phases([new], old_events + new_events, [old], old_events)

    def test_cumulative_meter_retains_old_reservation_and_new_usage(self):
        old, new, _, _, _ = fixture()
        actual = cumulative_accounting([old, new], None)
        self.assertEqual(actual["completed_calls"], 1)
        self.assertEqual(actual["unknown_or_inflight_calls"], 1)
        self.assertEqual(actual["locked_planning_credits"], "4.225")
        self.assertEqual(actual["planning_credits"], "0.0000785")
        self.assertEqual(actual["usage"], {"input_tokens": 20, "cached_input": 4,
                                          "output": 3, "reasoning": 1})
        self.assertIsNone(actual["actual_account_charge"])
        self.assertEqual(actual["API_key_calls"], 0)

    def test_prior_fatal_stop_remains_fatal_within_its_own_phase(self):
        old, new, old_events, new_events, manifest = fixture()
        settings = {"workers": 1, "live": False}
        with self.assertRaisesRegex(ReplayMismatch, "admission after fatal failure"):
            _metering([old, new], old_events + new_events, "systemic_transport_failure", manifest, settings)
        remaining, suffix = partition_phases([old, new], old_events + new_events, [old], old_events)
        old_accounting, old_peak = _metering([old], old_events, "systemic_transport_failure", manifest, settings)
        new_accounting, new_peak = _metering(remaining, suffix, None, manifest, settings)
        self.assertEqual(old_accounting["unknown_or_inflight_calls"], 1)
        self.assertEqual(new_accounting["completed_calls"], 1)
        self.assertEqual((old_peak, new_peak), (1, 1))
        with self.assertRaisesRegex(ReplayMismatch, "systemic fault did not stop admissions"):
            _metering([old], old_events, None, manifest, settings)


if __name__ == "__main__":
    unittest.main()
