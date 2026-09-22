"""Read-only live-evidence audit plus reproducible GPT-6 Luna report generation."""
from collections import Counter
from decimal import Decimal
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "experiments/dependency_memory"))
from luna6_revision import study
from luna6_revision.protocol import request_bytes, smoke_request
from luna6_revision.transport import usage_cost


def load(path):
    return json.loads(path.read_text(encoding="utf-8"))


def independent_truth(original, event):
    """Separate obligation-set formulation; does not call the study grader."""
    artifact = event["value"] if event["kind"] == "artifact" else original["artifact"]
    approval = event["value"] if event["kind"] == "approve" else original["approval"]
    ci_artifact = event["value"] if event["kind"] == "ci_artifact" else original["ci_artifact"]
    required = set(original["required"])
    if event["kind"] == "require_test":
        required.add(event["value"])
    ci = dict(original["ci"])
    if event["kind"] == "test" and original["ci_artifact"] == event["artifact"]:
        ci[event["name"]] = event["value"]
    blockers = set(original["blockers"])
    if event["kind"] == "add_blocker":
        blockers.add(event["value"])
    if event["kind"] == "close_blocker":
        blockers.discard(event["value"])
    work = ({"approval"} if approval != artifact else set()) | {"ci:"+x for x in required if ci_artifact != artifact or ci.get(x) != "pass"} | {"blocker:"+x for x in blockers}
    return {"action": "hold" if work else "release", "artifact": artifact, "work": sorted(work)}


