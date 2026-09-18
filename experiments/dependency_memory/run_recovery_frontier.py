"""Generate exact restricted frontiers and execute their endpoint witnesses."""

import argparse
import csv
from dataclasses import asdict, replace
from fractions import Fraction
import hashlib
from itertools import combinations, product
import json
from pathlib import Path

from artifact_workflow import Config, Fixture, POLICIES, Receipt, run_episode
from recovery_frontier import efficient_vertices, executable_policy, reference_plan, strategy_points


def scenarios():
    base = Config(revise=False, recovery_available=True, recovery_cost=4)
    return {
        "cheap_recovery": replace(base, recovery_cost=1),
        "costly_recovery": base,
        "revision_cheap_recovery": replace(base, revise=True),
        "revision_costly_recovery": replace(base, revise=True, recovery_cost=8),
        "ample_parent": replace(base, first_capacity=6),
        "small_child": replace(base, second_capacity=1),
        "uninformative_manifest": replace(base, candidate_count=6),
        "inspection_unavailable": replace(base, probe_available=False),
        "recovery_unavailable": replace(base, recovery_available=False),
        "anticipate_revision": replace(base, revise=True, first_capacity=1),
    }


def route_fixtures(config):
    # Contents are fixed across routes and irrelevant to reference decisions.
    # These deterministic payloads are not cryptographic secrets or model trials.
    receipts = tuple(Receipt(f"job-{i}", 1, hashlib.sha256(f"receipt-v2:{i}".encode()).hexdigest()[:32])
                     for i in range(config.jobs))
    for candidates in combinations(sorted(r.key for r in receipts), config.candidate_count):
        revision = Receipt(candidates[0], 2, "f" * 32) if config.revise else None
        for target in candidates:
            yield Fixture(receipts, candidates, target, revision)


def point_dict(point):
    return {"strategy": point.strategy, "incremental_cost": str(point.cost), "success": str(point.success)}


def diagnostics():
    rows, cases = [], []
    for name, config in scenarios().items():
        fixtures = tuple(route_fixtures(config))
        points = strategy_points(config)
        ref = reference_plan(config.jobs, config.candidate_count, config.first_capacity,
                             config.second_capacity, config.revise)
        policies = [executable_policy(config, inspect=i, recover=r)
                    for i, r in product((False, True), repeat=2)
                    if (not i or config.probe_available) and (not r or config.recovery_available)]
        policies += list(POLICIES)
        policies += [replace(POLICIES[1], name="structured_never_recover", recovery="if_missing"),
                     replace(POLICIES[2], name="structured_always_recover", recovery="if_missing")]
        aggregates = []
        for policy in policies:
            episodes = [run_episode(config, f, policy) for f in fixtures]
            for index, (fixture, result) in enumerate(zip(fixtures, episodes)):
                rows.append({"scenario": name, "route_index": index,
                             "fixture_sha256": hashlib.sha256(json.dumps(asdict(fixture), sort_keys=True).encode()).hexdigest(),
                             "policy": policy.name, "success": result.success,
                             "failure": result.failure or "", "cost_units": result.cost_units,
                             "incremental_cost_units": result.cost_units - 7 - config.delay,
                             "probe_attempted": result.probe_attempted,
                             "recovery_attempted": result.recovery_attempted,
                             "peak_records": max(c["retained_records"] for c in result.compactions),
                             "peak_serialized_bytes": max(c["serialized_bytes"] for c in result.compactions)})
            p = Fraction(sum(r.success for r in episodes), len(episodes))
            cost = Fraction(sum(r.cost_units - 7 - config.delay for r in episodes), len(episodes))
            if policy.retention == "planned":
                label = ("inspect" if policy.probing == "always" else "retain")
                label += "+recover" if policy.recovery == "if_missing" else ""
                expected = next(p for p in points if p.strategy == label)
                if (cost, p) != (expected.cost, expected.success):
                    raise AssertionError(f"Executable reference mismatch: {name}, {label}")
            aggregates.append({"policy": policy.name, "success": str(p), "incremental_cost": str(cost),
                               "episodes": len(episodes)})
        cases.append({"scenario": name, "config": asdict(config),
                      "route_count": len(fixtures), "first_keys": ref.first_keys,
                      "p0": str(ref.hit_without_inspection), "p1": str(ref.hit_with_inspection),
                      "points": [point_dict(p) for p in points],
                      "frontier": [point_dict(p) for p in efficient_vertices(points)],
                      "policies": aggregates})
    # A deliberately small grid, all evaluated analytically, without model calls.
    grid = []
    for m, b1, b2, revise, probe, recovery in product((1, 2, 3, 6), (0, 1, 2, 4, 6),
                                                    (0, 1, 2, 3, 6), (False, True), (1, 2, 4), (0, 1, 2, 4, 8)):
        c = Config(candidate_count=m, first_capacity=b1, second_capacity=b2, revise=revise,
                   probe_cost=probe, recovery_available=True, recovery_cost=recovery)
        ref = reference_plan(c.jobs, m, b1, b2, revise)
        full = [p for p in strategy_points(c) if p.success == 1]
        optimum = min(p.cost for p in full)
        grid.append({"jobs": c.jobs, "candidates": m, "first_capacity": b1, "second_capacity": b2,
                     "revise": revise, "probe_cost": probe, "recovery_cost": recovery,
                     "p0": str(ref.hit_without_inspection), "p1": str(ref.hit_with_inspection),
                     "minimum_expected_extra_cost_for_success_one": str(optimum),
                     "optimal_endpoints": ";".join(p.strategy for p in full if p.cost == optimum)})
    summary = {"version": "recovery_frontier_v1", "date": "2026-09-18",
               "scope": "Exact uniform-route expectations in the declared atomic-record policy class; no LLM trials.",
               "cost_scope": "Expected incremental synthetic action units above 7+delay; not a hard-budget frontier or API dollars.",
               "source_sha256": {name: hashlib.sha256((Path(__file__).parent / name).read_bytes()).hexdigest()
                                 for name in ("artifact_workflow.py", "recovery_frontier.py", "run_recovery_frontier.py")},
               "grid_configurations": len(grid), "executed_episodes": len(rows), "scenarios": cases}
    return rows, grid, summary


