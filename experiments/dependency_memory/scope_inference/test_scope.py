import ast
from copy import deepcopy
from itertools import islice
import json
from pathlib import Path
import unittest
from unittest.mock import patch

from experiments.dependency_memory.workflow_replay import evidence
from experiments.dependency_memory.scope_inference import codec, protocol, study


class ScopeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.original = staticmethod(evidence.historical_classifier())

    def test_hand_contract_agrees_with_original_and_existing_projection_on_catalog(self):
        count = 0
        for row in study.control_catalog():
            expected = study.answer(row, self.original)
            self.assertEqual(expected, study.answer(codec.project(row, study.HAND), self.original))
            self.assertEqual(expected, study.answer(evidence.project(row), self.original))
            count += 1
        self.assertEqual(count, 14505)

    def test_nonempty_unknown_metadata_witness(self):
        row = {"status": "transport_failure", "error_type": "StudyStopped", "provider_metadata": {"unexpected": 1}}
        weak = deepcopy(study.HAND)
        weak["nonempty_paths"] = []
        self.assertEqual(study.answer(row, self.original)[0], "unknown")
        self.assertEqual(study.answer(codec.project(row, weak), self.original)[0], "preflight_only")
        self.assertEqual(study.answer(codec.project(row, study.HAND), self.original)[0], "unknown")

    def test_presence_and_absence_do_not_drop_contradictory_null(self):
        row = {"status": "transport_failure", "provider_metadata": {"dispatched": False, "usage": None}}
        projected = codec.project(row, study.HAND)
        self.assertIs(projected["provider_metadata"]["usage"], True)
        self.assertEqual(study.answer(projected, self.original)[0], "unknown")
        del row["provider_metadata"]["usage"]
        self.assertEqual(study.answer(codec.project(row, study.HAND), self.original)[0], "preflight_only")

    def test_malformed_container_and_boolean_ticket_are_not_coerced(self):
        for meta in (None, False, [], "bad", {"dispatched": True, "attempt_ticket": True}):
            row = {"status": "transport_failure", "provider_metadata": meta}
            self.assertEqual(study.answer(row, self.original), study.answer(codec.project(row, study.HAND), self.original))

    def test_projection_is_idempotent_and_does_not_mutate_inputs(self):
        for row in islice(study.control_catalog(), 1200):
            before = deepcopy(row)
            projected = codec.project(row, study.HAND)
            self.assertEqual(codec.project(projected, study.HAND), projected)
            self.assertEqual(row, before)

    def test_full_value_and_presence_precedence(self):
        contract = {"value_paths": ["a.b"], "presence_paths": ["a", "c"], "nonempty_paths": []}
        self.assertEqual(codec.project({"a": {"b": 9, "noise": 2}, "c": None}, contract), {"a": {"b": 9}, "c": True})
        self.assertEqual(codec.project({"a": "wrong-container"}, contract), {"a": "wrong-container"})

    def test_bad_paths_and_extra_fields_are_rejected(self):
        for paths in (["a", "a"], ["../x"], ["a."], [codec.MARKER], [["a"]], [1]):
            with self.assertRaises(ValueError):
                codec.validate({"value_paths": paths, "presence_paths": [], "nonempty_paths": []})
        with self.assertRaises(ValueError):
            codec.validate({**study.HAND, "expected": True})

    def test_conservative_ast_root_projection_and_cache_are_strong_controls(self):
        roots = codec.literal_roots(study.public_program())
        self.assertEqual(roots["value_paths"], ["error_type", "provider_metadata", "status"])
        records, _ = evidence.load_snapshot()
        cached = study.staged(records, self.original, kind="cached")
        self.assertEqual(cached["final_queries"], 24)
        self.assertEqual(cached["correct"], 24)
        for row in records:
            self.assertEqual(study.answer(row, self.original), study.answer(codec.project(row, roots), self.original))

    def test_source_only_requests_exclude_records_and_gold_contract(self):
        for variant in ("concise", "closure"):
            request = protocol.request(variant)
            text = protocol.request_bytes(request).decode()
            self.assertEqual(set(request["observation"]), {"public_program", "projection_language"})
            self.assertNotIn("def project", text)
            self.assertNotIn("historical_decision", text)
            self.assertNotIn("control_catalog", text)
        identities = [row["identity"] for row in study.schedule()]
        self.assertEqual(len(identities), len(set(identities)))
        self.assertEqual(len(identities), 8)

    def test_utf8_caps_preserve_full_state_or_admit_empty(self):
        rows = [{"value": "é"}]
        size = len(codec.wire(rows))
        self.assertEqual(codec.admit(rows, size)[0], codec.wire(rows).decode())
        self.assertEqual(codec.admit(rows, size - 1)[0], "")

    def test_binding_parent_cap_cannot_resurrect_historical_records(self):
        records, _ = evidence.load_snapshot()
        with patch.object(codec, "PARENT_CAP", 0):
            result = study.staged(records, self.original, kind="cached")
        self.assertTrue(result["parent"]["infeasible"])
        self.assertEqual(result["correct"], 0)
        self.assertTrue(all(row["proposal_bytes"] == 2 for row in result["children"]))

    def test_new_eight_call_and_credit_caps_stop_before_process_creation(self):
        from experiments.dependency_memory.scope_inference import transport, profile
        audit = {"version": "scope_luna6_preflight_v1", "isolation_passed": True, "real_model_generations": 0,
                 "cases": [{"payload_audit": {"visible_tool_spec_sha256": profile.VISIBLE_TOOL_SPEC_SHA256,
                            "bootstrap_tool_specification": None}} for _ in range(4)]}
        with patch.object(transport.Client, "check_hashes"), patch.object(transport, "AppServer") as server:
            client = transport.Client("unused", "unused", Path("unused"), audit)
            client.attempts = 8
            with self.assertRaises(RuntimeError):
                client.complete("unattempted", protocol.request("closure"))
            self.assertEqual(client.attempts, 8)
            client.attempts = 0
            client.spent = transport.Decimal("13")
            with self.assertRaises(RuntimeError):
                client.complete("another-unattempted", protocol.request("closure"))
            self.assertEqual(client.attempts, 0)
            server.assert_not_called()

    def test_actor_codec_imports_have_no_external_information_channels(self):
        path = Path(codec.__file__)
        imports = [node.module or "" for node in ast.walk(ast.parse(path.read_text())) if isinstance(node, ast.ImportFrom)]
        self.assertFalse(any("evidence" in name or "study" in name or "appserver" in name for name in imports))


if __name__ == "__main__":
    unittest.main()
