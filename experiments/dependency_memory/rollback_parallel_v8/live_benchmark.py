"""Fixed ABBA throughput probe with identical prompts and unique admissions.

This is a separate engineering allocation, not rollback efficacy evidence and
not a retry of a historical model call. All four batches run serially; only
requests inside a batch are concurrent. Each task prompt is repeated once per
batch, disclosed as a deliberate repeated-prompt diagnostic.
"""
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import asdict
from datetime import datetime
from pathlib import Path
import argparse
import math
import shutil
from statistics import median
import time

from .common import ROOT, STUDY, read, save_new, sha, now, wire
from .prepare import check_bundle
from .engine import initial_state
from .accounting import Identity, Ledger, Stopped, CallUnknown
from .runner import client_preflight
from .audit import verify_live_preflight
from .client import live_factory
from ..rollback_checkpoint_v7.contexts import render
from ..rollback_checkpoint_v7.audit import _inventory, _metering, ReplayMismatch
from ..rollback_development_v5.audit import ledger_rows
from ..rollback_development_v5_continuation.dispatch import Dispatcher
from ..rollback_development_v5.analysis import metering


COUNTS = (8, 16, 16, 8)
TASKS = 16


def plan(manifest, tasks):
    selected = tasks[:TASKS]
    if len(selected) != TASKS:
        raise ValueError("throughput probe needs sixteen frozen tasks")
    rows = []
    for batch, workers in enumerate(COUNTS):
        for task in selected:
            identity = Identity(STUDY, task["task_id"], "throughput", f"batch{batch}-workers{workers}", 1, "action")
            request = render(task, initial_state(task))
            rows.append({"batch": batch, "workers": workers, "identity": asdict(identity),
                         "call_id": identity.key, "request_hash": sha(request.json_text)})
    return {"version": "rollback-parallel-v8-throughput-v1", "base_manifest_sha256": sha(manifest),
            "model": manifest["model"], "effort": manifest["effort"],
            "source_bindings": manifest["source_bindings"], "schedule": rows,
            "generation_ceiling": 64, "batch_workers": list(COUNTS),
            "scope": "four serial batches, same sixteen prompts; descriptive timing with cache/order/provider noise"}


def prepare_probe(bundle):
    manifest, tasks = check_bundle(bundle)
    value = plan(manifest, tasks)
    save_new(Path(bundle) / "throughput_manifest.json", value)
    save_new(Path(bundle) / "throughput_bundle.json", {"manifest_sha256": sha(value), "model_calls": 0})
    return value


def checked_plan(bundle):
    manifest, tasks = check_bundle(bundle)
    value = read(Path(bundle) / "throughput_manifest.json")
    if value != plan(manifest, tasks) or sha(value) != read(Path(bundle) / "throughput_bundle.json")["manifest_sha256"]:
        raise ValueError("throughput plan changed")
    return value, tasks[:TASKS]


def analyze(calls, batches):
    rows = []
    for batch in batches:
        arm = f"batch{batch['batch']}-workers{batch['workers']}"
        admitted = [call for call in calls if call["identity"]["arm"] == arm]
        completed = [call for call in admitted if call["state"] == "completed"]
        latencies = sorted(call["elapsed_seconds"] for call in completed)
        duration = batch["wall_seconds"]
        rows.append({**batch, "planned_calls": TASKS, "admitted_calls": len(admitted),
                     "completed_calls": len(completed), "unknown_calls": len(admitted)-len(completed),
                     "never_admitted_calls": TASKS-len(admitted), "resources": metering(completed),
                     "known_call_elapsed_seconds": {"minimum": min(latencies), "median": median(latencies),
                                                    "maximum": max(latencies)} if latencies else None,
                     "completed_calls_per_second": len(completed)/duration if duration else None})
    comparable = all(row["completed_calls"] == TASKS for row in rows) and len(rows) == len(COUNTS)
    pooled = {str(workers): sum(row["wall_seconds"] for row in rows if row["workers"] == workers)
              for workers in (8, 16)}
    return {"evidence_kind": "observed_subscription_throughput_probe", "batches": rows,
            "all_64_calls_known": comparable,
            "pooled_batch_seconds": pooled,
            "descriptive_16_vs_8_speed_ratio": pooled["8"]/pooled["16"] if comparable else None,
            "descriptive_elapsed_reduction_fraction": 1-pooled["16"]/pooled["8"] if comparable else None,
            "limitations": "Two batches per worker count, repeated prompts and possible cache/provider/order effects; no general or causal provider throughput guarantee; no rollback efficacy claim."}


