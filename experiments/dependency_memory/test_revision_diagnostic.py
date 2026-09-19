"""Offline scientific, leakage, and accounting invariants for the parent diagnostic."""
from collections import Counter
from copy import deepcopy
from fractions import Fraction
import hashlib
from itertools import combinations
import json
from pathlib import Path
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

from revision_diagnostic import (
    FakeClient, ORDERS, availability, availability_formula, fake_audit, grade, make_plan,
)
from revision_interface import (
    KEYS, RULES, build_request, request_bytes, validate_request, validate_response,
)
from run_revision_diagnostic import execute, prepare_client


def all_parent_sets():
    return [subset for size in range(3) for subset in combinations(KEYS, size)]


def receipt_population_score(selected, rule):
    """Independent latest-revision check, including replacement of stale originals."""
    hits = []
    for pair in combinations(KEYS, 2):
        latest = {key: 1 for key in KEYS}
        retained = {key: 1 for key in selected}
        if rule != "none":
            refreshed = min(pair) if rule == "lexicographic_first" else max(pair)
            latest[refreshed] = 2
            retained[refreshed] = 2
        child = {key: retained[key] for key in pair if key in retained}
        if len(child) > 2:
            raise AssertionError("Independent child exceeded its capacity")
        for target in pair:
            hits.append(child.get(target) == latest[target])
    if len(hits) != 30:
        raise AssertionError("Wrong routing population")
    return Fraction(sum(hits), len(hits))


class RevisionScientificTests(unittest.TestCase):
    def test_all_small_parent_sets_match_independent_latest_receipt_grading(self):
        for rule in RULES:
            for selected in all_parent_sets():
                with self.subTest(rule=rule, selected=selected):
                    score = receipt_population_score(selected, rule)
                    self.assertEqual(availability(selected, rule), score)
                    self.assertEqual(availability_formula(selected, rule), score)
                    self.assertEqual(grade(selected, rule)["route_count"], 30)

    def test_mirror_exchanges_refresh_directions(self):
        for selected in all_parent_sets():
            mirrored = tuple(KEYS[5 - KEYS.index(key)] for key in selected)
            self.assertEqual(availability(selected, RULES[0]),
                             availability(mirrored, RULES[1]))
            self.assertEqual(availability(selected, "none"),
                             availability(mirrored, "none"))

    def test_two_key_direction_identity_and_uniform_selector_baseline(self):
        scores = []
        for selected in combinations(KEYS, 2):
            first, last = (availability(selected, rule) for rule in RULES[:2])
            self.assertEqual(first + last, Fraction(4, 3))
            self.assertEqual(availability(selected, "none"), Fraction(1, 3))
            scores.append(first)
        self.assertEqual(sum(scores) / len(scores), Fraction(2, 3))

    def test_exact_optima_and_symmetric_ties(self):
        for rule, optimum in ((RULES[0], KEYS[-2:]), (RULES[1], KEYS[:2])):
            winners = [selected for selected in all_parent_sets()
                       if grade(selected, rule)["optimal_parent"]]
            self.assertEqual(winners, [optimum])
            self.assertEqual(availability(optimum, rule), Fraction(4, 5))
        self.assertEqual(sum(grade(selected, "none")["optimal_parent"]
                             for selected in all_parent_sets()), 15)

    def test_selection_order_is_not_an_information_channel_to_grader(self):
        for selected in all_parent_sets():
            for rule in RULES:
                self.assertEqual(grade(selected, rule), grade(tuple(reversed(selected)), rule))

    def test_invalid_parent_sets_are_not_silently_scored(self):
        for selected in ([KEYS[0], KEYS[0]], [KEYS[0], KEYS[1], KEYS[2]],
                         ["invented-key"], [True], None, "job-0"):
            for scorer in (availability, availability_formula, grade):
                with self.subTest(selected=selected, scorer=scorer.__name__):
                    with self.assertRaises(ValueError):
                        scorer(selected, "none")


