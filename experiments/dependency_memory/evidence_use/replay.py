"""Reconstruct pinned historical finals; keep evaluator evidence outside guard."""
from __future__ import annotations

import argparse
from collections import Counter
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import platform
import sys
from time import perf_counter_ns, process_time_ns

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "experiments/dependency_memory"))
HERE = Path(__file__).parent
RESULTS = ROOT / "experiments/dependency_memory/results"
OUTPUT = RESULTS / "evidence_use_2026-10-01"

from . import guard
from experiments.dependency_memory.cross_record import run as cross_run, analyze as cross_analysis
from experiments.dependency_memory.cross_record_continuation import analyze as cross_combined
from experiments.dependency_memory.workflow_eval_live import study as live_study, analyze as live_analysis
from experiments.dependency_memory.workflow_executed import study as executed_study
from experiments.dependency_memory.workflow_executed_posthoc import audit as executed_audit


def read(path):
    return json.loads(path.read_text(encoding="utf-8"))


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()).hexdigest()


def verify_sources():
    lock = read(HERE / "source-lock.json")
    if lock["version"] != "evidence_use_sources_v1":
        raise ValueError("Unknown evidence source lock")
    for name, expected in lock["sha256"].items():
        path = ROOT / name
        if not path.is_relative_to(ROOT) or hashlib.sha256(path.read_bytes()).hexdigest() != expected:
            raise ValueError("Historical input changed: " + name)
    return len(lock["sha256"])


def _calls(*directories):
    result = {}
    for directory in directories:
        for path in (directory / "calls").glob("*.json"):
            value = read(path)
            if path.stem != value["identity"] or path.stem in result:
                raise ValueError("Duplicate or inconsistent historical call")
            result[path.stem] = value
    return result


def observations():
    """Existing analyzers validate requests, answers, costs and frozen provenance."""
    verified = {
        "cross_record": cross_combined.analyze(cross_combined.OUTPUT),
        "workflow_live": live_analysis.analyze(RESULTS / "workflow_live_2026-09-29"),
        "workflow_executed": executed_audit.analyze(),
    }
    all_rows = []
    cross_calls = _calls(cross_combined.ORIGINAL, cross_combined.OUTPUT)
    cross_cases = {}
    for path in cross_run.fixture_paths()[0]:
        case = read(path)
        for future in case["futures"]:
            cross_cases[future["id"]] = (case, future)
    for old in verified["cross_record"]["decisions"]:
        call = cross_calls[old["identity"]]
        case, future = cross_cases[old["future_id"]]
        parent = None
        if old["arm"] in {"prompt", "structured", "checked", "automatic", "direct"}:
            episode_path = cross_combined.OUTPUT / (case["id"] + "-episode.json")
            if not episode_path.exists():
                episode_path = cross_combined.ORIGINAL / episode_path.name
            parent = read(episode_path)["memories"][old["arm"]]["parent"]
        all_rows.append({"study": "cross_record", "arm": old["arm"], "identity": old["identity"],
                         "status": "observed" if call["status"] == "completed" else "missing_transport",
                         "expected": old["expected"], "response": call.get("response"),
                         "correct": old["correct"] if call["status"] == "completed" else None,
                         "request": call["request"], "parent_memory": parent,
                         "origin": "constructed_cross_record_trace", "historical_information": old["information"]})
    for study_name, study, directories in (
        ("workflow_live", live_study, (RESULTS / "workflow_live_2026-09-29",)),
        ("workflow_executed", executed_study, (RESULTS / "workflow_executed_2026-09-29", RESULTS / "workflow_executed_continuation_2026-09-29")),
    ):
        calls = _calls(*directories)
        cases = {c["id"]: c for c in study.cases()}
        for arm, arm_results in verified[study_name]["arms"].items():
            for old in arm_results["outcomes"]:
                case = cases[old["case"]]
                identity = case["id"] + "-" + arm + "-final"
                call = calls.get(identity)
                status = old.get("status", "observed")
                parent = None
                if call and arm == "direct":
                    parent = study.wire(live_study.direct_records(case["initial"])).decode()
                elif call and arm in {"checked", "prose"}:
                    child_call = calls.get(case["id"] + "-" + arm + "-child")
                    if child_call and child_call["status"] == "completed":
                        parent = child_call["request"]["observation"]["previous_memory"]
                all_rows.append({"study": study_name, "arm": arm, "identity": identity,
                                 "status": status, "expected": old.get("expected"),
                                 "response": old.get("response"), "correct": old.get("exact"),
                                 "request": call["request"] if call else None, "parent_memory": parent,
                                 "origin": case.get("origin", "authored_executed_scenario"), "historical_information": None})
    return all_rows, verified


