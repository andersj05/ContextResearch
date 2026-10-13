"""Independently verify scheduler coverage, bounds and persisted dependencies."""
import math


def verify_trace(trace, jobs, workers):
    def require(ok, reason):
        if not ok:
            raise ValueError("scheduler_trace:" + reason)

    by_id = {job["job_id"]: job for job in jobs}
    rank = {job["job_id"]: index for index, job in enumerate(jobs)}
    require(trace["schema"] == "rollback-v8-dependency-scheduler-trace-v1", "schema")
    require(trace["policy"] == "ready continuations before unstarted prefixes; frozen manifest rank within each category", "policy")
    require(trace["workers"] == workers and trace["jobs_total"] == len(jobs)
            and trace["jobs_completed"] == len(jobs), "denominator")
    states, times = {key: [] for key in by_id}, {key: {} for key in by_id}
    remaining = {key for key, job in by_id.items() if job["arm"] == "prefix"}
    outstanding, active, completed = set(), set(), []
    peak_active = peak_outstanding = early = 0
    previous = 0.0
    flags = {}
    for event in trace["events"]:
        key, kind, seconds = event["job_id"], event["event"], event["seconds"]
        require(key in by_id and kind in {"submit", "start", "finish", "persisted"}, "event_identity")
        require(type(seconds) in (int, float) and math.isfinite(seconds)
                and seconds >= previous, "event_time")
        previous = seconds
        expected = ("submit", "start", "finish", "persisted")
        require(len(states[key]) < 4 and kind == expected[len(states[key])], "event_order")
        states[key].append(kind)
        times[key][kind] = seconds
        job = by_id[key]
        if kind == "submit":
            parent = job.get("depends_on")
            require(parent is None or "persisted" in states[parent], "unpersisted_parent")
            available = [candidate for candidate in jobs
                         if (not states[candidate["job_id"]] or candidate["job_id"] == key)
                         and (candidate.get("depends_on") is None
                              or "persisted" in states[candidate["depends_on"]])]
            expected_job = min(available, key=lambda candidate: (candidate["arm"] == "prefix", rank[candidate["job_id"]]))
            require(key == expected_job["job_id"], "ready_priority_or_frozen_rank")
            outstanding.add(key)
            peak_outstanding = max(peak_outstanding, len(outstanding))
        elif kind == "start":
            active.add(key)
            peak_active = max(peak_active, len(active))
            flags[key] = job["arm"] != "prefix" and bool(remaining)
            early += int(flags[key])
            require(event["active_jobs"] == len(active)
                    and event["prefixes_not_persisted"] == len(remaining), "start_counts")
        elif kind == "finish":
            require(key in active, "inactive_finish")
            active.remove(key)
            require(event["active_jobs"] == len(active), "finish_counts")
        else:
            outstanding.remove(key)
            if job["arm"] == "prefix":
                remaining.remove(key)
            completed.append(key)
            require(event["prefixes_not_persisted"] == len(remaining), "persisted_counts")
    require(not active and not outstanding and not remaining, "unfinished")
    require(all(len(value) == 4 for value in states.values()), "missing_job")
    require(peak_active <= workers and peak_outstanding <= workers, "worker_limit")
    require(trace["peak_active_workers"] == peak_active
            and trace["max_outstanding"] == peak_outstanding
            and trace["continuation_started_before_all_prefixes_persisted"] == early,
            "summary_counts")
    require(trace["completion_order"] == completed, "completion_order")
    require([row["job_id"] for row in trace["jobs"]] == [job["job_id"] for job in jobs], "row_order")
    for rank, row in enumerate(trace["jobs"]):
        key = row["job_id"]
        job = by_id[key]
        require(row["task_id"] == job["task_id"] and row["arm"] == job["arm"]
                and row["depends_on"] == job.get("depends_on") and row["rank"] == rank,
                "row_identity")
        for field, event in (("submitted_seconds", "submit"), ("started_seconds", "start"),
                             ("finished_seconds", "finish"), ("completed_seconds", "persisted")):
            require(row[field] == times[key][event], "row_time")
        require(row["started_before_all_prefixes_persisted"] is flags[key], "row_early_flag")
    require(type(trace["wall_seconds"]) in (int, float) and math.isfinite(trace["wall_seconds"])
            and trace["wall_seconds"] >= previous, "wall_time")
    return {"passed": True, "jobs": len(jobs), "peak_active_jobs": peak_active,
            "peak_outstanding_jobs": peak_outstanding,
            "continuations_started_before_all_prefixes_persisted": early}
