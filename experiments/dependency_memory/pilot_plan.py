"""Generate an offline pilot schedule and exact calibration; never call a model.

The manifest is evaluator-side planning material, not a model prompt. Renderers,
the isolated adapter, exact provider revision, and spending remain launch gates.
"""

import argparse
from dataclasses import asdict
from fractions import Fraction
import hashlib
import json
from pathlib import Path
import random

from artifact_workflow import run_episode
from recovery_frontier import executable_policy, reference_plan
from run_recovery_frontier import route_fixtures, scenarios


SCENARIOS = (
    "cheap_recovery", "costly_recovery", "revision_cheap_recovery",
    "revision_costly_recovery", "ample_parent", "small_child",
)
ARMS = ("never_inspect", "always_inspect", "model_selective")
RENDER_MODES = ("explicit_labels", "inferred_dependencies")
FAMILIES = {
    "development": ("direct_artifact_tags",),
    "heldout": ("alias_chain", "package_prerequisites", "validation_scope", "deployment_handoff"),
}
SEEDS = {
    "development_route": 2026091901,
    "heldout_route": 2026091902,
    "payload_root": 2026091903,
    "template_render": 2026091904,
    "call_order": 2026091905,
}


def calibration():
    """Optimal atomic retention only; these labels do not assume model skill."""
    configs = scenarios()
    rows = []
    for name in SCENARIOS:
        c = configs[name]
        ref = reference_plan(c.jobs, c.candidate_count, c.first_capacity, c.second_capacity, c.revise)
        p0, p1 = ref.hit_without_inspection, ref.hit_with_inspection
        cost0 = (1 - p0) * c.recovery_cost
        cost1 = c.probe_cost + (1 - p1) * c.recovery_cost
        best = min(cost0, cost1)
        rows.append({
            "scenario": name, "config": asdict(c), "p0": str(p0), "p1": str(p1),
            "no_inspection_extra_cost": str(cost0), "inspection_extra_cost": str(cost1),
            "optimal_extra_cost": str(best),
            "optimal_decisions": [decision for decision, value in (("skip", cost0), ("inspect", cost1))
                                  if value == best],
            "inspection_minus_skip_cost": str(cost1 - cost0),
            "scope": "Exact full-route expectation with optimal atomic retention and reliable recovery.",
        })
    return rows


def fixture_assignments():
    """Disjoint route indices in the existing lexicographic 30-route ordering.

Payload and renderer seeds are reserved, not used here to create yet-unwritten
natural-language fixtures. The committed manifest pins the sampled indices.
"""
    routes = list(range(30))
    development = random.Random(SEEDS["development_route"]).sample(routes, 1)
    remaining = [r for r in routes if r not in development]
    heldout = random.Random(SEEDS["heldout_route"]).sample(remaining, 4)
    return [
        {"split": split, "family": family, "route_index": route}
        for split, selected in (("development", development), ("heldout", heldout))
        for family, route in zip(FAMILIES[split], selected)
    ]


def sampled_reference(assignments):
    """Realized costs of fixed population-reference policies on reserved routes.

    Compile each policy without the sampled targets. Do not optimize retention
    for these few selected routes or call their average a population optimum.
    """
    rows = []
    configs = scenarios()
    for split in FAMILIES:
        routes = [a["route_index"] for a in assignments if a["split"] == split]
        for name in SCENARIOS:
            config = configs[name]
            fixtures = tuple(route_fixtures(config))
            row = {"split": split, "scenario": name, "route_indices": routes,
                   "fixture_count": len(routes)}
            for inspect, prefix in ((False, "skip"), (True, "inspect")):
                policy = executable_policy(config, inspect=inspect, recover=True)
                episodes = [run_episode(config, fixtures[r], policy) for r in routes]
                if not all(e.success for e in episodes):
                    raise AssertionError("Reference recovery did not complete the sampled workflow")
                row[prefix + "_mean_extra_cost"] = str(Fraction(
                    sum(e.cost_units - 7 - config.delay for e in episodes), len(episodes)))
                row[prefix + "_pre_recovery_hit_rate"] = str(Fraction(
                    sum(not e.recovery_attempted for e in episodes), len(episodes)))
            rows.append(row)
    return rows


