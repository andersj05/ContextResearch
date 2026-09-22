"""Reconcile saved calls, exact terminal scores, and matched full-method costs."""
from __future__ import annotations

from decimal import Decimal
from hashlib import sha256
import json
from pathlib import Path

from .casebook import EVAL, grade, truth
from .run import (ARMS, ROOT, execution_request, fingerprints, fixture_paths,
                  memory_request)
from luna6_revision.protocol import request_bytes
from luna6_revision.transport import usage_cost

CPU_PRICE = Decimal("0.0001")
BYTE_PRICE = Decimal("0.00000001")


def load(path):
    return json.loads(path.read_text(encoding="utf-8"))


def analyze(directory):
    completion, manifest = (load(directory / name) for name in ("completion.json", "manifest.json"))
    if completion.get("status") != "complete" or completion.get("calls") != 126:
        raise ValueError("Incomplete fixed schedule")
    if manifest.get("fingerprints") != fingerprints() or manifest.get("scheduled_calls") != 126:
        raise ValueError("Frozen study source drift")
    calls = {path.stem: load(path) for path in (directory / "calls").glob("*.json")}
    if len(calls) != 126:
        raise ValueError("Actual model-call count differs")
    observed = Decimal(0)
    usage = {key: 0 for key in ("inputTokens", "cachedInputTokens", "outputTokens", "reasoningOutputTokens")}
    for identity, call in calls.items():
        if (call.get("identity") != identity or call.get("status") != "completed" or
                call.get("tool_items") != 0 or call.get("usage_events") != 1 or
                call.get("model") != "gpt-6-luna" or call.get("effort") != "medium"):
            raise ValueError("Invalid model-call contract: " + identity)
        if sha256(request_bytes(call["request"])).hexdigest() != call["request_sha256"]:
            raise ValueError("Saved public request hash differs")
        cost = usage_cost(call["usage"])
        if cost != Decimal(call["planning_credits"]):
            raise ValueError("Saved model cost differs")
        observed += cost
        for key in usage:
            usage[key] += call["usage"][key]
    if observed != Decimal(completion["planning_credits"]):
        raise ValueError("Actual model credits do not reconcile")

    totals = {arm: {"decisions": 0, "failures": 0, "model_calls": 0,
                    "model_credits": Decimal(0), "cpu_ns": 0, "local_bytes_read": 0,
                    "input_tokens": 0, "cached_input_tokens": 0, "output_tokens": 0}
              for arm in ARMS}
    families = {family: {arm: {"decisions": 0, "failures": 0} for arm in ARMS} for family in EVAL}
    verdicts = {"proposed_parent_pass": 0, "proposed_child_pass": 0, "parent_fallbacks": 0,
                "child_fallbacks": 0, "automatic_infeasible": 0, "direct_infeasible": 0,
                "checked_infeasible": 0, "prompt_parent_clipped": 0, "prompt_child_clipped": 0,
                "checked_child_clipped": 0}
    detail = []
    seen = set()

    def charge(arm, identity):
        call = calls[identity]
        row = totals[arm]
        row["model_calls"] += 1
        row["model_credits"] += Decimal(call["planning_credits"])
        row["input_tokens"] += call["usage"]["inputTokens"]
        row["cached_input_tokens"] += call["usage"]["cachedInputTokens"]
        row["output_tokens"] += call["usage"]["outputTokens"]

    for path in fixture_paths():
        case = load(path)
        cid = case["id"]
        episode = load(directory / (cid + "-episode.json"))
        if episode.get("case_id") != cid or len(episode.get("decisions", [])) != 18:
            raise ValueError("Incomplete episode: " + cid)
        for arm in ARMS:
            totals[arm]["cpu_ns"] += episode["local"][arm]["cpu_ns"]
            totals[arm]["local_bytes_read"] += episode["local"][arm]["bytes_read"]

        parent_id, child_id, checked_id = (cid + suffix for suffix in
                                            ("-prompt-parent", "-prompt-child", "-checked-child"))
        if calls[parent_id]["request"] != memory_request(case, "parent",
                {"tool_schema": case["tool_schema"], "tool_results": case["tool_results"]}, manifest["parent_cap"]):
            raise ValueError("Parent observation contract differs")
        if calls[child_id]["request"] != memory_request(case, "child",
                {"previous_memory": episode["memories"]["prompt"]["parent"],
                 "candidates": case["candidate_ids"]}, manifest["child_cap"]):
            raise ValueError("Strong child observation contract differs")
        if calls[checked_id]["request"] != memory_request(case, "child",
                {"previous_memory": episode["memories"]["checked"]["parent"],
                 "candidates": case["candidate_ids"]}, manifest["child_cap"], checked=True):
            raise ValueError("Checked child observation contract differs")
        charge("prompt", parent_id)
        charge("checked", parent_id)  # Shared actual call, fully charged in both counterfactual arms.
        charge("prompt", child_id)
        charge("checked", checked_id)
        seen.update((parent_id, child_id, checked_id))

        checks = episode["checks"]
        verdicts["proposed_parent_pass"] += int(checks["proposed_parent"]["passed"])
        verdicts["proposed_child_pass"] += int(checks.get("proposed_child", {}).get("passed", False))
        verdicts["parent_fallbacks"] += int(checks["parent_fallback"])
        verdicts["child_fallbacks"] += int(checks["child_fallback"])
        for arm in ("automatic", "direct", "checked"):
            verdicts[arm + "_infeasible"] += int(arm in episode["infeasible"])
        for key, location in (("prompt_parent_clipped", ("prompt", "parent_bounds")),
                              ("prompt_child_clipped", ("prompt", "child_bounds")),
                              ("checked_child_clipped", ("checked", "child_bounds"))):
            verdicts[key] += int(episode["memories"][location[0]][location[1]]["clipped"])

        future_by_id = {item["id"]: item for item in case["futures"]}
        pair_seen = set()
        for item in episode["decisions"]:
            identity, arm = item["identity"], item["arm"]
            if identity in seen or arm not in ARMS or identity not in calls:
                raise ValueError("Duplicate or missing final model call")
            seen.add(identity)
            future = future_by_id[item["future_id"]]
            pair = (future["id"], arm)
            if pair in pair_seen or identity != future["id"] + "-" + arm:
                raise ValueError("Unmatched paired decision")
            pair_seen.add(pair)
            if arm in ("prompt", "checked", "automatic", "direct"):
                retained = episode["memories"][arm]["child"]
            elif arm == "indexed":
                retained = episode["index"][future["target"]]
            else:
                from .casebook import compact
                retained = compact(case["tool_results"])
            if (calls[identity]["request"] != execution_request(case, retained, future) or
                    len(retained.encode()) != item["memory_bytes"]):
                raise ValueError("Final observation contract differs")
            expected = truth(case, future)
            response = calls[identity]["response"]
            success = grade(response, expected)
            charge(arm, identity)
            totals[arm]["decisions"] += 1
            totals[arm]["failures"] += int(not success)
            families[case["family"]][arm]["decisions"] += 1
            families[case["family"]][arm]["failures"] += int(not success)
            detail.append({"identity": identity, "arm": arm, "family": case["family"],
                "correct": success, "expected": expected, "response": response,
                "model_credits": calls[identity]["planning_credits"],
                "memory_bytes": item["memory_bytes"], "recovery_bytes": item["recovery_bytes"]})
        if len(pair_seen) != 18:
            raise ValueError("Missing paired final decisions")
    if seen != set(calls) or any(row["decisions"] != 18 for row in totals.values()):
        raise ValueError("Unassigned call or unequal decision schedule")
    # The hypothetical method sum counts each actual parent call twice.
    shared_parent_cost = sum((Decimal(call["planning_credits"]) for key, call in calls.items()
                              if key.endswith("-prompt-parent")), Decimal(0))
    if sum((row["model_credits"] for row in totals.values()), Decimal(0)) != observed + shared_parent_cost:
        raise ValueError("Shared parent accounting does not reconcile")
    for row in totals.values():
        row["local_credits"] = Decimal(row["cpu_ns"]) / Decimal(10**9) * CPU_PRICE + Decimal(row["local_bytes_read"]) * BYTE_PRICE
        row["total_credits"] = row["model_credits"] + row["local_credits"]
        row["cache_neutral_model_credits"] = (Decimal(row["input_tokens"]) * Decimal("2.5") +
                                               Decimal(row["output_tokens"]) * Decimal("12.5")) / Decimal(10**6)
        for key in ("model_credits", "local_credits", "total_credits", "cache_neutral_model_credits"):
            row[key] = str(row[key])
    automatic, prompt, authored = (totals[name] for name in ("automatic", "prompt", "direct"))
    criteria = {"fewer_failures_than_prompt": automatic["failures"] < prompt["failures"],
                "equal_or_lower_total_cost": Decimal(automatic["total_credits"]) <= Decimal(prompt["total_credits"]),
                "no_more_failures_than_direct": automatic["failures"] <= authored["failures"]}
    criteria["primary_success"] = all(criteria.values())
    allowance = Decimal(prompt["total_credits"])
    for row in totals.values():
        row["eligible_at_prompt_cost"] = Decimal(row["total_credits"]) <= allowance
    return {"version": "schema_transfer_analysis_v1", "cases": 6, "paired_terminal_cases": 18,
        "actual_model_calls": len(calls), "actual_model_planning_credits": str(observed),
        "shared_parent_credits_counted_in_both_methods": str(shared_parent_cost),
        "usage": usage, "arms": totals, "families": families, "checks": verdicts,
        "criteria": criteria, "common_allowance_prompt_total_credits": str(allowance),
        "price_assumptions": {"cpu_credit_per_second": str(CPU_PRICE),
                              "local_read_credit_per_byte": str(BYTE_PRICE)}, "decisions": detail}


