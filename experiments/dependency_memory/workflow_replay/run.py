"""Regenerate historical workflow replay results without models or network."""
from __future__ import annotations

from copy import deepcopy
from itertools import combinations
import hashlib
import json
from pathlib import Path

from .evidence import (HASHES, HISTORICAL_COMMIT, historical_classifier,
                       load_snapshot, make_scoped_receipt, original_decision, reuse_receipt, wire)
from .replay import Archive, METHODS, continue_route, entry_for, Meter, prepare

HERE = Path(__file__).resolve().parent
RESULTS = HERE.parent / "results"
CAPACITIES = ((512, 256), (1024, 512), (1536, 768), (2048, 1024), (4096, 2048))
EXTRAS = (1024, 4096, 16384, 65536)
PRICES = (0, 128, 1024)
ARCHIVES = ("none", "full", "projected")


def routes(records):
    return [(pair, row) for pair in combinations(range(4), 2)
            for row in records if row["worker"] in pair]


def expected_action(row, reference):
    result = reference(row)
    return {"case_id": row["case_id"], "request_sha256": row["request_sha256"],
            "classification": result[0], "settled": result[1], "reserved": result[2]}


def evaluate(records, reference, method, capacities, extra, check_price, archive, detailed=False):
    initial = prepare(records, method, capacities[0], extra, check_price, reference)
    return [continue_route(initial, pair, row["case_id"], capacities[1], archive,
                           expected_action(row, reference), detailed=detailed)
            for pair, row in routes(records)]


def aggregate(rows):
    return {"routes": len(rows), "successful": sum(r["success"] for r in rows),
            "pre_recovery_available": sum(r["pre_recovery_available"] for r in rows),
            "budget_rejections": sum(r["budget_rejected_at"] is not None for r in rows),
            "total_cost": sum(r["cost"] for r in rows),
            "total_bytes": sum(r["bytes"] for r in rows),
            "total_checks": sum(r["checks"] for r in rows),
            "total_tool_calls": sum(r["tool_calls"] for r in rows),
            "max_parent_bytes": max(r["parent_bytes"] or 0 for r in rows),
            "max_child_bytes": max(r["child_bytes"] or 0 for r in rows)}


def frontier(unlimited, common):
    thresholds = sorted({r["cost"] for rows in unlimited.values() for r in rows if r["success"]})
    points = []
    for allowance in thresholds:
        successes = {m: sum(r["success"] and r["cost"] <= allowance for r in rows)
                     for m, rows in unlimited.items()}
        points.append({"total_allowance": allowance, "extra_allowance": allowance - common,
                       "successes": successes})
    # Retain all changes and their exact thresholds, including adverse regions.
    return points


def cache_controls(records, reference):
    metered = next(r for r in records if r["status"] == "transport_failure"
                   and r["provider_metadata"].get("dispatched") is True)
    preflight = next(r for r in records if r["provider_metadata"].get("dispatched") is False)
    edits = []

    def add(name, original, edit, *, revision="checker-v1"):
        changed = deepcopy(original)
        edit(changed)
        edits.append((name, original, changed, revision))

    add("unchanged", metered, lambda r: None)
    add("irrelevant_latency", metered, lambda r: r.update(latency_seconds=999.0))
    add("irrelevant_quota_metadata", metered,
        lambda r: r["provider_metadata"].update(quota_before={"annotation": "edited"}))
    add("settlement_changed", metered,
        lambda r: r["provider_metadata"]["credit_accounting"].update(conservative_credit_equivalent_exact="0.05"))
    add("reservation_ticket_invalidated", metered,
        lambda r: r["provider_metadata"].update(attempt_ticket=0))
    add("absent_usage_becomes_present", preflight,
        lambda r: r["provider_metadata"].update(usage=None))
    add("absent_turn_becomes_present", preflight,
        lambda r: r["provider_metadata"].update(turn_id="new-turn"))
    add("case_identity_changed", metered, lambda r: r.update(case_id=r["case_id"] + "-changed"))
    add("request_hash_changed", metered, lambda r: r.update(request_sha256="a" * 64))
    add("payload_changed_without_hash_update", metered, lambda r: r.update(request_utf8=r["request_utf8"] + " "))
    add("checker_changed", metered, lambda r: None, revision="checker-v2")
    result = []
    for name, original, changed, revision in edits:
        receipt = make_scoped_receipt(original, "checker-v1")
        reused = reuse_receipt(receipt, changed, revision)
        result.append({"control": name, "synthetic_edit_to_historical_record": name != "unchanged",
            "reuse": reused is not None, "original_decision": reference(original),
            "current_decision": reference(changed), "reused_result": reused,
            "naive_unscoped_result_stale": reference(original) != reference(changed),
            "current_evidence_read_bytes": len(wire(changed)), "receipt_bytes": len(wire(receipt))})
    return result


