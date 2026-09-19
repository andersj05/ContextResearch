"""Independent route/tree and saved-evidence checks for revision analysis."""

from dataclasses import replace
from fractions import Fraction
from itertools import combinations
import json
from pathlib import Path
import tempfile
import unittest

from artifact_workflow import (Action, ArtifactEnvironment, Config, Fixture,
                               Observation, Receipt)
from pilot_interface import public_metadata, retention_request
from revision_analysis import (DEFAULT_RUN, analyze, best_parent, grade_observed_child,
                               grade_parent, pair_formula, parent_value)


def independent_environment_value(config, first):
    """Maximize child choices BEFORE grading the pair's two hidden targets.

    Uses actual latest-receipt replacement and terminal payload verification,
    with no availability-count objective or closed-form probability formula.
    """
    receipts = tuple(Receipt(f"job-{i}", 1, f"receipt-{i}") for i in range(config.jobs))
    first_records = tuple(r for r in receipts if r.key in first)
    hits, routes = 0, 0
    for manifest in combinations(sorted(r.key for r in receipts), config.candidate_count):
        revision = Receipt(manifest[0], 2, "fresh-payload") if config.revise else None
        current = {r.key: r for r in first_records}
        if revision:
            current[revision.key] = revision
        available = tuple(current.values())
        best = 0
        for size in range(min(config.second_capacity, len(available)) + 1):
            for child in combinations(available, size):
                score = 0
                for target in manifest:
                    fixture = Fixture(receipts, manifest, target, revision)
                    env = ArtifactEnvironment(config, fixture)
                    for action in ("collect_receipts", "seal_receipts", "read_manifest",
                                   "process_build", "seal_build"):
                        env.step(Action(action))
                    for _ in range(config.delay):
                        env.step(Action("work"))
                    env.step(Action("get_requirement"))
                    supplied = next((r for r in child if r.key == target), None)
                    result = env.step(Action("submit", supplied))
                    score += bool(result.success)
                best = max(best, score)
        hits += best
        routes += len(manifest)
    return Fraction(hits, routes)


def first_request(config, candidates=None):
    receipts = tuple(Receipt(f"job-{i}", 1, f"value-{i}") for i in range(config.jobs))
    events = (Observation("receipts", receipts=receipts),)
    if candidates is not None:
        events += (Observation("manifest", candidates=candidates),)
    events += (Observation("checkpoint", checkpoint=1),)
    return retention_request(config, public_metadata(config), (), events, 1, "explicit_labels")


