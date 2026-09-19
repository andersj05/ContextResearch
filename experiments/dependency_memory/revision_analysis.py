"""Offline, same-public-view grading of saved parent and child selections.

No model is called. An uninspected fixed parent is graded on the full uniform
route population with optimal downstream record selection. A manifest already
visible in the first request instead conditions that population; the saved
answer does not define a model policy for other manifests.
"""

from __future__ import annotations

import argparse
from collections import Counter
from fractions import Fraction
import hashlib
from itertools import combinations
import json
from math import comb
from pathlib import Path

from artifact_workflow import Config
from pilot_interface import (infer_candidates, request_bytes,
                             validate_retention_response)


VERSION = "revision_parent_analysis_v1"
HERE = Path(__file__).resolve().parent
DEFAULT_RUN = HERE / "results" / "luna_development_2026-09-19"


def subsets(keys, capacity):
    return (part for size in range(min(len(keys), capacity) + 1)
            for part in combinations(keys, size))


def _dimensions(config, first, known_candidates):
    if not isinstance(config, Config) or config.jobs > 10:
        raise ValueError("Analysis requires a validated Config with at most ten jobs")
    keys = tuple(sorted(f"job-{i}" for i in range(config.jobs)))
    if len(first) != len(set(first)) or not set(first) <= set(keys):
        raise ValueError("Parent keys must be distinct public job keys")
    if len(first) > config.first_capacity:
        raise ValueError("Parent exceeds first capacity")
    if known_candidates is not None:
        if (tuple(known_candidates) != tuple(sorted(set(known_candidates)))
                or len(known_candidates) != config.candidate_count
                or not set(known_candidates) <= set(keys)):
            raise ValueError("Known candidates must be the canonical public manifest")
    return keys


def parent_value(config, first, known_candidates=None):
    """Return exact ideal-child availability and number of possible target routes."""
    keys = _dimensions(config, first, known_candidates)
    manifests = ((tuple(known_candidates),) if known_candidates is not None
                 else tuple(combinations(keys, config.candidate_count)))
    retained = set(first)
    hits = 0
    for manifest in manifests:
        available = retained.intersection(manifest)
        if config.revise:
            available.add(manifest[0])
        hits += min(config.second_capacity, len(available))
    routes = len(manifests) * config.candidate_count
    return Fraction(hits, routes), routes


def best_parent(config, known_candidates=None):
    """Enumerate all permitted parents, including underfilled records and ties."""
    keys = _dimensions(config, (), known_candidates)
    best, winners, checked = Fraction(-1), [], 0
    for first in subsets(keys, config.first_capacity):
        checked += 1
        value, _ = parent_value(config, first, known_candidates)
        if value > best:
            best, winners = value, [first]
        elif value == best:
            winners.append(first)
    return best, tuple(winners), checked


def pair_formula(jobs, first_ranks, second_capacity, revise):
    """Independent closed form for two candidates and a fixed parent.

    Ranks are zero-based *lexicographic* ranks, not arbitrary numeric labels.
    For a revised pair with two child slots the smaller candidate is always
    refreshed, and retained rank j is the larger candidate in j pairs.
    """
    if (type(jobs) is not int or jobs < 2 or type(second_capacity) is not int
            or second_capacity < 0 or type(revise) is not bool):
        raise ValueError("Invalid pair dimensions")
    ranks = tuple(first_ranks)
    if (any(type(i) is not int or not 0 <= i < jobs for i in ranks)
            or len(set(ranks)) != len(ranks)):
        raise ValueError("Ranks must be distinct integers within the public order")
    if second_capacity == 0:
        return Fraction(0)
    if revise:
        if second_capacity == 1:
            return Fraction(1, 2)
        return Fraction(1, 2) + Fraction(sum(ranks), jobs * (jobs - 1))
    if second_capacity == 1:
        return Fraction(comb(jobs, 2) - comb(jobs - len(ranks), 2), jobs * (jobs - 1))
    return Fraction(len(ranks), jobs)


