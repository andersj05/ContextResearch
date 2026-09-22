"""Opt-in finite launch. Every production request is charged and saved."""
import argparse
import hashlib
import json
from pathlib import Path
import random
import time

from .protocol import request_bytes, smoke_request
from . import study
from .transport import Client, save


def fingerprints():
    here = Path(__file__).resolve().parent
    paths = list(here.glob("*.py")) + [here / "CONTRACT.md"]
    paths += [here.parent / name for name in ("luna_appserver.py", "codex_subscription.py", "luna_budget.py", "request_contracts.py")]
    return {p.relative_to(here.parent).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}


def execute(client, directory):
    smoke = client.complete("000-smoke", smoke_request())
    if smoke != {"memory": "ready"}:
        raise ValueError("Smoke output differs")
    episodes = []
    for fixture in study.fixtures():
        fid = fixture["id"]
        row = {"fixture": fixture, "memories": {}, "cost_calls": {}, "continuations": []}
        # Stage-one proposals have no pair, seed, future, truth, or method label.
        parents = {}
        for arm in ("prose", "structured"):
            identity = fid + "-" + arm + "-parent"
            response = client.complete(identity, study.memory_request("parent", arm, {"release_tool_history": fixture["records"]}, study.PARENT_CAP))
            parents[arm], bounds = study.admit(response, study.PARENT_CAP)
            row["memories"][arm + "_parent"] = {"memory": parents[arm], **bounds}
            row["cost_calls"][arm] = [identity]
        t = time.process_time_ns()
        parents["repair"], parent_check = study.repair(parents["structured"], fixture["records"], study.PARENT_CAP)
        parent_check["cpu_ns"] = time.process_time_ns()-t
        parents["direct"] = study.projection(fixture["records"])
        row["memories"]["repair_parent"] = {"memory": parents["repair"], "check": parent_check}
        row["cost_calls"]["repair"] = list(row["cost_calls"]["structured"])
        memories = {}
        for arm in ("prose", "structured", "repair"):
            identity = fid + "-" + arm + "-child"
            response = client.complete(identity, study.memory_request("child", arm, {"previous_memory": parents[arm], "candidate_services": fixture["pair"]}, study.CHILD_CAP))
            memories[arm], bounds = study.admit(response, study.CHILD_CAP)
            row["memories"][arm + "_child_proposal"] = {"memory": memories[arm], **bounds}
            row["cost_calls"][arm].append(identity)
        # Enforced deletion: second repair reads only the retained bounded parent.
        recovered_parent = study.decode(parents["repair"])
        child_records = [x for x in recovered_parent if x["service"] in fixture["pair"]]
        t = time.process_time_ns()
        memories["repair"], child_check = study.repair(memories["repair"], child_records, study.CHILD_CAP)
        child_check["cpu_ns"] = time.process_time_ns()-t
        direct_parent = study.decode(parents["direct"])
        memories["direct"] = study.projection([x for x in direct_parent if x["service"] in fixture["pair"]])
        row["memories"]["repair_child"] = {"memory": memories["repair"], "check": child_check}
        row["memories"]["direct_parent"] = {"memory": parents["direct"]}
        row["memories"]["direct_child"] = {"memory": memories["direct"]}
        for arm in ("direct", "indexed", "full"):
            row["cost_calls"][arm] = []
        for future in fixture["futures"]:
            target = next(x for x in fixture["records"] if x["service"] == future["target"])
            truth = study.expected(target, future["event"])
            arms = list(study.ARMS)
            random.Random(future["id"] + ":frozen-order").shuffle(arms)
            for arm in arms:
                recovered_bytes = 0
                if arm == "indexed":
                    memory = study.compact(target)
                    recovered_bytes = len(memory.encode())
                elif arm == "full":
                    memory = study.compact(fixture["records"])
                else:
                    memory = memories[arm]
                identity = future["id"] + "-" + arm
                response = client.complete(identity, study.execute_request(memory, future))
                row["cost_calls"][arm].append(identity)
                row["continuations"].append({"id": identity, "arm": arm, "future": future, "truth": truth,
                                               "recovered_bytes": recovered_bytes, "memory_bytes": len(memory.encode())})
        # Scoring is deliberately deferred until all fixed episodes complete.
        save(directory / (fid + "-episode.json"), row)
        episodes.append(row)
    return episodes


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--executable", required=True, type=Path)
    parser.add_argument("--global-instructions", required=True, type=Path)
    parser.add_argument("--directory", required=True, type=Path)
    parser.add_argument("--launch", action="store_true")
    args = parser.parse_args()
    if not args.launch:
        parser.error("Explicit --launch is required")
    directory = args.directory.resolve()
    if (directory / "manifest.json").exists():
        raise ValueError("Launch already exists; no implicit continuation or retries")
    audit = json.loads((directory / "preflight.json").read_text())
    (directory / "calls").mkdir(exist_ok=False)
    frozen = fingerprints()
    manifest = {"version": "luna6_revision_launch_v1", "model": "gpt-6-luna", "reasoning_effort": "medium",
                "model_revision": "mutable alias; no immutable snapshot exposed", "sampling_seed": None,
                "service_tier": "default", "max_calls": 144, "max_planning_credits": "20", "scheduled_calls": 117,
                "fingerprints": frozen, "preflight_sha256": hashlib.sha256((directory / "preflight.json").read_bytes()).hexdigest(),
                "fixtures": study.fixtures(), "date": "2026-09-22", "status": "running"}
    save(directory / "manifest.json", manifest)
    client = Client(args.executable, args.global_instructions, directory, audit)
    try:
        execute(client, directory)
        if fingerprints() != frozen:
            raise ValueError("Source drift during launch")
        save(directory / "completion.json", {"status": "complete", "calls": client.attempts, "planning_credits": str(client.spent)})
    except Exception as error:
        save(directory / "completion.json", {"status": "stopped", "calls": client.attempts, "planning_credits_settled": str(client.spent), "error_type": type(error).__name__, "error": str(error)[:160]})
        raise


if __name__ == "__main__":
    main()
