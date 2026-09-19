"""Offline plan, exact grading, and fake controls for revision-aware retention.

This diagnostic grades one cold parent choice over the entire routing population.
It never samples a realized candidate/target and never models counterfactual Luna
child choices. Optimal downstream selection is a declared experimental control.
"""
from __future__ import annotations

import hashlib
from itertools import combinations
import json
from fractions import Fraction
from pathlib import Path
import random

from revision_interface import KEYS, RULES, build_request, request_bytes, validate_response

VERSION = "revision_parent_diagnostic_v1"
MAX_REQUESTS = 24
SCHEDULE_SEED = 2026091907
PAYLOAD_SEED = 2026091908
ORDERS = (
    KEYS, tuple(reversed(KEYS)),
    tuple(KEYS[i] for i in (2, 5, 1, 4, 0, 3)),
    tuple(KEYS[i] for i in (3, 0, 4, 1, 5, 2)),
)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=False, allow_nan=False).encode("utf-8")


def digest(value):
    return hashlib.sha256(canonical(value)).hexdigest()


def _selection(keys, rule):
    if type(rule) is not str or rule not in RULES:
        raise ValueError("Unknown refresh rule")
    if (type(keys) not in (tuple, list) or len(keys) > 2
            or any(type(key) is not str for key in keys)
            or len(set(keys)) != len(keys) or not set(keys) <= set(KEYS)):
        raise ValueError("Invalid parent selection")
    return tuple(sorted(keys))


def availability(keys, rule):
    """Independent 15-pair/30-target enumeration with an optimal two-slot child."""
    keys = _selection(keys, rule)
    successes = 0
    for pair in combinations(KEYS, 2):
        available = set(keys).intersection(pair)
        if rule == "lexicographic_first":
            available.add(pair[0])
        elif rule == "lexicographic_last":
            available.add(pair[-1])
        # At most two candidates exist; an optimal two-slot child keeps all
        # available candidates. Each has one equiprobable target continuation.
        for target in pair:
            successes += target in available
    return Fraction(successes, 30)


def availability_formula(keys, rule):
    keys = _selection(keys, rule)
    ranks = [KEYS.index(key) for key in keys]
    if rule == "none":
        return Fraction(len(keys), 6)
    weight = sum(ranks) if rule == "lexicographic_first" else sum(5 - rank for rank in ranks)
    return Fraction(1, 2) + Fraction(weight, 30)


def grade(keys, rule):
    keys = _selection(keys, rule)
    score = availability(keys, rule)
    choices = [pair for size in range(3) for pair in combinations(KEYS, size)]
    best = max(availability(pair, rule) for pair in choices)
    return {"keys": list(keys), "selected_rank_sum": sum(KEYS.index(key) for key in keys),
            "availability": str(score), "best_availability": str(best),
            "exact_parent_regret": str(best - score), "optimal_parent": score == best,
            "route_count": 30, "downstream_selector": "guaranteed_optimal"}


def make_plan():
    cases = []
    for fixture in range(2):
        records = [{"key": key, "revision": 1,
                    "token": digest([VERSION, PAYLOAD_SEED, fixture, key])[:32]} for key in KEYS]
        for order, record_order in enumerate(ORDERS):
            for rule in RULES:
                request = build_request(rule, record_order, records)
                cases.append({"case_id": f"f{fixture}-o{order}-r{RULES.index(rule)}",
                    "fixture": fixture, "order": order, "refresh_rule": rule,
                    "request": request, "request_sha256": hashlib.sha256(request_bytes(request)).hexdigest()})
    random.Random(SCHEDULE_SEED).shuffle(cases)
    here = Path(__file__).resolve().parent
    root = here.parents[1]
    sources = sorted(here.glob("*.py")) + [
        here / "results/revision_transport_audit.json", root / "docs/REVISION_DIAGNOSTIC.md"]
    return {"version": VERSION, "split": "development", "maximum_model_requests": MAX_REQUESTS,
            "planned_cases": len(cases), "model_requests_completed_by_plan": 0,
            "realized_routes_sampled": 0, "heldout_requests": 0,
            "schedule_seed": SCHEDULE_SEED, "payload_seed": PAYLOAD_SEED,
            "source_sha256": {path.relative_to(root).as_posix(): hashlib.sha256(path.read_bytes()).hexdigest()
                              for path in sources},
            "proposed_transport": {"model": "gpt-5.6-luna", "model_revision": "mutable alias",
                "reasoning_effort": "low", "service_tier": "default", "new_credit_equivalent_cap": 12,
                "additional_api_dollars": 0, "authorization": "pending new allocation beyond completed 96-request tranche"},
            "scope": "Post-pilot targeted development diagnostic; 30 counterfactual routes per choice are not model trials",
            "fixed_canonical_order_channels": ["public_metadata.job_keys", "response_schema.properties.keys.items.enum"],
            "cases": cases}


class FakeClient:
    def __init__(self, mode="optimal"):
        if mode not in ("optimal", "always_low", "always_high", "first_visible", "invalid"):
            raise ValueError("Unknown fake control")
        self.mode = mode

    def complete(self, request):
        request_bytes(request)
        if self.mode == "invalid":
            return {"keys": ["invented-key"]}
        if self.mode == "first_visible":
            return {"keys": [row["key"] for row in request["visible_records"][:2]]}
        if self.mode == "always_high" or (self.mode == "optimal" and request["refresh_rule"] == "lexicographic_first"):
            return {"keys": list(KEYS[-2:])}
        return {"keys": list(KEYS[:2])}


