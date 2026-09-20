"""Offline scheduling, concurrency, persistence, and budget regressions."""
from copy import deepcopy
from decimal import Decimal
import json
import hashlib
from pathlib import Path
import tempfile
import threading
from types import SimpleNamespace
import unittest
from unittest.mock import patch

from luna_appserver import ResponseFormatError, TransportError
from luna_budget import BudgetExceeded, BudgetStopped, CreditBudget
from luna_isolation import turn_parameters, wire_body_byte_bound
from request_contracts import request_bytes as dispatch_bytes
from run_transfer_study import (DispatchGate, StudyStopped, TransferCreditBudget,
                                execute, prepare_clients, source_commit, validate_plan)
from test_luna_appserver import FakeServer, make_client, successful_events
from transfer_interface import request_bytes
from transfer_study import FakeClient, make_plan


class TransferBudgetTests(unittest.TestCase):
    def test_new_allocation_does_not_expand_old_default_or_old_explicit_cap(self):
        self.assertEqual(CreditBudget().max_attempts, 96)
        with self.assertRaises(ValueError):
            CreditBudget(max_attempts=97)
        worker = TransferCreditBudget()
        self.assertEqual((worker.cap, worker.max_attempts), (Decimal(50), 384))
        usage = {"inputTokens": 1000, "cachedInputTokens": 0,
                 "outputTokens": 10, "reasoningOutputTokens": 0}
        for _ in range(384):
            worker.settle(worker.reserve(), usage)
        with self.assertRaises(BudgetExceeded):
            worker.reserve()
        self.assertEqual(worker.settled_attempts, 384)
        for cap in (385, -1, True, 1.0):
            with self.assertRaises(ValueError):
                TransferCreditBudget(cap)

    def test_uncertainty_stops_one_worker_without_spending_another_budget(self):
        workers = [TransferCreditBudget() for _ in range(4)]
        workers[0].fail(workers[0].reserve(), "generation_failure")
        with self.assertRaises(BudgetStopped):
            workers[0].reserve()
        self.assertEqual(workers[0].committed, Decimal("10.4025"))
        self.assertEqual([w.committed for w in workers[1:]], [Decimal(0)] * 3)

    def test_commit_attestation_rejects_uncommitted_or_changed_fingerprinted_sources(self):
        source = b"fixed source\n"
        plan = {"source_sha256": {"source.py": hashlib.sha256(source).hexdigest()}}
        commit = "a" * 40

        def result(data, code=0):
            return SimpleNamespace(returncode=code, stdout=data, stderr=b"")

        with patch("run_transfer_study.subprocess.run", side_effect=[result(commit.encode()), result(source)]):
            self.assertEqual(source_commit(plan), commit)
        for blob in (result(b"changed source\n"), result(b"", code=128)):
            with patch("run_transfer_study.subprocess.run", side_effect=[result(commit.encode()), blob]):
                with self.assertRaises(ValueError):
                    source_commit(plan)


