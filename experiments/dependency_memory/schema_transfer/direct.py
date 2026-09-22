"""Explicit per-family direct records: strong authored control, never extractor input."""
from __future__ import annotations

from time import perf_counter_ns

from .casebook import CHILD_CAP, PARENT_CAP, compact
from .memory import encode, select

PATHS = {
    "escrow": ("invoice_id", "current_receipt", "authorization.for_receipt", "authorization.state"),
    "package": ("package_id", "release_digest", "scan.subject_digest", "scan.state",
                "signature.subject_digest", "signature.state"),
    "retry_queue": ("request_token", "dispatch.attempt_uuid", "dispatch.state",
                    "result.attempt_uuid", "result.state", "billing.for_attempt",
                    "billing.state", "retry_policy.retry_allowed"),
    "ci_promotion": ("deployment_slot", "build.digest", "build.channel",
                     "authorization.approved_digest", "authorization.state",
                     "verification.subject", "verification.unit", "verification.integration",
                     "handoff.environment"),
    "data_pipeline": ("pipeline_run", "extract.output_dataset", "extract.state",
                      "transform.input_dataset", "transform.output_dataset", "transform.state",
                      "load.input_dataset", "load.output_dataset", "load.state",
                      "quality.subject_dataset", "quality.state",
                      "consent.approved_output", "consent.state"),
}


def project(family, records, *, cap=PARENT_CAP):
    start = perf_counter_ns()
    memory = encode(list(PATHS[family]), records)
    if len(memory.encode()) > cap:
        raise ValueError("Authored direct projection exceeds cap")
    return memory, {"cpu_ns": perf_counter_ns() - start,
                    "source_bytes_read": len(compact(records).encode()),
                    "memory_bytes_written": len(memory.encode())}


def child(memory, candidates, *, cap=CHILD_CAP):
    return select(memory, candidates, cap=cap)
