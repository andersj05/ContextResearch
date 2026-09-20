"""Read-only saved-evidence audit for the 1,536-request transfer study.

No provider client is instantiated. Live evidence requires an explicit frozen
Git commit; source bytes are compared with raw Git blobs, never the checkout.
Route grading and accounting are independent; aggregate/report regeneration
uses the study's declared analysis implementation.
"""
from __future__ import annotations

import argparse
from collections import Counter
from decimal import Decimal
from fractions import Fraction
import hashlib
from itertools import combinations, product
import json
from pathlib import Path, PurePosixPath
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "experiments/dependency_memory"))
from luna_appserver import strict_json
from luna_isolation import wire_body_byte_bound
from transfer_interface import request_bytes, validate_response
import transfer_study as study

RESERVATION = Decimal("10.4025")
WORKER_CREDITS = Decimal(50)
TOTAL_CREDITS = Decimal(200)
FACTORS = ("jobs", "framing", "guarantee", "guidance", "refresh_rule")
FACTOR_VALUES = ((6, 12), ("compact", "workflow"), ("explicit_optimal", "unspecified"),
                 ("generic", "prospective"), ("first", "last", "none"))
STATUSES = ("completed", "policy_failure", "transport_failure", "reserved")
TOKEN_NAMES = ("input_tokens", "cached_input_tokens", "output_tokens",
               "reasoning_output_tokens", "cache_write_input_tokens")


def require(condition, message):
    if not condition:
        raise ValueError(message)


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"),
        ensure_ascii=False, allow_nan=False).encode("utf-8")).hexdigest()


def hash_map(value):
    require(type(value) is dict and value, "Missing source provenance")
    for name, sha in value.items():
        path = PurePosixPath(name) if type(name) is str else None
        require(path is not None and name and not path.is_absolute()
                and ".." not in path.parts and not any(c in name for c in "\\:\r\n")
                and type(sha) is str and re.fullmatch(r"[0-9a-f]{64}", sha),
                "Malformed source provenance hash or path")


def verify_source_commit(hashes, commit, root=ROOT):
    """Read all committed blobs in one subprocess; preserve exact CR/LF bytes."""
    hash_map(hashes)
    require(type(commit) is str and re.fullmatch(r"[0-9a-fA-F]{7,40}", commit),
            "Live evidence requires --source-commit with the frozen Git commit hash")
    root = Path(root).resolve()
    git = ["git", "-c", "safe.directory=" + root.as_posix()]
    resolved = subprocess.run([*git, "rev-parse", "--verify", commit + "^{commit}"],
        cwd=root, capture_output=True, check=False)
    require(resolved.returncode == 0, "Frozen source commit does not resolve")
    full = resolved.stdout.decode("ascii").strip()
    names = list(hashes)
    result = subprocess.run([*git, "cat-file", "--batch"], cwd=root,
        input="".join(full + ":" + name + "\n" for name in names).encode("utf-8"),
        capture_output=True, check=False)
    require(result.returncode == 0, "Cannot read frozen Git source blobs")
    offset = 0
    for name in names:
        end = result.stdout.find(b"\n", offset)
        require(end >= offset, "Truncated Git blob response")
        header = result.stdout[offset:end].split()
        require(len(header) == 3 and header[1] == b"blob" and header[2].isdigit(),
                "Missing frozen source blob: " + name)
        size = int(header[2])
        raw = result.stdout[end + 1:end + 1 + size]
        require(len(raw) == size and result.stdout[end + 1 + size:end + 2 + size] == b"\n",
                "Truncated frozen source blob: " + name)
        require(hashlib.sha256(raw).hexdigest() == hashes[name],
                "Frozen source hash mismatch: " + name)
        offset = end + size + 2
    require(offset == len(result.stdout), "Unexpected trailing Git blob output")
    return {"source_commit": full, "source_blobs_checked": len(names),
            "source_hash_policy": "raw Git blobs at explicit frozen commit"}