class RevisionAnalysisTests(unittest.TestCase):
    def test_pair_formula_matches_every_fixed_set_for_small_populations(self):
        for n in range(2, 8):
            keys = tuple(f"job-{i}" for i in range(n))
            for size in range(n + 1):
                for selected in combinations(keys, size):
                    for capacity in (0, 1, 2, 6):
                        for revise in (False, True):
                            config = Config(jobs=n, first_capacity=n,
                                            second_capacity=capacity, revise=revise)
                            expected = pair_formula(n, (int(k[4:]) for k in selected), capacity, revise)
                            self.assertEqual(parent_value(config, selected),
                                             (expected, n * (n - 1)))

    def test_parent_value_matches_independent_environment_and_child_decisions(self):
        for n in (3, 4):
            keys = tuple(f"job-{i}" for i in range(n))
            for size in range(n + 1):
                for selected in combinations(keys, size):
                    for capacity in (0, 1, 2):
                        for revise in (False, True):
                            config = Config(jobs=n, first_capacity=n, second_capacity=capacity,
                                            revise=revise, delay=0, recovery_available=False)
                            self.assertEqual(parent_value(config, selected)[0],
                                             independent_environment_value(config, selected))

    def test_revision_asymmetry_and_symmetric_ties(self):
        plain = Config(revise=False, first_capacity=2, second_capacity=2)
        value, winners, checked = best_parent(plain)
        self.assertEqual(value, Fraction(1, 3))
        self.assertEqual(len(winners), 15)
        self.assertEqual(checked, 22)  # Includes empty and one-record parents.
        revised = replace(plain, revise=True)
        value, winners, _ = best_parent(revised)
        self.assertEqual((value, winners), (Fraction(4, 5), (("job-4", "job-5"),)))
        self.assertEqual(parent_value(revised, ("job-0", "job-1"))[0], Fraction(8, 15))
        self.assertEqual(parent_value(revised, ("job-1", "job-2"))[0], Fraction(3, 5))

    def test_capacity_one_and_ample_parent_controls(self):
        config = Config(first_capacity=1, second_capacity=2, revise=True)
        self.assertEqual(best_parent(config)[:2], (Fraction(2, 3), (("job-5",),)))
        config = replace(config, first_capacity=2, second_capacity=1)
        value, winners, checked = best_parent(config)
        self.assertEqual(value, Fraction(1, 2))
        self.assertEqual(len(winners), checked)
        config = replace(config, revise=False)
        self.assertEqual(best_parent(config)[0], Fraction(3, 10))
        config = replace(config, first_capacity=6, second_capacity=2)
        self.assertEqual(best_parent(config)[0], 1)

    def test_public_manifest_conditions_the_comparison(self):
        config = Config(revise=False)
        chosen = {"keys": ["job-2", "job-4"]}
        hidden = grade_parent(first_request(config), chosen)
        revealed = grade_parent(first_request(config, ("job-2", "job-4")), chosen)
        self.assertEqual((hidden["route_count"], hidden["ideal_child_availability"]), (30, "1/3"))
        self.assertEqual((revealed["route_count"], revealed["ideal_child_availability"]), (2, "1"))
        self.assertEqual(revealed["availability_gap"], "0")
        bad = grade_parent(first_request(config, ("job-2", "job-4")),
                           {"keys": ["job-0", "job-1"]})
        self.assertEqual(bad["availability_gap"], "1")

    def test_revision_with_manifest_spares_the_refreshed_record(self):
        config = Config(revise=True, first_capacity=1)
        request = first_request(config, ("job-2", "job-4"))
        good = grade_parent(request, {"keys": ["job-4"]})
        stale = grade_parent(request, {"keys": ["job-2"]})
        self.assertEqual(good["ideal_child_availability"], "1")
        self.assertEqual(stale["availability_gap"], "1/2")

    def test_child_tie_is_not_a_conditional_error(self):
        config = Config(revise=False, second_capacity=1)
        records = (Receipt("job-2", 1, "two"), Receipt("job-4", 1, "four"))
        events = (Observation("manifest", candidates=("job-2", "job-4")),
                  Observation("build"), Observation("checkpoint", checkpoint=2))
        request = retention_request(config, public_metadata(config), records, events, 2, "explicit_labels")
        for key in ("job-2", "job-4"):
            value = grade_observed_child(request, {"keys": [key]})
            self.assertEqual((value["conditional_availability"], value["availability_gap"]), ("1/2", "0"))
        self.assertEqual(grade_observed_child(request, {"keys": []})["availability_gap"], "1/2")

    def test_saved_evidence_separates_only_three_strict_parent_deficits(self):
        result = analyze()
        self.assertEqual(result["counts"], {
            "saved_parent_selections": 36, "full_population_parent_selections": 17,
            "manifest_conditioned_parent_selections": 19, "strict_parent_deficits": 3,
            "full_population_strict_deficits": 3, "manifest_conditioned_strict_deficits": 0,
            "observed_child_selections": 36, "strict_observed_child_deficits": 0})
        bad = [r for r in result["selections"] if not r["parent"]["population_optimal_parent"]]
        self.assertTrue(all(r["parent"]["config"]["revise"] and r["arm"] == "never_inspect" for r in bad))
        self.assertEqual(sorted(r["parent"]["availability_gap"] for r in bad), ["1/5", "1/5", "4/15"])
        self.assertEqual(len(result["dimension_controls"]), 32)
        self.assertEqual(result["new_model_requests"], 0)

    def test_saved_content_hash_tampering_is_rejected(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            (root / "summary.json").write_bytes((DEFAULT_RUN / "summary.json").read_bytes())
            lines = (DEFAULT_RUN / "requests.jsonl").read_text(encoding="utf-8").splitlines()
            row = json.loads(lines[0])
            row["request_sha256"] = "0" * 64
            lines[0] = json.dumps(row)
            (root / "requests.jsonl").write_text("\n".join(lines) + "\n", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "content/hash"):
                analyze(root)

    def test_invalid_fixed_sets_and_nonpublic_routes_are_rejected(self):
        config = Config()
        for first in (("job-0", "job-0"), ("job-6",), ("job-0", "job-1", "job-2")):
            with self.assertRaises(ValueError):
                parent_value(config, first)
        with self.assertRaises(ValueError):
            parent_value(config, (), ("job-4", "job-2"))
        with self.assertRaises(ValueError):
            pair_formula(6, (1, 1), 2, True)


if __name__ == "__main__":
    unittest.main()