class TransferGateTests(unittest.TestCase):
    def test_stop_blocks_luna_after_preflight_before_generation_reservation(self):
        gate, client = DispatchGate(), make_client()
        client.dispatch_gate = gate
        server = FakeServer()
        server.client = client
        original_rpc = server.rpc

        def rpc(method, params):
            result = original_rpc(method, params)
            if method == "thread/start":
                gate.stop()  # Another worker failed while this one was preparing.
            return result

        server.rpc = rpc
        request = make_plan()["cases"][0]["request"]
        with patch("luna_appserver.AppServer", return_value=server):
            with self.assertRaises(StudyStopped):
                client.complete(request)
        self.assertEqual(client.budget.attempts, 0)
        self.assertFalse(any(method == "turn/start" for method, _ in server.calls))
        self.assertTrue(server.closed)

    def test_dispatch_rpc_failure_closes_gate_before_cleanup(self):
        gate, client = DispatchGate(), make_client()
        client.dispatch_gate = gate
        server = FakeServer()
        server.client = client
        original_rpc, original_close = server.rpc, server.close

        def rpc(method, params):
            if method == "turn/start":
                raise TransportError("synthetic_dispatch_failure")
            return original_rpc(method, params)

        def close():
            self.assertTrue(gate.event.is_set())
            original_close()

        server.rpc, server.close = rpc, close
        with patch("luna_appserver.AppServer", return_value=server):
            with self.assertRaises(TransportError):
                client.complete(make_plan()["cases"][0]["request"])
        self.assertEqual(client.budget.failed_attempts, 1)
        with self.assertRaises(StudyStopped):
            with gate:
                self.fail("A stopped gate admitted a new generation")

    def test_completed_malformed_response_does_not_stop_other_workers(self):
        gate, client = DispatchGate(), make_client()
        client.dispatch_gate = gate
        events = successful_events()
        events[0]["params"]["item"]["text"] = "{"
        server = FakeServer(events=events)
        server.client = client
        with patch("luna_appserver.AppServer", return_value=server):
            with self.assertRaises(ResponseFormatError):
                client.complete(make_plan()["cases"][0]["request"])
        self.assertFalse(gate.event.is_set())
        self.assertFalse(client.stopped)
        self.assertEqual(client.budget.settled_attempts, 1)


class TransferRunnerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.plan = make_plan()

    def setUp(self):
        self.plan_patch = patch("run_transfer_study.study.make_plan", return_value=deepcopy(self.plan))
        self.plan_patch.start()
        self.addCleanup(self.plan_patch.stop)

    def test_complete_optimal_control_preserves_all_blocks_and_denominators(self):
        summary = execute([FakeClient() for _ in range(4)])
        self.assertEqual(summary["request_attempts"], 1536)
        self.assertEqual(summary["model_requests"], 0)
        self.assertFalse(summary["shared_stop"])
        self.assertEqual(summary["attempt_status_counts"]["completed"], 1536)
        self.assertEqual(summary["primary"]["valid_pairs"], 128)
        self.assertTrue(all(row["grade"]["optimal_parent"] for row in summary["rows"]))
        for worker in summary["worker_summaries"]:
            self.assertEqual(worker["request_attempts"], 384)
            blocks = list(dict.fromkeys(row["block"] for row in worker["rows"]))
            self.assertEqual(blocks, list(range(worker["worker"], 32, 4)))

    def test_invalid_policy_continues_and_empty_or_partial_caps_keep_1536_rows(self):
        for cap in (0, 2):
            summary = execute([FakeClient("invalid") for _ in range(4)], limit_per_worker=cap)
            self.assertEqual(summary["request_attempts"], 4 * cap)
            self.assertEqual(summary["attempt_status_counts"]["policy_failure"], 4 * cap)
            self.assertEqual(len(summary["rows"]), 1536)
            self.assertEqual(sum(row["status"] == "incomplete" for row in summary["rows"]), 1536 - 4 * cap)
            self.assertFalse(summary["shared_stop"])
            self.assertTrue(all(row["grade"] is None for row in summary["rows"]))

    def test_inflight_workers_finish_but_shared_failure_prevents_their_next_request(self):
        barrier = threading.Barrier(4)
        failed = threading.Event()

        class CoordinatedClient(FakeClient):
            def __init__(self, worker):
                super().__init__()
                self.worker, self.calls = worker, 0

            def complete(self, request):
                self.calls += 1
                barrier.wait(timeout=5)
                if self.worker == 0:
                    self.dispatch_gate.stop()
                    failed.set()
                    raise TransportError("synthetic_uncertain_generation")
                if not failed.wait(timeout=5):
                    raise AssertionError("Failure did not propagate")
                return super().complete(request)

        clients = [CoordinatedClient(i) for i in range(4)]
        summary = execute(clients)
        self.assertEqual([c.calls for c in clients], [1] * 4)
        self.assertTrue(summary["shared_stop"])
        self.assertEqual(summary["attempt_status_counts"]["transport_failure"], 1)
        self.assertEqual(summary["attempt_status_counts"]["completed"], 3)
        self.assertEqual(sum(r["status"] == "incomplete" for r in summary["rows"]), 1532)

    def test_all_manifests_and_request_reservation_exist_before_any_call(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "study"

            class InspectingClient(FakeClient):
                def __init__(self, worker):
                    super().__init__()
                    self.worker = worker

                def complete(self, request):
                    manifest = json.loads((output / "manifest.json").read_text())
                    if len(manifest["plan"]["cases"]) != 1536:
                        raise AssertionError("Incomplete aggregate manifest before dispatch")
                    for worker in range(4):
                        if not (output / f"worker-{worker}" / "manifest.json").is_file():
                            raise AssertionError("A worker dispatched before all manifests existed")
                    ledger = json.loads((output / f"worker-{self.worker}" / "requests.json").read_text())
                    if len(ledger) != 1 or ledger[0]["status"] != "reserved":
                        raise AssertionError("Attempt was not persisted before dispatch")
                    if ledger[0]["request_utf8"].encode() != request_bytes(request):
                        raise AssertionError("Persisted request differs from dispatched input")
                    return super().complete(request)

            summary = execute([InspectingClient(i) for i in range(4)], output=output, limit_per_worker=1)
            self.assertEqual(summary["attempt_status_counts"]["completed"], 4)
            self.assertEqual(json.loads((output / "summary.json").read_text()), summary)
            for worker in range(4):
                saved = json.loads((output / f"worker-{worker}" / "summary.json").read_text())
                self.assertEqual(len(saved["rows"]), 384)
            with self.assertRaises(ValueError):
                execute([FakeClient() for _ in range(4)], output=output)

    def test_reused_client_invalid_limit_and_fake_live_are_rejected(self):
        client = FakeClient()
        with self.assertRaises(ValueError):
            execute([client] * 4)
        for cap in (-1, 385, True, 2.0):
            with self.assertRaises(ValueError):
                execute([FakeClient() for _ in range(4)], limit_per_worker=cap)
        with self.assertRaises(ValueError):
            execute([FakeClient() for _ in range(4)], fake=False, authorization="synthetic only")

    def test_plan_rejects_split_blocks_and_changed_request_before_any_worker(self):
        plan = deepcopy(self.plan)
        a, b = 0, next(i for i, row in enumerate(plan["cases"]) if row["block"] == 4)
        plan["cases"][a], plan["cases"][b] = plan["cases"][b], plan["cases"][a]
        with self.assertRaises(ValueError):
            validate_plan(plan)
        plan = deepcopy(self.plan)
        plan["cases"][0]["request_sha256"] = "0" * 64
        with self.assertRaises(ValueError):
            validate_plan(plan)

    def test_stale_frozen_plan_rejects_before_client_or_process_creation(self):
        frozen = deepcopy(self.plan)
        frozen["protocol_and_wire_audit_present"] = True
        frozen["allocation"] = "A different frozen allocation"
        args = SimpleNamespace(executable=Path("never-run.exe"), authorization="synthetic only")
        with patch.object(Path, "read_text", return_value=json.dumps(frozen)), \
                patch("run_transfer_study.LunaClient") as client, \
                patch("run_transfer_study.AppServer") as server:
            with self.assertRaises(ValueError):
                prepare_clients(args)
            client.assert_not_called()
            server.assert_not_called()

    def test_third_contract_serializes_without_expanding_wire_or_tool_access(self):
        for case in self.plan["cases"][:48]:
            request = case["request"]
            self.assertEqual(dispatch_bytes(request), request_bytes(request))
            turn = turn_parameters("new-thread", request)
            self.assertEqual(turn["input"][0]["text"], request_bytes(request).decode())
            self.assertEqual(turn["environments"], [])
            self.assertEqual(turn["runtimeWorkspaceRoots"], [])
            self.assertLessEqual(wire_body_byte_bound(request), 32768)


if __name__ == "__main__":
    unittest.main()
