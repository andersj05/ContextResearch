"""Independently reconcile a *closed* four-arm patch study from saved JSON.

This script imports no experiment implementation, contacts no model, and never
executes submitted source. It checks saved grades and bookkeeping; Docker
regrading and request-isolation replay remain separate audits. Missing-outcome
bounds enumerate binary completions and are finite-cohort bounds, not CIs.
"""
from argparse import ArgumentParser
from collections import Counter, defaultdict
from decimal import Decimal
from fractions import Fraction
from hashlib import sha256
from itertools import product
from pathlib import Path
import json
import math
import sqlite3


ARMS = ("K0", "R0", "KL", "RL")
RELEVANT = {
    "deletion_without_lesson": ("K0", "R0"),
    "deletion_with_lesson": ("KL", "RL"),
    "lesson_when_keeping": ("K0", "KL"),
    "lesson_when_removing": ("R0", "RL"),
    "deletion_main": ARMS,
    "lesson_main": ARMS,
    "interaction": ARMS,
}
UNKNOWN_DISPOSITIONS = {"unknown_dispatch", "infrastructure_stop", "controller_error"}
ROOT = Path(__file__).resolve().parents[1]


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False)


def digest(value):
    return sha256(value if isinstance(value, bytes) else canonical(value).encode("utf-8")).hexdigest()


