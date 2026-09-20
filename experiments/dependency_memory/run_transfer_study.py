"""Four independently budgeted, serial transfer workers; offline by default.

The complete 1,536-request allocation is frozen before any worker dispatch.
Each worker owns eight full blocks and a 50-credit-equivalent budget. A shared
generation gate stops new dispatch after uncertainty; in-flight calls may settle.
There are no retries, repairs, resumption, or outcome-dependent extensions.
"""
from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from decimal import Decimal
import hashlib
import json
from pathlib import Path
import subprocess
import tempfile
import threading
import time

from luna_appserver import AppServer, LunaClient, MODEL, PROVIDER_OVERRIDES, ResponseFormatError, TransportError
from luna_budget import CreditBudget
from luna_isolation import ISOLATION_OVERRIDES
from run_revision_diagnostic import atomic_json
from transfer_interface import VERSION as REQUEST_VERSION, request_bytes, validate_response
import transfer_study as study

ROOT = Path(__file__).resolve().parents[2]
WORKERS = 4
PER_WORKER_REQUESTS = 384
PER_WORKER_CREDITS = 50
TOTAL_REQUESTS = WORKERS * PER_WORKER_REQUESTS
TOTAL_CREDITS = WORKERS * PER_WORKER_CREDITS


class StudyStopped(RuntimeError):
    """A worker reached the dispatch gate after the shared stop was set."""


class DispatchGate:
    """Serialize only dispatch admission, never the generation itself."""

    def __init__(self):
        self.event = threading.Event()
        self.lock = threading.Lock()

    def check(self):
        if self.event.is_set():
            raise StudyStopped("shared_transport_stop")

    def stop(self):
        with self.lock:
            self.event.set()

    def __enter__(self):
        self.lock.acquire()
        if self.event.is_set():
            self.lock.release()
            raise StudyStopped("shared_transport_stop")
        return self

    def __exit__(self, exc_type, exc, traceback):
        # A failed turn/start or reservation must close admission before the
        # lock is released to another worker waiting to begin a generation.
        if exc_type is not None:
            self.event.set()
        self.lock.release()


class TransferCreditBudget(CreditBudget):
    """Explicit new allocation; the historical default remains capped at 96."""

    ATTEMPT_LIMIT = PER_WORKER_REQUESTS

    def __init__(self, max_attempts=PER_WORKER_REQUESTS):
        super().__init__(PER_WORKER_CREDITS, max_attempts)


def _hash(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"),
        ensure_ascii=False, allow_nan=False).encode()).hexdigest()


def source_commit(plan):
    """Attest only the frozen source set, allowing unrelated generated files."""
    def git(*arguments):
        result = subprocess.run(["git", "-c", f"safe.directory={ROOT.as_posix()}", *arguments],
            cwd=ROOT, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=30, check=False)
        if result.returncode != 0:
            raise ValueError("Frozen source must be committed before live preparation")
        return result.stdout

    commit = git("rev-parse", "HEAD").decode("ascii").strip()
    if len(commit) not in (40, 64) or any(c not in "0123456789abcdef" for c in commit):
        raise ValueError("Git did not return an immutable source commit")
    for path, expected in plan["source_sha256"].items():
        if hashlib.sha256(git("show", f"{commit}:{path}")).hexdigest() != expected:
            raise ValueError("Fingerprinted source differs from committed bytes: " + path)
    return commit


def _row(case):
    return {**{key: value for key, value in case.items()
               if key not in ("request", "request_sha256")},
            "status": "incomplete", "grade": None, "displayed_positions": None}


def validate_plan(plan):
    cases = plan.get("cases", [])
    if len(cases) != TOTAL_REQUESTS or len({case["case_id"] for case in cases}) != TOTAL_REQUESTS:
        raise ValueError("Transfer plan must contain exactly 1,536 unique cases")
    for worker in range(WORKERS):
        own = [case for case in cases if case["worker"] == worker]
        if len(own) != PER_WORKER_REQUESTS:
            raise ValueError("Every worker must own exactly eight complete blocks")
        expected_blocks = list(range(worker, 32, WORKERS))
        if list(dict.fromkeys(case["block"] for case in own)) != expected_blocks:
            raise ValueError("Worker blocks must advance in the frozen round-robin order")
        if any(sum(case["block"] == block for case in own) != 48 for block in expected_blocks):
            raise ValueError("Every block must contain all 48 conditions")
        if [case["block"] for case in own] != sorted(case["block"] for case in own):
            raise ValueError("A worker must finish one block before starting the next")
    for case in cases:
        raw = request_bytes(case["request"])
        if hashlib.sha256(raw).hexdigest() != case["request_sha256"]:
            raise ValueError("Frozen public request hash mismatch")