def independent_grade(keys, case):
    """Enumerate every target route and every full parent pair independently."""
    request = case["request"]
    priorities = {r["key"]: r["refresh_priority"] for r in request["public_metadata"]["jobs"]}
    jobs = tuple(priorities)
    rule = case["refresh_rule"]
    routes = []
    for pair in combinations(jobs, 2):
        refresh = None if rule == "none" else (min if rule == "first" else max)(pair, key=priorities.get)
        routes.extend((target, refresh) for target in pair)

    def score(selected):
        return Fraction(sum(target == refresh or target in selected for target, refresh in routes), len(routes))

    possibilities = [score(set(pair)) for pair in combinations(jobs, 2)]
    best, worst = max(possibilities), min(possibilities)
    availability = score(set(keys))
    span = best - worst if rule != "none" else None
    regret = best - availability
    return {"keys": list(keys), "selected_priorities": [priorities[k] for k in keys],
        "selected_count": len(keys), "availability": str(availability),
        "reference_availability": str(best), "exact_parent_regret": str(regret),
        "optimal_parent": regret == 0, "normalized_regret": str(regret / span) if span else None,
        "full_pair_regret_span": str(span) if span else None,
        "route_count": len(routes), "downstream_reference": "optimal_child"}


def amount(record, name, expected):
    require(type(record.get(name)) in (int, float) and Decimal(str(record[name])) == expected,
            "Credit amount mismatch: " + name)
    require(type(record.get(name + "_exact")) is str and Decimal(record[name + "_exact"]) == expected,
            "Exact credit amount mismatch: " + name)


def budget_snapshot(snapshot, *, attempts, settled_count, failed_count, spent, uncertain):
    require(type(snapshot) is dict, "Missing worker credit snapshot")
    committed = spent + uncertain
    for name, expected in (("cap_credit_equivalent", WORKER_CREDITS),
            ("per_attempt_reservation", RESERVATION), ("committed_credit_equivalent", committed),
            ("settled_credit_equivalent", spent), ("uncertain_credit_reservations", uncertain),
            ("remaining_credit_equivalent", WORKER_CREDITS - committed)):
        amount(snapshot, name, expected)
    require(Decimal(0) <= committed <= WORKER_CREDITS, "Worker credit cap exceeded")
    for name, expected in (("generation_attempts", attempts), ("generation_attempt_ceiling", 384),
            ("settled_attempts", settled_count), ("failed_attempts", failed_count),
            ("api_dollar_spend_authorized", 0), ("credit_purchases", 0), ("reset_redemptions", 0)):
        require(type(snapshot.get(name)) is int and snapshot[name] == expected, "Budget counter mismatch: " + name)
    require(snapshot.get("pending_ticket") is None and snapshot.get("stopped") is (failed_count > 0)
            and snapshot.get("api_key_fallback") is False, "Unsafe or unfinished worker budget state")


def usage_totals(ledger):
    result = {}
    for name in TOKEN_NAMES:
        values = [r["provider_metadata"].get("usage", {}).get(name) for r in ledger]
        measured = [v for v in values if type(v) is int and v >= 0]
        result[name] = {"reported": sum(measured) if measured else None, "measured_attempts": len(measured)}
    return result


def quota_allows_generation(snapshot, ceiling):
    """Independent interpretation of the recorded normalized quota snapshot."""
    if type(snapshot) is not dict or not snapshot:
        return False
    observed = False
    for row in snapshot.values():
        if type(row) is not dict or row.get("rateLimitReachedType") is not None or row.get("spendControlReached") is True:
            return False
        individual = row.get("individualLimit")
        if individual and (type(individual) is not dict
                           or type(individual.get("remainingPercent")) not in (int, float)
                           or individual["remainingPercent"] <= 0):
            return False
        for name in ("primary", "secondary"):
            window = row.get(name)
            if window is not None:
                if (type(window) is not dict or type(window.get("usedPercent")) not in (int, float)
                        or not 0 <= window["usedPercent"] < ceiling):
                    return False
                observed = True
    return observed


