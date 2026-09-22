"""Reproduce the finite representation checks, with zero model calls.

python -m experiments.dependency_memory.novelty_audit.run
"""
from copy import deepcopy
import hashlib
from itertools import combinations, product
import json
from pathlib import Path

from experiments.dependency_memory.collision_audit.engine import (
    Problem, Solver, canonical, minimum_repair_partition)
from experiments.dependency_memory.collision_audit.fixtures import (
    compatibility, diagnostic_specs, tool)
from .representations import (members, minimal_obstructions, safe_from_strategies,
                              strategy_outputs, weak_coloring)


HERE = Path(__file__).resolve().parent
RESULTS = HERE.parent / "results"


def check_fixture(spec):
    p = Problem(spec)
    solvers = [Solver(p, task) for task in p.tasks]
    cells = []
    for cell in p.cells:
        n = len(cell)
        safe = {0} | {mask for mask in range(1, 1 << n)
                      if all(s.optimum(tuple(cell[i] for i in members(mask, n)))[0] <= p.budget
                             for s in solvers)}
        edges = minimal_obstructions(n, safe)
        # Reconstruct the entire safe family from only its forbidden antichain.
        reconstructed = {mask for mask in range(1 << n)
                         if not any(e & mask == e for e in edges)}
        if reconstructed != safe:
            raise AssertionError("Obstruction hypergraph changed the safe family")
        colors = weak_coloring(n, edges)
        color_count = len(set(colors))
        partition = minimum_repair_partition(cell, solvers, p.budget)
        if color_count != len(partition):
            raise AssertionError("Weak coloring and repair-state optimum disagree")
        cells.append({"worlds": list(cell), "nonempty_subsets_checked": (1 << n) - 1,
                      "minimal_unsafe_groups": [[cell[i] for i in members(e, n)] for e in edges],
                      "weak_coloring": list(colors), "minimum_colors": color_count,
                      "minimum_repair_states": len(partition)})
    return {"name": p.name, "budget": p.budget, "cells": cells,
            "extra_message_states": max(c["minimum_colors"] for c in cells)}


def check_small_tables():
    """343 nonempty three-world answer relations, each at budgets 0, 1, 2."""
    spec = compatibility()
    spec["tools"] = [tool("first", 1, [0, 1, 1]), tool("second", 1, [1, 0, 1])]
    template = Problem(spec)
    output_sets = [strategy_outputs(3, "ABC", template.tools, b) for b in range(3)]
    answer_sets = [list(c) for size in range(1, 4) for c in combinations("ABC", size)]
    digest = hashlib.sha256()
    subset_checks = coloring_checks = 0
    for accepted in product(answer_sets, repeat=3):
        data = deepcopy(spec)
        data["tasks"][0]["accepted"] = {f"w{i}": values for i, values in enumerate(accepted)}
        p = Problem(data)
        solver = Solver(p, p.tasks[0])
        for budget, outputs in enumerate(output_sets):
            safe = safe_from_strategies(3, outputs, accepted)
            expected = {0} | {m for m in range(1, 8)
                              if solver.optimum(members(m, 3))[0] <= budget}
            if safe != expected:
                raise AssertionError("Forward strategy alphabet and recovery DP disagree")
            edges = minimal_obstructions(3, safe)
            reconstructed = {m for m in range(8) if not any(e & m == e for e in edges)}
            if safe != reconstructed:
                raise AssertionError("Minimal obstructions do not describe all safe sets")
            colors = weak_coloring(3, edges)
            states = len(minimum_repair_partition((0, 1, 2), [solver], budget))
            if len(set(colors)) != states:
                raise AssertionError("Strategy-derived colors disagree with repair DP")
            digest.update((canonical([accepted, budget, sorted(safe), edges, states]) + "\n").encode())
            subset_checks += 7
            coloring_checks += 1
    return {"accepted_action_tables": 343, "budgets": [0, 1, 2],
            "distinct_strategy_output_vectors_by_budget": list(map(len, output_sets)),
            "nonempty_subset_budget_checks": subset_checks,
            "coloring_checks": coloring_checks, "comparison_sha256": digest.hexdigest()}


def certificate():
    specs = diagnostic_specs()
    return {"schema": 1, "date": "2026-09-22", "model_calls": 0,
            "evidence": "elementary representation equivalence with finite checks; no novelty claim",
            "source_sha256": {name: hashlib.sha256((HERE / name).read_bytes()).hexdigest()
                              for name in ("representations.py", "run.py")},
            "fixture_specifications_sha256": hashlib.sha256(canonical(specs).encode()).hexdigest(),
            "small_strategy_check": check_small_tables(),
            "fixture_checks": [check_fixture(spec) for spec in specs]}


def report(data):
    small = data["small_strategy_check"]
    lines = ["# Novelty audit: finite representation checks", "",
             "September 22, 2026. Elementary reductions, not a new algorithm or model experiment.", "",
             "A recovery policy can be treated as an output symbol. A group is safe when",
             "some budget-bounded policy is valid in every member. Minimal unsafe groups",
             "form forbidden hyperedges; memory labels are a weak coloring of those edges.", "",
             f"Forward enumeration checks {small['accepted_action_tables']} accepted-action tables",
             f"at budgets {small['budgets']}: {small['nonempty_subset_budget_checks']:,} nonempty",
             f"subset/budget checks and {small['coloring_checks']:,} repair-coloring checks.",
             f"Distinct policy output vectors at these budgets: {small['distinct_strategy_output_vectors_by_budget']}.", "",
             "These reuse the September 21 three-world domain, extending its independent",
             "checks to the strategy and forbidden-hyperedge representations. They are not",
             "new independent tasks or additional model trials.", "",
             "| Existing fixture | Budget | Minimum repair states | Minimal unsafe groups |",
             "|---|---:|---:|---:|"]
    for row in data["fixture_checks"]:
        lines.append(f"| {row['name']} | {row['budget']} | {row['extra_message_states']} | "
                     f"{sum(len(c['minimal_unsafe_groups']) for c in row['cells'])} |")
    lines += ["", "The fixture checks derive feasibility from the existing recovery DP, then",
              "compare an independent color-assignment search with its repair partition DP.",
              "Only the three-world check also derives feasibility by forward policy enumeration.", "",
              "For the pairwise-compatible triple, the single forbidden edge is the entire",
              "triple. Two colors suffice. Replacing that edge by all pair conflicts would",
              "incorrectly demand three colors; retaining only genuinely unsafe pairs would",
              "incorrectly allow one. Higher-order compatibility matters, but is established",
              "hypergraph structure rather than a new information principle.", "",
              "Scope: finite public models, deterministic read-only tools, positive integer",
              "costs, worst-case zero error, exact retained/public equality, and no additional",
              "memory boundary during recovery. Fixed state labels exclude shared codebook size",
              "and are not token or byte budgets. No source-coding rate theorem is imported.", "",
              "[Novelty verdict and derivation](../../../research/FEEDBACK_NOVELTY_AUDIT_2026-09-22.md).", ""]
    return "\n".join(lines)


def main():
    data = certificate()
    (RESULTS / "feedback_novelty_certificate.json").write_text(
        json.dumps(data, indent=2) + "\n", encoding="utf-8", newline="\n")
    (RESULTS / "feedback_novelty_report.md").write_text(report(data), encoding="utf-8", newline="\n")
    small = data["small_strategy_check"]
    print(f"Checked {small['nonempty_subset_budget_checks']} strategy/subset comparisons, "
          f"{small['coloring_checks']} small colorings and {len(data['fixture_checks'])} fixtures.")


if __name__ == "__main__":
    main()
