"""Reconcile the frozen schedule, full method costs, and exact paired outcomes."""
from __future__ import annotations

from decimal import Decimal
from hashlib import sha256
import json
from pathlib import Path

from .run import (ARMS, CALL_SCHEDULE, ROOT, child_request, execution_request,
                  fingerprints, fixture_paths, parent_request)
from luna6_revision.protocol import request_bytes
from luna6_revision.transport import usage_cost
from experiments.dependency_memory.schema_transfer import memory as base
from experiments.dependency_memory.schema_transfer.casebook import TARGET_PATH, terminal
from .casebook import EVAL, compact, grade, truth
from . import memory

CPU_PRICE = Decimal("0.0001")
BYTE_PRICE = Decimal("0.00000001")


def load(path):
    return json.loads(path.read_text(encoding="utf-8"))


def reconstruct_table(data):
    if not isinstance(data, dict) or set(data) != {"f", "r"}:
        raise ValueError("Not a field/row table")
    rows = base.decode(compact(data))
    answer = []
    for flat in rows:
        nested = {}
        for path, value in flat.items():
            cursor = nested
            parts = path.split(".")
            for name in parts[:-1]:
                cursor = cursor.setdefault(name, {})
            cursor[parts[-1]] = value
        answer.append(nested)
    return answer


def information_sufficiency(retained, case, future):
    """Independent deterministic execution when memory has a decodable format."""
    try:
        data = json.loads(retained)
        if isinstance(data, dict):
            rows = reconstruct_table(data)
        elif isinstance(data, list):
            _, rows = memory.join(case["tool_schemas"], data)
        else:
            return "unparsed"
        target_field = TARGET_PATH[case["family"]]
        matched = [row for row in rows if row.get(target_field) == future["target"]]
        if len(matched) != 1:
            return "insufficient"
        return "sufficient" if terminal(case["family"], matched[0], future["event"]) == truth(case, future) else "insufficient"
    except (ValueError, KeyError, TypeError, json.JSONDecodeError):
        return "insufficient" if retained.strip().startswith(("{", "[")) else "unparsed"


def recalled_memory(arm, case, episode, future):
    if arm in ("prompt", "structured", "checked", "automatic", "direct"):
        return episode["memories"][arm]["child"]
    if arm == "indexed_raw":
        return episode["index"][future["target"]]
    if arm == "indexed_projected":
        group = json.loads(episode["index"][future["target"]])
        return memory.project(case["tool_schemas"], group)[0]
    if arm == "full":
        return compact(case["tool_results"])
    raise ValueError("Unknown arm")


