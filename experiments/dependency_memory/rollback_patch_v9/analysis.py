"""Prespecified factorial summaries for visible failed-patch retention.

The unit is a shared naturally failed task prefix, never a model call or an
individual test assertion. Missing scores remain missing. Finite-cohort bounds
and descriptive task-bootstrap intervals answer different questions.
"""
from collections import Counter, defaultdict
from decimal import Decimal
import hashlib
import json
import math
import random


ARMS = ("K0", "R0", "KL", "RL")
CONTRASTS = {
    "deletion_main": {"K0": -0.5, "R0": 0.5, "KL": -0.5, "RL": 0.5},
    "lesson_main": {"K0": -0.5, "R0": -0.5, "KL": 0.5, "RL": 0.5},
    "interaction": {"K0": 1, "R0": -1, "KL": -1, "RL": 1},
    "deletion_without_lesson": {"K0": -1, "R0": 1},
    "deletion_with_lesson": {"KL": -1, "RL": 1},
    "lesson_when_keeping": {"K0": -1, "KL": 1},
    "lesson_when_removing": {"R0": -1, "RL": 1},
}


def _hash(value):
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True,
                                     separators=(",", ":")).encode("utf-8")).hexdigest()


def _score(value):
    if value is not None and (type(value) is not int or value not in (0, 1)):
        raise ValueError("outcome must be integer zero/one or missing")
    return value


def _public_pass(attempt):
    receipt = attempt["public"]
    return receipt.get("status") == "public_pass" or receipt.get("passed") is True


def _outcome_endpoints(result, allowance):
    """Retain observed early endpoints even when a later generation is unknown."""
    score = _score(result.get("score"))
    attempts = result.get("attempts", [])
    if len(attempts) > allowance:
        raise ValueError("continuation exceeded its frozen attempt allowance")
    passes = [index for index, attempt in enumerate(attempts, 1) if _public_pass(attempt)]
    first = passes[0] if passes else None
    if "first_pass" in result and result["first_pass"] != first:
        raise ValueError("first public pass disagrees with saved attempts")
    if first is not None and first != len(attempts):
        raise ValueError("arm continued after public acceptance")
    if score == 1 and (first is None or attempts[first - 1]["terminal"].get("score") != 1):
        raise ValueError("terminal success lacks public acceptance and held-out pass")
    if first is not None and score is not None:
        if score != _score(attempts[first - 1]["terminal"].get("score")):
            raise ValueError("terminal score differs from publicly accepted candidate")
    public_curve, hidden_curve = {}, {}
    for limit in range(1, allowance + 1):
        public_curve[str(limit)] = (1 if first is not None and first <= limit else
                                    0 if len(attempts) >= limit or score is not None else None)
        heldout = any(attempt.get("terminal", {}).get("score") == 1 for attempt in attempts[:limit])
        hidden_curve[str(limit)] = (1 if heldout else
                                    0 if len(attempts) >= limit or score is not None else None)
    return {"terminal_success": score, "first_public_pass": first,
            "public_repair_by_attempt": public_curve,
            "diagnostic_any_heldout_pass_by_attempt": hidden_curve,
            "attempts_recorded": len(attempts),
            "disposition": result.get("disposition", "not_recorded")}


def _binary_summary(values):
    known = [value for value in values if value is not None]
    passed = sum(known)
    missing = len(values) - len(known)
    return {"planned_conditional_tasks": len(values), "known": len(known), "missing": missing,
            "passed": passed, "known_success_fraction": passed / len(known) if known else None,
            "finite_cohort_success_fraction_bounds": [passed / len(values), (passed + missing) / len(values)]
                if values else None}