def _counts(ledger):
    return {status: sum(row["status"] == status for row in ledger)
            for status in ("completed", "policy_failure", "transport_failure", "reserved")}


def _usage(ledger):
    result = {}
    for name in ("input_tokens", "cached_input_tokens", "output_tokens",
                 "reasoning_output_tokens", "cache_write_input_tokens"):
        values = [row["provider_metadata"].get("usage", {}).get(name) for row in ledger]
        measured = [v for v in values if type(v) is int and v >= 0]
        result[name] = {"reported": sum(measured) if measured else None,
                        "measured_attempts": len(measured)}
    return result


def _worker_summary(worker, rows, ledger, client, fake, cap, manifest):
    result = {"version": study.VERSION, "worker": worker, "fake": fake,
        "request_cap": cap, "planned_cases": len(rows), "request_attempts": len(ledger),
        "model_requests": 0 if fake else sum(a["provider_metadata"].get("dispatched", False) for a in ledger),
        "heldout_requests": 0, "manifest_sha256": _hash(manifest),
        "request_audit_sha256": _hash(ledger), "rows": rows,
        "attempt_status_counts": _counts(ledger), "usage_totals": _usage(ledger)}
    if not fake:
        result["credit_budget"] = client.budget.snapshot()
        result["transport_manifest"] = client.metadata
    return result


def _worker(worker, cases, client, fake, cap, output, manifest, gate, progress):
    ledger, rows = [], [_row(case) for case in cases]

    def persist(*, final=False):
        if output is None and not final:
            return None
        summary = _worker_summary(worker, rows, ledger, client, fake, cap, manifest)
        if output is not None:
            atomic_json(output / "requests.json", ledger)
            atomic_json(output / "summary.json", summary)
        return summary

    persist()
    try:
        for case, row in zip(cases, rows):
            if len(ledger) >= cap or gate.event.is_set():
                break
            raw = request_bytes(case["request"])
            attempt = {"attempt": len(ledger) + 1, "case_id": case["case_id"],
                "worker": worker, "block": case["block"], "request_utf8": raw.decode(),
                "request_sha256": hashlib.sha256(raw).hexdigest(), "request_bytes": len(raw),
                "status": "reserved", "response": None, "provider_metadata": {}, "latency_seconds": None}
            ledger.append(attempt)
            persist()  # Every reservation survives a process interruption.
            started = time.monotonic()
            try:
                if hasattr(client, "last_metadata"):
                    client.last_metadata = {}
                gate.check()
                response = client.complete(json.loads(raw))
            except ResponseFormatError as error:
                attempt.update(status="policy_failure", error_type=type(error).__name__)
                row["status"] = "policy_failure"
            except Exception as error:
                gate.stop()
                attempt.update(status="transport_failure", error_type=type(error).__name__)
                row["status"] = "transport_failure"
            else:
                attempt["response"] = response
                try:
                    selected = validate_response(response, case["request"])
                except (ValueError, TypeError, KeyError) as error:
                    attempt.update(status="policy_failure", error_type=type(error).__name__)
                    row["status"] = "policy_failure"
                else:
                    positions = {r["key"]: i + 1 for i, r in enumerate(case["request"]["visible_records"])}
                    row.update(status="completed", grade=study.grade(selected, case),
                               displayed_positions=[positions[key] for key in selected])
                    attempt["status"] = "completed"
            finally:
                attempt["latency_seconds"] = None if fake else round(time.monotonic() - started, 6)
                attempt["provider_metadata"] = dict(getattr(client, "last_metadata", {}) or {})
                persist()
            if progress is not None:
                progress(worker, len(ledger), attempt["status"], client)
    except BaseException:
        gate.stop()
        raise
    return persist(final=True), ledger


