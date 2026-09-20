"""Independent relational and information-input checks; no model requests."""

from copy import deepcopy
from dataclasses import replace
import inspect
from itertools import combinations
import json
import unittest

from artifact_workflow import Config
from heldout_renderers import (FAMILY_NAMES, JOB_KEYS, RENDER_MODES, VERSION,
                               infer_candidates, public_metadata, render_manifest)
from pilot_interface import inspection_request
from run_recovery_frontier import route_fixtures


def relational_catalog(metadata):
    """Enumerate all valid requests by relational joins, without either API.

    This starts from the public request vocabulary rather than a candidate
    pair, providing the opposite direction to the renderer's construction.
    """
    family = metadata["family"]
    requests = []
    if family == "alias_chain":
        for rows in combinations(metadata["aliases"], 2):
            artifacts = {name["artifact"] for name in metadata["names"] for alias in rows
                         if alias["intermediate_name"] == name["intermediate_name"]}
            requests.append((tuple(sorted(row["alias"] for row in rows)), artifacts))
    elif family == "package_prerequisites":
        for package in metadata["packages"]:
            artifacts = {source["source_artifact"] for source in metadata["components"]
                         if source["component"] in package["prerequisites"]}
            requests.append((package["package"], artifacts))
    elif family == "validation_scope":
        for obligation in metadata["obligations"]:
            if obligation["coverage"] != "all_scope_artifacts":
                raise AssertionError("Unexpected verification coverage")
            artifacts = {artifact for scope in metadata["scopes"]
                         if scope["scope"] == obligation["scope"] for artifact in scope["artifacts"]}
            requests.append((obligation["obligation"], artifacts))
    else:
        for handoff in metadata["handoffs"]:
            artifacts = {role["evidence_artifact"] for role in metadata["delivery_roles"]
                         if role["role"] in handoff["required_roles"]}
            requests.append((handoff["handoff"], artifacts))
    return {request: tuple(sorted(job["key"] for job in metadata["jobs"]
                                  if job["artifact"] in artifacts))
            for request, artifacts in requests}


def clue_value(manifest):
    fields = set(manifest) - {"kind", "task"}
    if len(fields) != 1:
        raise AssertionError("Inferred clue requires exactly one relation request")
    value = manifest[next(iter(fields))]
    return tuple(value) if isinstance(value, list) else value