def analyze(directory):
    manifest, completion = load(directory / "manifest.json"), load(directory / "completion.json")
    assert completion["status"] == "complete", "Do not score an unfinished fixed schedule"
    local_cost = load(directory / "local_cost_calibration.json")
    assert local_cost["script_sha256"] == hashlib.sha256((ROOT / "scripts/benchmark_luna6_local_cost.py").read_bytes()).hexdigest()
    assert local_cost["study_sha256"] == hashlib.sha256(Path(study.__file__).read_bytes()).hexdigest()
    calls = {p.stem: load(p) for p in sorted((directory / "calls").glob("*.json"))}
    assert len(calls) == completion["calls"] == manifest["scheduled_calls"] == 117
    assert manifest["fixtures"] == study.fixtures()
    for path, digest in manifest["fingerprints"].items():
        assert hashlib.sha256((ROOT / "experiments/dependency_memory" / path).read_bytes()).hexdigest() == digest, path
    assert hashlib.sha256((directory / "preflight.json").read_bytes()).hexdigest() == manifest["preflight_sha256"]
    total = Decimal(0)
    usage = Counter()
    stages = {}
    for identity, call in calls.items():
        assert call["identity"] == identity and call["status"] == "completed" and call["dispatched"]
        assert call["model"] == "gpt-6-luna" and call["effort"] == "medium"
        assert call["tool_items"] == 0 and call["usage_events"] == 1
        assert call["harness_termination"] == "sessionBudgetExceeded"
        assert hashlib.sha256(request_bytes(call["request"])).hexdigest() == call["request_sha256"]
        credit = usage_cost(call["usage"])
        assert credit == Decimal(call["planning_credits"])
        total += credit
        usage.update(call["usage"])
        stage = call["request"]["stage"]
        bucket = stages.setdefault(stage, {"calls": 0, "credits": Decimal(0), "input_tokens": 0, "output_tokens": 0, "reasoning_output_tokens": 0})
        bucket["calls"] += 1
        bucket["credits"] += credit
        bucket["input_tokens"] += call["usage"]["inputTokens"]
        bucket["output_tokens"] += call["usage"]["outputTokens"]
        bucket["reasoning_output_tokens"] += call["usage"]["reasoningOutputTokens"]
    assert total == Decimal(completion["planning_credits"]) and total <= Decimal(manifest["max_planning_credits"])
    assert calls["000-smoke"]["request"] == smoke_request()
    assert calls["000-smoke"]["response"] == {"memory": "ready"}
    seen = {"000-smoke"}
    method_rows = {a: {"arm": a, "cases": 0, "success": 0, "unsafe_release": 0,
                       "planning_credits": Decimal(0), "cache_neutral_credits": Decimal(0),
                       "model_calls_charged": 0, "wall_seconds": 0, "recovered_bytes": 0,
                       "checker_cpu_ns": 0, "checked_source_bytes": 0, "clipped_memories": 0} for a in study.ARMS}
    failures, scored, episodes = [], [], []

    def verify(identity, request):
        assert calls[identity]["request"] == request, identity
        seen.add(identity)

    for fixture in study.fixtures():
        fid = fixture["id"]
        episode = load(directory / (fid + "-episode.json"))
        assert episode["fixture"] == fixture
        parents, child = {}, {}
        for arm in ("prose", "structured"):
            identity = fid + "-" + arm + "-parent"
            verify(identity, study.memory_request("parent", arm, {"release_tool_history": fixture["records"]}, study.PARENT_CAP))
            parents[arm], bounds = study.admit(calls[identity]["response"], study.PARENT_CAP)
            assert episode["memories"][arm+"_parent"] == {"memory": parents[arm], **bounds}
            method_rows[arm]["clipped_memories"] += bounds["clipped"]
        parents["repair"] = study.projection(fixture["records"])
        assert parents["repair"] == episode["memories"]["repair_parent"]["memory"]
        method_rows["repair"]["clipped_memories"] += episode["memories"]["structured_parent"]["clipped"]
        for arm in ("prose", "structured", "repair"):
            identity = fid + "-" + arm + "-child"
            verify(identity, study.memory_request("child", arm, {"previous_memory": parents[arm], "candidate_services": fixture["pair"]}, study.CHILD_CAP))
            child[arm], bounds = study.admit(calls[identity]["response"], study.CHILD_CAP)
            assert episode["memories"][arm+"_child_proposal"] == {"memory": child[arm], **bounds}
            method_rows[arm]["clipped_memories"] += bounds["clipped"]
        child_records = [r for r in study.decode(parents["repair"]) if r["service"] in fixture["pair"]]
        child["repair"] = study.projection(child_records)
        child["direct"] = child["repair"]
        assert episode["memories"]["repair_child"]["memory"] == child["repair"] == episode["memories"]["direct_child"]["memory"]
        assert len(parents["repair"].encode()) <= study.PARENT_CAP and len(child["repair"].encode()) <= study.CHILD_CAP
        for boundary in ("parent", "child"):
            check = episode["memories"]["repair_"+boundary]["check"]
            method_rows["repair"]["checker_cpu_ns"] += check["cpu_ns"]
            method_rows["repair"]["checked_source_bytes"] += check["checked_source_bytes"]
        expected_continuations = {future["id"] + "-" + arm for future in fixture["futures"] for arm in study.ARMS}
        assert {x["id"] for x in episode["continuations"]} == expected_continuations
        for saved in episode["continuations"]:
            future, arm, identity = saved["future"], saved["arm"], saved["id"]
            assert future in fixture["futures"]
            original = next(r for r in fixture["records"] if r["service"] == future["target"])
            truth = independent_truth(original, future["event"])
            assert truth == saved["truth"] == study.expected(original, future["event"])
            memory = study.compact(original) if arm == "indexed" else study.compact(fixture["records"]) if arm == "full" else child[arm]
            verify(identity, study.execute_request(memory, future))
            assert saved["memory_bytes"] == len(memory.encode())
            verdict = study.grade(calls[identity]["response"], truth)
            independent_success = calls[identity]["response"] == truth
            if isinstance(calls[identity]["response"], dict) and isinstance(calls[identity]["response"].get("work"), list):
                independent_success = {**calls[identity]["response"], "work": sorted(calls[identity]["response"]["work"])} == truth
            assert verdict["success"] == independent_success
            method_rows[arm]["cases"] += 1
            method_rows[arm]["success"] += verdict["success"]
            method_rows[arm]["unsafe_release"] += verdict["unsafe_release"]
            method_rows[arm]["recovered_bytes"] += saved["recovered_bytes"]
            scored.append({"id": identity, "arm": arm, "future_id": future["id"], **verdict})
            if not verdict["success"]:
                failures.append({"id": identity, "arm": arm, "future": future, "expected": truth, "answer": calls[identity]["response"], "memory": memory, "parent_memory": parents.get(arm)})
        for arm in study.ARMS:
            charged = episode["cost_calls"][arm]
            terminal_ids = {x for x in expected_continuations if x.endswith("-"+arm)}
            manager_ids = set()
            if arm in {"prose", "structured", "repair"}:
                manager_ids = {fid+"-"+("structured" if arm == "repair" else arm)+"-parent", fid+"-"+arm+"-child"}
            assert set(charged) == terminal_ids | manager_ids and len(charged) == len(set(charged))
            for identity in charged:
                call = calls[identity]
                method_rows[arm]["planning_credits"] += Decimal(call["planning_credits"])
                u = call["usage"]
                method_rows[arm]["cache_neutral_credits"] += (Decimal(u["inputTokens"])*Decimal("2.5") + Decimal(u["outputTokens"])*Decimal("12.5"))/1000000
                method_rows[arm]["model_calls_charged"] += 1
                method_rows[arm]["wall_seconds"] += call["wall_seconds"]
        episodes.append(episode)
    assert seen == set(calls)
    for future in [x for f in study.fixtures() for x in f["futures"]]:
        assert calls[future["id"]+"-repair"]["request"] == calls[future["id"]+"-direct"]["request"]
    table = []
    for arm in study.ARMS:
        row = method_rows[arm]
        row["planning_credits"] = str(row["planning_credits"])
        row["cache_neutral_credits"] = str(row["cache_neutral_credits"])
        row["wall_seconds"] = round(row["wall_seconds"], 3)
        table.append(row)
    frontier = []
    for cap in sorted({Decimal(r["planning_credits"]) for r in table}):
        admitted = [r for r in table if Decimal(r["planning_credits"]) <= cap]
        best = max(r["success"] for r in admitted)
        frontier.append({"common_cap": str(cap), "best_success": best, "best_methods": [r["arm"] for r in admitted if r["success"] == best]})
    for row in stages.values():
        row["credits"] = str(row["credits"])
    full = method_rows["full"]
    direct = method_rows["direct"]
    extraction_margin = {"scope": "Post-hoc observed headroom for an additional projection extractor across these four histories, if it preserves the direct method's outcomes; no extractor was run.",
                         "observed_full_minus_direct_credits": str(Decimal(full["planning_credits"])-Decimal(direct["planning_credits"])),
                         "cache_neutral_full_minus_direct_credits": str(Decimal(full["cache_neutral_credits"])-Decimal(direct["cache_neutral_credits"])),
                         "same_observed_success": full["success"] == direct["success"]}
    return {"version": "luna6_revision_analysis_v1", "audit_passed": True, "launch_commit": "136d589",
            "actual_dispatches": len(calls), "actual_planning_credits": str(total), "usage": dict(usage),
            "stage_totals": stages, "additional_extraction_headroom": extraction_margin,
            "methods": table, "failures": failures, "scores": scored, "model_credit_frontier": frontier,
            "local_cost_calibration": local_cost,
            "identical_repair_direct_final_inputs": 16,
            "limitations": ["Four constructed histories; 16 correlated continuations per arm; development only.",
                            "Imposed byte caps and fresh reasoning state; not native provider compaction.",
                            "Hand-written gate adapter; no automatic extraction or generic feedback novelty.",
                            "Credits are token-metered planning equivalents; actual debit and infrastructure conversion unknown.",
                            "Costs start at the handoff; prior workflow execution and adapter development are unmeasured.",
                            "Direct and repaired final prompts are identical; differences there are sampling variation.",
                            "Overlong generated memories are clipped; this may explain errors and must be reported."]}


