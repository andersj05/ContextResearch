"""Decoder reachability and explicit coverage limits for the versioned checker."""
from copy import deepcopy
from itertools import combinations
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from experiments.dependency_memory.cross_record import memory as frozen
from experiments.dependency_memory.schema_transfer import memory as table
from .compatibility import (admit_or_project, certify_child, certify_parent,
                            select_by_owner)
from .replay import OUTPUT, validate_saved


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

    def test_id_certificate_does_not_require_state_field_retention(self):
        case = self.case
        parent, _ = frozen.project(case["tool_schemas"], case["tool_results"])
        data = json.loads(parent)
        column = data["f"].index("scan.state")
        del data["f"][column]
        for row in data["r"]:
            del row[column]
        omitted = json.dumps(data, separators=(",", ":"))
        certificate = certify_parent(omitted, case["tool_schemas"], case["tool_results"])
        self.assertTrue(certificate["passed"], certificate)
        child = select_by_owner(omitted, certificate["owner_path"], case["candidate_ids"])
        self.assertTrue(certify_child(child, omitted, case["candidate_ids"],
                                      certificate["owner_path"], case["tool_schemas"])["passed"])

    def test_parent_certificate_requires_the_actual_child_check(self):
        # Long untyped source prose is ignored by the ID detector. A short
        # proposed replacement is schema-valid but makes child coverage unknown.
        # Merely selecting/serializing every pair misses this contract failure.
        case = self.case
        schemas, results = deepcopy(case["tool_schemas"]), deepcopy(case["tool_results"])
        schemas["root"]["properties"]["description"] = {"type": "string"}
        for item in results:
            if item["tool"] == "root":
                item["data"]["description"] = "long public diagnostic context " * 4
        parent, _ = frozen.project(schemas, results)
        data = json.loads(parent)
        data["f"].append("description")
        for row in data["r"]:
            row.append("short")
        proposal = json.dumps(data, separators=(",", ":"))
        self.assertTrue(frozen.check(proposal, schemas, results)["passed"])
        rejected = certify_parent(proposal, schemas, results)
        self.assertFalse(rejected["passed"], rejected)
        self.assertEqual("child_incompatible", rejected["reason"])
        admitted, certificate, used_fallback = admit_or_project(proposal, schemas, results)
        self.assertTrue(used_fallback)
        self.assertEqual(parent, admitted)
        owners = [row["package_id"] for row in table.decode(parent)]
        for pair in combinations(owners, 2):
            child = select_by_owner(admitted, certificate["owner_path"], pair)
            self.assertTrue(certify_child(child, admitted, pair, certificate["owner_path"],
                                          schemas)["passed"])

    def test_capacity_limits_use_the_actual_serialized_bytes(self):
        case = self.case
        parent, _ = frozen.project(case["tool_schemas"], case["tool_results"])
        data = json.loads(parent)
        # Independent table slicing and serialization, without the selector.
        pair_sizes = [len(json.dumps({"f": data["f"], "r": list(pair)},
                                     sort_keys=True, separators=(",", ":")).encode("utf-8"))
                      for pair in combinations(data["r"], 2)]
        parent_size, child_size = len(parent.encode("utf-8")), max(pair_sizes)
        exact = certify_parent(parent, case["tool_schemas"], case["tool_results"],
                               parent_cap=parent_size, child_cap=child_size)
        self.assertTrue(exact["passed"], exact)
        self.assertEqual(child_size, exact["max_child_bytes"])
        self.assertEqual("parent_capacity", certify_parent(parent, case["tool_schemas"],
                         case["tool_results"], parent_cap=parent_size - 1)["reason"])
        self.assertEqual("child_capacity", certify_parent(parent, case["tool_schemas"],
                         case["tool_results"], child_cap=child_size - 1)["reason"])
        with self.assertRaises(ValueError):
            admit_or_project(parent, case["tool_schemas"], case["tool_results"],
                             child_cap=child_size - 1)

    def test_non_string_and_invalid_unicode_proposals_fail_without_crashing(self):
        case = self.case
        parent, _ = frozen.project(case["tool_schemas"], case["tool_results"])
        owner = "package_id"
        for proposal in (None, {}, 42, b"{}", "\ud800"):
            with self.subTest(proposal_type=type(proposal).__name__):
                self.assertFalse(certify_parent(proposal, case["tool_schemas"],
                                                 case["tool_results"])["passed"])
                self.assertFalse(certify_child(proposal, parent, case["candidate_ids"],
                                                owner, case["tool_schemas"])["passed"])
                admitted, certificate, fallback = admit_or_project(
                    proposal, case["tool_schemas"], case["tool_results"])
                self.assertTrue(fallback)
                self.assertTrue(certificate["passed"])
                self.assertEqual(parent, admitted)

    def test_duplicate_json_members_are_not_a_decodable_table(self):
        case = self.case
        parent, _ = frozen.project(case["tool_schemas"], case["tool_results"])
        child = select_by_owner(parent, "package_id", case["candidate_ids"])
        for prefix in ('{"f":[],', '{"r":[],'):
            with self.subTest(prefix=prefix):
                self.assertFalse(certify_parent(prefix + parent[1:], case["tool_schemas"],
                                                 case["tool_results"])["passed"])
                self.assertFalse(certify_child(prefix + child[1:], parent,
                                 case["candidate_ids"], "package_id", case["tool_schemas"])["passed"])

    def test_nonfinite_numeric_fields_are_not_schema_numbers(self):
        case = self.case
        schemas, results = deepcopy(case["tool_schemas"]), deepcopy(case["tool_results"])
        schemas["root"]["properties"]["duration"] = {"type": "number"}
        for item in results:
            if item["tool"] == "root":
                item["data"]["duration"] = 1.0
        parent, _ = frozen.project(schemas, results)
        child = select_by_owner(parent, "package_id", case["candidate_ids"])
        self.assertTrue(certify_parent(parent, schemas, results)["passed"])
        for value in ("NaN", "Infinity", "-Infinity", "1e999"):
            with self.subTest(value=value):
                self.assertFalse(certify_parent(parent.replace("1.0", value), schemas, results)["passed"])
                self.assertFalse(certify_child(child.replace("1.0", value), parent,
                                 case["candidate_ids"], "package_id", schemas)["passed"])

    def test_duplicate_missing_and_unrelated_owners_fail(self):
        case = self.case
        parent, _ = frozen.project(case["tool_schemas"], case["tool_results"])
        data = json.loads(parent)
        for rows in (data["r"][:-1], data["r"] + [data["r"][0]]):
            proposal = json.dumps({"f": data["f"], "r": rows})
            self.assertFalse(certify_parent(proposal, case["tool_schemas"], case["tool_results"])["passed"])
        first = case["candidate_ids"][0]
        for candidates in ([first], [first, first], [first, "missing"], [first, 7]):
            with self.subTest(candidates=candidates), self.assertRaises(ValueError):
                select_by_owner(parent, "package_id", candidates)

    def test_field_and_row_permutations_preserve_the_handoff(self):
        case = self.case
        parent, _ = frozen.project(case["tool_schemas"], case["tool_results"])
        data = json.loads(parent)
        permuted = json.dumps({"f": data["f"][::-1],
                               "r": [row[::-1] for row in data["r"][::-1]]}, separators=(",", ":"))
        self.assertTrue(certify_parent(permuted, case["tool_schemas"], case["tool_results"])["passed"])
        expected = {row["package_id"]: row for row in table.decode(parent)}
        for pair in combinations(expected, 2):
            child = select_by_owner(permuted, "package_id", pair)
            self.assertEqual([expected[value] for value in pair], table.decode(child))
            self.assertTrue(certify_child(child, permuted, pair, "package_id",
                                          case["tool_schemas"])["passed"])

    def test_saved_parent_diagnostic_recomputes_from_immutable_evidence(self):
        recorded = json.loads(OUTPUT.read_text(encoding="utf-8"))
        self.assertEqual(recorded, validate_saved())
        self.assertEqual(6, sum(row["v1_id_check_passed"] and not row["v2_parent_passed"]
                                for row in recorded["cases"]))
        self.assertEqual(252, recorded["counts"]["all_owner_pairs_checked"])

    def test_saved_replay_validation_rejects_missing_and_changed_results(self):
        recorded = json.loads(OUTPUT.read_text(encoding="utf-8"))
        with TemporaryDirectory() as directory:
            output = Path(directory) / "replay.json"
            with self.assertRaises(FileNotFoundError):
                validate_saved(output)
            recorded["counts"]["all_owner_pairs_checked"] += 1
            output.write_text(json.dumps(recorded), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "differs from source evidence"):
                validate_saved(output)


if __name__ == "__main__":
    unittest.main()
