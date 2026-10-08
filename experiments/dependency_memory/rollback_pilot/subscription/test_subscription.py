"""Scientific access, durable accounting and failure semantics for subscription E1."""
from decimal import Decimal
from pathlib import Path
import unittest
from unittest.mock import patch

from ..accounting import AccountingError, Identity
from ..fixtures import math_example, code_example
from ..prepare import calibration_requests
from ..records import ActorTask, EvaluatorTask, Record, InterfaceError, strict_loads, wire
from ..test_controller import workspace_temp
from ..transport import UnknownDispatch
from .accounting import Ledger, Usage, RESERVATION
from .calibration import freeze, check_frozen, inspect_answer
from . import calibration as calibration_module
from .dispatcher import Dispatcher
from .profile import Renderer, source_ids, output_schema, body_bound, MAX_BODY_BYTES
from .process import ProtocolError
from .transport import Response, collect, check_quota


class SubscriptionTests(unittest.TestCase):
    def test_exclusive_cached_and_reasoning_buckets(self):
        value = Usage(1000, 400, 200, 150)
        self.assertEqual(value.cost, Decimal(".0041"))
        self.assertEqual(Usage(1050000, 0, 128000, 128000).cost, RESERVATION)

    def test_invalid_metering_cannot_settle(self):
        for value in (Usage(True, 0, 1, 0), Usage(0, 0, 1, 0), Usage(1, 2, 1, 0),
                      Usage(1, 0, 1, 2), Usage(1050001, 0, 1, 0), Usage(1, 0, 128001, 0)):
            with self.subTest(value=value), self.assertRaises(AccountingError):
                value.validate()
        with self.assertRaises(AccountingError):
            Usage.from_telemetry({"inputTokens": 1, "cachedInputTokens": 0, "outputTokens": 2,
                                  "reasoningOutputTokens": 1, "totalTokens": 4})

    def test_crash_reservation_survives_reopening_and_blocks_admissions(self):
        with workspace_temp() as tmp:
            path = Path(tmp) / "ledger.sqlite"
            one, two = Identity("new", "task1", "checkpoint"), Identity("new", "task2", "checkpoint")
            ledger = Ledger(path)
            ledger.plan(one, "a")
            ledger.reserve(one)
            ledger.close()
            ledger = Ledger(path)
            self.assertEqual(Decimal(ledger.summary()["locked_reserve_credits"]), RESERVATION)
            ledger.plan(two, "b")
            with self.assertRaises(AccountingError):
                ledger.reserve(two)
            ledger.close()

    def test_unknown_dispatch_keeps_reserve_and_never_replays(self):
        with workspace_temp() as tmp:
            ledger = Ledger(Path(tmp) / "ledger.sqlite")
            identity = Identity("new", "task", "checkpoint")
            ledger.plan(identity, "a")
            ledger.reserve(identity)
            ledger.dispatch(identity, "a")
            ledger.unknown(identity, "fixture_error")
            self.assertTrue(ledger.summary()["blocked"])
            with self.assertRaises(AccountingError):
                ledger.plan(identity, "a")
            ledger.close()

    def test_actual_telemetry_settles_without_API_conversion(self):
        with workspace_temp() as tmp:
            ledger = Ledger(Path(tmp) / "ledger.sqlite", ceiling="4.225", max_calls=1)
            identity = Identity("new", "task", "checkpoint")
            ledger.plan(identity, "a")
            ledger.reserve(identity)
            ledger.dispatch(identity, "a")
            ledger.complete(identity, Usage(1000, 400, 200, 150), "known_wrong")
            summary = ledger.summary()
            self.assertFalse(summary["blocked"])
            self.assertEqual(summary["completed_credits"], "0.0041")
            self.assertNotIn("completed_cost_usd", summary)
            ledger.close()

    def test_existing_allocation_configuration_cannot_increase(self):
        with workspace_temp() as tmp:
            path = Path(tmp) / "ledger.sqlite"
            Ledger(path, ceiling="20", max_calls=8).close()
            with self.assertRaises(AccountingError):
                Ledger(path, ceiling="21", max_calls=8)

    def test_credit_ceiling_rejects_the_next_whole_reservation(self):
        with workspace_temp() as tmp:
            ledger = Ledger(Path(tmp) / "ledger.sqlite", ceiling="4.224")
            identity = Identity("new", "task", "checkpoint")
            ledger.plan(identity, "a")
            with self.assertRaises(AccountingError):
                ledger.reserve(identity)
            self.assertEqual(ledger.summary()["admitted_calls"], 0)
            ledger.close()

    def test_shared_primary_context_and_deleted_branch_routing(self):
        task, _, checkpoint, branch, feedback, lesson, summary = math_example()
        renderer = Renderer()
        keep = renderer.continuation("K", task, checkpoint, [branch], feedback, lesson, summary)
        rollback = renderer.continuation("R", task, checkpoint, [branch], feedback, lesson, summary)
        left = strict_loads(keep.data()["messages"][1]["content"])
        right = strict_loads(rollback.data()["messages"][1]["content"])
        self.assertEqual({k: v for k, v in left.items() if k != "trial"}, {k: v for k, v in right.items() if k != "trial"})
        self.assertEqual(keep.data()["messages"][0], rollback.data()["messages"][0])
        self.assertIn("ROUTING_MARKER_7Q9", keep.json_text)
        self.assertNotIn("ROUTING_MARKER_7Q9", rollback.json_text)
        self.assertIsNone(right["trial"])

    def test_renderer_rejects_forged_private_record_fields(self):
        task, _, checkpoint, *_ = math_example()
        forged = Record("checkpoint", wire({**checkpoint.data(), "private_witness": [6, 4]}))
        with self.assertRaises(InterfaceError):
            Renderer().render("branch", task, forged)

    def test_evaluator_cannot_cross_actor_render_boundary(self):
        _, evaluator, *_ = math_example()
        with self.assertRaises(InterfaceError):
            Renderer().render("checkpoint", evaluator)

    def test_only_supplied_lists_have_source_aliases(self):
        task, *_ = math_example()
        self.assertFalse(any(x.startswith("list") for x in source_ids(task)))
        request = Renderer().render("checkpoint", task)
        self.assertNotIn('"list1"', request.data()["messages"][0]["content"])

    def test_body_bound_counts_escaping_and_duplicated_schema(self):
        task, *_ = code_example()
        data = task.data()
        data["statement"] = '\\"\n' * 4000
        changed = ActorTask.from_dict(task.task_id, task.stratum, data)
        request = Renderer().render("checkpoint", changed)
        self.assertGreater(body_bound(request), len(request.json_text.encode()))
        self.assertFalse(Renderer().fits(request))
        self.assertEqual(body_bound(request), request.input_units)

    def test_calibration_fixtures_are_excluded_and_private_fields_unsent(self):
        rows = calibration_requests(Renderer())
        self.assertEqual(len(rows), 8)
        for row in rows:
            self.assertTrue(row["excluded_from_all_model_study_cohorts"])
            self.assertNotIn("reserved1", wire(row["request"]))
            self.assertNotIn("max_output_tokens_including_reasoning", row["request"]["settings"])
        self.assertNotIn("CODE_BRANCH_ONLY_CANARY", wire(rows[7]["request"]))

    def test_known_malformed_text_is_a_format_failure(self):
        rows = calibration_requests(Renderer())
        result = inspect_answer(rows[0], "invalid JSON", None)
        self.assertFalse(result["format_valid"])
        valid = inspect_answer(rows[6], '{"values":[6,4]}', None)
        self.assertTrue(valid["format_valid"])
        self.assertEqual(valid["grade"]["score"], 1)

    def test_writer_limit_is_explicitly_bytes_without_repair(self):
        row = calibration_requests(Renderer())[5]
        result = inspect_answer(row, wire({"summary": "x" * 1025}), None)
        self.assertFalse(result["format_valid"])
        self.assertEqual(result["disposition"], "writer_visible_byte_cap")

    def test_dispatch_failure_is_durable_and_blocks_the_next_identity(self):
        class Failing:
            def __init__(self):
                self.calls = 0
            def generate(self, *_):
                self.calls += 1
                raise RuntimeError("fixture")
        with workspace_temp() as tmp:
            ledger, transport = Ledger(Path(tmp) / "ledger.sqlite"), Failing()
            dispatcher = Dispatcher(tmp, ledger, transport)
            request = Renderer().render("checkpoint", math_example()[0])
            with self.assertRaises(UnknownDispatch):
                dispatcher.call(Identity("new", "one", "checkpoint"), request)
            with self.assertRaises(UnknownDispatch):
                dispatcher.call(Identity("new", "two", "checkpoint"), request)
            self.assertEqual(transport.calls, 1)
            self.assertTrue(ledger.summary()["blocked"])
            ledger.close()

    def test_response_saved_before_invalid_usage_stops_allocation(self):
        class BadUsage:
            def generate(self, *_):
                return Response("retained-response", Usage(10, 11, 1, 0), {})
        with workspace_temp() as tmp:
            ledger = Ledger(Path(tmp) / "ledger.sqlite")
            dispatcher = Dispatcher(tmp, ledger, BadUsage())
            identity = Identity("new", "one", "checkpoint")
            with self.assertRaises(UnknownDispatch):
                dispatcher.call(identity, Renderer().render("checkpoint", math_example()[0]))
            row = strict_loads((Path(tmp) / "responses" / (identity.key + ".json")).read_text())
            self.assertEqual(row["text"], "retained-response")
            self.assertTrue(ledger.summary()["blocked"])
            ledger.close()

    def test_quota_cannot_silently_switch_to_credits(self):
        row = {"ordinaryUsageAllowed": True, "spendControlReached": False, "rateLimitReachedType": None,
               "individualLimit": None, "primary": {"usedPercent": 99}, "secondary": None}
        check_quota({"codex": row})
        with self.assertRaises(ProtocolError):
            check_quota({"codex": {**row, "primary": {"usedPercent": 100}, "credits": {"hasCredits": True}}})

    def test_frozen_calibration_rejects_tampering_and_E2_authorization(self):
        with workspace_temp() as tmp:
            folder, schemas = Path(tmp) / "bundle", Path(tmp) / "schemas"
            schemas.mkdir()
            (schemas / "fixture.json").write_text("{}")
            preflight = Path(tmp) / "preflight.json"
            preflight.write_text(wire({"serialization_and_retry_audit_passed": True, "real_model_generations": 0}))
            with patch.object(calibration_module, "DockerRunner") as runner:
                runner.return_value.audit.return_value = {"scope": "authored test only"}
                freeze(folder, preflight, image="fixture", schema_folder=schemas)
            manifest, _ = check_frozen(folder)
            manifest["E2_launch_authorized"] = True
            (folder / "manifest.json").write_text(wire(manifest))
            with self.assertRaises(ValueError):
                check_frozen(folder)


if __name__ == "__main__":
    unittest.main()