def live_accounting(ledger, summary, manifest, plan, thread_ids):
    transport = manifest.get("transport")
    require(type(transport) is dict and transport == summary.get("transport_manifest"), "Transport manifest mismatch")
    require(transport.get("worker") == manifest["worker"] and transport.get("model") == "gpt-5.6-luna"
            and transport.get("experiment_version") == "transfer_study_v1", "Unexpected worker/model/experiment transport")
    require(transport.get("approved_plan_sha256") == digest(plan), "Approved plan hash mismatch")
    require(transport.get("source_sha256") == plan["source_sha256"], "Transport source provenance mismatch")
    hash_map({name: transport.get(name) for name in ("cli_sha256", "isolation_profile_sha256",
              "global_instructions_sha256", "advertised_model_sha256")})
    require(digest(transport.get("advertised_model")) == transport["advertised_model_sha256"], "Advertised model hash mismatch")
    require(transport.get("provider") == "luna_research" and transport.get("reasoning_effort") == "low"
            and transport.get("service_tier") == "default" and transport.get("http_and_stream_retries") == 0
            and transport.get("maximum_wire_body_bytes") == 32768, "Transport contract drift")
    # The original zero-generation launch used the historical 80% headroom
    # guard, with no explicit quota_guard_used_percent field. The amendment
    # pins 100% for this transfer allocation; provider denial still stops it.
    amended_quota = "quota_guard_used_percent" in transport
    quota_ceiling = transport.get("quota_guard_used_percent", 80)
    require(type(quota_ceiling) is int and quota_ceiling == (100 if amended_quota else 80)
            and transport.get("account_quota_stop_used_percent", 80) == quota_ceiling,
            "Unexpected declared transfer quota ceiling")
    require(type(manifest.get("authorization")) is str and manifest["authorization"].strip(), "Missing allocation note")
    budget_snapshot(transport.get("budget"), attempts=0, settled_count=0, failed_count=0,
                    spent=Decimal(0), uncertain=Decimal(0))
    spent = uncertain = Decimal(0)
    attempts = settled_count = failed_count = 0
    for row in ledger:
        meta = row["provider_metadata"]
        if amended_quota and meta:
            # A shared-stop admission rejection may occur before client.complete
            # creates metadata. Once client metadata exists its ceiling is fixed.
            require(meta.get("quota_guard_used_percent") == quota_ceiling,
                    "Attempt quota ceiling differs from declared transport")
        dispatched = meta.get("dispatched", False)
        require(type(dispatched) is bool, "Invalid dispatch flag")
        thread = meta.get("thread_id")
        if thread is not None:
            require(type(thread) is str and thread and thread not in thread_ids, "Missing or duplicate thread id")
            thread_ids.add(thread)
        if not dispatched:
            require(row["status"] == "transport_failure" and "credit_accounting" not in meta,
                    "Undispatched attempt was completed or charged")
            continue
        require(thread is not None, "Dispatched request lacks fresh thread id")
        if amended_quota:
            require(quota_allows_generation(meta.get("quota_before"), quota_ceiling),
                    "Dispatched request lacked eligible preflight quota evidence")
        require(not failed_count and spent + RESERVATION <= WORKER_CREDITS, "Dispatch exceeded worker reservation")
        attempts += 1
        require(type(meta.get("wire_body_byte_bound")) is int and meta["wire_body_byte_bound"]
                == wire_body_byte_bound(strict_json(row["request_utf8"])) <= 32768, "Request wire bound mismatch")
        require(type(meta.get("attempt_ticket")) is int and meta["attempt_ticket"] == attempts, "Generation ticket mismatch")
        accounting = meta.get("credit_accounting", {})
        require(type(accounting.get("ticket")) is int and accounting["ticket"] == attempts, "Accounting ticket mismatch")
        if accounting.get("status") == "settled":
            usage = meta.get("usage", {})
            for name in TOKEN_NAMES[:4]:
                require(type(usage.get(name)) is int and usage[name] >= 0, "Invalid token usage")
            inputs, cached, outputs, reasoning = (usage[k] for k in TOKEN_NAMES[:4])
            writes = usage.get("cache_write_input_tokens")
            require(writes is None or type(writes) is int and writes >= 0, "Invalid cache-write usage")
            require(0 < inputs < 272000 and cached + (writes or 0) <= inputs
                    and reasoning <= outputs <= 128000, "Token accounting envelope violated")
            expected = {"inputTokens": inputs, "cachedInputTokens": cached,
                "cacheWriteInputTokens": writes, "outputTokens": outputs,
                "reasoningOutputTokens": reasoning, "totalTokens": inputs + outputs}
            require(accounting.get("usage") == expected, "Token accounting differs from provider usage")
            require(accounting.get("cache_write_tokens_reported") is (writes is not None)
                    and accounting.get("cache_write_pricing_unresolved") is (writes is None or writes > 0),
                    "Unknown cache-write usage was misreported")
            actual = (Decimal(inputs) * Decimal("6.25") + Decimal(outputs) * 30) / 1000000
            basic = (Decimal(inputs - cached) * 5 + Decimal(cached) / 2 + Decimal(outputs) * 30) / 1000000
            amount(accounting, "conservative_credit_equivalent", actual)
            amount(accounting, "basic_rate_credit_estimate", basic)
            amount(accounting, "released_credit_equivalent", RESERVATION - actual)
            require(accounting.get("reasoning_already_in_output") is True
                    and accounting.get("observed_credit_balance_debit") is None
                    and accounting.get("observed_dollar_charge") is None, "Unsupported debit claim or double-counted reasoning")
            require(meta.get("harness_termination") == "session_budget_exceeded", "Missing one-generation guard")
            spent += actual
            settled_count += 1
        elif accounting.get("status") == "reservation_retained":
            require(row["status"] == "transport_failure", "Retained reservation without transport failure")
            uncertain += RESERVATION
            failed_count += 1
        else:
            raise ValueError("Dispatched attempt has no settled or retained accounting")
        budget_snapshot(accounting.get("budget"), attempts=attempts, settled_count=settled_count,
                        failed_count=failed_count, spent=spent, uncertain=uncertain)
        if row["status"] in ("completed", "policy_failure"):
            require(accounting.get("status") == "settled" and meta.get("status") == "completed"
                    and meta.get("model") == "gpt-5.6-luna" and meta.get("provider") == "luna_research"
                    and type(meta.get("tool_events_observed")) is int and meta["tool_events_observed"] == 0
                    and type(meta.get("provider_generation_count_observed")) is int
                    and meta["provider_generation_count_observed"] == 1, "Response lacks clean completed transport evidence")
            if amended_quota:
                require(quota_allows_generation(meta.get("quota_after"), quota_ceiling),
                        "Accepted response lacked eligible post-generation quota evidence")
    require(type(summary.get("model_requests")) is int and summary["model_requests"] == attempts, "Worker dispatch count mismatch")
    budget_snapshot(summary.get("credit_budget"), attempts=attempts, settled_count=settled_count,
                    failed_count=failed_count, spent=spent, uncertain=uncertain)
    return spent, uncertain