class HeldoutRendererTests(unittest.TestCase):
    def test_public_catalogs_bijectively_cover_all_fifteen_pairs(self):
        expected = set(combinations(JOB_KEYS, 2))
        for family in FAMILY_NAMES:
            with self.subTest(family=family):
                metadata = public_metadata(family)
                self.assertEqual(metadata["version"], VERSION)
                self.assertEqual(tuple(job["key"] for job in metadata["jobs"]), JOB_KEYS)
                self.assertEqual(len({job["artifact"] for job in metadata["jobs"]}), 6)
                catalog = relational_catalog(metadata)
                self.assertEqual(len(catalog), 15)
                self.assertEqual(set(catalog.values()), expected)
                self.assertTrue(all(len(pair) == 2 for pair in catalog.values()))

    def test_all_thirty_routes_match_independent_semantics_and_revision_order(self):
        for family in FAMILY_NAMES:
            metadata = public_metadata(family)
            catalog = relational_catalog(metadata)
            for revise in (False, True):
                routes = list(route_fixtures(Config(revise=revise)))
                self.assertEqual(len(routes), 30)
                for fixture in routes:
                    if revise:
                        self.assertEqual(fixture.revision.key, min(fixture.candidates))
                    for mode in RENDER_MODES:
                        with self.subTest(family=family, revise=revise, pair=fixture.candidates, mode=mode):
                            manifest = render_manifest(fixture.candidates, metadata, mode)
                            expected = (tuple(manifest["candidate_keys"]) if mode == "explicit_labels"
                                        else catalog[clue_value(manifest)])
                            self.assertEqual(expected, fixture.candidates)
                            self.assertEqual(infer_candidates(manifest, metadata), expected)
                            self.assertEqual(public_metadata(family), metadata)
                            if mode == "inferred_dependencies":
                                encoded = json.dumps(manifest)
                                self.assertNotIn("candidate_keys", manifest)
                                self.assertFalse(any(key in encoded for key in JOB_KEYS))

    def test_hand_worked_paths_use_intermediate_relations(self):
        # lowtide -> bramble -> ledger-snapshot -> job-0;
        # sunrise -> opal -> route-schema -> job-1.
        examples = {
            "alias_chain": ("requested_aliases", ["lowtide", "sunrise"]),
            # bundle-dune -> resolver, writer -> route-schema, ledger-snapshot.
            "package_prerequisites": ("requested_package", "bundle-dune"),
            # verify-aurora -> scope-dune -> ledger-snapshot, route-schema.
            "validation_scope": ("verification_obligation", "verify-aurora"),
            # handoff-dune -> curator, dispatcher -> route-schema, ledger-snapshot.
            "deployment_handoff": ("deployment_handoff", "handoff-dune"),
        }
        for family, (field, value) in examples.items():
            metadata = public_metadata(family)
            manifest = render_manifest(("job-0", "job-1"), metadata, "inferred_dependencies")
            self.assertEqual(manifest[field], value)
            self.assertEqual(infer_candidates(manifest, metadata), ("job-0", "job-1"))

    def test_target_and_payload_changes_cannot_change_metadata_or_clues(self):
        for family in FAMILY_NAMES:
            metadata = public_metadata(family)
            for fixture in route_fixtures(Config()):
                changed = replace(fixture,
                                  target=next(key for key in fixture.candidates if key != fixture.target),
                                  receipts=tuple(replace(row, token="PRIVATE-INITIAL") for row in fixture.receipts),
                                  revision=replace(fixture.revision, token="PRIVATE-REVISION"))
                for mode in RENDER_MODES:
                    before = render_manifest(fixture.candidates, metadata, mode)
                    after = render_manifest(changed.candidates, public_metadata(family), mode)
                    self.assertEqual(before, after)
                    encoded = json.dumps([metadata, before], sort_keys=True)
                    for receipt in fixture.receipts + (fixture.revision,):
                        self.assertNotIn(receipt.token, encoded)
                    self.assertNotIn("PRIVATE", encoded)

    def test_function_signatures_exclude_evaluator_channels(self):
        self.assertEqual(tuple(inspect.signature(public_metadata).parameters), ("family",))
        self.assertEqual(tuple(inspect.signature(render_manifest).parameters), ("candidates", "metadata", "render_mode"))
        self.assertEqual(tuple(inspect.signature(infer_candidates).parameters), ("manifest", "metadata"))
        metadata = public_metadata(FAMILY_NAMES[0])
        for private in ("target", "fixture", "receipt", "payload", "seed", "route_index", "config"):
            with self.subTest(private=private), self.assertRaises(TypeError):
                render_manifest(("job-0", "job-1"), metadata, "explicit_labels", **{private: "PRIVATE"})

    def test_metadata_and_manifest_channels_are_strictly_allowlisted(self):
        for family in FAMILY_NAMES:
            metadata = public_metadata(family)
            for mode in RENDER_MODES:
                manifest = render_manifest(("job-0", "job-1"), metadata, mode)
                for field in ("target", "receipt", "seed", "rationale", "family", "previous_response_id"):
                    altered = deepcopy(manifest)
                    altered[field] = "PRIVATE"
                    with self.subTest(family=family, field=field), self.assertRaises(ValueError):
                        infer_candidates(altered, metadata)
                altered = deepcopy(manifest)
                altered["kind"] = "requirement"
                with self.assertRaises(ValueError):
                    infer_candidates(altered, metadata)
            for mutation in (lambda value: value.update(target="PRIVATE"),
                             lambda value: value["jobs"][0].update(artifact="PRIVATE"),
                             lambda value: value["jobs"].reverse()):
                altered = deepcopy(metadata)
                mutation(altered)
                with self.assertRaises(ValueError):
                    render_manifest(("job-0", "job-1"), altered, "explicit_labels")
                with self.assertRaises(ValueError):
                    infer_candidates({"kind": "manifest", "candidate_keys": ["job-0", "job-1"]}, altered)

    def test_invalid_pairs_and_clues_are_rejected_without_repair(self):
        invalid_pairs = ((), ("job-0",), ("job-0", "job-1", "job-2"), ("job-0", "job-0"),
                         ("job-1", "job-0"), ("job-0", "unknown"), ("job-0", 1), "job-0,job-1", None)
        for family in FAMILY_NAMES:
            metadata = public_metadata(family)
            for candidates in invalid_pairs:
                with self.subTest(family=family, pair=candidates), self.assertRaises(ValueError):
                    render_manifest(candidates, metadata, "explicit_labels")
            manifest = render_manifest(("job-0", "job-1"), metadata, "inferred_dependencies")
            field = next(iter(set(manifest) - {"kind", "task"}))
            for invalid in ("unknown", None, 0, [], ["unknown", "unknown"], ["sunrise", "lowtide"]):
                altered = {**manifest, field: invalid}
                with self.subTest(family=family, clue=invalid), self.assertRaises(ValueError):
                    infer_candidates(altered, metadata)
            with self.assertRaises(ValueError):
                infer_candidates({**manifest, "task": manifest["task"] + " PRIVATE"}, metadata)
            with self.assertRaises(ValueError):
                render_manifest(("job-0", "job-1"), metadata, "unrecognized")
        for invalid_family in ("direct_artifact_tags", "unknown", None, [], 0):
            with self.assertRaises(ValueError):
                public_metadata(invalid_family)

    def test_fresh_catalogs_and_development_serializer_gate_remain_intact(self):
        for family in FAMILY_NAMES:
            metadata = public_metadata(family)
            changed = public_metadata(family)
            changed["jobs"][0]["artifact"] = "PRIVATE"
            self.assertEqual(public_metadata(family), metadata)
            # This milestone supplies offline semantics, not transport support.
            with self.assertRaises(ValueError):
                inspection_request(Config(), metadata=metadata)


if __name__ == "__main__":
    unittest.main()