def manual_prose_review(row):
    """One explicitly bounded human reading, never an automatic prose parser."""
    if (row["study"], row["identity"]) != ("workflow_live", "later_failure-prose-final"):
        return None
    memory = row["request"]["observation"]["memory"]
    task = row["request"]["observation"]["final_public_state"]
    quote = "repository latest observed success 9898533afb7afeeff47ea3bb12fc9ddbebe02a716a34f6e1f29a88bab30e4eaf."
    if (quote not in memory or task["snapshot"] != "09cada8a37340510b558263d367b89c8cd2620b8"
            or row["expected"]["evidence"].get("repository") != quote.split()[-1][:-1]):
        raise ValueError("Reviewed prose example changed")
    return {"review": "human_reading_of_one_retained_statement_against_public_rule_and_snapshot",
            "memory_sha256": hashlib.sha256(memory.encode()).hexdigest(), "public_task_sha256": digest(task),
            "quote": quote, "interpretation": "The same-snapshot repository success is retained; the final answer omits it and requests repository work.",
            "scope": "repository obligation only; does not certify every prose claim or supply an actor decoder"}


def diagnose(row):
    result = {k: row[k] for k in ("study", "arm", "identity", "status", "correct", "origin", "historical_information")}
    if row["status"] != "observed":
        return {**result, "failure_class": row["status"], "guard": None, "derived_exact": None}
    request, proposal = row["request"], row["response"]
    checked = guard.check(request, proposal)
    readout = checked["derived_answer"]
    derived_exact = readout == row["expected"] if readout is not None else None
    if row["correct"]:
        kind = "correct"
    elif derived_exact:
        kind = "wrong_proposal_despite_matching_retained_readout"
    elif readout is not None:
        kind = "retained_readout_disagrees_with_full_ledger"
    elif request["observation"]["memory"] == "":
        kind = "empty_terminal_memory"
    else:
        kind = "uncheckable_representation"
    manual = manual_prose_review(row)
    if manual and not row["correct"]:
        kind = "reviewed_retained_obligation_misused"
    first_disagreement = None
    if kind == "retained_readout_disagrees_with_full_ledger" and row["parent_memory"] is not None:
        probe = deepcopy(request)
        probe["observation"]["memory"] = row["parent_memory"]
        try:
            parent_readout = guard.derive(probe)
            first_disagreement = "by_first_boundary" if parent_readout != row["expected"] else "by_second_boundary"
        except (ValueError, TypeError, KeyError, RecursionError):
            first_disagreement = "parent_uncheckable"
    return {**result, "failure_class": kind, "first_observed_readout_disagreement": first_disagreement,
            "memory_sha256": hashlib.sha256(request["observation"]["memory"].encode()).hexdigest(),
            "memory_bytes": len(request["observation"]["memory"].encode()),
            "guard": checked, "derived_exact": derived_exact, "response": proposal,
            "expected": row["expected"], "manual_review": manual}


def summarize(rows):
    observed = [r for r in rows if r["status"] == "observed"]
    errors = [r for r in observed if not r["correct"]]
    return {
        "scheduled_finals": len(rows), "observed_finals": len(observed),
        "missing_transport": sum(r["status"] == "missing_transport" for r in rows),
        "not_dispatched": sum(r["status"] == "not_dispatched" for r in rows),
        "raw_correct": sum(r["correct"] for r in observed), "raw_errors": len(errors),
        "failure_classes": dict(sorted(Counter(r["failure_class"] for r in errors).items())),
        "guard_status": dict(sorted(Counter(r["guard"]["status"] for r in observed).items())),
        "wrong_proposals_contradicted": sum(r["guard"]["status"] == "contradicted" for r in errors),
        "wrong_proposals_consistent": sum(r["guard"]["status"] == "consistent" for r in errors),
        "wrong_proposals_uncheckable": sum(r["guard"]["status"] == "uncheckable" for r in errors),
        "correct_proposals_contradicted": sum(r["correct"] and r["guard"]["status"] == "contradicted" for r in observed),
        "correct_proposals_uncheckable": sum(r["correct"] and r["guard"]["status"] == "uncheckable" for r in observed),
        "derived_answers_available": sum(r["derived_exact"] is not None for r in observed),
        "derived_answers_correct": sum(r["derived_exact"] is True for r in observed),
        "derived_answers_wrong": sum(r["derived_exact"] is False for r in observed),
    }


