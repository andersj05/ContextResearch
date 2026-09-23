"""Reconcile two ledgers and report permanent missing answers separately."""
from __future__ import annotations

from decimal import Decimal
from hashlib import sha256
import json
from pathlib import Path

from experiments.dependency_memory.cross_record import run as original
from experiments.dependency_memory.cross_record import analyze as original_analysis
from experiments.dependency_memory.cross_record.casebook import EVAL, grade, truth
from luna6_revision.protocol import request_bytes
from luna6_revision.transport import RESERVATION, usage_cost
from .plan import ORIGINAL, schedule
from .run import OUTPUT, code_fingerprints, verify_plan

CPU_PRICE = Decimal("0.0001")
BYTE_PRICE = Decimal("0.00000001")


def load(path):
    return json.loads(path.read_text(encoding="utf-8"))


def combined_calls(directory):
    sources = (("original", ORIGINAL), ("continuation", directory))
    result = {}
    for phase, root in sources:
        for path in (root / "calls").glob("*.json"):
            if path.stem in result:
                raise ValueError("Repeated request identity across phases")
            record = load(path)
            if record.get("identity") != path.stem:
                raise ValueError("Call path and identity differ")
            result[path.stem] = (phase, record)
    if set(result) != set(schedule()):
        raise ValueError("Original and continuation do not cover exact fixed schedule")
    return result


def analyze(directory):
    plan = verify_plan()
    completion = load(directory / "completion.json")
    manifest = load(directory / "manifest.json")
    if (completion.get("status") != "complete_with_permanent_original_failure" or
            completion.get("new_attempts") != 149 or
            manifest.get("plan_sha256") != sha256((Path(__file__).parent / "plan.json").read_bytes()).hexdigest() or
            manifest.get("code_fingerprints") != code_fingerprints() or
            manifest.get("original_source_fingerprints") != original.fingerprints()):
        raise ValueError("Continuation incomplete or source drift")
    calls = combined_calls(directory)
    known_actual = Decimal(0)
    actual_usage = {name: 0 for name in ("inputTokens", "cachedInputTokens", "outputTokens", "reasoningOutputTokens")}
    missing = []
    for identity, (phase, call) in calls.items():
        if sha256(request_bytes(call["request"])).hexdigest() != call.get("request_sha256"):
            raise ValueError("Saved public request hash differs: " + identity)
        if call.get("model") != "gpt-6-luna" or call.get("effort") != "medium" or not call.get("dispatched"):
            raise ValueError("Model/dispatch contract differs: " + identity)
        if call["status"] == "completed":
            if call.get("tool_items") != 0 or call.get("usage_events") != 1:
                raise ValueError("Unexpected tool or usage events")
            price = usage_cost(call["usage"])
            if price != Decimal(call["planning_credits"]):
                raise ValueError("Token-derived cost differs")
            known_actual += price
            for name in actual_usage:
                actual_usage[name] += call["usage"][name]
        elif call["status"] == "transport_failure":
            if call.get("error") != "Provider generation error":
                raise ValueError("Unexpected failure origin")
            missing.append(identity)
        else:
            raise ValueError("Unexpected attempt status")
    expected_actual = Decimal(load(ORIGINAL / "completion.json")["planning_credits_settled"]) + Decimal(completion["settled_planning_credits"])
    if known_actual != expected_actual:
        raise ValueError("Settled token usage does not reconcile")
    if plan["original_failed_identity"] not in missing or len(missing) != 1 + len(completion["new_provider_failures"]):
        raise ValueError("Permanent failures not reconciled")
    if Decimal(completion["uncertain_reservation_credits"]) != RESERVATION * len(completion["new_provider_failures"]):
        raise ValueError("New uncertainty reserve differs")

    arms = {arm: {"decisions": 0, "terminal_failures": 0, "model_error_failures": 0,
                  "missing_answers": 0, "known_model_credits": Decimal(0),
                  "model_calls_charged": 0, "unknown_model_calls_charged": 0,
                  "cpu_ns": 0, "bytes_read": 0, "bytes_written": 0,
                  "information": {kind: 0 for kind in ("sufficient", "insufficient", "unparsed")}}
            for arm in original.ARMS}
    families = {family: {arm: {"decisions": 0, "failures": 0} for arm in original.ARMS} for family in EVAL}
    detail = []
    complete_future_ids = []

    def charge(arm, identity):
        call = calls[identity][1]
        arms[arm]["model_calls_charged"] += 1
        if call["status"] == "completed":
            arms[arm]["known_model_credits"] += Decimal(call["planning_credits"])
        else:
            arms[arm]["unknown_model_calls_charged"] += 1

    for path in original.fixture_paths()[0]:
        case = load(path)
        cid = case["id"]
        episode_path = directory / (cid + "-episode.json")
        episode = load(episode_path if episode_path.exists() else ORIGINAL / (cid + "-episode.json"))
        for arm in original.ARMS:
            local = episode["local"][arm]
            arms[arm]["cpu_ns"] += local["cpu_ns"]
            arms[arm]["bytes_read"] += local["bytes_read"]
            arms[arm]["bytes_written"] += local["bytes_written"]
        for arm in ("prompt", "structured"):
            identity = cid + "-" + arm + "-parent"
            if calls[identity][1]["request"] != original.parent_request(case, arm):
                raise ValueError("Parent request differs")
            charge(arm, identity)
            if arm == "structured":
                charge("checked", identity)
        for arm in ("prompt", "structured", "checked"):
            identity = cid + "-" + arm + "-child"
            if calls[identity][1]["request"] != original.child_request(case, arm, episode["memories"][arm]["parent"]):
                raise ValueError("Child request differs")
            charge(arm, identity)
        for future in case["futures"]:
            ids = [future["id"] + "-" + arm for arm in original.ARMS]
            fully_measured = all(calls[identity][1]["status"] == "completed" for identity in ids)
            if fully_measured:
                complete_future_ids.append(future["id"])
            for arm, identity in zip(original.ARMS, ids, strict=True):
                call = calls[identity][1]
                retained = original_analysis.recalled_memory(arm, case, episode, future) if hasattr(original_analysis, "recalled_memory") else None
                if retained is None:
                    raise ValueError("Original memory reconstruction unavailable")
                if call["request"] != original.execution_request(case, retained, future):
                    raise ValueError("Final public request differs: " + identity)
                charge(arm, identity)
                expected = truth(case, future)
                observed = call.get("response") if call["status"] == "completed" else None
                correct = call["status"] == "completed" and grade(observed, expected)
                arms[arm]["decisions"] += 1
                arms[arm]["terminal_failures"] += int(not correct)
                arms[arm]["model_error_failures"] += int(call["status"] == "completed" and not correct)
                arms[arm]["missing_answers"] += int(call["status"] != "completed")
                info = original_analysis.information_sufficiency(retained, case, future)
                arms[arm]["information"][info] += 1
                families[case["family"]][arm]["decisions"] += 1
                families[case["family"]][arm]["failures"] += int(not correct)
                detail.append({"identity": identity, "family": case["family"], "arm": arm,
                               "future_id": future["id"], "fully_measured_pair": fully_measured,
                               "status": call["status"], "correct": correct,
                               "information": info, "expected": expected, "response": observed})
    if len(complete_future_ids) > 36:
        raise ValueError("Impossible pair count")
    complete = {arm: {"decisions": 0, "failures": 0} for arm in original.ARMS}
    for row in detail:
        if row["fully_measured_pair"]:
            complete[row["arm"]]["decisions"] += 1
            complete[row["arm"]]["failures"] += int(not row["correct"])
    for arm, row in arms.items():
        row["known_local_credits"] = (Decimal(row["cpu_ns"]) / Decimal(10**9) * CPU_PRICE +
                                      Decimal(row["bytes_read"] + row["bytes_written"]) * BYTE_PRICE)
        row["known_total_lower_bound"] = row["known_model_credits"] + row["known_local_credits"]
        row["reservation_upper_bound"] = row["known_total_lower_bound"] + RESERVATION * row["unknown_model_calls_charged"]
        row["local_complete"] = arm not in {identity.rsplit("-", 1)[-1] for identity in missing}
        for key in ("known_model_credits", "known_local_credits", "known_total_lower_bound", "reservation_upper_bound"):
            row[key] = str(row[key])
    return {"version": "cross_record_continuation_analysis_v1", "status": "exploratory_post_stop",
            "original_primary_criterion": "unassessable_due_to_permanent_transport_failure",
            "scheduled_identities": 348, "original_attempts": 199, "new_attempts": 149,
            "permanent_missing_identities": missing, "fully_measured_paired_futures": len(complete_future_ids),
            "known_settled_model_credits": str(known_actual),
            "unknown_reservation_credits": str(RESERVATION * len(missing)),
            "actual_usage_on_completed_calls": actual_usage,
            "arms": arms, "complete_pairs": complete, "families": families,
            "price_assumptions": {"cpu_credit_per_second": str(CPU_PRICE),
                                  "local_read_or_write_credit_per_byte": str(BYTE_PRICE)},
            "decisions": detail}


