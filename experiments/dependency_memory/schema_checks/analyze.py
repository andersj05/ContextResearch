"""Independent saved-evidence reconciliation and matched-cost report."""
from __future__ import annotations

from collections import defaultdict
from decimal import Decimal
from hashlib import sha256
import json
from pathlib import Path

from .cases import grade, truth
from .run import ARMS, ROOT, fixture_paths, fingerprints
from luna6_revision.protocol import request_bytes
from luna6_revision.transport import usage_cost

CPU_PRICE = Decimal("0.0001")
BYTE_PRICE = Decimal("0.00000001")


def load(path):
    return json.loads(path.read_text(encoding="utf-8"))


def analyze(directory):
    completion = load(directory / "completion.json")
    manifest = load(directory / "manifest.json")
    if completion != {"status": "complete", "calls": 72,
                      "planning_credits": completion.get("planning_credits")}:
        raise ValueError("Incomplete schedule")
    if manifest["fingerprints"] != fingerprints() or manifest["scheduled_calls"] != 72:
        raise ValueError("Frozen source drift")
    calls = {path.stem: load(path) for path in (directory / "calls").glob("*.json")}
    if len(calls) != 72:
        raise ValueError("Call count differs")
    observed_credits = Decimal(0)
    usage = {key: 0 for key in ("inputTokens", "cachedInputTokens", "outputTokens", "reasoningOutputTokens")}
    for identity, call in calls.items():
        if (call["identity"] != identity or call["status"] != "completed" or call["tool_items"] != 0 or
                call["usage_events"] != 1 or call["model"] != "gpt-6-luna" or call["effort"] != "medium"):
            raise ValueError("Invalid call contract: " + identity)
        if sha256(request_bytes(call["request"])).hexdigest() != call["request_sha256"]:
            raise ValueError("Public request hash differs")
        price = usage_cost(call["usage"])
        if price != Decimal(call["planning_credits"]):
            raise ValueError("Call cost differs")
        observed_credits += price
        for key in usage:
            usage[key] += call["usage"][key]
    if observed_credits != Decimal(completion["planning_credits"]):
        raise ValueError("Total model cost differs")

    arm_rows = {arm: {"decisions": 0, "failures": 0, "model_credits": Decimal(0),
                      "cpu_ns": 0, "local_bytes_read": 0, "model_calls": 0,
                      "input_tokens": 0, "cached_input_tokens": 0, "output_tokens": 0}
                for arm in ARMS}
    by_family = {family: {arm: {"decisions": 0, "failures": 0} for arm in ARMS}
                 for family in ("retry", "ci_handoff", "data_job")}
    decision_rows = []
    seen_calls = set()
    for path in fixture_paths():
        case = load(path)
        episode = load(directory / (case["id"] + "-episode.json"))
        if episode["case_id"] != case["id"] or len(episode["decisions"]) != 10:
            raise ValueError("Episode incomplete")
        for identity in (case["id"] + "-prompt-parent", case["id"] + "-prompt-child"):
            call = calls[identity]
            if call["request"]["stage"] not in {"parent", "child"}:
                raise ValueError("Memory call stage differs")
            seen_calls.add(identity)
            row = arm_rows["prompt"]
            row["model_credits"] += Decimal(call["planning_credits"])
            row["model_calls"] += 1
            row["input_tokens"] += call["usage"]["inputTokens"]
            row["cached_input_tokens"] += call["usage"]["cachedInputTokens"]
            row["output_tokens"] += call["usage"]["outputTokens"]
        for arm in ("automatic", "direct"):
            row = arm_rows[arm]
            row["cpu_ns"] += episode["local"][arm]["cpu_ns"]
            row["local_bytes_read"] += episode["local"][arm]["bytes_read"]
        if not all(episode["local"]["automatic"][name]["passed"] for name in ("parent_check", "child_check")):
            raise ValueError("Saved automatic check did not pass")
        futures = {future["id"]: future for future in case["futures"]}
        for item in episode["decisions"]:
            identity, arm = item["identity"], item["arm"]
            if identity not in calls or identity in seen_calls or arm not in ARMS:
                raise ValueError("Duplicate or missing terminal call")
            seen_calls.add(identity)
            future = futures[item["future_id"]]
            expected = truth(case, future)
            call = calls[identity]
            if call["request"]["stage"] != "execute" or call["request"]["observation"]["target"] != future["target"]:
                raise ValueError("Terminal request differs")
            correct = grade(call["response"], expected)
            row = arm_rows[arm]
            row["decisions"] += 1
            row["failures"] += int(not correct)
            row["model_credits"] += Decimal(call["planning_credits"])
            row["model_calls"] += 1
            row["input_tokens"] += call["usage"]["inputTokens"]
            row["cached_input_tokens"] += call["usage"]["cachedInputTokens"]
            row["output_tokens"] += call["usage"]["outputTokens"]
            row["cpu_ns"] += item["recovery_cpu_ns"]
            row["local_bytes_read"] += item["recovery_bytes"]
            by_family[case["family"]][arm]["decisions"] += 1
            by_family[case["family"]][arm]["failures"] += int(not correct)
            decision_rows.append({"identity": identity, "family": case["family"], "arm": arm,
                "correct": correct, "expected": expected, "response": call["response"],
                "model_credits": call["planning_credits"], "memory_bytes": item["memory_bytes"],
                "recovery_bytes": item["recovery_bytes"]})
    if seen_calls != set(calls):
        raise ValueError("Unassigned model calls")
    if any(row["decisions"] != 12 for row in arm_rows.values()):
        raise ValueError("Unmatched decision schedule")
    if sum(row["model_credits"] for row in arm_rows.values()) != observed_credits:
        raise ValueError("Method costs do not reconcile")

    for row in arm_rows.values():
        row["local_credits"] = Decimal(row["cpu_ns"]) / Decimal(10**9) * CPU_PRICE + Decimal(row["local_bytes_read"]) * BYTE_PRICE
        row["total_credits"] = row["model_credits"] + row["local_credits"]
        for key in ("model_credits", "local_credits", "total_credits"):
            row[key] = str(row[key])
    auto, prompt, direct_row = (arm_rows[x] for x in ("automatic", "prompt", "direct"))
    fewer_failures = auto["failures"] < prompt["failures"]
    lower_cost = Decimal(auto["total_credits"]) <= Decimal(prompt["total_credits"])
    matches_direct = auto["failures"] <= direct_row["failures"]
    model_saving = Decimal(prompt["model_credits"]) - Decimal(auto["model_credits"])
    auto_seconds = Decimal(auto["cpu_ns"]) / Decimal(10**9)
    break_even_cpu_price = (model_saving - Decimal(auto["local_bytes_read"]) * BYTE_PRICE) / auto_seconds if auto_seconds else None
    return {"version": "schema_checks_analysis_v1", "source_commit": "284405d",
        "cases": 6, "paired_terminal_decisions": 12, "model_calls": len(calls),
        "actual_model_planning_credits": str(observed_credits), "usage": usage,
        "arm_totals": arm_rows, "by_family": by_family, "decisions": decision_rows,
        "criteria": {"fewer_failures_than_prompt": fewer_failures, "total_cost_no_higher_than_prompt": lower_cost,
                     "no_more_failures_than_direct": matches_direct,
                     "primary_success": fewer_failures and lower_cost,
                     "matches_direct_and_primary_success": fewer_failures and lower_cost and matches_direct},
        "cpu_price_break_even_vs_prompt_credits_per_second": str(break_even_cpu_price) if break_even_cpu_price is not None else None,
        "price_assumptions": {"cpu_credit_per_second": str(CPU_PRICE), "local_read_credit_per_byte": str(BYTE_PRICE)}}


