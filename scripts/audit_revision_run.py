"""Read-only validation of saved revision diagnostic evidence; no model calls."""
from __future__ import annotations

import argparse
from collections import Counter
from decimal import Decimal
from fractions import Fraction
import hashlib
from itertools import combinations
import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "experiments/dependency_memory"))

from luna_appserver import strict_json
from luna_isolation import wire_body_byte_bound
from revision_diagnostic import aggregate, digest, make_plan
from revision_interface import KEYS, request_bytes, validate_response

RESERVATION = Decimal("10.4025")
CAP = Decimal("12")


def require(condition, message):
    if not condition:
        raise ValueError(message)


def hash_map(value):
    require(type(value) is dict and value, "Missing source provenance")
    for name, sha in value.items():
        require(type(name) is str and name and type(sha) is str
                and re.fullmatch(r"[0-9a-f]{64}", sha), "Malformed source provenance hash")


def independent_grade(keys, rule):
    """Grade all target continuations independently of the runner's grader."""
    hits = 0
    for first, last in combinations(KEYS, 2):
        refreshed = first if rule == "lexicographic_first" else last if rule == "lexicographic_last" else None
        hits += sum(target == refreshed or target in keys for target in (first, last))
    availability = Fraction(hits, 30)
    best = Fraction(1, 3) if rule == "none" else Fraction(4, 5)
    return {"keys": list(keys), "selected_rank_sum": sum(KEYS.index(key) for key in keys),
            "availability": str(availability), "best_availability": str(best),
            "exact_parent_regret": str(best - availability), "optimal_parent": availability == best,
            "route_count": 30, "downstream_selector": "guaranteed_optimal"}


def amount(record, name, expected):
    require(type(record.get(name)) in (int, float) and Decimal(str(record[name])) == expected,
            "Credit amount mismatch: " + name)
    require(type(record.get(name + "_exact")) is str
            and Decimal(record[name + "_exact"]) == expected, "Exact credit amount mismatch: " + name)


def budget_snapshot(snapshot, *, cap, attempts, settled_count, failed_count, spent, uncertain):
    require(type(snapshot) is dict, "Missing credit budget snapshot")
    committed = spent + uncertain
    for name, expected in (("cap_credit_equivalent", CAP), ("per_attempt_reservation", RESERVATION),
                           ("committed_credit_equivalent", committed), ("settled_credit_equivalent", spent),
                           ("uncertain_credit_reservations", uncertain),
                           ("remaining_credit_equivalent", CAP - committed)):
        amount(snapshot, name, expected)
    require(Decimal(0) <= committed <= CAP, "Credit cap exceeded")
    for name, expected in (("generation_attempts", attempts), ("generation_attempt_ceiling", cap),
                           ("settled_attempts", settled_count), ("failed_attempts", failed_count),
                           ("api_dollar_spend_authorized", 0), ("credit_purchases", 0), ("reset_redemptions", 0)):
        require(type(snapshot.get(name)) is int and snapshot[name] == expected, "Budget counter mismatch: " + name)
    require(snapshot.get("pending_ticket") is None and snapshot.get("stopped") is (failed_count > 0)
            and snapshot.get("api_key_fallback") is False, "Unsafe or unfinished budget state")


