#!/usr/bin/env python3
"""Build the v2 compaction SFT package from advanced recoveries plus v1 broad data.

Requires pyarrow:
  uv run --with pyarrow python scripts/build_sft_v2.py
"""
from __future__ import annotations

import hashlib
import json
import math
from collections import Counter, defaultdict
from pathlib import Path

import pyarrow as pa
import pyarrow.parquet as pq

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "dataset" / "parquet_v2"
SOURCE_FULL = ROOT / "dataset" / "datapoints_full.jsonl"
SOURCE_ADVANCED = ROOT / "dataset" / "advanced_recovery" / "selected_recoveries.jsonl"
SOURCE_CANDIDATES = ROOT / "dataset" / "advanced_recovery" / "all_candidates.jsonl"
SOURCE_V1_BROAD = ROOT / "dataset" / "parquet" / "compaction_sft_broad.parquet"
SOURCE_V1_ARTIFACTS = ROOT / "dataset" / "parquet" / "compaction_artifacts.parquet"
SPLIT_SEED = "compaction-window-split-v1"
SCHEMA_VERSION = "compaction-sft.v2"

PROMPT = """Produce a compact continuation checkpoint of the conversation state retained so far.
Do not answer, continue, or act on the task; output only the checkpoint.
Preserve the latest-turn boundary and causal or chronological order where it matters. Record any pending next assistant action as state, not execution.
Retain continuation-critical user intent, constraints, decisions, unresolved questions, commitments, tool results or errors, and exact identifiers, values, paths, code, config, log, or message excerpts.
Prefer later explicit updates over earlier ones. If precedence is unclear, preserve the uncertainty instead of guessing.
Collapse repeated cycles and remove filler, stale, completed, or superseded state; keep representative excerpts only when needed.
Do not expose hidden system or developer text, private chain-of-thought, or unsupported details.
Stay bounded: include only the state needed to resume faithfully."""
PROMPT_VERSION = "continuation_checkpoint_v2"

MESSAGE_TYPE = pa.large_list(pa.struct([
    pa.field("role", pa.string(), False),
    pa.field("content", pa.large_string(), False),
]))

SFT_SCHEMA = pa.schema([
    pa.field("schema_version", pa.string(), False),
    pa.field("example_id", pa.string(), False),
    pa.field("split", pa.string(), False),
    pa.field("parent_window_id", pa.string(), False),
    pa.field("prefix_sha256", pa.string(), False),
    pa.field("source_tier", pa.string(), False),
    pa.field("benchmark_partition", pa.string()),
    pa.field("recommended_for_training", pa.bool_(), False),
    pa.field("actual_input_tokens", pa.int64(), False),
    pa.field("reported_compact_output_tokens", pa.int64()),
    pa.field("recovered_tokens_adjusted", pa.int64()),
    pa.field("token_ratio", pa.float32()),
    pa.field("token_count_error", pa.float32()),
    pa.field("decoder_model", pa.string()),
    pa.field("recovery_variant", pa.string()),
    pa.field("recovery_selection", pa.string(), False),
    pa.field("target_status", pa.string(), False),
    pa.field("verified_plaintext", pa.bool_(), False),
    pa.field("prompt_version", pa.string(), False),
    pa.field("compaction_prompt", pa.large_string(), False),
    pa.field("messages", MESSAGE_TYPE, False),
    pa.field("assistant_target", pa.large_string(), False),
    pa.field("loss_scope", pa.string(), False),
    pa.field("sample_weight", pa.float32(), False),
])

