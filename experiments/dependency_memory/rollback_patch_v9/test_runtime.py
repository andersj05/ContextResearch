"""No host candidate execution; access, typed grading and container bounds."""
from concurrent.futures import ThreadPoolExecutor
import json
import os
import threading
import unittest

from experiments.dependency_memory.rollback_patch_v9 import runtime
from experiments.dependency_memory.rollback_pilot.grading import ExecutionResult, InfrastructureError
from experiments.dependency_memory.rollback_pilot.records import wire


def candidate(engine="def solve(case):\n    return case\n", rules="VALUE = 1\n"):
    return {"files": [{"path": "engine.py", "text": engine},
                      {"path": "rules.py", "text": rules}]}


def envelope(outputs, *, status="completed", detail=""):
    return wire({"format": runtime.FORMAT, "status": status,
                 "outputs": outputs, "detail": detail})


class FakeRunner:
    def __init__(self, response):
        self.response, self.calls = response, []

    def execute(self, code, stdin, wall_seconds=10):
        self.calls.append({"code": code, "stdin": stdin, "wall_seconds": wall_seconds})
        if isinstance(self.response, Exception):
            raise self.response
        return self.response

    def configuration(self):
        return {"image": "disclosed-test-double"}


class RuntimeTests(unittest.TestCase):
    def check(self, response, *, expected=2, public=True):
        runner = FakeRunner(response)
        checker = runtime.PatchRuntime(runner=runner)
        value = checker.check(candidate(), [{"id": "case-one", "input": 1, "expected": expected}], public=public)
        return value, runner

    def test_exact_files_and_bytes_without_host_compile_import_or_execute(self):
        text = "raise AssertionError('must never execute on host')\n"
        program = runtime.candidate_program(candidate(engine=text))
        self.assertIn("/scratch", program)
        self.assertIn("must never execute on host", program)
        invalid = [None, {}, {"files": []}, {**candidate(), "extra": True}]
        for name in ("../engine.py", "/engine.py", "rules.py", "engine.py/other"):
            row = candidate()
            row["files"][0]["path"] = name
            invalid.append(row)
        invalid.append(candidate(engine="x" * (runtime.MAX_SOURCE_BYTES + 1)))
        for value in invalid:
            with self.subTest(value=str(value)[:40]), self.assertRaises(ValueError):
                runtime.candidate_program(value)

    def test_only_batch_inputs_enter_container_and_private_outputs_are_aggregate(self):
        secret = "PRIVATE_EXPECTED_SECRET"
        tests = [{"id": "PRIVATE_ID", "input": {"visible": 1}, "expected": secret}]
        runner = FakeRunner(ExecutionResult("completed", envelope(["wrong"])))
        checker = runtime.PatchRuntime(runner=runner)
        value = checker.check(candidate(), tests, public=False)
        self.assertEqual(json.loads(runner.calls[0]["stdin"]), {"cases": [{"visible": 1}]})
        self.assertNotIn(secret, wire(runner.calls))
        self.assertNotIn("PRIVATE_ID", wire(runner.calls))
        self.assertNotIn(secret, wire(value))
        self.assertNotIn("PRIVATE_ID", wire(value))
        self.assertNotIn("wrong", wire(value))
        self.assertEqual(value, {"status": "private_fail", "score": 0, "disposition": "test_failure",
                                 "test_count": 1, "passed_count": 0})

    def test_public_first_mismatch_has_public_evidence_and_complete_counts(self):
        runner = FakeRunner(ExecutionResult("completed", envelope([1, 9, 3])))
        tests = [{"id": str(i), "input": i, "expected": i} for i in (1, 2, 3)]
        result = runtime.PatchRuntime(runner=runner).check(candidate(), tests)
        self.assertEqual((result["status"], result["check_id"], result["input"], result["observed"],
                          result["expected"], result["passed_count"]), ("public_mismatch", "2", 2, 9, 2, 2))
        self.assertEqual(len(result["tests"]), 3)
        self.assertEqual(len(runner.calls), 1)

    def test_typed_json_comparison_rejects_bool_for_integer(self):
        result, _ = self.check(ExecutionResult("completed", envelope([True])), expected=1)
        self.assertEqual(result["status"], "public_mismatch")
        result, _ = self.check(ExecutionResult("completed", envelope([{"a": 1, "b": 2}])),
                               expected={"b": 2, "a": 1})
        self.assertEqual(result["status"], "public_pass")

    def test_execution_failures_and_output_errors_never_become_wrong_answer_eligibility(self):
        for status in ("syntax_error", "runtime_error", "timeout", "output_limit"):
            with self.subTest(status=status):
                result, _ = self.check(ExecutionResult(status, "", "private-code-error"))
                self.assertEqual(result["status"], status)
                private, _ = self.check(ExecutionResult(status, "private-input", "private-code-error"), public=False)
                self.assertNotIn("private-input", wire(private))
                self.assertNotIn("private-code-error", wire(private))
        for text in ("not JSON", envelope([]), wire({"format": runtime.FORMAT, "outputs": [2]})):
            result, _ = self.check(ExecutionResult("completed", text))
            self.assertEqual(result["status"], "invalid_output")
        result, _ = self.check(ExecutionResult("completed", envelope([], status="syntax_error", detail="line two")))
        self.assertEqual((result["status"], result["detail"]), ("syntax_error", "line two"))

    def test_bad_candidate_never_reaches_runner_and_bad_trusted_tests_raise(self):
        runner = FakeRunner(ExecutionResult("completed", envelope([1])))
        checker = runtime.PatchRuntime(runner=runner)
        result = checker.check({"files": []}, [{"id": "one", "input": 1, "expected": 1}])
        self.assertEqual(result["status"], "invalid_candidate")
        self.assertEqual(runner.calls, [])
        for tests in ([], [{"id": "one", "input": 1}],
                      [{"id": "one", "input": float("nan"), "expected": 1}],
                      [{"id": "one", "input": 1, "expected": 1}] * 2):
            with self.subTest(tests=tests), self.assertRaises(InfrastructureError):
                checker.check(candidate(), tests)

    def test_infrastructure_errors_propagate_and_release_bounded_slot(self):
        runner = FakeRunner(InfrastructureError("isolated engine unavailable"))
        checker = runtime.PatchRuntime(runner=runner, max_containers=1)
        with self.assertRaises(InfrastructureError):
            checker.check(candidate(), [{"id": "one", "input": 1, "expected": 1}])
        self.assertEqual(checker.statistics()["active_containers"], 0)
        runner.response = ExecutionResult("completed", envelope([1]))
        self.assertEqual(checker.check(candidate(), [{"id": "one", "input": 1, "expected": 1}])["score"], 1)

    def test_32_parallel_gradings_never_exceed_four_containers_or_mix_results(self):
        barrier = threading.Barrier(4)
        lock = threading.Lock()
        seen = []

        class Runner:
            def execute(self, code, stdin, wall_seconds):
                value = json.loads(stdin)["cases"][0]
                with lock:
                    seen.append(value)
                barrier.wait(timeout=10)
                return ExecutionResult("completed", envelope([value]))

        checker = runtime.PatchRuntime(runner=Runner(), max_containers=4)
        def evaluate(index):
            return checker.check(candidate(), [{"id": str(index), "input": index, "expected": index}])
        with ThreadPoolExecutor(max_workers=32) as pool:
            results = list(pool.map(evaluate, range(32)))
        self.assertTrue(all(result["score"] == 1 for result in results))
        self.assertEqual(sorted(seen), list(range(32)))
        self.assertEqual(checker.statistics(), {"executions": 32, "active_containers": 0,
                                               "peak_containers": 4, "maximum_containers": 4})