def grade_parent(request, response):
    retained = validate_retention_response(response, request)
    if request["boundary"] != 1:
        raise ValueError("Parent analysis requires boundary one")
    config = Config(**request["config"])
    keys = tuple(r.key for r in retained)
    if (len(request["visible_records"]) != config.jobs
            or any(r["revision"] != 1 for r in request["visible_records"])):
        raise ValueError("Analysis requires all initial current receipts at the first boundary")
    manifests = [infer_candidates(event, request["public_metadata"])
                 for event in request["observations"] if event["kind"] == "manifest"]
    if len(manifests) > 1:
        raise ValueError("Ambiguous first-boundary public manifest")
    known = manifests[0] if manifests else None
    actual, routes = parent_value(config, keys, known)
    best, winners, checked = best_parent(config, known)
    gap = best - actual
    return {
        "first_keys": list(keys), "config": request["config"],
        "conditioning": "observed_manifest" if known is not None else "all_unrevealed_manifests",
        "known_candidates": list(known) if known is not None else None,
        "route_count": routes, "ideal_child_availability": str(actual),
        "best_same_view_availability": str(best), "availability_gap": str(gap),
        "recovery_cost_gap_synthetic_units": str(gap * config.recovery_cost),
        "population_optimal_parent": gap == 0,
        "parent_sets_checked": checked, "optimal_parent_set_count": len(winners),
        "one_optimal_parent": list(winners[0]),
        "optimal_full_capacity_parent_count": sum(len(s) == min(config.first_capacity, config.jobs)
                                                   for s in winners),
    }


def grade_observed_child(request, response):
    retained = validate_retention_response(response, request)
    if request["boundary"] != 2:
        raise ValueError("Child analysis requires boundary two")
    config = Config(**request["config"])
    manifests = [infer_candidates(event, request["public_metadata"])
                 for event in request["observations"] if event["kind"] == "manifest"]
    if len(manifests) != 1:
        raise ValueError("Child view must reveal exactly one manifest")
    candidates = manifests[0]
    def current(receipt):
        return receipt["key"] in candidates and receipt["revision"] == (
            2 if config.revise and receipt["key"] == candidates[0] else 1)
    available = {r["key"] for r in request["visible_records"] if current(r)}
    chosen = {r.key for r in retained if r.key in available}
    best = Fraction(min(config.second_capacity, len(available)), config.candidate_count)
    actual = Fraction(len(chosen), config.candidate_count)
    return {"candidates": list(candidates), "available_candidate_keys": sorted(available),
            "chosen_candidate_keys": sorted(chosen), "route_count": config.candidate_count,
            "conditional_availability": str(actual), "best_same_view_availability": str(best),
            "availability_gap": str(best - actual), "same_view_optimal": actual == best}


def dimension_controls():
    """Small exact offline controls, deliberately not additional model outcomes."""
    rows = []
    for revise in (False, True):
        for first_capacity in (0, 1, 2, 6):
            for second_capacity in (0, 1, 2, 6):
                config = Config(first_capacity=first_capacity, second_capacity=second_capacity,
                                revise=revise)
                best, winners, checked = best_parent(config)
                values = Counter()
                for first in combinations(tuple(f"job-{i}" for i in range(6)), first_capacity):
                    value, routes = parent_value(config, first)
                    formula = pair_formula(6, (int(k[4:]) for k in first), second_capacity, revise)
                    if formula != value:
                        raise AssertionError("Pair formula disagrees with enumerated route objective")
                    values[str(value)] += 1
                rows.append({"revise": revise, "first_capacity": first_capacity,
                             "second_capacity": second_capacity, "route_count": routes,
                             "best_availability": str(best), "parent_sets_checked": checked,
                             "optimal_parent_set_count": len(winners),
                             "full_capacity_value_distribution": dict(sorted(values.items(),
                                                                             key=lambda item: Fraction(item[0])))})
    return rows


