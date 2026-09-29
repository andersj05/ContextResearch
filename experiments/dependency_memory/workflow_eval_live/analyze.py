"""Rebuild all public requests from saved responses before comparing methods."""
import argparse
from decimal import Decimal
import hashlib
import json
from pathlib import Path

from .run import execute, fingerprints
from . import study
from .protocol import request_bytes
from .transport import save, usage_cost
from experiments.dependency_memory.workflow_eval.grader import expected_answer, grade, strict_json, wire


def read(path):
    return strict_json(path.read_text(encoding="utf-8"))


def analyze(directory):
    manifest = read(directory / "manifest.json")
    completion = read(directory / "completion.json")
    if completion["status"] != "complete":
        return {"status": "incomplete", "scheduled_calls": 36, "completion": completion,
                "primary_criterion": "unassessed", "reason": "No complete paired comparison; preserve missing outcomes"}
    if manifest["fingerprints"] != fingerprints() or manifest["schedule"] != study.schedule():
        raise ValueError("Frozen source/schedule mismatch")
    if manifest["cases_sha256"] != hashlib.sha256(wire(study.cases())).hexdigest():
        raise ValueError("Frozen condition mismatch")
    if manifest["preflight_sha256"] != hashlib.sha256((directory / "preflight.json").read_bytes()).hexdigest():
        raise ValueError("Preflight evidence changed")
    calls = {p.stem: read(p) for p in (directory / "calls").glob("*.json")}
    if set(calls) != set(manifest["schedule"]) or completion["calls"] != 36:
        raise ValueError("Missing, extra or duplicate calls")
    seen = []
    class Replay:
        def complete(self, identity, request):
            record = calls[identity]
            seen.append(identity)
            if (record["identity"] != identity or record["status"] != "completed"
                    or record["dispatched"] is not True or record["model"] != "gpt-6-luna"
                    or record["effort"] != "medium" or record["request"] != request
                    or record["request_sha256"] != hashlib.sha256(request_bytes(request)).hexdigest()
                    or record["usage_events"] != 1 or record["tool_items"] != 0
                    or record["harness_termination"] != "sessionBudgetExceeded"):
                raise ValueError("Call evidence mismatch: " + identity)
            try:
                decoded = strict_json(record["raw_answer"])
            except ValueError:
                decoded = None
            if decoded != record["response"] or Decimal(record["planning_credits"]) != usage_cost(record["usage"]):
                raise ValueError("Answer or usage mismatch: " + identity)
            return decoded
    regenerated = execute(Replay())
    if seen != manifest["schedule"]:
        raise ValueError("Observed request order differs")
    arms = {a: {"successes": 0, "cases": 4, "false_ready": 0, "malformed": 0,
        "model_calls": 0, "model_credits": Decimal(0), "cache_neutral_model_credits": Decimal(0),
        "input_tokens": 0, "cached_input_tokens": 0, "output_tokens": 0, "reasoning_tokens": 0,
        "model_wall_seconds": 0.0, "local_cpu_ns": 0, "local_wall_ns": 0,
        "local_read_bytes": 0, "local_write_bytes": 0, "fallbacks": 0,
        "sufficiency": [], "outcomes": []} for a in study.ARMS}
    for case, fresh in zip(study.cases(), regenerated):
        saved = read(directory / (case["id"] + "-episode.json"))
        for key in ("id", "origin", "memories", "call_ids", "finals"):
            if saved[key] != fresh[key]:
                raise ValueError("Episode replay mismatch: " + key)
        for arm in study.ARMS:
            row = arms[arm]
            actual_events, expected_events = saved["local_events"][arm], fresh["local_events"][arm]
            fields = ("name", "read_bytes", "write_bytes")
            if [{k: x[k] for k in fields} for x in actual_events] != [{k: x[k] for k in fields} for x in expected_events]:
                raise ValueError("Local byte accounting mismatch")
            for event in actual_events:
                if any(type(event[k]) is not int or event[k] < 0 for k in ("cpu_ns", "wall_ns", "read_bytes", "write_bytes")):
                    raise ValueError("Invalid local resource measure")
                for dest, src in (("local_cpu_ns", "cpu_ns"), ("local_wall_ns", "wall_ns"),
                                  ("local_read_bytes", "read_bytes"), ("local_write_bytes", "write_bytes")):
                    row[dest] += event[src]
            for identity in saved["call_ids"][arm]:
                call = calls[identity]
                usage = call["usage"]
                row["model_calls"] += 1
                row["model_credits"] += usage_cost(usage)
                row["cache_neutral_model_credits"] += (Decimal(usage["inputTokens"]) * Decimal("2.5")
                                                        + Decimal(usage["outputTokens"]) * Decimal("12.5")) / 1000000
                for dest, src in (("input_tokens", "inputTokens"), ("cached_input_tokens", "cachedInputTokens"),
                                  ("output_tokens", "outputTokens"), ("reasoning_tokens", "reasoningOutputTokens")):
                    row[dest] += usage[src]
                row["model_wall_seconds"] += call["wall_seconds"]
            final = calls[saved["finals"][arm]["identity"]]
            normalized = study.normalize_response(final["response"])
            verdict = grade(case["initial"] + case["between"], case["task"], json.dumps(normalized))
            row["successes"] += int(verdict["exact"])
            row["false_ready"] += int(verdict["false_ready"] is True)
            row["malformed"] += int(verdict["malformed"])
            row["outcomes"].append({"case": case["id"], "response": normalized, **verdict})
            for stage in ("parent", "child"):
                row["fallbacks"] += int(saved["memories"].get(arm + "_" + stage, {}).get("audit", {}).get("fallback", False))
            try:
                retained = strict_json(final["request"]["observation"]["memory"])
                sufficient = expected_answer(retained, case["task"]) == expected_answer(case["initial"] + case["between"], case["task"])
            except (ValueError, TypeError, KeyError):
                sufficient = None
            row["sufficiency"].append({"case": case["id"], "deterministic_receipt_sufficiency": sufficient})
        if saved["index_storage"]["bytes"] != fresh["index_storage"]["bytes"] or saved["index_storage"]["byte_nanoseconds"] < 0:
            raise ValueError("Invalid index storage accounting")
    spent = sum((usage_cost(c["usage"]) for c in calls.values()), Decimal(0))
    if spent != Decimal(completion["planning_credits"]) or spent > Decimal("20"):
        raise ValueError("Launch budget mismatch")
    for row in arms.values():
        for key in ("model_credits", "cache_neutral_model_credits"):
            row[key] = str(row[key])
    return {"status": "complete", "model": "gpt-6-luna", "effort": "medium", "actual_model_calls": len(calls),
        "known_planning_credits": str(spent), "arms": arms,
        "index_storage_by_case": {c["id"]: read(directory / (c["id"] + "-episode.json"))["index_storage"] for c in study.cases()},
        "evidence_status": manifest["evidence_status"], "held_out_primary_criterion": "unassessed",
        "limits": ["One observed local workflow plus three constructed controls; four correlated cases.",
                   "Model costs are token-derived planning credits; actual account debit and human cost are unknown.",
                   "Local resources are measured separately and not monetized; no total-cost or native-compaction claim."]}


