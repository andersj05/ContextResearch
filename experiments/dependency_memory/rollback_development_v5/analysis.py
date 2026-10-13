"""Task-paired descriptive reporting; complete-episode and conditional effects separate."""
from collections import Counter, defaultdict
from statistics import mean, median
from decimal import Decimal
import random

from .common import SEED, sha


def interval(differences):
    if len(differences) < 6:
        return None
    rng = random.Random(SEED)
    n = len(differences)
    samples = sorted(sum(rng.choices(differences, k=n)) / n for _ in range(10000))
    return {"kind": "descriptive_task_bootstrap", "lower": samples[250], "upper": samples[9750], "resamples": 10000,
            "scope": "constructed task distribution only; not family-generalization or confirmation"}


def comparison(rows, left, right):
    indices = {arm: {r["task_id"]: r for r in rows if r["arm"] == arm} for arm in (left, right)}
    tasks = sorted(set(indices[left]) & set(indices[right])); d = []; bounds = []
    for task_id in tasks:
        a, b = indices[left][task_id]["score"], indices[right][task_id]["score"]
        bounds.append(((a if a is not None else 0) - (b if b is not None else 1),
                       (a if a is not None else 1) - (b if b is not None else 0)))
        if a is not None and b is not None:
            d.append(a - b)
    return {"left": left, "right": right, "scheduled_pairs": len(tasks), "complete_pairs": len(d),
            "mean_difference": mean(d) if d else None, "interval": interval(d), "differences": dict(Counter(d)),
            "fixed_denominator_missingness_bounds": [mean(x[i] for x in bounds) for i in (0, 1)] if bounds else None,
            "confirmatory_p_value": None}


def metering(calls):
    return {"recorded_calls": len(calls), "input_tokens": sum(c["usage"]["input_tokens"] for c in calls),
            "output_tokens_including_reasoning": sum(c["usage"]["output"] for c in calls),
            "cached_input_tokens": sum(c["usage"]["cached_input"] for c in calls),
            "reasoning_tokens_subset_of_output": sum(c["usage"]["reasoning"] for c in calls),
            "planning_credits": str(sum((Decimal(c["planning_credits"]) for c in calls), Decimal(0))),
            "sum_call_elapsed_seconds": sum(c["elapsed_seconds"] for c in calls)}


def analyze(tasks, execution, accounting, simulated=False):
    metadata = {t["task_id"]: t for t in tasks}; tracks = {}; prefix = []
    completed_calls = [c for c in accounting["calls"] if c["state"] == "completed"]
    allrows = []
    for row in execution["jobs"]:
        job, result = row["job"], row["result"]
        if job["arm"] == "prefix":
            prefix.append({"task_id": job["task_id"], **result}); continue
        t = metadata[job["task_id"]]
        allrows.append({"task_id": job["task_id"], "track": job["track"], "arm": job["arm"],
                        "family": t["family"], "domain": t["domain"], "horizon": t["horizon"], "difficulty": t["difficulty"], **result})
    for track in sorted({r["track"] for r in allrows}):
        selected = [r for r in allrows if r["track"] == track]
        # Ineligible common prefixes have no conditional recovery effect. Preserve them separately.
        eligible = {p["task_id"] for p in prefix if p.get("eligible")}
        measured = [r for r in selected if track != "mechanism" or r["task_id"] in eligible]
        conditions = {}
        for arm in sorted({r["arm"] for r in selected}):
            rows = [r for r in measured if r["arm"] == arm]
            known = [r for r in rows if r["score"] is not None]
            # Ledger identities retain paid work even if a grader/controller fails
            # before it can save a normal episode outcome or its call-id list.
            task_ids = {r["task_id"] for r in rows}
            calls = [c for c in completed_calls if c["identity"]["track"] == track and c["identity"]["arm"] == arm and c["identity"]["task_id"] in task_ids]
            conditions[arm] = {"tasks": len(rows), "known": len(known), "correct": sum(r["score"] for r in known),
                               "success_rate": mean(r["score"] for r in known) if known else None,
                               "success_rate_missingness_bounds": [sum(r["score"] for r in known) / len(rows),
                                                                     (sum(r["score"] for r in known) + len(rows) - len(known)) / len(rows)] if rows else None,
                               "dispositions": dict(Counter(r["disposition"] for r in rows)),
                               **metering(calls),
                               "resource_scope": "actual arm calls; common preparation separately reported for mechanism"}
        groups = {}
        for dimension in ("domain", "family", "horizon", "difficulty"):
            groups[dimension] = {value: comparison([r for r in measured if r[dimension] == value], "R", "K")
                                 for value in sorted({r[dimension] for r in measured})}
        tracks[track] = {"conditions": conditions, "R_minus_K": comparison(measured, "R", "K"), "strata": groups,
                         "secondary": [comparison(measured, *arms) for arms in (("R", "Z"), ("R", "G"), ("R", "F")) if all(any(r["arm"] == a for r in measured) for a in arms)]}
        if track == "mechanism":
            tracks[track]["evidence_lesson_R_minus_K"] = comparison(measured, "RE", "KE")
            tracks[track]["prefix_dispositions"] = dict(Counter(p.get("reason", "eligible_public_mismatch") for p in prefix))
            tracks[track]["shared_preparation"] = metering([c for c in completed_calls if c["identity"]["track"] == "mechanism" and c["identity"]["arm"] in {"prefix", "shared"}])
    calibration = []
    for horizon in ("short", "medium", "long"):
        for difficulty in ("moderate", "hard"):
            controls = [r for r in allrows if r["track"] == "policy" and r["arm"] in {"K", "F"} and r["horizon"] == horizon and r["difficulty"] == difficulty]
            cell = {"horizon": horizon, "difficulty": difficulty, "control_target": [0.4, 0.75], "scope": "descriptive design calibration; never a stop/exclusion rule"}
            for arm in ("K", "F"):
                rows = [r for r in controls if r["arm"] == arm]; known = [r for r in rows if r["score"] is not None]
                events = [e for r in rows for e in r.get("events", [])]
                cell[arm] = {"selected_tasks": len(rows), "known": len(known), "success_rate": mean(r["score"] for r in known) if known else None,
                             "median_actions": median(r["actions_used"] for r in rows if "actions_used" in r) if any("actions_used" in r for r in rows) else None,
                             "median_visible_history_bytes": median(e["input_history_bytes"] for e in events) if events else None}
            calibration.append(cell)
    return {"evidence_kind": "offline_scripted_fixture" if simulated else "prospective_model_development",
            "unique_tasks": len(tasks), "tracks_reuse_tasks": True, "tracks": tracks, "accounting": accounting,
            "control_calibration": calibration,
            "parallelism": {k: execution[k] for k in ("worker_count", "peak_active_jobs", "wall_seconds", "stopped")},
            "human_semantic_error_ratings": "unperformed", "immutable_provider_revision": None,
            "provider_sampling_seed": None, "construction_seed": SEED,
            "limitations": "48 constructed tasks in four fixed families. Repeated conditions are not independent tasks. Horizon alters disclosure timing and allowed computation together. No confirmation, native-compaction result, or actual account charge is established."}