def build_plan():
    cells = calibration()
    assignments = fixture_assignments()
    episodes = []
    for assignment in assignments:
        for cell in cells:
            for render_mode in RENDER_MODES:
                pair_id = f"{assignment['split']}/{assignment['family']}/{cell['scenario']}/{render_mode}"
                for arm in ARMS:
                    episodes.append({
                        **assignment, "scenario": cell["scenario"], "render_mode": render_mode,
                        "arm": arm, "pair_id": pair_id, "episode_id": f"{pair_id}/{arm}",
                        "maximum_model_requests": 2 + int(arm == "model_selective"),
                    })
    # Randomize inside a split, never interleave held-out calls into development.
    execution_order = []
    rng = random.Random(SEEDS["call_order"])
    for split in FAMILIES:
        group = [e["episode_id"] for e in episodes if e["split"] == split]
        rng.shuffle(group)
        execution_order.extend(group)
    stage_a = [{"scenario": name, "replicate": replicate,
                "decision_id": f"calibration/{name}/{replicate}", "maximum_model_requests": 1}
               for name in SCENARIOS for replicate in range(2)]
    return {
        "version": "inspection_pilot_design_v0.2", "date": "2026-09-19",
        "status": "offline design and calibration only; model launch not ready",
        "completed_model_requests": 0,
        "information_contract": "docs/LLM_PILOT_SPEC.md",
        "manifest_access": "Evaluator only; never include routes, seeds, answer labels, or this manifest in model messages.",
        "request_exclusions": ["scenario", "episode_id", "pair_id", "route_index", "seeds",
                               "reference_labels", "reference_costs", "verifier_truth", "previous_session_state"],
        "stage_b_interpretation": "With reliable recovery and scripted submission, valid completed episodes succeed even with empty memory. Pre-recovery availability and cost measure retention; terminal success checks execution/schema validity.",
        "sampling_limitation": "One route per family confounds family and route. Use mandatory same-fixture scripted comparisons; no family-effect or population-generalization claim.",
        "calibration_scope": "Stage A uses scripted optimal retention. Stage B uses learned retention; exact labels are references, not model-specific rationality labels.",
        "seeds": SEEDS,
        "model_launch_fields": {
            "provider": None, "model_revision": None, "api_version": None,
            "client_or_sdk_revision": None, "official_documentation_review": None,
            "cross_request_state_contract": None, "request_timeout": None,
            "reasoning_and_sampling_settings": None, "provider_sampling_seed_support": None,
            "usd_spending_cap": None, "price_snapshot": None, "per_request_token_caps": None,
            "prompt_artifact_hashes": None, "renderer_and_fixture_hashes": None,
            "adapter_and_isolation_audit": None, "approved_run_manifest_hash": None,
            "maximum_spend_and_reservation_audit": None,
            "full_memory_and_answer_visible_control_artifacts": None,
        },
        "launch_gates": [
            "Author and validate all five renderer families before test prompt freeze.",
            "Implement evaluator isolation and an allowlisted stateless request serializer.",
            "Verify no old response/session IDs, opaque state, archives, logs, seeds, or hidden routes enter requests.",
            "Pass offline full-memory, answer-visible, forget-all/recovery, and stale/wrong receipt controls.",
            "Freeze immutable fixtures, prompts, model settings, official documentation/prices, and dollar/token caps.",
            "Resolve all model_launch_fields in a reviewed run manifest before any model call.",
        ],
        "calibration": cells, "fixture_assignments": assignments,
        "sampled_scripted_reference": sampled_reference(assignments),
        "stage_a_decisions": stage_a, "stage_b_episodes": episodes,
        "stage_b_execution_order": execution_order,
        "counts": {
            "stage_a_decisions": len(stage_a),
            "stage_b_development_episodes": sum(e["split"] == "development" for e in episodes),
            "stage_b_heldout_episodes": sum(e["split"] == "heldout" for e in episodes),
            "stage_b_maximum_model_requests": sum(e["maximum_model_requests"] for e in episodes),
            "total_maximum_model_requests": len(stage_a) + sum(e["maximum_model_requests"] for e in episodes),
        },
        "accounting": {
            "automatic_retries": 0,
            "hard_api_dollar_budget": "Unspecified; request ceiling is not spending authorization.",
            "units": "Record slots, exact synthetic action costs, bytes, tokens, API dollars, and latency reported separately.",
            "failure_rule": "Count all attempts and failures; never discard or silently replace a failed run.",
            "diagnostic_calls": "Any additional paid diagnostic requires a versioned cap/manifest amendment.",
        },
        "source_sha256": {name: hashlib.sha256((Path(__file__).parent / name).read_bytes()).hexdigest()
                          for name in ("pilot_plan.py", "artifact_workflow.py", "recovery_frontier.py", "run_recovery_frontier.py")},
    }


