"""Bounded dependency scheduling for shared prefixes and paired continuations.

Only the coordinator submits work and publishes completed parents. Workers
never submit or wait on child jobs. A ready continuation has priority over an
unstarted prefix; frozen manifest order breaks ties inside either category.
This removes the global prefix barrier without changing any task context.

The callback is an evidence boundary: ``on_completed(future, job)`` must save
the result and publish the prefix before returning. It owns model/controller
error policy and must set the caller's global stop before raising a persistence
or invariant error. No descendant is released if that callback raises.
"""

from collections import defaultdict, deque
from concurrent.futures import FIRST_COMPLETED, ThreadPoolExecutor, wait
import heapq
import threading
import time


MAX_WORKERS = 32
TRACE_SCHEMA = "rollback-v9-dependency-scheduler-trace-v1"


def _validated(jobs, workers):
    if type(workers) is not int or not 1 <= workers <= MAX_WORKERS:
        raise ValueError("one through thirty-two workers required")
    jobs = list(jobs)
    by_id, by_task = {}, defaultdict(dict)
    for job in jobs:
        if not isinstance(job, dict):
            raise ValueError("job must be a dictionary")
        job_id, task_id, arm = (job.get(key) for key in ("job_id", "task_id", "arm"))
        if not isinstance(job_id, str) or not job_id or job_id in by_id:
            raise ValueError("unique nonempty job identities required")
        if not isinstance(task_id, str) or not task_id or arm not in {"prefix", "K0", "R0", "KL", "RL"}:
            raise ValueError("task identity and prefix/factorial arm required")
        if arm in by_task[task_id]:
            raise ValueError("one job per task and arm required")
        by_id[job_id] = job
        by_task[task_id][arm] = job
    for task_jobs in by_task.values():
        if set(task_jobs) not in ({"prefix", "K0"}, {"prefix", "K0", "R0", "KL", "RL"}):
            raise ValueError("each task requires its frozen calibration or factorial arms")
        prefix_id = task_jobs["prefix"]["job_id"]
        if task_jobs["prefix"].get("depends_on") is not None:
            raise ValueError("a prefix must not depend on another job")
        if any(task_jobs[arm].get("depends_on") != prefix_id for arm in task_jobs if arm != "prefix"):
            raise ValueError("continuations must depend on their own prefix")
    return jobs, by_id


def execute(jobs, work, on_completed, workers, *, on_submitted=None):
    """Execute every frozen job once and return an outcome-free timing trace.

    ``work(job)`` runs inside the worker pool. Its return value (or exception)
    belongs to ``on_completed(future, job)``, called on the coordinator thread.
    That callback returns only after the parent is durably saved, its contract
    checked, and its state published. The scheduler never examines a score or
    eligibility: ineligible continuations still execute their explicit no-call
    disposition path, while the caller's ledger blocks global-stop admissions.

    At most ``workers`` futures exist at a time. ``on_submitted(job)``, when
    supplied, is a coordinator notification after submission, not an admission
    or generation hook. Exceptions in callbacks fail closed for descendants
    and propagate after already-running workers drain; callers own global stop.
    """
    jobs, by_id = _validated(jobs, workers)
    rank = {job["job_id"]: index for index, job in enumerate(jobs)}
    prefixes = deque(job for job in jobs if job["arm"] == "prefix")
    children = defaultdict(list)
    for job in jobs:
        if job["arm"] != "prefix":
            children[job["depends_on"]].append(job)

    started = time.monotonic()
    lock = threading.Lock()
    events, completion_order, rows = [], [], {}
    remaining_prefixes = {job["job_id"] for job in prefixes}
    active = peak_active = early_continuations = 0
    max_outstanding = max_ready_continuations = 0

    def event(kind, job_id, **fields):
        # All callers hold lock, which also orders the timestamp/event sequence.
        seconds = time.monotonic() - started
        events.append({"event": kind, "seconds": seconds,
                       "job_id": job_id, **fields})
        return seconds

    def worker(job):
        nonlocal active, peak_active, early_continuations
        job_id = job["job_id"]
        with lock:
            active += 1
            peak_active = max(peak_active, active)
            earlier_than_all_prefixes = job["arm"] != "prefix" and bool(remaining_prefixes)
            early_continuations += int(earlier_than_all_prefixes)
            rows[job_id]["started_seconds"] = event(
                "start", job_id, active_jobs=active,
                prefixes_not_persisted=len(remaining_prefixes))
            rows[job_id]["started_before_all_prefixes_persisted"] = earlier_than_all_prefixes
        returned = False
        try:
            result = work(job)
            returned = True
            return result
        finally:
            with lock:
                active -= 1
                rows[job_id]["finished_seconds"] = event(
                    "finish", job_id, active_jobs=active, work_returned=returned)

    ready, pending = [], {}
    with ThreadPoolExecutor(max_workers=workers, thread_name_prefix="rollback-v9") as pool:
        while prefixes or ready or pending:
            while len(pending) < workers and (ready or prefixes):
                if ready:
                    _, job_id = heapq.heappop(ready)
                    job = by_id[job_id]
                else:
                    job = prefixes.popleft()
                    job_id = job["job_id"]
                with lock:
                    rows[job_id] = {
                        "job_id": job_id, "task_id": job["task_id"],
                        "arm": job["arm"], "depends_on": job.get("depends_on"),
                        "rank": rank[job_id],
                        "submitted_seconds": event("submit", job_id),
                    }
                future = pool.submit(worker, job)
                pending[future] = job
                max_outstanding = max(max_outstanding, len(pending))
                if on_submitted is not None:
                    on_submitted(job)
            done, _ = wait(pending, return_when=FIRST_COMPLETED)
            # Several completions may already be visible together. Persist that
            # set in manifest order before applying the ready-continuation rule.
            for future in sorted(done, key=lambda item: rank[pending[item]["job_id"]]):
                job = pending.pop(future)
                job_id = job["job_id"]
                on_completed(future, job)
                with lock:
                    if job["arm"] == "prefix":
                        remaining_prefixes.remove(job_id)
                    rows[job_id]["completed_seconds"] = event(
                        "persisted", job_id, prefixes_not_persisted=len(remaining_prefixes))
                    completion_order.append(job_id)
                for child in children[job_id]:
                    heapq.heappush(ready, (rank[child["job_id"]], child["job_id"]))
                max_ready_continuations = max(max_ready_continuations, len(ready))

    return {
        "schema": TRACE_SCHEMA,
        "policy": "ready continuations before unstarted prefixes; frozen manifest rank within each category",
        "workers": workers, "jobs_total": len(jobs), "jobs_completed": len(completion_order),
        "max_outstanding": max_outstanding, "peak_active_workers": peak_active,
        "maximum_ready_continuations": max_ready_continuations,
        "continuation_started_before_all_prefixes_persisted": early_continuations,
        "wall_seconds": time.monotonic() - started,
        "jobs": [rows[job["job_id"]] for job in jobs],
        "completion_order": completion_order, "events": events,
    }
