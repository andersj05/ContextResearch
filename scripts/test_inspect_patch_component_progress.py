"""Constructed parsing/comparison tests; no Docker or candidate execution."""

from types import SimpleNamespace
import json
import unittest

from scripts.inspect_patch_component_progress import (
    Capture, FORMAT, PatchRuntime, component_scores, compare_components, outputs_from, selected_records)


class ComponentDiagnosticTests(unittest.TestCase):
    def task(self):
        return {"contract": {"component_contracts": [{"component_id": "component_01", "family": "fixture"}]},
                "public_tests": [{"id": "public-" + str(i), "input": {}, "expected": {"component_01": 1}} for i in range(6)],
                "evaluator": {"reserved_tests": [{"id": "private-" + str(i), "input": {}, "expected": {"component_01": 1}} for i in range(18)]}}

    def test_complete_comparison_is_typed_and_does_not_infer_from_one_case(self):
        task = self.task()
        outputs = [{"component_01": 1}] * 24
        before = component_scores(task, outputs)
        self.assertIs(before[0]["all_24_cases_correct"], True)
        outputs[-1] = {"component_01": True}
        after = component_scores(task, outputs)
        self.assertIs(after[0]["all_24_cases_correct"], False)
        self.assertEqual(after[0]["passed_cases"], 23)
        self.assertEqual(compare_components(before, after)["regressed"], ["component_01"])

    def test_crashed_suite_is_not_imputed_as_component_failure(self):
        rows = component_scores(self.task(), None)
        self.assertIsNone(rows[0]["all_24_cases_correct"])
        self.assertEqual(rows[0]["unobserved_cases"], 24)
        rows = component_scores(self.task(), [{}] * 24)
        self.assertIs(rows[0]["all_24_cases_correct"], False)
        self.assertEqual(rows[0]["failed_cases"], 24)

    def test_unknown_final_keeps_known_first_but_never_fills_final_submission(self):
        first = {"step": 1, "public": {"status": "public_mismatch"}, "candidate": {"files": []}}
        result = {"score": None, "disposition": "unknown_dispatch", "attempts": [first]}
        selected = selected_records(result)
        self.assertEqual(selected["first_repair"], first)
        self.assertIsNone(selected["terminal_submitted_repair"])
        self.assertIsNone(selected["public_accepted_repair"])
        result["disposition"] = "repair_budget_exhausted"
        self.assertEqual(selected_records(result)["terminal_submitted_repair"], first)
        first["public"]["status"] = "public_pass"
        result["disposition"] = "runtime_error"
        self.assertEqual(selected_records(result)["terminal_submitted_repair"], first)

    def test_capture_requires_complete_valid_batch_shape(self):
        envelope = {"format": FORMAT, "status": "completed", "outputs": [{"component_01": 1}], "detail": ""}
        captured = SimpleNamespace(status="completed", stdout=json.dumps(envelope))
        self.assertEqual(outputs_from(captured, 1), envelope["outputs"])
        self.assertIsNone(outputs_from(captured, 2))
        envelope["status"] = "syntax_error"
        captured.stdout = json.dumps(envelope)
        self.assertIsNone(outputs_from(captured, 1))

    def test_capture_preserves_private_runtime_api_and_excludes_expected_from_inputs(self):
        sent = []

        class ConstructedRunner:
            def execute(self, program, payload, **limits):
                sent.append((program, json.loads(payload), limits))
                return SimpleNamespace(status="completed", stderr="", stdout=json.dumps({
                    "format": FORMAT, "status": "completed", "outputs": [{"component_01": 17}], "detail": ""}))

        capture = Capture(ConstructedRunner())
        runtime = PatchRuntime(runner=capture, max_containers=1)
        # Text is passed as inert data to a constructed runner, never executed.
        candidate = {"files": [{"path": "engine.py", "text": "def solve(data): return data\n"},
                               {"path": "rules.py", "text": ""}]}
        receipt = runtime.check(candidate, [{"id": "private-fixture", "input": {"x": 4},
                                             "expected": {"component_01": 17}}], public=False)
        self.assertEqual(receipt["status"], "private_pass")
        self.assertNotIn("observed", receipt)
        self.assertEqual(sent[0][1], {"cases": [{"x": 4}]})
        self.assertEqual(outputs_from(capture.local.result, 1), [{"component_01": 17}])


if __name__ == "__main__":
    unittest.main()