def render(report):
    lines = ["# GPT-6 Luna medium: delayed release pilot", "", "Frozen launch `136d589`; September 22, 2026. See [contract](../../luna6_revision/CONTRACT.md).", "",
             f"Audit passed. **{report['actual_dispatches']} actual model calls**, {report['actual_planning_credits']} planning credits, including smoke and every failed decision. Four constructed histories, 16 delayed continuations per method.", "",
             "| Method | Exact success | Unsafe release | Model credits | Cache-neutral credits | Charged calls | Clipped memories |", "|---|---:|---:|---:|---:|---:|---:|"]
    for r in report["methods"]:
        lines.append(f"| {r['arm']} | {r['success']}/{r['cases']} | {r['unsafe_release']} | {r['planning_credits']} | {r['cache_neutral_credits']} | {r['model_calls_charged']} | {r['clipped_memories']} |")
    lines += ["", "Parent calls shared during the experiment are charged in full to each hypothetical method that uses them. Method charges therefore do not sum to actual experiment usage. Each method serves four continuations per history; compaction calls are charged once per history. Cache-neutral costs remove cache discounts, without rerunning the model.", "",
              "Repair and direct retention have identical terminal inputs. Their response differences cannot identify a memory-treatment effect. Repair uses a conservative whole-projection replacement, not minimal semantic repair.", "",
              "## Common model-credit allowances", "", "| Common cap | Best exact success | Methods attaining it |", "|---:|---:|---|"]
    for r in report["model_credit_frontier"]:
        lines.append(f"| {r['common_cap']} | {r['best_success']}/16 | {', '.join(r['best_methods'])} |")
    lines += ["", "These are observed method points under an equal allowance, not interpolated learning curves. CPU checking time and recovery bytes are separate physical measurements in the JSON report; unknown infrastructure-to-credit conversion prevents a fully monetized total-cost claim.", "", "## Failed decisions", ""]
    for f in report["failures"]:
        lines += [f"- `{f['id']}`: expected `{json.dumps(f['expected'], sort_keys=True)}`; received `{json.dumps(f['answer'], sort_keys=True)}`."]
    lines += ["", "## Limits", ""] + ["- " + x for x in report["limitations"]]
    return "\n".join(lines) + "\n"


def main():
    directory = ROOT / "experiments/dependency_memory/results/luna6_revision_2026-09-22"
    report = analyze(directory)
    (directory / "analysis.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8", newline="\n")
    (directory / "report.md").write_text(render(report), encoding="utf-8", newline="\n")
    print(json.dumps({k: report[k] for k in ("audit_passed", "actual_dispatches", "actual_planning_credits", "methods")}))


if __name__ == "__main__":
    main()