def main():
    directory = ROOT / "experiments/dependency_memory/results/schema_transfer_2026-09-22"
    result = analyze(directory)
    (directory / "analysis.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    lines = ["# Prospective transfer to unseen workflow schemas", "",
        "Six constructed evaluation traces, 18 paired terminal decisions. The casebook and protocol were frozen before implementation and model calls.", "",
        "| Method | Failures / 18 | Calls charged | Model credits | Local credits | Total experimental credits | Eligible at prompt cost |",
        "|---|---:|---:|---:|---:|---:|:---:|"]
    for arm in ARMS:
        row = result["arms"][arm]
        lines.append(f"| {arm} | {row['failures']} | {row['model_calls']} | {row['model_credits']} | {row['local_credits']} | {row['total_credits']} | {'yes' if row['eligible_at_prompt_cost'] else 'no'} |")
    lines += ["", "**Prespecified primary success:** " + ("met" if result["criteria"]["primary_success"] else "not met") + ".", "",
        "| Family | " + " | ".join(ARMS) + " |", "|---|" + "---:|" * len(ARMS)]
    for family in EVAL:
        lines.append("| " + family + " | " + " | ".join(str(result["families"][family][arm]["failures"]) + "/6" for arm in ARMS) + " |")
    lines += ["", "## Scope and accounting", "",
        f"Actual calls: {result['actual_model_calls']}; token-derived planning credits: {result['actual_model_planning_credits']}. "
        "The shared parent writer is one actual call per trace and is fully charged to both hypothetical prompt methods.",
        "Local CPU and read-byte conversion rates are synthetic. Human authoring of the direct baseline and provider infrastructure are unmeasured. "
        "Actual subscription debit is not attributable to this experiment. These are constructed traces, not production incidents.", "",
        "## Check verdicts", "", "```json", json.dumps(result["checks"], indent=2), "```", ""]
    (directory / "report.md").write_text("\n".join(lines), encoding="utf-8")
    print(json.dumps({key: value for key, value in result.items() if key != "decisions"}, indent=2))


if __name__ == "__main__":
    main()
