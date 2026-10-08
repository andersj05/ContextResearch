"""Dispatch/crash, cohort-flow and matched-request engineering tests."""
from decimal import Decimal
from pathlib import Path
import tempfile
import threading
import unittest

from .accounting import AccountingError, Identity, Ledger, PER_CALL, Usage
from .contexts import ByteCounter, Renderer
from .controller import Controller
from .fixtures import math_example
from .records import wire, strict_loads
from .schedule import task_slots, terminal_order, writer_order
from .transport import FakeTransport, Response, UnknownDispatch


def workspace_temp():
    root = Path(__file__).resolve().parents[3] / "tmp" / "rollback_tests"
    root.mkdir(parents=True, exist_ok=True)
    return tempfile.TemporaryDirectory(dir=root)


def fixture_script(overrides=None):
    task, evaluator, checkpoint, branch, receipt, lesson, summary = math_example()
    defaults = {"checkpoint": checkpoint.json_text, "branch": branch.json_text,
                "lesson": lesson.json_text, "summary": summary.json_text, "terminal": '{"values":[6,4]}'}
    overrides = overrides or {}
    def script(identity, request):
        key = (identity.stage, identity.arm, identity.draw, identity.slot)
        result = overrides.get(key, overrides.get(identity.stage, defaults[identity.stage]))
        if identity.stage == "lesson" and key not in overrides and "lesson" not in overrides:
            data = strict_loads(result)
            context = strict_loads(request.data()["messages"][1]["content"])
            data["evidence_ids"] = [context["feedback"]["receipt_id"]]
            result = wire(data)
        return result(identity, request) if callable(result) else result
    return script


class LedgerTests(unittest.TestCase):
    def test_exact_reserve_and_exclusive_buckets_without_reasoning_double_charge(self):
        self.assertEqual(PER_CALL, Decimal("0.012288"))
        self.assertEqual(PER_CALL * 320, Decimal("3.932160"))
        usage = Usage(600, 100, 200, 300, 400, 250)
        self.assertEqual(usage.cost, Decimal("0.0002495"))
        for bad in (Usage(600, 600, 200, 300, 400, 250), Usage(0, 0, 0, 0, 3, 4),
                    Usage(0, 0, 0, 0, -1, 0), Usage(True, 1, 0, 0, 0, 0), Usage(0, 0, 0, 0, 16385, 0)):
            with self.assertRaises(AccountingError):
                bad.validate()

    def test_prior_reservation_hash_binding_and_immutable_dispatch_identity(self):
        with workspace_temp() as tmp:
            ledger = Ledger(Path(tmp) / "ledger.sqlite")
            identity = Identity("E0", "task", "checkpoint")
            with self.assertRaises(AccountingError):
                ledger.dispatch(identity, "hash")
            ledger.plan(identity, "hash")
            ledger.reserve(identity)
            with self.assertRaises(AccountingError):
                ledger.dispatch(identity, "different")
            ledger.dispatch(identity, "hash")
            ledger.complete(identity, Usage(1, 1, 0, 0, 1, 0), "known")
            self.assertEqual([x["state"] for x in ledger.events()], ["planned", "reserved", "dispatched", "completed"])
            with self.assertRaises(AccountingError):
                ledger.plan(identity, "hash")
            with self.assertRaises(AccountingError):
                ledger.dispatch(identity, "hash")
            ledger.close()

    def test_possible_dispatch_survives_crash_and_blocks_replay_and_new_calls(self):
        with workspace_temp() as tmp:
            path = Path(tmp) / "ledger.sqlite"
            identity = Identity("E0", "task", "checkpoint")
            ledger = Ledger(path)
            ledger.plan(identity, "hash")
            ledger.reserve(identity)
            ledger.dispatch(identity, "hash")
            ledger.close()  # Crash before any saved response/reconciliation.
            recovered = Ledger(path)
            self.assertEqual(recovered.summary()["locked_reserve_usd"], "0.012288")
            with self.assertRaises(AccountingError):
                recovered.plan(identity, "hash")
            other = Identity("E0", "task2", "checkpoint")
            recovered.plan(other, "hash2")
            with self.assertRaises(AccountingError):
                recovered.reserve(other)
            self.assertEqual(recovered.rows()[identity.key]["state"], "dispatched")
            recovered.close()

    def test_budget_and_call_ceiling_release_only_verified_unused_reserve(self):
        with workspace_temp() as tmp:
            ledger = Ledger(Path(tmp) / "ledger.sqlite", ceiling="0.02", max_calls=2)
            for slot in (1, 2):
                identity = Identity("E0", "task", "branch", slot=slot)
                ledger.plan(identity, str(slot))
                ledger.reserve(identity)
                ledger.dispatch(identity, str(slot))
                ledger.complete(identity, Usage(10, 10, 0, 0, 10, 0), "known")
            third = Identity("E0", "task3", "checkpoint")
            ledger.plan(third, "third")
            with self.assertRaises(AccountingError):
                ledger.reserve(third)
            self.assertLess(Decimal(ledger.summary()["liability_usd"]), Decimal("0.02"))
            ledger.close()
            with self.assertRaises(AccountingError):
                Ledger(Path(tmp) / "ledger.sqlite", ceiling="5.00", max_calls=320)

    def test_reserved_call_blocks_second_worker_transactionally(self):
        with workspace_temp() as tmp:
            path = Path(tmp) / "ledger.sqlite"
            ledger = Ledger(path)
            identities = [Identity("E0", "task", "branch", slot=i) for i in (1, 2)]
            for i in identities:
                ledger.plan(i, i.key)
            barrier, results = threading.Barrier(2), []
            def worker(identity):
                connection = Ledger(path)
                barrier.wait()
                try:
                    connection.reserve(identity)
                    results.append("reserved")
                except AccountingError:
                    results.append("blocked")
                finally:
                    connection.close()
            threads = [threading.Thread(target=worker, args=(i,)) for i in identities]
            for t in threads:
                t.start()
            for t in threads:
                t.join(timeout=10)
            self.assertEqual(sorted(results), ["blocked", "reserved"])
            ledger.close()