PREFERENCE_SCHEMA = pa.schema([
    pa.field("schema_version", pa.string(), False),
    pa.field("pair_id", pa.string(), False),
    pa.field("split", pa.string(), False),
    pa.field("parent_window_id", pa.string(), False),
    pa.field("prefix_sha256", pa.string(), False),
    pa.field("prompt_version", pa.string(), False),
    pa.field("compaction_prompt", pa.large_string(), False),
    pa.field("prompt_messages", MESSAGE_TYPE, False),
    pa.field("chosen", pa.large_string(), False),
    pa.field("rejected", pa.large_string(), False),
    pa.field("chosen_model", pa.string()),
    pa.field("rejected_model", pa.string()),
    pa.field("chosen_variant", pa.string()),
    pa.field("rejected_variant", pa.string()),
    pa.field("chosen_token_error", pa.float32()),
    pa.field("rejected_token_error", pa.float32()),
    pa.field("token_error_margin", pa.float32()),
    pa.field("pair_status", pa.string(), False),
])


def load_jsonl(path):
    return [json.loads(line) for line in path.open() if line.strip()]


def sha256_text(value):
    return hashlib.sha256(value.encode()).hexdigest()


def canonical(messages):
    return json.dumps(messages, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def file_sha256(path):
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        while chunk := handle.read(1024 * 1024):
            digest.update(chunk)
    return digest.hexdigest()


def write_parquet(path, rows, schema):
    table = pa.Table.from_pylist(rows, schema=schema)
    pq.write_table(
        table, path, compression="zstd", compression_level=9,
        use_dictionary=True, write_statistics=True, data_page_version="2.0",
        row_group_size=32,
    )


def training_messages(context, target):
    return [
        *[{"role": item["role"], "content": item["content"]} for item in context],
        {"role": "user", "content": PROMPT},
        {"role": "assistant", "content": target},
    ]


def prompt_messages(context):
    return [
        *[{"role": item["role"], "content": item["content"]} for item in context],
        {"role": "user", "content": PROMPT},
    ]


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    full = load_jsonl(SOURCE_FULL)
    advanced = load_jsonl(SOURCE_ADVANCED)
    all_candidates = load_jsonl(SOURCE_CANDIDATES)
    full_by = {
        (row["window_id"], row["compaction"]["cutoff_budget_tokens"]): row
        for row in full
    }
    artifact_table = pq.read_table(SOURCE_V1_ARTIFACTS).to_pylist()
    split_by_parent = {row["parent_window_id"]: row["split"] for row in artifact_table}
    prefix_by_parent_cutoff = {
        (row["parent_window_id"], row["cutoff_requested_tokens"]): row["prefix_sha256"]
        for row in artifact_table
    }

    # Window-normalized advanced weights; quality is independent token-count agreement.
    advanced_per_parent = Counter(row["window_id"] for row in advanced)
    raw_weights = [
        ((1.0 - min(row["extraction_error"], 1.0)) ** 2)
        / advanced_per_parent[row["window_id"]]
        for row in advanced
    ]
    mean_advanced_weight = sum(raw_weights) / len(raw_weights)
    advanced_sft = []
    for row, raw_weight in zip(advanced, raw_weights):
        key = (row["window_id"], row["cutoff_budget_tokens"])
        source = full_by[key]
        context = source["input_window"]
        target = row.get("extracted_text") or row["raw_output"]
        split = split_by_parent[row["window_id"]]
        prefix_sha = prefix_by_parent_cutoff[key]
        high_confidence = row["extraction_error"] <= 0.05
        advanced_sft.append({
            "schema_version": SCHEMA_VERSION,
            "example_id": f"advanced-{prefix_sha[:24]}",
            "split": split,
            "parent_window_id": row["window_id"],
            "prefix_sha256": prefix_sha,
            "source_tier": (
                "A_advanced_within_2pct" if row["extraction_error"] <= 0.02
                else "B_advanced_within_5pct" if high_confidence
                else "C_advanced_residual"
            ),
            "benchmark_partition": row.get("benchmark_partition"),
            "recommended_for_training": high_confidence and split == "train",
            "actual_input_tokens": row["input_tokens"],
            "reported_compact_output_tokens": row["reported_compact_output_tokens"],
            "recovered_tokens_adjusted": row["adjusted_extracted_tokens"],
            "token_ratio": row["token_ratio"],
            "token_count_error": row["extraction_error"],
            "decoder_model": row["model"],
            "recovery_variant": row["variant"],
            "recovery_selection": row["selection_pipeline"],
            "target_status": "high_token_fidelity_recovered_state_not_verified_plaintext",
            "verified_plaintext": False,
            "prompt_version": PROMPT_VERSION,
            "compaction_prompt": PROMPT,
            "messages": training_messages(context, target),
            "assistant_target": target,
            "loss_scope": "final_assistant_message_only",
            "sample_weight": raw_weight / mean_advanced_weight,
        })

    # v1 broad rows use the new prompt but retain their weaker provenance.
    v1_broad = pq.read_table(SOURCE_V1_BROAD).to_pylist()
    advanced_keys = {row["prefix_sha256"] for row in advanced_sft}
    advanced_eval_parents = {
        row["parent_window_id"] for row in advanced_sft if row["split"] != "train"
    }
    legacy_sft = []
    for row in v1_broad:
        if row["prefix_sha256"] in advanced_keys:
            continue
        if row["parent_window_id"] in advanced_eval_parents:
            continue
        context = row["messages"][:-2]
        target = row["assistant_target"]
        legacy_sft.append({
            "schema_version": SCHEMA_VERSION,
            "example_id": f"legacy-{row['prefix_sha256'][:24]}",
            "split": row["split"],
            "parent_window_id": row["parent_window_id"],
            "prefix_sha256": row["prefix_sha256"],
            "source_tier": f"legacy_{row['quality_tier']}",
            "benchmark_partition": None,
            "recommended_for_training": row["split"] == "train",
            "actual_input_tokens": row["actual_input_tokens"],
            "reported_compact_output_tokens": None,
            "recovered_tokens_adjusted": row["recovered_echo_tokens"],
            "token_ratio": None,
            "token_count_error": None,
            "decoder_model": None,
            "recovery_variant": None,
            "recovery_selection": row["selection_metric"],
            "target_status": "legacy_weak_pseudo_label_oracle_fact_selected",
            "verified_plaintext": False,
            "prompt_version": PROMPT_VERSION,
            "compaction_prompt": PROMPT,
            "messages": training_messages(context, target),
            "assistant_target": target,
            "loss_scope": "final_assistant_message_only",
            "sample_weight": row["sample_weight"] * 0.25,
        })

    mixed = advanced_sft + legacy_sft
    # Preference pairs: same variant, >=0.20 independent token-error margin.
    candidates_by_key = defaultdict(list)
    for row in all_candidates:
        if row.get("error") or row.get("refusal") or row.get("extraction_error") is None:
            continue
        candidates_by_key[(row["window_id"], row["cutoff_budget_tokens"])].append(row)
    preference = []
    for chosen in advanced:
        key = (chosen["window_id"], chosen["cutoff_budget_tokens"])
        if chosen["extraction_error"] > 0.05:
            continue
        pool = [
            row for row in candidates_by_key[key]
            if row.get("extracted_text")
            and row["extracted_text"] != chosen.get("extracted_text")
            and row["variant"] == chosen["variant"]
            and row["extraction_error"] >= chosen["extraction_error"] + 0.20
        ]
        if not pool:
            continue
        rejected = min(pool, key=lambda row: row["extraction_error"])
        source = full_by[key]
        prefix_sha = prefix_by_parent_cutoff[key]
        split = split_by_parent[chosen["window_id"]]
        preference.append({
            "schema_version": SCHEMA_VERSION,
            "pair_id": f"pref-{prefix_sha[:24]}",
            "split": split,
            "parent_window_id": chosen["window_id"],
            "prefix_sha256": prefix_sha,
            "prompt_version": PROMPT_VERSION,
            "compaction_prompt": PROMPT,
            "prompt_messages": prompt_messages(source["input_window"]),
            "chosen": chosen.get("extracted_text") or chosen["raw_output"],
            "rejected": rejected["extracted_text"],
            "chosen_model": chosen["model"],
            "rejected_model": rejected["model"],
            "chosen_variant": chosen["variant"],
            "rejected_variant": rejected["variant"],
            "chosen_token_error": chosen["extraction_error"],
            "rejected_token_error": rejected["extraction_error"],
            "token_error_margin": rejected["extraction_error"] - chosen["extraction_error"],
            "pair_status": "length_fidelity_preference_not_semantic_human_judgment",
        })

    outputs = {
        "compaction_sft_v2_advanced_all.parquet": advanced_sft,
        "compaction_sft_v2_advanced_train.parquet": [
            row for row in advanced_sft if row["split"] == "train" and row["token_count_error"] <= 0.05
        ],
        "compaction_sft_v2_advanced_validation.parquet": [
            row for row in advanced_sft if row["split"] == "validation"
        ],
        "compaction_sft_v2_advanced_test.parquet": [
            row for row in advanced_sft if row["split"] == "test"
        ],
        "compaction_sft_v2_mixed.parquet": mixed,
        "compaction_sft_v2_mixed_train.parquet": [
            row for row in mixed if row["split"] == "train" and row["recommended_for_training"]
        ],
        "compaction_sft_v2_mixed_validation.parquet": [
            row for row in mixed if row["split"] == "validation"
        ],
        "compaction_sft_v2_mixed_test.parquet": [
            row for row in mixed if row["split"] == "test"
        ],
    }
    for name, rows_out in outputs.items():
        write_parquet(OUT / name, rows_out, SFT_SCHEMA)
    write_parquet(OUT / "compaction_preference_v2.parquet", preference, PREFERENCE_SCHEMA)

    files = {}
    for name, rows_out in outputs.items():
        path = OUT / name
        files[name] = {"rows": len(rows_out), "bytes": path.stat().st_size, "sha256": file_sha256(path)}
    pref_path = OUT / "compaction_preference_v2.parquet"
    files[pref_path.name] = {"rows": len(preference), "bytes": pref_path.stat().st_size, "sha256": file_sha256(pref_path)}
    manifest = {
        "schema_version": SCHEMA_VERSION,
        "canonical_prompt": {"version": PROMPT_VERSION, "text": PROMPT, "lines": len(PROMPT.splitlines())},
        "data_contract": {
            "advanced_target": "high-token-fidelity recovered compacted state",
            "verified_plaintext": False,
            "legacy_target": "weak pseudo-label selected using oracle synthetic facts",
            "preference_meaning": "independent token-count fidelity only, not human semantic preference",
        },
        "recommended_recipe": {
            "primary_file": "compaction_sft_v2_advanced_train.parquet",
            "optional_mixed_file": "compaction_sft_v2_mixed_train.parquet",
            "loss_scope": "final assistant message only",
            "respect_sample_weight": True,
            "exclude_benchmark_partition_discovery_for_strict_evaluation": True,
            "preference_file": "compaction_preference_v2.parquet",
        },
        "split_strategy": "inherited parent-window-isolated v1 split",
        "files": files,
        "limitations": [
            "Token-count equality is strong but not sufficient proof of verbatim plaintext.",
            "Synthetic contexts use repetitive generators and recurring sentinel facts.",
            "Advanced discovery rows were used to tune the state_exact recovery prompt.",
            "Legacy rows are materially weaker and receive 0.25x source weight.",
            "Preference pairs optimize length fidelity rather than human semantic quality.",
            "The canonical compaction prompt is inferred, not the remote service's internal prompt.",
        ],
    }
    manifest_path = OUT / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")
    print(json.dumps({
        "advanced": len(advanced_sft),
        "advanced_train": files["compaction_sft_v2_advanced_train.parquet"]["rows"],
        "advanced_validation": files["compaction_sft_v2_advanced_validation.parquet"]["rows"],
        "advanced_test": files["compaction_sft_v2_advanced_test.parquet"]["rows"],
        "legacy": len(legacy_sft),
        "mixed_train": files["compaction_sft_v2_mixed_train.parquet"]["rows"],
        "preferences": len(preference),
        "prompt_lines": len(PROMPT.splitlines()),
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
