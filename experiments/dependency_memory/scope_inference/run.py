"""Prepare, attest, run once, and independently analyze the eight-call allocation."""
import argparse
from datetime import datetime, timezone
from decimal import Decimal
import hashlib
import json
from pathlib import Path
import subprocess

from experiments.dependency_memory.workflow_replay import evidence
from . import codec, profile, protocol, study

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
RESULTS = HERE.parent / "results/scope_luna_2026-10-01"
DEPENDENCIES = ("luna_appserver.py", "luna_budget.py", "codex_subscription.py", "request_contracts.py",
                "workflow_replay/evidence.py", "workflow_eval_live/profile.py")


def save(path, value):
    raw = json.dumps(value, indent=2, sort_keys=True, allow_nan=False).encode() + b"\n"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(raw)


def fingerprints():
    files = [*HERE.glob("*.py"), HERE / "PROTOCOL.md"]
    files += [HERE.parent / name for name in DEPENDENCIES]
    files += [ROOT / name for name in evidence.HASHES]
    return {p.relative_to(ROOT).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(files)}


def stable(value):
    if isinstance(value, dict):
        return {k: stable(v) for k, v in value.items() if k not in {"cpu_ns", "wall_ns"}}
    if isinstance(value, list):
        return [stable(v) for v in value]
    return value


def prepare(preflight, directory=RESULTS):
    if (directory / "manifest.json").exists():
        raise FileExistsError("Do not overwrite this allocation")
    audit = json.loads(preflight.read_text(encoding="utf-8"))
    if (audit.get("version") != "scope_luna6_preflight_v1" or audit.get("isolation_passed") is not True
            or audit.get("real_model_generations") != 0 or profile.VISIBLE_TOOL_SPEC_SHA256 is None
            or any(c["payload_audit"]["visible_tool_spec_sha256"] != profile.VISIBLE_TOOL_SPEC_SHA256 for c in audit["cases"])):
        raise ValueError("Fresh pinned zero-generation audit required")
    controls = study.offline_controls()
    rows = [{**row, "request": protocol.request(row["variant"]),
             "request_sha256": hashlib.sha256(protocol.request_bytes(protocol.request(row["variant"]))).hexdigest()}
            for row in study.schedule()]
    manifest = {"version": "scope_luna_launch_v1", "date": "2026-10-01", "model": profile.MODEL,
        "effort": "medium", "service_tier": "default", "immutable_model_revision": None, "sampling_seed": None,
        "schedule_seed": study.SEED, "max_calls": 8, "planning_credit_cap": "20", "per_call_reservation": "7.65",
        "api_dollar_spend": 0, "actual_account_debit": None, "priced_total_cost": None,
        "source_sha256": fingerprints(), "program_sha256": hashlib.sha256(study.public_program().encode()).hexdigest(),
        "catalog": study.catalog_lock(), "historical_source_hashes": evidence.HASHES, "requests": rows,
        "external_human_review": "pending", "evidence_class": "one inspected public program; eight correlated source-only calls; constructed catalog/timing"}
    save(directory / "preflight.json", audit)
    save(directory / "offline-controls.json", controls)
    save(directory / "manifest.json", manifest)
    return manifest


def verify(manifest):
    if (manifest["version"] != "scope_luna_launch_v1" or manifest["source_sha256"] != fingerprints()
            or manifest["catalog"] != study.catalog_lock() or manifest["max_calls"] != 8
            or manifest["planning_credit_cap"] != "20" or manifest["per_call_reservation"] != "7.65"):
        raise ValueError("Frozen method or allocation changed")
    expected = study.schedule()
    if len(manifest["requests"]) != len(expected):
        raise ValueError("Frozen identities changed")
    for actual, scheduled in zip(manifest["requests"], expected):
        if (any(actual[k] != scheduled[k] for k in scheduled) or actual["request"] != protocol.request(scheduled["variant"])
                or actual["request_sha256"] != hashlib.sha256(protocol.request_bytes(actual["request"])).hexdigest()):
            raise ValueError("Frozen public request changed")


