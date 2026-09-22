import json
from decimal import Decimal
from pathlib import Path
from hashlib import sha256
import unittest
import tempfile

from .cases import DEV_SEEDS, FAMILIES, make_case, terminal, truth
from .memory import check, decode, direct, project, select
from .run import EXEC_SCHEMA, execution_request, memory_request, prepare_memories
from luna6_revision.protocol import request_bytes


class SchemaCheckTests(unittest.TestCase):
    def test_frozen_file_hashes_and_split(self):
        folder = Path(__file__).parent / "fixtures"
        manifest = json.loads((folder / "manifest.json").read_text())
        self.assertEqual(len(manifest["cases"]), 12)
        for item in manifest["cases"]:
            raw = (folder / item["file"]).read_bytes()
            self.assertEqual(sha256(raw).hexdigest(), item["sha256"])
            self.assertEqual(len(raw), item["bytes"])
        self.assertEqual(len({x["sha256"] for x in manifest["cases"]}), 12)

    def test_dev_memory_fits_and_second_boundary_uses_parent_only(self):
        for family in FAMILIES:
            for seed in DEV_SEEDS:
                case = make_case(family, seed, "development")
                auto = project(case["tool_schema"], case["tool_results"])
                self.assertTrue(check(auto, case["tool_schema"], case["tool_results"])["passed"])
                selected = select(auto, case["candidates"])
                selected_rows = [row for row in case["tool_results"] if case["candidates"][0] in str(row) or case["candidates"][1] in str(row)]
                self.assertEqual(len(selected_rows), 2)
                self.assertTrue(check(selected, case["tool_schema"], selected_rows)["passed"])
                self.assertEqual(len(decode(selected)), 2)
                self.assertEqual(len(decode(select(direct(family, case["tool_results"]), case["candidates"]))), 2)

    def test_exact_id_and_owned_reference_mutations_fail(self):
        for family in FAMILIES:
            case = make_case(family, DEV_SEEDS[0], "development")
            auto = project(case["tool_schema"], case["tool_results"])
            parsed = json.loads(auto)
            identity = next(x for x in parsed["fields"] if x.endswith("key"))
            col = parsed["fields"].index(identity)
            parsed["rows"][0][col] += "-corrupt"
            self.assertGreater(check(json.dumps(parsed), case["tool_schema"], case["tool_results"])["identity_errors"], 0)
            parsed = json.loads(auto)
            reference = next(x for x in parsed["fields"] if "covers" in x or "input_key" in x or x == "retry_of")
            col = parsed["fields"].index(reference)
            parsed["rows"][0][col], parsed["rows"][1][col] = parsed["rows"][1][col], parsed["rows"][0][col]
            result = check(json.dumps(parsed), case["tool_schema"], case["tool_results"])
            self.assertFalse(result["passed"])
            self.assertGreater(result["relation_errors"], 0)

    def test_checker_does_not_certify_unannotated_state(self):
        case = make_case("retry", DEV_SEEDS[0], "development")
        parsed = json.loads(project(case["tool_schema"], case["tool_results"]))
        col = parsed["fields"].index("result_state")
        parsed["rows"][0][col] = "wrong"
        self.assertTrue(check(json.dumps(parsed), case["tool_schema"], case["tool_results"])["passed"])

    def test_independent_terminal_controls(self):
        retry = {"request_key": "r", "attempt_key": "a", "dispatch_state": "sent",
                 "result_state": "failed", "can_retry": True}
        self.assertEqual(terminal("retry", retry, {"path": "note", "value": "x"}),
                         {"action": "retry", "target_id": "r", "work": ["attempt:a"]})
        self.assertEqual(terminal("retry", retry, {"path": "dispatch_state", "value": "not_sent"})["action"], "dispatch")
        ci = {"current_build": "b", "approval": {"covers_build": "old"},
              "check": {"covers_build": "b", "verdict": "pass"}}
        self.assertEqual(terminal("ci_handoff", ci, {"path": "note", "value": "x"})["work"], ["approval"])
        self.assertEqual(terminal("ci_handoff", ci, {"path": "approval.covers_build", "value": "b"})["action"], "handoff")
        data = {"extract": {"state": "pass", "output_key": "raw"},
                "transform": {"state": "pass", "input_key": "wrong", "output_key": "clean"},
                "load": {"state": "pass", "input_key": "clean", "output_key": "table"},
                "publish_approval": {"covers_output": "table"}}
        self.assertEqual(terminal("data_job", data, {"path": "note", "value": "x"})["work"], ["link:transform"])
        self.assertEqual(terminal("data_job", data, {"path": "transform.input_key", "value": "raw"})["action"], "publish")

    def test_dev_request_envelopes_and_local_handoff(self):
        class FakeClient:
            def __init__(self):
                self.identities = []
                self.attempts = 0
                self.spent = Decimal(0)

            def complete(self, identity, request):
                request_bytes(request)
                self.identities.append(identity)
                self.attempts += 1
                return {"memory": ""}

        for family in FAMILIES:
            case = make_case(family, DEV_SEEDS[0], "development")
            parent = memory_request(case, "parent", {"tool_schema": case["tool_schema"],
                                                      "tool_results": case["tool_results"]}, 2600)
            self.assertNotIn("candidates", parent["observation"])
            self.assertNotIn("futures", parent["observation"])
            client = FakeClient()
            with tempfile.TemporaryDirectory() as folder:
                episode = prepare_memories(client, case, Path(folder))
            self.assertEqual(len(client.identities), 2)
            self.assertTrue(episode["local"]["automatic"]["child_check"]["passed"])
            final = execution_request(case, episode["memories"]["automatic"]["child"], case["futures"][0])
            self.assertEqual(final["response_schema"], EXEC_SCHEMA)
            request_bytes(final)


if __name__ == "__main__":
    unittest.main()