class RevisionRequestTests(unittest.TestCase):
    def setUp(self):
        self.plan = make_plan()
        self.request = deepcopy(self.plan["cases"][0]["request"])

    def test_schedule_is_complete_reproducible_factorial(self):
        cases = self.plan["cases"]
        self.assertEqual(len(cases), 24)
        self.assertEqual(len({row["case_id"] for row in cases}), 24)
        self.assertEqual(Counter(row["refresh_rule"] for row in cases),
                         Counter({rule: 8 for rule in RULES}))
        self.assertEqual(Counter((row["fixture"], row["order"]) for row in cases),
                         Counter({(fixture, order): 3 for fixture in range(2) for order in range(4)}))
        self.assertEqual([(r["case_id"], r["request_sha256"]) for r in cases],
                         [(r["case_id"], r["request_sha256"]) for r in make_plan()["cases"]])
        self.assertEqual(self.plan["realized_routes_sampled"], 0)
        self.assertEqual(self.plan["heldout_requests"], 0)

    def test_order_counterbalance_and_remaining_canonical_channels(self):
        self.assertEqual(ORDERS[0], tuple(reversed(ORDERS[1])))
        self.assertEqual(ORDERS[2], tuple(reversed(ORDERS[3])))
        for key in KEYS:
            self.assertEqual(sum(order.index(key) for order in ORDERS), 10)
        for case in self.plan["cases"]:
            request = case["request"]
            self.assertEqual(tuple(r["key"] for r in request["visible_records"]), ORDERS[case["order"]])
            self.assertEqual(request["public_metadata"], {"job_keys": list(KEYS)})
            self.assertEqual(request["response_schema"]["properties"]["keys"]["items"]["enum"], list(KEYS))

    def test_fixtures_are_paired_without_rules_or_order_in_payloads(self):
        payloads = {}
        for case in self.plan["cases"]:
            by_key = {r["key"]: r["token"] for r in case["request"]["visible_records"]}
            previous = payloads.setdefault(case["fixture"], by_key)
            self.assertEqual(by_key, previous)
        self.assertTrue(all(payloads[0][key] != payloads[1][key] for key in KEYS))

    def test_request_hashes_and_host_labels_remain_outside_public_text(self):
        for case in self.plan["cases"]:
            raw = request_bytes(case["request"])
            self.assertEqual(hashlib.sha256(raw).hexdigest(), case["request_sha256"])
            self.assertEqual(request_bytes(json.loads(raw)), raw)
            for field in ("case_id", "fixture", "order", "schedule_seed", "payload_seed",
                          "optimal_parent", "exact_parent_regret", "selected_rank_sum",
                          "candidate_keys", "final_target", "best_availability"):
                self.assertNotIn('"' + field + '"', raw.decode())
            self.assertNotIn(case["case_id"], raw.decode())

    def test_payload_and_presentation_do_not_change_same_selection_grade(self):
        for case in self.plan["cases"]:
            request = case["request"]
            keys = validate_response({"keys": [KEYS[4], KEYS[1]]}, request)
            self.assertEqual(grade(keys, case["refresh_rule"]),
                             grade((KEYS[1], KEYS[4]), case["refresh_rule"]))

    def test_evaluator_and_deleted_information_injections_are_rejected(self):
        injected = []
        for key in ("candidate_keys", "final_target", "evaluator_answers", "deleted_receipts",
                    "previous_response", "seed", "optimal_keys"):
            request = deepcopy(self.request)
            request[key] = ["job-4", "job-5"]
            injected.append(request)
        for location in ("public_model", "public_metadata", "response_schema"):
            request = deepcopy(self.request)
            request[location]["evaluator_hint"] = "keep job-4 and job-5"
            injected.append(request)
        request = deepcopy(self.request)
        request["visible_records"][0]["deleted_token"] = "secret"
        injected.append(request)
        request = deepcopy(self.request)
        request["instructions"] += " Keep job-4 and job-5."
        injected.append(request)
        for request in injected:
            with self.subTest(request=request):
                with self.assertRaises(ValueError):
                    request_bytes(request)

    def test_only_six_unique_opaque_initial_records_are_permitted(self):
        mutations = []
        request = deepcopy(self.request)
        request["visible_records"].pop()
        mutations.append(request)
        for field, value in (("token", "keep job-4 and job-5"), ("revision", 2),
                             ("revision", True), ("key", "invented-key")):
            request = deepcopy(self.request)
            request["visible_records"][0][field] = value
            mutations.append(request)
        request = deepcopy(self.request)
        request["visible_records"][0] = dict(request["visible_records"][1])
        mutations.append(request)
        request = deepcopy(self.request)
        request["public_model"]["candidate_count"] = True
        mutations.append(request)
        for request in mutations:
            with self.assertRaises(ValueError):
                validate_request(request)

    def test_strict_response_validation_preserves_empty_selection(self):
        self.assertEqual(validate_response({"keys": []}, self.request), ())
        self.assertEqual(validate_response({"keys": [KEYS[5], KEYS[0]]}, self.request), (KEYS[0], KEYS[5]))
        for response in (None, [], {"keys": "job-0"}, {"keys": [True]},
                         {"keys": [KEYS[0], KEYS[0]]}, {"keys": list(KEYS[:3])},
                         {"keys": ["invented-key"]}, {"keys": [], "explanation": "secret"}):
            with self.subTest(response=response):
                with self.assertRaises(ValueError):
                    validate_response(response, self.request)