def contrast(rows, weights, *, seed, bootstrap_replicates=10000, minimum_complete=6):
    """Linear paired contrast with exact finite-cohort missing-value bounds.

    Each row contains task_id, family and one binary/missing outcome per arm.
    The bounds optimize every missing cell independently in {0,1}; they are
    identification bounds for this fixed cohort, not confidence intervals.
    """
    if not weights or any(arm not in ARMS for arm in weights):
        raise ValueError("known nonempty factorial contrast required")
    if type(bootstrap_replicates) is not int or bootstrap_replicates < 0:
        raise ValueError("nonnegative bootstrap replicate count required")
    complete, lower, upper = [], [], []
    for row in rows:
        lo = hi = value = 0.0
        known = True
        for arm, weight in weights.items():
            observed = _score(row[arm])
            if observed is None:
                known = False
                lo += min(0.0, weight)
                hi += max(0.0, weight)
            else:
                lo += weight * observed
                hi += weight * observed
                value += weight * observed
        lower.append(lo)
        upper.append(hi)
        if known:
            complete.append((row["task_id"], row["family"], value))
    n = len(rows)
    interval = None
    if len(complete) >= minimum_complete and bootstrap_replicates:
        families = defaultdict(list)
        for _, family, value in complete:
            families[family].append(value)
        rng = random.Random(seed)
        groups = [families[family] for family in sorted(families)]
        draws = sorted(sum(sum(rng.choices(group, k=len(group))) for group in groups) / len(complete)
                       for _ in range(bootstrap_replicates))
        quantile = lambda probability: draws[max(0, math.ceil(probability * len(draws)) - 1)]
        interval = {"lower": quantile(0.025), "upper": quantile(0.975), "level": 0.95,
                    "method": "percentile task bootstrap stratified within authored family",
                    "replicates": bootstrap_replicates, "seed": seed,
                    "scope": "Complete cases only, conditional on the authored families and observed natural failures; not an interval for missing scores or unseen families."}
    return {
        "weights": dict(weights), "eligible_tasks": n, "complete_tasks": len(complete),
        "incomplete_tasks": n - len(complete),
        "complete_case_mean": sum(value for _, _, value in complete) / len(complete) if complete else None,
        "finite_cohort_missingness_bounds": [sum(lower) / n, sum(upper) / n] if n else None,
        "descriptive_bootstrap_95": interval,
        "complete_case_family_counts": dict(sorted(Counter(family for _, family, _ in complete).items())),
        "confirmatory_p_value": None,
    }


def _resources(calls):
    known = [call for call in calls if call["state"] == "completed"]
    unknown = [call for call in calls if call["state"] == "unknown"]
    return {
        "admitted_calls": len(calls), "known_calls": len(known), "unknown_calls": len(unknown),
        "inflight_calls": sum(call["state"] == "dispatched" for call in calls),
        "known_usage": {key: sum(call["usage"][key] for call in known)
                        for key in ("input_tokens", "cached_input", "output", "reasoning")},
        "known_planning_credits": str(sum((Decimal(call["planning_credits"]) for call in known), Decimal(0))),
        "unknown_locked_planning_credits": str(sum((Decimal(call["reserve_credits"]) for call in unknown), Decimal(0))),
        "sum_known_call_elapsed_seconds": sum(call["elapsed_seconds"] for call in known),
    }