def run_probe(bundle, output, *, live=False, executable=None, global_instructions=None):
    if not live:
        raise ValueError("live throughput dispatch requires explicit live=True")
    value, tasks = checked_plan(bundle)
    bundle, output = Path(bundle).resolve(), Path(output).resolve()
    marker = bundle / "throughput_launch_started.json"
    if not output.is_relative_to(ROOT) or output.exists() or marker.exists():
        raise ValueError("new workspace probe output and unstarted allocation required")
    executable = executable or shutil.which("codex.exe") or shutil.which("codex")
    if not executable:
        raise ValueError("installed executable missing")
    global_instructions = Path(global_instructions or Path.home()/".codex"/"AGENTS.md")
    output.mkdir(parents=True)
    checked = client_preflight(executable, global_instructions, output/"scratch", tasks, 16)
    save_new(output/"preflight.json", checked)
    save_new(marker, {"output": str(output), "manifest_sha256": sha(value), "started_utc": now()})
    save_new(output/"manifest.json", value)
    identities = [Identity(**row["identity"]) for row in value["schedule"]]
    ledger = Ledger(output/"ledger.sqlite", identities, 16, generation_ceiling=64)
    dispatcher = Dispatcher(output, value, ledger,
                            live_factory(executable, global_instructions, checked, output/"scratch"))
    requests = {task["task_id"]: render(task, initial_state(task)) for task in tasks}
    batches = []
    for batch, workers in enumerate(COUNTS):
        started_utc, started = now(), time.monotonic()
        dispositions = []
        def work(row):
            identity = Identity(**row["identity"])
            try:
                dispatcher(identity, requests[identity.task_id])
                status = "completed"
            except CallUnknown:
                status = "unknown"
            except Stopped:
                status = "stopped_or_not_admitted"
            except Exception:
                ledger.stop("controller_error")
                raise
            return {"call_id": identity.key, "status": status}
        planned = [row for row in value["schedule"] if row["batch"] == batch]
        with ThreadPoolExecutor(max_workers=workers, thread_name_prefix=f"v8-throughput-{batch}") as pool:
            futures = [pool.submit(work, row) for row in planned]
            for future in as_completed(futures):
                dispositions.append(future.result())
        record = {"batch": batch, "workers": workers, "started_utc": started_utc,
                  "finished_utc": now(), "wall_seconds": time.monotonic()-started,
                  "dispositions": sorted(dispositions, key=lambda row: row["call_id"])}
        batches.append(record)
        save_new(output/"batches"/f"{batch}.json", record)
        snapshot = ledger.snapshot()
        print(wire({"batch_finished": batch, "workers": workers,
                    "completed": snapshot["completed_calls"],
                    "unknown": snapshot["unknown_or_inflight_calls"], "stop": snapshot["stop"]}), flush=True)
    accounting = ledger.snapshot()
    save_new(output/"accounting.json", accounting)
    save_new(output/"analysis.json", analyze(accounting["calls"], batches))
    save_new(output/"evidence_manifest.json", {
        "files": [{"path": path.relative_to(output).as_posix(), "sha256": sha(path.read_bytes())}
                  for path in sorted(output.rglob("*.json")) if "scratch" not in path.relative_to(output).parts],
        "ledger_sha256": sha((output/"ledger.sqlite").read_bytes())})
    return {"model_calls": len(accounting["calls"]), "completed": accounting["completed_calls"],
            "unknown": accounting["unknown_or_inflight_calls"], "stop": accounting["stop"]}


