"""Independent finite formulations and recovery-channel invariants."""

from dataclasses import replace
from fractions import Fraction
from itertools import combinations
import unittest

from artifact_workflow import (Action, ArtifactEnvironment, Config, Fixture, Policy,
                               Receipt, run_episode)
from recovery_frontier import (Point, efficient_vertices, executable_policy,
                               no_revision_formula, reference_plan,
                               strategy_points, success_at_budget)


def fixtures(config):
    receipts = tuple(Receipt(f"job-{i}", 1, f"opaque-{i}") for i in range(config.jobs))
    for a in combinations(sorted(r.key for r in receipts), config.candidate_count):
        for target in a:
            revision = Receipt(a[0], 2, "new-opaque") if config.revise else None
            yield Fixture(receipts, a, target, revision)


def subsets(items, capacity):
    return (s for k in range(min(len(items), capacity) + 1) for s in combinations(items, k))


def independent_tree_value(n, m, b1, b2, revise, inspect):
    """Enumerate retention decisions then grade EVERY unrevealed final target.

    Deliberately includes smaller parent/child sets and does not use the planner's
    availability helper or min-count objective.
    """
    manifests = list(combinations(range(n), m))

    def branch_hits(first, a):
        current = [i for i in first if i in a and (not revise or i != a[0])]
        if revise:
            current.append(a[0])
        return max(sum(target in child for target in a) for child in subsets(current, b2))

    if inspect:
        hits = sum(max(branch_hits(first, a) for first in subsets(tuple(range(n)), b1))
                   for a in manifests)
    else:
        hits = max(sum(branch_hits(first, a) for a in manifests)
                   for first in subsets(tuple(range(n)), b1))
    return Fraction(hits, len(manifests) * m)


class RecoveryTests(unittest.TestCase):
    def test_recovery_after_zero_memory_returns_latest_revision(self):
        c = Config(jobs=3, first_capacity=0, second_capacity=0,
                   recovery_available=True, recovery_cost=4)
        for fixture in fixtures(c):
            result = run_episode(c, fixture, Policy("recover", recovery="if_missing"))
            self.assertTrue(result.success)
            self.assertTrue(result.recovery_attempted)
            self.assertEqual(result.cost_units, 7 + c.delay + 4)
            expected = fixture.revision if fixture.target == fixture.candidates[0] else next(
                r for r in fixture.receipts if r.key == fixture.target)
            self.assertEqual(result.package, expected)
            self.assertTrue(all(x["retained_records"] == 0 for x in result.compactions))

    def test_archive_is_inaccessible_before_requirement(self):
        c = Config(recovery_available=True, recovery_cost=3)
        env = ArtifactEnvironment(c, next(fixtures(c)))
        observation = env.step(Action("recover_receipt"))
        self.assertEqual(observation.error, "action_out_of_order")
        self.assertEqual(observation.receipts, ())
        self.assertEqual(env.cost_units, 3)
        self.assertFalse(env.recovery_attempted)

    def test_unavailable_and_repeated_recovery_are_charged(self):
        c = Config(delay=0, recovery_cost=2)
        env = ArtifactEnvironment(c, next(fixtures(c)))
        for name in ("collect_receipts", "seal_receipts", "read_manifest",
                     "process_build", "seal_build", "get_requirement"):
            env.step(Action(name))
        cost = env.cost_units
        self.assertEqual(env.step(Action("recover_receipt")).error, "recovery_unavailable")
        self.assertEqual(env.step(Action("recover_receipt")).error, "recovery_already_attempted")
        self.assertEqual(env.cost_units, cost + 4)

    def test_recovery_is_optional_and_does_not_supply_bulk_archive(self):
        c = Config(first_capacity=0, second_capacity=0, recovery_available=True)
        fixture = next(fixtures(c))
        without = run_episode(c, fixture, Policy("never"))
        with_recovery = run_episode(c, fixture, Policy("recover", recovery="if_missing"))
        self.assertFalse(without.success)
        restored = [r for event in with_recovery.trace
                    if event["observation"]["kind"] == "recovery"
                    for r in event["observation"]["receipts"]]
        self.assertEqual(len(restored), 1)
        self.assertEqual(restored[0]["key"], fixture.target)
        self.assertEqual(without.trace[:-1], with_recovery.trace[:-2])

    def test_free_recovery_and_spending_limit(self):
        c = Config(first_capacity=0, second_capacity=0, recovery_available=True, recovery_cost=0)
        result = run_episode(c, next(fixtures(c)), Policy("recover", recovery="if_missing"))
        self.assertTrue(result.success)
        self.assertEqual(result.cost_units, 7 + c.delay)
        limited = replace(c, recovery_cost=3, cost_budget=7 + c.delay + 2)
        result = run_episode(limited, next(fixtures(limited)), Policy("recover", recovery="if_missing"))
        self.assertFalse(result.success)
        self.assertEqual(result.failure, "cost_budget")
        self.assertLessEqual(result.cost_units, limited.cost_budget)
        with self.assertRaisesRegex(ValueError, "nonbinding"):
            strategy_points(limited)

    def test_paired_continuation_preserves_recovery_contract(self):
        c = Config(first_capacity=0, second_capacity=0, recovery_available=True)
        fixture = next(fixtures(c))
        checkpoint = run_episode(c, fixture, Policy("prefix"), stop_at_first_boundary=True)
        failed = run_episode(c, fixture, Policy("never"), checkpoint=checkpoint)
        recovered = run_episode(c, fixture, Policy("recover", recovery="if_missing"), checkpoint=checkpoint)
        self.assertFalse(failed.success)
        self.assertTrue(recovered.success)
        self.assertFalse(checkpoint.environment.recovery_attempted)
        self.assertEqual(recovered.cost_units - failed.cost_units, c.recovery_cost)


