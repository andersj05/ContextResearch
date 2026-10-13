"""Conditional paired development outcomes, missingness and complete accounting."""
from collections import Counter
import random
from statistics import median

from .common import sha
from ..rollback_development_v5.analysis import metering
from ..rollback_challenge_v6.statistics import paired


def analyze(tasks, execution, accounting, manifest, *, simulated):
    jobs = execution["jobs"]
    prefixes = {row["job"]["task_id"]: row["result"] for row in jobs if row["job"]["arm"] == "prefix"}
    eligible_ids = {task_id for task_id, prefix in prefixes.items() if prefix.get("eligible") is True}
    selected = [task for task in tasks if task["task_id"] in eligible_ids]
    rows = [{**row["job"], **row["result"]} for row in jobs if row["job"]["arm"] in {"K", "R"}]
    eligible_rows = [row for row in rows if row["task_id"] in eligible_ids]
    primary = paired(eligible_rows, selected, confirmatory=False)
    index = {(row["task_id"], row["arm"]): row.get("score") for row in eligible_rows}
    complete_ids = {task_id for task_id in eligible_ids if all(index.get((task_id, arm)) is not None for arm in ("K", "R"))}
    differences = [index[task["task_id"], "R"] - index[task["task_id"], "K"]
                   for task in selected if task["task_id"] in complete_ids]
    interval = None
    if len(differences) >= manifest["minimum_complete_pairs_for_descriptive_interval"]:
        rng = random.Random(manifest["seed"] + 1)
        draws = sorted(sum(rng.choices(differences, k=len(differences))) / len(differences) for _ in range(10000))
        interval = [draws[249], draws[9749]]
    primary.update(descriptive_task_bootstrap_95=interval, bootstrap_replicates=10000 if interval else 0,
                   interval_seed=manifest["seed"] + 1, confirmatory_p=None,
                   interval_scope="conditional on eligible authored tasks; all-tie intervals do not establish equivalence",
                   pair_count_screen_passed=len(complete_ids) >= manifest["minimum_complete_pairs_for_descriptive_interval"])
    calls = [call for call in accounting["calls"] if call["state"] == "completed"]
    resources = {arm: metering([call for call in calls if call["identity"]["arm"] == arm])
                 for arm in ("prefix", "K", "R")}
    complete_resources = {arm: metering([call for call in calls if call["identity"]["arm"] == arm
                                        and call["identity"]["task_id"] in complete_ids])
                          for arm in ("prefix", "K", "R")}
    standalone = {arm: metering([call for call in calls if call["identity"]["arm"] in {"prefix", arm}
                                 and call["identity"]["task_id"] in complete_ids]) for arm in ("K", "R")}
    arm_outcomes = {}
    for arm in ("K", "R"):
        subset = [row for row in eligible_rows if row["arm"] == arm]
        known = [row for row in subset if row.get("score") is not None]
        arm_outcomes[arm] = {"scheduled_conditional": len(selected), "known": len(known),
                             "passed": sum(row["score"] for row in known),
                             "missing": len(selected) - len(known),
                             "dispositions": dict(sorted(Counter(row["disposition"] for row in subset).items()))}
    prefix_reasons = Counter(prefix.get("reason", prefix.get("disposition", "unspecified")) for prefix in prefixes.values())
    stage_counts = Counter(str(prefix.get("state", {}).get("stage", -1) + 1)
                           for prefix in prefixes.values() if prefix.get("eligible"))
    proofs = [prefix["pair_contract"] for prefix in prefixes.values()
              if prefix.get("eligible") and "pair_contract" in prefix]
    context_sizes = {}
    for field in ("trial_bytes", "failed_record_bytes", "checkpoint_bytes", "public_dossier_bytes"):
        values = [proof[field] for proof in proofs]
        context_sizes[field] = {"pairs": len(values), "minimum": min(values) if values else None,
                                "median": median(values) if values else None,
                                "maximum": max(values) if values else None}
    task_rows = [{"task_id": task["task_id"], "eligible": task["task_id"] in eligible_ids,
                  "prefix_reason": prefixes.get(task["task_id"], {}).get("reason"),
                  "R": index.get((task["task_id"], "R")), "K": index.get((task["task_id"], "K"))}
                 for task in tasks]
    return {
        "evidence_kind": "offline_scripted_fixture" if simulated else "observed_subscription_generations",
        "manifest_sha256": sha(manifest), "split": manifest["split"], "selected_tasks": len(tasks),
        "prefix_dispositions": dict(sorted(prefix_reasons.items())), "eligible_prefixes": len(selected),
        "eligible_first_failure_stages": dict(sorted(stage_counts.items())),
        "eligible_context_sizes_utf8": context_sizes,
        "primary": primary, "arms": arm_outcomes, "tasks": task_rows,
        "shared_preparation_resources": resources["prefix"],
        "continuation_resources": {arm: resources[arm] for arm in ("K", "R")},
        "complete_pair_resources": complete_resources,
        "standalone_projections_complete_pairs": standalone,
        "projection_note": "Each projection includes the common preparation; projections overlap and must not be summed as actual spend.",
        "accounting": accounting,
        "limitations": [
            "Development pilot; no confirmatory superiority, equivalence, new-family, or native-compaction claim.",
            "Conditional effect after naturally failed shared prefixes; initial successes and unusable prefixes remain reported separately.",
            "Only one visible branch is removed. Shared lessons may retain branch-derived details; private reasoning is not replayed in either arm.",
            "All released task facts are retained in both arms, changing information access from v6; cross-study rate differences do not isolate a repair effect.",
            "Provider revision, sampling seed and actual subscription charges unavailable. Missing outcomes remain missing.",
            "Bootstrap intervals and complete-case exact p-values are descriptive; no automatic sample extension."
        ]
    }
