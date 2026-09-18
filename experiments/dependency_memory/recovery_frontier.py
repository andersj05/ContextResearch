"""Exact finite reference for declared record selection, inspection, and recovery.

Uniform candidate subsets, a uniform final target within each subset, optional
refresh of the lexicographically first candidate. No access to an instance's
future route is supplied to reference_plan(). See RECOVERY_FRONTIER.md.
"""

from dataclasses import dataclass
from fractions import Fraction
from functools import lru_cache
from itertools import combinations
from math import comb

from artifact_workflow import Config, Policy


@dataclass(frozen=True)
class Reference:
    hit_without_inspection: Fraction
    hit_with_inspection: Fraction
    first_keys: tuple[str, ...]
    parent_sets_checked: int
    candidate_sets: int


@dataclass(frozen=True)
class Point:
    cost: Fraction
    success: Fraction
    strategy: str


def _available(first, candidates, revise):
    keys = set(first).intersection(candidates)
    if revise:
        keys.add(candidates[0])
    return keys


@lru_cache(maxsize=None)
def reference_plan(jobs, candidate_count, first_capacity, second_capacity, revise=False):
    # Validate dimensions with the environment's own public contract.
    c = Config(jobs=jobs, candidate_count=candidate_count, first_capacity=first_capacity,
               second_capacity=second_capacity, revise=revise)
    if c.jobs > 10:
        raise ValueError("Exact reference is restricted to at most ten jobs")
    size = min(c.first_capacity, c.jobs)
    search_size = comb(c.jobs, size) * comb(c.jobs, c.candidate_count)
    if search_size > 250_000:
        raise ValueError("Exact reference is restricted to small instances")
    keys = tuple(sorted(f"job-{i}" for i in range(c.jobs)))
    manifests = tuple(combinations(keys, c.candidate_count))
    best_total, best_first, checked = -1, (), 0
    # A single first set must work across ALL unrevealed manifests.
    for first in combinations(keys, size):
        checked += 1
        total = sum(min(c.second_capacity, len(_available(first, a, c.revise))) for a in manifests)
        if total > best_total:
            best_total, best_first = total, first
    hit0 = Fraction(best_total, len(manifests) * c.candidate_count)
    # With an early manifest, avoid the receipt that will be refreshed for free.
    available = min(c.first_capacity, c.candidate_count - int(c.revise)) + int(c.revise)
    hit1 = Fraction(min(c.second_capacity, available), c.candidate_count)
    return Reference(hit0, hit1, best_first, checked, len(manifests))


def no_revision_formula(jobs, candidates, first_capacity, second_capacity):
    """Independent hypergeometric formulation, not used in reference_plan."""
    b = min(first_capacity, jobs)
    lower, upper = max(0, candidates - (jobs - b)), min(b, candidates)
    numerator = sum(comb(b, h) * comb(jobs - b, candidates - h) * min(second_capacity, h)
                    for h in range(lower, upper + 1))
    return Fraction(numerator, comb(jobs, candidates) * candidates)


def strategy_points(config: Config):
    mandatory = 7 + config.delay
    extra_cost = (config.probe_cost if config.probe_available else 0)
    extra_cost += config.recovery_cost if config.recovery_available else 0
    extra_calls = int(config.probe_available) + int(config.recovery_available)
    if config.cost_budget < mandatory + extra_cost or config.call_limit < mandatory + extra_calls:
        raise ValueError("Reference requires nonbinding episode cost and call limits")
    ref = reference_plan(config.jobs, config.candidate_count, config.first_capacity,
                         config.second_capacity, config.revise)
    points = [Point(Fraction(0), ref.hit_without_inspection, "retain")]
    if config.probe_available:
        points.append(Point(Fraction(config.probe_cost), ref.hit_with_inspection, "inspect"))
    if config.recovery_available:
        for point in tuple(points):
            points.append(Point(point.cost + (1 - point.success) * config.recovery_cost,
                                Fraction(1), point.strategy + "+recover"))
    return tuple(points)


def efficient_vertices(points):
    """Upper success / lower expected-cost convex frontier (mixing permitted)."""
    by_cost = {}
    for p in points:
        if p.cost not in by_cost or p.success > by_cost[p.cost].success:
            by_cost[p.cost] = p
    nondominated = []
    best_success = Fraction(-1)
    for p in sorted(by_cost.values(), key=lambda x: x.cost):
        if p.success > best_success:
            nondominated.append(p)
            best_success = p.success
    hull = []
    for p in nondominated:
        while len(hull) >= 2:
            a, b = hull[-2:]
            # Slopes must decrease; remove collinear interior points too.
            if (b.success - a.success) * (p.cost - b.cost) > (p.success - b.success) * (b.cost - a.cost):
                break
            hull.pop()
        hull.append(p)
    return tuple(hull)


def success_at_budget(points, budget):
    budget = Fraction(budget)
    if budget < 0:
        raise ValueError("Negative expected incremental budget")
    hull = efficient_vertices(points)
    if not hull or budget < hull[0].cost:
        raise ValueError("No feasible strategy")
    for a, b in zip(hull, hull[1:]):
        if budget < b.cost:
            return a.success + (budget - a.cost) * (b.success - a.success) / (b.cost - a.cost)
    return hull[-1].success


def executable_policy(config, *, inspect=False, recover=False):
    """Compile public distribution parameters to a fixed, non-clairvoyant policy."""
    ref = reference_plan(config.jobs, config.candidate_count, config.first_capacity,
                         config.second_capacity, config.revise)
    if inspect and not config.probe_available:
        raise ValueError("Cannot compile inspection when unavailable")
    if recover and not config.recovery_available:
        raise ValueError("Cannot compile recovery when unavailable")
    return Policy("reference" + ("_inspect" if inspect else "_retain") + ("_recover" if recover else ""),
                  probing="always" if inspect else "never", retention="planned",
                  recovery="if_missing" if recover else "never",
                  first_keys=ref.first_keys, skip_refresh=config.revise)
