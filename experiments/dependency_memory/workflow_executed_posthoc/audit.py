"""Post-stop audit of both immutable prefixes; no provider calls or new answers."""
from decimal import Decimal
import hashlib
import json
from pathlib import Path

from experiments.dependency_memory.workflow_executed_continuation.run import (
    ORIGINAL, OUTPUT, original, study, verify, verify_record, read,
)
from experiments.dependency_memory.workflow_executed.transport import save, usage_cost, RESERVATION
from experiments.dependency_memory.workflow_eval_live.protocol import request_bytes
from experiments.dependency_memory.workflow_eval.grader import grade, expected_answer, strict_json

DESTINATION = ORIGINAL.parent / "workflow_executed_partial_audit.json"
REPORT = ORIGINAL.parent / "workflow_executed_partial_report.md"


def analyze():
    plan, old, old_known = verify(OUTPUT)
    completion = read(OUTPUT / "completion.json")
    new = {p.stem: read(p) for p in (OUTPUT / "calls").glob("*.json")}
    if (completion["status"] != "stopped" or completion["new_calls"] != 9
            or set(old) & set(new) or set(new) != set(plan["pending"][:9])):
        raise ValueError("Stopped suffix does not match its recorded prefix")
    calls = old | new
    schedule = plan["schedule"]
    if set(calls) != set(schedule[:26]):
        raise ValueError("Combined dispatches do not form the frozen 26-call prefix")
    failures = {
        "tests_later_failure-prose-final": "appserver_timeout",
        "tests_recovery-full-final": "Provider generation error",
    }
    seen = []
    class PrefixEnd(Exception):
        pass
    class Replay:
        def complete(self, identity, request):
            if identity not in calls:
                if identity != schedule[26]:
                    raise ValueError("Unexpected first unattempted identity")
                raise PrefixEnd()
            record = calls[identity]
            seen.append(identity)
            if identity not in failures:
                return verify_record(record, identity, request)
            if (record["identity"] != identity or record["status"] != "transport_failure"
                    or record["dispatched"] is not True or record["error"] != failures[identity]
                    or record["request"] != request or record["request_sha256"] != hashlib.sha256(request_bytes(request)).hexdigest()
                    or record["model"] != "gpt-6-luna" or record["effort"] != "medium"
                    or record["reservation_credits"] != str(RESERVATION)
                    or "usage" in record or "response" in record or request["stage"] != "execute"):
                raise ValueError("Permanent failure disposition differs")
            return None
    try:
        original.execute(Replay())
    except PrefixEnd:
        pass
    if seen != schedule[:26]:
        raise ValueError("Not all attempted requests were reconstructed")
    metered = {i: c for i, c in calls.items() if c["status"] == "completed"}
    known = sum((usage_cost(c["usage"]) for c in metered.values()), Decimal(0))
    new_known = sum((usage_cost(c["usage"]) for c in new.values() if c["status"] == "completed"), Decimal(0))
    if new_known != Decimal(completion["new_known_credits"]) or known != old_known + new_known:
        raise ValueError("Known costs do not reconcile")
    unknown = len(failures) * RESERVATION
    arms = {}
    for arm in study.ARMS:
        row = {"scheduled_cases": 12, "answered": 0, "correct": 0, "false_ready": 0, "malformed": 0,
               "transport_missing": 0, "not_dispatched": 0, "known_credits": Decimal(0), "unknown_reservations": Decimal(0), "outcomes": []}
        for case in study.cases():
            identity = case["id"] + "-" + arm + "-final"
            record = calls.get(identity)
            if record is None:
                row["not_dispatched"] += 1
                row["outcomes"].append({"case": case["id"], "status": "not_dispatched"})
            elif record["status"] != "completed":
                row["transport_missing"] += 1
                row["outcomes"].append({"case": case["id"], "status": "missing_transport", "error": record["error"]})
            else:
                response = study.normalize_response(record["response"])
                verdict = grade(case["initial"] + case["between"], case["task"], json.dumps(response))
                row["answered"] += 1
                row["correct"] += int(verdict["exact"])
                row["false_ready"] += int(verdict["false_ready"] is True)
                row["malformed"] += int(verdict["malformed"])
                try:
                    retained = strict_json(record["request"]["observation"]["memory"])
                    sufficient = expected_answer(retained, case["task"]) == expected_answer(case["initial"] + case["between"], case["task"])
                except (ValueError, TypeError, KeyError):
                    sufficient = None
                row["outcomes"].append({"case": case["id"], "status": "observed", "response": response,
                    "retained_table_sufficient": sufficient, **verdict})
            for stage in (("parent", "child", "final") if arm in {"checked", "prose"} else ("final",)):
                call = calls.get(case["id"] + "-" + arm + "-" + stage)
                if call is not None:
                    if call["status"] == "completed":
                        row["known_credits"] += usage_cost(call["usage"])
                    else:
                        row["unknown_reservations"] += RESERVATION
        row["scheduled_success_bounds"] = [row["correct"], row["correct"] + row["transport_missing"] + row["not_dispatched"]]
        row["reserved_upper_credits_for_attempts"] = str(row["known_credits"] + row["unknown_reservations"])
        row["known_credits"], row["unknown_reservations"] = str(row["known_credits"]), str(row["unknown_reservations"])
        arms[arm] = row
    complete_cases = [case["id"] for case in study.cases() if all(
        calls.get(case["id"] + "-" + arm + "-final", {}).get("status") == "completed" for arm in study.ARMS)]
    usage = {key: sum(c["usage"][key] for c in metered.values()) for key in ("inputTokens", "cachedInputTokens", "outputTokens", "reasoningOutputTokens")}
    if sum(a["answered"] + a["transport_missing"] + a["not_dispatched"] for a in arms.values()) != 60:
        raise ValueError("Terminal denominators do not reconcile")
    return {"status": "incomplete_after_two_transport_failures", "scheduled_calls": 108, "dispatches": len(calls),
        "metered_answers": len(metered), "transport_failures": failures, "never_dispatched": schedule[26:],
        "original_primary_criterion": "unassessable", "complete_paired_cases": complete_cases,
        "known_planning_credits": str(known), "unknown_reservation_credits": str(unknown),
        "reserved_upper_credits": str(known + unknown), "ceiling_credits": "20",
        "next_dispatch_reservation_fits": known + unknown + RESERVATION <= Decimal("20"),
        "usage_for_metered_calls": usage, "arms": arms,
        "request_replay": "All 26 attempted inputs reconstructed from frozen source and prior saved responses; no regeneration.",
        "audit_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "limits": ["Only one fully answered paired case; do not rank methods from this partial run.",
                   "No reliable latency, complete cost or narrow-retrieval comparison; two calls have unknown usage.",
                   "Provider error details do not establish a root cause. Native-compaction and real-world held-out claims remain unsupported."]}