def live_accounting(ledger, summary, manifest, cap):
    transport = manifest.get("transport")
    require(type(transport) is dict and transport == summary.get("transport_manifest"), "Transport manifest mismatch")
    require(transport.get("model") == "gpt-5.6-luna", "Unexpected model")
    require(transport.get("experiment_version") == "revision_parent_diagnostic_v1", "Wrong experiment transport")
    require(transport.get("approved_plan_sha256") == manifest.get("plan_sha256"),
            "Approved plan hash differs from saved run plan")
    hash_map(transport.get("source_sha256"))
    hash_map({name: transport.get(name) for name in
              ("cli_sha256", "isolation_profile_sha256", "global_instructions_sha256", "advertised_model_sha256")})
    require(digest(transport.get("advertised_model")) == transport["advertised_model_sha256"], "Advertised model hash mismatch")
    require(transport.get("provider") == "luna_research" and transport.get("reasoning_effort") == "low"
            and transport.get("service_tier") == "default" and transport.get("http_and_stream_retries") == 0
            and transport.get("maximum_wire_body_bytes") == 32768, "Transport contract drift")
    budget_snapshot(transport.get("budget"), cap=cap, attempts=0,
                    settled_count=0, failed_count=0, spent=Decimal(0), uncertain=Decimal(0))
    require(type(manifest.get("authorization")) is str and manifest["authorization"].strip(), "Missing new-allocation note")
    spent, uncertain = Decimal(0), Decimal(0)
    attempts = settled_count = failed_count = 0
    totals = Counter()
    for row in ledger:
        meta = row["provider_metadata"]
        dispatched = meta.get("dispatched", False)
        require(type(dispatched) is bool, "Invalid dispatch flag")
        if not dispatched:
            require(row["status"] == "transport_failure" and "credit_accounting" not in meta,
                    "Undispatched attempt was completed or charged")
            continue
        require(not failed_count and spent + RESERVATION <= CAP, "Dispatch exceeded available reservation")
        attempts += 1
        require(type(meta.get("wire_body_byte_bound")) is int
                and meta["wire_body_byte_bound"] == wire_body_byte_bound(strict_json(row["request_utf8"])) <= 32768,
                "Missing or inconsistent request wire bound")
        require(type(meta.get("attempt_ticket")) is int and meta["attempt_ticket"] == attempts,
                "Generation ticket sequence mismatch")
        accounting = meta.get("credit_accounting", {})
        require(type(accounting.get("ticket")) is int and accounting["ticket"] == attempts, "Accounting ticket mismatch")
        if accounting.get("status") == "settled":
            usage = meta.get("usage", {})
            for key in ("input_tokens", "cached_input_tokens", "output_tokens", "reasoning_output_tokens"):
                require(type(usage.get(key)) is int and usage[key] >= 0, "Missing or invalid token count")
            inputs, cached, outputs, reasoning = (usage[k] for k in
                ("input_tokens", "cached_input_tokens", "output_tokens", "reasoning_output_tokens"))
            writes = usage.get("cache_write_input_tokens")
            require(writes is None or type(writes) is int and writes >= 0, "Invalid cache-write token count")
            require(0 < inputs < 272000 and cached + (writes or 0) <= inputs
                    and reasoning <= outputs <= 128000, "Token accounting envelope violated")
            expected_usage = {"inputTokens": inputs, "cachedInputTokens": cached,
                "cacheWriteInputTokens": writes or 0, "outputTokens": outputs,
                "reasoningOutputTokens": reasoning, "totalTokens": inputs + outputs}
            require(accounting.get("usage") == expected_usage, "Token accounting differs from provider usage")
            actual = (Decimal(inputs) * Decimal("6.25") + Decimal(outputs) * 30) / 1000000
            basic = (Decimal(inputs - cached) * 5 + Decimal(cached) / 2 + Decimal(outputs) * 30) / 1000000
            amount(accounting, "conservative_credit_equivalent", actual)
            amount(accounting, "basic_rate_credit_estimate", basic)
            amount(accounting, "released_credit_equivalent", RESERVATION - actual)
            require(accounting.get("reasoning_already_in_output") is True
                    and accounting.get("observed_credit_balance_debit") is None
                    and accounting.get("observed_dollar_charge") is None,
                    "Unsupported invoice claim or reasoning double-counting")
            require(meta.get("harness_termination") == "session_budget_exceeded", "Missing one-generation guard")
            spent += actual
            settled_count += 1
            totals.update({"input_tokens": inputs, "cached_input_tokens": cached,
                           "output_tokens": outputs, "reasoning_output_tokens": reasoning})
        elif accounting.get("status") == "reservation_retained":
            require(row["status"] == "transport_failure", "Retained reservation without transport failure")
            uncertain += RESERVATION
            failed_count += 1
        else:
            raise ValueError("Dispatched attempt has no settled or retained accounting")
        budget_snapshot(accounting.get("budget"), cap=cap, attempts=attempts,
                        settled_count=settled_count, failed_count=failed_count, spent=spent, uncertain=uncertain)
        if row["status"] in ("completed", "policy_failure"):
            require(meta.get("status") == "completed" and meta.get("model") == "gpt-5.6-luna"
                    and meta.get("provider") == "luna_research"
                    and type(meta.get("tool_events_observed")) is int and meta["tool_events_observed"] == 0
                    and type(meta.get("provider_generation_count_observed")) is int
                    and meta["provider_generation_count_observed"] == 1,
                    "Completed response lacks clean transport evidence")
    require(type(summary.get("model_requests")) is int and summary["model_requests"] == attempts, "Model dispatch count mismatch")
    budget_snapshot(summary.get("credit_budget"), cap=cap, attempts=attempts,
                    settled_count=settled_count, failed_count=failed_count, spent=spent, uncertain=uncertain)
    return {"usage_totals": dict(totals), "settled_credit_equivalent": str(spent),
            "retained_credit_equivalent": str(uncertain)}


