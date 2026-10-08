"""Task-level E2 descriptive analysis, fixed-denominator bounds and cost views."""
from collections import Counter
from decimal import Decimal
from fractions import Fraction
import random

from .contexts import ARMS


def validate_rows(rows):
    if len({row["task_id"] for row in rows}) != len(rows):
        raise ValueError("duplicate analysis task")
    for row in rows:
        if row["domain"] not in {"math", "coding"} or set(row["grades"]) != set(ARMS):
            raise ValueError("analysis domain/arms")
        for scores in row["grades"].values():
            if len(scores) != 2 or any(x is not None and (type(x) is not int or x not in (0, 1)) for x in scores):
                raise ValueError("two binary-or-unknown task draws required")
        if row["primary_scheduled"] and not {"K", "R"}.issubset(row["scheduled_arms"]):
            raise ValueError("primary task lacks scheduled K/R slots")


def number(value):
    return None if value is None else {"fraction": str(value), "percentage_points": float(value * 100)}


def paired(rows, treatment, control, bootstrap_seed=20261009, resamples=10000):
    pairs, complete, lowers, uppers = [], [], [], []
    for row in rows:
        a, b = row["grades"][treatment], row["grades"][control]
        known = all(x is not None for x in a + b)
        difference = (Fraction(sum(a) - sum(b), 2) if known else None)
        low = Fraction(sum(0 if x is None else x for x in a) - sum(1 if x is None else x for x in b), 2)
        high = Fraction(sum(1 if x is None else x for x in a) - sum(0 if x is None else x for x in b), 2)
        lowers.append(low)
        uppers.append(high)
        if difference is not None:
            complete.append(difference)
        pairs.append({"task_id": row["task_id"], treatment: a, control: b, "difference": number(difference),
                      "missingness_lower": number(low), "missingness_upper": number(high)})
    n = len(rows)
    interval = None
    if len(complete) >= 6:
        rng = random.Random(bootstrap_seed)
        distribution = sorted(sum(rng.choices(complete, k=len(complete)), Fraction(0)) / len(complete) for _ in range(resamples))
        interval = {"kind": "descriptive_task_bootstrap_95_percent",
                    "lower": number(distribution[int(resamples * 0.025)]),
                    "upper": number(distribution[min(resamples - 1, int(resamples * 0.975))]),
                    "seed": bootstrap_seed, "resamples": resamples,
                    "quantile_rule": "sorted resamples at zero-based floor(p*n)"}
    return {"scheduled_tasks": n, "complete_tasks": len(complete), "pairs": pairs,
            "complete_pair_mean": number(sum(complete, Fraction(0)) / len(complete)) if complete else None,
            "complete_pair_range": [number(min(complete)), number(max(complete))] if complete else None,
            "all_scheduled_missingness_bounds": [number(sum(lowers, Fraction(0)) / n), number(sum(uppers, Fraction(0)) / n)] if n else None,
            "bootstrap": interval, "confirmatory_p_value": None}


def resources(events, rows):
    latest = {}
    for event in events:
        latest.setdefault(event["call_id"], {}).update(event)
    completed = [event for event in latest.values() if event["state"] == "completed"]
    unresolved = [event for event in latest.values() if event["state"] in {"reserved", "dispatched", "unknown"}]
    actual = sum((Decimal(event["cost_usd"]) for event in completed), Decimal(0))
    usage = {key: sum(event["usage"][key] for event in completed) for key in
             ("input_tokens", "uncached_input", "cached_input", "cache_write", "output", "reasoning")}
    projections = {}
    for arm in ARMS:
        stages = {"checkpoint", "branch"} | ({"lesson"} if arm in {"K", "R"} else {"summary"} if arm == "G" else set())
        includes = lambda event: event["identity"]["stage"] in stages or (event["identity"]["stage"] == "terminal" and event["identity"]["arm"] == arm)
        selected = [event for event in completed if includes(event)]
        locked = [event for event in unresolved if includes(event)]
        projections[arm] = {"known_projected_usd": str(sum((Decimal(event["cost_usd"]) for event in selected), Decimal(0))),
                            "locked_projected_reserve_usd": str(sum((Decimal(event["reserve_usd"]) for event in locked), Decimal(0))),
                            "incomplete": bool(locked) or any(arm in row["scheduled_arms"] and None in row["grades"][arm] for row in rows),
                            "scope": "observed episode standalone projection; not measured independent-policy spend"}
    return {"unit": "synthetic_API_USD_not_actual_provider_spend", "shared_experiment_cost_usd": str(actual),
            "usage": usage, "known_completed_calls": len(completed), "unknown_or_pending_calls": len(unresolved),
            "locked_reserve_usd": str(sum((Decimal(e["reserve_usd"]) for e in unresolved), Decimal(0))),
            "standalone_policy_projections": projections, "sum_projections_is_actual_spend": False}


