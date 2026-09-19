"""End-to-end controls for actual serialized development requests."""

from dataclasses import replace
import json
from pathlib import Path
import tempfile
import unittest

from artifact_workflow import Action, ArtifactEnvironment, Fixture, Receipt
from pilot_interface import FakeClient, inspection_request, validate_inspection_response
from pilot_plan import fixture_assignments
from run_development_pilot import (RequestLedger, RequestStop, development_fixture,
                                   execute, make_manifest, run_model_episode)
from run_recovery_frontier import route_fixtures, scenarios


class DevelopmentPilotTests(unittest.TestCase):
    def test_complete_fake_tranche_and_pairing(self):
        summary, ledger = execute(FakeClient("optimal"))
        self.assertEqual(summary["request_attempts"], 96)
        self.assertEqual(summary["model_requests"], 0)
        self.assertEqual(summary["heldout_requests"], 0)
        self.assertEqual(len(summary["stage_a"]), 12)
        self.assertEqual(len(summary["stage_b"]), 36)
        self.assertTrue(all(row["excess_cost"] == "0" for row in summary["stage_a"]))
        self.assertTrue(all(row["success"] for row in summary["stage_b"]))
        for row in summary["stage_b"]:
            self.assertEqual(row["request_attempts"], 2 + int(row["arm"] == "model_selective"))
            reference = row["fixed_policy_reference"]["inspect" if row["inspection"] else "skip"]
            self.assertEqual(row["synthetic_cost_units"], reference["synthetic_cost_units"])
            self.assertEqual(row["pre_recovery_available"], reference["pre_recovery_available"])
        forbidden = ("cheap_recovery", "costly_recovery", "scenario", "episode_id", "pair_id",
                     "route_index", "payload_root", "reference_cost", "expected_extra_cost")
        for attempt in ledger.rows:
            for label in forbidden:
                self.assertNotIn(label, attempt["request_utf8"])

    def test_fixtures_share_payloads_across_paired_revision_conditions(self):
        assignment = fixture_assignments()[0]
        configs = scenarios()
        plain = development_fixture(configs["costly_recovery"], assignment)
        revised = development_fixture(configs["revision_costly_recovery"], assignment)
        self.assertEqual(plain.receipts, revised.receipts)
        self.assertEqual(plain.candidates, revised.candidates)
        self.assertEqual(plain.target, revised.target)
        self.assertEqual(revised.revision.key, revised.candidates[0])
        self.assertNotIn(revised.revision.token, {r.token for r in plain.receipts})
        with self.assertRaises(ValueError):
            development_fixture(configs["costly_recovery"], fixture_assignments()[1])

    def test_deleted_receipts_do_not_reappear_in_actual_second_requests(self):
        for name in ("costly_recovery", "revision_costly_recovery"):
            config = scenarios()[name]
            fixture = development_fixture(config, fixture_assignments()[0])
            ledger = RequestLedger(FakeClient("forget_all"))
            result = run_model_episode(config, fixture, "always_inspect", "inferred_dependencies", ledger, "test")
            self.assertTrue(result["success"])
            self.assertFalse(result["pre_recovery_available"])
            self.assertTrue(result["recovery_attempted"])
            second = json.loads(ledger.rows[1]["request_utf8"])
            self.assertEqual(len(second["visible_records"]), int(config.revise))
            for receipt in fixture.receipts:
                self.assertNotIn(receipt.token, ledger.rows[1]["request_utf8"])
            if config.revise:
                self.assertIn(fixture.revision.token, ledger.rows[1]["request_utf8"])

    def test_all_manager_requests_invariant_to_final_target(self):
        config = scenarios()["revision_costly_recovery"]
        fixture = development_fixture(config, fixture_assignments()[0])
        requests = []
        for target in fixture.candidates:
            ledger = RequestLedger(FakeClient("optimal"))
            run_model_episode(config, replace(fixture, target=target), "model_selective",
                              "inferred_dependencies", ledger, "test")
            requests.append([row["request_utf8"] for row in ledger.rows])
        self.assertEqual(*requests)

    def test_budget_reservation_and_failed_attempts_do_not_retry(self):
        with tempfile.TemporaryDirectory() as folder:
            summary, ledger = execute(FakeClient("optimal"), cap=13, output=Path(folder) / "run")
            self.assertEqual(len(ledger.rows), 13)
            self.assertEqual(sum(r["status"] == "incomplete" for r in summary["stage_b"]), 36)
            saved = (Path(folder) / "run" / "requests.jsonl").read_text().splitlines()
            self.assertEqual(len(saved), 13)
            with self.assertRaises(ValueError):
                execute(FakeClient("optimal"), output=Path(folder) / "run")
        class BrokenClient:
            calls = 0
            def complete(self, request):
                self.calls += 1
                raise OSError("fixture-independent failure")
        broken = BrokenClient()
        summary, ledger = execute(broken)
        self.assertEqual(broken.calls, 1)
        self.assertEqual(summary["request_attempts"], 1)
        self.assertEqual(ledger.rows[0]["status"], "transport_failure")
        self.assertTrue(all(r["status"] == "incomplete" for r in summary["stage_b"]))

    def test_invalid_policy_records_failures_without_corrective_calls(self):
        summary, ledger = execute(FakeClient("invalid"))
        # Twelve invalid A decisions and one invalid first request per episode.
        self.assertEqual(summary["request_attempts"], 48)
        self.assertTrue(all(r["status"] == "policy_failure" for r in ledger.rows))
        self.assertTrue(all(r["status"] == "policy_failure" for r in summary["stage_b"]))

    def test_failed_attempt_cannot_inherit_previous_usage(self):
        class IntermittentClient:
            last_metadata = {}
            calls = 0
            def complete(self, request):
                self.calls += 1
                if self.calls == 2:
                    raise TimeoutError()
                self.last_metadata = {"request_id": "first-only", "output_tokens": 7}
                return {"inspect": False}
        ledger = RequestLedger(IntermittentClient())
        request = inspection_request(scenarios()["cheap_recovery"], calibration=True)
        ledger.complete(request, "first", validate_inspection_response)
        with self.assertRaises(RequestStop):
            ledger.complete(request, "second", validate_inspection_response)
        self.assertEqual(ledger.rows[0]["provider_metadata"]["output_tokens"], 7)
        self.assertEqual(ledger.rows[1]["provider_metadata"], {})

    def test_live_execution_is_blocked_before_any_dispatch(self):
        with self.assertRaisesRegex(ValueError, "provider launch contract"):
            execute(FakeClient("optimal"), fake=False)

    def test_full_memory_and_answer_visible_controls_all_routes(self):
        # Controls are offline and deliberately change information/capacity.
        # The answer-visible controller never sends an evaluator answer to a model.
        for revise in (False, True):
            config = replace(scenarios()["costly_recovery"], revise=revise,
                             first_capacity=6, second_capacity=6, recovery_available=False)
            for fixture in route_fixtures(config):
                ledger = RequestLedger(FakeClient("optimal"))
                result = run_model_episode(config, fixture, "never_inspect", "inferred_dependencies", ledger, "control")
                self.assertTrue(result["success"])
                self.assertTrue(result["pre_recovery_available"])
                # Deliberately reveal the answer early only to this offline control.
                required = fixture.revision if revise and fixture.target == fixture.revision.key else next(
                    r for r in fixture.receipts if r.key == fixture.target)
                env = ArtifactEnvironment(config, fixture)
                for name in ("collect_receipts", "seal_receipts", "read_manifest", "process_build", "seal_build"):
                    env.step(Action(name))
                for _ in range(config.delay):
                    env.step(Action("work"))
                env.step(Action("get_requirement"))
                self.assertTrue(env.step(Action("submit", required)).success)

    def test_verifier_rejects_incorrect_and_stale_payloads(self):
        config = scenarios()["revision_costly_recovery"]
        fixture = next(f for f in route_fixtures(config) if f.target == f.candidates[0])
        for submitted, expected in ((Receipt(fixture.target, 1, fixture.receipts[0].token), "stale_revision"),
                                     (Receipt(fixture.target, 2, "wrong"), "wrong_receipt")):
            env = ArtifactEnvironment(config, fixture)
            for name in ("collect_receipts", "seal_receipts", "read_manifest", "process_build", "seal_build"):
                env.step(Action(name))
            for _ in range(config.delay):
                env.step(Action("work"))
            env.step(Action("get_requirement"))
            self.assertEqual(env.step(Action("submit", submitted)).error, expected)


if __name__ == "__main__":
    unittest.main()
