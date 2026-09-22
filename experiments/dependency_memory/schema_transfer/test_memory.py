"""Development-only invariant tests for the generic certificate."""
import json
import unittest

from .casebook import DEV, DEV_SEEDS, make_case
from .memory import check, decode, project, retained_schema, select, selected


class GenericMemoryTests(unittest.TestCase):
    def test_development_projections_fit_and_certify_twice(self):
        for family in DEV:
            for seed in DEV_SEEDS:
                case = make_case(family, seed, "development")
                parent, _ = project(case["tool_schema"], case["tool_results"])
                self.assertTrue(check(parent, case["tool_schema"], case["tool_results"])["passed"])
                child, _ = select(parent, case["candidate_ids"])
                chosen = decode(child)
                expected = [row for row in decode(parent) if case["candidate_ids"][0] in row.values() or
                            case["candidate_ids"][1] in row.values()]
                self.assertTrue(check(child, retained_schema(case["tool_schema"], parent), expected)["passed"])
                self.assertEqual(len(chosen), 2)

    def test_exact_identity_and_owner_relationship_are_distinct(self):
        case = make_case("escrow", DEV_SEEDS[0], "development")
        schema, source = case["tool_schema"], case["tool_results"]
        parent, _ = project(schema, source)
        parsed = json.loads(parent)
        owner = parsed["f"].index("invoice_id")
        scoped = parsed["f"].index("authorization.for_receipt")
        altered = json.loads(parent)
        altered["r"][0][owner] = "f" * 16
        self.assertFalse(check(json.dumps(altered), schema, source)["exact_ids"])
        swapped = json.loads(parent)
        swapped["r"][0][scoped], swapped["r"][1][scoped] = swapped["r"][1][scoped], swapped["r"][0][scoped]
        verdict = check(json.dumps(swapped), schema, source)
        self.assertTrue(verdict["exact_ids"])
        self.assertFalse(verdict["relationships"])
        self.assertFalse(verdict["passed"])

    def test_unstructured_and_unknown_coverage_fail_closed(self):
        case = make_case("package", DEV_SEEDS[0], "development")
        self.assertFalse(check("The signature looks good", case["tool_schema"], case["tool_results"])["passed"])
        schema = {"type": "object", "properties": {"record_id": {"type": "string", "pattern": "^[a-f0-9]{16}$"},
                   "mystery": {"type": "string"}}}
        with self.assertRaisesRegex(ValueError, "Unknown coverage"):
            selected(schema, [{"record_id": "a" * 16, "mystery": "short"}])


if __name__ == "__main__":
    unittest.main()
