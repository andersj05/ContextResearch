"""Run one bounded development tranche through managed Codex subscription auth.

Explicit --run is required. This command never resumes, retries, buys credits,
switches providers, or runs held-out fixtures. Its first generation is also the
connection diagnostic and consumes the same 96-request allocation.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import tempfile

from luna_appserver import AppServer, LunaClient, MODEL, PROVIDER_OVERRIDES, TransportError
from luna_budget import CreditBudget
from luna_isolation import ISOLATION_OVERRIDES
from pilot_report import report
from run_development_pilot import execute, canonical

ROOT = Path(__file__).resolve().parents[2]


def progress(attempt, metadata):
    print(json.dumps({"generation": attempt, "usage": metadata["usage"],
                      "credit_equivalent_committed": metadata["credit_accounting"]["budget"]["committed_credit_equivalent"]}), flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--executable", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--audit", type=Path, default=Path(__file__).parent / "results/luna_transport_audit.json")
    parser.add_argument("--run", action="store_true", help="Dispatch the authorized development tranche, at most 96 generations")
    args = parser.parse_args()
    if not args.run:
        parser.error("Explicit --run is required; read docs/LUNA_DEVELOPMENT_RUN.md first")
    if args.output.exists() and any(args.output.iterdir()):
        parser.error("Output must be empty; existing runs cannot be overwritten or resumed")
    audit = json.loads(args.audit.read_text(encoding="utf-8"))
    client = LunaClient(args.executable, audit, budget=CreditBudget(20, 96), progress=progress)
    # No thread or generation is created in this catalog observation.
    with tempfile.TemporaryDirectory(prefix="contextresearch-luna-catalog-") as cwd:
        server = AppServer(args.executable, cwd, (*ISOLATION_OVERRIDES, *PROVIDER_OVERRIDES))
        try:
            server.initialize()
            catalog = server.rpc("model/list", {"includeHidden": True, "limit": 100})
            matches = [row for row in catalog.get("data", []) if row.get("model") == MODEL]
            if len(matches) != 1 or matches[0].get("hidden") is True:
                raise TransportError("requested_model_not_available")
            client.metadata["advertised_model"] = matches[0]
            client.metadata["advertised_model_sha256"] = hashlib.sha256(canonical(matches[0])).hexdigest()
        finally:
            server.close()
    # Freeze every local implementation source and the reviewed contract before
    # execute persists the manifest and reserves the first public request.
    files = list(Path(__file__).parent.glob("*.py")) + [args.audit,
        ROOT / "docs/LUNA_DEVELOPMENT_RUN.md", ROOT / "docs/LLM_PILOT_SPEC.md"]
    client.metadata["source_sha256"] = {
        path.resolve().relative_to(ROOT).as_posix(): hashlib.sha256(path.read_bytes()).hexdigest()
        for path in sorted(files)
    }
    client.metadata["started_utc"] = datetime.now(timezone.utc).isoformat()
    client.metadata["authorization"] = "User requested the initial Luna development tests; at most 96 generations, 20 planning credit equivalents, no purchases or API billing"
    summary, ledger = execute(client, cap=96, fake=False, output=args.output,
                              client_name="codex-subscription-gpt-5.6-luna-low")
    (args.output / "report.md").write_text(report(summary), encoding="utf-8", newline="\n")
    print(json.dumps({"output": str(args.output), "model_requests": summary["model_requests"],
                      "attempt_status_counts": summary["attempt_status_counts"],
                      "stage_a_completed": sum(row["status"] == "completed" for row in summary["stage_a"]),
                      "stage_b_completed": sum(row["status"] == "completed" for row in summary["stage_b"]),
                      "credit_budget": client.budget.snapshot(),
                      "last_error": ledger.rows[-1]["provider_metadata"].get("error_code") if ledger.rows else None}), flush=True)


if __name__ == "__main__":
    main()
