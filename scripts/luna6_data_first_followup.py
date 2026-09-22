"""Frozen opt-in 24-call prompt repair; shares the original 144-call/20-credit cap."""
from decimal import Decimal
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "experiments/dependency_memory"))
from luna6_revision import study
from luna6_revision.transport import Client, save, usage_cost
from luna6_revision.protocol import request_bytes
from analyze_luna6_revision import independent_truth

ORIGINAL = ROOT / "experiments/dependency_memory/results/luna6_revision_2026-09-22"
DESTINATION = ROOT / "experiments/dependency_memory/results/luna6_data_first_2026-09-22"
GUIDANCE = (
    "The complete gate rules and output schema are public and will be supplied again at every later stage. "
    "Do not spend retained memory repeating those rules. Start with compact service-specific facts. "
    "Preserve complete service/test/blocker identifiers without renaming or abbreviating their values. "
    "At the child boundary retain only the named candidate services. "
)


def memory_request(stage, observation, cap):
    request = study.memory_request(stage, "structured", observation, cap)
    request["instruction"] = GUIDANCE + request["instruction"].replace(
        "Only that string survives.", "Only that string survives from the private source history; the public gate rules are repeated.")
    return request


def load(path):
    return json.loads(path.read_text(encoding="utf-8"))


def fingerprints():
    paths = [Path(__file__), ROOT / "docs/LUNA6_DATA_FIRST_FOLLOWUP.md", ROOT / "scripts/analyze_luna6_revision.py"]
    paths += list((ROOT / "experiments/dependency_memory/luna6_revision").glob("*.py"))
    return {str(path.relative_to(ROOT)).replace("\\", "/"): hashlib.sha256(path.read_bytes()).hexdigest() for path in paths}


def launch():
    completion = load(ORIGINAL / "completion.json")
    assert completion["status"] == "complete" and completion["calls"] == 117
    assert Decimal(completion["planning_credits"]) == Decimal("1.1282525")
    if DESTINATION.exists():
        raise ValueError("Follow-up already exists; never retry implicitly")
    (DESTINATION / "calls").mkdir(parents=True)
    audit = load(ORIGINAL / "preflight.json")
    frozen = fingerprints()
    save(DESTINATION / "manifest.json", {"variant": "data_first_v1", "scheduled_new_calls": 24,
         "prior_calls": 117, "prior_credits": completion["planning_credits"], "shared_call_cap": 144,
         "shared_credit_cap": "20", "model": "gpt-6-luna", "reasoning_effort": "medium",
         "fingerprints": frozen, "main_manifest_sha256": hashlib.sha256((ORIGINAL / "manifest.json").read_bytes()).hexdigest(),
         "guidance": GUIDANCE, "status": "frozen-before-followup-answers"})
    client = Client(Path("C:/Users/jense/AppData/Local/OpenAI/Codex/bin/d375f7df50d3b421/codex.exe"),
                    Path("C:/Users/jense/.codex/AGENTS.md"), DESTINATION, audit)
    client.attempts = completion["calls"]
    client.spent = Decimal(completion["planning_credits"])
    try:
        for fixture in study.fixtures():
            fid = fixture["id"]
            parent_response = client.complete(fid+"-parent", memory_request("parent", {"release_tool_history": fixture["records"]}, study.PARENT_CAP))
            parent, _ = study.admit(parent_response, study.PARENT_CAP)
            child_response = client.complete(fid+"-child", memory_request("child", {"previous_memory": parent, "candidate_services": fixture["pair"]}, study.CHILD_CAP))
            child, _ = study.admit(child_response, study.CHILD_CAP)
            for future in fixture["futures"]:
                client.complete(future["id"], study.execute_request(child, future))
        assert fingerprints() == frozen, "Frozen code drift"
        save(DESTINATION / "completion.json", {"status": "complete", "new_calls": client.attempts-117,
             "combined_calls": client.attempts, "combined_credits": str(client.spent),
             "new_credits": str(client.spent-Decimal(completion["planning_credits"]))})
    except Exception as error:
        save(DESTINATION / "completion.json", {"status": "stopped", "combined_attempts": client.attempts,
             "combined_settled_credits": str(client.spent), "error": str(error)[:160]})
        raise