def attest(manifest, directory):
    verify(manifest)
    git = ["git", "-c", "safe.directory=" + ROOT.as_posix()]
    commit = subprocess.check_output([*git, "rev-parse", "HEAD"], cwd=ROOT).decode().strip()
    files = {**manifest["source_sha256"], (directory / "manifest.json").relative_to(ROOT).as_posix(): hashlib.sha256((directory / "manifest.json").read_bytes()).hexdigest()}
    for path, expected in files.items():
        committed = subprocess.check_output([*git, "show", commit + ":" + path], cwd=ROOT)
        if hashlib.sha256(committed).hexdigest() != expected:
            raise ValueError("Uncommitted frozen source: " + path)
    return commit


def run(executable, instructions, directory=RESULTS):
    from .transport import Client
    manifest = json.loads((directory / "manifest.json").read_text())
    commit = attest(manifest, directory)
    if (directory / "launch.json").exists() or (directory / "calls").exists():
        raise FileExistsError("Never resume or retry this dispatched allocation")
    launch = {"source_commit": commit, "manifest_sha256": hashlib.sha256((directory / "manifest.json").read_bytes()).hexdigest(),
              "started_at_utc": datetime.now(timezone.utc).isoformat(), "authorized_calls": 8, "planning_credit_cap": "20"}
    with (directory / "launch.json").open("xb") as file:
        file.write(codec.wire(launch) + b"\n")
    audit = json.loads((directory / "preflight.json").read_text())
    client = Client(executable, instructions, directory, audit)
    for row in manifest["requests"]:
        try:
            verify(manifest)
            client.complete(row["identity"], row["request"])
        except Exception as error:
            save(directory / "stop.json", {"error_type": type(error).__name__, "identity": row["identity"],
                 "stopped_at_utc": datetime.now(timezone.utc).isoformat(), "retry_authorized": False})
            break
    # Scoring starts only after all calls complete or a durable stop is recorded.
    result, measured = analyze(directory)
    save(directory / "evaluations.json", measured)
    save(directory / "analysis.json", result)
    (directory / "report.md").write_bytes(report(result).encode())
    return result


def analyze(directory=RESULTS):
    from .transport import RESERVATION, usage_cost
    from luna_appserver import strict_json
    manifest = json.loads((directory / "manifest.json").read_text())
    verify(manifest)
    original, records = evidence.historical_classifier(), evidence.load_snapshot()[0]
    rows, measured, known, neutral, unknown = [], {}, Decimal(0), Decimal(0), Decimal(0)
    for planned in manifest["requests"]:
        path = directory / "calls" / (planned["identity"] + ".json")
        if not path.exists():
            rows.append({k: planned[k] for k in ("identity", "replicate", "variant")} | {"status": "not_dispatched"})
            continue
        call = json.loads(path.read_text())
        if call["identity"] != planned["identity"] or call["request"] != planned["request"] or call["request_sha256"] != planned["request_sha256"]:
            raise ValueError("Saved generation belongs to another frozen request")
        if (call["model"] != profile.MODEL or call["effort"] != "medium"
                or call["wire_body_byte_bound"] != profile.wire_body_byte_bound(planned["request"])
                or type(call["dispatched"]) is not bool):
            raise ValueError("Saved generation violates its transport contract")
        row = {k: planned[k] for k in ("identity", "replicate", "variant")}
        row.update(status=call["status"], dispatched=call["dispatched"])
        if call["status"] != "completed":
            if call["dispatched"]:
                unknown += RESERVATION
            rows.append(row)
            continue
        charge = usage_cost(call["usage"])
        if str(charge) != call["planning_credits"]:
            raise ValueError("Saved usage and settlement differ")
        known += charge
        cache_free = {**call["usage"], "cachedInputTokens": 0}
        neutral += usage_cost(cache_free)
        row["planning_credits"] = str(charge)
        try:
            parsed = strict_json(call["raw_answer"])
        except (ValueError, TypeError):
            parsed = None
        if parsed != call["response"] or call.get("usage_events") != 1 or call.get("tool_items") != 0:
            raise ValueError("Raw answer or generation count differs from saved response")
        try:
            contract = codec.validate(call["response"])
        except (TypeError, ValueError):
            row.update(contract_valid=False, complete_contract=False, policy_failure=True)
            rows.append(row)
            continue
        scores = {"contract": contract, "catalog": study.evaluate(contract, study.control_catalog(), original),
                  "history": study.evaluate(contract, records, original), "staged": study.staged(records, original, contract=contract)}
        measured[row["identity"]] = scores
        row.update(contract_valid=True, complete_contract=scores["catalog"]["disagreements"] == 0,
                   **stable(scores))
        rows.append(row)
    completed = sum(row["status"] == "completed" for row in rows)
    variants = {variant: {"completed": sum(r["status"] == "completed" for r in rows if r["variant"] == variant),
                 "complete_contracts": sum(r.get("complete_contract", False) for r in rows if r["variant"] == variant),
                 "false_preflight_only": sum(r.get("catalog", {}).get("false_preflight_only", 0) for r in rows if r["variant"] == variant)}
                for variant in ("concise", "closure")}
    criterion = None if completed != 8 else (variants["closure"]["complete_contracts"] > variants["concise"]["complete_contracts"]
                                            and variants["closure"]["false_preflight_only"] == 0)
    controls = json.loads((directory / "offline-controls.json").read_text())
    fresh = study.offline_controls()
    if stable(controls) != stable(fresh):
        raise ValueError("Frozen baseline semantics differ from fresh original-program replay")
    if known + unknown > Decimal(20) or completed > 8:
        raise ValueError("Allocation exceeded")
    result = {"version": "scope_luna_analysis_v1", "date": "2026-10-01", "status": "complete" if completed == 8 else "incomplete",
        "provider_dispatches": sum(r.get("dispatched", False) for r in rows), "metered_answers": completed,
        "scheduled_calls": 8, "not_dispatched": sum(r["status"] == "not_dispatched" for r in rows),
        "known_planning_credits": str(known), "cache_neutral_planning_credits": str(neutral), "unknown_reservations": str(unknown),
        "api_dollar_spend": 0, "actual_account_debit": None, "priced_total_cost": None,
        "variants": variants, "primary_criterion_met": criterion, "calls": rows, "controls": stable(controls),
        "prospective_natural_episodes": 0, "external_human_review": "pending",
        "limits": "One inspected public program; correlated source-only calls. Catalog/timing constructed. Finite agreement is not universal semantic certification or production improvement."}
    return result, measured


