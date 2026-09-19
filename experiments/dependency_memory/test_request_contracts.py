"""Offline dispatch checks for existing and revision diagnostic requests."""
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import unittest
from unittest.mock import patch

from artifact_workflow import Config
from audit_luna_transport import synthetic_response
from luna_appserver import LunaClient
from luna_isolation import turn_parameters, wire_body_byte_bound
from pilot_interface import inspection_request, request_bytes as pilot_bytes
from request_contracts import request_bytes
from revision_interface import (KEYS, RULES, build_request,
                                request_bytes as revision_bytes,
                                validate_response)


def revision_request(rule="lexicographic_first", reverse=False):
    records = [{"key": key, "revision": 1,
                "token": hashlib.sha256(key.encode()).hexdigest()[:32]} for key in KEYS]
    return build_request(rule, KEYS[::-1] if reverse else KEYS, records)


class RequestContractTests(unittest.TestCase):
    def test_all_recorded_pilot_requests_remain_byte_identical(self):
        ledger = Path(__file__).parent / "results/luna_development_2026-09-19/requests.jsonl"
        rows = [json.loads(line) for line in ledger.read_text(encoding="utf-8").splitlines()]
        self.assertEqual(len(rows), 96)
        for row in rows:
            with self.subTest(attempt=row["attempt"]):
                original = row["request_utf8"].encode("utf-8")
                request = json.loads(original)
                self.assertEqual(request_bytes(request), original)
                self.assertEqual(request_bytes(request), pilot_bytes(request))
                self.assertEqual(hashlib.sha256(original).hexdigest(), row["request_sha256"])

    def test_new_contract_preserves_declared_rule_record_order_and_payload(self):
        for rule in RULES:
            for reverse in (False, True):
                with self.subTest(rule=rule, reverse=reverse):
                    request = revision_request(rule, reverse)
                    original = deepcopy(request)
                    encoded = request_bytes(request)
                    self.assertEqual(encoded, revision_bytes(request))
                    self.assertEqual(request, original)
                    self.assertEqual(json.loads(encoded)["visible_records"], original["visible_records"])

    def test_unknown_missing_or_nonstring_contract_cannot_fall_through(self):
        for request in (None, [], {}, {"version": None}, {"version": True},
                        {"version": ["pilot_public_request_v1"]},
                        {"version": "pilot_public_request_v2"},
                        {"version": "revision_parent_request_v2"}):
            with self.subTest(request=request), self.assertRaises(ValueError):
                request_bytes(request)

    def test_contract_version_relabeling_does_not_bypass_validation(self):
        pilot = inspection_request(Config(), calibration=True)
        revised = revision_request()
        pilot["version"] = "revision_parent_request_v1"
        revised["version"] = "pilot_public_request_v1"
        for request in (pilot, revised):
            with self.assertRaises(ValueError):
                request_bytes(request)

    def test_evaluator_channels_and_answer_hints_rejected_for_both_contracts(self):
        for request in (inspection_request(Config(), calibration=True), revision_request()):
            for key in ("evaluator_answer", "previous_response", "candidate_pair", "target"):
                with self.subTest(version=request["version"], key=key), self.assertRaises(ValueError):
                    request_bytes({**request, key: "undeclared"})
            changed = deepcopy(request)
            changed["instructions"] += " Keep the evaluator-preferred records."
            with self.assertRaises(ValueError):
                request_bytes(changed)
            changed = deepcopy(request)
            changed["response_schema"]["description"] = "evaluator-preferred answer"
            with self.assertRaises(ValueError):
                request_bytes(changed)

    def test_revision_request_reaches_turn_without_extra_context(self):
        request = revision_request()
        turn = turn_parameters("fresh-test-thread", request)
        self.assertEqual(turn["input"], [{"type": "text", "text": revision_bytes(request).decode(),
                                          "text_elements": []}])
        self.assertEqual(turn["environments"], [])
        self.assertEqual(turn["runtimeWorkspaceRoots"], [])
        self.assertLessEqual(wire_body_byte_bound(request), 32768)
        self.assertNotIn("uniqueItems", turn["outputSchema"]["properties"]["keys"])
        self.assertTrue(request["response_schema"]["properties"]["keys"]["uniqueItems"])

    def test_invalid_contract_is_rejected_before_process_or_generation(self):
        client = LunaClient.__new__(LunaClient)
        client.stopped = False
        with patch("luna_appserver.AppServer") as process:
            with self.assertRaises(ValueError):
                client.complete({"version": "unapproved"})
            process.assert_not_called()

    def test_synthetic_final_is_valid_without_an_answer_oracle(self):
        self.assertEqual(synthetic_response(inspection_request(Config(), calibration=True)),
                         '{"inspect":false}')
        for rule in RULES:
            request = revision_request(rule)
            self.assertEqual(validate_response(json.loads(synthetic_response(request)), request), ())


if __name__ == "__main__":
    unittest.main()
