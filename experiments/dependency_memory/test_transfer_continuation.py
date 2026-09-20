"""Offline invariants for consuming residual study allocations."""
from copy import deepcopy
from decimal import Decimal
import hashlib
import json
from pathlib import Path
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

from continue_transfer_study import ContinuationCreditBudget, eligible_cases, execute, prepare_clients
from luna_appserver import LunaClient, MODEL
from luna_budget import BudgetExceeded, BudgetStopped
from run_transfer_study import _hash
from transfer_interface import VERSION as REQUEST_VERSION
from transfer_study import FakeClient, make_plan


def fixture():
    original = make_plan()
    workers = []
    for worker in range(4):
        # A missing interior case and final case exercise exact filtering.
        own = [case for case in original["cases"] if case["worker"] == worker]
        workers.append({"worker": worker, "eligible_case_ids": [own[5]["case_id"], own[-1]["case_id"]],
            "remaining_model_attempt_cap": 2, "remaining_credit_equivalent_cap_exact": "11"})
    return {"version": "transfer_continuation_launch_v1", "original_plan": original,
        "certificate": {"workers": workers, "remaining_model_attempt_cap": 8,
                        "remaining_credit_equivalent_cap_exact": "44"},
        "prior_run_dirs": [], "source_sha256": {}}