def report(summary):
    lines = ["# Exact recovery comparison: development results", "", "September 18, 2026.", "",
             f"{summary['executed_episodes']} scripted episodes across ten settings check the executable reference and heuristic policies. A separate grid contains {summary['grid_configurations']} exact parameter configurations. These are constructed diagnostics, not independent task samples or LLM trials.", "",
             "Costs below are expected extra synthetic units above the common workflow cost of 10. p0/p1 are optimal hit probabilities without/with early inspection before recovery. All reported fractions are exact.", "",
             "| Setting | p0 | p1 | Inspection / recovery price | Cheapest success-one endpoint(s) | Extra cost |",
             "|---|---|---|---|---|---|"]
    for case in summary["scenarios"]:
        full = [p for p in case["points"] if p["success"] == "1"]
        best = min((Fraction(p["incremental_cost"]) for p in full), default=None)
        labels = ", ".join(p["strategy"] for p in full if Fraction(p["incremental_cost"]) == best)
        c = case["config"]
        prices = f"{c['probe_cost'] if c['probe_available'] else 'off'} / {c['recovery_cost'] if c['recovery_available'] else 'off'}"
        lines.append(f"| {case['scenario']} | {case['p0']} | {case['p1']} | {prices} | {labels or 'infeasible'} | {best if best is not None else '—'} |")
    lines += ["", "## Findings", "",
              "With six jobs, two candidates, and two record slots at each boundary, reliable recovery at price one reaches success one for an expected extra cost of 2/3. Inspection costs one and is dominated. Raising recovery price to four makes inspection the cheaper success-one choice. The break-even recovery price is 3/2 in this no-revision setting.", "",
              "The public revision schedule raises the best uninspected hit probability from 1/3 to 4/5: storing job-4 and job-5 exploits the known refresh of the smallest candidate. The inspection break-even recovery price rises to five. This is an effect of the specified scheduling distribution, not a universal benefit of revisions.", "",
              "With a one-record child and no revisions, early inspection raises pre-recovery success from 3/10 to 1/2, yet at recovery price four its one-unit charge exceeds the 4/5 expected recovery cost it avoids. Inspection helps retention while making the success-one policy more expensive. Ample parent memory and an uninformative manifest give additional null controls.", "",
              "## Evidence and scope", "",
              "[All executed outcomes](recovery_episodes.csv), [exact grid](recovery_grid.csv), and [summary with frontier vertices and source hashes](recovery_frontier_summary.json) are regenerated together. Reference endpoints are checked against actual environment runs over every candidate/target pair; tests independently enumerate small decision trees and hypergeometric probabilities.", "",
              "The frontier allows randomized policies and constrains expected extra cost, with nonbinding episode limits. It assumes reliable late recovery, opaque atomic records, a known uniform routing distribution, and the published revision rule. It does not optimize arbitrary bit encodings, model summaries, archive storage, unreliable retrieval, or unknown real-world dependencies. See the [derivation and information contract](../RECOVERY_FRONTIER.md).", ""]
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=Path(__file__).parent / "results")
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    rows, grid, summary = diagnostics()
    for filename, values in (("recovery_episodes.csv", rows), ("recovery_grid.csv", grid)):
        with (args.output / filename).open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(values[0]), lineterminator="\n")
            writer.writeheader()
            writer.writerows(values)
    (args.output / "recovery_frontier_summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8", newline="\n")
    (args.output / "recovery_frontier_report.md").write_text(report(summary), encoding="utf-8", newline="\n")
    print(json.dumps({key: summary[key] for key in ("version", "grid_configurations", "executed_episodes")}, indent=2))


if __name__ == "__main__":
    main()