def report(result):
    lines = ["# Luna 6 observed-workflow development comparison", "", "September 29, 2026.", ""]
    if result["status"] != "complete":
        return "\n".join(lines + ["Run incomplete. No complete paired comparison is reported.", "", json.dumps(result, indent=2)])
    lines += [f"{result['actual_model_calls']} calls; {result['known_planning_credits']} token-derived planning credits.", "",
              "| Method | Correct / 4 | False ready | Model credits | Cache-neutral credits | Fallbacks |",
              "|---|---:|---:|---:|---:|---:|"]
    for arm, row in result["arms"].items():
        lines.append(f"| {arm} | {row['successes']}/4 | {row['false_ready']} | {row['model_credits']} | {row['cache_neutral_model_credits']} | {row['fallbacks']} |")
    lines += ["", "These four cases share one observed local development capture. Three continuations are constructed controls. The twelve-episode held-out study remains unperformed.", "",
              "All writers are charged. The saved analysis also reports usage, per-case answers, deterministic receipt sufficiency where parseable, CPU, byte traffic and index storage duration. Prose sufficiency can be unknown. Local resources are not monetized; the table compares model cost only.", "",
              "No production saving, native-compaction improvement, generalization or statistical superiority is established.", ""]
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("directory", type=Path)
    args = parser.parse_args()
    result = analyze(args.directory)
    save(args.directory / "analysis.json", result)
    (args.directory / "report.md").write_text(report(result), encoding="utf-8", newline="\n")
    print(report(result))


if __name__ == "__main__":
    main()
