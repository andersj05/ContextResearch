#!/usr/bin/env python3
"""Analyze paper-style recovery candidates and persist best candidates."""
from __future__ import annotations

import json
import math
import os
import statistics
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = Path(os.environ.get(
    "SOURCE", ROOT / "raw" / "advanced_recovery_v2.jsonl"
))
SUMMARY = Path(os.environ.get(
    "SUMMARY", ROOT / "raw" / "advanced_recovery_v2_summary.json"
))
BEST = Path(os.environ.get(
    "BEST", ROOT / "raw" / "advanced_recovery_v2_best.jsonl"
))
ECHO_OVERHEAD = 6


def median(values):
    return statistics.median(values) if values else None


def main():
    rows = [json.loads(line) for line in SOURCE.open() if line.strip()]
    grouped = defaultdict(list)
    for row in rows:
        key = (row["window_id"], row["cutoff_budget_tokens"])
        grouped[(key, row["variant"])].append(row)

    best_by_variant = {}
    variant_stats = {}
    for (key, variant), candidates in grouped.items():
        valid = [
            row for row in candidates
            if not row.get("error")
            and row.get("extraction_error") is not None
            and not row.get("refusal")
        ]
        if valid:
            best_by_variant[(key, variant)] = min(
                valid, key=lambda row: (row["extraction_error"], -row.get("identifier_support", 0))
            )

    variants = sorted({row["variant"] for row in rows})
    sample_keys = sorted({(row["window_id"], row["cutoff_budget_tokens"]) for row in rows})
    for variant in variants:
        all_candidates = [row for row in rows if row["variant"] == variant]
        bests = [
            best_by_variant[(key, variant)] for key in sample_keys
            if (key, variant) in best_by_variant
        ]
        errors = [row["extraction_error"] for row in bests]
        variant_stats[variant] = {
            "candidates": len(all_candidates),
            "samples_with_valid_candidate": len(bests),
            "candidate_refusal_rate": (
                sum(bool(row.get("refusal")) for row in all_candidates) / len(all_candidates)
                if all_candidates else None
            ),
            "candidate_error_rate": (
                sum(bool(row.get("error")) for row in all_candidates) / len(all_candidates)
                if all_candidates else None
            ),
            "best_error_median": median(errors),
            "best_error_mean": statistics.mean(errors) if errors else None,
            "best_error_le_0_1": sum(error <= 0.1 for error in errors),
            "best_error_le_0_2": sum(error <= 0.2 for error in errors),
            "best_error_le_0_5": sum(error <= 0.5 for error in errors),
            "best_unique_fact_recall_median": median([
                row["unique_fact_recall"] for row in bests
                if row.get("unique_fact_recall") is not None
            ]),
            "best_dynamic_fact_recall_median": median([
                row["dynamic_fact_recall"] for row in bests
                if row.get("dynamic_fact_recall") is not None
            ]),
            "best_identifier_support_median": median([
                row["identifier_support"] for row in bests
                if row.get("identifier_support") is not None
            ]),
            "best_token_ratio_median": median([
                row["token_ratio"] for row in bests if row.get("token_ratio") is not None
            ]),
        }

    selected = []
    baseline_errors = {}
    for key in sample_keys:
        candidates = [
            row for (candidate_key, _), row in best_by_variant.items()
            if candidate_key == key
        ]
        if not candidates:
            continue
        winner = min(
            candidates,
            key=lambda row: (row["extraction_error"], -row.get("identifier_support", 0)),
        )
        reported = winner.get("reported_compact_output_tokens") or 0
        baseline_echo = winner.get("baseline_echo_tokens")
        baseline_ratio = (
            max(0, baseline_echo - ECHO_OVERHEAD) / reported
            if baseline_echo is not None and reported else None
        )
        baseline_error = abs(1.0 - baseline_ratio) if baseline_ratio is not None else None
        baseline_errors[key] = baseline_error
        winner = dict(winner)
        winner["baseline_adjusted_token_ratio"] = baseline_ratio
        winner["baseline_extraction_error"] = baseline_error
        winner["improves_baseline_error"] = (
            baseline_error is not None and winner["extraction_error"] < baseline_error
        )
        selected.append(winner)

    BEST.write_text("".join(json.dumps(row, ensure_ascii=False) + "\n" for row in selected))
    wins = Counter(row["variant"] for row in selected)
    summary = {
        "source": str(SOURCE),
        "candidates": len(rows),
        "samples": len(sample_keys),
        "selection": "lowest token-count extraction error after refusal filtering",
        "echo_overhead_subtracted": ECHO_OVERHEAD,
        "variant_stats": variant_stats,
        "winning_variant_counts": dict(wins),
        "global_best_error_median": median([row["extraction_error"] for row in selected]),
        "global_best_error_le_0_1": sum(row["extraction_error"] <= 0.1 for row in selected),
        "global_best_error_le_0_2": sum(row["extraction_error"] <= 0.2 for row in selected),
        "beats_prior_baseline": sum(bool(row["improves_baseline_error"]) for row in selected),
        "prior_baseline_error_median": median([
            error for error in baseline_errors.values() if error is not None
        ]),
        "limitations": [
            "Token-count agreement is independent length evidence, not proof of verbatim plaintext.",
            "compaction_summary is a state item, not necessarily the paper's encrypted reasoning item.",
            "Best-of selection creates multiple-comparisons optimism.",
        ],
    }
    SUMMARY.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n")
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
