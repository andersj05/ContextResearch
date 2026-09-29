"""Audit the suffix and report missing outcomes without filling the original gap."""
import argparse
from decimal import Decimal
import json
from pathlib import Path

from .run import ORIGINAL, OUTPUT, GAP, original, study, verify, verify_record, read
from experiments.dependency_memory.workflow_executed.transport import save, usage_cost, RESERVATION
from experiments.dependency_memory.workflow_eval.grader import grade, expected_answer, strict_json


def analyze(directory, original_directory=ORIGINAL):
    plan, old, known_old = verify(directory, original_directory)
    completion = read(directory / "completion.json")
    if completion["status"] != "complete_suffix_with_original_gap":
        return {"status": "stopped", "scheduled_total": 108, "original_primary_criterion": "unassessable", "completion": completion}
    new = {p.stem: read(p) for p in (directory / "calls").glob("*.json")}
    if set(old) & set(new) or set(new) != set(plan["pending"]) or completion["new_calls"] != 91:
        raise ValueError("Missing, repeated or extra dispatched identity")
    calls = old | new
    seen = []
    class Replay:
        def complete(self, identity, request):
            seen.append(identity)
            return verify_record(calls[identity], identity, request, allow_gap=True)
    episodes = original.execute(Replay())
    if seen != plan["schedule"]:
        raise ValueError("Combined request order differs")
    for episode in episodes:
        saved = read(directory / (episode["id"] + "-episode.json"))
        for key in ("id", "origin", "memories", "call_ids", "finals"):
            if saved[key] != episode[key]:
                raise ValueError("Reconstructed memory differs")
        old_episode = original_directory / (episode["id"] + "-episode.json")
        if old_episode.is_file():
            old_saved = read(old_episode)
            for key in ("id", "origin", "memories", "call_ids", "finals"):
                if old_saved[key] != episode[key]:
                    raise ValueError("Original completed episode differs")
    known_new = sum((usage_cost(c["usage"]) for c in new.values()), Decimal(0))
    known = known_old + known_new
    if (known_new != Decimal(completion["new_known_credits"]) or known != Decimal(completion["combined_known_credits"])
            or known + RESERVATION > Decimal("20")):
        raise ValueError("Combined budget mismatch")
    complete_cases = [c["id"] for c in study.cases() if all(calls[c["id"] + "-" + a + "-final"]["status"] == "completed" for a in study.ARMS)]
    arms = {a: {"scheduled_cases": 12, "observed_successes": 0, "missing": 0, "false_ready": 0,
        "malformed": 0, "complete_pair_successes": 0, "complete_pair_cases": len(complete_cases),
        "known_credits": Decimal(0), "cache_neutral_known_credits": Decimal(0),
        "complete_pair_credits": Decimal(0), "complete_pair_cache_neutral_credits": Decimal(0),
        "input_tokens": 0, "cached_input_tokens": 0, "output_tokens": 0, "reasoning_tokens": 0,
        "metered_calls": 0, "unknown_usage_calls": 0, "fallbacks": 0, "infeasible_memories": 0,
        "outcomes": [], "sufficiency": []} for a in study.ARMS}
    for case, episode in zip(study.cases(), episodes):
        for arm in study.ARMS:
            row = arms[arm]
            for identity in episode["call_ids"][arm]:
                record = calls[identity]
                if record["status"] != "completed":
                    row["unknown_usage_calls"] += 1
                    continue
                usage = record["usage"]
                cost = usage_cost(usage)
                neutral = (Decimal(usage["inputTokens"]) * Decimal("2.5") + Decimal(usage["outputTokens"]) * Decimal("12.5")) / 1000000
                row["metered_calls"] += 1
                row["known_credits"] += cost
                row["cache_neutral_known_credits"] += neutral
                if case["id"] in complete_cases:
                    row["complete_pair_credits"] += cost
                    row["complete_pair_cache_neutral_credits"] += neutral
                for dest, source in (("input_tokens", "inputTokens"), ("cached_input_tokens", "cachedInputTokens"), ("output_tokens", "outputTokens"), ("reasoning_tokens", "reasoningOutputTokens")):
                    row[dest] += usage[source]
            final = calls[case["id"] + "-" + arm + "-final"]
            if final["status"] != "completed":
                row["missing"] += 1
                row["outcomes"].append({"case": case["id"], "status": "missing_transport", "exact": None})
            else:
                normalized = study.normalize_response(final["response"])
                verdict = grade(case["initial"] + case["between"], case["task"], json.dumps(normalized))
                row["observed_successes"] += int(verdict["exact"])
                row["false_ready"] += int(verdict["false_ready"] is True)
                row["malformed"] += int(verdict["malformed"])
                if case["id"] in complete_cases:
                    row["complete_pair_successes"] += int(verdict["exact"])
                row["outcomes"].append({"case": case["id"], "status": "observed", "response": normalized, **verdict})
            for stage in ("parent", "child"):
                audit = episode["memories"].get(arm + "_" + stage, {}).get("audit", {})
                row["fallbacks"] += int(audit.get("fallback", False))
                row["infeasible_memories"] += int(audit.get("infeasible", False))
            try:
                memory = strict_json(final["request"]["observation"]["memory"])
                sufficient = expected_answer(memory, case["task"]) == expected_answer(case["initial"] + case["between"], case["task"])
            except (ValueError, TypeError, KeyError):
                sufficient = None
            row["sufficiency"].append({"case": case["id"], "deterministic_receipt_sufficiency": sufficient})
    for row in arms.values():
        reserve = row["unknown_usage_calls"] * RESERVATION
        row["reserved_upper_credits"] = row["known_credits"] + reserve
        row["cache_neutral_reserved_upper_credits"] = row["cache_neutral_known_credits"] + reserve
        row["success_count_lower"] = row["observed_successes"]
        row["success_count_upper"] = row["observed_successes"] + row["missing"]
        for key, value in row.items():
            if isinstance(value, Decimal):
                row[key] = str(value)
    narrow = [c for c in study.cases() if len(c["task"]["required_checks"]) < len(study.CHECKS)]
    retrieval = {"cases": len(narrow)}
    for arm in ("indexed", "full"):
        retrieval[arm + "_input_tokens"] = sum(calls[c["id"] + "-" + arm + "-final"]["usage"]["inputTokens"] for c in narrow)
        retrieval[arm + "_successes"] = sum(o["exact"] for o in arms[arm]["outcomes"] if o["case"] in {c["id"] for c in narrow})
    return {"status": "analyzed_post_stop_extension", "total_dispatches": len(calls), "metered_answers": len(calls)-1,
        "permanent_gap": GAP, "original_primary_criterion": "unassessable", "complete_pair_cases": complete_cases,
        "known_planning_credits": str(known), "unknown_reservation_credits": str(RESERVATION),
        "reserved_upper_credits": str(known + RESERVATION), "arms": arms, "selective_retrieval": retrieval,
        "resource_limit": "Partial original episode CPU/byte counters unavailable; continuation local events include replay. No complete infrastructure cost.",
        "evidence_status": "Twelve authored scenarios in one fixture family; real subprocess outputs; exploratory post-stop extension."}