def audit(run_dir, *, allow_fake=False):
    run_dir = Path(run_dir)
    manifest, ledger, summary = [strict_json((run_dir / name).read_text(encoding="utf-8"))
                                 for name in ("manifest.json", "requests.json", "summary.json")]
    require(digest(manifest) == summary.get("manifest_sha256"), "Manifest hash mismatch")
    require(digest(ledger) == summary.get("request_audit_sha256"), "Request audit hash mismatch")
    plan = manifest["plan"]
    require(digest(plan) == manifest.get("plan_sha256"), "Plan hash mismatch")
    hash_map(plan.get("source_sha256"))
    expected_plan = make_plan()
    # Source fingerprints describe the historical run; do not require current
    # source files to have remained unchanged since the evidence was saved.
    require({k: v for k, v in plan.items() if k != "source_sha256"}
            == {k: v for k, v in expected_plan.items() if k != "source_sha256"}, "Frozen plan differs from v1 schedule")
    require(manifest.get("version") == summary.get("version") == plan["version"], "Version mismatch")
    fake = manifest.get("fake")
    require(type(fake) is bool and summary.get("fake") is fake and (not fake or allow_fake),
            "Fake evidence requires explicit allow_fake")
    cap = manifest.get("request_cap")
    require(type(cap) is int and 0 <= cap <= 24 and summary.get("request_cap") == cap, "Invalid request cap")
    require(manifest.get("heldout_requests") == summary.get("heldout_requests") == 0, "Unexpected held-out calls")
    require(type(ledger) is list and len(ledger) <= cap and summary.get("request_attempts") == len(ledger), "Attempt count mismatch")
    require(type(summary.get("rows")) is list and len(summary["rows"]) == summary.get("planned_cases") == 24,
            "All 24 scheduled denominators must be retained")
    attempts = Counter()
    terminal_failure = False
    for index, (case, row) in enumerate(zip(plan["cases"], summary["rows"])):
        require({k: row.get(k) for k in ("case_id", "fixture", "order", "refresh_rule")}
                == {k: case[k] for k in ("case_id", "fixture", "order", "refresh_rule")}, "Case schedule mismatch")
        if index >= len(ledger):
            require(row.get("status") == "incomplete" and row.get("grade") is None
                    and row.get("displayed_positions") is None, "Missing request was imputed as an outcome")
            continue
        require(not terminal_failure, "Request dispatched after a transport failure")
        attempt = ledger[index]
        require(attempt.get("attempt") == index + 1 and attempt.get("case_id") == case["case_id"], "Attempt order mismatch")
        raw = attempt["request_utf8"].encode("utf-8")
        require(raw == request_bytes(case["request"]) == request_bytes(strict_json(raw.decode())), "Request differs from frozen public input")
        require(hashlib.sha256(raw).hexdigest() == attempt.get("request_sha256") == case["request_sha256"]
                and attempt.get("request_bytes") == len(raw), "Public request hash or byte count mismatch")
        status = attempt.get("status")
        require(status in ("completed", "policy_failure", "transport_failure") and row.get("status") == status, "Invalid attempt status")
        require(type(attempt.get("provider_metadata")) is dict, "Missing provider metadata")
        latency = attempt.get("latency_seconds")
        require(latency is None if fake else type(latency) in (int, float) and latency >= 0, "Invalid latency accounting")
        attempts[status] += 1
        if status == "transport_failure":
            terminal_failure = True
            require(attempt.get("response") is None, "Transport failure contains an accepted response")
        else:
            try:
                keys = validate_response(attempt.get("response"), case["request"])
            except (ValueError, TypeError, KeyError):
                require(status == "policy_failure", "Completed response fails host schema")
            else:
                require(status == "completed", "Valid response labeled as policy failure")
                require(row.get("grade") == independent_grade(keys, case["refresh_rule"]), "Grade differs from independent route enumeration")
                positions = {r["key"]: i + 1 for i, r in enumerate(case["request"]["visible_records"])}
                require(row.get("displayed_positions") == [positions[key] for key in keys], "Displayed selection positions mismatch")
        if status != "completed":
            require(row.get("grade") is None and row.get("displayed_positions") is None, "Failure imputed as a grade")
            require(type(attempt.get("error_type")) is str and attempt["error_type"], "Missing failure category")
    require(len(ledger) == cap or terminal_failure, "Unexplained early stop")
    expected_counts = {key: attempts[key] for key in ("completed", "policy_failure", "transport_failure", "reserved")}
    require(summary.get("attempt_status_counts") == expected_counts, "Attempt status totals mismatch")
    for name, value in aggregate(summary["rows"]).items():
        require(summary.get(name) == value, "Aggregate mismatch: " + name)
    accounting = {}
    if fake:
        require(type(summary.get("model_requests")) is int and summary["model_requests"] == 0
                and all(not row["provider_metadata"] for row in ledger), "Fake run reports provider activity")
    else:
        accounting = live_accounting(ledger, summary, manifest, cap)
    return {"version": "revision_run_evidence_audit_v1", "passed": True, "fake": fake,
            "planned_cases_checked": 24, "requests_checked": len(ledger),
            "model_requests": summary["model_requests"],
            "manifest_sha256": digest(manifest), "request_audit_sha256": digest(ledger),
            "status_counts": expected_counts, "source_hash_policy": "historical format only",
            "new_model_requests": 0, **accounting}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-dir", type=Path, required=True)
    parser.add_argument("--allow-fake", action="store_true")
    args = parser.parse_args()
    print(json.dumps(audit(args.run_dir, allow_fake=args.allow_fake), indent=2))


if __name__ == "__main__":
    main()