def analyze():
    source_count = verify_sources()
    inputs, historical = observations()
    rows = [diagnose(row) for row in inputs]
    studies = {}
    for name in sorted({r["study"] for r in rows}):
        subset = [r for r in rows if r["study"] == name]
        studies[name] = {"summary": summarize(subset), "arms": {arm: summarize([r for r in subset if r["arm"] == arm]) for arm in sorted({r["arm"] for r in subset})}}
    paths = sorted(HERE.glob("*.py")) + [HERE / "PROTOCOL.md", HERE / "source-lock.json"]
    return {"version": "evidence_use_retrospective_v1", "date": "2026-10-01", "new_model_calls": 0,
            "protocol_freeze_commit": "24da0e1", "historical_input_files": source_count,
            "source_sha256": {p.relative_to(ROOT).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest() for p in paths},
            "summary": summarize(rows), "studies": studies, "decisions": rows,
            "historical_primary_status": {"cross_record": historical["cross_record"]["original_primary_criterion"], "workflow_live": "held_out_unassessed", "workflow_executed": historical["workflow_executed"]["original_primary_criterion"]},
            "limits": ["Post-hoc replay of inspected, correlated development evidence; no new model answer or unseen evaluation.",
                       "Hand-written public-rule interpreters, not automatic extraction or arbitrary prose checking.",
                       "Readout agreement is an instance-level calculation, not authentication or coverage of the full source.",
                       "A veto or abstention is not a corrected task; deterministic outputs are separately scored counterfactuals.",
                       "Original missing outcomes, primary criteria and model-cost ledgers remain unchanged; local resources are unpriced."]}


def report(result):
    s = result["summary"]
    lines = ["# Retained evidence and final decision audit", "", "October 1, 2026. Post-hoc offline replay; zero new model calls.", "",
             f"{s['scheduled_finals']} scheduled finals: {s['observed_finals']} observed, {s['missing_transport']} transport gaps and {s['not_dispatched']} never dispatched.",
             "Pooled counts reconcile the ledger; these are correlated observations, not independent trials.", "",
             "| Study / arm | Raw correct / observed | Wrong contradicted | Wrong consistent | Wrong uncheckable | Correct contradicted / uncheckable | Derived correct / available |",
             "|---|---:|---:|---:|---:|---:|---:|"]
    for study, data in result["studies"].items():
        for arm, row in data["arms"].items():
            lines.append(f"| {study} / {arm} | {row['raw_correct']}/{row['observed_finals']} | {row['wrong_proposals_contradicted']} | {row['wrong_proposals_consistent']} | {row['wrong_proposals_uncheckable']} | {row['correct_proposals_contradicted']} / {row['correct_proposals_uncheckable']} | {row['derived_answers_correct']}/{row['derived_answers_available']} |")
    lines += ["", "Failure classes:", ""]
    for kind, count in s["failure_classes"].items():
        lines.append(f"- {kind}: {count}")
    lines += ["", "The actor-side check reads only admitted memory and the already public rule/state. Full ledgers and intermediate memories are evaluator-only. The three outcomes are consistency, contradiction and uncheckable representation.", "",
              "A contradicted answer can be vetoed, but no repair call or new execution occurs. A consistent answer can still be wrong if memory omitted or changed evidence. Correct prose answers can become uncheckable under this typed parser; that abstention cost must be reported. No overall guard or compression gain is inferred.", "",
              "The single reviewed prose obligation preserves a repository success which the final answer omits. That bounded human reading does not give the actor an automatic prose decoder.", "",
              "The associated tests include a same-memory/different-history omission witness: a later failed run can be absent from retained memory without changing any guard input. The guard therefore cannot authenticate completeness. Explicit provenance/coverage would be additional state to budget and validate prospectively.", "",
              "The JSON includes every identity, original answer, diagnostic, input hashes, missing disposition and counterfactual readout. Historical primary outcomes and costs remain unchanged. Batched local measurements are saved separately and are not priced.", ""]
    return "\n".join(lines)