def analyze(tasks, execution, accounting, manifest, *, simulated=False):
    """Keep calibration feasibility separate from the frozen factorial study."""
    by_id = {task["task_id"]: task for task in tasks}
    if len(by_id) != len(tasks):
        raise ValueError("duplicate task identity")
    results = {}
    for row in execution["jobs"]:
        job = row["job"]
        key = (job["task_id"], job["arm"])
        if key in results or job["task_id"] not in by_id or job["arm"] not in ("prefix", *ARMS):
            raise ValueError("duplicate or unallocated job result")
        results[key] = row["result"]
    allowance = manifest.get("continuation_attempts", 3)
    if type(allowance) is not int or allowance <= 0:
        raise ValueError("positive continuation allowance required")
    calibration = manifest.get("split") == "calibration"
    rows, dispositions, lessons = [], Counter(), Counter()
    for task in tasks:
        task_id = task["task_id"]
        prefix = results.get((task_id, "prefix"), {})
        eligible = prefix.get("eligible") is True
        dispositions[prefix.get("reason", "missing_prefix_result")] += 1
        if eligible:
            lessons[prefix.get("lesson_disposition", "not_recorded")] += 1
        row = {"task_id": task_id, "family": task["family"], "eligible": eligible,
               "prefix_reason": prefix.get("reason", "missing_prefix_result"), "arms": {}}
        for arm in ARMS:
            result = results.get((task_id, arm), {})
            endpoint = _outcome_endpoints(result, allowance) if eligible else None
            row[arm] = endpoint["terminal_success"] if endpoint else None
            row["arms"][arm] = endpoint
        rows.append(row)
    selected = [row for row in rows if row["eligible"]]
    arm_outcomes = {}
    requested_arms = ("K0",) if calibration else ARMS
    for arm in requested_arms:
        endpoints = [row["arms"][arm] for row in selected]
        arm_outcomes[arm] = {
            "terminal_success": _binary_summary([item["terminal_success"] for item in endpoints]),
            "public_repair_by_attempt": {str(limit): _binary_summary([
                item["public_repair_by_attempt"][str(limit)] for item in endpoints])
                for limit in range(1, allowance + 1)},
            "diagnostic_any_heldout_pass_by_attempt": {str(limit): _binary_summary([
                item["diagnostic_any_heldout_pass_by_attempt"][str(limit)] for item in endpoints])
                for limit in range(1, allowance + 1)},
            "dispositions": dict(sorted(Counter(item["disposition"] for item in endpoints).items())),
        }
    comparisons = {}
    if not calibration:
        for name, weights in CONTRASTS.items():
            seed = manifest.get("bootstrap_seed", manifest.get("seed", 0) + 1) + int(_hash(name)[:8], 16)
            comparisons[name] = contrast(selected, weights, seed=seed,
                bootstrap_replicates=manifest.get("bootstrap_replicates", 10000),
                minimum_complete=manifest.get("minimum_complete_for_interval", 6))
    calls = accounting["calls"]
    eligible_ids = {row["task_id"] for row in selected}
    complete_ids = {row["task_id"] for row in selected if all(row[arm] is not None for arm in ARMS)}

    def group(call):
        identity = call["identity"]
        return "shared_lesson" if identity["stage"] == "lesson" else "shared_prefix" if identity["arm"] == "prefix" else identity["arm"]

    resource_groups = {name: _resources([call for call in calls if group(call) == name])
                       for name in ("shared_prefix", "shared_lesson", *ARMS)}
    if sum(value["admitted_calls"] for value in resource_groups.values()) != len(calls):
        raise ValueError("call resource categories do not cover the ledger")
    projections = {}
    if not calibration:
        for arm in ARMS:
            included = {"shared_prefix", arm} | ({"shared_lesson"} if arm.endswith("L") else set())
            projections[arm] = _resources([call for call in calls
                if call["identity"]["task_id"] in complete_ids and group(call) in included])
    return {
        "evidence_kind": "offline_scripted_fixture" if simulated else "observed_subscription_generations",
        "manifest_sha256": _hash(manifest), "split": manifest.get("split"),
        "planned_tasks": len(tasks), "eligible_natural_failures": len(selected),
        "eligible_family_counts": dict(sorted(Counter(row["family"] for row in selected).items())),
        "prefix_dispositions": dict(sorted(dispositions.items())),
        "lesson_dispositions_on_eligible_prefixes": dict(sorted(lessons.items())),
        "complete_quartets": len(complete_ids), "arms": arm_outcomes,
        "factorial_contrasts": comparisons,
        "factorial_effects_evaluated": not calibration,
        "feasibility": {"substantive_natural_public_failures": len(selected),
                        "K0_publicly_repaired_within_allowance": arm_outcomes["K0"]["public_repair_by_attempt"][str(allowance)]["passed"]},
        "actual_study_resources": _resources(calls), "disjoint_resource_categories": resource_groups,
        "complete_quartet_standalone_resource_projections": projections,
        "projection_scope": "Complete quartets only. Each projection includes the shared prefix; only KL/RL include the shared writer. Projections overlap and must not be summed as actual spend.",
        "tasks": rows,
        "limitations": [
            "Conditional on observed eligible natural failures; report every planned prefix disposition separately. Unknown prefix eligibility is not silently imputed.",
            "Final task success requires public acceptance and a held-out pass of that accepted candidate. A held-out pass on a publicly failing candidate is diagnostic only.",
            "Unknown arm outcomes remain missing. Identification bounds cover the fixed eligible cohort; bootstrap intervals cover only complete cases and are descriptive.",
            "Bootstrap resamples tasks within the fixed authored families, preserving all four arm outcomes together; it does not measure generalization to unseen program families.",
            "No confirmatory p-value, automatic sample extension, equivalence conclusion from all-tie intervals, or private-reasoning effect is claimed.",
            "Equal actor-attempt allowances are not equal total computation: lesson generation is charged separately. Actual subscription debit is unavailable.",
        ],
    }
