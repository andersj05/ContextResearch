"""Composition, independent oracle, isolation and information-boundary checks."""

import ast
from collections import Counter
from copy import deepcopy
import unittest

from . import tasks


class CompositePatchTaskTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cohort = tasks.generate()

    def test_fixed_cohort_and_independent_composed_expectations(self):
        self.assertEqual(len(self.cohort), 16)
        self.assertEqual(Counter(task["family"] for task in self.cohort), dict.fromkeys(tasks.FAMILIES, 4))
        report = tasks.verify_tasks(self.cohort)
        self.assertTrue(report["passed"])
        self.assertEqual(report["public_cases"], 96)
        self.assertEqual(report["private_cases"], 288)
        self.assertEqual(report["component_case_comparisons"], 3072)
        self.assertEqual(report["unique_public_contexts"], 16)
        self.assertFalse(report["candidate_code_executed_on_host"])

    def test_factory_namespaces_and_real_large_project_sources(self):
        for task in self.cohort:
            for files in (task["base_files"], task["evaluator"]["reference_files"]):
                source = {row["path"]: row["text"] for row in files}
                self.assertGreater(sum(len(text.encode()) for text in source.values()), 14000)
                self.assertLessEqual(sum(len(text.encode()) for text in source.values()), tasks.SOURCE_BYTES)
                tree = ast.parse(source["rules.py"])
                factories = [node for node in tree.body if isinstance(node, ast.FunctionDef)]
                self.assertEqual(len(factories), 8)
                self.assertEqual({node.name for node in factories}, {"_build_component_" + str(i).zfill(2) for i in range(1, 9)})
                for factory in factories:
                    self.assertTrue(any(isinstance(node, ast.FunctionDef) and node.name == "solve" for node in factory.body))
                    self.assertFalse(any(isinstance(node, ast.ImportFrom) and node.module == "rules" for node in factory.body))
                    self.assertTrue(any(isinstance(node, ast.Assign) and any(isinstance(target, ast.Name) and target.id == "POLICY" for target in node.targets) for node in factory.body))
                ast.parse(source["engine.py"])

    def test_public_projection_keeps_all_components_and_excludes_evaluator(self):
        task = deepcopy(self.cohort[0])
        task["evaluator"]["canary"] = "PRIVATE_REFERENCE_CANARY"
        task["hidden_metadata"] = "PRIVATE_REFERENCE_CANARY"
        actor = tasks.public_task(task)
        self.assertEqual(set(actor), {"task_id", "family", "contract", "base_files", "public_tests"})
        self.assertNotIn("PRIVATE_REFERENCE_CANARY", tasks.canonical(actor))
        self.assertEqual(actor["contract"]["component_contracts"], task["contract"]["component_contracts"])
        self.assertEqual(actor["base_files"], task["base_files"])
        self.assertEqual(actor["public_tests"], task["public_tests"])
        self.assertNotIn("component_bindings", tasks.canonical(actor))
        actor["contract"]["component_contracts"][0]["policy"]["changed"] = True
        self.assertNotEqual(actor["contract"], task["contract"])

    def test_each_task_contains_five_leading_and_three_other_components(self):
        for task in self.cohort:
            contracts = task["contract"]["component_contracts"]
            counts = Counter(row["family"] for row in contracts)
            lead = task["family"].removeprefix("composite_")
            self.assertEqual(counts[lead], 5)
            self.assertEqual(sorted(counts.values()), [1, 1, 1, 5])
            self.assertEqual(len({row["sha256"] for row in task["evaluator"]["component_bindings"]}), 8)
            ids = {row["component_id"] for row in contracts}
            self.assertEqual(ids, {"component_" + str(i).zfill(2) for i in range(1, 9)})
            for case in task["public_tests"] + task["evaluator"]["reserved_tests"]:
                self.assertEqual(set(case["input"]), ids)
                self.assertEqual(set(case["expected"]), ids)

    def test_determinism_split_separation_and_component_pool_reuse_disclosed(self):
        self.assertEqual(self.cohort, tasks.generate())
        study = tasks.generate(split="study", seed=tasks.DEFAULT_SEED + 1, per_family=4)
        fingerprint = lambda task: tasks.sha({key: task[key] for key in ("family", "contract", "base_files", "public_tests")})
        self.assertFalse({fingerprint(task) for task in self.cohort} & {fingerprint(task) for task in study})
        self.assertFalse({row["sha256"] for task in self.cohort for row in task["evaluator"]["component_bindings"]}
                         & {row["sha256"] for task in study for row in task["evaluator"]["component_bindings"]})
        self.assertTrue(all("recur across tasks" in task["evaluator"]["provenance"] for task in self.cohort))

    def test_checker_detects_one_changed_component_answer(self):
        task = deepcopy(self.cohort[0])
        task["evaluator"]["reserved_tests"][0]["expected"]["component_08"] = {"incorrect": 1}
        task["sha256"] = tasks.sha({key: value for key, value in task.items() if key != "sha256"})
        with self.assertRaisesRegex(ValueError, "independent expected output"):
            tasks.verify_tasks([task])

    def test_private_grading_does_not_return_reserved_detail(self):
        class Runtime:
            def check(self, proposed, cases, *, public=True):
                return {"score": 1, "disposition": "correct", "private_secret": "PRIVATE_VALUE"}
        task = self.cohort[0]
        self.assertEqual(tasks.terminal_check(task, tasks.reference_candidate(task), Runtime()),
                         {"score": 1, "disposition": "correct"})

    def test_import_removal_preserves_other_imports_and_nested_semantics(self):
        source = "import itertools\nfrom rules import POLICY, allowed\nfrom collections import Counter\n\ndef solve(data):\n    return POLICY\n"
        transformed = tasks._without_rules_import(source)
        self.assertNotIn("from rules", transformed)
        self.assertIn("import itertools", transformed)
        self.assertIn("from collections import Counter", transformed)
        self.assertIn("return POLICY", transformed)
        ast.parse(transformed)

    def test_rejects_unsupported_allocations(self):
        for args in ({"split": "unknown"}, {"per_family": 0}, {"per_family": True},
                     {"per_family": 65}, {"split": "calibration", "per_family": 5}):
            with self.subTest(args=args), self.assertRaises(ValueError):
                tasks.generate(**args)


if __name__ == "__main__":
    unittest.main()
