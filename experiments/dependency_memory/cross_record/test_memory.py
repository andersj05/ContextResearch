"""Scientific invariants for cross-record joining, scope, and retained facts."""
import json
from pathlib import Path
import unittest

from experiments.dependency_memory.schema_transfer import memory as base
from . import analyze, direct, memory


class MemoryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        path = Path(__file__).parent / "fixtures/development-package-61011.json"
        cls.case = json.loads(path.read_text(encoding="utf-8"))

    def test_order_independent_join_and_complete_projection(self):
        case = self.case
        parent, _ = memory.project(case["tool_schemas"], case["tool_results"])
        reversed_parent, _ = memory.project(case["tool_schemas"], list(reversed(case["tool_results"])))
        self.assertEqual(parent, reversed_parent)
        self.assertTrue(memory.check(parent, case["tool_schemas"], case["tool_results"])["passed"])
        child, _ = memory.select(parent, case["candidate_ids"])
        self.assertTrue(memory.check_child(child, parent, case["candidate_ids"], case["tool_schemas"])[0]["passed"])
        for future in case["futures"]:
            self.assertEqual("sufficient", analyze.information_sufficiency(child, case, future))
        authored, _ = direct.project(case["family"], case["tool_schemas"], case["tool_results"])
        authored_child, _ = direct.child(authored, case["candidate_ids"])
        for future in case["futures"]:
            self.assertEqual("sufficient", analyze.information_sufficiency(authored_child, case, future))

    def test_identifier_swap_preserves_bag_but_breaks_relationships(self):
        case = self.case
        parent, _ = memory.project(case["tool_schemas"], case["tool_results"])
        data = json.loads(parent)
        column = data["f"].index("scan.subject_digest")
        data["r"][0][column], data["r"][1][column] = data["r"][1][column], data["r"][0][column]
        verdict = memory.check(json.dumps(data), case["tool_schemas"], case["tool_results"])
        self.assertTrue(verdict["exact_ids"])
        self.assertFalse(verdict["relationships"])

    def test_missing_component_is_unknown_not_certified(self):
        case = self.case
        missing = case["tool_results"][1:]
        with self.assertRaises(ValueError):
            memory.project(case["tool_schemas"], missing)

    def test_identifier_corruption_is_detected(self):
        case = self.case
        parent, _ = memory.project(case["tool_schemas"], case["tool_results"])
        data = json.loads(parent)
        column = data["f"].index("scan.record_id")
        data["r"][0][column] = "0000000000000000"
        verdict = memory.check(json.dumps(data), case["tool_schemas"], case["tool_results"])
        self.assertFalse(verdict["exact_ids"])
        self.assertFalse(verdict["passed"])


if __name__ == "__main__":
    unittest.main()