IMAGE = os.environ.get("ROLLBACK_V9_DOCKER_IMAGE")


@unittest.skipUnless(IMAGE, "set ROLLBACK_V9_DOCKER_IMAGE for actual isolated container checks")
class DockerRuntimeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.checker = runtime.PatchRuntime(IMAGE)
        cls.audit = cls.checker.audit()

    def test_two_files_batch_inputs_typed_outputs_and_true_mismatch(self):
        source = candidate("from rules import offset\ndef solve(case):\n    return case['value'] + offset\n", "offset = 2\n")
        tests = [{"id": str(i), "input": {"value": i}, "expected": i + 2} for i in (1, 3, 9)]
        self.assertEqual(self.checker.check(source, tests)["status"], "public_pass")
        source["files"][1]["text"] = "offset = 1\n"
        result = self.checker.check(source, tests)
        self.assertEqual((result["status"], result["passed_count"]), ("public_mismatch", 0))

    def test_both_file_syntax_errors_are_classified_without_wrong_answer_eligibility(self):
        for key in ("engine", "rules"):
            source = candidate(**{key: "def broken(:\n"})
            result = self.checker.check(source, [{"id": "one", "input": 1, "expected": 1}])
            self.assertEqual(result["status"], "syntax_error")

    def test_module_runtime_error_is_distinct_and_private_error_has_no_details(self):
        source = candidate("raise RuntimeError('PRIVATE_FAILURE_CANARY')\n")
        tests = [{"id": "PRIVATE_TEST_ID", "input": "PRIVATE_INPUT_CANARY", "expected": 1}]
        result = self.checker.check(source, tests)
        self.assertEqual(result["status"], "runtime_error")
        private = self.checker.check(source, tests, public=False)
        self.assertEqual(private["disposition"], "runtime_error")
        self.assertNotIn("CANARY", wire(private))
        self.assertNotIn("PRIVATE_TEST_ID", wire(private))

    def test_concurrent_suites_keep_separate_scratch_and_inputs(self):
        source = candidate("import pathlib,time\ndef solve(case):\n    p=pathlib.Path('/scratch/unique')\n    assert not p.exists()\n    p.write_text(str(case))\n    time.sleep(0.2)\n    assert p.read_text()==str(case)\n    return case\n")
        def check(index):
            return self.checker.check(source, [{"id": str(index), "input": index, "expected": index}])
        with ThreadPoolExecutor(max_workers=8) as pool:
            results = list(pool.map(check, range(8)))
        self.assertTrue(all(result["score"] == 1 for result in results))
        self.assertEqual(self.checker.statistics()["active_containers"], 0)
        self.assertLessEqual(self.checker.statistics()["peak_containers"], 4)


if __name__ == "__main__":
    unittest.main()