def status_failure_witness(records, reference):
    """Execute two tempting status-only resumption plans against original facts.

    These are local proposed ID lists. No request is generated or authorized.
    IDs themselves differ, so this is not an unrestricted information lower bound.
    """
    failures = [r for r in records if r["status"] == "transport_failure"]
    eligible = [r["case_id"] for r in failures if reference(r)[0] == "preflight_only"]
    retry_all = [r["case_id"] for r in failures]
    return {"shared_status": "transport_failure", "case_ids": retry_all,
        "correct_first_submission_ids": eligible,
        "retry_all_duplicate_dispatch_ids": [key for key in retry_all if key not in eligible],
        "hold_all_missed_eligible_ids": eligible,
        "interpretation": "Counterfactual proposed plans; no actual duplicate generation or compaction-causal history asserted"}


def certificate():
    records, provenance = load_snapshot()
    original = historical_classifier()
    reference = lambda row: original_decision(row, original)
    archives = {mode: Archive(records, mode) for mode in ARCHIVES}
    common = len(wire(records))
    matrix = []
    for caps in CAPACITIES:
        for extra in EXTRAS:
            for price in PRICES:
                for mode, archive in archives.items():
                    arms = {method: aggregate(evaluate(records, reference, method, caps, extra, price, archive))
                            for method in METHODS}
                    matrix.append({"parent_cap": caps[0], "child_cap": caps[1],
                        "extra_allowance": extra, "total_allowance": common + extra,
                        "check_price": price, "archive": mode, "arms": arms})
    frontiers = []
    for caps in CAPACITIES:
        for price in PRICES:
            for mode, archive in archives.items():
                unlimited = {m: evaluate(records, reference, m, caps, 10**9, price, archive) for m in METHODS}
                frontiers.append({"parent_cap": caps[0], "child_cap": caps[1],
                    "check_price": price, "archive": mode, "points": frontier(unlimited, common),
                    "unlimited": {m: aggregate(rows) for m, rows in unlimited.items()}})
    detail = {m: evaluate(records, reference, m, (1536, 768), 16384, 128, archives["none"], detailed=True)
              for m in METHODS}
    sizes = {m: len(wire([1, [entry_for(r, m, Meter(10**9, 0)) for r in records]])) for m in METHODS}
    comparisons = {}
    for other in ("status", "fields", "compact_fields", "direct_receipts"):
        differences = [r["arms"]["repair"]["successful"] - r["arms"][other]["successful"] for r in matrix]
        comparisons[other] = {"repair_better": sum(d > 0 for d in differences),
                              "tied": sum(d == 0 for d in differences),
                              "repair_worse": sum(d < 0 for d in differences)}
    return {"version": "historical_workflow_replay_v1", "date": "2026-09-22",
        "evidence_kind": "exploratory counterfactual handoffs of real historical attempt records",
        "new_model_calls": 0, "historical_source_commit": HISTORICAL_COMMIT,
        "source_sha256": {**HASHES, **{p.relative_to(HERE.parents[2]).as_posix():
            hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sorted(HERE.glob("*")) if p.suffix in (".py", ".md")}},
        "selection": "last two attempts per worker; no quality filter",
        "records": provenance, "status_failure_witness": status_failure_witness(records, reference),
        "common_initial_observation_bytes": common,
        "memory_sizes_without_truncation": sizes, "routes_per_contract": 24,
        "matrix": matrix, "grid_comparisons": comparisons, "frontiers": frontiers,
        "primary_no_archive": {m: aggregate(rows) for m, rows in detail.items()},
        "primary_traces": detail, "cache_controls": cache_controls(records, reference),
        "limitations": ["No observed compaction-causal failure or new LLM trial",
            "One inspected historical workflow; no held-out or independent-task estimate",
            "Synthetic byte/check/tool prices, not production dollars or tokens",
            "Trusted Python interfaces, not adversarial process isolation",
            "Explicit public-rule adapter, not automatic semantic extraction",
            "Direct rule receipts are a stronger, cheaper baseline than audit-and-repair",
            "Source mining, CPU time, archive indexing/storage and provider cache economics unpriced"]}