def check_plan(plan):
    require(type(plan) is dict, "Missing frozen plan")
    hash_map(plan.get("source_sha256"))
    required_sources = {"experiments/dependency_memory/" + name for name in
        ("transfer_interface.py", "transfer_study.py", "run_transfer_study.py",
         "request_contracts.py", "luna_appserver.py", "luna_budget.py", "luna_isolation.py")}
    require(required_sources <= set(plan["source_sha256"]), "Missing essential source fingerprints")
    expected = study.make_plan()
    require({k: v for k, v in plan.items() if k != "source_sha256"}
            == {k: v for k, v in expected.items() if k != "source_sha256"}, "Frozen plan differs from declared schedule")
    for field, value in (("maximum_model_requests", 1536), ("planned_cases", 1536), ("blocks", 32),
            ("conditions_per_block", 48), ("workers", 4), ("worker_request_cap", 384),
            ("credit_equivalent_cap", 200), ("worker_credit_equivalent_cap", 50),
            ("additional_api_dollars", 0), ("purchases", 0), ("reset_redemptions", 0),
            ("heldout_requests", 0), ("realized_routes_sampled", 0)):
        require(type(plan.get(field)) is int and plan[field] == value, "Plan allocation mismatch: " + field)
    cases = plan["cases"]
    require(len(cases) == len({c["case_id"] for c in cases}) == 1536, "Plan must retain 1536 unique scheduled cases")
    for block in range(32):
        group = [case for case in cases if case["block"] == block]
        require(Counter(tuple(c[k] for k in FACTORS) for c in group)
                == Counter(product(*FACTOR_VALUES)), "Incomplete or repeated factorial block")
        require(all(c["worker"] == block % 4 for c in group), "Wrong block-to-worker assignment")
    for case in cases:
        raw = request_bytes(case["request"])
        require(case["request_sha256"] == hashlib.sha256(raw).hexdigest()
                and case["request_bytes"] == len(raw), "Frozen request hash or byte count mismatch")