def report(plan):
    lines = [
        "# Pilot calibration and reserved schedule", "", "September 19, 2026.", "",
        "This is an offline plan, not a model result or a launch-ready run manifest. No model requests have been made by this artifact. See the [pilot specification](../../../docs/LLM_PILOT_SPEC.md).", "",
        "The costs below are exact full-route expectations for optimal atomic-record retention, reliable recovery, and nonbinding episode limits. They exclude the common ten-unit workflow and all API costs.", "",
        "| Regime | Hit without / with inspection | Extra cost: skip / inspect | Cheaper decision | Cost of choosing the other decision |",
        "|---|---|---|---|---|",
    ]
    for c in plan["calibration"]:
        lines.append(f"| {c['scenario']} | {c['p0']} / {c['p1']} | {c['no_inspection_extra_cost']} / {c['inspection_extra_cost']} | {', '.join(c['optimal_decisions'])} | {abs(Fraction(c['inspection_minus_skip_cost']))} |")
    counts = plan["counts"]
    lines += [
        "", "## Prespecified stages", "",
        f"Stage A reserves {counts['stage_a_decisions']} inspection decisions across six regimes, with exact scripted retention and recovery. Each decision can be evaluated over all 30 routes; those route checks are not independent model decisions.", "",
        f"Stage B reserves {counts['stage_b_development_episodes']} development and {counts['stage_b_heldout_episodes']} held-out episodes across three inspection arms and two render modes. One development route and four distinct held-out routes are paired across regimes, render modes, and arms. Template families are reserved specifications; their natural-language fixtures have not been authored or validated.", "",
        f"The maximum planned total is {counts['total_maximum_model_requests']} requests, with no automatic retries. Exact model revision, settings, token caps, official price snapshot, dollar budget, renderer/prompt hashes, and isolation audit remain open. A request ceiling alone is not spending authorization.", "",
        "## Interpretation", "",
        "Under perfect scripted retention, costly recovery and costly recovery with the scheduled revision favor inspection. Cheap recovery, cheaper recovery with that revision, ample parent memory, and the small child capacity favor skipping it. In Stage B an imperfect model may face different effective hit rates; reference disagreement alone is not proof of an irrational inspection decision.", "",
        "## Same-fixture reference for the reserved held-out sample", "",
        "These are realized averages on four selected routes, using policies fixed from the full public distribution. They are not new optimality labels or estimates with useful sampling precision. One route per family also prevents separating family effects from route effects.", "",
        "| Regime | Sampled extra cost: skip / inspect |", "|---|---|",
    ]
    for row in plan["sampled_scripted_reference"]:
        if row["split"] == "heldout":
            lines.append(f"| {row['scenario']} | {row['skip_mean_extra_cost']} / {row['inspect_mean_extra_cost']} |")
    lines += [
        "", "In this small sample, costly_recovery and revision_cheap_recovery are ties (one unit either way), although their full-distribution expectations favor different decisions. Do not interpret disagreement with the population comparison as a measured model effect. The same-fixture scripted comparison is mandatory for Stage B.", "",
        "Reliable recovery and scripted submission let even a forget-all policy complete every valid episode. Pre-recovery availability and total cost are the retention signals; terminal success is mainly an interface/execution check in this design. The offline forget-all control is checked across all six regimes and all 30 routes. Scenario names and evaluator pair/episode identifiers must be excluded from model requests because they can suggest the intended decision.", "",
        "[Machine-readable plan](pilot_plan.json) includes evaluator-only route indices, reserved seeds, pair identifiers, execution order, unresolved launch fields, and source hashes. It must never be serialized wholesale into a model request. All counts are planned; the existing recovery report remains the completed scripted evidence.", "",
    ]
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=Path(__file__).parent / "results")
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    plan = build_plan()
    (args.output / "pilot_plan.json").write_text(json.dumps(plan, indent=2) + "\n", encoding="utf-8", newline="\n")
    (args.output / "pilot_calibration_report.md").write_text(report(plan), encoding="utf-8", newline="\n")
    print(json.dumps({"status": plan["status"], **plan["counts"]}, indent=2))


if __name__ == "__main__":
    main()