def read(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def require(condition, label):
    if not condition:
        raise ValueError(label)


def binary(value, label):
    require(type(value) is int and value in (0, 1), label)
    return value


def effects(values):
    """Evaluate the seven protocol expressions directly using exact fractions."""
    k0, r0, kl, rl = (Fraction(values[arm]) for arm in ARMS)
    d0, dl = r0 - k0, rl - kl
    lk, lr = kl - k0, rl - r0
    return {"deletion_without_lesson": d0, "deletion_with_lesson": dl,
            "lesson_when_keeping": lk, "lesson_when_removing": lr,
            "deletion_main": (d0 + dl) / 2, "lesson_main": (lk + lr) / 2,
            "interaction": dl - d0}


def contrasts(rows):
    accumulated = {name: {"lower": Fraction(0), "upper": Fraction(0),
                          "complete": [], "families": Counter()} for name in RELEVANT}
    for row in rows:
        missing = [arm for arm in ARMS if row[arm] is None]
        possible = []
        for replacements in product((0, 1), repeat=len(missing)):
            completed = {arm: row[arm] for arm in ARMS}
            completed.update(zip(missing, replacements))
            possible.append(effects(completed))
        for name, required in RELEVANT.items():
            values = [entry[name] for entry in possible]
            saved = accumulated[name]
            saved["lower"] += min(values)
            saved["upper"] += max(values)
            if all(row[arm] is not None for arm in required):
                require(len(set(values)) == 1, "irrelevant missing arms alter a contrast")
                saved["complete"].append(values[0])
                saved["families"][row["family"]] += 1
    result, total = {}, len(rows)
    for name, entry in accumulated.items():
        complete = entry["complete"]
        bounds = [entry["lower"] / total, entry["upper"] / total] if total else None
        mean = sum(complete, Fraction(0)) / len(complete) if complete else None
        result[name] = {
            "eligible_tasks": total, "complete_tasks": len(complete), "incomplete_tasks": total - len(complete),
            "complete_case_mean": float(mean) if mean is not None else None,
            "complete_case_mean_exact": str(mean) if mean is not None else None,
            "finite_cohort_missingness_bounds": [float(x) for x in bounds] if bounds is not None else None,
            "finite_cohort_missingness_bounds_exact": [str(x) for x in bounds] if bounds is not None else None,
            "complete_case_family_counts": dict(sorted(entry["families"].items())),
            "units": "difference in binary success proportions; multiply by 100 for percentage points",
            "scope": "Bounds enumerate missing binary outcomes in the fixed eligible cohort; not confidence intervals. Complete-case means can have a smaller denominator.",
        }
    return result


def terminal_from_receipts(result, allowance):
    """Reconstruct the endpoint from public stopping and accepted private grade."""
    attempts = result.get("attempts", [])
    require(len(attempts) <= allowance, "repair allowance exceeded")
    require([record["step"] for record in attempts] == list(range(1, len(attempts) + 1)),
            "nonsequential received repair attempts")
    passes = [index for index, record in enumerate(attempts, 1) if record["public"]["status"] == "public_pass"]
    if passes:
        require(len(passes) == 1 and passes[0] == len(attempts), "continued after public acceptance")
        value = binary(attempts[-1]["terminal"]["score"], "nonbinary accepted private score")
        require(result.get("first_pass") == passes[0], "public stopping step differs")
        require(result.get("score") == value and type(result.get("score")) is int, "saved terminal endpoint differs")
        return value
    require(result.get("first_pass") is None, "spurious public stopping step")
    disposition = result.get("disposition", "missing_result")
    if disposition == "repair_budget_exhausted":
        require(len(attempts) == allowance and result.get("score") == 0, "incorrect exhausted-budget endpoint")
        return 0
    if disposition == "context_capacity":
        require(result.get("score") == 0, "capacity disposition must retain its frozen zero score")
        return 0
    require(disposition in UNKNOWN_DISPOSITIONS or disposition.startswith("lesson_unavailable:"),
            "unexpected eligible missing disposition: " + str(disposition))
    require(result.get("score") is None, "unknown eligible arm imputed to a score")
    return None


def arm_summary(values):
    known = [value for value in values if value is not None]
    passed, total = sum(known), len(values)
    missing = total - len(known)
    return {"planned_conditional_tasks": total, "known": len(known), "passed": passed,
            "missing": missing, "known_success_fraction": passed / len(known) if known else None,
            "finite_cohort_success_fraction_bounds": [passed / total, (passed + missing) / total] if total else None}


def resources(calls):
    known = [call for call in calls if call["state"] == "completed"]
    unknown = [call for call in calls if call["state"] == "unknown"]
    require(len(known) + len(unknown) == len(calls), "closed run has in-flight calls")
    usage = {key: 0 for key in ("input_tokens", "cached_input", "output", "reasoning")}
    for call in known:
        for key in usage:
            value = call["usage"][key]
            require(type(value) is int and value >= 0, "invalid token usage")
            usage[key] += value
        require(call["usage"]["cached_input"] <= call["usage"]["input_tokens"], "cache usage exceeds input")
        require(call["usage"]["reasoning"] <= call["usage"]["output"], "reasoning usage exceeds output")
    return {"admitted_calls": len(calls), "known_calls": len(known), "unknown_calls": len(unknown),
            "inflight_calls": 0, "known_usage": usage,
            "known_planning_credits": str(sum((Decimal(call["planning_credits"]) for call in known), Decimal(0))),
            "unknown_locked_planning_credits": str(sum((Decimal(call["reserve_credits"]) for call in unknown), Decimal(0))),
            "sum_known_call_elapsed_seconds": sum(call["elapsed_seconds"] for call in known)}


def resource_group(call):
    identity = call["identity"]
    if identity["arm"] == "prefix":
        return "shared_lesson" if identity["stage"] == "lesson" else "shared_prefix"
    return identity["arm"]


def compare(actual, saved, label):
    if actual is None or saved is None:
        require(actual is saved, label)
    elif isinstance(actual, dict):
        require(isinstance(saved, dict), label)
        for key, value in actual.items():
            require(key in saved, label + "." + key + " missing")
            compare(value, saved[key], label + "." + key)
    elif isinstance(actual, list):
        require(isinstance(saved, list) and len(actual) == len(saved), label)
        for index, (value, other) in enumerate(zip(actual, saved)):
            compare(value, other, label + "." + str(index))
    elif isinstance(actual, float):
        require(isinstance(saved, (int, float)) and math.isclose(actual, saved, rel_tol=1e-12, abs_tol=1e-9), label)
    elif isinstance(actual, str) and label.endswith(("known_planning_credits", "unknown_locked_planning_credits")):
        require(Decimal(actual) == Decimal(saved), label)
    else:
        require(type(actual) is type(saved) and actual == saved, label)


def global_stop_gate(execution, accounting, active_stops, inherited_stops, recovery=None):
    """An operational resumption cannot erase an earlier failed validity gate."""
    active = active_stops[0] if active_stops else None
    require(len(active_stops) <= 1 and accounting["stop"] == active,
            "active global stop records differ")
    if recovery is None:
        require(not inherited_stops, "unamended run has inherited stops")
        require(type(execution["stopped"]) is bool and execution["stopped"] == bool(active_stops),
                "original execution stop differs from ledger")
    else:
        require(recovery["isolated_content_interpretation_gate_permanently_failed"] is True,
                "recovery erased original validity failure")
        require(inherited_stops == recovery["inherited_stops"] == [recovery["inherited_stop"]]
                and bool(inherited_stops[0]), "inherited original stop differs")
        require(execution["inherited_stops"] == inherited_stops and execution["stopped"] is True,
                "recovered execution erased original stop")
        require(type(execution["phase_stopped"]) is bool
                and execution["phase_stopped"] == bool(active_stops), "phase stop differs")
    return bool(active_stops or inherited_stops)


def recovery_accounting(manifest, run, execution, calls):
    """Partition cumulative resources without charging historical calls twice.

    Full executable receipt replay is a separate audit. Here original admitted
    rows and retained jobs are checked against the hash-bound sealed phase.
    """
    binding = manifest.get("recovery")
    if binding is None:
        return None
    prior = (ROOT / binding["prior_output"]).resolve()
    require(prior.is_relative_to(ROOT), "prior evidence escapes workspace")
    require(digest(read(prior / "evidence_manifest.json")) == binding["prior_evidence_manifest_sha256"],
            "bound original seal changed")
    require(digest((prior / "ledger.sqlite").read_bytes()) == binding["prior_ledger_sha256"],
            "bound original ledger changed")
    require(digest(read(prior / "manifest.json")) == binding["prior_manifest_sha256"],
            "bound original manifest changed")
    for name in ("execution.json", "manifest.json", "accounting.json", "evidence_manifest.json"):
        require((prior / name).read_bytes() == (run / ("prior_" + name)).read_bytes(),
                "original evidence copy changed: " + name)
    prior_execution, prior_accounting = read(prior / "execution.json"), read(prior / "accounting.json")
    require(prior_execution["stopped"] is True, "recovery did not inherit a stopped original phase")
    require(prior_accounting["stop"] == binding["inherited_stop"], "bound original stop changed")
    old = {call["call_id"]: call for call in prior_accounting["calls"]}
    cumulative = {call["call_id"]: call for call in calls}
    require(len(old) == len(prior_accounting["calls"]) == binding["prior_admissions"],
            "original admission count changed")
    for call_id, call in old.items():
        require(cumulative.get(call_id) == call, "historical call or unknown was changed")
    prior_resources = resources(list(old.values()))
    new_calls = [call for call in calls if call["call_id"] not in old]
    new_resources = resources(new_calls)
    total = resources(calls)
    require(prior_resources["known_calls"] == binding["prior_completed"]
            and prior_resources["unknown_calls"] == binding["prior_unknown"], "original state counts differ")
    for key in ("admitted_calls", "known_calls", "unknown_calls", "inflight_calls"):
        require(prior_resources[key] + new_resources[key] == total[key], "phase count does not sum: " + key)
    for key in total["known_usage"]:
        require(prior_resources["known_usage"][key] + new_resources["known_usage"][key]
                == total["known_usage"][key], "phase token count does not sum: " + key)
    for key in ("known_planning_credits", "unknown_locked_planning_credits"):
        require(Decimal(prior_resources[key]) + Decimal(new_resources[key]) == Decimal(total[key]),
                "phase planning units do not sum: " + key)
    compare(prior_execution["wall_seconds"] + execution["phase_wall_seconds"],
            execution["wall_seconds"], "phase wall time sum")
    prior_rows = {row["job"]["job_id"]: row for row in prior_execution["jobs"]}
    current_rows = {row["job"]["job_id"]: row for row in execution["jobs"]}
    plan = read(run / "recovery_plan.json")
    phase = read(run / "recovery_execution.json")
    require([row["job_id"] for row in plan["jobs"]] == [job["job_id"] for job in manifest["jobs"]],
            "recovery plan changed original jobs")
    require(digest(plan) == phase["selection_sha256"] == binding["selection_sha256"],
            "recovery plan binding differs")
    require(sorted(call["call_id"] for call in new_calls) == phase["new_admission_ids"],
            "new admissions differ from cumulative ledger difference")
    expected_replays, retained, resumed = set(), [], []
    for row in plan["jobs"]:
        job_id = row["job_id"]
        require(digest(prior_rows[job_id]) == row["prior_row_sha256"], "prior job provenance changed")
        owner = (row["task_id"], row["arm"])
        owned = [call for call in old.values() if
                 (call["identity"]["task_id"], call["identity"]["arm"]) == owner]
        unknown_ids = sorted(call["call_id"] for call in owned if call["state"] == "unknown")
        require(sorted(call["call_id"] for call in owned) == row["historical_call_ids"]
                and unknown_ids == row["unknown_call_ids"], "recovery ownership changed")
        if unknown_ids:
            require(row["decision"] == "retain", "unknown-owning job was resumed")
        if row["decision"] == "retain":
            retained.append(job_id)
            require(current_rows[job_id] == prior_rows[job_id], "retained job outcome changed")
            path = Path("jobs") / (job_id + ".json")
            require((run / path).read_bytes() == (prior / path).read_bytes(), "retained job bytes changed")
            require(not any((call["identity"]["task_id"], call["identity"]["arm"]) == owner
                            for call in new_calls), "retained job received a new call")
        else:
            require(row["decision"] == "resume", "unknown recovery decision")
            resumed.append(job_id)
            expected_replays.update(call["call_id"] for call in owned)
    require(sorted(expected_replays) == phase["historical_replayed_call_ids"], "replay inventory differs")
    require(plan["historical_admissions"] == phase["historical_admissions"] == len(old),
            "recovery historical admission count differs")
    require(plan["unknown_admissions_preserved"] == prior_resources["unknown_calls"],
            "recovery unknown count differs")
    return {"original_phase": prior_resources, "new_phase": new_resources,
            "cumulative_admissions": len(calls), "original_job_rows_retained": len(retained),
            "resumed_job_rows": len(resumed), "historical_receipts_replayed_without_new_admission": len(expected_replays),
            "original_unknown_rows_unchanged": True, "retained_job_bytes_unchanged": True,
            "prior_stop": binding["inherited_stop"], "causal_interpretation_gate_permanently_failed": True,
            "phase_wall_seconds": [prior_execution["wall_seconds"], execution["phase_wall_seconds"]],
            "scope": "Cumulative resources partition into original and new admissions. Historical receipt reconstruction is not a new model call; phase wall times exclude offline recovery preparation."}


def failed_components(task, prefix):
    record = prefix["failed_record"]
    receipt = record["public"]
    examples = {item["id"]: item for item in task["public_tests"]}
    require(receipt["check_id"] in examples, "failed receipt refers to a nonpublic case")
    example = examples[receipt["check_id"]]
    require(canonical(example["input"]) == canonical(receipt["input"]), "failed public input changed")
    require(canonical(example["expected"]) == canonical(receipt["expected"]), "failed public expected value changed")
    contracts = {row["component_id"]: row["family"] for row in task["contract"]["component_contracts"]}
    expected, observed = receipt["expected"], receipt["observed"]
    differing, extra = [], []
    if type(observed) is dict and type(expected) is dict:
        for name in expected:
            if name not in observed or canonical(observed[name]) != canonical(expected[name]):
                differing.append({"component_id": name, "family": contracts[name],
                                  "kind": "missing_component" if name not in observed else "wrong_component_value"})
        extra = sorted(set(observed) - set(expected))
        classification = "component_value_mismatch" if differing else "extra_component_keys"
    else:
        classification = "whole_compound_output_not_object"
    return {"task_id": task["task_id"], "leading_family": task["family"],
            "first_failing_public_case": receipt["check_id"], "classification": classification,
            "differing_components": differing, "extra_component_keys": extra,
            "changed_nonempty_lines": record["changed_nonempty_lines"],
            "failed_patch_utf8_bytes": len(record["visible_work"]["patch"].encode("utf-8")),
            "candidate_source_utf8_bytes": sum(len(row["text"].encode("utf-8")) for row in record["candidate"]["files"])}


def process_diagnostics(tasks, results, selected):
    """Describe visible stopping, private acceptance grades and shared hints.

    These observations locate failure categories in the saved experiment; they
    do not reveal a model's internal reason for failing or receiving a benefit.
    """
    initial_public, initial_joint, initial_private = Counter(), Counter(), Counter()
    missing_initial, initial_public_accepted_hidden_failed = 0, 0
    initial_public_pass_hidden_pass = 0
    for task in tasks:
        prefix = results[(task["task_id"], "prefix")]
        attempts = prefix.get("attempts", [])
        require(len(attempts) <= 1, "multiple initial attempts")
        if not attempts:
            missing_initial += 1
            continue
        record = attempts[0]
        public, private = record["public"]["status"], record["terminal"]["score"]
        binary(private, "nonbinary received initial private score")
        initial_public[public] += 1
        initial_private[str(private)] += 1
        initial_joint[public + "|private=" + str(private)] += 1
        initial_public_accepted_hidden_failed += int(public == "public_pass" and private == 0)
        initial_public_pass_hidden_pass += int(public == "public_pass" and private == 1)
    arm_process = {}
    for arm in ARMS:
        receipt_counts, first_public, first_joint, stopping, dispositions = (Counter() for _ in range(5))
        public_passes, accepted_correct, accepted_wrong, first_repair_correct = 0, 0, 0, 0
        receipt_statuses = Counter()
        for selected_task in selected:
            result = results[(selected_task["task_id"], arm)]
            attempts = result.get("attempts", [])
            receipt_counts[str(len(attempts))] += 1
            dispositions[result["disposition"]] += 1
            stopping[str(result.get("first_pass"))] += 1
            for record in attempts:
                receipt_statuses[record["public"]["status"]] += 1
            if attempts:
                public = attempts[0]["public"]["status"]
                private = binary(attempts[0]["terminal"]["score"], "nonbinary first repair private score")
                first_public[public] += 1
                first_joint[public + "|private=" + str(private)] += 1
                first_repair_correct += int(public == "public_pass" and private == 1)
            if result.get("first_pass") is not None:
                public_passes += 1
                accepted_correct += int(result["score"] == 1)
                accepted_wrong += int(result["score"] == 0)
        arm_process[arm] = {
            "eligible_tasks": len(selected), "received_attempt_count_distribution": dict(sorted(receipt_counts.items())),
            "first_received_public_statuses": dict(sorted(first_public.items())),
            "first_received_public_private_joint": dict(sorted(first_joint.items())),
            "all_received_public_statuses": dict(sorted(receipt_statuses.items())),
            "first_public_pass_step_counts": dict(sorted(stopping.items())),
            "first_repair_public_and_private_pass": first_repair_correct,
            "publicly_accepted_repairs": public_passes, "accepted_private_successes": accepted_correct,
            "accepted_private_failures": accepted_wrong, "terminal_dispositions": dict(sorted(dispositions.items())),
        }
    lesson_fields = {key: Counter() for key in ("focus", "location", "diagnosis", "next_check", "confidence")}
    lessons, missing_lessons = [], Counter()
    for selected_task in selected:
        prefix = results[(selected_task["task_id"], "prefix")]
        lesson = prefix.get("lesson")
        if lesson is None:
            missing_lessons[prefix["lesson_disposition"]] += 1
            continue
        require(prefix["lesson_disposition"] == "valid" and set(lesson) == set(lesson_fields),
                "unexpected saved lesson schema or disposition")
        for key, value in lesson.items():
            require(type(value) is str, "noncategorical saved lesson")
            lesson_fields[key][value] += 1
        lessons.append({"task_id": selected_task["task_id"], "leading_family": selected_task["family"],
                        "lesson": lesson})
    return {
        "initial_attempt": {"planned_tasks": len(tasks), "received_attempts": sum(initial_public.values()),
            "no_received_initial_attempt": missing_initial,
            "public_status_counts": dict(sorted(initial_public.items())),
            "private_score_counts": dict(sorted(initial_private.items())),
            "public_private_joint": dict(sorted(initial_joint.items())),
            "public_and_private_pass": initial_public_pass_hidden_pass,
            "public_pass_but_private_fail": initial_public_accepted_hidden_failed},
        "repairs_conditional_on_eligible_prefix": arm_process,
        "shared_lesson_content": {"eligible_tasks": len(selected), "valid_lessons": len(lessons),
            "missing_by_disposition": dict(sorted(missing_lessons.items())),
            "category_counts": {key: dict(sorted(counts.items())) for key, counts in lesson_fields.items()},
            "tasks": lessons,
            "scope": "One categorical lesson per eligible prefix is shared by KL and RL. Counts describe saved hints, not truth, independent treatment replicates, or evidence that a category causes an effect."},
        "scope": "Public acceptance ends an arm even if its held-out grade fails. Initial public passes are ineligible for the rollback comparison. First-repair correctness and final accepted correctness are distinct observed endpoints.",
    }


def audit(bundle, run):
    bundle, run = Path(bundle).resolve(), Path(run).resolve()
    # Check closure before opening outcome-bearing files. Never poll or summarize
    # a partially completed allocation through this entry point.
    require((run / "execution.json").is_file() and (run / "evidence_manifest.json").is_file(),
            "final execution and sealed evidence are required; no interim analysis")
    manifest, tasks = read(bundle / "manifest.json"), read(bundle / "tasks.json")
    require(manifest == read(run / "manifest.json"), "run and bundle manifest differ")
    require(digest(manifest) == read(bundle / "bundle.json")["manifest_sha256"], "manifest binding differs")
    require(digest(tasks) == manifest["tasks_sha256"], "task binding differs")
    evidence = read(run / "evidence_manifest.json")
    for row in evidence["files"]:
        path = (run / row["path"]).resolve()
        require(path.is_relative_to(run), "sealed path escapes run")
        require(digest(path.read_bytes()) == row["sha256"], "sealed evidence changed: " + row["path"])
    require(digest((run / "ledger.sqlite").read_bytes()) == evidence["ledger_sha256"], "sealed ledger changed")
    execution, accounting = read(run / "execution.json"), read(run / "accounting.json")
    settings, saved = read(run / "run_settings.json"), read(run / "analysis.json")
    require(type(settings["live"]) is bool, "unknown evidence kind")
    require(settings["retries"] == 0, "nonzero retry contract")
    require([row["job"] for row in execution["jobs"]] == manifest["jobs"], "final job inventory differs")
    task_map = {task["task_id"]: task for task in tasks}
    require(len(task_map) == len(tasks), "duplicate task")
    results = {(row["job"]["task_id"], row["job"]["arm"]): row["result"] for row in execution["jobs"]}
    require(len(results) == len(execution["jobs"]) == len(tasks) * 5, "four-arm final disposition inventory differs")
    require(set(results) == {(task_id, arm) for task_id in task_map for arm in ("prefix", *ARMS)}, "missing or foreign task arm")
    selected, prefix_reasons, lesson_reasons, diagnostics = [], Counter(), Counter(), []
    for task in tasks:
        task_id, family = task["task_id"], task["family"]
        prefix = results[(task_id, "prefix")]
        prefix_reasons[prefix["reason"]] += 1
        if prefix["eligible"] is True:
            require(prefix["failed_record"]["public"]["status"] == "public_mismatch", "eligible fork has no public mismatch")
            lesson_reasons[prefix["lesson_disposition"]] += 1
            selected.append({"task_id": task_id, "family": family, **{
                arm: terminal_from_receipts(results[(task_id, arm)], manifest["continuation_attempts"]) for arm in ARMS}})
            diagnostics.append(failed_components(task, prefix))
        else:
            require(prefix["eligible"] is False, "invalid eligibility flag")
            for arm in ARMS:
                result = results[(task_id, arm)]
                require(result["score"] is None and not result["attempts"] and
                        result["disposition"].startswith("not_eligible:"), "ineligible task acquired a repair outcome")
    summaries = {arm: arm_summary([row[arm] for row in selected]) for arm in ARMS}
    comparisons = contrasts(selected)
    family_counts = dict(sorted(Counter(row["family"] for row in selected).items()))
    compare(len(tasks), saved["planned_tasks"], "planned task count")
    compare(len(selected), saved["eligible_natural_failures"], "eligible task count")
    compare(family_counts, saved["eligible_family_counts"], "eligible families")
    compare(dict(prefix_reasons), saved["prefix_dispositions"], "prefix dispositions")
    compare(dict(lesson_reasons), saved["lesson_dispositions_on_eligible_prefixes"], "lesson dispositions")
    compare(sum(all(row[arm] is not None for arm in ARMS) for row in selected), saved["complete_quartets"], "complete quartets")
    for arm, summary in summaries.items():
        compare(summary, saved["arms"][arm]["terminal_success"], "arm " + arm)
    for name, values in comparisons.items():
        compared = {key: values[key] for key in ("eligible_tasks", "complete_tasks", "incomplete_tasks",
                    "complete_case_mean", "finite_cohort_missingness_bounds", "complete_case_family_counts")}
        compare(compared, saved["factorial_contrasts"][name], "contrast " + name)

    db = sqlite3.connect((run / "ledger.sqlite").as_uri() + "?mode=ro", uri=True)
    try:
        calls = [{"call_id": row[0], "identity": json.loads(row[1]), "request_hash": row[2],
                  "state": row[3], **json.loads(row[4])}
                 for row in db.execute("SELECT id,identity,request_hash,state,payload FROM calls ORDER BY id")]
        events = list(db.execute("SELECT call_id,state FROM events ORDER BY seq"))
        stop_reasons = [row[0] for row in db.execute("SELECT reason FROM stops ORDER BY id")]
        inherited_stops = [row[0] for row in db.execute("SELECT reason FROM inherited_stops ORDER BY rowid")]
    finally:
        db.close()
    require(calls == sorted(accounting["calls"], key=lambda row: row["call_id"]), "saved calls differ from durable SQLite")
    require(len({call["call_id"] for call in calls}) == len(calls), "duplicate admission")
    planned = {digest(identity): identity for identity in manifest["schedule"]}
    require(len(planned) == manifest["generation_ceiling"], "duplicate frozen generation identity")
    require(len(calls) <= manifest["generation_ceiling"], "generation ceiling exceeded")
    for call in calls:
        require(planned.get(call["call_id"]) == call["identity"], "unallocated call")
    admitted, active, peak = set(), set(), 0
    for call_id, state in events:
        if state == "dispatched":
            require(call_id not in admitted, "repeated admission event")
            admitted.add(call_id)
            active.add(call_id)
            peak = max(peak, len(active))
        else:
            require(state in ("completed", "unknown") and call_id in active, "invalid terminal call event")
            active.remove(call_id)
    require(not active and admitted == {call["call_id"] for call in calls}, "event inventory or drain differs")
    require(peak <= manifest["workers"], "worker admission cap exceeded")
    total_resources = resources(calls)
    compare(total_resources, saved["actual_study_resources"], "actual resources")
    compare(total_resources["known_calls"], accounting["completed_calls"], "completed accounting")
    compare(total_resources["unknown_calls"], accounting["unknown_or_inflight_calls"], "unknown accounting")
    compare(total_resources["known_usage"], accounting["usage"], "token accounting")
    require(Decimal(total_resources["known_planning_credits"]) == Decimal(accounting["planning_credits"]), "planning credit sum differs")
    require(Decimal(total_resources["unknown_locked_planning_credits"]) == Decimal(accounting["locked_planning_credits"]), "unknown reserve sum differs")
    groups = {name: resources([call for call in calls if resource_group(call) == name])
              for name in ("shared_prefix", "shared_lesson", *ARMS)}
    require(sum(row["admitted_calls"] for row in groups.values()) == len(calls), "resource groups do not partition calls")
    compare(groups, saved["disjoint_resource_categories"], "resource categories")
    capacity = [{"task_id": row["job"]["task_id"], "arm": row["job"]["arm"]}
                for row in execution["jobs"] if row["result"].get("reason") == "context_capacity"
                or row["result"].get("disposition") == "context_capacity"]
    globally_stopped = global_stop_gate(execution, accounting, stop_reasons, inherited_stops,
                                       manifest.get("recovery"))
    phase_resources = recovery_accounting(manifest, run, execution, calls)
    gate = {"passed": not capacity and not globally_stopped, "capacity_stops": capacity,
            "global_stop": globally_stopped}
    compare(gate, saved["capacity_interpretation_gate"], "capacity interpretation")
    task_component_families, component_counts = Counter(), Counter()
    for row in diagnostics:
        task_component_families.update({item["family"] for item in row["differing_components"]})
        component_counts.update(item["family"] for item in row["differing_components"])
    return {
        "passed": True, "evidence_kind": "independent_offline_reconciliation_of_" + ("live_observations" if settings["live"] else "scripted_fixture"),
        "model_calls_performed_by_audit": 0, "candidate_code_executed_by_audit": False,
        "live_model_admissions_in_audited_run": len(calls) if settings["live"] else 0,
        "manifest_sha256": digest(manifest), "sealed_evidence_manifest_sha256": digest(evidence),
        "audit_script_sha256": digest(Path(__file__).read_bytes()),
        "run": run.relative_to(ROOT).as_posix(), "bundle": bundle.relative_to(ROOT).as_posix(),
        "planned_tasks": len(tasks), "eligible_natural_failures": len(selected),
        "eligible_leading_family_counts": family_counts, "prefix_dispositions": dict(sorted(prefix_reasons.items())),
        "lesson_dispositions_on_eligible_prefixes": dict(sorted(lesson_reasons.items())),
        "arms": summaries, "factorial_contrasts": comparisons,
        "failure_and_repair_process": process_diagnostics(tasks, results, selected),
        "eligible_task_outcomes": selected, "actual_study_resources": total_resources,
        "disjoint_resource_categories": groups, "peak_simultaneous_admissions": peak,
        "capacity_interpretation_gate": gate,
        "operational_recovery_accounting": phase_resources,
        "first_failing_public_case_diagnostics": {
            "tasks_with_mismatching_component_family": dict(sorted(task_component_families.items())),
            "mismatching_components_by_family": dict(sorted(component_counts.items())),
            "classification_counts": dict(sorted(Counter(row["classification"] for row in diagnostics).items())),
            "tasks": diagnostics,
            "scope": "Only the first reported public mismatch per eligible prefix. Whole-output shape errors are not attributed to component algorithms. A component can differ in several tasks; these are descriptive counts, not independent trials or internal-cause diagnoses."},
        "scope": [
            "All contrasts are conditional on the fixed cohort's observed eligible naturally failed prefixes. Unknown prefix eligibility is reported through dispositions, not included as a known failed prefix.",
            "Finite-cohort bounds enumerate missing binary outcomes; they are not confidence intervals. This independent script does not recompute bootstrap intervals or assign confirmatory p-values.",
            "Token units are provider-recorded counts: cached_input is a subset of input_tokens and reasoning is a subset of output. Planning credits and unknown reservations are bookkeeping units, not actual subscription charges or dollars.",
            "Shared prefix and lesson calls are counted once in actual spend. Resource categories partition calls; no overlapping standalone-policy projections are added together.",
            "This checks outcomes from saved public/private receipts and durable accounting. It does not replace isolated source regrading, request replay, or verification of inaccessible provider internals.",
            "Any operational recovery retains the original failed interpretation gate. Descriptive contrasts can span provider time and operational phases; resumption does not turn them into isolated causal estimates.",
        ],
    }


def self_test():
    row = {"task_id": "constructed-missingness", "family": "fixture", "K0": 1, "R0": None, "KL": 0, "RL": None}
    calculated = contrasts([row])
    expected = {"deletion_without_lesson": [-1, 0], "deletion_with_lesson": [0, 1],
                "lesson_when_keeping": [-1, -1], "lesson_when_removing": [-1, 1],
                "deletion_main": [-0.5, 0.5], "lesson_main": [-1, 0], "interaction": [0, 2]}
    for name, bounds in expected.items():
        require(calculated[name]["finite_cohort_missingness_bounds"] == bounds, "self-test bound " + name)
    require(calculated["lesson_when_keeping"]["complete_case_mean"] == -1, "self-test complete contrast")
    require(calculated["deletion_without_lesson"]["complete_case_mean"] is None, "self-test incomplete contrast")
    public_fail = {"step": 1, "public": {"status": "public_mismatch"}, "terminal": {"score": 1}}
    missing = {"attempts": [public_fail], "score": None, "first_pass": None, "disposition": "unknown_dispatch"}
    require(terminal_from_receipts(missing, 3) is None, "self-test unknown is not failure")
    accepted = {"attempts": [{"step": 1, "public": {"status": "public_pass"}, "terminal": {"score": 0}}],
                "score": 0, "first_pass": 1, "disposition": "test_failure"}
    require(terminal_from_receipts(accepted, 3) == 0, "self-test hidden failure of accepted repair")
    sample = resources([{"state": "completed", "usage": {"input_tokens": 5, "cached_input": 2, "output": 3, "reasoning": 1},
                         "planning_credits": "0.1", "elapsed_seconds": 2},
                        {"state": "unknown", "reserve_credits": "0.2"}])
    require(sample["known_calls"] == sample["unknown_calls"] == 1 and sample["known_usage"]["input_tokens"] == 5
            and sample["known_usage"]["output"] == 3, "self-test usage subcategories double-counted")
    require(not global_stop_gate({"stopped": False}, {"stop": None}, [], []), "self-test clean original gate")
    require(global_stop_gate({"stopped": True}, {"stop": "original"}, ["original"], []),
            "self-test original stopped gate")
    recovery = {"inherited_stop": "original", "inherited_stops": ["original"],
                "isolated_content_interpretation_gate_permanently_failed": True}
    continued = {"stopped": True, "phase_stopped": False, "inherited_stops": ["original"]}
    require(global_stop_gate(continued, {"stop": None}, [], ["original"], recovery),
            "self-test inherited stop cannot disappear")
    for bad_execution, bad_inherited in ((dict(continued, stopped=False), ["original"]), (continued, [])):
        try:
            global_stop_gate(bad_execution, {"stop": None}, [], bad_inherited, recovery)
        except ValueError:
            pass
        else:
            raise ValueError("self-test erased inherited stop was accepted")
    tasks = [{"task_id": "eligible", "family": "fixture"}, {"task_id": "initial-pass", "family": "fixture"}]
    lesson = {"focus": "requirements", "location": "rules.py", "diagnosis": "missing_constraint",
              "next_check": "trace_failed_example", "confidence": "low"}
    recorded = {
        ("eligible", "prefix"): {"attempts": [public_fail], "lesson": lesson, "lesson_disposition": "valid"},
        ("initial-pass", "prefix"): {"attempts": accepted["attempts"]},
        ("eligible", "K0"): accepted,
        ("eligible", "R0"): {"attempts": [public_fail, {"step": 2, "public": {"status": "public_pass"},
                               "terminal": {"score": 1}}], "score": 1, "first_pass": 2, "disposition": "correct"},
        ("eligible", "KL"): {"attempts": [public_fail], "score": None, "first_pass": None,
                                "disposition": "infrastructure_stop"},
        ("eligible", "RL"): {"attempts": [], "score": None, "first_pass": None,
                                "disposition": "unknown_dispatch"},
    }
    process = process_diagnostics(tasks, recorded, [{"task_id": "eligible", "family": "fixture"}])
    require(process["initial_attempt"]["public_pass_but_private_fail"] == 1,
            "self-test initial public and hidden outcomes conflated")
    repairs = process["repairs_conditional_on_eligible_prefix"]
    require(repairs["K0"]["accepted_private_failures"] == 1
            and repairs["R0"]["first_repair_public_and_private_pass"] == 0
            and repairs["R0"]["accepted_private_successes"] == 1,
            "self-test immediate and eventual hidden correctness conflated")
    require(process["shared_lesson_content"]["valid_lessons"] == 1
            and process["shared_lesson_content"]["category_counts"]["confidence"] == {"low": 1}
            and repairs["RL"]["received_attempt_count_distribution"] == {"0": 1},
            "self-test shared lesson or unreceived arm double counted")
    return {"passed": True, "constructed_checks": 20, "model_calls": 0}


def main():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("--bundle", type=Path)
    parser.add_argument("--run", type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--self-test", action="store_true")
    arguments = parser.parse_args()
    checked = self_test() if arguments.self_test else None
    if arguments.bundle is None and arguments.run is None and arguments.output is None:
        require(arguments.self_test, "provide bundle/run/output or --self-test")
        print(canonical(checked))
        return
    require(all(value is not None for value in (arguments.bundle, arguments.run, arguments.output)),
            "bundle, run and output are required together")
    output = arguments.output.resolve()
    require(output.is_relative_to(ROOT) and not output.is_relative_to(arguments.run.resolve()),
            "audit destination must be in workspace outside the sealed run")
    require(not output.exists(), "new audit output required")
    report = audit(arguments.bundle, arguments.run)
    if checked is not None:
        report["constructed_self_test"] = checked
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("x", encoding="utf-8") as destination:
        json.dump(report, destination, indent=2, sort_keys=True, ensure_ascii=False, allow_nan=False)
        destination.write("\n")
    print(canonical({"passed": report["passed"], "output": str(output), "planned_tasks": report["planned_tasks"],
                     "eligible_natural_failures": report["eligible_natural_failures"], "arms": report["arms"],
                     "calls": report["actual_study_resources"]["admitted_calls"],
                     "known": report["actual_study_resources"]["known_calls"],
                     "unknown": report["actual_study_resources"]["unknown_calls"]}))


if __name__ == "__main__":
    main()
