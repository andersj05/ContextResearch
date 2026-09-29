"""Prepare, then explicitly launch the fixed 108-call development comparison."""
from __future__ import annotations

import argparse
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import sys
from time import perf_counter_ns, process_time_ns

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "experiments/dependency_memory"))

from . import study
from .transport import Client, save
from experiments.dependency_memory.workflow_eval_live.protocol import request_bytes
from experiments.dependency_memory.workflow_eval.grader import strict_json, wire
from experiments.dependency_memory.workflow_eval.packet import direct_records


def fingerprints():
    paths = list(Path(__file__).parent.glob("*.py")) + [Path(__file__).parent / "CONTRACT.md"]
    paths += [ROOT / "experiments/dependency_memory" / n for n in
              ("luna_appserver.py", "codex_subscription.py", "luna_budget.py", "request_contracts.py")]
    paths += [Path(__file__).parent / "capture.json"]
    paths += [p for p in (ROOT / "experiments/dependency_memory/workflow_eval_live").glob("*.py")]
    paths += [p for p in study.PACKET.rglob("*") if p.is_file() and "__pycache__" not in p.parts]
    return {p.relative_to(ROOT).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(paths)}


def execute(client, directory=None):
    """No terminal grading or evaluator feedback inside this loop."""
    episodes = []
    for case in study.cases():
        cid = case["id"]
        row = {"id": cid, "origin": case["origin"], "memories": {},
               "call_ids": {a: [] for a in study.ARMS}, "finals": {},
               "local_events": {a: [] for a in study.ARMS}}

        def measured(arm, name, inputs, operation):
            size = len(wire(inputs))
            cpu, wall = process_time_ns(), perf_counter_ns()
            value = operation()
            elapsed_cpu, elapsed_wall = process_time_ns() - cpu, perf_counter_ns() - wall
            row["local_events"][arm].append({"name": name, "cpu_ns": elapsed_cpu,
                "wall_ns": elapsed_wall, "read_bytes": size, "write_bytes": len(wire(value))})
            return value

        def call(arm, stage, request):
            identity = f"{cid}-{arm}-{stage}"
            row["call_ids"][arm].append(identity)
            return client.complete(identity, request)

        index_start = perf_counter_ns()
        index = measured("indexed", "build_raw_index", case["initial"],
                         lambda: {c: [deepcopy(r) for r in case["initial"] if r["check"] == c] for c in study.CHECKS})
        initial_index_bytes = len(wire(index))
        parents = {}
        for arm in study.order(cid + "parent", ("checked", "prose")):
            response = call(arm, "parent", study.memory_request("parent", arm, {"tool_observations": case["initial"]}))
            if arm == "checked":
                memory, audit = measured(arm, "parent_check_and_fallback", [response, case["initial"]],
                                         lambda: study.checked_memory(response, case["initial"], study.PARENT_CAP))
            else:
                memory, audit = measured(arm, "parent_admission", response,
                                         lambda: study.admit_prose(response, study.PARENT_CAP))
            parents[arm] = memory
            row["memories"][arm + "_parent"] = {"memory": memory, "audit": audit}
        parents["direct"] = measured("direct", "parent_projection", case["initial"],
                                      lambda: wire(direct_records(case["initial"])).decode())
        parent_size = len(parents["direct"].encode())
        if parent_size > study.PARENT_CAP:
            parents["direct"] = ""
        row["memories"]["direct_parent"] = {"memory": parents["direct"], "audit": {"proposal_bytes": parent_size, "infeasible": parent_size > study.PARENT_CAP}}
        # All source-dependent actor state below is bounded parent + new observations.
        memories = {}
        for arm in study.order(cid + "child", ("checked", "prose")):
            observation = {"previous_memory": parents[arm], "new_observations": case["between"], "scope": case["scope"]}
            response = call(arm, "child", study.memory_request("child", arm, observation))
            if arm == "checked":
                available = (strict_json(parents[arm]) if parents[arm] else []) + case["between"]
                memory, audit = measured(arm, "child_check_and_fallback", [response, available],
                                         lambda: study.checked_memory(response, [r for r in available if r["check"] in case["scope"]], study.CHILD_CAP))
            else:
                memory, audit = measured(arm, "child_admission", response,
                                         lambda: study.admit_prose(response, study.CHILD_CAP))
            memories[arm] = memory
            row["memories"][arm + "_child"] = {"memory": memory, "audit": audit}
        direct_available = (strict_json(parents["direct"]) if parents["direct"] else []) + case["between"]
        memories["direct"] = measured("direct", "child_projection", direct_available,
            lambda: wire(direct_records(direct_available, case["scope"])).decode())
        child_size = len(memories["direct"].encode())
        if child_size > study.CHILD_CAP:
            memories["direct"] = ""
        row["memories"]["direct_child"] = {"memory": memories["direct"], "audit": {"proposal_bytes": child_size, "infeasible": child_size > study.CHILD_CAP}}
        index_update = perf_counter_ns()
        def update_index():
            for r in case["between"]:
                index[r["check"]].append(deepcopy(r))
            return index
        index = measured("indexed", "index_new_observations", case["between"], update_index)
        updated_index_bytes = len(wire(index))
        for arm in study.order(cid, study.ARMS):
            if arm == "indexed":
                memory = measured(arm, "retrieve_all_requested_records", index,
                    lambda: wire([r for c in case["task"]["required_checks"] for r in index[c]]).decode())
                now = perf_counter_ns()
                row["index_storage"] = {"bytes": updated_index_bytes,
                    "byte_nanoseconds": initial_index_bytes * (index_update - index_start)
                                       + updated_index_bytes * (now - index_update),
                    "scope": "measured retention during interleaved development schedule"}
            elif arm == "full":
                memory = measured(arm, "read_full_history", case["initial"] + case["between"],
                                   lambda: wire(case["initial"] + case["between"]).decode())
            else:
                memory = memories[arm]
            identity = f"{cid}-{arm}-final"
            call(arm, "final", study.final_request(memory, case["task"]))
            row["finals"][arm] = {"identity": identity, "memory_bytes": len(memory.encode())}
        episodes.append(row)
        if directory is not None:
            save(directory / (cid + "-episode.json"), row)
    return episodes


