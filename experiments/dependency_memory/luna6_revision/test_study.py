import itertools
import json
from decimal import Decimal
import unittest

from . import study
from .protocol import request_bytes, smoke_request
from .profile import wire_body_byte_bound
from .transport import usage_cost


class StudyChecks(unittest.TestCase):
    def test_independent_gate_truth_table(self):
        for approval, scope, unit, integ, optional, blocker in itertools.product((False, True), repeat=6):
            row = {"artifact": "a", "approval": "a" if approval else "old", "ci_artifact": "a" if scope else "old",
                   "required": ["unit", "integ"], "ci": {"unit": "pass" if unit else "fail", "integ": "pass" if integ else "fail", "perf": "pass" if optional else "fail"},
                   "blockers": ["B"] if blocker else []}
            observed = study.expected(row, {"kind": "note", "value": "irrelevant"})
            allowed = approval and scope and unit and integ and not blocker
            self.assertEqual(observed["action"], "release" if allowed else "hold")
            self.assertEqual(len(observed["work"]), (not approval) + (not (scope and unit)) + (not (scope and integ)) + blocker)

    def test_projection_sufficiency_and_capacity(self):
        for f in study.fixtures():
            parent = study.projection(f["records"])
            self.assertLessEqual(len(parent.encode()), study.PARENT_CAP)
            child_records = [r for r in study.decode(parent) if r["service"] in f["pair"]]
            child = study.projection(child_records)
            self.assertLessEqual(len(child.encode()), study.CHILD_CAP)
            decoded = {r["service"]: r for r in study.decode(child)}
            for future in f["futures"]:
                original = next(r for r in f["records"] if r["service"] == future["target"])
                self.assertEqual(study.expected(original, future["event"]), study.expected(decoded[future["target"]], future["event"]))

    def test_repairs_use_available_view_and_are_idempotent(self):
        f = study.fixtures()[0]
        repaired, check = study.repair("all ready", f["records"], study.PARENT_CAP)
        same, second = study.repair(repaired, study.decode(repaired), study.PARENT_CAP)
        self.assertTrue(check["changed"])
        self.assertFalse(second["changed"])
        self.assertEqual(repaired, same)
        with self.assertRaises(ValueError):
            study.repair("", f["records"], 1)

    def test_late_events_include_directional_and_irrelevant_controls(self):
        flips = set()
        for f in study.fixtures():
            for i in range(0, 4, 2):
                a, b = f["futures"][i:i+2]
                row = next(r for r in f["records"] if r["service"] == a["target"])
                first, second = study.expected(row, a["event"]), study.expected(row, b["event"])
                self.assertNotEqual(first["action"], second["action"])
                flips.add((first["action"], second["action"]))
        self.assertEqual(flips, {("release", "hold"), ("hold", "release")})

    def test_wire_bounds_and_disclosure(self):
        for f in study.fixtures():
            r = study.memory_request("parent", "structured", {"release_tool_history": f["records"]}, study.PARENT_CAP)
            self.assertNotIn('"seed"', request_bytes(r).decode())
            self.assertNotIn("candidate_services", request_bytes(r).decode())
            self.assertLessEqual(wire_body_byte_bound(r), 32768)
            for future in f["futures"]:
                self.assertLessEqual(wire_body_byte_bound(study.execute_request(study.compact(f["records"]), future)), 32768)

    def test_utf8_prefix_budget(self):
        retained, audit = study.admit({"memory": "aa€b"}, 4)
        self.assertEqual(retained, "aa")
        self.assertTrue(audit["clipped"])
        self.assertEqual(audit["admitted_bytes"], 2)

    def test_grader_rejects_missing_and_duplicate_obligations(self):
        truth = {"action": "hold", "artifact": "a", "work": ["approval"]}
        self.assertTrue(study.grade(truth, truth)["success"])
        for response in (None, {}, {**truth, "work": []}, {**truth, "artifact": "wrong"}, {**truth, "work": ["approval", "approval"]}):
            self.assertFalse(study.grade(response, truth)["success"])
        self.assertTrue(study.grade({**truth, "action": "release"}, truth)["unsafe_release"])

    def test_reasoning_charged_once_and_bad_usage_rejected(self):
        usage = {"inputTokens": 1000, "cachedInputTokens": 200, "outputTokens": 100, "reasoningOutputTokens": 90, "totalTokens": 1100}
        self.assertEqual(usage_cost(usage), Decimal(".00330"))
        self.assertEqual(usage_cost({**usage, "reasoningOutputTokens": 0}), usage_cost(usage))
        for change in ({"inputTokens": -1}, {"cachedInputTokens": 1001}, {"reasoningOutputTokens": 101}, {"totalTokens": 1}, {"outputTokens": None}):
            with self.assertRaises(ValueError):
                usage_cost({**usage, **change})


if __name__ == "__main__":
    unittest.main()
