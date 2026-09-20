"""Frozen factorial transfer study and exact scoring; no provider calls here."""
from __future__ import annotations

from collections import Counter
from fractions import Fraction
import hashlib
from itertools import combinations, product
import json
from pathlib import Path
import random

from transfer_interface import (JOB_COUNTS, FRAMINGS, GUARANTEES, GUIDANCE, RULES,
    build_request, job_keys, request_bytes, validate_response)

VERSION = "transfer_study_v1"
BLOCKS = 32
WORKERS = 4
MAX_REQUESTS = 1536
CREDIT_CAP = 200
SEED = 2026091913
BOOTSTRAP_SEED = 2026091914
FACTORS = ("jobs", "framing", "guarantee", "guidance", "refresh_rule")


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=False, allow_nan=False).encode("utf-8")


def digest(value):
    return hashlib.sha256(canonical(value)).hexdigest()


def block_material(block, jobs):
    if type(block) is not int or not 0 <= block < BLOCKS or jobs not in JOB_COUNTS:
        raise ValueError("Unknown block or size")
    keys = job_keys(jobs)
    ranks = list(range(jobs))
    random.Random(digest([VERSION, SEED, "priority", block, jobs])).shuffle(ranks)
    order = list(keys)
    random.Random(digest([VERSION, SEED, "display", block, jobs])).shuffle(order)
    records = [{"key": key, "revision": 1,
                "token": digest([VERSION, SEED, "payload", block, jobs, key])[:32]}
               for key in keys]
    return dict(zip(keys, ranks)), order, records


def make_plan():
    cases = []
    for block in range(BLOCKS):
        group = []
        for jobs in JOB_COUNTS:
            priorities, order, records = block_material(block, jobs)
            for framing, guarantee, guidance, rule in product(FRAMINGS, GUARANTEES, GUIDANCE, RULES):
                request = build_request(jobs=jobs, refresh_rule=rule, priorities=priorities,
                    record_order=order, records=records, framing=framing,
                    guarantee=guarantee, guidance=guidance)
                raw = request_bytes(request)
                group.append({"case_id": f"b{block:02d}-n{jobs}-{framing}-{guarantee}-{guidance}-{rule}",
                    "block": block, "worker": block % WORKERS, "jobs": jobs,
                    "framing": framing, "guarantee": guarantee, "guidance": guidance,
                    "refresh_rule": rule, "request": request,
                    "request_sha256": hashlib.sha256(raw).hexdigest(), "request_bytes": len(raw)})
        random.Random(digest([VERSION, SEED, "condition_order", block])).shuffle(group)
        cases.extend(group)
    here = Path(__file__).resolve().parent
    root = here.parents[1]
    ancillary = [root / "docs/TRANSFER_STUDY.md", here / "results/transfer_transport_audit.json"]
    files = sorted(here.glob("*.py")) + [p for p in ancillary if p.is_file()]
    return {"version": VERSION, "date": "2026-09-19", "maximum_model_requests": MAX_REQUESTS,
        "planned_cases": len(cases), "blocks": BLOCKS, "conditions_per_block": 48,
        "workers": WORKERS, "worker_request_cap": MAX_REQUESTS // WORKERS,
        "credit_equivalent_cap": CREDIT_CAP, "worker_credit_equivalent_cap": CREDIT_CAP // WORKERS,
        "allocation": "User authorized thousands of Luna requests; bounded here to 1536 new requests and 200 conservative credit equivalents",
        "model": "gpt-5.6-luna", "model_revision": "mutable alias", "reasoning_effort": "low",
        "additional_api_dollars": 0, "purchases": 0, "reset_redemptions": 0,
        "evaluator_seed": SEED, "bootstrap_seed": BOOTSTRAP_SEED,
        "model_sampling_seed": None, "model_requests_completed_by_plan": 0,
        "realized_routes_sampled": 0, "heldout_requests": 0,
        "protocol_and_wire_audit_present": all(p.is_file() for p in ancillary),
        "source_sha256": {p.relative_to(root).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
                          for p in files},
        "primary_comparison": "generic minus prospective normalized optimal-child-reference regret in workflow/unspecified/first-or-last cells; 128 matched pairs in 32 blocks",
        "analysis": "Raw regret by size; normalized paired block means with a fixed 5000-resample cluster bootstrap; no-refresh excluded from primary comparison; validity and all missing outcomes retained",
        "scope": "Isolated parent-retention transfer/context-load study; child capacity equals candidate count and is nonbinding; not a native-compaction experiment",
        "stopping": "Fixed sample, no answer-dependent tuning or extensions. Any transport/accounting stop propagates before new dispatch; in-flight requests may finish. No retries or resume.",
        "cases": cases}