def execute(clients, *, fake=True, output=None, authorization=None,
            limit_per_worker=PER_WORKER_REQUESTS, progress=None):
    if type(limit_per_worker) is not int or not 0 <= limit_per_worker <= PER_WORKER_REQUESTS:
        raise ValueError("Per-worker request cap must be an integer from zero through 384")
    if len(clients) != WORKERS or len({id(c) for c in clients}) != WORKERS:
        raise ValueError("Four distinct worker clients are required")
    plan = study.make_plan()
    validate_plan(plan)
    if not fake:
        if output is None or not isinstance(authorization, str) or not authorization.strip():
            raise ValueError("Live transfer requires persistent evidence and explicit new-allocation authorization")
        if limit_per_worker != PER_WORKER_REQUESTS or not plan.get("protocol_and_wire_audit_present"):
            raise ValueError("Live transfer requires the complete reviewed 1,536-request allocation")
        for client in clients:
            if (not isinstance(client, LunaClient) or not client.audit.get("launch_ready")
                    or client.audit.get("public_request_contract") != REQUEST_VERSION
                    or type(client.budget) is not TransferCreditBudget
                    or client.budget.snapshot() != TransferCreditBudget().snapshot()
                    or getattr(client, "quota_used_limit", None) != 100
                    or client.metadata.get("quota_guard_used_percent") != 100
                    or client.metadata.get("fingerprinted_sources_match_commit") is not True
                    or not client.metadata.get("source_commit")
                    or client.metadata.get("approved_plan_sha256") != _hash(plan)):
                raise ValueError("Live transfer requires fresh audited clients with separate approved worker budgets")
        if len({id(client.budget) for client in clients}) != WORKERS:
            raise ValueError("Worker credit budgets must not be shared")
        if len({client.metadata["source_commit"] for client in clients}) != 1:
            raise ValueError("Worker clients must share one attested source commit")
    manifest = {"version": study.VERSION, "plan": plan, "plan_sha256": _hash(plan),
        "fake": fake, "request_cap": WORKERS * limit_per_worker, "worker_count": WORKERS,
        "per_worker_request_cap": limit_per_worker, "credit_equivalent_cap": TOTAL_CREDITS,
        "per_worker_credit_equivalent_cap": PER_WORKER_CREDITS, "heldout_requests": 0}
    if not fake:
        manifest.update(authorization=authorization, started_utc=datetime.now(timezone.utc).isoformat(),
                        worker_transports=[client.metadata for client in clients],
                        source_commit=clients[0].metadata["source_commit"],
                        fingerprinted_sources_match_commit=True)
    directory = Path(output) if output is not None else None
    if directory is not None:
        directory.mkdir(parents=True, exist_ok=True)
        if any(directory.iterdir()):
            raise ValueError("Use a new empty directory; no resume or overwrite is permitted")
        atomic_json(directory / "manifest.json", manifest)
    gate = DispatchGate()
    worker_inputs = []
    for worker, client in enumerate(clients):
        client.dispatch_gate = gate
        cases = [case for case in plan["cases"] if case["worker"] == worker]
        worker_manifest = {"version": study.VERSION, "worker": worker, "fake": fake,
            "aggregate_manifest_sha256": _hash(manifest), "plan_sha256": _hash(plan),
            "cases": cases, "request_cap": limit_per_worker,
            "credit_equivalent_cap": PER_WORKER_CREDITS, "heldout_requests": 0}
        if not fake:
            worker_manifest.update(authorization=authorization, transport=client.metadata,
                                   source_commit=client.metadata["source_commit"])
        worker_dir = directory / f"worker-{worker}" if directory is not None else None
        if worker_dir is not None:
            worker_dir.mkdir()
            atomic_json(worker_dir / "manifest.json", worker_manifest)
            atomic_json(worker_dir / "requests.json", [])
            atomic_json(worker_dir / "summary.json", _worker_summary(worker,
                [_row(case) for case in cases], [], client, fake, limit_per_worker, worker_manifest))
        worker_inputs.append((worker, cases, client, fake, limit_per_worker,
                              worker_dir, worker_manifest, gate, progress))
    # Every aggregate/worker manifest and initial denominator is durable before
    # the first ThreadPool submission can start a client process or generation.
    completed = {}
    with ThreadPoolExecutor(max_workers=WORKERS, thread_name_prefix="transfer") as pool:
        futures = {pool.submit(_worker, *args): args[0] for args in worker_inputs}
        try:
            for future in as_completed(futures):
                completed[futures[future]] = future.result()
        except BaseException:
            gate.stop()
            raise
    workers = [completed[i][0] for i in range(WORKERS)]
    all_attempts = [attempt for i in range(WORKERS) for attempt in completed[i][1]]
    by_id = {row["case_id"]: row for worker in workers for row in worker["rows"]}
    rows = [by_id[case["case_id"]] for case in plan["cases"]]
    summary = {"version": study.VERSION, "fake": fake, "request_cap": WORKERS * limit_per_worker,
        "planned_cases": len(rows), "request_attempts": len(all_attempts),
        "model_requests": sum(worker["model_requests"] for worker in workers), "heldout_requests": 0,
        "manifest_sha256": _hash(manifest), "worker_summaries": workers, "rows": rows,
        "attempt_status_counts": _counts(all_attempts), "usage_totals": _usage(all_attempts),
        "shared_stop": gate.event.is_set(), **study.aggregate(rows)}
    if not fake:
        budget = {"cap_credit_equivalent": TOTAL_CREDITS,
                  "cap_credit_equivalent_exact": str(TOTAL_CREDITS)}
        for name in ("committed_credit_equivalent", "settled_credit_equivalent",
                     "uncertain_credit_reservations", "remaining_credit_equivalent"):
            value = sum((Decimal(worker["credit_budget"][name + "_exact"]) for worker in workers), Decimal(0))
            budget.update({name: float(value), name + "_exact": str(value)})
        summary["credit_budget"] = budget
    if directory is not None:
        atomic_json(directory / "summary.json", summary)
        (directory / "report.md").write_text(study.report(summary), encoding="utf-8", newline="\n")
    return summary


