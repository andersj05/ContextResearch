"""Information-channel, supersession and outcome-separation tests; no provider."""
import ast
from copy import deepcopy
import json
from pathlib import Path
import unittest
from unittest.mock import patch

from experiments.dependency_memory.evidence_use.guard import receipt_answer
from . import actor, runtime
from .audit import FixtureClient, histories, SCOPES, TREES, INVENTORIES, proposals, screen
from .oracle import specification


def case():
    rows = next(r for r in histories(1) if r and r[0]["check"] == "tests" and r[0]["returncode"] == 0)
    for row in rows:
        row.update(argv=["python", "-m", "unittest"], stdout="Public success\r\n", stderr="", expected="PRIVATE_LABEL")
    return {"id": "control", "initial": rows, "between": [], "scope": ["tests"],
            "task": {"snapshot": TREES[0], "required_checks": ["tests"], "artifacts": {}, "expected": "PRIVATE_TASK_LABEL"},
            "expected": "PRIVATE_EPISODE_LABEL", "inspection": "private annotation"}


class MethodTests(unittest.TestCase):
    def test_reverse_specification_and_latest_projection_on_small_complete_grid(self):
        from experiments.dependency_memory.workflow_eval.grader import expected_answer
        for records in histories(1):
            for tree in TREES:
                for scope in SCOPES:
                    for inventory in INVENTORIES:
                        task = {"snapshot": tree, "required_checks": scope, "artifacts": inventory}
                        expected = specification(records, task)
                        self.assertEqual(expected, expected_answer(records, task))
                        self.assertEqual(expected, specification(actor.project(records), task))

    def test_canonical_shadow_matches_direct_for_valid_invalid_and_binding_proposals(self):
        for records in histories(1):
            for proposal in proposals(records):
                for cap in (0, 2, 203, 4096):
                    direct, _ = actor.direct_memory(records, cap)
                    checked, _ = actor.checked_shadow({"memory": proposal}, records, cap)
                    self.assertEqual(direct, checked)

    def test_later_failure_overrides_success_even_if_older_success_matches_artifacts(self):
        rows = next(r for r in histories(1) if r and r[0]["check"] == "paper" and r[0]["snapshot"] == TREES[0] and r[0]["returncode"] == 0)
        task = {"snapshot": TREES[0], "required_checks": ["paper"], "artifacts": INVENTORIES[0]}
        later = deepcopy(rows[0])
        later.update(returncode=1, artifacts={}, run_id="d" * 64)
        self.assertEqual(["paper"], specification(rows + [later], task)["needs_work"])
        self.assertEqual([], specification([later] + rows, task)["needs_work"])

    def test_public_requests_exclude_evaluator_labels_and_observe_order(self):
        class Recording(FixtureClient):
            def __init__(self):
                self.requests = []
            def complete(self, identity, request):
                self.requests.append((identity, deepcopy(request)))
                return super().complete(identity, request)
        source = case()
        client = Recording()
        trace = runtime.execute(source, client)
        self.assertEqual("complete", trace["status"])
        self.assertEqual(runtime.schedule("control"), [i for i, _ in client.requests])
        self.assertEqual(6, len(client.requests))
        for _, request in client.requests:
            self.assertNotIn("PRIVATE", actor.request_bytes(request).decode())
            self.assertNotIn("inspection", request["observation"])
            if request["stage"] != "execute":
                self.assertNotIn("final_public_state", request["observation"])
        self.assertEqual("PRIVATE_LABEL", source["initial"][0]["expected"])
        self.assertEqual(0, trace["provider_generations"])
        self.assertIsNone(trace["priced_total_cost"])

    def test_transport_stop_keeps_exact_prefix_and_never_retries(self):
        class Broken(FixtureClient):
            attempts = []
            def complete(self, identity, request):
                self.attempts.append(identity)
                raise TimeoutError("private credential must not enter results")
        client = Broken()
        trace = runtime.execute(case(), client)
        self.assertEqual(runtime.schedule("control")[:1], client.attempts)
        self.assertEqual("missing_response", trace["slots"][0]["status"])
        self.assertTrue(all(s["status"] == "not_dispatched_after_stop" for s in trace["slots"][1:]))
        self.assertNotIn("credential", json.dumps(trace))
        self.assertEqual(0, trace["simulated_or_replayed_completions"])

    def test_final_veto_is_recorded_without_a_repair_or_another_call(self):
        class WrongFinal(FixtureClient):
            def complete(self, identity, request):
                if request["stage"] == "execute":
                    return actor.wire({"ready": False, "needs_work": ["tests"], "evidence": {c: None for c in actor.CHECKS}}).decode()
                return super().complete(identity, request)
        trace = runtime.execute(case(), WrongFinal())
        self.assertEqual(6, trace["simulated_or_replayed_completions"])
        self.assertTrue(all(r["guard"]["status"] == "contradicted" and not r["released"] for r in trace["finals"].values()))
        self.assertTrue(all(r["response"]["ready"] is False for r in trace["finals"].values()))
        self.assertTrue(all(r["guard"]["derived_answer"]["ready"] is True for r in trace["finals"].values()))

    def test_empty_parent_cannot_be_resurrected_in_direct_child(self):
        with patch.object(actor, "PARENT_CAP", 0):
            class Empty(FixtureClient):
                def complete(self, identity, request):
                    if request["stage"] != "execute":
                        return '{"memory":"[]"}'
                    return super().complete(identity, request)
            trace = runtime.execute(case(), Empty())
        self.assertEqual("", trace["memories"]["direct_parent"]["memory"])
        self.assertEqual("[]", trace["memories"]["direct_child"]["memory"])
        self.assertFalse(trace["finals"]["direct"]["response"]["ready"])
        self.assertTrue(trace["finals"]["full"]["response"]["ready"])

    def test_scope_and_utf8_caps_are_enforced_without_truncation(self):
        bad = case()
        bad["scope"] = ["paper"]
        with self.assertRaises(ValueError):
            runtime.execute(bad, FixtureClient())
        self.assertEqual("λ", actor.admit_prose({"memory": "λ"}, 2)[0])
        self.assertEqual("", actor.admit_prose({"memory": "λ"}, 1)[0])
        self.assertEqual("", actor.admit_prose({"memory": "x" * 1537}, 1536)[0])
        with self.assertRaises(ValueError):
            actor.request_bytes({**actor.final_request("[]", case()), "expected": {}})

    def test_requested_archive_preserves_later_failures_and_order(self):
        source = case()
        later = deepcopy(source["initial"][0])
        later.update(returncode=1, run_id="d" * 64)
        source["between"] = [later]
        trace = runtime.execute(source, FixtureClient())
        for arm in ("indexed", "full"):
            memory = actor.strict_json(trace["finals"][arm]["request"]["observation"]["memory"])
            self.assertEqual([source["initial"][0]["run_id"], later["run_id"]], [r["run_id"] for r in memory])
            self.assertFalse(trace["finals"][arm]["response"]["ready"])
        self.assertGreater(trace["archive_storage"]["byte_nanoseconds"], 0)

    def test_correct_prose_can_be_uncheckable_and_is_not_scored_as_repaired(self):
        class Prose(FixtureClient):
            def complete(self, identity, request):
                if request["stage"] != "execute":
                    return '{"memory":"The tests passed; the exact receipt is retained in prose."}'
                if identity.endswith("prose-final"):
                    return actor.wire({"ready": True, "needs_work": [], "evidence": {
                        c: case()["initial"][0]["run_id"] if c == "tests" else None for c in actor.CHECKS}}).decode()
                return super().complete(identity, request)
        trace = runtime.execute(case(), Prose())
        answer = trace["finals"]["prose"]
        self.assertEqual("uncheckable", answer["guard"]["status"])
        self.assertFalse(answer["released"])
        task = {k: case()["task"][k] for k in ("snapshot", "required_checks", "artifacts")}
        self.assertEqual(specification(case()["initial"], task), answer["response"])

    def test_runtime_imports_no_evaluator_or_provider(self):
        for module in (actor, runtime):
            tree = ast.parse(Path(module.__file__).read_text(encoding="utf-8"))
            imports = [n.module or "" for n in ast.walk(tree) if isinstance(n, ast.ImportFrom)]
            self.assertFalse(any("oracle" in name or "grader" in name or "appserver" in name for name in imports))
        with self.assertRaises(ValueError):
            runtime.execute(case(), type("Live", (), {"mode": "live"})())

    def test_screen_distinguishes_full_refresh_and_actual_parent_dependence(self):
        public = runtime.public_case(case())
        public["source_commits"] = []  # Constructed timing control, no actual source observation.
        self.assertTrue(screen(public)["parent_needed_for_actual_query"])
        refreshed = deepcopy(public)
        later = deepcopy(refreshed["initial"][0])
        later["run_id"] = "d" * 64
        refreshed["between"] = [later]
        self.assertFalse(screen(refreshed)["parent_needed_for_actual_query"])

    def test_request_budget_stops_before_callback_without_clipping(self):
        source = case()
        source["initial"][0]["stdout"] = "x" * (actor.MAX_REQUEST_BYTES + 1)
        class Never(FixtureClient):
            attempts = 0
            def complete(self, identity, request):
                self.attempts += 1
                return super().complete(identity, request)
        client = Never()
        trace = runtime.execute(source, client)
        self.assertEqual("stopped", trace["status"])
        self.assertEqual(0, client.attempts)
        self.assertTrue(all(not slot["dispatched"] for slot in trace["slots"]))
        self.assertEqual(actor.MAX_REQUEST_BYTES + 1, len(source["initial"][0]["stdout"]))

    def test_saved_replay_rejects_a_response_from_another_public_request(self):
        from .simulate import ReplayClient
        client = ReplayClient({"version": actor.VERSION, "mode": "saved_response_replay", "calls": [
            {"identity": "control-prose-parent", "request_sha256": "0" * 64, "response_text": '{"memory":"[]"}'}]})
        trace = runtime.execute(case(), client)
        self.assertEqual("stopped", trace["status"])
        self.assertEqual(0, client.position)
        self.assertEqual("missing_response", trace["slots"][0]["status"])


if __name__ == "__main__":
    unittest.main()
