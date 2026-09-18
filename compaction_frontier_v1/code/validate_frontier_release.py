#!/usr/bin/env python3
"""Validate schemas, joins, statistics, provenance, trainer views, and archive."""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import statistics
import zipfile
from collections import Counter, defaultdict
from pathlib import Path

import pyarrow.parquet as pq

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_RELEASE = ROOT / "release" / "compaction_frontier_v1"
ECHO_OVERHEAD = 6


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        while chunk := handle.read(1024 * 1024):
            digest.update(chunk)
    return digest.hexdigest()


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode()).hexdigest()


def canonical_messages(messages) -> str:
    return json.dumps(messages, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def close(actual, expected, tolerance=1e-6):
    assert actual is not None
    assert math.isclose(actual, expected, rel_tol=tolerance, abs_tol=tolerance), (actual, expected)


def stat_index(rows):
    result = {}
    for row in rows:
        key = (row["analysis_id"], row["cohort"], row["metric"])
        assert key not in result, key
        result[key] = row
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--release", type=Path, default=DEFAULT_RELEASE)
    parser.add_argument("--zip", type=Path)
    args = parser.parse_args()
    release = args.release.resolve()
    manifest = json.loads((release / "manifest.json").read_text())
    expected_files = set(manifest["files"])
    actual_files = {
        str(path.relative_to(release)) for path in release.rglob("*")
        if path.is_file() and path.name not in {"manifest.json", "SHA256SUMS"}
    }
    assert actual_files == expected_files, (actual_files - expected_files, expected_files - actual_files)
    for relative, metadata in manifest["files"].items():
        path = release / relative
        assert path.stat().st_size == metadata["bytes"], relative
        assert sha256(path) == metadata["sha256"], relative
        if path.suffix == ".parquet":
            assert pq.read_metadata(path).num_rows == metadata["parquet_rows"], relative
    sums = {}
    for line in (release / "SHA256SUMS").read_text().splitlines():
        digest, relative = line.split("  ", 1)
        sums[relative] = digest
    assert sums["manifest.json"] == sha256(release / "manifest.json")
    assert set(sums) == expected_files | {"manifest.json"}
    for relative, digest in sums.items():
        assert sha256(release / relative) == digest, relative

    # Every Parquet must fully decode and match its own metadata.
    parquet_paths = sorted(release.rglob("*.parquet"))
    assert len(parquet_paths) >= 16
    parquet_counts = {}
    for path in parquet_paths:
        table = pq.read_table(path)
        assert table.num_rows == pq.read_metadata(path).num_rows
        assert table.num_columns > 0
        parquet_counts[str(path.relative_to(release))] = table.num_rows

    data = release / "data"
    master_table = pq.read_table(data / "examples_master.parquet")
    master = master_table.to_pylist()
    selected = pq.read_table(data / "advanced_selected_examples.parquet").to_pylist()
    candidates = pq.read_table(data / "recovery_candidates.parquet").to_pylist()
    experiments = pq.read_table(data / "recovery_experiment_runs.parquet").to_pylist()
    stats = pq.read_table(data / "statistical_evidence.parquet").to_pylist()
    methods = pq.read_table(data / "method_catalog.parquet").to_pylist()
    sources = pq.read_table(data / "source_provenance.parquet").to_pylist()
    assert master_table.schema.metadata[b"schema_version"] == b"compaction-frontier-release.v1"
    assert len(master) == 2061
    assert len(selected) == 104
    assert len(candidates) == 1410
    assert len(experiments) == 2287
    assert len(methods) == 6
    assert len(sources) == 40
    assert len(stats) >= 200
    assert len({row["example_id"] for row in master}) == len(master)
    assert len({row["prefix_sha256"] for row in master}) == len(master)
    assert len({row["parent_window_id"] for row in master}) == 308
    assert len({row["candidate_id"] for row in candidates}) == len(candidates)

    # Identity, context, exact fresh envelopes, token provenance, and legacy metrics.
    parent_splits = defaultdict(set)
    for row in master:
        parent_splits[row["parent_window_id"]].add(row["split"])
        expected_prefix = sha256_text(canonical_messages(row["input_messages"]))
        assert row["prefix_sha256"] == expected_prefix
        assert row["example_id"] == f"cmp-{expected_prefix[:24]}"
        assert row["actual_input_tokens"] > 0
        assert row["remote_compact_output_tokens"] > 0
        assert row["input_message_count"] == len(row["input_messages"])
        assert all(message["role"] in {"user", "assistant"} and message["content"] for message in row["input_messages"])
        raw = row["raw_compaction_encrypted_content"]
        assert raw.startswith("gAAAAA")
        assert len(raw) == row["raw_compaction_envelope_chars"]
        assert sha256_text(raw) == row["raw_compaction_sha256"]
        assert not row["raw_envelope_is_plaintext"]
        assert row["stochastic_fresh_capture"]
        assert not row["fresh_capture_id_matches_original"]
        assert row["fresh_capture_item_id"] != row["original_discarded_item_id"]
        assert row["ground_truth_facts_unique"] == list(dict.fromkeys(row["ground_truth_fact_occurrences"]))
        if row["legacy_echo_input_tokens"] is not None:
            adjusted = max(0, row["legacy_echo_input_tokens"] - ECHO_OVERHEAD)
            assert adjusted == row["legacy_adjusted_tokens"]
            ratio = adjusted / row["remote_compact_output_tokens"]
            close(row["legacy_token_ratio"], ratio)
            close(row["legacy_token_error"], abs(1 - ratio))
        assert not row["verified_plaintext"]
        assert not row["label_is_gold"]
    assert all(len(splits) == 1 for splits in parent_splits.values())
    assert max(row["actual_input_tokens"] for row in master) == 398_958
    assert {row["capture_endpoint"] for row in master} == {"https://chatgpt.com/backend-api/codex/responses/compact"}

    # Selected advanced rows are an exact master subset, and all confidence math recomputes.
    advanced = [row for row in master if row["advanced_available"]]
    assert len(advanced) == 104
    assert {(row["example_id"], row["advanced_recovery_text"]) for row in advanced} == {
        (row["example_id"], row["advanced_recovery_text"]) for row in selected
    }
    assert Counter(row["advanced_benchmark_partition"] for row in advanced) == {"holdout": 92, "discovery": 12}
    assert Counter(row["confidence_tier"] for row in advanced) == {
        "A_high_token_fidelity_le_2pct": 92,
        "B_high_token_fidelity_le_5pct": 9,
        "C_advanced_residual": 3,
    }
    for row in advanced:
        adjusted = row["advanced_echo_input_tokens"] - ECHO_OVERHEAD
        assert adjusted == row["advanced_adjusted_tokens"]
        ratio = adjusted / row["remote_compact_output_tokens"]
        close(row["advanced_token_ratio"], ratio)
        close(row["advanced_token_error"], abs(1 - ratio))
        assert row["advanced_recovery_text"]
        assert row["target_status"] == "high_token_fidelity_recovered_state_not_verified_plaintext"
        assert row["recommended_sft"] == (row["split"] == "train" and row["advanced_token_error"] <= 0.05)
        assert row["recommended_evaluation"] == (row["split"] != "train")

    # Candidate calculations and final-selection joins.
    selected_candidates = [row for row in candidates if row["selected_final"]]
    assert len(selected_candidates) == 104
    assert len({row["example_id"] for row in selected_candidates}) == 104
    advanced_by_id = {row["example_id"]: row for row in advanced}
    for row in candidates:
        if row["echo_input_tokens"] is not None:
            adjusted = row["echo_input_tokens"] - row["echo_overhead_tokens"]
            assert adjusted == row["adjusted_extracted_tokens"]
            ratio = adjusted / row["reported_compact_output_tokens"]
            close(row["token_ratio"], ratio)
            close(row["extraction_error"], abs(1 - ratio))
        if row["selected_final"]:
            target = advanced_by_id[row["example_id"]]
            assert row["model"] == target["advanced_decoder_model"]
            assert row["variant"] == target["advanced_variant"]
            assert row["replicate"] == target["advanced_replicate"]
            assert row["extracted_text"] == target["advanced_recovery_text"]

    # Lossless experiment archive includes winners, controls, prompt discovery, and negative results.
    expected_stages = {
        "preregistered_holdout_luna": 1040,
        "prompt_discovery": 360,
        "state_exact_scale_discovery": 240,
        "no_envelope_control": 240,
        "targeted_terra_fallback": 190,
        "best_of_50_rescue": 100,
        "bounded_luna_rescue": 40,
        "bounded_terra_rescue": 40,
        "early_terra_fallback": 30,
        "paper_template_benchmark": 4,
        "paper_figure37_chunk_probe": 3,
    }
    assert Counter(row["experiment_stage"] for row in experiments) == expected_stages
    assert len({row["experiment_record_id"] for row in experiments}) == len(experiments)
    assert Counter(row["control_condition"] for row in experiments) == {
        "native_compaction_summary_envelope": 2047,
        "no_envelope_prompt_only": 240,
    }
    experiment_source_rows = defaultdict(list)
    for row in experiments:
        payload = json.loads(row["record_json"])
        assert payload.get("window_id") == row["window_id"]
        assert payload.get("variant") == row["variant"]
        assert payload.get("raw_output") == row["raw_output"]
        experiment_source_rows[row["source_path"]].append(row["source_row"])
    for ordinals in experiment_source_rows.values():
        assert sorted(ordinals) == list(range(len(ordinals)))
    selection_matches = [row for row in experiments if row["matches_final_selection"]]
    assert {row["prefix_sha256"] for row in selection_matches} == {row["prefix_sha256"] for row in advanced}

    # Recompute load-bearing statistics.
    index = stat_index(stats)
    for cohort_name, cohort_rows in (
        ("advanced_all", advanced),
        ("advanced_holdout", [row for row in advanced if row["advanced_benchmark_partition"] == "holdout"]),
        ("advanced_discovery", [row for row in advanced if row["advanced_benchmark_partition"] == "discovery"]),
    ):
        errors = [row["advanced_token_error"] for row in cohort_rows]
        ratios = [row["advanced_token_ratio"] for row in cohort_rows]
        close(index[("advanced_token_fidelity", cohort_name, "median_extraction_error")]["value"], statistics.median(errors))
        close(index[("advanced_token_fidelity", cohort_name, "mean_extraction_error")]["value"], statistics.mean(errors))
        close(index[("advanced_token_fidelity", cohort_name, "median_token_ratio")]["value"], statistics.median(ratios))
        for tolerance in (0.005, 0.01, 0.02, 0.05, 0.1, 0.2):
            row = index[("advanced_token_fidelity", cohort_name, f"within_{tolerance:.3f}")]
            count = sum(error <= tolerance for error in errors)
            assert row["numerator"] == count and row["denominator"] == len(errors)
            close(row["value"], count / len(errors))
            assert row["ci95_low"] <= row["value"] <= row["ci95_high"]

    paired = [row for row in advanced if row["legacy_token_error"] is not None]
    wins = sum(row["advanced_token_error"] < row["legacy_token_error"] for row in paired)
    paired_stat = index[("paired_recovery_comparison", "advanced_vs_legacy", "advanced_win_rate")]
    assert paired_stat["numerator"] == wins and paired_stat["denominator"] == len(paired)
    close(paired_stat["value"], wins / len(paired))

    by_bin = defaultdict(list)
    for row in master:
        by_bin[row["context_50k_bin"]].append(row)
    for bin_start, rows in by_bin.items():
        cohort = f"input_{bin_start}_{bin_start + 50000}"
        close(index[("context_scaling", cohort, "rows")]["value"], len(rows))
        close(index[("context_scaling", cohort, "compact_output_tokens_median")]["value"], statistics.median(row["remote_compact_output_tokens"] for row in rows))
        close(index[("context_scaling", cohort, "envelope_chars_median")]["value"], statistics.median(row["raw_compaction_envelope_chars"] for row in rows))

    # Every rate statistic is internally coherent.
    for row in stats:
        if row["numerator"] is not None and row["denominator"] is not None and row["unit"] == "rate":
            assert 0 <= row["numerator"] <= row["denominator"]
            close(row["value"], row["numerator"] / row["denominator"])
            if row["ci95_low"] is not None:
                assert 0 <= row["ci95_low"] <= row["value"] <= row["ci95_high"] <= 1

    # Source lineage hashes the repository inputs used to build this release.
    assert len({row["source_path"] for row in sources}) == len(sources)
    for row in sources:
        source = ROOT / row["source_path"]
        assert source.is_file(), row["source_path"]
        assert sha256(source) == row["source_sha256"], row["source_path"]
        assert row["materialized_into"]

    # Method taxonomy and documentation must preserve the paper/local distinction.
    method_by_id = {row["method_id"]: row for row in methods}
    assert set(method_by_id) == {
        "paper_gpt_fig35", "paper_gpt_fig36", "paper_gpt_fig37",
        "local_legacy_semantic", "local_state_exact", "sft_prompt_v2",
    }
    assert method_by_id["paper_gpt_fig35"]["provenance"] == "paper_authored"
    assert "not verified verbatim plaintext" in method_by_id["local_state_exact"]["recommended_use"]
    required_docs = {
        "README.md", "DATA_DICTIONARY.md", "EXPERIMENT_DESIGN.md",
        "STATISTICAL_GUIDE.md", "SCHEMAS.json", "CITATION.cff", "ANALYSIS.md",
        "advanced_recovery_summary.json", "legacy_parquet_manifest.json",
    }
    assert required_docs <= {path.name for path in (release / "docs").iterdir()}
    analysis_artifacts = list((release / "docs" / "analysis_artifacts").glob("*.json"))
    assert len(analysis_artifacts) >= 20
    assert "Verified plaintext" in (release / "docs" / "EXPERIMENT_DESIGN.md").read_text()

    # Trainer views: expected counts, canonical terminal prompt, parent isolation.
    trainer = release / "trainer_views"
    trainer_manifest = json.loads((trainer / "manifest.json").read_text())
    for name, metadata in trainer_manifest["files"].items():
        path = trainer / name
        assert path.is_file()
        assert sha256(path) == metadata["sha256"]
        assert pq.read_metadata(path).num_rows == metadata["rows"]
    canonical_prompt = trainer_manifest["canonical_prompt"]["text"]
    for path in trainer.glob("compaction_sft_v2_*.parquet"):
        rows = pq.read_table(path).to_pylist()
        for row in rows:
            assert row["messages"][-2] == {"role": "user", "content": canonical_prompt}
            assert row["messages"][-1]["role"] == "assistant"
            assert row["messages"][-1]["content"] == row["assistant_target"]
            assert not row["verified_plaintext"]
            assert row["target_status"] != "gold"
    advanced_splits = {}
    for split in ("train", "validation", "test"):
        rows = pq.read_table(trainer / f"compaction_sft_v2_advanced_{split}.parquet", columns=["parent_window_id"]).to_pylist()
        advanced_splits[split] = {row["parent_window_id"] for row in rows}
    assert not (advanced_splits["train"] & advanced_splits["validation"])
    assert not (advanced_splits["train"] & advanced_splits["test"])
    assert not (advanced_splits["validation"] & advanced_splits["test"])

    # Optional archive is a byte-complete representation of the release directory.
    zip_summary = None
    if args.zip:
        archive = args.zip.resolve()
        assert archive.is_file()
        with zipfile.ZipFile(archive) as handle:
            assert handle.testzip() is None
            members = {name for name in handle.namelist() if not name.endswith("/")}
            prefix = release.name + "/"
            expected_members = {prefix + str(path.relative_to(release)) for path in release.rglob("*") if path.is_file()}
            assert members == expected_members, (members - expected_members, expected_members - members)
        sidecar = archive.with_suffix(archive.suffix + ".sha256")
        assert sidecar.read_text().split()[0] == sha256(archive)
        zip_summary = {"path": str(archive), "bytes": archive.stat().st_size, "sha256": sha256(archive)}

    summary = {
        "status": "PASS",
        "release": str(release),
        "master_examples": len(master),
        "parent_windows": len(parent_splits),
        "advanced_selected": len(advanced),
        "advanced_candidates": len(candidates),
        "experiment_records": len(experiments),
        "statistics": len(stats),
        "parquet_files_smoke_loaded": len(parquet_paths),
        "trainer_rows": {name: count for name, count in parquet_counts.items() if name.startswith("trainer_views/")},
        "archive": zip_summary,
    }
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