def report(result):
    lines = ["# Executed workflow partial evidence audit", "", "September 29, 2026.", "",
        "The 108-call experiment remains incomplete after two transport failures. No failed request was retried.", "",
        f"{result['dispatches']} dispatched; {result['metered_answers']} metered answers; {len(result['never_dispatched'])} never dispatched.",
        f"Known model cost: {result['known_planning_credits']} planning credits. Unknown-usage reservations: {result['unknown_reservation_credits']}. Reserved upper bound: {result['reserved_upper_credits']}.",
        "Another 7.65-credit reservation does not fit the frozen 20-credit ceiling. This is a reservation limit, not measured account spending.", "",
        "| Method | Correct observed finals | Transport-missing finals | Undispatched finals |",
        "|---|---:|---:|---:|"]
    for arm, row in result["arms"].items():
        lines.append(f"| {arm} | {row['correct']}/{row['answered']} | {row['transport_missing']} | {row['not_dispatched']} |")
    lines += ["", "Every method retains the original twelve-case denominator. Conditional observed-answer ratios do not repair missing outcomes or establish a winner. Only the unchanged case is fully paired.", "",
        "All 26 attempted requests were reconstructed from saved evidence. The local corpus contains twelve authored scenarios and 48 actual subprocess observations, including seven failed commands. Offline reproduction checks all saved source/runtime outcomes; this is not untouched real-world evidence.", ""]
    return "\n".join(lines)


if __name__ == "__main__":
    result = analyze()
    save(DESTINATION, result)
    REPORT.write_text(report(result), encoding="utf-8", newline="\n")
    print(report(result))
