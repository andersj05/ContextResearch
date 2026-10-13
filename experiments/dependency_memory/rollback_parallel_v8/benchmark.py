"""Offline scheduling diagnostics from sealed, already completed model work.

The deterministic replay holds each job's measured first-admission-to-last-
completion span fixed. It is a counterfactual scheduler calculation, not a live
provider speedup measurement. An optional scaled sleep workload exercises the
new executable scheduler without contacting a provider.
"""
from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
from contextlib import closing
from datetime import datetime
from hashlib import sha256
import heapq
import json
import math
from pathlib import Path
import sqlite3
import statistics
import threading
import time


def _read(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def _digest(path):
    return sha256(Path(path).read_bytes()).hexdigest()


def _overlap(start, end, interval):
    return max(0.0, min(end, interval[1]) - max(start, interval[0]))


def _peak(intervals):
    events = sorted((point, delta) for start, end in intervals if end > start
                    for point, delta in ((start, 1), (end, -1)))
    active = peak = 0
    for _, delta in events:
        active += delta
        peak = max(peak, active)
    if active:
        raise ValueError("unbalanced timing intervals")
    return peak


def _summary(values):
    return ({"min": min(values), "median": statistics.median(values),
             "max": max(values), "sum": sum(values)} if values else None)


def _validate_nodes(nodes):
    by_id = {node["job_id"]: node for node in nodes}
    if len(by_id) != len(nodes):
        raise ValueError("duplicate job identity")
    for node in nodes:
        duration = node["duration_seconds"]
        if not isinstance(duration, (float, int)) or not math.isfinite(duration) or duration < 0:
            raise ValueError("job duration must be finite and nonnegative")
        dependency = node.get("depends_on")
        if node["arm"] == "prefix":
            if dependency is not None:
                raise ValueError("prefix cannot depend on another job")
        elif node["arm"] in {"K", "R"}:
            parent = by_id.get(dependency)
            if not parent or parent["arm"] != "prefix" or parent["task_id"] != node["task_id"]:
                raise ValueError("continuation must depend on its own prefix")
        else:
            raise ValueError("unknown job arm")
    return by_id


def load_recorded_workload(folder):
    """Read-only import of a sealed, entirely known v7 run's timing evidence.

    The service proxy contains local gaps *within* each trajectory, but cannot
    capture work performed before its first admission or after its last saved
    completion. Zero-call dispositions have zero service time in the replay.
    """
    folder = Path(folder)
    evidence = _read(folder / "evidence_manifest.json")
    sealed = {item["path"]: item["sha256"] for item in evidence["files"]}
    bound = {}
    for name in ("accounting.json", "manifest.json", "execution.json", "run_settings.json"):
        digest = _digest(folder / name)
        if sealed.get(name) != digest:
            raise ValueError("timing source does not match evidence seal: " + name)
        bound[name] = digest
    ledger_path = folder / "ledger.sqlite"
    if _digest(ledger_path) != evidence["ledger_sha256"]:
        raise ValueError("timing ledger does not match evidence seal")
    bound["ledger.sqlite"] = evidence["ledger_sha256"]
    bound["evidence_manifest.json"] = _digest(folder / "evidence_manifest.json")
    accounting = _read(folder / "accounting.json")
    manifest = _read(folder / "manifest.json")
    execution = _read(folder / "execution.json")
    settings = _read(folder / "run_settings.json")
    workers = settings["workers"]
    if accounting["stop"] or any(call["state"] != "completed" for call in accounting["calls"]):
        raise ValueError("this timing replay requires a completed run with no unknown calls")
    if not accounting["calls"]:
        raise ValueError("no recorded calls to replay")
    with closing(sqlite3.connect(ledger_path.resolve().as_uri() + "?mode=ro", uri=True)) as connection:
        event_rows = connection.execute("SELECT call_id,state,payload FROM events ORDER BY seq").fetchall()
    admitted, completed = {}, {}
    for call_id, state, payload in event_rows:
        if state not in {"dispatched", "completed"}:
            raise ValueError("unexpected ledger event in completed timing source")
        target = admitted if state == "dispatched" else completed
        if call_id in target:
            raise ValueError("duplicate ledger event identity")
        target[call_id] = json.loads(payload)
    calls_by_id = {call["call_id"]: call for call in accounting["calls"]}
    if set(admitted) != set(completed) or set(admitted) != set(calls_by_id):
        raise ValueError("ledger and accounting call identities differ")
    origin = min(datetime.fromisoformat(row["admitted_utc"]) for row in admitted.values())
    grouped = {}
    call_intervals = []
    for call_id, call in calls_by_id.items():
        if completed[call_id]["completed_utc"] != call["completed_utc"]:
            raise ValueError("ledger and accounting completion timestamps differ")
        start = (datetime.fromisoformat(admitted[call_id]["admitted_utc"]) - origin).total_seconds()
        end = (datetime.fromisoformat(call["completed_utc"]) - origin).total_seconds()
        if start > end:
            raise ValueError("negative measured call interval")
        identity = call["identity"]
        grouped.setdefault((identity["task_id"], identity["arm"]), []).append((start, end))
        call_intervals.append((start, end))
    nodes = []
    for job in manifest["jobs"]:
        intervals = grouped.pop((job["task_id"], job["arm"]), [])
        start = min((row[0] for row in intervals), default=None)
        end = max((row[1] for row in intervals), default=None)
        nodes.append(dict(job, duration_seconds=0.0 if not intervals else end - start,
                          call_count=len(intervals), observed_start_seconds=start,
                          observed_end_seconds=end))
    if grouped:
        raise ValueError("calls have no corresponding frozen job")
    by_id = _validate_nodes(nodes)
    nonzero = [node for node in nodes if node["call_count"]]
    job_intervals = [(node["observed_start_seconds"], node["observed_end_seconds"]) for node in nonzero]
    envelope = max(end for _, end in call_intervals)
    phase_details = {}
    for name, selection in (("prefix", [node for node in nonzero if node["arm"] == "prefix"]),
                            ("continuation", [node for node in nonzero if node["arm"] != "prefix"])):
        if not selection:
            continue
        intervals = [(node["observed_start_seconds"], node["observed_end_seconds"]) for node in selection]
        first = min(start for start, _ in intervals)
        last = max(end for _, end in intervals)
        tail_start = max(start for start, _ in intervals)
        busy = sum(end - start for start, end in intervals)
        tail_busy = sum(_overlap(tail_start, last, interval) for interval in intervals)
        phase_details[name] = {
            "jobs_with_calls": len(selection), "start_seconds": first, "end_seconds": last,
            "wall_seconds": last - first, "job_span_busy_worker_seconds": busy,
            "job_span_utilization": busy / (workers * (last - first)),
            "idle_worker_seconds": workers * (last - first) - busy,
            "last_job_started_seconds": tail_start, "tail_wall_seconds": last - tail_start,
            "tail_idle_worker_seconds": workers * (last - tail_start) - tail_busy,
        }
    prefix_end = phase_details["prefix"]["end_seconds"]
    barrier_wait = [max(0.0, prefix_end - by_id[node["depends_on"]]["observed_end_seconds"])
                    for node in nonzero if node["arm"] != "prefix"]
    busy_jobs = sum(node["duration_seconds"] for node in nodes)
    admitted_span = sum(end - start for start, end in call_intervals)
    measured_elapsed = sum(call["elapsed_seconds"] for call in calls_by_id.values())
    return {
        "evidence_kind": "offline_timing_diagnostic_of_completed_live_run",
        "source_directory": folder.as_posix(), "source_sha256": bound,
        "source_time_origin_utc": origin.isoformat(), "jobs": nodes,
        "observed": {
            "workers": workers, "calls": len(calls_by_id), "jobs": len(nodes),
            "jobs_with_calls": len(nonzero), "zero_call_dispositions": len(nodes) - len(nonzero),
            "controller_wall_seconds": execution["wall_seconds"],
            "admission_to_completion_envelope_seconds": envelope,
            "summed_call_elapsed_seconds": measured_elapsed,
            "summed_admitted_interval_seconds": admitted_span,
            "summed_job_span_seconds": busy_jobs,
            "job_span_utilization": busy_jobs / (workers * envelope),
            "admitted_call_utilization": admitted_span / (workers * envelope),
            "peak_admitted_calls": _peak(call_intervals),
            "peak_jobs_with_calls": _peak(job_intervals),
            "intra_job_outside_admitted_interval_worker_seconds": busy_jobs - admitted_span,
            "intra_job_span_minus_call_elapsed_worker_seconds": busy_jobs - measured_elapsed,
            "phase_details": phase_details,
            "per_continuation_prefix_phase_barrier_wait_seconds": _summary(barrier_wait),
            "barrier_wait_interpretation": "Dependency-ready time forbidden by the phase barrier; queued waits are not additive recoverable wall time.",
            "unmeasured_attribution": "No instrumented split of source hashing, serialization, local process setup or provider latency; call elapsed includes multiple components.",
        },
    }


def simulate(nodes, workers, *, policy="pipeline"):
    """Deterministic, nonpreemptive list scheduling with fixed service times.

    Pipeline chooses ready continuations first, then frozen manifest rank.
    Two-phase chooses manifest-ranked prefixes, waits for all prefixes, then
    manifest-ranked continuations. Both include every frozen zero-call job.
    """
    if type(workers) is not int or workers < 1:
        raise ValueError("positive worker count required")
    if policy not in {"pipeline", "two_phase"}:
        raise ValueError("unknown scheduling policy")
    _validate_nodes(nodes)
    pending = dict(enumerate(nodes))
    done = set()
    running = []
    trace = []
    current = 0.0
    all_prefixes = {node["job_id"] for node in nodes if node["arm"] == "prefix"}
    peak = 0
    while pending or running:
        while running and running[0][0] <= current:
            finish, rank, start = heapq.heappop(running)
            node = nodes[rank]
            done.add(node["job_id"])
            trace.append({"job_id": node["job_id"], "arm": node["arm"],
                          "start_seconds": start, "finish_seconds": finish,
                          "duration_seconds": node["duration_seconds"]})
        eligible = [(rank, node) for rank, node in pending.items()
                    if node.get("depends_on") is None or node["depends_on"] in done]
        if policy == "two_phase" and not all_prefixes.issubset(done):
            eligible = [(rank, node) for rank, node in eligible if node["arm"] == "prefix"]
        eligible.sort(key=lambda item: ((item[1]["arm"] == "prefix") if policy == "pipeline" else False,
                                        item[0]))
        for rank, node in eligible[:workers - len(running)]:
            del pending[rank]
            heapq.heappush(running, (current + node["duration_seconds"], rank, current))
        peak = max(peak, sum(end > start for end, _, start in running))
        if running:
            current = running[0][0]
        elif pending:
            raise ValueError("unresolved dependency graph")
    busy = sum(node["duration_seconds"] for node in nodes)
    return {
        "evidence_kind": "offline_fixed_service_time_counterfactual",
        "policy": policy, "workers": workers, "makespan_seconds": current,
        "busy_worker_seconds": busy, "idle_worker_seconds": workers * current - busy,
        "utilization": busy / (workers * current) if current else 0.0,
        "peak_active_jobs": peak, "trace": trace,
    }


def compare_recorded(workload, worker_counts=(8, 16, 32)):
    comparisons = [simulate(workload["jobs"], workers, policy=policy)
                   for workers in worker_counts for policy in ("two_phase", "pipeline")]
    baseline = simulate(workload["jobs"], workload["observed"]["workers"], policy="two_phase")
    for result in comparisons:
        result["speedup_vs_replayed_original_policy"] = baseline["makespan_seconds"] / result["makespan_seconds"]
        result["seconds_saved_vs_replayed_original_policy"] = baseline["makespan_seconds"] - result["makespan_seconds"]
    observed = workload["observed"]["controller_wall_seconds"]
    return {
        "evidence_kind": "offline_fixed_service_time_counterfactual",
        "model_calls": 0, "source_sha256": workload["source_sha256"],
        "observed": workload["observed"], "jobs": workload["jobs"], "comparisons": comparisons,
        "baseline_replay_vs_observed_controller_seconds": {
            "replay": baseline["makespan_seconds"], "observed": observed,
            "observed_minus_replay": observed - baseline["makespan_seconds"],
        },
        "assumptions_and_limits": [
            "Every comparison holds the same recorded per-job first-admission-to-last-completion duration fixed.",
            "The calculation does not model concurrency-dependent provider throttling, latency, cache behavior, failures or changed model outcomes.",
            "Job service spans include local gaps between their calls; pre-admission and post-completion job work is uninstrumented and zero-call dispositions are assigned zero duration.",
            "The replay is not a new model observation or a measured live speedup; its original-policy discrepancy describes its timing approximation.",
            "Ready continuations precede queued prefixes; frozen manifest rank breaks ties. Actual asynchronous completion order may differ.",
        ],
    }


def sleep_workload(nodes, workers, *, policy="pipeline", time_scale=0.001):
    """Run a tiny timed local workload on the executable scheduler; no models.

    Sleeping stands in for fixed recorded service time. This measures the local
    scheduler on an artificial I/O-like workload, not model throughput. The
    two-phase control uses ThreadPoolExecutor with the v7 phase barrier.
    """
    _validate_nodes(nodes)
    if type(workers) is not int or workers < 1 or not math.isfinite(time_scale) or time_scale <= 0:
        raise ValueError("positive workers and finite time scale required")
    if policy not in {"pipeline", "two_phase"}:
        raise ValueError("unknown scheduling policy")
    jobs = [{key: node[key] for key in ("job_id", "task_id", "arm", "depends_on") if key in node}
            for node in nodes]
    durations = {node["job_id"]: node["duration_seconds"] * time_scale for node in nodes}
    lock = threading.Lock()
    persisted = set()
    intervals = {}
    active = peak = 0
    start = time.monotonic()

    def work(job):
        nonlocal active, peak
        with lock:
            if job.get("depends_on") and job["depends_on"] not in persisted:
                raise AssertionError("child began before parent persistence")
            active += 1
            peak = max(peak, active)
            job_start = time.monotonic() - start
        time.sleep(durations[job["job_id"]])
        with lock:
            intervals[job["job_id"]] = (job_start, time.monotonic() - start)
            active -= 1
        return job["job_id"]

    def complete(future, job):
        if future.result() != job["job_id"]:
            raise AssertionError("wrong workload result")
        with lock:
            if job["job_id"] in persisted:
                raise AssertionError("job persisted twice")
            persisted.add(job["job_id"])

    if policy == "pipeline":
        from .scheduler import execute
        scheduler_trace = execute(jobs, work, complete, workers)
    else:
        with ThreadPoolExecutor(max_workers=workers) as pool:
            for prefix_phase in (True, False):
                futures = {pool.submit(work, job): job for job in jobs
                           if (job["arm"] == "prefix") == prefix_phase}
                for future in as_completed(futures):
                    complete(future, futures[future])
        scheduler_trace = None
    wall = time.monotonic() - start
    if len(persisted) != len(jobs) or peak > workers:
        raise AssertionError("incomplete or over-capacity local workload")
    return {
        "evidence_kind": "executed_local_scaled_sleep_workload",
        "model_calls": 0, "policy": policy, "workers": workers,
        "time_scale": time_scale, "wall_seconds": wall, "jobs_completed": len(persisted),
        "peak_active_workers": peak,
        "requested_sleep_worker_seconds": sum(durations.values()),
        "observed_busy_worker_seconds": sum(end - begin for begin, end in intervals.values()),
        "dependency_persistence_checked": True, "at_most_once_checked": True,
        "intervals": {key: {"start_seconds": value[0], "end_seconds": value[1]}
                      for key, value in sorted(intervals.items())},
        "scheduler_trace": scheduler_trace,
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--workers", nargs="+", type=int, default=[8, 16, 32])
    parser.add_argument("--sleep-repeats", type=int, default=0)
    parser.add_argument("--time-scale", type=float, default=0.001)
    args = parser.parse_args(argv)
    if args.output.exists():
        parser.error("output already exists; preserve prior measurements")
    if args.sleep_repeats < 0:
        parser.error("sleep repeats must be nonnegative")
    workload = load_recorded_workload(args.source)
    report = compare_recorded(workload, args.workers)
    executions = []
    for repeat in range(args.sleep_repeats):
        # Alternate condition order to reduce a simple warm-up/order artifact.
        conditions = [(workers, policy) for workers in args.workers for policy in ("two_phase", "pipeline")]
        if repeat % 2:
            conditions.reverse()
        for workers, policy in conditions:
            execution = sleep_workload(workload["jobs"], workers, policy=policy, time_scale=args.time_scale)
            execution["repeat"] = repeat + 1
            executions.append(execution)
    report["executed_local_sleep_workloads"] = executions
    if executions:
        report["local_sleep_summary"] = [
            {"workers": workers, "policy": policy,
             "wall_seconds": _summary([row["wall_seconds"] for row in executions
                                       if row["workers"] == workers and row["policy"] == policy])}
            for workers in args.workers for policy in ("two_phase", "pipeline")]
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("x", encoding="utf-8", newline="\n") as handle:
        json.dump(report, handle, sort_keys=True, indent=2, ensure_ascii=False, allow_nan=False)
        handle.write("\n")
    print(json.dumps({"output": str(args.output), "model_calls": 0,
                      "comparisons": [{key: value for key, value in row.items() if key != "trace"}
                                      for row in report["comparisons"]],
                      "local_workloads": len(executions)}, sort_keys=True))


if __name__ == "__main__":
    main()
