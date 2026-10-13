"""Offline post hoc inspection of the saved v6/v7 information boundaries.

Reads frozen inputs and received requests; never contacts a model or rewrites
original evidence. Output is a descriptive supplement, not a new experiment.
"""
import argparse
from collections import Counter
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "experiments/dependency_memory/results"
V7 = RESULTS / "rollback_checkpoint_v7_2026-10-12"
V6 = RESULTS / "rollback_challenge_v6_four_actions_confirmation_2026-10-09"


def read(path):
    return json.loads(path.read_text(encoding="utf-8"))


def wire(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def inspect():
    run = V7 / "live_pilot"
    execution = read(run / "execution.json")
    tasks = {t["task_id"]: t for t in read(V7 / "prepared_client_2026-10-12/tasks.json")}
    grouped = {}
    for row in execution["jobs"]:
        grouped.setdefault(row["job"]["task_id"], {})[row["job"]["arm"]] = row["result"]
    counts = {arm: Counter() for arm in ("K", "R")}
    rows = []
    for task_id, arms in grouped.items():
        prefix = arms["prefix"]
        if not prefix["eligible"]:
            continue
        task = tasks[task_id]
        stage = prefix["pair_contract"]["failure_stage"]
        expected_dossier = [
            {"stage": i + 1, "stage_count": len(task["stages"]),
             "requirements": task["stages"][i]["requirements"]}
            for i in range(stage)
        ]
        payloads = {}
        record = {"task_id": task_id, "failure_stage": stage,
                  "remaining_stages": len(task["stages"]) - stage + 1}
        for arm in ("K", "R"):
            outcome = arms[arm]
            call_id = outcome["call_ids"][0]
            payload = read(run / "requests" / (call_id + ".json"))
            state = json.loads(payload["messages"][1]["content"])
            assert state["public_dossier"] == expected_dossier
            assert state["accepted_artifact"] == prefix["checkpoint"]["artifact"]
            assert state["checkpoint"]["records"] == prefix["checkpoint"]["checkpoint_records"]
            assert state["lesson"] == prefix["lesson"]
            assert state["trial"] == (prefix["trial"] if arm == "K" else [])
            assert state["remaining_actions"] == record["remaining_stages"]
            record["remaining_actions"] = state["remaining_actions"]
            state["trial"] = []
            payload["messages"][1]["content"] = wire(state)
            payloads[arm] = payload
            events = outcome["events"]
            assert events and events[0]["stage"] == stage
            immediate = events[0]["status"] == "public_pass"
            eventual = any(e["stage"] == stage and e["status"] == "public_pass" for e in events)
            final = outcome["score"] == 1
            counts[arm].update({"eligible": 1, "immediate_repair": int(immediate),
                               "eventual_same_stage_repair": int(eventual),
                               "terminal_success": int(final),
                               "repair_after_first_retry": int(eventual and not immediate),
                               "immediate_repair_then_later_failure": int(immediate and not final)})
            record[arm] = {"first_call_id": call_id, "immediate_repair": immediate,
                           "eventual_same_stage_repair": eventual, "terminal_success": final,
                           "events": [{k: e[k] for k in ("stage", "step", "status", "check")} for e in events]}
        assert payloads["K"] == payloads["R"]
        failed_values = prefix["trial"][0]["action"]["candidate"]["values"]
        normalize = lambda value: re.sub(r"\s+", "", wire(value))
        record["complete_failed_vector_in_lesson"] = normalize(failed_values) in normalize(prefix["lesson"])
        rows.append(record)

    example_id = "54838cccf1bf274693aeb052961beca3921e76a9ff952fbdcb5e9bb5d6454bcb"
    request_path = V6 / "live_confirmation/requests" / (example_id + ".json")
    response_path = V6 / "live_confirmation/responses" / (example_id + ".json")
    state = json.loads(read(request_path)["messages"][1]["content"])
    response = json.loads(read(response_path)["text"])
    assert state["history"] == [] and state["public_dossier"] == []
    assert state["packet"]["stage"] == 2 and state["memory"]
    assert response["candidate"] == state["checkpoint_artifact"]
    v6_example = {
        "call_id": example_id, "task_id": state["task"]["task_id"],
        "history_records": len(state["history"]), "dossier_packets": len(state["public_dossier"]),
        "current_packet_records": len(state["packet"]["requirements"]),
        "response_repeats_checkpoint": True, "response_note": response["note"],
        "request_sha256": digest(request_path), "response_sha256": digest(response_path),
    }
    return {
        "evidence_kind": "post_hoc_saved_request_and_trajectory_inspection",
        "evidence_date_utc": "2026-10-13", "model_calls": 0,
        "limitations": ["Descriptive observations, not prespecified additional efficacy endpoints.",
                        "Literal lesson overlap is not a semantic information measure.",
                        "Matched requests do not identify private reasoning or the cause of individual errors.",
                        "V6 example establishes a source-removal path, not the share of the effect it explains."],
        "v7_execution_sha256": digest(run / "execution.json"),
        "v7_tasks_sha256": digest(V7 / "prepared_client_2026-10-12/tasks.json"),
        "v7_verified_pairs": len(rows),
        "v7_checks": {"only_trial_differs": True, "source_packets_preserved": True,
                      "accepted_artifact_matches_pre_failure_checkpoint": True,
                      "shared_lesson_identical": True, "remaining_actions_equal_remaining_stages": True},
        "v7_counts": counts,
        "v7_complete_failed_vectors_in_lessons": sum(r["complete_failed_vector_in_lesson"] for r in rows),
        "v7_rows": rows, "v6_example": v6_example,
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = inspect()
    if args.output:
        with args.output.open("x", encoding="utf-8", newline="\n") as stream:
            json.dump(result, stream, ensure_ascii=False, sort_keys=True, indent=2)
            stream.write("\n")
    print(wire({k: v for k, v in result.items() if k != "v7_rows"}))