def analyze(directory):
    completion, manifest = (load(directory / name) for name in ("completion.json", "manifest.json"))
    if completion.get("status") != "complete" or completion.get("calls") != CALL_SCHEDULE:
        raise ValueError("Incomplete fixed schedule")
    if manifest.get("fingerprints") != fingerprints() or manifest.get("scheduled_calls") != CALL_SCHEDULE:
        raise ValueError("Frozen study source drift")
    paths, fixtures = fixture_paths()
    if manifest.get("implementation_commit") != fixtures["implementation_commit"]:
        raise ValueError("Implementation freeze differs")
    calls = {path.stem: load(path) for path in (directory / "calls").glob("*.json")}
    if len(calls) != CALL_SCHEDULE:
        raise ValueError("Actual model call count differs")
    actual_credits = Decimal(0)
    actual_usage = {key: 0 for key in ("inputTokens", "cachedInputTokens", "outputTokens", "reasoningOutputTokens")}
    for identity, call in calls.items():
        if (call.get("identity") != identity or call.get("status") != "completed" or
                call.get("tool_items") != 0 or call.get("usage_events") != 1 or
                call.get("model") != "gpt-6-luna" or call.get("effort") != "medium"):
            raise ValueError("Invalid call contract: " + identity)
        if sha256(request_bytes(call["request"])).hexdigest() != call["request_sha256"]:
            raise ValueError("Public request hash changed: " + identity)
        price = usage_cost(call["usage"])
        if price != Decimal(call["planning_credits"]):
            raise ValueError("Call price changed")
        actual_credits += price
        for key in actual_usage:
            actual_usage[key] += call["usage"][key]
    if actual_credits != Decimal(completion["planning_credits"]):
        raise ValueError("Actual model usage does not reconcile")

    totals = {arm: {"decisions": 0, "failures": 0, "model_calls": 0,
                    "model_credits": Decimal(0), "cpu_ns": 0, "local_bytes_read": 0,
                    "local_bytes_written": 0, "input_tokens": 0,
                    "cached_input_tokens": 0, "output_tokens": 0,
                    "information": {kind: 0 for kind in ("sufficient", "insufficient", "unparsed")}}
              for arm in ARMS}
    families = {family: {arm: {"decisions": 0, "failures": 0} for arm in ARMS} for family in EVAL}
    event_position = {str(i): {arm: {"decisions": 0, "failures": 0} for arm in ARMS} for i in range(3)}
    verdicts = {name: 0 for name in ("structured_parent_pass", "checked_child_proposal_pass",
              "parent_fallbacks", "child_fallbacks", "automatic_infeasible", "direct_infeasible",
              "checked_infeasible", "prompt_parent_clipped", "prompt_child_clipped",
              "structured_parent_clipped", "structured_child_clipped", "checked_child_clipped")}
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

    for path in paths:
        case = load(path)
        cid = case["id"]
        episode = load(directory / (cid + "-episode.json"))
        if episode.get("case_id") != cid or len(episode.get("decisions", [])) != 24:
            raise ValueError("Incomplete episode: " + cid)
        for arm in ARMS:
            local = episode["local"][arm]
            totals[arm]["cpu_ns"] += local["cpu_ns"]
            totals[arm]["local_bytes_read"] += local["bytes_read"]
            totals[arm]["local_bytes_written"] += local["bytes_written"]
        for arm in ("prompt", "structured"):
            identity = cid + "-" + arm + "-parent"
            if calls[identity]["request"] != parent_request(case, arm):
                raise ValueError("Parent request differs")
            charge(arm, identity)
            if arm == "structured":
                charge("checked", identity)
            seen.add(identity)
        for arm in ("prompt", "structured", "checked"):
            identity = cid + "-" + arm + "-child"
            if calls[identity]["request"] != child_request(case, arm, episode["memories"][arm]["parent"]):
                raise ValueError("Child request differs")
            charge(arm, identity)
            seen.add(identity)

        checks = episode["checks"]
        verdicts["structured_parent_pass"] += int(checks["structured_parent"]["passed"])
        verdicts["checked_child_proposal_pass"] += int(checks.get("checked_child_proposal", {}).get("passed", False))
        verdicts["parent_fallbacks"] += int(checks["parent_fallback"])
        verdicts["child_fallbacks"] += int(checks.get("child_fallback", False))
        for arm in ("automatic", "direct", "checked"):
            verdicts[arm + "_infeasible"] += int(arm in episode["infeasible"])
        for arm in ("prompt", "structured"):
            for stage in ("parent", "child"):
                verdicts[arm + "_" + stage + "_clipped"] += int(episode["memories"][arm][stage + "_bounds"]["clipped"])
        verdicts["checked_child_clipped"] += int(episode["memories"]["checked"]["child_bounds"]["clipped"])

        future_by_id = {item["id"]: item for item in case["futures"]}
        pair_seen = set()
        for item in episode["decisions"]:
            identity, arm = item["identity"], item["arm"]
            if identity in seen or arm not in ARMS or identity not in calls:
                raise ValueError("Duplicate or missing final call")
            seen.add(identity)
            future = future_by_id[item["future_id"]]
            pair = (future["id"], arm)
            if pair in pair_seen or identity != future["id"] + "-" + arm:
                raise ValueError("Unmatched paired decision")
            pair_seen.add(pair)
            retained = recalled_memory(arm, case, episode, future)
            if (calls[identity]["request"] != execution_request(case, retained, future) or
                    len(retained.encode()) != item["memory_bytes"] or item["truth"] != truth(case, future)):
                raise ValueError("Final observation or truth contract differs")
            expected = truth(case, future)
            response = calls[identity]["response"]
            success = grade(response, expected)
            charge(arm, identity)
            totals[arm]["decisions"] += 1
            totals[arm]["failures"] += int(not success)
            info = information_sufficiency(retained, case, future)
            totals[arm]["information"][info] += 1
            families[case["family"]][arm]["decisions"] += 1
            families[case["family"]][arm]["failures"] += int(not success)
            position = future["id"].rsplit("-", 1)[-1]
            event_position[position][arm]["decisions"] += 1
            event_position[position][arm]["failures"] += int(not success)
            detail.append({"identity": identity, "arm": arm, "family": case["family"],
                "event_position": position, "correct": success, "expected": expected,
                "response": response, "information": info,
                "model_credits": calls[identity]["planning_credits"],
                "memory_bytes": item["memory_bytes"]})
        if len(pair_seen) != 24:
            raise ValueError("Missing paired final decisions")
    if seen != set(calls) or any(row["decisions"] != 36 for row in totals.values()):
        raise ValueError("Unassigned call or unequal paired schedule")
    shared_parent_cost = sum((Decimal(call["planning_credits"]) for key, call in calls.items()
                              if key.endswith("-structured-parent")), Decimal(0))
    if sum((row["model_credits"] for row in totals.values()), Decimal(0)) != actual_credits + shared_parent_cost:
        raise ValueError("Shared parent accounting does not reconcile")
    for row in totals.values():
        row["local_credits"] = (Decimal(row["cpu_ns"]) / Decimal(10**9) * CPU_PRICE +
                                Decimal(row["local_bytes_read"] + row["local_bytes_written"]) * BYTE_PRICE)
        row["total_credits"] = row["model_credits"] + row["local_credits"]
        row["cache_neutral_model_credits"] = (Decimal(row["input_tokens"]) * Decimal("2.5") +
                                               Decimal(row["output_tokens"]) * Decimal("12.5")) / Decimal(10**6)
        for key in ("model_credits", "local_credits", "total_credits", "cache_neutral_model_credits"):
            row[key] = str(row[key])
    automatic, prompt, structured, authored, recovered = (
        totals[name] for name in ("automatic", "prompt", "structured", "direct", "indexed_projected"))
    auto_cost, index_cost = Decimal(automatic["total_credits"]), Decimal(recovered["total_credits"])
    nondominated = not (recovered["failures"] <= automatic["failures"] and index_cost <= auto_cost)
    criteria = {"fewer_failures_than_prompt": automatic["failures"] < prompt["failures"],
                "fewer_failures_than_structured": automatic["failures"] < structured["failures"],
                "equal_or_lower_cost_than_prompt": auto_cost <= Decimal(prompt["total_credits"]),
                "equal_or_lower_cost_than_structured": auto_cost <= Decimal(structured["total_credits"]),
                "no_more_failures_than_direct": automatic["failures"] <= authored["failures"],
                "nondominated_by_indexed_projected": nondominated}
    criteria["primary_success"] = all(criteria.values())
    allowance = min(Decimal(prompt["total_credits"]), Decimal(structured["total_credits"]))
    for row in totals.values():
        row["eligible_at_prompted_allowance"] = Decimal(row["total_credits"]) <= allowance
    return {"version": "cross_record_analysis_v1", "cases": 12, "paired_terminal_cases": 36,
        "actual_model_calls": len(calls), "actual_model_planning_credits": str(actual_credits),
        "shared_parent_credits_counted_twice": str(shared_parent_cost), "usage": actual_usage,
        "arms": totals, "families": families, "event_position": event_position,
        "checks": verdicts, "criteria": criteria,
        "common_allowance_prompted_total_credits": str(allowance),
        "price_assumptions": {"cpu_credit_per_second": str(CPU_PRICE),
                              "local_read_or_write_credit_per_byte": str(BYTE_PRICE)},
        "decisions": detail}