def prepare_clients(args):
    if args.executable is None or not isinstance(args.authorization, str) or not args.authorization.strip():
        raise ValueError("--live requires --executable and explicit --authorization for this allocation")
    frozen = json.loads((Path(__file__).parent / "results/transfer_study_plan.json").read_text(encoding="utf-8"))
    if not frozen.get("protocol_and_wire_audit_present") or frozen != study.make_plan():
        raise ValueError("Transfer plan is missing reviewed dependencies or differs from its frozen artifact")
    validate_plan(frozen)
    audit_bytes = args.audit.read_bytes()
    audit = json.loads(audit_bytes)
    if (audit.get("public_request_contract") != REQUEST_VERSION
            or hashlib.sha256(audit_bytes).hexdigest() != frozen["source_sha256"].get(
                "experiments/dependency_memory/results/transfer_transport_audit.json")):
        raise ValueError("The transfer wire audit must match the separately frozen contract artifact")
    commit = source_commit(frozen)
    if frozen != study.make_plan():
        raise ValueError("Fingerprinted sources changed during commit verification")
    clients = [LunaClient(args.executable, audit, budget=TransferCreditBudget(),
                          quota_used_limit=100) for _ in range(WORKERS)]
    with tempfile.TemporaryDirectory(prefix="contextresearch-transfer-catalog-") as cwd:
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
        client.metadata.update(worker=worker, experiment_version=study.VERSION,
            approved_plan_sha256=_hash(frozen), source_sha256=frozen["source_sha256"],
            advertised_model=matches[0], advertised_model_sha256=_hash(matches[0]),
            source_commit=commit, fingerprinted_sources_match_commit=True)
    return clients


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    modes = parser.add_mutually_exclusive_group()
    modes.add_argument("--plan", action="store_true")
    modes.add_argument("--offline-audit", action="store_true")
    modes.add_argument("--live", action="store_true")
    parser.add_argument("--fake-mode", choices=("optimal", "static_low", "first_visible", "invalid"), default="optimal")
    parser.add_argument("--limit-per-worker", type=int, default=PER_WORKER_REQUESTS)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--executable", type=Path)
    parser.add_argument("--audit", type=Path, default=Path(__file__).parent / "results/transfer_transport_audit.json")
    parser.add_argument("--authorization")
    args = parser.parse_args()
    if not 0 <= args.limit_per_worker <= PER_WORKER_REQUESTS:
        parser.error("--limit-per-worker must be between zero and 384")
    if args.live and args.limit_per_worker != PER_WORKER_REQUESTS:
        parser.error("The live allocation contains four complete 384-request workers")
    if args.plan:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        atomic_json(args.output, study.make_plan())
        return
    if args.offline_audit:
        controls = []
        for mode in ("optimal", "static_low", "first_visible", "invalid"):
            summary = execute([study.FakeClient(mode) for _ in range(WORKERS)])
            controls.append({"mode": mode, **{k: v for k, v in summary.items()
                if k not in ("rows", "worker_summaries")}})
        args.output.parent.mkdir(parents=True, exist_ok=True)
        atomic_json(args.output, {"version": study.VERSION, "model_requests": 0,
                    "plan_sha256": _hash(study.make_plan()), "controls": controls})
        return
    if args.output.exists() and any(args.output.iterdir()):
        parser.error("Output must be empty; existing runs cannot be overwritten or resumed")
    clients = prepare_clients(args) if args.live else [study.FakeClient(args.fake_mode) for _ in range(WORKERS)]
    print_lock = threading.Lock()

    def progress(worker, attempts, status, client):
        if not args.live:
            return
        with print_lock:
            print(json.dumps({"worker": worker, "attempts": attempts, "status": status,
                "credit_equivalent_committed": client.budget.snapshot()["committed_credit_equivalent"]}), flush=True)

    summary = execute(clients, fake=not args.live, output=args.output,
                      authorization=args.authorization, limit_per_worker=args.limit_per_worker, progress=progress)
    print(json.dumps({"output": str(args.output), "model_requests": summary["model_requests"],
        "attempt_status_counts": summary["attempt_status_counts"], "shared_stop": summary["shared_stop"]}))


if __name__ == "__main__":
    main()
