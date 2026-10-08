"""Coding selection and public/private checker checks using authored fixtures."""
from copy import deepcopy
from unittest.mock import patch
import unittest

from .code_runner import DockerRunner
from .coding_tasks import EXPOSED, select_coding
from .fixtures import code_example
from .grading import CodeChecker, ExecutionResult, InfrastructureError, compare_tokens
from .records import InterfaceError, digest, wire


class SumRunner:
    """An engineering double: no candidate source is executed on the host."""
    def __init__(self):
        self.inputs = []

    def execute(self, code, stdin, wall_seconds=10):
        self.inputs.append((code, stdin))
        if code == "raise":
            return ExecutionResult("runtime_error", stderr="authored runtime failure")
        if code == "timeout":
            return ExecutionResult("timeout")
        if code == "infrastructure":
            raise InfrastructureError("authored engine failure")
        return ExecutionResult("completed", "0\n" if code == "wrong" else str(sum(map(int, stdin.split()))) + "\n")


def inventory_fixture():
    items = []
    for difficulty in ("easy", "medium", "hard"):
        for index in range(6):
            items.append({"platform": "authored", "question_id": f"{difficulty}{index}", "difficulty": difficulty,
                          "release_date": "2026-10-08", "statement": f"Authored selection fixture {difficulty}/{index}: sum two integers.",
                          "input_format": "Two integers", "output_format": "One integer",
                          "public_tests": [{"id": "public1", "input": "2 3\n", "output": "5\n"}],
                          "private_tests": [{"id": "reserved1", "input": "-4 9\n", "output": "5\n"}],
                          "interface": "stdin_stdout", "comparison": "exact_tokens", "standard_library_python": True,
                          "license_review": {"permitted": True, "source": "authored-test-fixture-not-real-license-review", "reviewer": "unittest fixture"},
                          "reference_code": "reference-sum-double", "reference_provenance": "authored double, never an acquired benchmark solution",
                          "retained_tests_complete": True})
    return {"dataset": "livecodebench/code_generation_lite", "release": "release_v6", "dataset_commit": "0" * 40,
            "loader_sha256": "0" * 64, "source_files": [{"path": "authored_inventory_fixture", "sha256": "0" * 64}], "items": items}


class CodingPreparationTests(unittest.TestCase):
    def test_selection_uses_frozen_hash_order_and_four_per_stratum(self):
        inventory = inventory_fixture()
        selected, report = select_coding(inventory, CodeChecker(SumRunner()))
        self.assertEqual(len(selected), 12)
        self.assertEqual(report["shortfalls"], {"easy": 0, "medium": 0, "hard": 0})
        for difficulty in ("easy", "medium", "hard"):
            ordered = sorted((digest(f"rollback-v02|20261007|authored|{x['question_id']}"), x["question_id"])
                             for x in inventory["items"] if x["difficulty"] == difficulty)
            actual = [e.data()["origin"]["question_id"] for t, e in selected if t.stratum == difficulty]
            self.assertEqual(actual, [identity for _, identity in ordered[:4]])
        reversed_input = deepcopy(inventory)
        reversed_input["items"].reverse()
        self.assertEqual([t.task_id for t, _ in selected], [t.task_id for t, _ in select_coding(reversed_input, CodeChecker(SumRunner()))[0]])

    def test_exposed_ids_duplicate_identity_and_content_are_logged(self):
        inventory = inventory_fixture()
        exposed = deepcopy(inventory["items"][0])
        exposed.update(platform="atcoder", question_id="abc301_a", statement="Authored exposed-ID test.")
        inventory["items"] += [exposed, deepcopy(inventory["items"][1])]
        duplicate_content = deepcopy(inventory["items"][2])
        duplicate_content["question_id"] = "another-id-same-statement"
        inventory["items"].append(duplicate_content)
        _, report = select_coding(inventory, CodeChecker(SumRunner()))
        self.assertEqual(len(EXPOSED), 10)
        reasons = [r["reason"] for r in report["exclusions"]]
        self.assertIn("design_or_human_exposure", reasons)
        self.assertEqual(reasons.count("duplicate_identity_or_statement"), 2)

    def test_license_reference_test_completeness_and_interface_gates(self):
        changes = [("license_review", {}), ("reference_code", ""), ("private_tests", []), ("retained_tests_complete", False),
                   ("comparison", "floating_tolerance"), ("interface", "callable_method"), ("standard_library_python", False)]
        for field, value in changes:
            inventory = inventory_fixture()
            inventory["items"] = [deepcopy(inventory["items"][0])]
            inventory["items"][0][field] = value
            selected, report = select_coding(inventory, CodeChecker(SumRunner()))
            self.assertFalse(selected)
            self.assertEqual(len(report["exclusions"]), 1)
            self.assertEqual(report["shortfalls"]["easy"], 4)

    def test_wrong_reference_is_pre_freeze_exclusion_but_engine_loss_stops_preparation(self):
        inventory = inventory_fixture()
        inventory["items"][0]["reference_code"] = "wrong"
        _, report = select_coding(inventory, CodeChecker(SumRunner()))
        self.assertIn("reference_fails_fixed_suite_or_resources", [x["reason"] for x in report["exclusions"]])
        inventory["items"][0]["reference_code"] = "infrastructure"
        with self.assertRaises(InfrastructureError):
            select_coding(inventory, CodeChecker(SumRunner()))

    def test_unpinned_or_substituted_dataset_is_rejected(self):
        for field, value in (("dataset_commit", "main"), ("loader_sha256", None), ("release", "release_v5"),
                             ("dataset", "livecodebench/code_generation"), ("source_files", [])):
            inventory = inventory_fixture()
            inventory[field] = value
            with self.assertRaises((InterfaceError, TypeError)):
                select_coding(inventory, CodeChecker(SumRunner()))