def analyze(run_dir=DEFAULT_RUN):
    run_dir = Path(run_dir)
    ledger_path, summary_path = run_dir / "requests.jsonl", run_dir / "summary.json"
    ledger = [json.loads(line) for line in ledger_path.read_text(encoding="utf-8").splitlines()]
    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    if summary.get("fake") or summary.get("heldout_requests") != 0:
        raise ValueError("Expected completed real development evidence, without held-out calls")
    by_id = {}
    for row in ledger:
        identity = row["evaluator_id"]
        if identity in by_id:
            raise ValueError("Duplicate evaluator request id")
        payload = request_bytes(json.loads(row["request_utf8"]))
        if (payload.decode() != row["request_utf8"]
                or hashlib.sha256(payload).hexdigest() != row["request_sha256"]):
            raise ValueError("Public request failed canonical content/hash verification")
        by_id[identity] = row
    results = []
    for episode in sorted(summary["stage_b"], key=lambda row: row["episode_id"]):
        if episode["status"] != "completed":
            raise ValueError("This analysis requires completed episodes; no silent exclusion")
        requests = [by_id[episode["episode_id"] + f"/retain-{boundary}"] for boundary in (1, 2)]
        if any(row["status"] != "completed" for row in requests):
            raise ValueError("Retention request is not completed")
        first, second = (json.loads(row["request_utf8"]) for row in requests)
        parent = grade_parent(first, requests[0]["response"])
        child = grade_observed_child(second, requests[1]["response"])
        if (episode["inspection"] != (parent["known_candidates"] is not None)
                or first["config"] != second["config"]
                or first["render_mode"] != episode["render_mode"]
                or second["render_mode"] != first["render_mode"]):
            raise ValueError("Saved summary and public inspection/configuration views disagree")
        results.append({"episode_id": episode["episode_id"], "scenario": episode["scenario"],
                        "arm": episode["arm"], "render_mode": episode["render_mode"],
                        "actual_pre_recovery_available": episode["pre_recovery_available"],
                        "parent": parent, "observed_child": child})
    parent_request_ids = {identity.removesuffix("/retain-1") for identity, row in by_id.items()
                          if identity.endswith("/retain-1")}
    if parent_request_ids != {row["episode_id"] for row in results}:
        raise ValueError("Saved parent requests and analyzed episode ids do not match")
    full = [row for row in results if row["parent"]["known_candidates"] is None]
    conditional = [row for row in results if row["parent"]["known_candidates"] is not None]
    deficits = [row for row in results if not row["parent"]["population_optimal_parent"]]
    return {"version": VERSION, "date": "2026-09-19", "new_model_requests": 0,
            "source_sha256": {"requests.jsonl": hashlib.sha256(ledger_path.read_bytes()).hexdigest(),
                              "summary.json": hashlib.sha256(summary_path.read_bytes()).hexdigest(),
                              "revision_analysis.py": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                              "artifact_workflow.py": hashlib.sha256((HERE / "artifact_workflow.py").read_bytes()).hexdigest(),
                              "pilot_interface.py": hashlib.sha256((HERE / "pilot_interface.py").read_bytes()).hexdigest()},
            "method": "Exact fixed-parent grading with optimal downstream selection; same observed public view",
            "counts": {"saved_parent_selections": len(results),
                       "full_population_parent_selections": len(full),
                       "manifest_conditioned_parent_selections": len(conditional),
                       "strict_parent_deficits": len(deficits),
                       "full_population_strict_deficits": sum(not r["parent"]["population_optimal_parent"] for r in full),
                       "manifest_conditioned_strict_deficits": sum(not r["parent"]["population_optimal_parent"] for r in conditional),
                       "observed_child_selections": len(results),
                       "strict_observed_child_deficits": sum(not r["observed_child"]["same_view_optimal"] for r in results)},
            "limitations": ["Offline reuse of one development route, not new model trials or a population estimate of the model policy.",
                            "Unknown counterfactual child actions are replaced by declared ideal downstream selection.",
                            "Inspected parents are graded only conditional on their observed manifest; no unseen-manifest answers are invented.",
                            "Exact gaps isolate parent choice at fixed inspection and visible information, not end-to-end inspection regret.",
                            "All old run artifacts remain unchanged; no held-out evidence or native-harness comparison."],
            "selections": results, "dimension_controls": dimension_controls()}