def audit(run_dir, *, allow_fake=False, frozen_commit=None, source_commit=None):
    directory = Path(run_dir)
    load = lambda path: strict_json(path.read_text(encoding="utf-8"))
    manifest, summary = load(directory / "manifest.json"), load(directory / "summary.json")
    require(digest(manifest) == summary.get("manifest_sha256"), "Aggregate manifest hash mismatch")
    plan = manifest.get("plan")
    check_plan(plan)
    require(digest(plan) == manifest.get("plan_sha256"), "Plan hash mismatch")
    require(manifest.get("version") == summary.get("version") == plan["version"] == "transfer_study_v1", "Version mismatch")
    fake = manifest.get("fake")
    require(type(fake) is bool and summary.get("fake") is fake and (not fake or allow_fake), "Fake evidence requires explicit allow_fake")
    cap = manifest.get("per_worker_request_cap")
    require(type(cap) is int and 0 <= cap <= 384 and (fake or cap == 384), "Invalid per-worker request cap")
    require(manifest.get("worker_count") == 4 and manifest.get("request_cap") == summary.get("request_cap") == 4 * cap
            and manifest.get("credit_equivalent_cap") == 200
            and manifest.get("per_worker_credit_equivalent_cap") == 50, "Aggregate allocation mismatch")
    require(manifest.get("heldout_requests") == summary.get("heldout_requests") == 0, "Unexpected held-out requests")
    provenance = {"source_hash_policy": "format only for explicitly allowed fake evidence", "source_blobs_checked": 0}
    require(frozen_commit is None or source_commit is None or frozen_commit == source_commit,
            "Conflicting frozen source commits")
    explicit_commit = frozen_commit or source_commit
    saved_commit = manifest.get("source_commit")
    if explicit_commit is not None and saved_commit is not None:
        require(saved_commit.startswith(explicit_commit) or explicit_commit.startswith(saved_commit),
                "Explicit source commit differs from saved launch commit")
    selected_commit = explicit_commit or saved_commit
    if not fake or selected_commit is not None:
        require(fake or plan.get("protocol_and_wire_audit_present") is True, "Live plan lacks reviewed protocol and wire audit")
        provenance = verify_source_commit(plan["source_sha256"], selected_commit)
        if not fake and saved_commit is not None:
            require(manifest.get("fingerprinted_sources_match_commit") is True,
                    "Launch did not verify fingerprinted source commit")
    worker_summaries, all_attempts, all_rows = [], [], {}
    threads = set()
    spent = uncertain = Decimal(0)
    for worker in range(4):
        worker_dir = directory / f"worker-{worker}"
        wm, ledger, ws = (load(worker_dir / name) for name in ("manifest.json", "requests.json", "summary.json"))
        cases = [c for c in plan["cases"] if c["worker"] == worker]
        require(wm.get("version") == ws.get("version") == plan["version"] and wm.get("worker") == ws.get("worker") == worker
                and wm.get("fake") is ws.get("fake") is fake, "Worker identity mismatch")
        require(wm.get("aggregate_manifest_sha256") == digest(manifest) and wm.get("plan_sha256") == digest(plan)
                and wm.get("cases") == cases, "Worker manifest differs from aggregate plan")
        require(digest(wm) == ws.get("manifest_sha256") and digest(ledger) == ws.get("request_audit_sha256"), "Worker evidence hash mismatch")
        require(wm.get("request_cap") == ws.get("request_cap") == cap and wm.get("credit_equivalent_cap") == 50
                and wm.get("heldout_requests") == ws.get("heldout_requests") == 0, "Worker allocation mismatch")
        require(type(ledger) is list and len(ledger) <= cap and ws.get("request_attempts") == len(ledger), "Worker attempt count mismatch")
        require(type(ws.get("rows")) is list and len(ws["rows"]) == ws.get("planned_cases") == 384, "All 384 worker outcomes must be retained")
        terminal = False
        for index, (case, row) in enumerate(zip(cases, ws["rows"])):
            fields = {k: v for k, v in case.items() if k not in ("request", "request_sha256")}
            require({k: row.get(k) for k in fields} == fields, "Worker case schedule mismatch")
            all_rows[case["case_id"]] = row
            if index >= len(ledger):
                require(row.get("status") == "incomplete" and row.get("grade") is None
                        and row.get("displayed_positions") is None, "Missing request imputed as an outcome")
                continue
            require(not terminal, "Worker continued after transport failure")
            attempt = ledger[index]
            require(attempt.get("attempt") == index + 1 and attempt.get("case_id") == case["case_id"]
                    and attempt.get("worker") == worker and attempt.get("block") == case["block"], "Attempt order mismatch")
            raw = attempt["request_utf8"].encode("utf-8")
            require(raw == request_bytes(case["request"]) == request_bytes(strict_json(raw.decode("utf-8"))), "Request differs from frozen public input")
            require(hashlib.sha256(raw).hexdigest() == attempt.get("request_sha256") == case["request_sha256"]
                    and attempt.get("request_bytes") == len(raw), "Public request hash or byte count mismatch")
            status = attempt.get("status")
            require(status in STATUSES[:3] and row.get("status") == status, "Invalid or unfinished attempt status")
            require(type(attempt.get("provider_metadata")) is dict, "Missing provider metadata")
            latency = attempt.get("latency_seconds")
            require(latency is None if fake else type(latency) in (int, float) and latency >= 0, "Invalid latency accounting")
            if status == "transport_failure":
                terminal = True
                require(attempt.get("response") is None, "Transport failure contains accepted response")
            else:
                try:
                    selected = validate_response(attempt.get("response"), case["request"])
                except (ValueError, TypeError, KeyError):
                    require(status == "policy_failure", "Completed response fails host schema")
                else:
                    require(status == "completed", "Valid response labeled policy failure")
                    require(row.get("grade") == independent_grade(selected, case), "Grade differs from independent route enumeration")
                    positions = {r["key"]: i + 1 for i, r in enumerate(case["request"]["visible_records"])}
                    require(row.get("displayed_positions") == [positions[k] for k in selected], "Displayed positions mismatch")
            if status != "completed":
                require(row.get("grade") is None and row.get("displayed_positions") is None, "Failure imputed as a grade")
                require(type(attempt.get("error_type")) is str and attempt["error_type"], "Missing failure category")
                if not fake and attempt["error_type"] == "ResponseFormatError":
                    meta = attempt["provider_metadata"]
                    require(status == "policy_failure" and attempt.get("response") is None
                            and meta.get("response_status") == "invalid_json"
                            and meta.get("credit_accounting", {}).get("status") == "settled", "Malformed answer lacks settled response-format evidence")
        require(len(ledger) == cap or summary.get("shared_stop") is True, "Unexplained worker early stop")
        require(ws.get("attempt_status_counts") == {s: sum(r["status"] == s for r in ledger) for s in STATUSES}, "Worker status count mismatch")
        require(ws.get("usage_totals") == usage_totals(ledger), "Worker usage totals mismatch")
        if fake:
            require(ws.get("model_requests") == 0 and all(not r["provider_metadata"] for r in ledger), "Fake evidence reports provider activity")
        else:
            require(wm.get("authorization") == manifest.get("authorization"), "Worker allocation note mismatch")
            if saved_commit is not None:
                require(wm.get("source_commit") == saved_commit
                        and wm.get("transport", {}).get("source_commit") == saved_commit
                        and wm.get("transport", {}).get("fingerprinted_sources_match_commit") is True,
                        "Worker frozen source commit mismatch")
            require(type(manifest.get("worker_transports")) is list and len(manifest["worker_transports"]) == 4
                    and wm.get("transport") == manifest["worker_transports"][worker], "Worker transport differs from aggregate")
            worker_spent, worker_uncertain = live_accounting(ledger, ws, wm, plan, threads)
            spent += worker_spent
            uncertain += worker_uncertain
        worker_summaries.append(ws)
        all_attempts.extend(ledger)
    require(summary.get("worker_summaries") == worker_summaries, "Aggregate worker summaries mismatch")
    require(summary.get("rows") == [all_rows[c["case_id"]] for c in plan["cases"]]
            and summary.get("planned_cases") == 1536, "All 1536 aggregate scheduled outcomes must be retained")
    counts = {s: sum(r["status"] == s for r in all_attempts) for s in STATUSES}
    require(summary.get("attempt_status_counts") == counts and summary.get("request_attempts") == len(all_attempts), "Aggregate attempt counts mismatch")
    require(type(summary.get("shared_stop")) is bool and summary["shared_stop"] is (counts["transport_failure"] > 0), "Shared-stop state inconsistent with recorded failures")
    require(summary.get("usage_totals") == usage_totals(all_attempts), "Aggregate usage totals mismatch")
    dispatched = sum(ws["model_requests"] for ws in worker_summaries)
    require(type(summary.get("model_requests")) is int and summary["model_requests"] == dispatched <= 1536, "Aggregate model-request count mismatch")
    regenerated_analysis = study.aggregate(summary["rows"])
    for name, value in regenerated_analysis.items():
        require(summary.get(name) == value, "Aggregate analysis mismatch: " + name)
    # Saved JSON sorts object keys; the Markdown writer displays some mappings
    # using insertion order. Rebuild those mappings from rows before rendering.
    require((directory / "report.md").read_text(encoding="utf-8")
            == study.report({**summary, **regenerated_analysis}), "Saved report differs from regenerated analysis")
    if not fake:
        require(spent + uncertain <= TOTAL_CREDITS, "Aggregate credit cap exceeded")
        for name, value in (("cap_credit_equivalent", TOTAL_CREDITS), ("settled_credit_equivalent", spent),
                ("uncertain_credit_reservations", uncertain), ("committed_credit_equivalent", spent + uncertain),
                ("remaining_credit_equivalent", TOTAL_CREDITS - spent - uncertain)):
            amount(summary.get("credit_budget", {}), name, value)
    return {"version": "transfer_run_evidence_audit_v1", "passed": True, "fake": fake,
        "planned_cases_checked": 1536, "requests_checked": len(all_attempts), "model_requests": dispatched,
        "unique_threads_checked": len(threads), "status_counts": counts, "usage_totals": usage_totals(all_attempts),
        "settled_credit_equivalent": str(spent), "retained_credit_equivalent": str(uncertain),
        "manifest_sha256": digest(manifest), "summary_sha256": digest(summary),
        "auditor_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "new_model_requests": 0, **provenance,
        "limitations": "Local saved-evidence consistency audit; cannot authenticate inaccessible provider internals or actual subscription debit. Cross-worker dispatch chronology is not present in these ledgers; the shared-stop gate is covered by runner tests."}