def analyze():
    done, manifest = load(DESTINATION / "completion.json"), load(DESTINATION / "manifest.json")
    assert done["status"] == "complete" and done["new_calls"] == 24 and done["combined_calls"] == 141
    assert fingerprints() == manifest["fingerprints"]
    assert hashlib.sha256((ORIGINAL / "manifest.json").read_bytes()).hexdigest() == manifest["main_manifest_sha256"]
    calls = {path.stem: load(path) for path in (DESTINATION / "calls").glob("*.json")}
    assert len(calls) == 24
    total, neutral = Decimal(0), Decimal(0)
    usage = {"inputTokens": 0, "cachedInputTokens": 0, "outputTokens": 0, "reasoningOutputTokens": 0}
    for identity, call in calls.items():
        assert call["identity"] == identity and call["model"] == "gpt-6-luna" and call["effort"] == "medium"
        assert call["status"] == "completed" and call["tool_items"] == 0 and call["usage_events"] == 1
        assert hashlib.sha256(request_bytes(call["request"])).hexdigest() == call["request_sha256"]
        cost = usage_cost(call["usage"])
        assert cost == Decimal(call["planning_credits"])
        total += cost
        neutral += (Decimal(call["usage"]["inputTokens"])*Decimal("2.5") + Decimal(call["usage"]["outputTokens"])*Decimal("12.5"))/1000000
        for key in usage:
            usage[key] += call["usage"][key]
    assert total == Decimal(done["new_credits"])
    assert total+Decimal(manifest["prior_credits"]) == Decimal(done["combined_credits"]) <= Decimal("20")
    decisions, memories, seen = [], [], set()
    for fixture in study.fixtures():
        fid = fixture["id"]
        parent_call, child_call = calls[fid+"-parent"], calls[fid+"-child"]
        assert parent_call["request"] == memory_request("parent", {"release_tool_history": fixture["records"]}, study.PARENT_CAP)
        parent, bounds1 = study.admit(parent_call["response"], study.PARENT_CAP)
        assert child_call["request"] == memory_request("child", {"previous_memory": parent, "candidate_services": fixture["pair"]}, study.CHILD_CAP)
        child, bounds2 = study.admit(child_call["response"], study.CHILD_CAP)
        memories.append({"history": fid, "parent": parent, "parent_bounds": bounds1, "child": child, "child_bounds": bounds2})
        seen.update((fid+"-parent", fid+"-child"))
        for future in fixture["futures"]:
            identity = future["id"]
            assert calls[identity]["request"] == study.execute_request(child, future)
            row = next(r for r in fixture["records"] if r["service"] == future["target"])
            truth = independent_truth(row, future["event"])
            verdict = study.grade(calls[identity]["response"], truth)
            decisions.append({"id": identity, "answer": calls[identity]["response"], "truth": truth, **verdict})
            seen.add(identity)
    assert seen == set(calls)
    report = {"audit_passed": True, "new_calls": 24, "cases": 16,
              "success": sum(r["success"] for r in decisions), "unsafe_release": sum(r["unsafe_release"] for r in decisions),
              "planning_credits": str(total), "cache_neutral_credits": str(neutral), "usage": usage,
              "clipped_memories": sum(r[b]["clipped"] for r in memories for b in ("parent_bounds", "child_bounds")),
              "memories": memories, "decisions": decisions, "combined_calls": done["combined_calls"],
              "combined_credits": done["combined_credits"],
              "limitations": "Post-pilot prompt package on the same four constructed histories; development evidence, not held-out, statistically independent, or a single-factor causal effect."}
    return report


if __name__ == "__main__":
    if sys.argv[1:] == ["--launch"]:
        launch()
    elif sys.argv[1:] == ["--analyze"]:
        result = analyze()
        save(DESTINATION / "analysis.json", result)
        print(json.dumps({k:v for k,v in result.items() if k not in {"memories", "decisions"}}))
    else:
        raise SystemExit("Use --launch (paid, never replay) or --analyze (offline)")