def main():
    result = analyze(OUTPUT)
    (OUTPUT / "analysis.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    lines = ["# Cross-record continuation after permanent provider failure", "",
             "The original 348-call preregistered run stopped after 199 dispatches. One projected-index final call was permanently missing. A separate frozen continuation dispatched only the remaining 149 identities. This is an exploratory post-stop analysis; the original primary criterion is unassessable.", "",
             f"Complete paired futures: {result['fully_measured_paired_futures']}/36. Known settled model planning credits: {result['known_settled_model_credits']}; missing usage has {result['unknown_reservation_credits']} credits of conservative reservation, not observed debit.", "",
             "| Method | Exact failures / 36 | Model errors | Missing answers | Failures on complete pairs | Known model credits | Known local credits | Known lower total |",
             "|---|---:|---:|---:|---:|---:|---:|---:|"]
    for arm in original.ARMS:
        row, paired = result["arms"][arm], result["complete_pairs"][arm]
        lines.append(f"| {arm} | {row['terminal_failures']} | {row['model_error_failures']} | {row['missing_answers']} | {paired['failures']}/{paired['decisions']} | {row['known_model_credits']} | {row['known_local_credits']} | {row['known_total_lower_bound']} |")
    lines += ["", "The lower total for an arm with a missing answer omits unknown model usage; the original failed indexed projection also lost its unsaved local recovery timer. It is not a measured equal-cost comparison for that arm.", "",
              "| Family | " + " | ".join(original.ARMS) + " |", "|---|" + "---:|" * len(original.ARMS)]
    for family in EVAL:
        lines.append("| " + family + " | " + " | ".join(str(result["families"][family][arm]["failures"]) + "/12" for arm in original.ARMS) + " |")
    (OUTPUT / "report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps({key: value for key, value in result.items() if key != "decisions"}, indent=2))


if __name__ == "__main__":
    main()
