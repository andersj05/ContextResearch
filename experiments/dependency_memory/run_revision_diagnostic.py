"""Prepare or run the separate revision-parent diagnostic; offline by default.

The completed 96-request tranche is never reused or extended. Live use requires
an explicitly authorized new allocation and --live, plus a reviewed wire audit.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import tempfile
import time

from revision_diagnostic import MAX_REQUESTS, FakeClient, aggregate, canonical, digest, fake_audit, grade, make_plan, report
from revision_interface import request_bytes, validate_response


def atomic_json(path, value):
    path = Path(path)
    temporary = path.with_suffix(path.suffix + ".part")
    with temporary.open("wb") as stream:
        stream.write(canonical(value) + b"\n")
        stream.flush()
        os.fsync(stream.fileno())
    temporary.replace(path)


def execute(client, *, fake=True, cap=MAX_REQUESTS, output=None, authorization=None):
    if type(cap) is not int or not 0 <= cap <= MAX_REQUESTS:
        raise ValueError("Revision diagnostic cap must be between zero and 24")
    if not fake:
        from luna_appserver import LunaClient
        if not isinstance(client, LunaClient) or not client.audit.get("launch_ready"):
            raise ValueError("Live execution requires the audited subscription client")
        if output is None or not isinstance(authorization, str) or not authorization.strip():
            raise ValueError("Live execution requires persisted evidence and an explicit new allocation note")
    plan = make_plan()
    if not fake and client.metadata.get("approved_plan_sha256") != digest(plan):
        raise ValueError("Live plan differs from the prepared diagnostic artifact")
    manifest = {"version": plan["version"], "plan": plan, "plan_sha256": digest(plan),
                "request_cap": cap, "fake": fake, "heldout_requests": 0}
    if not fake:
        manifest.update(transport=client.metadata, authorization=authorization,
                        started_utc=datetime.now(timezone.utc).isoformat())
    if output is not None:
        output = Path(output)
        output.mkdir(parents=True, exist_ok=True)
        if any(output.iterdir()):
            raise ValueError("Use a new empty directory; never resume or overwrite a tranche")
        atomic_json(output / "manifest.json", manifest)
    ledger, rows, stopped = [], [], False
    for case in plan["cases"]:
        row = {key: case[key] for key in ("case_id", "fixture", "order", "refresh_rule")}
        row.update(status="incomplete", grade=None, displayed_positions=None)
        if stopped or len(ledger) >= cap:
            rows.append(row)
            continue
        raw = request_bytes(case["request"])
        attempt = {"attempt": len(ledger) + 1, "case_id": case["case_id"],
                   "request_utf8": raw.decode("utf-8"), "request_sha256": hashlib.sha256(raw).hexdigest(),
                   "request_bytes": len(raw), "status": "reserved", "response": None,
                   "provider_metadata": {}, "latency_seconds": None}
        ledger.append(attempt)
        if output:
            atomic_json(output / "requests.json", ledger)
        start = time.monotonic()
        try:
            if hasattr(client, "last_metadata"):
                client.last_metadata = {}
            response = client.complete(json.loads(raw))
        except Exception as error:
            attempt.update(status="transport_failure", error_type=type(error).__name__)
            row.update(status="transport_failure")
            stopped = True
        else:
            attempt["response"] = response
            try:
                keys = validate_response(response, case["request"])
            except (ValueError, TypeError, KeyError) as error:
                attempt.update(status="policy_failure", error_type=type(error).__name__)
                row.update(status="policy_failure")
            else:
                positions = {r["key"]: i + 1 for i, r in enumerate(case["request"]["visible_records"])}
                row.update(status="completed", grade=grade(keys, case["refresh_rule"]),
                           displayed_positions=[positions[key] for key in keys])
                attempt["status"] = "completed"
        finally:
            attempt["latency_seconds"] = None if fake else round(time.monotonic() - start, 6)
            attempt["provider_metadata"] = dict(getattr(client, "last_metadata", {}) or {})
            if output:
                atomic_json(output / "requests.json", ledger)
        rows.append(row)
    summary = {"version": plan["version"], "fake": fake, "request_cap": cap,
               "planned_cases": len(rows), "request_attempts": len(ledger),
               "model_requests": 0 if fake else sum(r["provider_metadata"].get("dispatched", False) for r in ledger),
               "heldout_requests": 0, "manifest_sha256": digest(manifest),
               "request_audit_sha256": digest(ledger), "rows": rows,
               "attempt_status_counts": {status: sum(row["status"] == status for row in ledger)
                    for status in ("completed", "policy_failure", "transport_failure", "reserved")},
               **aggregate(rows)}
    if not fake:
        summary["credit_budget"] = client.budget.snapshot()
        summary["transport_manifest"] = client.metadata
        summary["usage_totals"] = {}
        for field in ("input_tokens", "cached_input_tokens", "output_tokens", "reasoning_output_tokens"):
            values = [row["provider_metadata"].get("usage", {}).get(field) for row in ledger]
            measured = [value for value in values if type(value) is int and value >= 0]
            summary["usage_totals"][field] = {"reported": sum(measured) if measured else None,
                                             "measured_attempts": len(measured)}
    if output:
        atomic_json(output / "summary.json", summary)
        (output / "report.md").write_text(report(summary), encoding="utf-8", newline="\n")
    return summary, ledger


def prepare_client(args):
    from luna_appserver import AppServer, LunaClient, MODEL, PROVIDER_OVERRIDES, TransportError
    from luna_budget import CreditBudget
    from luna_isolation import ISOLATION_OVERRIDES
    from run_luna_pilot import progress
    if args.executable is None or not args.authorization:
        raise ValueError("--live needs --executable and an explicit new-allocation --authorization note")
    audit = json.loads(args.audit.read_text(encoding="utf-8"))
    if audit.get("public_request_contract") != "revision_parent_request_v1":
        raise ValueError("The revision request requires its own recorded wire audit")
    frozen_plan = json.loads((Path(__file__).parent / "results/revision_diagnostic_plan.json").read_text(encoding="utf-8"))
    if frozen_plan != make_plan():
        raise ValueError("Prepared plan is stale; review and freeze it before live use")
    if hashlib.sha256(args.audit.read_bytes()).hexdigest() != frozen_plan["source_sha256"][
            "experiments/dependency_memory/results/revision_transport_audit.json"]:
        raise ValueError("Transport audit differs from the frozen plan")
    client = LunaClient(args.executable, audit, budget=CreditBudget(12, args.max_requests), progress=progress)
    client.metadata["approved_plan_sha256"] = digest(frozen_plan)
    with tempfile.TemporaryDirectory(prefix="contextresearch-revision-catalog-") as cwd:
        server = AppServer(args.executable, cwd, (*ISOLATION_OVERRIDES, *PROVIDER_OVERRIDES))
        try:
            server.initialize()
            catalog = server.rpc("model/list", {"includeHidden": True, "limit": 100})
            models = [row for row in catalog.get("data", []) if row.get("model") == MODEL]
            if len(models) != 1 or models[0].get("hidden") is True:
                raise TransportError("requested_model_not_available")
            client.metadata.update(advertised_model=models[0], advertised_model_sha256=digest(models[0]))
        finally:
            server.close()
    root = Path(__file__).resolve().parents[2]
    files = list(Path(__file__).parent.glob("*.py")) + [args.audit, root / "docs/REVISION_DIAGNOSTIC.md"]
    client.metadata["source_sha256"] = {str(path.resolve().relative_to(root)).replace("\\", "/"):
        hashlib.sha256(path.read_bytes()).hexdigest() for path in sorted(files)}
    client.metadata["experiment_version"] = "revision_parent_diagnostic_v1"
    return client


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    modes = parser.add_mutually_exclusive_group()
    modes.add_argument("--plan", action="store_true")
    modes.add_argument("--offline-audit", action="store_true")
    modes.add_argument("--live", action="store_true")
    parser.add_argument("--fake-mode", choices=("optimal", "always_low", "always_high", "first_visible", "invalid"), default="optimal")
    parser.add_argument("--max-requests", type=int, default=MAX_REQUESTS)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--executable", type=Path)
    parser.add_argument("--audit", type=Path, default=Path(__file__).parent / "results/revision_transport_audit.json")
    parser.add_argument("--authorization", help="Record the user's explicit new allocation; never infer it from remaining old credits")
    args = parser.parse_args()
    if not 0 <= args.max_requests <= MAX_REQUESTS:
        parser.error("--max-requests must be from zero through 24")
    if args.plan or args.offline_audit:
        value = make_plan() if args.plan else fake_audit()
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8", newline="\n")
        print(json.dumps({"output": str(args.output), "model_requests": 0}))
        return
    client = prepare_client(args) if args.live else FakeClient(args.fake_mode)
    summary, _ = execute(client, fake=not args.live, cap=args.max_requests,
                         output=args.output, authorization=args.authorization)
    print(json.dumps({"output": str(args.output), "model_requests": summary["model_requests"],
                      "attempt_status_counts": summary["attempt_status_counts"], "by_rule": summary["by_rule"]}))


if __name__ == "__main__":
    main()
