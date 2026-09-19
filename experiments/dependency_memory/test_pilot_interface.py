"""Public-input invariants; no model, credentials, subprocess, or network."""

from copy import deepcopy
from dataclasses import replace
from fractions import Fraction
import json
import unittest

from artifact_workflow import Action, ArtifactEnvironment, Config, Observation, Receipt
from pilot_interface import (FakeClient, RENDER_MODES, infer_candidates, inspection_request,
                             public_metadata, render_manifest, request_bytes, retention_request,
                             validate_inspection_response, validate_request,
                             validate_retention_response)
from pilot_plan import SCENARIOS
from recovery_frontier import reference_plan
from run_recovery_frontier import route_fixtures, scenarios


def boundary_requests(config, fixture, client, *, inspect=False, render_mode="explicit_labels"):
    """Use real environment observations; never give the client a fixture."""
    environment = ArtifactEnvironment(config, fixture)
    metadata = public_metadata(config)
    window = (environment.step(Action("collect_receipts")),)
    if inspect:
        window += (environment.step(Action("inspect_manifest")),)
    window += (environment.step(Action("seal_receipts")),)
    first = retention_request(config, metadata, (), window, 1, render_mode)
    memory = validate_retention_response(client.complete(first), first)
    window = tuple(environment.step(Action(action)) for action in
                   ("read_manifest", "process_build", "seal_build"))
    second = retention_request(config, metadata, memory, window, 2, render_mode)
    retained = validate_retention_response(client.complete(second), second)
    return first, second, retained