class ControllerTests(unittest.TestCase):
    def run_case(self, overrides=None, renderer=None, max_calls=320):
        temp = workspace_temp()
        self.addCleanup(temp.cleanup)
        task, evaluator, *_ = math_example()
        transport = FakeTransport(fixture_script(overrides))
        controller = Controller(Path(temp.name) / "run", "engineering-E0", transport, renderer=renderer, max_calls=max_calls)
        self.addCleanup(controller.ledger.close)
        rows = controller.run([(task, evaluator)])
        return controller, transport, rows[0]

    def test_full_episode_retains_identical_primary_fields_and_no_cross_draw_input(self):
        controller, transport, row = self.run_case()
        self.assertEqual(len(transport.calls), 12)
        self.assertEqual(row["grades"], {arm: [1, 1] for arm in ("K", "R", "Z", "G")})
        self.assertTrue(row["primary_scheduled"])
        self.assertEqual(row["context_hashes"]["K"]["shared"], row["context_hashes"]["R"]["shared"])
        terminal = [event for event in controller.ledger.rows().values() if event["identity"]["stage"] == "terminal"]
        self.assertEqual([(e["identity"]["arm"], e["identity"]["draw"]) for e in terminal], terminal_order(0))
        for arm in ("K", "R", "Z", "G"):
            hashes = [e["request_hash"] for e in terminal if e["identity"]["arm"] == arm]
            self.assertEqual(hashes[0], hashes[1])
        self.assertFalse(controller.ledger.summary()["blocked"])

    def test_immediate_success_is_not_replaced_or_forced_into_a_failed_branch(self):
        branch = math_example()[3].data()
        branch["artifact"] = {"values": [6, 4]}
        _, transport, row = self.run_case({"branch": wire(branch)})
        self.assertEqual(len(transport.calls), 2)
        self.assertEqual(row["flow"], ["public_pass"])
        self.assertFalse(row["primary_scheduled"])
        self.assertEqual(row["initial_grade"]["score"], 1)

    def test_valid_continue_consumes_slot_but_malformed_branch_never_gets_format_retry(self):
        branch = math_example()[3].data()
        branch.update(status="continue", artifact=None)
        _, transport, row = self.run_case({("branch", None, None, 1): wire(branch)})
        self.assertEqual(len(transport.calls), 13)
        self.assertEqual(row["branch_count"], 2)
        _, transport, row = self.run_case({"branch": '{"values":[5,5]}'})
        self.assertEqual(len(transport.calls), 2)
        self.assertTrue(row["flow"][0].startswith("malformed_branch"))
        self.assertFalse(row["public_failure"])

    def test_two_no_candidate_branches_remain_in_full_cohort(self):
        branch = math_example()[3].data()
        branch.update(status="continue", artifact=None)
        _, transport, row = self.run_case({"branch": wire(branch)})
        self.assertEqual(len(transport.calls), 3)
        self.assertEqual(row["flow"], ["no_candidate", "no_candidate"])
        self.assertEqual(row["scheduled_arms"], [])

    def test_unusable_summary_blocks_G_only_and_lesson_blocks_only_K_R(self):
        _, transport, row = self.run_case({"summary": '{"extra":"malformed"}'})
        self.assertEqual(len(transport.calls), 10)
        self.assertTrue(row["primary_scheduled"])
        self.assertEqual(row["scheduled_arms"], ["K", "R", "Z"])
        self.assertEqual(row["grades"]["K"], [1, 1])
        _, transport, row = self.run_case({"lesson": '{"extra":"malformed"}'})
        self.assertEqual(len(transport.calls), 8)
        self.assertFalse(row["primary_scheduled"])
        self.assertEqual(row["scheduled_arms"], ["Z", "G"])

    def test_oversize_writer_is_preserved_and_never_truncated_into_validity(self):
        controller, _, row = self.run_case({"summary": wire({"summary": "x" * 1200})})
        self.assertFalse(row["summary_usable"])
        self.assertTrue(row["primary_scheduled"])
        artifacts = list((controller.folder / "responses").glob("*.json"))
        self.assertTrue(any("x" * 1200 in x.read_text() for x in artifacts))

    def test_K_capacity_failure_blocks_R_before_either_dispatch(self):
        class FixtureCounter(ByteCounter):
            counter_id = "synthetic_K_capacity_overflow_fixture"
            def request(self, text):
                data = strict_loads(strict_loads(text)["messages"][1]["content"])
                return 32769 if data["trial"] is not None and data["lesson"] is not None else super().request(text)
        controller, _, row = self.run_case(renderer=Renderer(counter=FixtureCounter()))
        self.assertTrue(row["capacity_infeasible"])
        self.assertFalse(row["primary_scheduled"])
        self.assertEqual(row["scheduled_arms"], ["Z", "G"])
        self.assertFalse(any(event["identity"]["arm"] in {"K", "R"} for event in controller.ledger.rows().values()))

    def test_known_capped_and_malformed_terminal_outputs_score_zero_with_metered_cost(self):
        def capped(identity, request):
            return Response("", Usage(request.input_units, request.input_units, 0, 0, 50, 50), capped=True)
        controller, _, row = self.run_case({("terminal", "K", 1, 1): capped, ("terminal", "R", 1, 1): '{"values":[true,4]}'})
        self.assertEqual(row["grades"]["K"], [0, 1])
        self.assertEqual(row["grades"]["R"], [0, 1])
        self.assertFalse(controller.ledger.summary()["blocked"])
        self.assertEqual(controller.ledger.summary()["admitted_calls"], 12)

    def test_unknown_terminal_stops_launch_and_preserves_never_dispatched_slots_as_unknown(self):
        controller, transport, row = self.run_case({("terminal", "R", 1, 1): UnknownDispatch("simulated network loss")})
        self.assertEqual(len(transport.calls), 6)  # checkpoint, branch, two writers, K1, R1
        self.assertEqual(row["grades"]["K"], [1, None])
        self.assertEqual(row["grades"]["R"], [None, None])
        self.assertTrue(row["primary_scheduled"])
        self.assertEqual(controller.ledger.summary()["locked_reserve_usd"], "0.012288")
        self.assertTrue(controller.dispatcher.stopped)

    def test_missing_usage_preserves_response_and_locked_liability(self):
        controller, _, row = self.run_case({"summary": Response('{"summary":"raw response preserved"}', None)})
        self.assertTrue(row["primary_scheduled"])
        self.assertTrue(controller.ledger.summary()["blocked"])
        self.assertEqual(row["grades"]["K"], [None, None])
        self.assertTrue(any("raw response preserved" in p.read_text() for p in (controller.folder / "responses").glob("*.json")))

    def test_existing_result_directory_and_provider_transport_are_rejected(self):
        with workspace_temp() as tmp:
            with self.assertRaises(FileExistsError):
                Controller(tmp, "E0", FakeTransport(fixture_script()))
            with self.assertRaises(ValueError):
                Controller(Path(tmp) / "forbidden", "E0", object())

    def test_writer_rotation_and_draw_reversal_keep_stable_unfilled_identities(self):
        task = math_example()[0]
        self.assertEqual(writer_order(0), ("lesson", "summary"))
        self.assertEqual(writer_order(1), ("summary", "lesson"))
        for index in range(12):
            slots = task_slots("E0", task, index)
            self.assertEqual(len(slots), 13)
            self.assertEqual(len({slot.key for slot in slots}), 13)
            order = terminal_order(index)
            self.assertEqual([a for a, d in order[:4]], list(reversed([a for a, d in order[4:]])))
            self.assertEqual(sorted(order), sorted((a, d) for a in ("K", "R", "Z", "G") for d in (1, 2)))