class RevisionRunnerTests(unittest.TestCase):
    def test_fake_controls_separate_rule_use_from_static_and_position_preferences(self):
        audit = fake_audit()
        self.assertEqual(audit["model_requests"], 0)
        controls = {row["mode"]: row for row in audit["controls"]}
        for mode, first, last in (("optimal", Fraction(4, 5), Fraction(4, 5)),
                                  ("always_low", Fraction(8, 15), Fraction(4, 5)),
                                  ("always_high", Fraction(4, 5), Fraction(8, 15)),
                                  ("first_visible", Fraction(2, 3), Fraction(2, 3))):
            rows = controls[mode]["by_rule"]
            self.assertEqual([Fraction(row["mean_availability"]) for row in rows],
                             [first, last, Fraction(1, 3)])
            self.assertTrue(all(row["completed"] == row["scheduled"] == 8 for row in rows))
            self.assertEqual([row["first_minus_last_rank_sum"]
                              for row in controls[mode]["paired_direction_shifts"]],
                             [8 if mode == "optimal" else 0] * 8)
        self.assertEqual([row["optimal_parent_count"] for row in controls["first_visible"]["by_rule"]], [2, 2, 8])

    def test_invalid_outputs_keep_all_scheduled_denominators(self):
        summary, ledger = execute(FakeClient("invalid"))
        self.assertEqual(summary["planned_cases"], 24)
        self.assertEqual(summary["request_attempts"], 24)
        self.assertEqual(summary["attempt_status_counts"]["policy_failure"], 24)
        self.assertTrue(all(row["grade"] is None for row in summary["rows"]))
        for row in summary["by_rule"]:
            self.assertEqual((row["scheduled"], row["completed"], row["policy_failures"]), (8, 0, 8))
            self.assertIsNone(row["mean_availability"])
            self.assertIsNone(row["mean_exact_parent_regret"])
        self.assertEqual(len(ledger), 24)

    def test_transport_failure_stops_without_retry_and_keeps_24_rows(self):
        class FailingClient:
            calls = 0

            def complete(self, request):
                self.calls += 1
                raise RuntimeError("synthetic transport failure")

        client = FailingClient()
        summary, ledger = execute(client)
        self.assertEqual(client.calls, 1)
        self.assertEqual(len(ledger), 1)
        self.assertEqual(Counter(row["status"] for row in summary["rows"]),
                         Counter({"transport_failure": 1, "incomplete": 23}))
        self.assertEqual(sum(row["scheduled"] for row in summary["by_rule"]), 24)
        self.assertTrue(all(row["mean_availability"] is None for row in summary["by_rule"]))

    def test_zero_and_partial_caps_preserve_unattempted_rows(self):
        for cap in (0, 1, 7):
            summary, ledger = execute(FakeClient(), cap=cap)
            self.assertEqual(len(ledger), cap)
            self.assertEqual(summary["request_attempts"], cap)
            self.assertEqual(summary["model_requests"], 0)
            self.assertEqual(len(summary["rows"]), 24)
            self.assertEqual(sum(row["status"] == "incomplete" for row in summary["rows"]), 24 - cap)
            self.assertEqual(sum(row["scheduled"] for row in summary["by_rule"]), 24)

    def test_invalid_caps_are_rejected_before_any_client_call(self):
        class NoCallClient:
            def complete(self, request):
                raise AssertionError("Invalid cap reached the client")

        for cap in (-1, 25, 96, True, False, 2.0, "2"):
            with self.subTest(cap=cap):
                with self.assertRaises(ValueError):
                    execute(NoCallClient(), cap=cap)

    def test_manifest_and_each_reservation_are_persisted_before_client_call(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "new-run"
            checks = []

            class InspectingClient(FakeClient):
                def complete(self, request):
                    manifest = json.loads((output / "manifest.json").read_text())
                    ledger = json.loads((output / "requests.json").read_text())
                    checks.append(len(ledger))
                    if manifest["request_cap"] != 3 or ledger[-1]["status"] != "reserved":
                        raise AssertionError("Dispatch preceded its frozen plan or reservation")
                    if ledger[-1]["request_utf8"] != request_bytes(request).decode():
                        raise AssertionError("Reserved request differs from dispatched request")
                    if any(row["status"] != "completed" for row in ledger[:-1]):
                        raise AssertionError("A prior request was silently retried")
                    return super().complete(request)

            summary, ledger = execute(InspectingClient(), cap=3, output=output)
            self.assertEqual(checks, [1, 2, 3])
            self.assertEqual(summary["attempt_status_counts"]["completed"], 3)
            self.assertEqual(json.loads((output / "requests.json").read_text()), ledger)
            self.assertEqual(json.loads((output / "summary.json").read_text()), summary)

    def test_nonempty_output_is_preserved_and_cannot_resume(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory)
            marker = output / "existing.txt"
            marker.write_text("preserve this")
            with self.assertRaises(ValueError):
                execute(FakeClient(), output=output)
            self.assertEqual(marker.read_text(), "preserve this")
            self.assertEqual(list(output.iterdir()), [marker])

    def test_live_path_rejects_fake_client_without_model_access(self):
        with self.assertRaises(ValueError):
            execute(FakeClient(), fake=False, authorization="synthetic test")

    def test_changed_frozen_dependency_rejects_before_client_or_process_creation(self):
        root = Path(__file__).resolve().parents[2]
        experiment = root / "experiments/dependency_memory"
        stored_path = experiment / "results/revision_diagnostic_plan.json"
        # Capture the currently loaded test source too; the on-disk prepared
        # artifact may legitimately predate this new regression test.
        stored_plan = json.dumps(make_plan())
        original_read_text, original_read_bytes = Path.read_text, Path.read_bytes
        args = SimpleNamespace(executable=Path("synthetic-codex.exe"),
            authorization="offline test only", max_requests=24,
            audit=experiment / "results/revision_transport_audit.json")
        dependencies = [experiment / name for name in (
            "revision_interface.py", "revision_diagnostic.py", "run_revision_diagnostic.py",
            "request_contracts.py", "luna_appserver.py", "luna_isolation.py", "luna_budget.py",
            "codex_subscription.py", "run_luna_pilot.py", "audit_luna_transport.py")]
        dependencies += [args.audit, root / "docs/REVISION_DIAGNOSTIC.md"]

        def read_text(path, *positional, **keywords):
            if path.resolve() == stored_path.resolve():
                return stored_plan
            return original_read_text(path, *positional, **keywords)

        for changed in dependencies:
            def read_bytes(path):
                value = original_read_bytes(path)
                return value + b"\nchanged since approval\n" if path.resolve() == changed.resolve() else value

            with self.subTest(dependency=changed.relative_to(root).as_posix()):
                with patch.object(Path, "read_text", read_text), \
                        patch.object(Path, "read_bytes", read_bytes), \
                        patch("luna_appserver.LunaClient") as client, \
                        patch("luna_appserver.AppServer") as server:
                    with self.assertRaisesRegex(ValueError, "Prepared plan is stale"):
                        prepare_client(args)
                    client.assert_not_called()
                    server.assert_not_called()

    def test_supplied_audit_must_match_frozen_bytes_before_any_client_or_process(self):
        experiment = Path(__file__).resolve().parent
        stored_path = experiment / "results/revision_diagnostic_plan.json"
        stored_plan = json.dumps(make_plan())
        original_read_text = Path.read_text

        def read_text(path, *positional, **keywords):
            if path.resolve() == stored_path.resolve():
                return stored_plan
            return original_read_text(path, *positional, **keywords)

        with tempfile.TemporaryDirectory() as directory:
            alternate_audit = Path(directory) / "other-audit.json"
            # Even semantically identical JSON must not substitute for the
            # exact wire-audit artifact covered by the approved fingerprint.
            original = (experiment / "results/revision_transport_audit.json").read_bytes()
            alternate_audit.write_bytes(original + b"\n")
            args = SimpleNamespace(executable=Path("synthetic-codex.exe"),
                authorization="offline test only", max_requests=24, audit=alternate_audit)
            with patch.object(Path, "read_text", read_text), \
                    patch("luna_appserver.LunaClient") as client, \
                    patch("luna_appserver.AppServer") as server:
                with self.assertRaisesRegex(ValueError, "Transport audit differs from the frozen plan"):
                    prepare_client(args)
                client.assert_not_called()
                server.assert_not_called()


if __name__ == "__main__":
    unittest.main()