class CodeGradingTests(unittest.TestCase):
    def test_exact_token_comparison_preserves_numeric_strings_and_case(self):
        self.assertTrue(compare_tokens(" 1\n2\t", "1 2"))
        self.assertFalse(compare_tokens("1.0", "1"))
        self.assertFalse(compare_tokens("YES", "Yes"))

    def test_reserved_failures_never_become_public_feedback(self):
        task, evaluator, *_ = code_example()
        class PublicOnlyRunner(SumRunner):
            def execute(self, code, stdin, wall_seconds=10):
                self.inputs.append((code, stdin))
                return ExecutionResult("completed", "5\n" if stdin == "2 3\n" else "HIDDEN_WRONG_OUTPUT")
        runner = PublicOnlyRunner()
        checker = CodeChecker(runner)
        receipt = checker.receipt(task, {"code": "authored-public-only"})
        self.assertEqual(receipt.data()["status"], "public_pass")
        self.assertEqual(len(runner.inputs), 1)
        grade = checker.grade(task, evaluator, {"code": "authored-public-only"})
        self.assertEqual(grade["score"], 0)
        self.assertNotIn("HIDDEN_WRONG_OUTPUT", receipt.json_text)
        self.assertNotIn("reserved1", receipt.json_text)

    def test_runner_receives_one_input_and_source_without_expected_or_other_tests(self):
        task, evaluator, *_ = code_example()
        runner = SumRunner()
        self.assertEqual(CodeChecker(runner).grade(task, evaluator, {"code": "reference"})["score"], 1)
        self.assertEqual(runner.inputs, [("reference", "2 3\n"), ("reference", "-4 9\n"), ("reference", "0 0\n")])

    def test_runtime_and_timeout_are_not_public_mismatch_eligibility(self):
        task = code_example()[0]
        checker = CodeChecker(SumRunner())
        for code in ("raise", "timeout"):
            self.assertFalse(checker.receipt(task, {"code": code}).eligible)
        self.assertTrue(checker.receipt(task, {"code": "wrong"}).eligible)

    def test_suite_limit_keeps_a_timeout_disposition_and_does_not_prune_tests(self):
        task, evaluator, *_ = code_example()
        checker = CodeChecker(SumRunner(), suite_wall_seconds=0)
        grade = checker.grade(task, evaluator, {"code": "reference"})
        self.assertEqual(grade["score"], 0)
        self.assertEqual(grade["tests"][0]["status"], "suite_timeout")

    def test_unpinned_image_and_engine_failure_never_execute_host_code(self):
        with self.assertRaises(InfrastructureError):
            DockerRunner("python:3.11-slim")
        runner = DockerRunner("python@sha256:" + "0" * 64, executable="definitely-no-such-docker-executable")
        with self.assertRaises(InfrastructureError):
            runner.execute("raise AssertionError('must not run on host')", "")