def report(data):
    primary = data["primary_no_archive"]
    full = next(f for f in data["frontiers"] if (f["parent_cap"], f["check_price"], f["archive"]) == (1536, 128, "full"))
    first_repaired = next(p for p in full["points"] if p["successes"]["repair"] == 24)
    lines = ["# Historical workflow memory replay", "", "September 22, 2026. Offline and exploratory; zero new model calls.", "",
        "Eight real attempt records supply counterfactual handoffs. The original transport failures were observed; their attribution to compaction was not.", "",
        "## Concrete delayed obligation", "",
        "Three final worker attempts dispatched and settled before their answers were lost. The fourth stopped before dispatch. All four say `transport_failure`. A later resumption plan must exclude the three dispatched cases and allow only the preflight case's first submission, subject to the separate full-study checks.", "",
        "The original pure classifier and the saved continuation certificate agree on every selected record. Exact case IDs, request hashes and planning credit amounts remain bound together.", "",
        "A local proposed plan that retries all four failed-status attempts contains three duplicate-dispatch IDs. Holding all four loses the one eligible first submission. Neither plan is executed against a provider; these are explicit failure witnesses for status-only rules.", "",
        "## Two byte boundaries", "",
        f"Common initial observation: **{data['common_initial_observation_bytes']:,} UTF-8 bytes**, charged to every method. Untruncated status / fields / compact fields / receipts: **{data['memory_sizes_without_truncation']['status']} / {data['memory_sizes_without_truncation']['fields']} / {data['memory_sizes_without_truncation']['compact_fields']} / {data['memory_sizes_without_truncation']['direct_receipts']} bytes**.", "",
        "At 1,536 parent bytes, 768 child bytes, no archive, 16,384 additional cost units and 128 units per checker invocation:", "",
        "| Method | Correct / 24 routes | Pre-recovery available | Mean actual cost | Checker calls / 24 |",
        "|---|---:|---:|---:|---:|"]
    for method, row in primary.items():
        lines.append(f"| {method} | {row['successful']} | {row['pre_recovery_available']} | {row['total_cost']/24:.2f} | {row['total_checks']} |")
    lines += ["", "The 24 routes enumerate delayed worker-pair and target reveals over the same eight records. They are not independent trials. All methods have the same total allowance; cheaper runs are not padded.", "",
        "With whole-record archive recovery available, the first exact frontier threshold where repair completes every route is "
        f"**{first_repaired['total_allowance']:,} total units** ({first_repaired['extra_allowance']:,} above common input). "
        "At that same allowance the successful route counts are: " + ", ".join(f"{m} {n}/24" for m, n in first_repaired["successes"].items()) + ". "
        "This is a descriptive threshold from the complete frontier, not a preregistered statistical comparison.", "",
        "## Full resource comparison", "",
        "The 180-contract grid varies both byte caps, allowance, checker price and archive access. Each cell has five methods and 24 routes. Counts below describe this constructed grid, not estimated prevalence.", "",
        "| Comparator | Repair wins | Ties | Repair loses |", "|---|---:|---:|---:|"]
    for method, row in data["grid_comparisons"].items():
        lines.append(f"| {method} | {row['repair_better']} | {row['tied']} | {row['repair_worse']} |")
    lines += ["", "The JSON includes all 45 exact allowance frontiers, including every method's completion-cost threshold, and actual spending on failed runs. The direct-receipt baseline has the same representation with less work; specific diagnosis is not needed once the rule is known.", "",
        "## Receipt invalidation", "",
        "A separate scope control binds checker revision, critical-field presence/values, case identity and actual request payload. Irrelevant latency/quota edits permit reuse. Relevant evidence, absent-to-present fields, identity, payload or checker changes invalidate it. These edits are constructed perturbations of historical records.", "",
        "The cache check reads current evidence: its byte cost is explicit in the JSON. It does not claim free validation, and it is separate from the main immutable-record replay.", "",
        "## Reproduce and interpret", "", "```powershell",
        "python -m experiments.dependency_memory.workflow_replay.run",
        "python -m unittest discover -s experiments/dependency_memory/workflow_replay -t . -v", "```", "",
        "See [the frozen exploratory contract](../workflow_replay/CONTRACT.md) and [source-hashed results](workflow_replay_certificate.json). UTF-8 transfer, checker calls and tool calls have explicitly synthetic prices. CPU time, archive indexing/storage, tokens, cache changes and production billing are unmeasured. These results establish a replay capability and conditional budget improvements over weaker summaries, not a deployed-agent improvement or a novel feedback algorithm.", ""]
    return "\n".join(lines)


def main():
    data = certificate()
    RESULTS.mkdir(exist_ok=True)
    (RESULTS / "workflow_replay_certificate.json").write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    (RESULTS / "workflow_replay_report.md").write_text(report(data), encoding="utf-8", newline="\n")
    print(json.dumps({"records": len(data["records"]), "contracts": len(data["matrix"]),
        "primary": {m: r["successful"] for m, r in data["primary_no_archive"].items()},
        "new_model_calls": 0}))


if __name__ == "__main__":
    main()
