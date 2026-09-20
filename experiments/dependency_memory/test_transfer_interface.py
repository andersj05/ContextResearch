"""Public information and condition-isolation invariants for transfer requests."""

from copy import deepcopy
import inspect
from itertools import product
import json
import unittest

from transfer_interface import (FRAMINGS, GUARANTEES, GUIDANCE, JOB_COUNTS, RULES, VERSION,
                                build_request, job_keys, request_bytes, response_schema,
                                validate_request, validate_response)


def inputs(jobs=6, **conditions):
    keys = job_keys(jobs)
    return {"jobs": jobs, "refresh_rule": "first",
            "priorities": {key: (index * 5 + 3) % jobs for index, key in enumerate(keys)},
            "record_order": tuple(reversed(keys[1:] + keys[:1])),
            "records": [{"key": key, "revision": 1, "token": f"{index + 21:032x}"}
                        for index, key in enumerate(keys)],
            "framing": "compact", "guarantee": "explicit_optimal", "guidance": "generic",
            **conditions}


def fields(value):
    if isinstance(value, dict):
        return set(value).union(*(fields(child) for child in value.values()))
    if isinstance(value, list):
        return set().union(*(fields(child) for child in value))
    return set()


class TransferRequestTests(unittest.TestCase):
    def test_all_factor_conditions_preserve_model_records_and_priority_mapping(self):
        requests = []
        for jobs in JOB_COUNTS:
            spec = inputs(jobs)
            for framing, guarantee, guidance, rule in product(FRAMINGS, GUARANTEES, GUIDANCE, RULES):
                request = build_request(**{**spec, "framing": framing, "guarantee": guarantee,
                                           "guidance": guidance, "refresh_rule": rule})
                requests.append(request_bytes(request))
                self.assertEqual(json.loads(request_bytes(request)), request)
                self.assertEqual(request["version"], VERSION)
                self.assertEqual(request["public_model"], {"jobs": jobs, "candidate_count": 2,
                                                          "parent_capacity_records": 2, "child_capacity_records": 2})
                self.assertEqual([row["key"] for row in request["visible_records"]], list(spec["record_order"]))
                self.assertEqual(request["public_metadata"], {"jobs": [
                    {"key": key, "refresh_priority": spec["priorities"][key]} for key in job_keys(jobs)]})
                self.assertEqual(request["response_schema"]["properties"]["keys"]["items"]["enum"], list(job_keys(jobs)))
                self.assertIn("uniformly from all unordered pairs", request["instructions"])
                self.assertIn("uniformly from the candidate pair", request["instructions"])
                self.assertIn("before any optional recovery", request["instructions"])
        self.assertEqual(len(requests), 48)
        self.assertEqual(len(set(requests)), 48)

    def test_frame_changes_only_wording_and_fixed_context(self):
        for jobs in JOB_COUNTS:
            compact = build_request(**inputs(jobs, framing="compact"))
            workflow = build_request(**inputs(jobs, framing="workflow"))
            changed = {key for key in compact if compact[key] != workflow[key]}
            self.assertEqual(changed, {"instructions", "public_context"})
            # The first sentence introduces framing; all mathematical rules and
            # requested actions afterwards are byte-identical.
            self.assertEqual(compact["instructions"].split(". ", 1)[1], workflow["instructions"].split(". ", 1)[1])
            self.assertEqual(compact["public_context"], [])
            self.assertEqual([row["event"] for row in workflow["public_context"]],
                             ["collection_complete", "checkpoint_due", "build_pending"])
            context = json.dumps(workflow["public_context"])
            for row in workflow["visible_records"]:
                self.assertNotIn(row["key"], context)
                self.assertNotIn(row["token"], context)

    def test_guarantee_and_guidance_change_only_prespecified_advice(self):
        baseline = build_request(**inputs())
        unspecified = build_request(**inputs(guarantee="unspecified"))
        prospective = build_request(**inputs(guidance="prospective"))
        for changed in (unspecified, prospective):
            self.assertEqual({key for key in baseline if baseline[key] != changed[key]}, {"instructions"})
        self.assertIn("guaranteed to choose optimally", baseline["instructions"])
        self.assertNotIn("guaranteed", unspecified["instructions"])
        self.assertNotIn("optimally", unspecified["instructions"])
        self.assertIn("which will not", prospective["instructions"])
        self.assertLessEqual(abs(len(baseline["instructions"].split()) - len(prospective["instructions"].split())), 2)
        for request in (baseline, unspecified, prospective):
            for key in job_keys(6):
                self.assertNotIn(key, request["instructions"])
            self.assertNotIn("retain the highest", request["instructions"])
            self.assertNotIn("retain the lowest", request["instructions"])

    def test_first_and_last_are_public_priority_rules_not_key_or_display_order(self):
        for jobs in JOB_COUNTS:
            first = build_request(**inputs(jobs, refresh_rule="first"))
            last = build_request(**inputs(jobs, refresh_rule="last"))
            none = build_request(**inputs(jobs, refresh_rule="none"))
            self.assertIn("minimum refresh_priority", first["instructions"])
            self.assertIn("maximum refresh_priority", last["instructions"])
            self.assertIn("does not refresh any job", none["instructions"])
            mapping = {row["key"]: row["refresh_priority"] for row in first["public_metadata"]["jobs"]}
            self.assertNotEqual(min(mapping, key=mapping.get), min(mapping))
            self.assertNotEqual(max(mapping, key=mapping.get), max(mapping))
            self.assertEqual(set(mapping.values()), set(range(jobs)))
            for request in (last, none):
                self.assertEqual(request["public_metadata"], first["public_metadata"])
                self.assertEqual(request["visible_records"], first["visible_records"])

    def test_factor_and_evaluator_labels_are_absent_from_serialized_requests(self):
        excluded = {"framing", "guarantee", "guidance", "block", "case_id", "request_id", "seed",
                    "candidate_keys", "target", "final_target", "evaluator_answers", "optimal_keys",
                    "best_availability", "reference_costs", "previous_response", "session_id"}
        for framing, guarantee, guidance in product(FRAMINGS, GUARANTEES, GUIDANCE):
            request = build_request(**inputs(framing=framing, guarantee=guarantee, guidance=guidance))
            self.assertTrue(excluded.isdisjoint(fields(json.loads(request_bytes(request)))))
            for label in ("explicit_optimal", "unspecified", "prospective", "generic", "compact"):
                self.assertNotIn('"' + label + '"', request_bytes(request).decode())
        signature = inspect.signature(build_request)
        self.assertFalse(any(parameter.kind == inspect.Parameter.VAR_KEYWORD for parameter in signature.parameters.values()))
        for private in ("candidate_keys", "target", "seed", "block", "case_id", "reference_answer"):
            with self.subTest(private=private), self.assertRaises(TypeError):
                build_request(**inputs(), **{private: "PRIVATE"})

    def test_payload_and_order_changes_affect_only_declared_visible_records(self):
        original_inputs = inputs()
        original = build_request(**original_inputs)
        alternate = deepcopy(original_inputs)
        alternate["record_order"] = tuple(reversed(alternate["record_order"]))
        alternate["records"] = [{**row, "token": f"{index + 100:032x}"}
                                for index, row in enumerate(alternate["records"])]
        changed = build_request(**alternate)
        self.assertEqual({key for key in original if original[key] != changed[key]}, {"visible_records"})
        selected = {"keys": ["job-04", "job-01"]}
        self.assertEqual(validate_response(selected, original), validate_response(selected, changed))
        # Input objects are not retained as mutable aliases in the request.
        original_inputs["records"][0]["token"] = "PRIVATE"
        original_inputs["priorities"]["job-00"] = 999
        self.assertEqual(request_bytes(original), request_bytes(json.loads(request_bytes(original))))

    def test_nested_evaluator_and_extra_information_channels_are_rejected(self):
        original = build_request(**inputs(framing="workflow"))
        altered = []
        for field in ("candidate_keys", "target", "block", "seed", "optimal_keys", "rationale"):
            altered.append({**deepcopy(original), field: "PRIVATE"})
        for location in ("public_model", "public_metadata", "response_schema"):
            request = deepcopy(original)
            request[location]["hidden_hint"] = "PRIVATE"
            altered.append(request)
        for location in ("visible_records", "public_context"):
            request = deepcopy(original)
            request[location][0]["hidden_hint"] = "PRIVATE"
            altered.append(request)
        request = deepcopy(original)
        request["public_metadata"]["jobs"][0]["hidden_hint"] = "PRIVATE"
        altered.append(request)
        request = deepcopy(original)
        request["instructions"] += " Keep job-04 and job-05."
        altered.append(request)
        request = deepcopy(original)
        request["public_context"][0]["description"] += " PRIVATE"
        altered.append(request)
        request = deepcopy(original)
        request["public_context"] = []
        altered.append(request)
        for request in altered:
            with self.assertRaises(ValueError):
                request_bytes(request)

    def test_invalid_counts_priorities_orders_and_records_fail_closed(self):
        for jobs in (0, 5, 7, 13, True, 6.0, "6"):
            with self.assertRaises(ValueError):
                job_keys(jobs)
        altered = []
        for priorities in ({}, {key: 0 for key in job_keys(6)},
                           {key: index + 1 for index, key in enumerate(job_keys(6))}):
            altered.append(inputs(priorities=priorities))
        request_input = inputs()
        request_input["priorities"]["job-00"] = True
        altered.append(request_input)
        for order in (("job-00",), job_keys(6)[:-1] + ("job-00",), tuple(range(6)), "job-00"):
            altered.append(inputs(record_order=order))
        for field, value in (("token", "SECRET"), ("token", "F" * 32), ("revision", 2),
                             ("revision", True), ("key", "job-0")):
            request_input = inputs()
            request_input["records"][0][field] = value
            altered.append(request_input)
        request_input = inputs()
        request_input["records"].pop()
        altered.append(request_input)
        request_input = inputs()
        request_input["records"][0] = dict(request_input["records"][1])
        altered.append(request_input)
        for request_input in altered:
            with self.assertRaises(ValueError):
                build_request(**request_input)

    def test_invalid_inbound_model_metadata_and_schema_are_rejected(self):
        original = build_request(**inputs())
        altered = []
        for field, value in (("jobs", 7), ("candidate_count", True), ("parent_capacity_records", 1),
                             ("child_capacity_records", 3)):
            request = deepcopy(original)
            request["public_model"][field] = value
            altered.append(request)
        request = deepcopy(original)
        request["public_metadata"]["jobs"].reverse()
        altered.append(request)
        request = deepcopy(original)
        request["public_metadata"]["jobs"][0]["refresh_priority"] = 999
        altered.append(request)
        request = deepcopy(original)
        request["response_schema"]["properties"]["keys"]["items"]["enum"].reverse()
        altered.append(request)
        request = deepcopy(original)
        request["response_schema"]["additionalProperties"] = 0
        altered.append(request)
        for request in altered:
            with self.assertRaises(ValueError):
                validate_request(request)
        for field in ("framing", "guarantee", "guidance", "refresh_rule"):
            with self.assertRaises(ValueError):
                build_request(**inputs(**{field: "unknown"}))

    def test_response_validation_returns_only_canonical_valid_selections(self):
        for jobs in JOB_COUNTS:
            request = build_request(**inputs(jobs))
            keys = job_keys(jobs)
            self.assertEqual(validate_response({"keys": []}, request), ())
            self.assertEqual(validate_response({"keys": [keys[-1], keys[0]]}, request), (keys[0], keys[-1]))
            for response in (None, [], {"keys": "job-00"}, {"keys": [True]},
                             {"keys": [keys[0], keys[0]]}, {"keys": list(keys[:3])},
                             {"keys": ["job-12"]}, {"keys": [], "rationale": "PRIVATE"}):
                with self.subTest(response=response), self.assertRaises(ValueError):
                    validate_response(response, request)


if __name__ == "__main__":
    unittest.main()