def report(result):
    lines = ["# Executed workflow continuation: descriptive comparison", "", "September 29, 2026.", ""]
    if result["status"] != "analyzed_post_stop_extension":
        return "\n".join(lines + ["Extension stopped; comparison unavailable.", json.dumps(result, indent=2)])
    lines += [f"{result['total_dispatches']} total dispatches; {result['metered_answers']} metered answers; one permanent original transport gap.",
              "The original 12-case criterion is unassessable. Counts below retain /12 with missing outcomes explicit.", "",
              "| Method | Observed correct /12 | Missing | Correct on 11 complete pairs | Known credits | Reserved upper credits |",
              "|---|---:|---:|---:|---:|---:|"]
    for arm, row in result["arms"].items():
        lines.append(f"| {arm} | {row['observed_successes']}/12 | {row['missing']} | {row['complete_pair_successes']}/11 | {row['known_credits']} | {row['reserved_upper_credits']} |")
    lines += ["", f"Total known model cost: {result['known_planning_credits']} planning credits; reserved upper: {result['reserved_upper_credits']}. Actual account debit is unknown.", "",
              "All writers count. Compare fully metered complete-pair and cache-neutral costs in analysis.json. Local costs are incomplete for the interrupted episode; no fully priced cost claim.", "",
              "These are twelve scripted scenarios in one fixture family, with actual command outputs. The untouched real-world study remains pending.", ""]
    return "\n".join(lines)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("directory", type=Path, nargs="?", default=OUTPUT)
    args = parser.parse_args()
    result = analyze(args.directory)
    save(args.directory / "analysis.json", result)
    (args.directory / "report.md").write_text(report(result), encoding="utf-8", newline="\n")
    print(report(result))
