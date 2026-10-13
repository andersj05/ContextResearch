"""Outcome-blind recovery selection and byte-preserving receipt import.

Selection uses admission ownership and terminal/interruption dispositions, never
quality scores, contrasts, or whether a particular arm is winning. Unknown
admissions retain their complete prior job and are never retried.
"""

from collections import Counter, defaultdict
from pathlib import Path

from experiments.dependency_memory.rollback_patch_v11.common import read, sha


SCHEMA = "rollback-v11-resume-selection-v1"
INTERRUPTED = {"infrastructure_stop", "unstarted_global_stop"}
UNSAFE_ERRORS = {"controller_error", "infrastructure_error"}


def calls_for_job(job, historical):
    return [call for call in historical
            if call["identity"]["task_id"] == job["task_id"]
            and call["identity"]["arm"] == job["arm"]]


def select_jobs(manifest, prior_execution, historical):
    """Return a reproducible plan without selecting on any treatment outcome.

    The result deliberately includes every original job. The unchanged dependency
    scheduler can run retained jobs as local byte-copy operations and release
    children through its original persistence barrier.
    """
    jobs = manifest["jobs"]
    if [row["job"] for row in prior_execution["jobs"]] != jobs:
        raise ValueError("prior job inventory or order differs")
    if len({job["job_id"] for job in jobs}) != len(jobs):
        raise ValueError("duplicate original job")
    prior = {row["job"]["job_id"]: row for row in prior_execution["jobs"]}
    jobs_by_owner = {(job["task_id"], job["arm"]): job for job in jobs}
    if len(jobs_by_owner) != len(jobs):
        raise ValueError("duplicate task/arm job")
    if len({call["call_id"] for call in historical}) != len(historical):
        raise ValueError("duplicate historical admission")
    by_job = defaultdict(list)
    for call in historical:
        if call["state"] not in {"completed", "unknown"}:
            raise ValueError("historical admissions must be drained")
        owner = (call["identity"]["task_id"], call["identity"]["arm"])
        if owner not in jobs_by_owner:
            raise ValueError("historical admission outside original jobs")
        by_job[jobs_by_owner[owner]["job_id"]].append(call)
    selected = {}

    def choose(job, decision, reason):
        owned = by_job[job["job_id"]]
        selected[job["job_id"]] = {
            "job_id": job["job_id"], "task_id": job["task_id"], "arm": job["arm"],
            "decision": decision, "reason": reason,
            "historical_call_ids": sorted(call["call_id"] for call in owned),
            "unknown_call_ids": sorted(call["call_id"] for call in owned if call["state"] == "unknown"),
            "prior_row_sha256": sha(prior[job["job_id"]]),
        }

    # Prefix decisions precede descendant decisions regardless of manifest order.
    for job in jobs:
        if job["arm"] != "prefix":
            continue
        result = prior[job["job_id"]]["result"]
        owned = by_job[job["job_id"]]
        if any(call["state"] == "unknown" for call in owned):
            choose(job, "retain", "preserved_unknown_admission")
        elif result.get("reason") in UNSAFE_ERRORS:
            raise ValueError("controller or unclassified infrastructure error is not a quota recovery")
        elif (result.get("reason") in INTERRUPTED
              or result.get("lesson_disposition") in INTERRUPTED):
            choose(job, "resume", "healthy_interrupted_prefix")
        elif result.get("reason") == "unknown_dispatch" or result.get("lesson_disposition") == "unknown_dispatch":
            raise ValueError("unknown prefix disposition lacks an unknown admission")
        elif type(result.get("eligible")) is not bool or not result.get("reason"):
            raise ValueError("prefix lacks a final or recoverable disposition")
        else:
            choose(job, "retain", "terminal_prefix")

    for job in jobs:
        if job["arm"] == "prefix":
            continue
        parent_id = job.get("depends_on")
        if parent_id not in selected or selected[parent_id]["arm"] != "prefix":
            raise ValueError("child lacks its original prefix")
        if selected[parent_id]["task_id"] != job["task_id"]:
            raise ValueError("child depends on another task")
        result = prior[job["job_id"]]["result"]
        parent = prior[parent_id]["result"]
        owned = by_job[job["job_id"]]
        disposition = result.get("disposition", "")
        if any(call["state"] == "unknown" for call in owned):
            choose(job, "retain", "preserved_unknown_admission")
        elif disposition in UNSAFE_ERRORS:
            raise ValueError("controller or unclassified infrastructure error is not a quota recovery")
        elif selected[parent_id]["decision"] == "resume":
            # Even a previously no-call child must receive the recovered parent.
            # Existing completed calls, if any, can only be receipt-replayed.
            choose(job, "resume", "recompute_after_resumed_prefix")
        elif not parent.get("eligible"):
            if owned:
                raise ValueError("ineligible retained prefix has admitted child calls")
            choose(job, "retain", "blocked_by_retained_ineligible_prefix")
        elif job["arm"].endswith("L") and parent.get("lesson") is None:
            if owned:
                raise ValueError("missing retained lesson has admitted lesson-arm calls")
            choose(job, "retain", "blocked_by_retained_unavailable_lesson")
        elif disposition in INTERRUPTED:
            choose(job, "resume", "healthy_interrupted_continuation")
        elif disposition == "unknown_dispatch":
            raise ValueError("unknown continuation disposition lacks an unknown admission")
        elif not disposition:
            raise ValueError("continuation lacks a final or recoverable disposition")
        else:
            choose(job, "retain", "terminal_continuation")

    planned = [selected[job["job_id"]] for job in jobs]
    return {"schema": SCHEMA, "jobs": planned,
            "counts": dict(Counter(row["decision"] for row in planned)),
            "reason_counts": dict(Counter(row["reason"] for row in planned)),
            "historical_admissions": len(historical),
            "unknown_admissions_preserved": sum(call["state"] == "unknown" for call in historical),
            "selection_uses_quality_scores": False}