def main():
    directory = ROOT / "experiments/dependency_memory/results/cross_record_2026-09-22"
    result = analyze(directory)
    (directory / "analysis.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    lines = ["# Prospective cross-record recovery comparison", "",
        "Twelve constructed evaluation traces and 36 paired terminal decisions. The domain grammars were visible before this study; exact seeds were derived after the implementation freeze.", "",
        "| Method | Failures / 36 | Calls charged | Model credits | Local credits | Total experimental credits | Eligible at prompted allowance |",
        "|---|---:|---:|---:|---:|---:|:---:|"]
    for arm in ARMS:
        row = result["arms"][arm]
        lines.append(f"| {arm} | {row['failures']} | {row['model_calls']} | {row['model_credits']} | {row['local_credits']} | {row['total_credits']} | {'yes' if row['eligible_at_prompted_allowance'] else 'no'} |")
    lines += ["", "**Prespecified primary success:** " + ("met" if result["criteria"]["primary_success"] else "not met") + ".", "",
        "| Family | " + " | ".join(ARMS) + " |", "|---|" + "---:|" * len(ARMS)]
    for family in EVAL:
        lines.append("| " + family + " | " + " | ".join(str(result["families"][family][arm]["failures"]) + "/12" for arm in ARMS) + " |")
    lines += ["", "## Scope and accounting", "",
        f"Actual calls: {result['actual_model_calls']}; token-derived planning credits: {result['actual_model_planning_credits']}. "
        "The structured parent writer is one physical call per trace and fully charged to both hypothetical structured and checked methods. "
        "Local CPU/read/write conversion rates are synthetic. Human authoring, provider infrastructure, and actual subscription debit are unmeasured.",
        "This uses constructed traces with previously visible domain grammars; it is not external held-out validation.", "",
        "## Check verdicts", "", "```json", json.dumps(result["checks"], indent=2), "```", ""]
    (directory / "report.md").write_text("\n".join(lines), encoding="utf-8")
    print(json.dumps({key: value for key, value in result.items() if key != "decisions"}, indent=2))


if __name__ == "__main__":
    main()