def benchmark(inputs, repeats):
    eligible = [r for r in inputs if r["status"] == "observed"]
    batch_input = sum(len(json.dumps([r["request"], r["response"]], separators=(",", ":")).encode()) for r in eligible)
    batch_output = sum(len(json.dumps(guard.check(r["request"], r["response"]), separators=(",", ":")).encode()) for r in eligible)
    cpu, wall = process_time_ns(), perf_counter_ns()
    for _ in range(repeats):
        for row in eligible:
            guard.check(row["request"], row["response"])
    return {"scope": "in-process final check only; excludes evidence loading, evaluator grading, model calls, I/O and human rule compilation",
            "python": platform.python_version(), "platform": platform.platform(), "repeats": repeats,
            "checks_per_repeat": len(eligible), "cpu_ns": process_time_ns() - cpu, "wall_ns": perf_counter_ns() - wall,
            "serialized_input_bytes_per_repeat": batch_input, "serialized_output_bytes_per_repeat": batch_output,
            "byte_definition": "compact JSON of the whole final request/proposal and result; includes already public instructions, excludes evaluator evidence",
            "price": None, "total_cost_claim": False}


def witnesses(inputs):
    """Post-hoc reduction of inspected cases, retaining the exact public task."""
    selected = (
        ("data_pipeline-1854593748-0-automatic", "proposed_publish_despite_stale_approval"),
        ("ci_promotion-3868710405-1-structured", "exact_identifier_transcription_error"),
        ("tests_recovery-direct-final", "unnecessary_rerun_despite_success_receipt"),
        ("retry_queue-215957210-0-structured", "wrong_state_already_in_parent_memory"),
    )
    by_id = {r["identity"]: r for r in inputs}
    result = []
    for identity, kind in selected:
        row = by_id[identity]
        actor = deepcopy(row["request"])
        old_memory = actor["observation"]["memory"]
        if row["study"] == "cross_record":
            family = next(f for f, rule in guard.PUBLIC_RULES.items() if actor["instruction"].endswith(rule))
            retained = guard.cross_rows(old_memory, family)
            chosen = [r for r in retained if r.get(guard.OWNERS[family]) == actor["observation"]["target"]]
            if len(chosen) != 1:
                raise ValueError("Witness target not unique")
            fields = list(guard.FIELDS[family])
            actor["observation"]["memory"] = json.dumps({"f": fields, "r": [[chosen[0][p] for p in fields]]}, separators=(",", ":"))
        before, after = guard.check(row["request"], row["response"]), guard.check(actor, row["response"])
        if before != after:
            raise ValueError("Reduction changed the diagnostic")
        result.append({"identity": identity, "kind": kind, "source_study": row["study"],
                       "origin": "post_hoc_reduction_of_inspected_historical_evidence",
                       "original_memory_sha256": hashlib.sha256(old_memory.encode()).hexdigest(),
                       "original_memory_bytes": len(old_memory.encode()),
                       "reduced_memory_bytes": len(actor["observation"]["memory"].encode()),
                       "actor_request": actor, "proposal": row["response"], "guard": after,
                       "evaluator_only_expected": row["expected"]})
    return {"version": "evidence_use_witnesses_v1", "limits": "These are reductions, not new task samples or unseen cases. Public instructions/state remain present and are not omitted from accounting.", "witnesses": result}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--benchmark-repeats", type=int, default=50)
    args = parser.parse_args()
    if args.benchmark_repeats < 1:
        parser.error("benchmark repetitions must be positive")
    result = analyze()
    OUTPUT.mkdir(parents=True, exist_ok=True)
    (OUTPUT / "analysis.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8", newline="\n")
    (OUTPUT / "report.md").write_text(report(result), encoding="utf-8", newline="\n")
    inputs, _ = observations()
    (OUTPUT / "witnesses.json").write_text(json.dumps(witnesses(inputs), indent=2) + "\n", encoding="utf-8", newline="\n")
    measurement = benchmark(inputs, args.benchmark_repeats)
    measurement["analysis_sha256"] = hashlib.sha256((OUTPUT / "analysis.json").read_bytes()).hexdigest()
    (OUTPUT / "measurement.json").write_text(json.dumps(measurement, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps(result["summary"], indent=2))


if __name__ == "__main__":
    main()
