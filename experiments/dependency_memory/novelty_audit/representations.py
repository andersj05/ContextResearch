"""Finite strategy alphabets and weak coloring of forbidden unsafe groups.

This is an elementary reformulation of the existing collision auditor. It is
not a new algorithm or a scalable solver. Tool observations persist throughout
recovery, the model is public, and all costs are positive integers.
"""
from functools import cache
from itertools import product


def members(mask, n):
    return tuple(i for i in range(n) if mask & (1 << i))


def strategy_outputs(n, answers, tools, budget):
    """All world-indexed outputs of globally budget-bounded policy trees.

    Compose every combination of observation branches forward; do not consult
    accepted-action sets or the collision solver. Equal output vectors can be
    merged because all represented trees already satisfy the hard budget.
    Intended only for tiny fixtures: the Cartesian products grow very quickly.
    """
    if type(budget) is not int or budget < 0:
        raise ValueError("Budget must be a nonnegative integer")
    if not answers or n < 1:
        raise ValueError("Supply worlds and terminal answers")
    if any(type(t.cost) is not int or t.cost <= 0 or len(t.observations) != n
           for t in tools):
        raise ValueError("Supply positive-cost tools with one observation per world")
    leaves = {(answer,) * n for answer in answers}

    @cache
    def enumerate_at(remaining):
        outcomes = set(leaves)
        for tool in tools:
            if tool.cost > remaining:
                continue
            observations = sorted(set(tool.observations))
            indexes = tuple(observations.index(o) for o in tool.observations)
            children = enumerate_at(remaining - tool.cost)
            for branches in product(children, repeat=len(observations)):
                outcomes.add(tuple(branches[indexes[i]][i] for i in range(n)))
        return tuple(sorted(outcomes))

    return enumerate_at(budget)


def safe_from_strategies(n, outputs, accepted):
    """A cell is safe iff one budget-bounded strategy is accepted by all worlds."""
    return {mask for mask in range(1 << n)
            if any(all(out[i] in accepted[i] for i in members(mask, n))
                   for out in outputs)}


def minimal_obstructions(n, safe_masks):
    """Minimal unsafe sets, with the hereditary-family assumptions checked."""
    safe = set(safe_masks)
    if 0 not in safe or any(type(m) is not int or not 0 <= m < 1 << n for m in safe):
        raise ValueError("Supply a valid safe family containing the empty set")
    for mask in safe:
        if any(mask ^ (1 << i) not in safe for i in members(mask, n)):
            raise ValueError("The safe family must be downward closed")
    return tuple(mask for mask in range(1, 1 << n) if mask not in safe
                 and all(mask ^ (1 << i) in safe for i in members(mask, n)))


def weak_coloring(n, edges):
    """Enumerate restricted-growth colorings; no forbidden edge is monochromatic.

    Search color assignments directly, independently of safe-subset partition
    DP. Return None when even a singleton is forbidden. The first vertex has
    color zero; new colors appear in order, removing color-name symmetries.
    """
    if n < 1 or any(type(e) is not int or not 0 < e < 1 << n for e in edges):
        raise ValueError("Supply nonempty edges on a nonempty vertex set")
    edges = tuple(set(edges))
    if any(e.bit_count() == 1 for e in edges):
        return None
    best = tuple(range(n))

    def visit(colors, used):
        nonlocal best
        if used >= len(set(best)):
            return
        if len(colors) == n:
            best = colors
            return
        for color in range(used + 1):
            candidate = colors + (color,)
            assigned = (1 << len(candidate)) - 1
            if any(e & assigned == e and len({candidate[i] for i in members(e, n)}) == 1
                   for e in edges):
                continue
            visit(candidate, max(used, color + 1))

    visit((0,), 1)
    return best