def grade(selected, case):
    request = case["request"]
    keys = validate_response({"keys": list(selected)}, request)
    priorities = {r["key"]: r["refresh_priority"] for r in request["public_metadata"]["jobs"]}
    n = case["jobs"]
    ranks = [priorities[k] for k in keys]
    rule = case["refresh_rule"]
    if rule == "none":
        score, best = Fraction(len(keys), n), Fraction(2, n)
        normalizer = None
    else:
        weight = sum(ranks) if rule == "first" else sum(n - 1 - rank for rank in ranks)
        score = Fraction(1, 2) + Fraction(weight, n * (n - 1))
        best = Fraction(1, 2) + Fraction(2 * n - 3, n * (n - 1))
        normalizer = Fraction(2 * n - 4, n * (n - 1))
    regret = best - score
    return {"keys": list(keys), "selected_priorities": ranks, "selected_count": len(keys),
        "availability": str(score), "reference_availability": str(best),
        "exact_parent_regret": str(regret), "optimal_parent": regret == 0,
        "normalized_regret": str(regret / normalizer) if normalizer else None,
        "full_pair_regret_span": str(normalizer) if normalizer else None,
        "route_count": n * (n - 1), "downstream_reference": "optimal_child"}


def enumerate_availability(selected, priorities, rule):
    """Independent outcome formulation, without the rank-sum shortcut."""
    hits = 0
    keys = tuple(priorities)
    for pair in combinations(keys, 2):
        available = set(selected).intersection(pair)
        if rule != "none":
            available.add((min if rule == "first" else max)(pair, key=priorities.__getitem__))
        hits += sum(target in available for target in pair)
    return Fraction(hits, len(keys) * (len(keys) - 1))


class FakeClient:
    def __init__(self, mode="optimal"):
        if mode not in ("optimal", "static_low", "first_visible", "invalid"):
            raise ValueError("Unknown fake control")
        self.mode = mode
        self.last_metadata = {}

    def complete(self, request):
        request_bytes(request)
        if self.mode == "invalid":
            return {"keys": ["invented-key"]}
        if self.mode == "first_visible":
            return {"keys": [r["key"] for r in request["visible_records"][:2]]}
        jobs = request["public_metadata"]["jobs"]
        if self.mode == "static_low" or request["refresh_rule"] == "none":
            selected = sorted(r["key"] for r in jobs)[:2]
        else:
            selected = [r["key"] for r in sorted(jobs, key=lambda r: r["refresh_priority"],
                         reverse=request["refresh_rule"] == "first")[:2]]
        return {"keys": selected}


def mean_fraction(values):
    return str(sum(values, Fraction()) / len(values)) if values else None


def bootstrap_interval(values):
    """Descriptive cluster-bootstrap percentile interval; blocks are the unit."""
    if len(values) < 2:
        return None
    rng = random.Random(BOOTSTRAP_SEED)
    estimates = sorted(sum(rng.choice(values) for _ in values) / len(values) for _ in range(5000))
    return [estimates[124], estimates[4874]]


def aggregate(rows):
    conditions = []
    for factors in product(JOB_COUNTS, FRAMINGS, GUARANTEES, GUIDANCE, RULES):
        selected = [row for row in rows if tuple(row[k] for k in FACTORS) == factors]
        valid = [row for row in selected if row["status"] == "completed"]
        metered = [row for row in selected if row["status"] in ("completed", "policy_failure")]
        conditions.append({**dict(zip(FACTORS, factors)), "scheduled": len(selected),
            "completed": len(valid), "policy_failures": sum(r["status"] == "policy_failure" for r in selected),
            "transport_failures": sum(r["status"] == "transport_failure" for r in selected),
            "incomplete": sum(r["status"] == "incomplete" for r in selected),
            "optimal_count": sum(r["grade"]["optimal_parent"] for r in valid),
            "valid_and_optimal_denominator": len(metered),
            "underfilled": sum(r["grade"]["selected_count"] < 2 for r in valid),
            "mean_exact_regret": mean_fraction([Fraction(r["grade"]["exact_parent_regret"]) for r in valid])})
    by_key = {(r["block"], *(r[k] for k in FACTORS)): r for r in rows}
    pairs = []
    for block, n, rule in product(range(BLOCKS), JOB_COUNTS, ("first", "last")):
        a = by_key.get((block, n, "workflow", "unspecified", "generic", rule))
        b = by_key.get((block, n, "workflow", "unspecified", "prospective", rule))
        valid = bool(a and b and a["status"] == b["status"] == "completed")
        metered = bool(a and b and all(r["status"] in ("completed", "policy_failure") for r in (a, b)))
        row = {"block": block, "jobs": n, "refresh_rule": rule,
               "both_valid": valid, "both_transport_complete": metered,
               "regret_benefit": None, "normalized_regret_benefit": None,
               "valid_and_optimal_benefit": None}
        if valid:
            row["regret_benefit"] = str(Fraction(a["grade"]["exact_parent_regret"]) - Fraction(b["grade"]["exact_parent_regret"]))
            row["normalized_regret_benefit"] = str(Fraction(a["grade"]["normalized_regret"]) - Fraction(b["grade"]["normalized_regret"]))
        if metered:
            row["valid_and_optimal_benefit"] = int(b["status"] == "completed" and b["grade"]["optimal_parent"]) - int(a["status"] == "completed" and a["grade"]["optimal_parent"])
        pairs.append(row)
    block_effects = []
    for block in range(BLOCKS):
        group = [p for p in pairs if p["block"] == block]
        complete = all(p["both_valid"] for p in group)
        block_effects.append({"block": block, "complete": complete,
            "normalized_regret_benefit": mean_fraction([Fraction(p["normalized_regret_benefit"]) for p in group]) if complete else None})
    values = [float(Fraction(r["normalized_regret_benefit"])) for r in block_effects if r["complete"]]
    valid_pairs = [p for p in pairs if p["both_valid"]]
    return {"status_counts": dict(Counter(r["status"] for r in rows)), "by_condition": conditions,
        "primary": {"scheduled_pairs": len(pairs), "valid_pairs": len(valid_pairs),
            "transport_complete_pairs": sum(p["both_transport_complete"] for p in pairs),
            "complete_blocks": len(values), "planned_blocks": BLOCKS,
            "mean_normalized_regret_benefit": mean_fraction([Fraction(p["normalized_regret_benefit"]) for p in valid_pairs]),
            "complete_block_mean_normalized_regret_benefit": mean_fraction([Fraction(r["normalized_regret_benefit"]) for r in block_effects if r["complete"]]),
            "block_bootstrap_95_percent_interval": bootstrap_interval(values),
            "bootstrap_resamples": 5000,
            "mean_valid_and_optimal_benefit": mean_fraction([Fraction(p["valid_and_optimal_benefit"]) for p in pairs if p["both_transport_complete"]]),
            "raw_regret_benefit_by_size": {str(n): mean_fraction([Fraction(p["regret_benefit"]) for p in valid_pairs if p["jobs"] == n]) for n in JOB_COUNTS},
            "pairs": pairs, "block_effects": block_effects,
            "coverage_warning": "Regret uses valid pairs only; bootstrap uses fully valid blocks. Do not infer a clean treatment benefit when missingness differs."}}