class PilotInterfaceTests(unittest.TestCase):
    def setUp(self):
        self.config = scenarios()["costly_recovery"]
        self.fixture = tuple(route_fixtures(self.config))[0]
        self.metadata = public_metadata(self.config)

    def test_metadata_and_manifest_mapping_cover_all_routes_both_directions(self):
        seen = set()
        for fixture in route_fixtures(self.config):
            self.assertEqual(public_metadata(self.config), self.metadata)
            self.assertNotIn(fixture.receipts[0].token, json.dumps(self.metadata))
            for mode in RENDER_MODES:
                rendered = render_manifest(fixture.candidates, self.metadata, mode)
                self.assertEqual(infer_candidates(rendered, self.metadata), fixture.candidates)
                if mode == "inferred_dependencies":
                    self.assertNotIn("candidate_keys", rendered)
                    mapping = {r["key"]: r["artifact_property"] for r in self.metadata["jobs"]}
                    self.assertEqual(rendered["requested_properties"],
                                     [mapping[k] for k in fixture.candidates])
            seen.add((fixture.candidates, fixture.target))
        self.assertEqual(len(seen), 30)

    def test_private_target_changes_neither_boundary_request(self):
        for name in SCENARIOS:
            config = scenarios()[name]
            for fixture in route_fixtures(config):
                other = replace(fixture, target=next(k for k in fixture.candidates if k != fixture.target))
                for mode in RENDER_MODES:
                    for inspect in (False, True):
                        original = boundary_requests(config, fixture, FakeClient(), inspect=inspect, render_mode=mode)
                        changed = boundary_requests(config, other, FakeClient(), inspect=inspect, render_mode=mode)
                        self.assertEqual(request_bytes(original[0]), request_bytes(changed[0]))
                        self.assertEqual(request_bytes(original[1]), request_bytes(changed[1]))

    def test_unrevealed_route_and_revision_payload_do_not_enter_inspection(self):
        config = scenarios()["revision_costly_recovery"]
        baseline = None
        for fixture in route_fixtures(config):
            environment = ArtifactEnvironment(config, fixture)
            window = (environment.step(Action("collect_receipts")),)
            request = inspection_request(config, window=window, render_mode="inferred_dependencies")
            encoded = request_bytes(request)
            if baseline is None:
                baseline = encoded
            self.assertEqual(encoded, baseline)
            self.assertNotIn(fixture.revision.token.encode(), encoded)
            other = replace(fixture, revision=replace(fixture.revision, token="PRIVATE-UNSEEN-REVISION"))
            altered_environment = ArtifactEnvironment(config, other)
            altered = inspection_request(config, window=(altered_environment.step(Action("collect_receipts")),),
                                         render_mode="inferred_dependencies")
            self.assertEqual(request_bytes(altered), encoded)

    def test_deleted_receipts_cannot_reappear_after_first_boundary(self):
        for name in ("costly_recovery", "revision_costly_recovery"):
            config = scenarios()[name]
            for fixture in route_fixtures(config):
                for mode in RENDER_MODES:
                    first, second, retained = boundary_requests(config, fixture, FakeClient("forget_all"),
                                                               render_mode=mode)
                    serialized = request_bytes(second)
                    self.assertTrue(first["visible_records"])
                    for receipt in fixture.receipts:
                        self.assertNotIn(receipt.token.encode(), serialized)
                    self.assertEqual(retained, ())
                    if fixture.revision:
                        self.assertEqual(second["visible_records"],
                                         [{"key": fixture.revision.key, "revision": 2, "token": fixture.revision.token}])
                    else:
                        self.assertEqual(second["visible_records"], [])

    def test_all_actual_outbound_fields_are_allowlisted(self):
        first, second, _ = boundary_requests(self.config, self.fixture, FakeClient(), inspect=True)
        requests = [first, second, inspection_request(self.config, calibration=True)]
        excluded = ("scenario", "pair_id", "episode_id", "route_index", "seed", "seeds",
                    "target", "verifier_truth", "reference_costs", "reference_labels",
                    "previous_response_id", "session_id", "opaque_reasoning", "archive")
        def field_names(value):
            if isinstance(value, dict):
                return set(value).union(*(field_names(v) for v in value.values()))
            if isinstance(value, list):
                return set().union(*(field_names(v) for v in value))
            return set()
        for request in requests:
            actual = json.loads(request_bytes(request))
            self.assertTrue(set(excluded).isdisjoint(field_names(actual)))
            for field in excluded:
                modified = deepcopy(request)
                modified[field] = "PRIVATE-CANARY"
                with self.assertRaises(ValueError):
                    request_bytes(modified)
            for name in SCENARIOS:
                self.assertNotIn(name.encode(), request_bytes(request))

    def test_nested_channels_are_rejected_before_dispatch(self):
        request, _, _ = boundary_requests(self.config, self.fixture, FakeClient(), inspect=True)
        for location in ("config", "public_metadata", "response_schema"):
            changed = deepcopy(request)
            changed[location]["private_target"] = "PRIVATE-CANARY"
            with self.assertRaises(ValueError):
                request_bytes(changed)
        for location in ("visible_records", "observations"):
            changed = deepcopy(request)
            changed[location][0]["private_target"] = "PRIVATE-CANARY"
            with self.assertRaises(ValueError):
                request_bytes(changed)
        changed = deepcopy(request)
        changed["instructions"] += "PRIVATE-CANARY"
        with self.assertRaises(ValueError):
            request_bytes(changed)

    def test_metadata_cannot_carry_a_route_or_receipt(self):
        for field in ("manifest", "token", "target", "seed"):
            metadata = deepcopy(self.metadata)
            metadata[field] = "PRIVATE-CANARY"
            with self.assertRaises(ValueError):
                inspection_request(self.config, metadata)
        metadata = deepcopy(self.metadata)
        metadata["jobs"][0]["artifact_property"] = self.fixture.receipts[0].token
        with self.assertRaises(ValueError):
            inspection_request(self.config, metadata)

    def test_extra_evaluator_attributes_on_observation_are_not_forwarded(self):
        event = Observation("receipts", receipts=self.fixture.receipts,
                            required_key="PRIVATE-TARGET", required_revision=999,
                            candidates=self.fixture.candidates, error="PRIVATE-CANARY", success=True)
        request = inspection_request(self.config, window=(event,))
        payload = request_bytes(request)
        self.assertNotIn(b"PRIVATE", payload)
        self.assertNotIn(b"required_revision", payload)
        self.assertEqual(request["observations"], [{"kind": "receipts", "observed_keys":
                                                 [r.key for r in self.fixture.receipts]}])

    def test_schema_failures_do_not_repair_keys_or_values(self):
        first, _, _ = boundary_requests(self.config, self.fixture, FakeClient())
        invalid = [None, [], {"keys": "job-0"}, {"keys": [0]}, {"keys": ["job-0", "job-0"]},
                   {"keys": ["job-0", "job-1", "job-2"]}, {"keys": ["unknown"]},
                   {"keys": [], "rationale": "extra memory"}, {"keys": [], "inspect": False}]
        for response in invalid:
            with self.subTest(response=response), self.assertRaises(ValueError):
                validate_retention_response(response, first)
        for response in (None, True, {}, {"inspect": 1}, {"inspect": "false"},
                         {"inspect": False, "keys": []}):
            with self.subTest(response=response), self.assertRaises(ValueError):
                validate_inspection_response(response)
        self.assertFalse(validate_inspection_response({"inspect": False}))
        self.assertTrue(validate_inspection_response({"inspect": True}))

    def test_canonical_retention_exactly_maps_latest_visible_values(self):
        config = scenarios()["revision_costly_recovery"]
        fixture = tuple(route_fixtures(config))[0]
        first, second, _ = boundary_requests(config, fixture, FakeClient(), inspect=True)
        forward = validate_retention_response({"keys": ["job-0", "job-1"]}, second)
        reverse = validate_retention_response({"keys": ["job-1", "job-0"]}, second)
        self.assertEqual(forward, reverse)
        self.assertEqual(forward[0], fixture.revision)
        self.assertEqual(forward[1], fixture.receipts[1])
        self.assertNotIn(fixture.receipts[0].token.encode(), request_bytes(second))
        self.assertEqual(request_bytes(first), request_bytes(dict(reversed(list(first.items())))))

    def test_old_window_or_post_boundary_target_is_rejected(self):
        initial = Observation("receipts", receipts=self.fixture.receipts)
        manifest = Observation("manifest", candidates=self.fixture.candidates)
        for window in ((initial, Observation("checkpoint", checkpoint=1), manifest,
                        Observation("checkpoint", checkpoint=2)),
                       (initial, manifest, Observation("checkpoint", checkpoint=2)),
                       (Observation("requirement", required_key=self.fixture.target),
                        Observation("checkpoint", checkpoint=2))):
            with self.assertRaises(ValueError):
                retention_request(self.config, self.metadata, (), window, 2, "explicit_labels")
        with self.assertRaises(ValueError):
            inspection_request(self.config, window=(manifest,))
        with self.assertRaises(ValueError):
            inspection_request(self.config, window=(initial,), calibration=True)

    def test_public_fake_attains_reference_for_all_routes_modes_and_cells(self):
        for name in SCENARIOS:
            config = scenarios()[name]
            reference = reference_plan(config.jobs, config.candidate_count, config.first_capacity,
                                       config.second_capacity, config.revise)
            for mode in RENDER_MODES:
                for inspect in (False, True):
                    hits = []
                    for fixture in route_fixtures(config):
                        _, _, retained = boundary_requests(config, fixture, FakeClient(),
                                                          inspect=inspect, render_mode=mode)
                        expected = (fixture.revision if fixture.revision and fixture.target == fixture.revision.key
                                    else next(r for r in fixture.receipts if r.key == fixture.target))
                        hits.append(expected in retained)
                    observed = Fraction(sum(hits), len(hits))
                    expected_rate = reference.hit_with_inspection if inspect else reference.hit_without_inspection
                    self.assertEqual(observed, expected_rate, (name, mode, inspect))
            choice = FakeClient().complete(inspection_request(config, calibration=True))
            skip_cost = (1 - reference.hit_without_inspection) * config.recovery_cost
            inspect_cost = config.probe_cost + (1 - reference.hit_with_inspection) * config.recovery_cost
            self.assertEqual(validate_inspection_response(choice), inspect_cost < skip_cost)

    def test_fake_invalid_control_fails_and_zero_capacity_remains_legal(self):
        first, _, _ = boundary_requests(self.config, self.fixture, FakeClient())
        with self.assertRaises(ValueError):
            validate_retention_response(FakeClient("invalid").complete(first), first)
        request = inspection_request(self.config, calibration=True)
        with self.assertRaises(ValueError):
            validate_inspection_response(FakeClient("invalid").complete(request))
        config = replace(self.config, first_capacity=0, second_capacity=0)
        first, second, retained = boundary_requests(config, self.fixture, FakeClient())
        self.assertEqual(retained, ())
        self.assertEqual(first["response_schema"]["properties"]["keys"]["maxItems"], 0)
        self.assertEqual(second["response_schema"]["properties"]["keys"]["maxItems"], 0)
        self.assertNotIn("enum", second["response_schema"]["properties"]["keys"]["items"])


if __name__ == "__main__":
    unittest.main()
