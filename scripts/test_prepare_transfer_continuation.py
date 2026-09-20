"""Synthetic continuation-certificate invariants; no active evidence or model calls."""
from copy import deepcopy
from decimal import Decimal
import hashlib
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import prepare_transfer_continuation as module
from prepare_transfer_continuation import (RESERVATION, certificate_from_evidence,
                                         classify_attempt, load_phase)
from audit_transfer_run import digest
from transfer_interface import request_bytes
import transfer_study as study


class ContinuationCertificateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # These are public frozen-design fixtures, not any saved model outputs.
        cls.plan = study.make_plan()
        cls.worker_cases = [[case for case in cls.plan["cases"] if case["worker"] == worker]
                            for worker in range(4)]

    def phase(self, phase_id, entries=()):
        """Construct independently metered synthetic prior evidence.

        Entries are (worker, original-worker-offset, outcome-kind, settled-price).
        Only the filesystem entry point claims a fresh real-evidence audit.
        """
        manifest = {"version":"transfer_study_v1", "phase_id":phase_id, "fake":False,
            "plan":self.plan, "plan_sha256":digest(self.plan),
            "source_commit":f"{phase_id + 1:040x}"}
        workers = []
        total_spent = total_uncertain = Decimal(0)
        total_dispatched = 0
        for worker in range(4):
            ledger = []
            spent = uncertain = Decimal(0)
            dispatched = 0
            for owner, offset, kind, price in entries:
                if owner != worker:
                    continue
                case = self.worker_cases[worker][offset]
                raw = request_bytes(case["request"])
                ticket = dispatched + 1
                meta = {"dispatched":False}
                if kind in ("completed", "policy_failure", "post_quota", "uncertain"):
                    dispatched += 1
                    meta = {"dispatched":True, "attempt_ticket":ticket,
                        "thread_id":f"synthetic-{phase_id}-{worker}-{ticket}"}
                    if kind == "uncertain":
                        meta["credit_accounting"] = {"ticket":ticket, "status":"reservation_retained"}
                        uncertain += RESERVATION
                    else:
                        amount = Decimal(price)
                        meta["credit_accounting"] = {"ticket":ticket, "status":"settled",
                            "conservative_credit_equivalent_exact":str(amount)}
                        spent += amount
                if kind == "gate":
                    meta = {}
                status = kind if kind in ("completed", "policy_failure") else "transport_failure"
                attempt = {"case_id":case["case_id"], "worker":worker, "block":case["block"],
                    "attempt":len(ledger)+1, "request_utf8":raw.decode(),
                    "request_sha256":hashlib.sha256(raw).hexdigest(), "request_bytes":len(raw),
                    "status":status, "provider_metadata":meta, "response":None}
                if status != "completed":
                    attempt["error_type"] = "StudyStopped" if kind == "gate" else "SyntheticFailure"
                ledger.append(attempt)
            budget = {"pending_ticket":None, "cap_credit_equivalent_exact":"50",
                "settled_credit_equivalent_exact":str(spent),
                "uncertain_credit_reservations_exact":str(uncertain),
                "committed_credit_equivalent_exact":str(spent+uncertain)}
            workers.append({"ledger":ledger, "summary":{"worker":worker,
                "request_audit_sha256":digest(ledger), "request_attempts":len(ledger),
                "model_requests":dispatched, "credit_budget":budget}})
            total_spent += spent
            total_uncertain += uncertain
            total_dispatched += dispatched
        return {"run_directory":f"synthetic-phase-{phase_id}", "manifest":manifest, "workers":workers,
            "audit":{"passed":True, "fake":False, "manifest_sha256":digest(manifest),
                "source_commit":manifest["source_commit"], "source_blobs_checked":1,
                "model_requests":total_dispatched, "settled_credit_equivalent":str(total_spent),
                "retained_credit_equivalent":str(total_uncertain)}}

    def rehash_ledger(self, phase, worker=0):
        phase["workers"][worker]["summary"]["request_audit_sha256"] = digest(phase["workers"][worker]["ledger"])

    def test_only_proved_first_submissions_remain_eligible(self):
        phase = self.phase(0, [(0,0,"completed",".1"), (0,1,"policy_failure",".2"),
            (0,2,"post_quota",".3"), (0,3,"uncertain","0"),
            (0,4,"preflight","0"), (1,0,"gate","0")])
        result = certificate_from_evidence([phase])
        self.assertEqual((result["prior_host_attempts"], result["prior_model_attempts"],
                          result["remaining_model_attempt_cap"]), (6,4,1532))
        eligible = result["workers"][0]["eligible_case_ids"]
        self.assertEqual(eligible, [c["case_id"] for c in self.worker_cases[0][4:]])
        self.assertEqual(result["workers"][0]["remaining_credit_equivalent_cap_exact"], "38.9975")
        self.assertEqual(result["remaining_credit_equivalent_cap_exact"], "188.9975")
        self.assertEqual(result["prior_retained_reservations_exact"], "10.4025")
        self.assertEqual(result["new_model_requests"], 0)
        self.assertFalse(result["response_quality_used_for_eligibility"])

    def test_preflight_then_first_dispatch_counts_once_across_phases(self):
        before = self.phase(0, [(0,0,"preflight","0")])
        after = self.phase(1, [(0,0,"completed",".1"), (1,0,"completed",".2")])
        result = certificate_from_evidence([before, after])
        self.assertEqual((result["prior_host_attempts"],result["prior_model_attempts"]), (3,2))
        self.assertEqual(result["remaining_credit_equivalent_cap_exact"], "199.7")
        case = next(c for c in result["case_dispositions"] if c["case_id"] == self.worker_cases[0][0]["case_id"])
        self.assertEqual([h["classification"] for h in case["prior_attempt_history"]], ["preflight_only","dispatched"])

    def test_disjoint_phases_preserve_residual_per_worker_budget(self):
        before = self.phase(0, [(0,0,"completed","3"), (2,0,"post_quota","2")])
        after = self.phase(1, [(0,1,"completed","4"), (2,1,"uncertain","0")])
        result = certificate_from_evidence([before, after])
        self.assertEqual(result["workers"][0]["remaining_credit_equivalent_cap_exact"], "43")
        self.assertEqual(result["workers"][2]["remaining_credit_equivalent_cap_exact"], "37.5975")
        self.assertEqual(result["remaining_credit_equivalent_cap_exact"], "180.5975")

    def test_prior_success_failure_and_uncertainty_cannot_be_retried(self):
        for kind in ("completed", "policy_failure", "post_quota", "uncertain"):
            with self.subTest(kind=kind):
                before = self.phase(0, [(0,0,kind,".1")])
                after = self.phase(1, [(0,0,"completed",".1")])
                with self.assertRaisesRegex(ValueError, "Previously dispatched"):
                    certificate_from_evidence([before, after])

    def test_ambiguous_missing_metadata_and_unfinished_rows_are_rejected(self):
        for kind in ("missing", "reserved"):
            phase = self.phase(0, [(0,0,"gate","0")])
            attempt = phase["workers"][0]["ledger"][0]
            if kind == "missing":
                attempt["error_type"] = "UnknownCrash"
            else:
                attempt["status"] = "reserved"
            self.rehash_ledger(phase)
            with self.assertRaisesRegex(ValueError, "Ambiguous dispatch"):
                certificate_from_evidence([phase])

    def test_response_quality_does_not_affect_remaining_schedule(self):
        before = self.phase(0, [(0,0,"completed",".1")])
        first = certificate_from_evidence([before])
        before["workers"][0]["ledger"][0]["response"] = {"keys":["different-selection"]}
        self.rehash_ledger(before)
        second = certificate_from_evidence([before])
        self.assertEqual([w["eligible_case_ids"] for w in first["workers"]],
                         [w["eligible_case_ids"] for w in second["workers"]])
        self.assertNotEqual(first["certificate_sha256"], second["certificate_sha256"])

    def test_hash_drift_and_forged_zero_dispatch_are_rejected(self):
        phase = self.phase(0, [(0,0,"completed",".1")])
        attempt = phase["workers"][0]["ledger"][0]
        attempt["provider_metadata"]["dispatched"] = False
        attempt["status"] = "transport_failure"
        self.rehash_ledger(phase)
        with self.assertRaisesRegex(ValueError, "Contradictory preflight"):
            certificate_from_evidence([phase])
        phase = self.phase(0, [(0,0,"completed",".1")])
        phase["workers"][0]["ledger"][0]["request_utf8"] += " "
        self.rehash_ledger(phase)
        with self.assertRaisesRegex(ValueError, "request bytes changed"):
            certificate_from_evidence([phase])

    def test_combined_worker_cap_cannot_be_reset_by_new_phase(self):
        before = self.phase(0, [(0,i,"completed","10") for i in range(3)])
        after = self.phase(1, [(0,i,"completed","10") for i in range(3,6)])
        with self.assertRaisesRegex(ValueError, "Combined prior worker budget"):
            certificate_from_evidence([before, after])

    def test_insufficient_residual_reservation_is_reported_without_new_funds(self):
        before = self.phase(0, [(0,i,"completed","10") for i in range(4)])
        result = certificate_from_evidence([before])
        self.assertEqual(result["workers"][0]["remaining_credit_equivalent_cap_exact"], "10")
        self.assertFalse(result["workers"][0]["first_reservation_fits"])

    def test_duplicate_phase_and_counter_drift_are_rejected(self):
        phase = self.phase(0, [(0,0,"completed",".1")])
        with self.assertRaisesRegex(ValueError, "Duplicate prior phase"):
            certificate_from_evidence([phase, phase])
        phase["workers"][0]["summary"]["model_requests"] = 0
        with self.assertRaisesRegex(ValueError, "model-attempt count"):
            certificate_from_evidence([phase])

    def test_reordered_public_schedule_and_missing_commit_provenance_are_rejected(self):
        before, after = self.phase(0), self.phase(1)
        altered = {**self.plan, "cases":list(self.plan["cases"])}
        altered["cases"][0], altered["cases"][1] = altered["cases"][1], altered["cases"][0]
        after["manifest"]["plan"] = altered
        after["manifest"]["plan_sha256"] = digest(altered)
        after["audit"]["manifest_sha256"] = digest(after["manifest"])
        with self.assertRaisesRegex(ValueError, "Public schedule changed"):
            certificate_from_evidence([before, after])
        before["audit"]["source_blobs_checked"] = 0
        with self.assertRaisesRegex(ValueError, "Git source provenance"):
            certificate_from_evidence([before])

    def test_active_directory_is_rejected_before_any_response_read_or_audit(self):
        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary)
            (directory / "manifest.json").write_text("{}",encoding="utf-8")
            with patch.object(module, "audit", side_effect=AssertionError("Must not inspect active evidence")) as mocked:
                with self.assertRaisesRegex(ValueError, "not finalized"):
                    load_phase(directory)
                mocked.assert_not_called()


class DispatchClassificationTests(unittest.TestCase):
    def test_missing_flag_is_accepted_only_for_proved_closed_gate(self):
        self.assertEqual(classify_attempt({"status":"transport_failure", "provider_metadata":{},
                                          "error_type":"StudyStopped"})[0], "preflight_only")
        for meta in ({}, {"dispatched":None}, {"dispatched":"false"}):
            with self.assertRaisesRegex(ValueError, "Ambiguous dispatch"):
                classify_attempt({"status":"transport_failure", "provider_metadata":meta,
                                  "error_type":"TransportError"})

    def test_retained_reservation_is_always_a_consumed_case(self):
        attempt = {"status":"transport_failure", "provider_metadata":{"dispatched":True,
            "attempt_ticket":1, "credit_accounting":{"status":"reservation_retained", "ticket":1}}}
        self.assertEqual(classify_attempt(attempt), ("dispatched_uncertain", Decimal(0), RESERVATION))


if __name__ == "__main__":
    unittest.main()
