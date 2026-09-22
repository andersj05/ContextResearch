"""Hand-written field selections for the authored direct-record control."""
from __future__ import annotations

from time import perf_counter_ns

from experiments.dependency_memory.schema_transfer import memory as base
from .casebook import CHILD_CAP, PARENT_CAP, compact
from .memory import join

# Explicit field choices are only used by this control, never by the extractor.
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


def project(family, tool_schemas, tool_results, *, cap=PARENT_CAP):
    start = perf_counter_ns()
    _, rows = join(tool_schemas, tool_results)
    result = base.encode(list(PATHS[family]), rows)
    if len(result.encode()) > cap:
        raise ValueError("Hand-written parent exceeds cap")
    return result, {"cpu_ns": perf_counter_ns() - start,
                    "source_bytes_read": len(compact(tool_schemas).encode()) + len(compact(tool_results).encode()),
                    "memory_bytes_written": len(result.encode())}


def child(parent, candidates, *, cap=CHILD_CAP):
    return base.select(parent, candidates, cap=cap)
