"""Task-level live analysis with subscription resource units, not API dollars."""
from decimal import Decimal

from ..analysis import analyze as e0_analyze
from ..contexts import ARMS


def resources(events, rows):
    latest = {}
    for event in events:
        latest.setdefault(event["call_id"], {}).update(event)
    complete = [r for r in latest.values() if r["state"] == "completed"]
    pending = [r for r in latest.values() if r["state"] in {"reserved", "dispatched", "unknown"}]
    total = lambda rs,key: str(sum((Decimal(r[key]) for r in rs), Decimal(0)))
    projections = {}
    for arm in ARMS:
        stages = {"checkpoint", "branch"} | ({"lesson"} if arm in {"K","R"} else {"summary"} if arm=="G" else set())
        include = lambda r: r["identity"]["stage"] in stages or (r["identity"]["stage"]=="terminal" and r["identity"]["arm"]==arm)
        done, unknown = [r for r in complete if include(r)], [r for r in pending if include(r)]
        projections[arm] = {"known_projected_planning_credits": total(done,"planning_credits"),
                            "locked_reserve_credits": total(unknown,"reserve_credits"),
                            "incomplete": bool(unknown) or any(arm in r["scheduled_arms"] and None in r["grades"][arm] for r in rows),
                            "scope": "observed episode standalone projection; not independently run policies"}
    return {"unit": "subscription_planning_credits_not_actual_account_charge",
            "shared_experiment_planning_credits": total(complete,"planning_credits"),
            "known_completed_calls": len(complete), "unknown_or_pending_calls": len(pending),
            "locked_reserve_credits": total(pending,"reserve_credits"),
            "usage": {key:sum(r["usage"][key] for r in complete) for key in ("input_tokens","cached_input","output","reasoning")},
            "API_model_calls": 0, "API_spend_USD": "0", "actual_account_charge": None,
            "standalone_policy_projections": projections, "sum_projections_is_actual_spend": False}


def analyze(rows, events):
    result = e0_analyze(rows)
    result["evidence_kind"] = "live_subscription_authored_engineering_pilot_not_LiveCodeBench_v02"
    result["resources"] = resources(events, rows)
    for domain, data in result["domains"].items():
        selected = [r for r in rows if r["domain"] == domain]
        initial = [r["initial_grade"] for r in selected if "initial_grade" in r]
        data["initial_candidates_graded"] = len(initial)
        data["initial_candidates_correct"] = sum(x["score"]==1 for x in initial)
        data["initial_candidates_failed_reserved_grading"] = sum(x["score"]==0 for x in initial)
        data["repeated_rejected_candidates"] = {arm:sum(x is True for r in selected for x in r["repeated_candidates"][arm]) for arm in ARMS}
    return result


def markdown(result):
    lines = ["# Authored subscription engineering pilot", "",
             "GPT-6 Luna medium through the user's Codex subscription. Coding tasks are original",
             "repository-authored tasks; this is a source amendment, not the planned LiveCodeBench cohort.", "",
             "| Domain | Selected | Initial correct | Public failures | Paired K/R tasks | Complete K/R | R minus K (pp) |",
             "|---|---:|---:|---:|---:|---:|---:|"]
    for domain,data in result["domains"].items():
        p = data["primary_R_minus_K"]
        mean = p["complete_pair_mean"]
        lines.append(f"| {domain} | {data['selected_tasks']} | {data['initial_candidates_correct']} | {data['public_failure_tasks']} | {p['scheduled_tasks']} | {p['complete_tasks']} | {mean['percentage_points'] if mean else 'unidentified'} |")
    r = result["resources"]
    lines += ["", f"Completed generations: {r['known_completed_calls']}; unknown/pending: {r['unknown_or_pending_calls']}.",
              f"Calculated planning credits: {r['shared_experiment_planning_credits']}. Actual account charge is unavailable.",
              "No API-key calls or API dollar spend. Reasoning tokens are included in output, not added again.", "",
              "All 24 selected tasks, every condition, skipped slots, missingness and resource projections are",
              "retained in analysis.json and slot_dispositions.jsonl. Two draws remain repeated measurements",
              "on one task. Small eligible denominators limit interpretation; a missing recovery opportunity",
              "does not establish equivalence. No general rollback benefit or manuscript claim is established.", ""]
    return "\n".join(lines)
