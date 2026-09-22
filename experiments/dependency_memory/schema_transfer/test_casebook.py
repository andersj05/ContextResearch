import json
from hashlib import sha256
from pathlib import Path
import unittest

from .casebook import DEV, EVAL, DEV_SEEDS, EVAL_SEEDS, make_case, truth, terminal


class FrozenCasebookTests(unittest.TestCase):
    def test_split_hashes_and_no_custom_role_annotations(self):
        folder = Path(__file__).parent / "fixtures"
        manifest = json.loads((folder / "manifest.json").read_text())
        self.assertEqual(len(manifest["cases"]), 10)
        self.assertEqual(sum(item["split"] == "evaluation" for item in manifest["cases"]), 6)
        for item in manifest["cases"]:
            raw = (folder / item["file"]).read_bytes()
            self.assertEqual(len(raw), item["bytes"])
            self.assertEqual(sha256(raw).hexdigest(), item["sha256"])
            case = json.loads(raw)
            self.assertNotIn("x-reference", json.dumps(case["tool_schema"]))
            self.assertNotIn("x-ephemeral", json.dumps(case["tool_schema"]))
            self.assertEqual(len(case["candidate_ids"]), 2)
            self.assertEqual(len(case["futures"]), 3)
            self.assertTrue(all(future["target"] in case["candidate_ids"] for future in case["futures"]))

    def test_distinct_schema_structures_and_terminal_patterns(self):
        expected = {"escrow": ["hold", "submit", "hold"],
                    "package": ["hold", "publish", "hold"],
                    "retry_queue": ["retry", "close", "hold"],
                    "ci_promotion": ["hold", "promote", "hold"],
                    "data_pipeline": ["hold", "publish", "hold"]}
        for split, families, seeds in (("development", DEV, DEV_SEEDS), ("evaluation", EVAL, EVAL_SEEDS)):
            for family in families:
                for seed in seeds:
                    case = make_case(family, seed, split)
                    self.assertEqual([truth(case, future)["action"] for future in case["futures"]], expected[family])
                    self.assertEqual(len({row[next(iter(row))] for row in case["tool_results"]}), 7)

    def test_independent_scope_and_state_controls(self):
        ci = {"deployment_slot": "slot", "build": {"digest": "new", "channel": "stable"},
              "authorization": {"approved_digest": "old", "state": "approved"},
              "verification": {"subject": "new", "unit": "pass", "integration": "pass"},
              "handoff": {"environment": "prod"}}
        self.assertEqual(terminal("ci_promotion", ci, {"path": "note", "value": "x"})["work"], ["approval_scope"])
        self.assertEqual(terminal("ci_promotion", ci, {"path": "authorization.approved_digest", "value": "new"})["action"], "promote")
        retry = {"request_token": "r", "dispatch": {"state": "not_sent", "attempt_uuid": "a"},
                 "result": {"attempt_uuid": "other", "state": "failed"},
                 "billing": {"for_attempt": "other", "state": "none"},
                 "retry_policy": {"retry_allowed": False}}
        self.assertEqual(terminal("retry_queue", retry, {"path": "note", "value": "x"}),
                         {"action": "submit", "target_id": "r", "work": []})
        retry["dispatch"]["state"] = "sent"
        self.assertEqual(terminal("retry_queue", retry, {"path": "note", "value": "x"})["work"],
                         ["billing_scope", "result_scope"])
        data = {"extract": {"state": "pass", "output_dataset": "raw"},
                "transform": {"state": "pass", "input_dataset": "old", "output_dataset": "clean"},
                "load": {"state": "pass", "input_dataset": "clean", "output_dataset": "table"},
                "quality": {"state": "pass", "subject_dataset": "table"},
                "consent": {"state": "approved", "approved_output": "table"}}
        self.assertEqual(terminal("data_pipeline", data, {"path": "note", "value": "x"})["work"], ["link_transform"])


if __name__ == "__main__":
    unittest.main()
