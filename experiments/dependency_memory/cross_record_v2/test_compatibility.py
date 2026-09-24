"""Decoder reachability and explicit coverage limits for the versioned checker."""
from itertools import combinations
import json
from pathlib import Path
import unittest

from experiments.dependency_memory.cross_record import memory as frozen
from experiments.dependency_memory.schema_transfer import memory as table
from .compatibility import (admit_or_project, certify_child, certify_parent,
                            select_by_owner)
from .replay import OUTPUT, replay


class CompatibilityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        path = Path(__file__).resolve().parents[1] / "cross_record/fixtures/development-package-61011.json"
        cls.case = json.loads(path.read_text(encoding="utf-8"))

    def test_every_future_owner_pair_survives_both_boundaries(self):
        case = self.case
        parent, _ = frozen.project(case["tool_schemas"], case["tool_results"])
        certificate = certify_parent(parent, case["tool_schemas"], case["tool_results"])
        self.assertTrue(certificate["passed"], certificate)
        schema, source = frozen.join(case["tool_schemas"], case["tool_results"])
        owner = certificate["owner_path"]
        source_by_owner = {row[owner]: row for row in source}
        self.assertEqual(7, len(source_by_owner))
        for pair in combinations(source_by_owner, 2):
            child = select_by_owner(parent, owner, pair)
            self.assertLessEqual(len(child.encode()), 2600)
            self.assertTrue(certify_child(child, parent, pair, owner, case["tool_schemas"])["passed"])
            decoded = table.decode(child)
            self.assertEqual(list(pair), [row[owner] for row in decoded])
            for row in decoded:
                for path in json.loads(child)["f"]:
                    self.assertEqual(table.value_at(source_by_owner[row[owner]], path), row[path])

    def test_repeated_component_join_keys_expose_frozen_checker_mismatch(self):
        case = self.case
        parent, _ = frozen.project(case["tool_schemas"], case["tool_results"])
        data = json.loads(parent)
        # This is the model-output shape reported in six frozen evaluation cases.
        for component in sorted(set(case["tool_schemas"]) - {"root"}):
            data["f"].append(component + ".workflow_key")
            for row in data["r"]:
                row.append(row[data["f"].index("workflow_key")])
        proposal = json.dumps(data, separators=(",", ":"))
        self.assertTrue(frozen.check(proposal, case["tool_schemas"], case["tool_results"])["passed"])
        certificate = certify_parent(proposal, case["tool_schemas"], case["tool_results"])
        self.assertFalse(certificate["passed"])
        self.assertEqual("unsupported_parent_path", certificate["reason"])
        admitted, fallback_certificate, used_fallback = admit_or_project(
            proposal, case["tool_schemas"], case["tool_results"])
        self.assertTrue(used_fallback)
        self.assertTrue(fallback_certificate["passed"])
        child = select_by_owner(admitted, fallback_certificate["owner_path"], case["candidate_ids"])
        self.assertTrue(certify_child(child, admitted, case["candidate_ids"],
                                      fallback_certificate["owner_path"], case["tool_schemas"])["passed"])

    def test_owner_selection_ignores_the_same_value_in_another_field(self):
        parent = json.dumps({"f": ["id", "other"], "r": [["alpha", "x"], ["beta", "alpha"],
                                                       ["gamma", "y"]]}, separators=(",", ":"))
        with self.assertRaises(ValueError):
            table.select(parent, ["alpha", "gamma"])
        child = select_by_owner(parent, "id", ["alpha", "gamma"])
        self.assertEqual(["alpha", "gamma"], [row["id"] for row in table.decode(child)])

    def test_child_cannot_introduce_a_path_absent_from_parent(self):
        case = self.case
        parent, _ = frozen.project(case["tool_schemas"], case["tool_results"])
        owner = certify_parent(parent, case["tool_schemas"], case["tool_results"])["owner_path"]
        child = json.loads(select_by_owner(parent, owner, case["candidate_ids"]))
        child["f"].append("scan.workflow_key")
        for row in child["r"]:
            row.append("made-up-alias")
        verdict = certify_child(json.dumps(child), parent, case["candidate_ids"],
                                owner, case["tool_schemas"])
        self.assertFalse(verdict["passed"])
        self.assertEqual("unsupported_child_path", verdict["reason"])

    def test_id_certificate_does_not_claim_state_semantics(self):
        case = self.case
        parent, _ = frozen.project(case["tool_schemas"], case["tool_results"])
        data = json.loads(parent)
        column = data["f"].index("scan.state")
        data["r"][0][column] = "fail" if data["r"][0][column] != "fail" else "pass"
        changed = json.dumps(data, separators=(",", ":"))
        self.assertTrue(certify_parent(changed, case["tool_schemas"], case["tool_results"])["passed"])

    def test_schema_type_is_checked_even_when_identifiers_are_intact(self):
        case = self.case
        parent, _ = frozen.project(case["tool_schemas"], case["tool_results"])
        data = json.loads(parent)
        data["r"][0][data["f"].index("scan.state")] = {"state": "pass"}
        verdict = certify_parent(json.dumps(data), case["tool_schemas"], case["tool_results"])
        self.assertFalse(verdict["passed"])
        self.assertEqual("schema_type_or_enum", verdict["reason"])

    def test_saved_parent_diagnostic_recomputes_from_immutable_evidence(self):
        recorded = json.loads(OUTPUT.read_text(encoding="utf-8"))
        self.assertEqual(recorded, replay())
        self.assertEqual(6, sum(row["v1_id_check_passed"] and not row["v2_parent_passed"]
                                for row in recorded["cases"]))
        self.assertEqual(252, recorded["counts"]["all_owner_pairs_checked"])


if __name__ == "__main__":
    unittest.main()
