"""First submissions remaining after the documented transfer quota stop.

Offline by default. Historical evidence stays immutable; a new phase consumes
only the residual case and credit allocation certified from finalized runs.
"""
from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from decimal import Decimal
import hashlib
import json
from pathlib import Path
import sys
import tempfile
import threading

from luna_appserver import AppServer, LunaClient, MODEL, PROVIDER_OVERRIDES, TransportError
from luna_budget import CreditBudget
from luna_isolation import ISOLATION_OVERRIDES
from run_revision_diagnostic import atomic_json
from transfer_interface import VERSION as REQUEST_VERSION
import run_transfer_study as runner
import transfer_study as study

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
from prepare_transfer_continuation import prepare_continuation, public_schedule

VERSION = "transfer_continuation_run_v1"
PLAN_VERSION = "transfer_continuation_launch_v1"
EXTRA_SOURCES = (
    "docs/TRANSFER_CONTINUATION.md",
    "scripts/prepare_transfer_continuation.py",
    "scripts/test_prepare_transfer_continuation.py",
    "scripts/audit_transfer_run.py",
    "scripts/audit_transfer_continuation.py",
    "scripts/test_audit_transfer_continuation.py",
)


class ContinuationCreditBudget(CreditBudget):
    ATTEMPT_LIMIT = 384

    def __init__(self, worker_certificate):
        super().__init__(worker_certificate["remaining_credit_equivalent_cap_exact"],
                         worker_certificate["remaining_model_attempt_cap"])


def relative_directory(path):
    return Path(path).resolve().relative_to(ROOT).as_posix()


def make_launch_plan(prior_dirs):
    directories = [ROOT / relative_directory(path) for path in prior_dirs]
    certificate = prepare_continuation(directories)
    original = json.loads((directories[0] / "manifest.json").read_text(encoding="utf-8"))["plan"]
    current = study.make_plan()
    if public_schedule(current) != public_schedule(original) or any(
        a["request"] != b["request"] for a, b in zip(current["cases"], original["cases"])
    ):
        raise ValueError("Public requests or original schedule changed")
    sources = dict(current["source_sha256"])
    for name in EXTRA_SOURCES:
        sources[name] = hashlib.sha256((ROOT / name).read_bytes()).hexdigest()
    return {"version": PLAN_VERSION, "original_plan": original,
            "certificate": certificate,
            "prior_run_dirs": [relative_directory(path) for path in directories],
            "source_sha256": sources}


def eligible_cases(plan, worker):
    certificate = plan["certificate"]["workers"][worker]
    ids = certificate["eligible_case_ids"]
    by_id = {case["case_id"]: case for case in plan["original_plan"]["cases"]}
    cases = [by_id[case_id] for case_id in ids]
    if any(case["worker"] != worker for case in cases) or len(cases) != certificate["remaining_model_attempt_cap"]:
        raise ValueError("Certificate worker schedule does not reconcile")
    return cases


def prepare_clients(args, plan):
    if args.executable is None or not args.authorization or not args.authorization.strip():
        raise ValueError("Live continuation requires executable and explicit allocation note")
    if plan != make_launch_plan([ROOT / path for path in plan["prior_run_dirs"]]):
        raise ValueError("Continuation source or finalized evidence changed after freeze")
    commit = runner.source_commit(plan)
    audit_path = ROOT / "experiments/dependency_memory/results/transfer_transport_audit.json"
    audit_bytes = audit_path.read_bytes()
    if hashlib.sha256(audit_bytes).hexdigest() != plan["source_sha256"][audit_path.relative_to(ROOT).as_posix()]:
        raise ValueError("Wire audit changed")
    audit = json.loads(audit_bytes)
    if audit.get("public_request_contract") != REQUEST_VERSION or not audit.get("launch_ready"):
        raise ValueError("The reviewed wire audit must cover the transfer request contract")
    clients = [LunaClient(args.executable, audit, budget=ContinuationCreditBudget(row),
                         quota_used_limit=100, credit_backed_quota=True)
               for row in plan["certificate"]["workers"]]
    with tempfile.TemporaryDirectory(prefix="contextresearch-continuation-catalog-") as cwd:
        server = AppServer(args.executable, cwd, (*ISOLATION_OVERRIDES, *PROVIDER_OVERRIDES))
        try:
            server.initialize()
            catalog = server.rpc("model/list", {"includeHidden": True, "limit": 100})
            matches = [row for row in catalog.get("data", []) if row.get("model") == MODEL]
            if len(matches) != 1 or matches[0].get("hidden") is True:
                raise TransportError("requested_model_not_available")
        finally:
            server.close()
    for worker, client in enumerate(clients):
        client.metadata.update(worker=worker, experiment_version=VERSION,
            approved_original_plan_sha256=runner._hash(plan["original_plan"]),
            approved_plan_sha256=runner._hash(plan),
            approved_continuation_sha256=runner._hash(plan),
            source_sha256=plan["source_sha256"], advertised_model=matches[0],
            advertised_model_sha256=runner._hash(matches[0]), source_commit=commit,
            fingerprinted_sources_match_commit=True)
    return clients