def copy_exact(source, destination):
    source, destination = Path(source), Path(destination)
    data = source.read_bytes()
    destination.parent.mkdir(parents=True, exist_ok=True)
    with destination.open("xb") as stream:
        stream.write(data)
    if destination.read_bytes() != data:
        raise ValueError("historical evidence copy changed")
    return sha(data)


def copy_history(prior, output, historical):
    """Import all admitted envelopes, preserving even an unknown's saved reply."""
    prior, output = Path(prior), Path(output)
    admitted = {call["call_id"] for call in historical}
    completed = {call["call_id"] for call in historical if call["state"] == "completed"}
    requests = {path.stem for path in (prior / "requests").glob("*.json")}
    responses = {path.stem for path in (prior / "responses").glob("*.json")}
    if requests != admitted or not completed <= responses <= admitted:
        raise ValueError("historical receipt inventory differs from admissions")
    copies = []
    for directory in ("requests", "responses", "diagnostics"):
        for source in sorted((prior / directory).glob("*.json")):
            if source.stem not in admitted:
                raise ValueError("unadmitted historical receipt")
            relative = source.relative_to(prior)
            copies.append({"prior_path": relative.as_posix(), "path": relative.as_posix(),
                           "sha256": copy_exact(source, output / relative)})
    for name in ("execution.json", "manifest.json", "accounting.json", "evidence_manifest.json",
                 "scheduler_trace.json", "preflight.json"):
        source = prior / name
        if source.is_file():
            destination = output / ("prior_" + name)
            copies.append({"prior_path": name, "path": destination.name,
                           "sha256": copy_exact(source, destination)})
    return {"files": copies, "receipt_bytes_preserved": True,
            "scope": "Original admitted requests, saved responses and diagnostics copied byte-for-byte; no old ledger identity is dispatched again."}