def report(summary):
    primary = summary["primary"]
    lines = ["# Parent-retention transfer study", "",
        "Controlled synthetic development study; no native-compaction or full-agent comparison.", "",
        f"Fake: **{summary.get('fake')}**. Model requests: **{summary.get('model_requests')}**. "
        f"Scheduled: **{MAX_REQUESTS}**. Status counts: `{json.dumps(summary['status_counts'], sort_keys=True)}`.", "",
        "## Prespecified primary comparison", "",
        "Generic minus prospective guidance regret in fuller-workflow, unspecified-child, refresh-present cells. "
        "Positive values favor prospective guidance. The child reference is optimal for grading; its skill is not promised in these prompts.", "",
        f"Valid paired selections: {primary['valid_pairs']}/{primary['scheduled_pairs']}. "
        f"Complete blocks: {primary['complete_blocks']}/{BLOCKS}.", "",
        f"Mean normalized regret benefit across valid pairs: **{primary['mean_normalized_regret_benefit']}**. "
        f"Complete-block mean: **{primary['complete_block_mean_normalized_regret_benefit']}**; "
        f"its descriptive 95% block-bootstrap interval: **{primary['block_bootstrap_95_percent_interval']}**.", "",
        f"Raw availability-regret benefit by size: `{json.dumps(primary['raw_regret_benefit_by_size'], sort_keys=True)}`. "
        f"Mean valid-and-optimal benefit: `{primary['mean_valid_and_optimal_benefit']}`.", "",
        primary["coverage_warning"], "", "## Complete factorial display", "",
        "| Jobs | Framing/context | Later guarantee | Guidance | Refresh | Valid / planned | Optimal | Mean raw regret |",
        "|---|---|---|---|---|---|---|---|"]
    for r in summary["by_condition"]:
        lines.append(f"| {r['jobs']} | {r['framing']} | {r['guarantee']} | {r['guidance']} | {r['refresh_rule']} | {r['completed']}/{r['scheduled']} | {r['optimal_count']} | {r['mean_exact_regret']} |")
    lines += ["", "## Accounting", "",
        f"Reported usage totals: `{json.dumps(summary.get('usage_totals', {}), sort_keys=True)}`. "
        f"Conservative credit-equivalent accounting: `{json.dumps(summary.get('credit_budget', {}), sort_keys=True)}`. "
        "These token-derived equivalents are not an observed subscription debit.", "",
        "No-refresh full pairs all tie. Larger n adds ranking/context load but reduces the maximum raw regret. "
        "Normalized regret divides by the full-pair range (4/15 at six jobs, 5/33 at twelve); underfilled answers can exceed one. "
        "The second boundary is nonbinding because child slots equal the candidate count. Intervals describe sampled-block variation, "
        "not natural-task generalization or an immutable model revision. All failures and incomplete cases remain recorded.", "",
        "[Protocol](../../../../docs/TRANSFER_STUDY.md)", ""]
    return "\n".join(lines)