def audit_probe(bundle, output):
    value, tasks = checked_plan(bundle)
    output = Path(output).resolve()
    if read(output/"manifest.json") != value:
        raise ReplayMismatch("throughput manifest differs")
    _inventory(output)
    verify_live_preflight(read(output/"preflight.json"), 16)
    calls, events, stop = ledger_rows(output/"ledger.sqlite")
    manifest = {**value, "schedule": [row["identity"] for row in value["schedule"]]}
    accounting, peak = _metering(calls, events, stop, manifest, {"workers": 16, "live": True})
    if accounting != read(output/"accounting.json"):
        raise ReplayMismatch("throughput accounting differs")
    requests = {task["task_id"]: render(task, initial_state(task)) for task in tasks}
    for call in calls:
        request = requests[call["identity"]["task_id"]]
        if call["request_hash"] != sha(request.json_text) or read(output/"requests"/(call["call_id"]+".json")) != request.data():
            raise ReplayMismatch("throughput prompts differ from identical frozen inputs")
        if call["state"] == "completed":
            response = read(output/"responses"/(call["call_id"]+".json"))
            if response["usage"] != call["usage"] or response["metadata"] != call["metadata"]:
                raise ReplayMismatch("throughput response or usage differs")
    batches = [read(output/"batches"/f"{i}.json") for i in range(4)]
    batch_peaks = []
    for index, batch in enumerate(batches):
        expected = {row["call_id"] for row in value["schedule"] if row["batch"] == index}
        if batch["batch"] != index or batch["workers"] != COUNTS[index] or {row["call_id"] for row in batch["dispositions"]} != expected or len(batch["dispositions"]) != TASKS:
            raise ReplayMismatch("throughput batch denominator differs")
        if not math.isfinite(batch["wall_seconds"]) or batch["wall_seconds"] <= 0:
            raise ReplayMismatch("throughput batch time invalid")
        start, end = datetime.fromisoformat(batch["started_utc"]), datetime.fromisoformat(batch["finished_utc"])
        if start.tzinfo is None or end.tzinfo is None or end < start:
            raise ReplayMismatch("throughput batch UTC interval invalid")
        if abs((end-start).total_seconds()-batch["wall_seconds"]) > 1.0:
            raise ReplayMismatch("throughput monotonic and UTC duration disagree")
        if index and batch["started_utc"] < batches[index-1]["finished_utc"]:
            raise ReplayMismatch("throughput batches overlapped")
        subset = [call for call in calls if call["call_id"] in expected]
        subset_events = [event for event in events if event["call_id"] in expected]
        for event in subset_events:
            timestamp = event["payload"].get("admitted_utc", event["payload"].get("completed_utc", event["payload"].get("observed_utc")))
            if timestamp is None or not batch["started_utc"] <= timestamp <= batch["finished_utc"]:
                raise ReplayMismatch("throughput call outside its serial batch")
        by_key = {call["call_id"]: call for call in subset}
        for disposition in batch["dispositions"]:
            call = by_key.get(disposition["call_id"])
            expected_status = ("completed" if call and call["state"] == "completed" else
                               "unknown" if call and call.get("failure_scope") == "trajectory" else
                               "stopped_or_not_admitted")
            if disposition["status"] != expected_status:
                raise ReplayMismatch("throughput disposition disagrees with ledger")
        _, batch_peak = _metering(subset, subset_events, stop, manifest, {"workers": COUNTS[index], "live": True})
        batch_peaks.append({"batch": index, "workers": COUNTS[index], "peak_admitted_calls": batch_peak})
    if analyze(calls, batches) != read(output/"analysis.json"):
        raise ReplayMismatch("throughput analysis does not reproduce")
    return {"all_passed": True, "model_calls": 0, "calls_replayed": len(calls),
            "peak_admitted_calls": peak, "identical_prompts_verified": True,
            "serial_batches_verified": True, "batch_peaks": batch_peaks,
            "utc_duration_agreement_tolerance_seconds": 1.0, "source": "current frozen source"}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=["prepare", "launch", "audit"])
    parser.add_argument("--bundle", required=True, type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--live", action="store_true")
    args = parser.parse_args()
    if args.mode != "prepare" and args.output is None:
        parser.error("--output required")
    result = (prepare_probe(args.bundle) if args.mode == "prepare" else
              run_probe(args.bundle, args.output, live=args.live) if args.mode == "launch" else
              audit_probe(args.bundle, args.output))
    print(wire(result))


if __name__ == "__main__":
    main()
