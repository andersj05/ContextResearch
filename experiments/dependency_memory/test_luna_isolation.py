"""Offline information-channel invariants for the installed-client audit."""
from copy import deepcopy
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from artifact_workflow import Config
from luna_isolation import (ALLOWED_WRAPPERS, BASE_INSTRUCTIONS, DEVELOPER_INSTRUCTIONS,
                            MODEL, ROLLOUT_GUARD_TEXT, audit_payload, schema_projection,
                            thread_parameters, turn_parameters, wire_body_byte_bound,
                            expected_isolation_config, validate_effective_config)
from pilot_interface import inspection_request


def fixture():
    global_text = "Public background independent of every fixture.\n"
    public_text = "Only visible records."
    functions = {name: {"name": name, "direct": True, "code_mode_name": None,
                       "deferred": False, "source": {"kind": "harness"}}
                 for name in ALLOWED_WRAPPERS}
    tool_item = {"type": "additional_tools", "role": "developer", "tools": [
        {"type": "namespace", "name": "functions", "tools": [
            {"type": "function", "name": name} for name in ALLOWED_WRAPPERS]}]}
    texts = [("developer", BASE_INSTRUCTIONS), ("developer", DEVELOPER_INSTRUCTIONS),
             ("user", "# AGENTS.md instructions\n\n<INSTRUCTIONS>\n" + global_text.strip() + "\n</INSTRUCTIONS>"),
             ("user", public_text), ("developer", ROLLOUT_GUARD_TEXT)]
    return {"model": MODEL, "store": False, "stream": True,
            "client_metadata": {"x-codex-turn-metadata": json.dumps({"tool_namespaces_info": {
                "functions": {"name": "functions", "functions": functions}}})},
            "input": [tool_item] + [{"type": "message", "role": role,
                                       "content": [{"type": "input_text", "text": text}]}
                                      for role, text in texts]}, public_text, global_text


class LunaIsolationTests(unittest.TestCase):
    def audit(self, body, public_text, global_text):
        return audit_payload(body, public_text=public_text, global_instructions_text=global_text)

    def test_declared_background_and_intrinsics_are_exactly_allowlisted(self):
        body, public, background = fixture()
        report = self.audit(body, public, background)
        self.assertEqual(report["nested_tools"], [])
        self.assertEqual(report["external_information_tools"], [])
        self.assertEqual(report["input_message_count"], 5)

    def test_effective_config_checks_every_override_without_echoing_values(self):
        config = expected_isolation_config()
        config["unrelated_preference"] = "allowed"
        self.assertGreater(validate_effective_config(config)["verified_isolation_leaves"], 40)
        config["features"]["shell_tool"] = "sensitive-unexpected-value"
        with self.assertRaisesRegex(ValueError, "features.shell_tool") as caught:
            validate_effective_config(config)
        self.assertNotIn("sensitive-unexpected-value", str(caught.exception))

    def test_missing_critical_flag_bool_integer_confusion_and_guard_drift_fail(self):
        config = expected_isolation_config()
        del config["features"]["memories"]
        with self.assertRaisesRegex(ValueError, "features.memories"):
            validate_effective_config(config)
        config = expected_isolation_config()
        config["features"]["shell_tool"] = 0
        with self.assertRaises(ValueError):
            validate_effective_config(config)
        config = expected_isolation_config()
        config["features"]["rollout_budget"]["prefill_token_weight"] = 0
        with self.assertRaisesRegex(ValueError, "prefill_token_weight"):
            validate_effective_config(config)

    def test_effective_config_rejects_added_skill_or_enabled_mcp_server(self):
        config = expected_isolation_config()
        config["skills"]["config"].append({"name": "private_archive", "enabled": True})
        with self.assertRaises(ValueError):
            validate_effective_config(config)
        config = expected_isolation_config()
        config["mcp_servers"]["unreviewed"] = {"command": "private", "enabled": True}
        with self.assertRaises(ValueError):
            validate_effective_config(config)

    def test_prior_response_storage_and_unknown_fields_are_rejected(self):
        body, public, background = fixture()
        for key, value in [("previous_response_id", "old"), ("conversation", "old"),
                           ("store", True), ("unreviewed", "private")]:
            with self.subTest(key=key), self.assertRaises(ValueError):
                self.audit({**body, key: value}, public, background)

    def test_hidden_nested_tool_and_top_level_tool_are_rejected(self):
        body, public, background = fixture()
        changed = deepcopy(body)
        metadata = json.loads(changed["client_metadata"]["x-codex-turn-metadata"])
        metadata["tool_namespaces_info"]["shell"] = {"name": "shell", "functions": {}}
        changed["client_metadata"]["x-codex-turn-metadata"] = json.dumps(metadata)
        with self.assertRaises(ValueError):
            self.audit(changed, public, background)
        with self.assertRaises(ValueError):
            self.audit({**body, "tools": [{"type": "web_search"}]}, public, background)

    def test_deleted_data_or_skill_context_injected_into_input_is_rejected(self):
        body, public, background = fixture()
        for role, text in [("developer", "skills catalog"), ("user", "deleted receipt"),
                           ("assistant", "old reasoning")]:
            changed = deepcopy(body)
            changed["input"].append({"type": "message", "role": role,
                                     "content": [{"type": "input_text", "text": text}]})
            with self.subTest(role=role), self.assertRaises(ValueError):
                self.audit(changed, public, background)

    def test_unknown_embedded_input_type_and_changed_global_context_are_rejected(self):
        body, public, background = fixture()
        changed = deepcopy(body)
        changed["input"].append({"type": "reasoning", "encrypted_content": "old"})
        with self.assertRaises(ValueError):
            self.audit(changed, public, background)
        with self.assertRaises(ValueError):
            self.audit(body, public, background + "extra instruction")

    def test_schema_projection_preserves_host_constraint(self):
        schema = {"type": "object", "properties": {"keys": {"type": "array", "uniqueItems": True}}}
        original = deepcopy(schema)
        result = schema_projection(schema)
        self.assertEqual(schema, original)
        self.assertNotIn("uniqueItems", result["properties"]["keys"])

    def test_fresh_no_environment_thread_and_bounded_public_turn(self):
        with tempfile.TemporaryDirectory() as cwd:
            params = thread_parameters(cwd, "synthetic")
            self.assertEqual(params["environments"], [])
            self.assertEqual(params["selectedCapabilityRoots"], [])
            self.assertTrue(params["ephemeral"])
            Path(cwd, "private.txt").write_text("private")
            with self.assertRaises(ValueError):
                thread_parameters(cwd, "synthetic")
        request = inspection_request(Config(), calibration=True)
        params = turn_parameters("fresh", request)
        self.assertEqual(params["serviceTierForTurn"], "default")
        self.assertLessEqual(wire_body_byte_bound(request), 32768)
        with self.assertRaises(ValueError):
            turn_parameters("fresh", request, max_public_bytes=1)
        with patch("luna_isolation.MAX_FIXED_WIRE_BYTES", 40000), self.assertRaises(ValueError):
            turn_parameters("fresh", request)


if __name__ == "__main__":
    unittest.main()