class ContinuationTests(unittest.TestCase):
    def test_saved_raw_audit_reaches_client_attestation_before_launch_readiness(self):
        # The real saved no-auth probe is intentionally not launch-ready:
        # LunaClient must still attest the installed binary and instructions.
        raw = (Path(__file__).parent / "results/transfer_transport_audit.json").read_bytes()
        audit = json.loads(raw)
        self.assertIs(audit["launch_ready"], False)
        self.assertIs(audit["isolation_passed"], True)
        self.assertEqual(audit["public_request_contract"], REQUEST_VERSION)
        plan = fixture()
        audit_path = "experiments/dependency_memory/results/transfer_transport_audit.json"
        plan["source_sha256"][audit_path] = hashlib.sha256(raw).hexdigest()
        args = SimpleNamespace(executable=Path("never-started.exe"), authorization="bounded continuation")
        clients = [SimpleNamespace(metadata={}) for _ in range(4)]
        advertised = {"model": MODEL, "hidden": False}
        with patch("continue_transfer_study.make_launch_plan", return_value=plan), \
             patch("continue_transfer_study.runner.source_commit", return_value="0" * 40), \
             patch.object(Path, "read_bytes", return_value=raw), \
             patch("continue_transfer_study.LunaClient", side_effect=clients) as client_factory, \
             patch("continue_transfer_study.AppServer") as server_factory:
            server = server_factory.return_value
            server.rpc.return_value = {"data": [advertised]}
            prepared = prepare_clients(args, plan)
        self.assertEqual(prepared, clients)
        self.assertEqual(client_factory.call_count, 4)
        for call in client_factory.call_args_list:
            self.assertIs(call.args[1]["launch_ready"], False)
            self.assertEqual(call.args[1]["public_request_contract"], REQUEST_VERSION)
            self.assertTrue(call.kwargs["credit_backed_quota"])
        server_factory.assert_called_once()
        server.initialize.assert_called_once_with()
        server.rpc.assert_called_once_with("model/list", {"includeHidden": True, "limit": 100})
        server.close.assert_called_once_with()
        self.assertTrue(all(client.metadata["advertised_model"] == advertised for client in prepared))

    def test_wrong_wire_contract_is_rejected_before_client_or_process_creation(self):
        plan = fixture()
        audit = {"public_request_contract": "different_request_contract", "launch_ready": True}
        raw = json.dumps(audit).encode()
        audit_path = "experiments/dependency_memory/results/transfer_transport_audit.json"
        plan["source_sha256"][audit_path] = hashlib.sha256(raw).hexdigest()
        args = SimpleNamespace(executable=Path("never-started.exe"), authorization="bounded continuation")
        with patch("continue_transfer_study.make_launch_plan", return_value=plan), \
             patch("continue_transfer_study.runner.source_commit", return_value="0" * 40), \
             patch.object(Path, "read_bytes", return_value=raw), \
             patch("continue_transfer_study.LunaClient") as client_factory, \
             patch("continue_transfer_study.AppServer") as server_factory:
            with self.assertRaises(ValueError):
                prepare_clients(args, plan)
        client_factory.assert_not_called()
        server_factory.assert_not_called()

    def test_live_execute_defensively_rejects_wrong_wire_contract_before_dispatch(self):
        plan = fixture()
        clients = []
        for worker, certificate in enumerate(plan["certificate"]["workers"]):
            client = LunaClient.__new__(LunaClient)
            client.audit = {"launch_ready": True, "public_request_contract": "different_request_contract"}
            client.budget = ContinuationCreditBudget(certificate)
            client.quota_used_limit = 100
            client.credit_backed_quota = True
            client.metadata = {"worker": worker, "source_commit": "0" * 40,
                "fingerprinted_sources_match_commit": True,
                "approved_continuation_sha256": _hash(plan),
                "quota_guard_used_percent": 100, "credit_backed_quota": True,
                "quota_policy": "included_or_existing_credits"}
            clients.append(client)
        with tempfile.TemporaryDirectory() as tmp, \
             patch("continue_transfer_study.make_launch_plan", return_value=plan), \
             patch.object(LunaClient, "complete") as complete, \
             patch("continue_transfer_study.AppServer") as server_factory:
            with self.assertRaises(ValueError):
                execute(plan, clients, output=tmp, authorization="bounded continuation", fake=False)
            self.assertEqual(list(Path(tmp).iterdir()), [])
        complete.assert_not_called()
        server_factory.assert_not_called()

    def test_every_manifest_and_initial_ledger_exists_before_first_decision(self):
        plan = fixture()
        with tempfile.TemporaryDirectory() as tmp:
            directory = Path(tmp)
            class CheckingClient(FakeClient):
                def complete(self, request):
                    if not (directory / "manifest.json").is_file():
                        raise AssertionError("Missing aggregate manifest before decision")
                    for worker in range(4):
                        own = directory / f"worker-{worker}"
                        for name in ("manifest.json", "requests.json", "summary.json"):
                            if not (own / name).is_file():
                                raise AssertionError("Missing worker evidence before decision")
                        manifest = json.loads((own / "manifest.json").read_text())
                        expected = plan["certificate"]["workers"][worker]["eligible_case_ids"]
                        if [case["case_id"] for case in manifest["cases"]] != expected:
                            raise AssertionError("Manifest includes an ineligible or reordered case")
                    return super().complete(request)
            result = execute(plan, [CheckingClient("optimal") for _ in range(4)], output=tmp, fake=True)
        self.assertEqual(result["attempt_status_counts"]["completed"], 8)
        self.assertFalse(result["shared_stop"])

    def test_residual_budget_does_not_renew_original_worker_allocation(self):
        row = fixture()["certificate"]["workers"][0]
        budget = ContinuationCreditBudget(row)
        self.assertEqual((budget.cap, budget.max_attempts), (Decimal(11), 2))
        usage = {"inputTokens": 1000, "cachedInputTokens": 0, "outputTokens": 10, "reasoningOutputTokens": 0}
        for _ in range(2):
            budget.settle(budget.reserve(), usage)
        with self.assertRaises(BudgetExceeded):
            budget.reserve()
        row["remaining_credit_equivalent_cap_exact"] = "10"
        with self.assertRaises(BudgetExceeded):
            ContinuationCreditBudget(row).reserve()

    def test_uncertain_attempt_retains_residual_reservation(self):
        budget = ContinuationCreditBudget(fixture()["certificate"]["workers"][0])
        budget.fail(budget.reserve())
        self.assertEqual(budget.committed, Decimal("10.4025"))
        with self.assertRaises(BudgetStopped):
            budget.reserve()

    def test_exact_case_filtering_and_global_original_order(self):
        plan = fixture()
        clients = [FakeClient("optimal") for _ in range(4)]
        with tempfile.TemporaryDirectory() as tmp:
            summary = execute(plan, clients, output=tmp, fake=True)
            expected = {cid for worker in plan["certificate"]["workers"] for cid in worker["eligible_case_ids"]}
            self.assertEqual([r["case_id"] for r in summary["rows"]],
                [c["case_id"] for c in plan["original_plan"]["cases"] if c["case_id"] in expected])
            self.assertEqual(summary["attempt_status_counts"]["completed"], 8)
            self.assertTrue(all(row["grade"]["optimal_parent"] for row in summary["rows"]))
            self.assertEqual(summary["model_requests"], 0)
            for worker in range(4):
                ledger = json.loads((Path(tmp) / f"worker-{worker}/requests.json").read_text())
                self.assertEqual([a["case_id"] for a in ledger], plan["certificate"]["workers"][worker]["eligible_case_ids"])
            with self.assertRaises(ValueError):
                execute(plan, [FakeClient() for _ in range(4)], output=tmp, fake=True)

    def test_policy_failures_remain_without_replacement(self):
        with tempfile.TemporaryDirectory() as tmp:
            summary = execute(fixture(), [FakeClient("invalid") for _ in range(4)], output=tmp, fake=True)
        self.assertEqual(summary["attempt_status_counts"]["policy_failure"], 8)
        self.assertEqual(summary["request_attempts"], 8)
        self.assertFalse(summary["shared_stop"])

    def test_wrong_worker_certificate_is_rejected(self):
        plan = deepcopy(fixture())
        plan["certificate"]["workers"][0]["eligible_case_ids"][0] = plan["certificate"]["workers"][1]["eligible_case_ids"][0]
        with self.assertRaises(ValueError):
            eligible_cases(plan, 0)


if __name__ == "__main__":
    unittest.main()