def prepare(directory, preflight):
    directory.mkdir(parents=True, exist_ok=True)
    if (directory / "manifest.json").exists():
        raise ValueError("Existing immutable launch manifest")
    audit = strict_json(preflight.read_text(encoding="utf-8"))
    if audit.get("isolation_passed") is not True or audit.get("real_model_generations") != 0:
        raise ValueError("Fresh zero-generation isolation preflight required")
    save(directory / "preflight.json", audit)
    save(directory / "manifest.json", {"version": "workflow_executed_v1", "date": "2026-09-29",
        "model": "gpt-6-luna", "reasoning_effort": "medium", "service_tier": "default",
        "immutable_model_revision": None, "sampling_seed": None,
        "schedule_seed": study.SEED, "scheduled_calls": 108, "max_calls": 108,
        "max_planning_credits": "20", "per_call_reservation": "7.65", "api_dollar_spend": 0,
        "evidence_status": "twelve controlled local scenarios with actual subprocess observations; one fixture family",
        "authorization": "User authorized continuing experiments after the Luna 6 pilot on September 29",
        "fingerprints": fingerprints(), "schedule": study.schedule(),
        "cases_sha256": hashlib.sha256(wire(study.cases())).hexdigest(),
        "preflight_sha256": hashlib.sha256((directory / "preflight.json").read_bytes()).hexdigest()})


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--directory", required=True, type=Path)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--prepare", type=Path, metavar="PREFLIGHT")
    mode.add_argument("--launch", action="store_true")
    parser.add_argument("--executable", type=Path)
    parser.add_argument("--global-instructions", type=Path)
    args = parser.parse_args()
    directory = args.directory.resolve()
    if args.prepare:
        prepare(directory, args.prepare)
        print("Frozen 108-call development launch; zero generations dispatched.")
        return
    manifest = strict_json((directory / "manifest.json").read_text(encoding="utf-8"))
    if manifest["fingerprints"] != fingerprints() or manifest["schedule"] != study.schedule():
        raise ValueError("Frozen implementation or schedule changed")
    if manifest["cases_sha256"] != hashlib.sha256(wire(study.cases())).hexdigest():
        raise ValueError("Frozen conditions changed")
    if manifest["preflight_sha256"] != hashlib.sha256((directory / "preflight.json").read_bytes()).hexdigest():
        raise ValueError("Preflight changed")
    (directory / "calls").mkdir(exist_ok=False)
    audit = strict_json((directory / "preflight.json").read_text(encoding="utf-8"))
    transport = Client(args.executable, args.global_instructions, directory, audit)
    class ScheduledClient:
        position = 0
        def complete(self, identity, request):
            if fingerprints() != manifest["fingerprints"] or identity != manifest["schedule"][self.position]:
                raise ValueError("Source or request order drift")
            self.position += 1
            return transport.complete(identity, request)
    try:
        execute(ScheduledClient(), directory)
        if transport.attempts != 108:
            raise ValueError("Incomplete schedule")
        save(directory / "completion.json", {"status": "complete", "calls": transport.attempts,
                                               "planning_credits": str(transport.spent)})
    except Exception as error:
        save(directory / "completion.json", {"status": "stopped", "calls": transport.attempts,
            "planning_credits_settled": str(transport.spent), "error_type": type(error).__name__, "error": str(error)[:160]})
        raise


if __name__ == "__main__":
    main()