def report(result):
    variants = result["variants"]
    lines = ["# Luna source-only dependency-scope development test", "", "October 1, 2026. One inspected public program; constructed catalog and delayed queries.", "",
        f"Status: {result['status']}; {result['provider_dispatches']}/8 dispatches, {result['metered_answers']} metered answers, {result['not_dispatched']} never dispatched.", "",
        "| Prompt | Completed | Complete contracts on the catalog | False preflight-only cases |", "|---|---:|---:|---:|"]
    for name, row in variants.items():
        lines.append(f"| {name} | {row['completed']} | {row['complete_contracts']} | {row['false_preflight_only']} |")
    lines += ["", f"Primary criterion met: {result['primary_criterion_met']}.", "",
        f"Known model planning cost: {result['known_planning_credits']}; cache-neutral: {result['cache_neutral_planning_credits']}; unknown reservations: {result['unknown_reservations']}.", "",
        "Zero-model handwritten, literal-root, raw and cached-result baselines are preserved in analysis.json. Scripted late decoding is not an uncharged LLM result. Extraction, local operations and model failures are charged separately; actual subscription debit and fully priced total cost remain unknown.", "",
        result["limits"], ""]
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--prepare", type=Path)
    mode.add_argument("--run", action="store_true")
    mode.add_argument("--analyze", action="store_true")
    parser.add_argument("--executable", type=Path)
    parser.add_argument("--global-instructions", type=Path)
    args = parser.parse_args()
    if args.prepare:
        result = prepare(args.prepare)
        print(json.dumps({"prepared": True, "calls": len(result["requests"]), "catalog": result["catalog"]}))
    elif args.run:
        result = run(args.executable, args.global_instructions)
        print(json.dumps({k: result[k] for k in ("status", "metered_answers", "known_planning_credits", "primary_criterion_met")}))
    else:
        result, _ = analyze()
        saved = json.loads((RESULTS / "analysis.json").read_text())
        if saved != result or (RESULTS / "report.md").read_text() != report(result):
            raise ValueError("Saved scope analysis differs from independent replay")
        print(json.dumps({"replay": "PASS", "metered_answers": result["metered_answers"], "primary_criterion_met": result["primary_criterion_met"]}))


if __name__ == "__main__":
    main()