def execute(plan, clients, *, output, authorization=None, fake=False, progress=None):
    if len(clients) != 4 or len({id(client) for client in clients}) != 4:
        raise ValueError("Four separate worker clients are required")
    certificate = plan["certificate"]
    if not fake:
        if not authorization or plan != make_launch_plan([ROOT / path for path in plan["prior_run_dirs"]]):
            raise ValueError("Live continuation requires unchanged evidence and allocation note")
        if len({client.metadata.get("source_commit") for client in clients}) != 1:
            raise ValueError("Worker source commits differ")
        for worker, client in enumerate(clients):
            if (not isinstance(client, LunaClient) or not client.audit.get("launch_ready")
                or client.audit.get("public_request_contract") != REQUEST_VERSION
                or type(client.budget) is not ContinuationCreditBudget
                or client.budget.snapshot() != ContinuationCreditBudget(certificate["workers"][worker]).snapshot()
                or getattr(client, "credit_backed_quota", False) is not True
                or client.metadata.get("approved_continuation_sha256") != runner._hash(plan)
                or client.metadata.get("fingerprinted_sources_match_commit") is not True):
                raise ValueError("Fresh audited residual-budget clients are required")
        if len({id(client.budget) for client in clients}) != 4:
            raise ValueError("Worker budgets must be independent")
    directory = Path(output)
    directory.mkdir(parents=True, exist_ok=True)
    if any(directory.iterdir()):
        raise ValueError("Continuation output must be new and empty")
    manifest = {"version": VERSION, "fake": fake, "worker_count": 4,
        "original_plan": plan["original_plan"], "original_plan_sha256": runner._hash(plan["original_plan"]),
        "certificate": certificate, "certificate_sha256": runner._hash(certificate),
        "prior_run_dirs": plan["prior_run_dirs"], "launch_plan_sha256": runner._hash(plan),
        "source_sha256": plan["source_sha256"], "authorization": authorization,
        "request_cap": certificate["remaining_model_attempt_cap"], "heldout_requests": 0,
        "credit_equivalent_cap_exact": certificate["remaining_credit_equivalent_cap_exact"]}
    if not fake:
        manifest.update(source_commit=clients[0].metadata["source_commit"],
            fingerprinted_sources_match_commit=True,
            started_utc=datetime.now(timezone.utc).isoformat(),
            worker_transports=[client.metadata for client in clients])
    atomic_json(directory / "manifest.json", manifest)
    gate, inputs = runner.DispatchGate(), []
    for worker, client in enumerate(clients):
        client.dispatch_gate = gate
        cases = eligible_cases(plan, worker)
        cap = len(cases)
        worker_manifest = {"version": study.VERSION, "phase_version": VERSION,
            "worker": worker, "fake": fake, "aggregate_manifest_sha256": runner._hash(manifest),
            "original_plan_sha256": runner._hash(plan["original_plan"]), "cases": cases,
            "request_cap": cap, "heldout_requests": 0,
            "credit_equivalent_cap_exact": certificate["workers"][worker]["remaining_credit_equivalent_cap_exact"]}
        if not fake:
            worker_manifest.update(authorization=authorization, transport=client.metadata,
                                   source_commit=client.metadata["source_commit"])
        worker_dir = directory / f"worker-{worker}"
        worker_dir.mkdir()
        atomic_json(worker_dir / "manifest.json", worker_manifest)
        atomic_json(worker_dir / "requests.json", [])
        atomic_json(worker_dir / "summary.json", runner._worker_summary(worker,
            [runner._row(case) for case in cases], [], client, fake, cap, worker_manifest))
        inputs.append((worker, cases, client, fake, cap, worker_dir, worker_manifest, gate, progress))
    completed = {}
    with ThreadPoolExecutor(max_workers=4, thread_name_prefix="transfer-continuation") as pool:
        futures = {pool.submit(runner._worker, *args): args[0] for args in inputs}
        try:
            for future in as_completed(futures):
                completed[futures[future]] = future.result()
        except BaseException:
            gate.stop()
            raise
    workers = [completed[i][0] for i in range(4)]
    attempts = [attempt for i in range(4) for attempt in completed[i][1]]
    by_id = {row["case_id"]: row for worker in workers for row in worker["rows"]}
    rows = [by_id[case["case_id"]] for case in plan["original_plan"]["cases"] if case["case_id"] in by_id]
    summary = {"version": VERSION, "fake": fake, "request_cap": manifest["request_cap"],
        "planned_cases": len(rows), "request_attempts": len(attempts),
        "model_requests": sum(worker["model_requests"] for worker in workers),
        "heldout_requests": 0, "manifest_sha256": runner._hash(manifest),
        "worker_summaries": workers, "rows": rows, "attempt_status_counts": runner._counts(attempts),
        "usage_totals": runner._usage(attempts), "shared_stop": gate.event.is_set(), **study.aggregate(rows)}
    if not fake:
        budget = {"cap_credit_equivalent": float(Decimal(manifest["credit_equivalent_cap_exact"])),
                  "cap_credit_equivalent_exact": manifest["credit_equivalent_cap_exact"]}
        for name in ("committed_credit_equivalent", "settled_credit_equivalent",
                     "uncertain_credit_reservations", "remaining_credit_equivalent"):
            value = sum((Decimal(worker["credit_budget"][name + "_exact"]) for worker in workers), Decimal(0))
            budget.update({name: float(value), name + "_exact": str(value)})
        summary["credit_budget"] = budget
    atomic_json(directory / "summary.json", summary)
    return summary


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    modes = parser.add_mutually_exclusive_group(required=True)
    modes.add_argument("--plan", action="store_true")
    modes.add_argument("--live", action="store_true")
    modes.add_argument("--fake", action="store_true")
    parser.add_argument("--prior-run-dir", action="append", type=Path, default=[])
    parser.add_argument("--launch-plan", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--executable", type=Path)
    parser.add_argument("--authorization")
    args = parser.parse_args()
    if args.plan:
        if args.output.exists():
            parser.error("Use a new launch-plan output")
        atomic_json(args.output, make_launch_plan(args.prior_run_dir))
        return
    if args.launch_plan is None:
        parser.error("A frozen --launch-plan is required")
    if args.output.exists() and any(args.output.iterdir()):
        parser.error("Output must be new and empty")
    plan = json.loads(args.launch_plan.read_text(encoding="utf-8"))
    clients = prepare_clients(args, plan) if args.live else [study.FakeClient("optimal") for _ in range(4)]
    lock = threading.Lock()
    def progress(worker, attempts, status, client):
        with lock:
            print(json.dumps({"worker": worker, "attempts": attempts, "status": status,
                "credit_equivalent_committed": None if args.fake else client.budget.snapshot()["committed_credit_equivalent"]}), flush=True)
    summary = execute(plan, clients, output=args.output, authorization=args.authorization,
                      fake=args.fake, progress=progress)
    print(json.dumps({"output": str(args.output), "model_requests": summary["model_requests"],
        "attempt_status_counts": summary["attempt_status_counts"], "shared_stop": summary["shared_stop"]}))


if __name__ == "__main__":
    main()