def report(result):
    counts = result["counts"]
    deficits = [row for row in result["selections"] if not row["parent"]["population_optimal_parent"]]
    lines = ["# Revision-aware retention: offline analysis of the completed Luna run", "",
             "September 19, 2026. This analysis reuses the saved development requests. It makes **zero new model calls** and leaves the original run unchanged.", "",
             f"All **{counts['saved_parent_selections']} first-boundary selections** were graded against the best atomic-record parent with the same inspection choice and public view. "
             f"The {counts['full_population_parent_selections']} uninspected selections each face all 30 equiprobable candidate/target routes. "
             f"For the {counts['manifest_conditioned_parent_selections']} inspected selections, the visible manifest fixes the pair, leaving two possible targets. "
             "Grading those answers across unobserved manifests would invent counterfactual model behavior.", "",
             f"There are **{counts['strict_parent_deficits']} strict parent-selection deficits**, all in uninspected revision cases. "
             f"The other {counts['saved_parent_selections'] - counts['strict_parent_deficits']} selections attain their same-view ideal-child reference. "
             f"All {counts['observed_child_selections']} observed second-boundary selections are optimal conditional on the records actually visible there; "
             "this does not establish optimal child choices on unseen routes.", "",
             "| Scenario | Rendering | First keys | Exact availability | Best same-view availability | Availability gap | Expected recovery-cost gap |",
             "|---|---|---|---|---|---|---|"]
    for row in deficits:
        p = row["parent"]
        lines.append(f"| {row['scenario']} | {row['render_mode']} | {', '.join(p['first_keys'])} | {p['ideal_child_availability']} | {p['best_same_view_availability']} | {p['availability_gap']} | {p['recovery_cost_gap_synthetic_units']} |")
    lines.extend(["", "The cost gaps use each row's recovery price and hold inspection fixed. They are exact losses of these fixed parent choices with an optimal child selector, not estimates of total model-policy regret. "
                  "Pooling the three gaps across reused prompts would not create independent trials.", "",
                  "## Why the public revision rule changes the best parent", "",
                  "Let n jobs be ordered lexicographically with ranks 0 through n−1. A pair is uniform among all unordered pairs, and its final target is uniform within the pair. "
                  "With at least two child slots, no revision, and a fixed retained set F, ideal downstream availability is |F|/n: all equal-size parent sets tie. "
                  "With revision of the smaller candidate, the refreshed target supplies 1/2 availability independently of F. A retained rank j is the unrevised larger candidate in exactly j pairs, so", "",
                  "```text\np(F; revised, child capacity ≥ 2) = 1/2 + sum(j for j in F) / [n(n−1)].\n```", "",
                  "For n=6 and two parent slots, ranks 4 and 5 uniquely maximize this expression at 4/5. Ranks 0 and 1 give 8/15; ranks 1 and 2 give 3/5. "
                  "Thus choosing the smallest keys is harmless under the symmetric no-revision population but strictly worse under this particular revision schedule.", "",
                  "With one child slot and no revision, availability is [C(n,2) − C(n−|F|,2)] / [n(n−1)]; equal-size parents still tie. "
                  "With one child slot and revision it is exactly 1/2 for every parent, because one fresh candidate is always available and the second boundary can retain only one. "
                  "Zero child capacity gives zero availability. Six parent slots preserve all initial records; child capacity then supplies the binding limit. "
                  "The JSON includes all 32 combinations of revision on/off and parent/child capacities 0, 1, 2, and 6, with full-capacity value distributions. These are offline controls, not model observations.", "",
                  "## Every saved selection", "",
                  "`Population` means all 30 routes before any manifest; `Manifest` means the two targets of the already visible pair. "
                  "The exact fractions assume optimal downstream retention. Actual availability is the outcome on the single realized route.", "",
                  "| Scenario | Rendering | Arm | View | First keys | Exact / best | Parent gap | Actual available | Child gap on observed view |",
                  "|---|---|---|---|---|---|---|---|---|"])
    for row in result["selections"]:
        p, child = row["parent"], row["observed_child"]
        view = "Population" if p["known_candidates"] is None else "Manifest"
        keys = ", ".join(key.removeprefix("job-") for key in p["first_keys"])
        lines.append(f"| {row['scenario']} | {row['render_mode']} | {row['arm']} | {view} | {keys} | {p['ideal_child_availability']} / {p['best_same_view_availability']} | {p['availability_gap']} | {row['actual_pre_recovery_available']} | {child['availability_gap']} |")
    lines.extend(["", "The three inspected small-child episodes that missed the realized target are target tie outcomes, not conditional expectation deficits. "
                  "The no-inspection, no-revision choices likewise cannot be called parent errors merely because their chosen pair missed this route. "
                  "The strict revision deficits are different: their ranking is worse across the declared population, even before knowing the realized pair.", "",
                  "## Reproduction and limits", "",
                  "```powershell\npython experiments/dependency_memory/revision_analysis.py\npython -m unittest discover -s experiments/dependency_memory -p test_revision_analysis.py -v\n```", "",
                  "Source requests and summaries are hashed in [the JSON certificate](revision_analysis.json). Original evidence is in [the Luna run report](luna_development_2026-09-19/report.md). "
                  "The calculations distinguish first-boundary loss from second-boundary choice using saved public requests only. "
                  "They do not identify model reasoning, establish a population success rate for its unobserved policy, measure a new intervention, or use held-out tasks.", ""])
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-dir", type=Path, default=DEFAULT_RUN)
    parser.add_argument("--output", type=Path, default=HERE / "results" / "revision_analysis.json")
    parser.add_argument("--report", type=Path, default=HERE / "results" / "revision_analysis_report.md")
    args = parser.parse_args()
    result = analyze(args.run_dir)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    args.report.write_text(report(result), encoding="utf-8")
    print(json.dumps(result["counts"], sort_keys=True))


if __name__ == "__main__":
    main()