class ExactReferenceTests(unittest.TestCase):
    def test_reference_matches_independent_decision_tree_enumeration(self):
        for n, m in ((3, 1), (3, 2), (4, 2), (4, 3)):
            for b1 in range(n + 1):
                for b2 in range(m + 1):
                    for revise in (False, True):
                        ref = reference_plan(n, m, b1, b2, revise)
                        for inspect, actual in ((False, ref.hit_without_inspection),
                                                (True, ref.hit_with_inspection)):
                            self.assertEqual(actual, independent_tree_value(n, m, b1, b2, revise, inspect))

    def test_no_revision_matches_hypergeometric_formula(self):
        for n in range(1, 8):
            for m in range(1, n + 1):
                for b1 in range(n + 2):
                    for b2 in range(m + 2):
                        self.assertEqual(reference_plan(n, m, b1, b2).hit_without_inspection,
                                         no_revision_formula(n, m, b1, b2))

    def test_nonclairvoyant_reference_and_revision_effect(self):
        plain = reference_plan(6, 2, 2, 2)
        revised = reference_plan(6, 2, 2, 2, True)
        self.assertEqual(plain.hit_without_inspection, Fraction(1, 3))
        self.assertEqual(plain.hit_with_inspection, 1)
        self.assertEqual(revised.hit_without_inspection, Fraction(4, 5))
        self.assertEqual(set(revised.first_keys), {"job-4", "job-5"})
        self.assertEqual(reference_plan(4, 2, 4, 1).hit_with_inspection, Fraction(1, 2))

    def test_compiled_policies_attain_every_reference_endpoint(self):
        for n, m, b1, b2 in ((4, 2, 1, 2), (4, 3, 2, 1), (6, 2, 2, 2), (3, 2, 0, 0)):
            for revise in (False, True):
                c = Config(jobs=n, candidate_count=m, first_capacity=b1, second_capacity=b2,
                           revise=revise, recovery_available=True, recovery_cost=4)
                points = strategy_points(c)
                cases = list(fixtures(c))
                for inspect, recover, index in ((False, False, 0), (True, False, 1),
                                                (False, True, 2), (True, True, 3)):
                    policy = executable_policy(c, inspect=inspect, recover=recover)
                    results = [run_episode(c, f, policy) for f in cases]
                    self.assertEqual(Fraction(sum(r.success for r in results), len(results)), points[index].success)
                    self.assertEqual(Fraction(sum(r.cost_units - 7 - c.delay for r in results), len(results)),
                                     points[index].cost)

    def test_frontier_matches_all_two_strategy_mixtures(self):
        for revise in (False, True):
            for probe in (1, 2, 5):
                for recovery in (0, 1, 3, 8):
                    points = strategy_points(Config(revise=revise, probe_cost=probe,
                                                    recovery_available=True, recovery_cost=recovery))
                    for budget in (Fraction(i, 4) for i in range(33)):
                        feasible = [p.success for p in points if p.cost <= budget]
                        for a, b in combinations(points, 2):
                            if a.cost > b.cost:
                                a, b = b, a
                            if a.cost <= budget < b.cost:
                                w = (budget - a.cost) / (b.cost - a.cost)
                                feasible.append((1 - w) * a.success + w * b.success)
                        self.assertEqual(success_at_budget(points, budget), max(feasible))

    def test_recovery_can_dominate_inspection(self):
        c = Config(revise=False, recovery_available=True, recovery_cost=1, probe_cost=1)
        hull = efficient_vertices(strategy_points(c))
        self.assertEqual([(p.cost, p.success) for p in hull],
                         [(0, Fraction(1, 3)), (Fraction(2, 3), 1)])
        c = replace(c, recovery_cost=4)
        hull = efficient_vertices(strategy_points(c))
        self.assertEqual(hull[-1].cost, 1)
        self.assertEqual(hull[-1].strategy, "inspect")

    def test_unavailable_inspection_and_capacity_monotonicity(self):
        c = Config(probe_available=False)
        self.assertEqual(len(strategy_points(c)), 1)
        with self.assertRaises(ValueError):
            executable_policy(c, inspect=True)
        for revise in (False, True):
            for b in range(6):
                low, high = reference_plan(6, 3, b, 2, revise), reference_plan(6, 3, b + 1, 2, revise)
                self.assertLessEqual(low.hit_without_inspection, high.hit_without_inspection)
                self.assertLessEqual(low.hit_with_inspection, high.hit_with_inspection)


if __name__ == "__main__":
    unittest.main()