def audit_allocation(run_dirs, *, allow_fake=False):
    """Reconcile unchanged public cases after zero-generation preflight launches.

    Host preflight attempts do not consume model-request allocations. This does
    not permit resuming or replacing a run that already generated model answers.
    """
    directories = [Path(path).resolve() for path in run_dirs]
    require(directories and len(set(directories)) == len(directories), "Allocation directories must be unique")
    results = [audit(directory, allow_fake=allow_fake) for directory in directories]
    require(all(result["model_requests"] == 0 for result in results[:-1]),
            "Only zero-generation preflight launches may precede the active allocation")
    public_cases = []
    for directory in directories:
        manifest = strict_json((directory / "manifest.json").read_text(encoding="utf-8"))
        public_cases.append([(case["case_id"], case["request_sha256"]) for case in manifest["plan"]["cases"]])
    require(all(cases == public_cases[0] for cases in public_cases), "Public requests changed between allocation launches")
    generations = sum(result["model_requests"] for result in results)
    spent = sum((Decimal(result["settled_credit_equivalent"]) for result in results), Decimal(0))
    uncertain = sum((Decimal(result["retained_credit_equivalent"]) for result in results), Decimal(0))
    require(generations <= 1536 and spent + uncertain <= TOTAL_CREDITS, "Combined allocation cap exceeded")
    return {"version": "transfer_allocation_evidence_audit_v1", "passed": True,
        "run_count": len(results), "requests_checked": sum(result["requests_checked"] for result in results),
        "model_requests": generations, "model_request_cap": 1536,
        "settled_credit_equivalent": str(spent), "retained_credit_equivalent": str(uncertain),
        "credit_equivalent_cap": 200, "public_cases_unchanged": True,
        "new_model_requests": 0, "runs": results}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-dir", required=True, type=Path)
    parser.add_argument("--allow-fake", action="store_true")
    parser.add_argument("--source-commit")
    parser.add_argument("--prior-run-dir", action="append", default=[], type=Path)
    args = parser.parse_args()
    if args.prior_run_dir:
        require(args.source_commit is None, "Allocation audit reads each manifest's distinct source commit")
        result = audit_allocation([*args.prior_run_dir, args.run_dir], allow_fake=args.allow_fake)
    else:
        result = audit(args.run_dir, allow_fake=args.allow_fake, frozen_commit=args.source_commit)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