def aggregate(rows):
    result = []
    for rule in RULES:
        selected = [row for row in rows if row["refresh_rule"] == rule]
        completed = [row for row in selected if row["status"] == "completed"]
        result.append({"refresh_rule": rule, "scheduled": len(selected), "completed": len(completed),
            "policy_failures": sum(row["status"] == "policy_failure" for row in selected),
            "transport_failures": sum(row["status"] == "transport_failure" for row in selected),
            "incomplete": sum(row["status"] == "incomplete" for row in selected),
            "optimal_parent_count": sum(row["grade"]["optimal_parent"] for row in completed),
            "mean_availability": str(sum((Fraction(row["grade"]["availability"]) for row in completed), Fraction()) / len(completed)) if completed else None,
            "mean_exact_parent_regret": str(sum((Fraction(row["grade"]["exact_parent_regret"]) for row in completed), Fraction()) / len(completed)) if completed else None})
    shifts = []
    for fixture in range(2):
        for order in range(4):
            pair = {row["refresh_rule"]: row for row in rows if row["fixture"] == fixture and row["order"] == order}
            lo, hi = (pair[rule] for rule in RULES[:2])
            complete = lo["status"] == hi["status"] == "completed"
            shifts.append({"fixture": fixture, "order": order, "complete": complete,
                "first_minus_last_rank_sum": lo["grade"]["selected_rank_sum"] - hi["grade"]["selected_rank_sum"] if complete else None})
    return {"by_rule": result, "paired_direction_shifts": shifts}


def fake_audit():
    plan = make_plan()
    controls = []
    for mode in ("optimal", "always_low", "always_high", "first_visible", "invalid"):
        client = FakeClient(mode)
        rows = []
        for case in plan["cases"]:
            row = {k: case[k] for k in ("case_id", "fixture", "order", "refresh_rule")}
            response = client.complete(case["request"])
            try:
                keys = validate_response(response, case["request"])
                row.update(status="completed", grade=grade(keys, case["refresh_rule"]))
            except ValueError:
                row.update(status="policy_failure", grade=None)
            rows.append(row)
        controls.append({"mode": mode, **aggregate(rows)})
    return {"version": VERSION, "plan_sha256": digest(plan), "fake_requests": 120,
            "model_requests": 0, "controls": controls,
            "interpretation": "Offline controls only; no follow-up model outcome"}


def report(summary):
    lines = ["# Revision-aware parent diagnostic", "",
             "Development only. Each selection is evaluated over 30 routes with an optimal later selector; "
             "those routes are not additional model trials.", "",
             f"Fake client: **{summary['fake']}**. Model requests: **{summary['model_requests']}**. "
             f"Request cap: **{summary['request_cap']}**. Held-out requests: **0**.", "",
             "| Refresh rule | Complete / planned | Optimal parent | Mean availability | Mean exact parent regret |",
             "|---|---|---|---|---|"]
    for row in summary["by_rule"]:
        lines.append(f"| {row['refresh_rule']} | {row['completed']}/{row['scheduled']} | {row['optimal_parent_count']}/{row['completed']} | {row['mean_availability']} | {row['mean_exact_parent_regret']} |")
    lines += ["", "Failures and incomplete decisions remain in the scheduled denominators. Means use only valid completed responses; no failure is imputed as an empty selection.", "",
        "| Case | Rule | Status | Keys | Displayed positions (1-based) | Availability | Exact parent regret |",
        "|---|---|---|---|---|---|---|"]
    for row in summary["rows"]:
        g = row.get("grade") or {}
        lines.append(f"| {row['case_id']} | {row['refresh_rule']} | {row['status']} | {g.get('keys')} | {row.get('displayed_positions')} | {g.get('availability')} | {g.get('exact_parent_regret')} |")
    lines += ["", "Refresh provides a free information channel; raw availability across refresh/no-refresh rules is not an understanding effect. "
        "Rule-specific exact regret and matched direction shifts are the diagnostic outcomes. The response enum and job metadata retain canonical order. "
        "Two receipt fixtures and four record orders do not establish population generalization or internal reasoning mechanisms.", ""]
    lines += ["| Fixture | Record order | Pair complete | First-minus-last selected-rank sum |",
              "|---|---|---|---|"]
    for pair in summary["paired_direction_shifts"]:
        lines.append(f"| {pair['fixture']} | {pair['order']} | {pair['complete']} | {pair['first_minus_last_rank_sum']} |")
    if not summary["fake"]:
        budget = summary["credit_budget"]
        lines += ["", f"Conservative credit-equivalent budget: {budget['cap_credit_equivalent']}; "
                  f"committed: {budget['committed_credit_equivalent']}; "
                  f"uncertain reservations: {budget['uncertain_credit_reservations']}.", "",
                  "Actual subscription debit attributable to this diagnostic is unknown. API billing, purchases, and resets are excluded. "
                  "Input includes cached input; output includes reasoning, so these buckets must not be added again.", "",
                  "| Reported token bucket | Subtotal | Attempts measured |", "|---|---|---|"]
        for name, value in summary.get("usage_totals", {}).items():
            lines.append(f"| {name} | {value['reported']} | {value['measured_attempts']}/{summary['request_attempts']} |")
    lines.append("")
    return "\n".join(lines)