def main():
    directory = ROOT / "experiments/dependency_memory/results/schema_checks_2026-09-22"
    result = analyze(directory)
    summary = {key: value for key, value in result.items() if key != "decisions"}
    (directory / "analysis.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    lines = ["# Schema-derived checks on frozen tool-result traces", "",
        "Six constructed evaluation traces across retry, CI handoff, and multi-stage data jobs; 12 paired terminal cases. "
        "This is a finite transfer test, not production evidence.", "",
        "| Method | Failures / 12 | Model calls | Model credits | Local credits | Total experimental credits |",
        "|---|---:|---:|---:|---:|---:|"]
    for arm in ARMS:
        row = result["arm_totals"][arm]
        lines.append(f"| {arm} | {row['failures']} | {row['model_calls']} | {row['model_credits']} | {row['local_credits']} | {row['total_credits']} |")
    lines += ["", "**Prespecified primary success:** " + ("met" if result["criteria"]["primary_success"] else "not met") + ".",
              "**Parity with hand-written direct records:** " + ("met" if result["criteria"]["no_more_failures_than_direct"] else "not met") + ".",
              "", "Local CPU and byte prices are declared experimental conversion rates, not provider charges. "
              "The direct control excludes human schema-authoring cost. The prompt and all final decisions are fully charged. "
              "Stored response/usage records and case hashes support independent replay. No provider session history or evaluator files entered the model calls.",
              "", "## Family outcomes", "", "| Family | " + " | ".join(ARMS) + " |",
              "|---|" + "---:|" * len(ARMS)]
    for family, rows in result["by_family"].items():
        lines.append("| " + family + " | " + " | ".join(str(rows[arm]["failures"]) + "/4" for arm in ARMS) + " |")
    lines += ["", f"Break-even local CPU price versus prompting, with the declared byte price: {result['cpu_price_break_even_vs_prompt_credits_per_second']} credits/second."]
    (directory / "report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