def analyze(rows, events=()):
    validate_rows(rows)
    domains = {}
    for domain in ("math", "coding"):
        selected = [row for row in rows if row["domain"] == domain]
        primary = [row for row in selected if row["primary_scheduled"]]
        stages = Counter(item.split(":", 1)[0] for row in selected for item in row["flow"])
        conditions = {}
        for arm in ARMS:
            scheduled = [row for row in selected if arm in row["scheduled_arms"]]
            scores = [x for row in scheduled for x in row["grades"][arm]]
            conditions[arm] = {"scheduled_tasks": len(scheduled), "scheduled_draws": len(scores),
                               "correct_known_draws": sum(x == 1 for x in scores), "failed_known_draws": sum(x == 0 for x in scores),
                               "unknown_draws": sum(x is None for x in scores), "draws_are_independent_tasks": False}
        example_classes = {}
        for row in selected:
            if not row["primary_scheduled"]:
                outcome = "not_primary_scheduled"
            elif any(x is None for x in row["grades"]["K"] + row["grades"]["R"]):
                outcome = "missing_primary"
            else:
                difference = sum(row["grades"]["R"]) - sum(row["grades"]["K"])
                outcome = "R_better" if difference > 0 else "K_better" if difference < 0 else "tie"
            example_classes.setdefault(outcome, row["task_id"])
        domains[domain] = {"selected_tasks": len(selected), "flow_event_counts": dict(sorted(stages.items())),
                           "all_task_flow": [{"task_id": r["task_id"], "flow": r["flow"], "primary_scheduled": r["primary_scheduled"],
                                              "lesson_usable": r["lesson_usable"], "summary_usable": r["summary_usable"],
                                              "capacity_infeasible": r["capacity_infeasible"]} for r in selected],
                           "public_failure_tasks": sum(r["public_failure"] for r in selected),
                           "capacity_infeasible_tasks": sum(r["capacity_infeasible"] for r in selected),
                           "primary_R_minus_K": paired(primary, "R", "K"), "conditions": conditions,
                           "secondary_R_minus_Z": paired([r for r in selected if {"R", "Z"}.issubset(r["scheduled_arms"])], "R", "Z"),
                           "secondary_R_minus_G": paired([r for r in selected if {"R", "G"}.issubset(r["scheduled_arms"])], "R", "G"),
                           "example_selection": example_classes, "example_rule": "first task in frozen order per outcome class",
                           "feasibility_screen_at_least_six_primary_tasks": len(primary) >= 6}
    return {"evidence_kind": "offline_scripted_fixture_analysis_not_model_observations", "domains": domains,
            "resources": resources(events, rows), "human_measures": {"refuted_assumption_repetition": "unreviewed",
              "retained_fact_loss": "unreviewed", "lesson_solution_sufficiency": "unreviewed"}}


def report_markdown(result):
    lines = ["# Offline rollback controller report", "", "Scripted engineering fixtures only; zero model calls or measured API spend.", "",
             "| Domain | Selected tasks | Public failures | Scheduled K/R tasks | Complete K/R tasks | R minus K (pp) |", "|---|---:|---:|---:|---:|---:|"]
    for domain, data in result["domains"].items():
        primary = data["primary_R_minus_K"]
        mean = primary["complete_pair_mean"]
        lines.append(f"| {domain} | {data['selected_tasks']} | {data['public_failure_tasks']} | {primary['scheduled_tasks']} | {primary['complete_tasks']} | {mean['percentage_points'] if mean else 'unknown'} |")
    lines += ["", "The differences above are authored outcomes used to check analysis, not evidence of a rollback effect.", "",
              "Full flow, all four conditions, secondary intersections, missingness bounds, task outcomes and",
              "synthetic resource projections are saved in `analysis.json`. Two draws remain repeated measurements on one task.", "",
              "Shared preparation is charged once in the synthetic experiment ledger. Standalone projections are separate",
              "and cannot be added to obtain experimental spend. Actual provider spend is USD 0.", ""]
    return "\n".join(lines)
