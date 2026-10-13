"""Independent examples, public/private separation and authored-project checks.

These default tests never execute source strings. Actual reference and mutant
execution is an opt-in Docker gate below, separate from host oracle tests.
"""

import ast
from collections import Counter
from copy import deepcopy
import difflib
import os
import unittest

from experiments.dependency_memory.rollback_patch_v9.tasks import (
    FAMILIES, FILES, FOCUS_CATEGORIES, PRIVATE_CASES, PUBLIC_CASES,
    canonical, generate, initial_candidate, oracle_intervals, oracle_ledger,
    oracle_resolver, oracle_routes, public_check, public_task,
    reference_candidate, sha, terminal_check, verify_tasks,
)


class AuthoredPatchTaskTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tasks = generate()

    def test_fixed_balanced_calibration_and_independent_expected_values(self):
        self.assertEqual(len(self.tasks), 16)
        self.assertEqual(Counter(task["family"] for task in self.tasks), dict.fromkeys(FAMILIES, 4))
        checked = verify_tasks(self.tasks)
        self.assertEqual(checked["public_cases"], 96)
        self.assertEqual(checked["private_cases"], 288)
        self.assertTrue(checked["passed"])
        self.assertEqual(checked["model_calls"], 0)
        self.assertFalse(checked["candidate_code_executed_on_host"])

    def test_generation_reproduces_and_splits_have_distinct_instances(self):
        self.assertEqual(self.tasks, generate())
        held = generate(split="study", per_family=1)
        self.assertFalse({task["task_id"] for task in held} & {task["task_id"] for task in self.tasks})
        self.assertFalse({task["evaluator"]["seed"] for task in held}
                         & {task["evaluator"]["seed"] for task in self.tasks})
        self.assertTrue(all(task["split"] == "study" for task in held))
        for task in self.tasks:
            self.assertEqual(task["sha256"], sha({key: value for key, value in task.items() if key != "sha256"}))
            public = {sha(test["input"]) for test in task["public_tests"]}
            private = {sha(test["input"]) for test in task["evaluator"]["reserved_tests"]}
            self.assertEqual(len(public), PUBLIC_CASES)
            self.assertEqual(len(private), PRIVATE_CASES)
            self.assertFalse(public & private)

    def test_every_family_varies_explicit_policy_and_actual_public_instance(self):
        for family in FAMILIES:
            tasks = [task for task in self.tasks if task["family"] == family]
            self.assertEqual(len({canonical(task["contract"]["policy"]) for task in tasks}), 4)
            self.assertEqual(len({canonical(task["public_tests"]) for task in tasks}), 4)
            self.assertEqual(len({canonical(task["base_files"]) for task in tasks}), 4)

    def test_two_substantive_modules_and_reference_grammar_without_host_execution(self):
        for task in self.tasks:
            self.assertEqual([row["path"] for row in task["base_files"]], list(FILES))
            self.assertEqual([row["path"] for row in task["evaluator"]["reference_files"]], list(FILES))
            self.assertEqual(initial_candidate(task)["files"], task["base_files"])
            self.assertEqual(reference_candidate(task)["files"], task["evaluator"]["reference_files"])
            for files in (task["base_files"], task["evaluator"]["reference_files"]):
                source_bytes = sum(len(row["text"].encode("utf-8")) for row in files)
                self.assertGreater(source_bytes, 1000)
                self.assertLessEqual(source_bytes, task["contract"]["source_limit_utf8_bytes"])
                for row in files:
                    parsed = ast.parse(row["text"], filename=row["path"])
                    self.assertGreaterEqual(len(row["text"].splitlines()), 12)
                    self.assertTrue(any(isinstance(node, ast.FunctionDef) for node in parsed.body))
            before = {row["path"]: row["text"] for row in task["base_files"]}
            after = {row["path"]: row["text"] for row in task["evaluator"]["reference_files"]}
            changed = sum(1 for path in FILES for line in difflib.ndiff(before[path].splitlines(), after[path].splitlines())
                          if line[:2] in {"- ", "+ "} and line[2:].strip())
            self.assertGreaterEqual(changed, 4)

    def test_public_projection_is_complete_allowlisted_and_independent_copy(self):
        original = deepcopy(self.tasks[0])
        original["evaluator"]["secret_extra"] = "PRIVATE_ONLY_CANARY"
        original["future_internal_metadata"] = "PRIVATE_ONLY_CANARY"
        actor = public_task(original)
        self.assertEqual(set(actor), {"task_id", "family", "contract", "base_files", "public_tests"})
        self.assertNotIn("PRIVATE_ONLY_CANARY", canonical(actor))
        self.assertEqual(actor["contract"]["lesson_focus_categories"], list(FOCUS_CATEGORIES))
        self.assertEqual(actor["public_tests"], original["public_tests"])
        self.assertEqual(actor["base_files"], original["base_files"])
        actor["base_files"][0]["text"] = "mutated actor copy"
        actor["public_tests"][0]["expected"] = "mutated actor copy"
        self.assertNotEqual(actor["base_files"], original["base_files"])
        self.assertNotEqual(actor["public_tests"], original["public_tests"])

    def test_public_and_terminal_runtime_routes_never_return_private_detail(self):
        task = self.tasks[0]
        seen = []

        class RecordingRuntime:
            def check(self, candidate, tests, *, public=True):
                seen.append((candidate, tests, public))
                if public:
                    return {"status": "public_mismatch", "check_id": tests[0]["id"],
                            "expected": tests[0]["expected"], "observed": None}
                return {"score": 0, "disposition": "test_failure", "private_expected": "DO_NOT_RETURN",
                        "private_input": "DO_NOT_RETURN", "private_stdout": "DO_NOT_RETURN"}

        runtime, proposed = RecordingRuntime(), initial_candidate(task)
        receipt = public_check(task, proposed, runtime)
        grade = terminal_check(task, proposed, runtime)
        self.assertEqual(receipt["status"], "public_mismatch")
        self.assertEqual(grade, {"score": 0, "disposition": "test_failure"})
        self.assertEqual(seen[0], (proposed, task["public_tests"], True))
        self.assertEqual(seen[1], (proposed, task["public_tests"] + task["evaluator"]["reserved_tests"], False))
        self.assertNotIn("DO_NOT_RETURN", canonical(grade))

    def test_ledger_filter_priority_tombstone_and_ordered_rounding(self):
        data = {"events": [{"id": "tx-a", "price": 10, "revision": 5, "sequence": 1},
                           {"id": "tx-a", "price": 20, "revision": 1, "sequence": 2},
                           {"id": "tx-a", "price": 99, "revision": 99, "sequence": 100}],
                "cutoff": 2, "rounding": "floor", "opening": {"empty|USD": 0}}
        p = {"revision_priority": "revision_first", "tax_base": "discounted"}
        self.assertEqual(oracle_ledger(data, p), {"balances": {"empty|USD": 0, "default|USD": 10}})
        p["revision_priority"] = "sequence_first"
        self.assertEqual(oracle_ledger(data, p)["balances"]["default|USD"], 20)
        data["events"].insert(2, {"id": "tx-a", "price": 30, "revision": 1, "sequence": 2, "void": True})
        self.assertEqual(oracle_ledger(data, p), {"balances": {"empty|USD": 0}})
        data = {"events": [{"price": 15, "discount_bp": 5000, "tax_bp": 1750, "kind": "refund"}], "rounding": "half_up"}
        self.assertEqual(oracle_ledger(data, p), {"balances": {"default|USD": -9}})
        p["tax_base"] = "original"
        self.assertEqual(oracle_ledger(data, p), {"balances": {"default|USD": -11}})

    def test_resolver_backtracking_cycles_absent_pins_and_objective(self):
        data = {"packages": {
            "a": [{"version": 1, "deps": [{"name": "b", "min": 1, "max": 1}]},
                  {"version": 2, "deps": [{"name": "b", "min": 2, "max": 2}]}],
            "b": [{"version": 1}, {"version": 2, "deps": [{"name": "a", "min": 1, "max": 2}]}],
            "z": [{"version": 3}]}, "roots": {"a": [1, 2]}, "pins": {"z": 3}}
        p = {"preference": "maximum", "name_order": "ascending"}
        self.assertEqual(oracle_resolver(data, p), {"versions": {"a": 1, "b": 1}})
        data["packages"]["b"][1]["deps"] = []
        self.assertEqual(oracle_resolver(data, p), {"versions": {"a": 2, "b": 2}})
        p["preference"] = "minimum"
        self.assertEqual(oracle_resolver(data, p), {"versions": {"a": 1, "b": 1}})
        data["roots"] = {}
        self.assertEqual(oracle_resolver(data, p), {"versions": {}})

    def test_resolver_intersection_and_conditional_feature(self):
        data = {"packages": {
            "a": [{"version": 1, "deps": [{"name": "c", "min": 1, "max": 1}]}],
            "b": [{"version": 1, "deps": [{"name": "c", "min": 2, "max": 2, "feature": "extra"}]}],
            "c": [{"version": 1}, {"version": 2}]}, "roots": {"a": [1, 1], "b": [1, 1]}}
        p = {"preference": "maximum", "name_order": "descending"}
        self.assertEqual(oracle_resolver(data, p), {"versions": {"c": 1, "b": 1, "a": 1}})
        data["features"] = ["extra"]
        self.assertEqual(oracle_resolver(data, p), {"error": "unsatisfiable"})

    def test_intervals_exact_count_negative_values_endpoint_ties_and_capacity(self):
        data = {"jobs": [{"id": "a", "start": 0, "end": 2, "value": -2, "group": "g"},
                         {"id": "b", "start": 2, "end": 4, "value": -1, "group": "g"},
                         {"id": "c", "start": 0, "end": 4, "value": 8, "group": "h"}], "k": 2}
        p = {"capacity": 1, "tie": "smallest"}
        self.assertEqual(oracle_intervals(data, p), {"selected": ["a", "b"], "value": -3})
        p["capacity"] = 2
        self.assertEqual(oracle_intervals(data, p), {"selected": ["b", "c"], "value": 7})
        data["mandatory"] = ["a"]
        data["quotas"] = {"g": [2, 2]}
        self.assertEqual(oracle_intervals(data, p), {"selected": ["a", "b"], "value": -3})
        data["blocked"] = ["a"]
        self.assertEqual(oracle_intervals(data, p), {"error": "impossible"})
        data = {"jobs": [{"id": x, "start": 0, "end": 1, "value": 5, "group": "g"} for x in ("a", "b")], "k": 1}
        self.assertEqual(oracle_intervals(data, p), {"selected": ["a"], "value": 5})
        p["tie"] = "largest"
        self.assertEqual(oracle_intervals(data, p), {"selected": ["b"], "value": 5})
        self.assertEqual(oracle_intervals({"jobs": [], "k": 0}, p), {"selected": [], "value": 0})

    def test_routes_waiting_close_boundary_coupon_policy_and_revisits(self):
        edge = lambda u, v, d, opening=0, close=20, discount=0: {
            "u": u, "v": v, "duration": d, "open": opening, "close": close, "discount": discount}
        p = {"coupon_rule": "at_most", "minimum_duration": 1}
        data = {"n": 3, "source": 0, "target": 2, "start": 0, "deadline": 8, "coupons": 1,
                "required": [0, 1], "edges": [edge(0, 1, 3, discount=9), edge(1, 2, 3, opening=5, close=6)]}
        self.assertEqual(oracle_routes(data, p), {"arrival": 8})
        data["edges"][1]["close"] = 5
        self.assertEqual(oracle_routes(data, p), {"arrival": None})
        data = {"n": 2, "source": 0, "target": 0, "start": 0, "deadline": 6, "coupons": 1,
                "required": [], "edges": [edge(0, 1, 3), edge(1, 0, 3)]}
        self.assertEqual(oracle_routes(data, p), {"arrival": 0})
        p["coupon_rule"] = "exact"
        self.assertEqual(oracle_routes(data, p), {"arrival": 6})
        data["required"] = [1]
        self.assertEqual(oracle_routes(data, p), {"arrival": 6})

    def test_verifier_detects_changed_expectation_even_with_updated_task_hash(self):
        task = deepcopy(self.tasks[0])
        task["evaluator"]["reserved_tests"][0]["expected"] = {"wrong": "value"}
        task["sha256"] = sha({key: value for key, value in task.items() if key != "sha256"})
        with self.assertRaisesRegex(ValueError, "independent expected output"):
            verify_tasks([task])
        for args in ({"split": "unknown"}, {"per_family": 0}, {"per_family": True},
                     {"per_family": 65}, {"split": "calibration", "per_family": 5}):
            with self.subTest(args=args), self.assertRaises(ValueError):
                generate(**args)


@unittest.skipUnless(os.environ.get("ROLLBACK_V9_DOCKER_IMAGE"), "explicit pinned Docker image required; no host execution fallback")
class AuthoredPatchDockerTests(unittest.TestCase):
    def test_all_sixteen_references_match_independent_oracles_and_bases_fail_publicly(self):
        from experiments.dependency_memory.rollback_patch_v9.runtime import PatchRuntime
        runtime = PatchRuntime(os.environ["ROLLBACK_V9_DOCKER_IMAGE"])
        runtime.audit()
        for task in generate():
            with self.subTest(task=task["task_id"]):
                self.assertEqual(public_check(task, reference_candidate(task), runtime)["status"], "public_pass")
                self.assertEqual(terminal_check(task, reference_candidate(task), runtime)["score"], 1)
                self.assertEqual(public_check(task, initial_candidate(task), runtime)["status"], "public_mismatch")


if __name__ == "__main__":
    unittest.main()
