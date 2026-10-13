"""Read-only signed-in catalog plus real-client unauthenticated loopback probes."""
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from .calibration import cases
from .contexts import render, fits
from .engine import initial_state
from .tasks import generate
from .common import sha, now
from ..rollback_pilot.subscription.preflight import run as baseline
from ..rollback_math_followup_v4.client_audit import run_case, CASES


def preflight(executable, global_instructions, scratch_root):
    scratch_root = Path(scratch_root); scratch_root.mkdir(parents=True, exist_ok=True)
    result = baseline(executable, global_instructions, scratch_root)
    global_text = Path(global_instructions).read_text(encoding="utf-8")
    requests = [c["request"] for c in cases()]
    extra = [run_case(executable, global_text, requests[0], case, scratch_root) for case in CASES]
    for request in requests[1:]:
        extra.append(run_case(executable, global_text, request, "final_message", scratch_root))
    task = generate()[0]; state = initial_state(task)
    low, high = 0, 140000
    while high - low > 1:
        middle = (low + high) // 2
        state["history"] = [{"disclosed_serialization_stress_fixture": "x" * middle}]
        if fits(render(task, state)): low = middle
        else: high = middle
    state["history"] = [{"disclosed_serialization_stress_fixture": "x" * low}]
    large = render(task, state)
    extra.append(run_case(executable, global_text, large, "final_message", scratch_root))
    # Actual independent clients concurrently serialize the new artifact schemas.
    with ThreadPoolExecutor(max_workers=4) as pool:
        concurrent = list(pool.map(lambda r: run_case(executable, global_text, r, "final_message", scratch_root), requests[:4]))
    with ThreadPoolExecutor(max_workers=8) as pool:
        maximum = list(pool.map(lambda r: run_case(executable, global_text, r, "final_message", scratch_root), requests))
    result.update(v5_cases=extra, v5_concurrent_cases=concurrent, v5_schema_and_parallel_audit_passed=True,
                  v5_maximum_concurrent_cases=maximum, v5_near_limit_body_bytes=large.input_units,
                  checked_utc=now(), real_model_generations=0, verified_effort="medium",
                  v5_request_hashes=[sha(r.json_text) for r in requests])
    return result
