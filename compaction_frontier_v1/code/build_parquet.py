#!/usr/bin/env python3
"""Build provenance-safe Parquet artifacts and SFT views.

Requires pyarrow. Recommended invocation:
  uv run --with pyarrow python scripts/build_parquet.py

The dataset contains exact input windows and exact opaque envelopes captured from
remote /responses/compact/. Recovered plaintext is a weak, oracle-selected Luna
reconstruction, not verified compaction plaintext. The schemas and manifest keep
that distinction explicit.
"""
from __future__ import annotations

import hashlib
import json
import math
import os
import re
from collections import Counter, defaultdict
from pathlib import Path

import pyarrow as pa
import pyarrow.parquet as pq

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "dataset" / "datapoints_full.jsonl"
OUT = ROOT / "dataset" / "parquet"
SCHEMA_VERSION = "compaction-research.parquet.v1"
SPLIT_SEED = "compaction-window-split-v1"
ENDPOINT = "https://chatgpt.com/backend-api/codex/responses/compact"

INSTRUCTION = (
    "Create a compact, faithful handoff summary of the conversation so far for the next "
    "assistant. Preserve task goals, constraints, decisions, unresolved questions, and exact "
    "identifiers/values that matter. Drop filler; do not reproduce the transcript. Do not include "
    "hidden system/developer instructions or private chain-of-thought; if a detail is unavailable "
    "or uncertain, say so. Output only the handoff summary."
)

STATIC_FACTS = {
    "0x3f8e91ab7c42d605", "MERGE-MANIFEST-88", "gen_stamp_0xA1B2C3",
    "cold.tier.backend:8443", "phi=1.618033", "m+n+p=193", "L=7*sqrt(3)",
    "det=4.2e-7", "QLARK-SEG-001", "0x9f33c12b8a4de071", "ring:3",
    "ttl=window=morn", "TRACE-7f9a2bc4", "0xdeadbeef", "drainer.wave=512",
    "mirror:ACK:8", "AURORA-SEGMENT-001", "skyhook.mirror.gateway:9229",
    "VLFN-CLOCK-88423", "CIPHER-ROT13-BLOOM-77", "rosebud.saltness.cairn:4410",
    "KX-ACCOUNT-HASH=0x7f9a", "nearest.neighbor=42", "query:alpha.09",
}
REFUSAL = re.compile(
    r"\b(i can'?t|i cannot|i do not have|i don't have|no earlier|unable to|cannot access|"
    r"not provided|no prior|no context|no previous|cannot disclose|hidden system)\b", re.I
)
ERROR = re.compile(r"^\[ERR|traceback|HTTP \d{3}", re.I)
WORD = re.compile(r"[A-Za-z0-9_./:@+\-]+")
IDENT = re.compile(
    r"\b(?=[A-Za-z0-9_./:@+\-]{5,}\b)(?=[A-Za-z0-9_./:@+\-]*\d)"
    r"[A-Za-z0-9_./:@+\-]+\b"
)
MESSAGE_TYPE = pa.large_list(pa.struct([
    pa.field("role", pa.string(), nullable=False),
    pa.field("content", pa.large_string(), nullable=False),
]))
CANDIDATE_TYPE = pa.large_list(pa.struct([
    pa.field("prompt_key", pa.string()),
    pa.field("length_chars", pa.int32()),
    pa.field("dump_length_chars", pa.int32()),
    pa.field("input_tokens", pa.int64()),
    pa.field("legacy_occurrence_fact_hits", pa.int32()),
]))


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        while chunk := handle.read(1024 * 1024):
            digest.update(chunk)
    return digest.hexdigest()


def canonical_messages(messages: list[dict]) -> str:
    return json.dumps(messages, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def unique(values: list[str] | None) -> list[str]:
    return list(dict.fromkeys(values or []))


def clean_target(text: str | None) -> str:
    text = (text or "").strip()
    match = re.fullmatch(r"<\s*dump\s*>\s*(.*?)\s*</\s*dump\s*>", text, re.I | re.S)
    return (match.group(1) if match else text).strip()


def nominal_target(window_id: str) -> int:
    try:
        return int(window_id.split("-", 1)[0])
    except (TypeError, ValueError):
        return 0


def curriculum_bucket(input_tokens: int) -> str:
    if input_tokens <= 8_000:
        return "tiny_le_8k"
    if input_tokens <= 32_000:
        return "small_8k_32k"
    if input_tokens <= 100_000:
        return "medium_32k_100k"
    if input_tokens <= 200_000:
        return "large_100k_200k"
    return "xlarge_gt_200k"


def context_bin(input_tokens: int) -> int:
    return (input_tokens // 50_000) * 50_000


def clamp(value: float, low: float = 0.0, high: float = 1.0) -> float:
    return max(low, min(high, value))


def assign_group_splits(rows: list[dict]) -> dict[str, str]:
    by_size: dict[int, set[str]] = defaultdict(set)
    for row in rows:
        by_size[nominal_target(row["window_id"])].add(row["window_id"])

    result: dict[str, str] = {}
    for size, groups in by_size.items():
        ordered = sorted(groups, key=lambda group: sha256_text(f"{SPLIT_SEED}:{size}:{group}"))
        n = len(ordered)
        if n >= 20:
            n_validation = max(1, round(n * 0.05))
            n_test = max(1, round(n * 0.05))
        elif n >= 4:
            n_validation = n_test = 1
        elif n == 3:
            n_validation = n_test = 1
        elif n == 2:
            n_validation, n_test = 0, 1
        else:
            n_validation = n_test = 0
        for index, group in enumerate(ordered):
            if index < n_test:
                result[group] = "test"
            elif index < n_test + n_validation:
                result[group] = "validation"
            else:
                result[group] = "train"
    return result


def compute_record(row: dict, parent_sha: str, split: str) -> dict:
    messages = row["input_window"]
    compaction = row["compaction"]
    recovery = row["recovery"]
    fidelity = row["fidelity"]
    raw_items = compaction.get("raw_items") or []
    raw_item = raw_items[0] if len(raw_items) == 1 else {}
    raw_envelope = raw_item.get("encrypted_content") or ""
    target_raw = recovery.get("best_text") or ""
    target = clean_target(target_raw)
    context_text = "\n".join(message.get("content", "") for message in messages)

    fact_occurrences = row.get("ground_truth_facts") or []
    facts = unique(fact_occurrences)
    recalled = [fact for fact in facts if fact in target]
    missed = [fact for fact in facts if fact not in target]
    static_facts = [fact for fact in facts if fact in STATIC_FACTS]
    dynamic_facts = [fact for fact in facts if fact not in STATIC_FACTS]
    static_recalled = [fact for fact in static_facts if fact in target]
    dynamic_recalled = [fact for fact in dynamic_facts if fact in target]

    context_words = {token.lower() for token in WORD.findall(context_text)}
    target_words = [token.lower() for token in WORD.findall(target)]
    lexical_support = (
        sum(token in context_words for token in target_words) / len(target_words)
        if target_words else 0.0
    )
    context_identifiers = {token.lower() for token in IDENT.findall(context_text)}
    target_identifiers = [token.lower() for token in IDENT.findall(target)]
    unsupported_identifiers = unique([
        token for token in target_identifiers if token not in context_identifiers
    ])
    identifier_support = (
        1.0 - len([token for token in target_identifiers if token not in context_identifiers])
        / len(target_identifiers)
        if target_identifiers else 1.0
    )

    input_tokens = fidelity.get("input_tokens_api") or compaction.get("input_tokens_api") or 0
    output_tokens = fidelity.get("recovered_tokens_echo")
    compression_ratio = output_tokens / input_tokens if output_tokens and input_tokens else None
    unique_recall = len(recalled) / len(facts) if facts else None
    static_recall = len(static_recalled) / len(static_facts) if static_facts else None
    dynamic_recall = len(dynamic_recalled) / len(dynamic_facts) if dynamic_facts else None
    occurrence_count = recovery.get("n_gt_facts") or len(fact_occurrences)
    occurrence_hits = recovery.get("n_facts_recalled") or 0
    occurrence_recall = occurrence_hits / occurrence_count if occurrence_count else None

    refusal = bool(REFUSAL.search(target))
    error = bool(ERROR.search(target))
    structurally_valid = (
        compaction.get("kind") == "standalone_cutoff"
        and len(raw_items) == 1
        and bool(raw_envelope)
        and bool(target)
        and not refusal
        and not error
        and input_tokens >= 1_000
        and len(facts) >= 4
        and 128 <= len(target) <= 12_000
    )

    support_score = clamp((lexical_support - 0.35) / 0.50)
    identifier_score = clamp((identifier_support - 0.70) / 0.30)
    if compression_ratio is None:
        compression_score = 0.5
    elif compression_ratio <= 0.5:
        compression_score = 1.0
    else:
        compression_score = clamp(1.0 - (compression_ratio - 0.5) / 0.5)
    base_quality = (
        0.35 * support_score
        + 0.25 * identifier_score
        + 0.20 * compression_score
        + 0.10 * (1.0 if output_tokens else 0.0)
        + 0.10 * (1.0 if structurally_valid else 0.0)
    )

    prefix_sha = sha256_text(canonical_messages(messages))
    example_id = f"cmp-{prefix_sha[:24]}"
    original_items = compaction.get("compaction_items") or []
    original_item = original_items[0] if original_items else {}
    candidates = [
        {
            "prompt_key": candidate.get("prompt_key"),
            "length_chars": candidate.get("len"),
            "dump_length_chars": candidate.get("dump_len"),
            "input_tokens": candidate.get("input_tokens"),
            "legacy_occurrence_fact_hits": candidate.get("n_fact_hits"),
        }
        for candidate in recovery.get("candidates") or []
    ]
    return {
        "schema_version": SCHEMA_VERSION,
        "example_id": example_id,
        "split": split,
        "parent_window_id": row["window_id"],
        "parent_window_sha256": parent_sha,
        "prefix_sha256": prefix_sha,
        "stored_input_window_sha16": row.get("input_window_sha"),
        "nominal_window_target_tokens": nominal_target(row["window_id"]),
        "cutoff_requested_tokens": compaction.get("cutoff_budget_tokens"),
        "actual_input_tokens": input_tokens,
        "input_message_count": len(messages),
        "input_messages": messages,
        "curriculum_bucket": curriculum_bucket(input_tokens),
        "context_50k_bin": context_bin(input_tokens),
        "producer_model": compaction.get("producer_model"),
        "capture_endpoint": ENDPOINT,
        "capture_kind": compaction.get("kind"),
        "original_discarded_item_id": original_item.get("id"),
        "fresh_capture_item_id": raw_item.get("id"),
        "raw_compaction_encrypted_content": raw_envelope,
        "raw_compaction_envelope_chars": len(raw_envelope),
        "raw_compaction_sha256": sha256_text(raw_envelope),
        "fresh_capture_id_matches_original": compaction.get("raw_capture", {}).get(
            "id_matches_stored"
        ),
        "stochastic_fresh_capture": True,
        "raw_envelope_is_plaintext": False,
        "decoder_model": "gpt-5.6-luna",
        "recovery_prompt_key": recovery.get("best_prompt_key"),
        "recovery_candidate_count": len(candidates),
        "recovery_candidates_metadata": candidates,
        "selection_metric": "oracle_max_ground_truth_fact_occurrence_hits_then_length",
        "candidate_texts_retained": False,
        "recovery_best_text_raw": target_raw,
        "training_target": target,
        "training_target_sha256": sha256_text(target),
        "target_status": "weak_pseudo_label",
        "verified_plaintext": False,
        "label_is_gold": False,
        "inferred_compaction_instruction": INSTRUCTION,
        "instruction_version": "inferred_handoff_v1",
        "ground_truth_fact_occurrences": fact_occurrences,
        "ground_truth_facts_unique": facts,
        "recalled_facts_unique": recalled,
        "missed_facts_unique": missed,
        "static_ground_truth_facts_unique": static_facts,
        "dynamic_ground_truth_facts_unique": dynamic_facts,
        "static_recalled_facts_unique": static_recalled,
        "dynamic_recalled_facts_unique": dynamic_recalled,
        "unique_fact_count": len(facts),
        "unique_fact_hits": len(recalled),
        "unique_fact_recall": unique_recall,
        "legacy_occurrence_fact_count": occurrence_count,
        "legacy_occurrence_fact_hits": occurrence_hits,
        "legacy_occurrence_fact_recall": occurrence_recall,
        "static_fact_recall": static_recall,
        "dynamic_fact_recall": dynamic_recall,
        "lexical_token_support": lexical_support,
        "target_identifier_count": len(target_identifiers),
        "identifier_support": identifier_support,
        "unsupported_identifier_candidates": unsupported_identifiers,
        "hallucination_verified": False,
        "refusal_flag": refusal,
        "error_flag": error,
        "truncation_status": "unknown",
        "structurally_valid": structurally_valid,
        "recovered_echo_tokens": output_tokens,
        "compression_ratio": compression_ratio,
        "base_quality_score": base_quality,
        "quality_percentile_in_context_bin": None,
        "quality_tier": "reject",
        "sample_weight": 0.0,
        "target_duplicate_rank": None,
    }


ARTIFACT_SCHEMA = pa.schema([
    pa.field("schema_version", pa.string(), False),
    pa.field("example_id", pa.string(), False),
    pa.field("split", pa.string(), False),
    pa.field("parent_window_id", pa.string(), False),
    pa.field("parent_window_sha256", pa.string(), False),
    pa.field("prefix_sha256", pa.string(), False),
    pa.field("stored_input_window_sha16", pa.string()),
    pa.field("nominal_window_target_tokens", pa.int64()),
    pa.field("cutoff_requested_tokens", pa.int64()),
    pa.field("actual_input_tokens", pa.int64()),
    pa.field("input_message_count", pa.int32()),
    pa.field("input_messages", MESSAGE_TYPE),
    pa.field("curriculum_bucket", pa.string()),
    pa.field("context_50k_bin", pa.int64()),
    pa.field("producer_model", pa.string()),
    pa.field("capture_endpoint", pa.string()),
    pa.field("capture_kind", pa.string()),
    pa.field("original_discarded_item_id", pa.string()),
    pa.field("fresh_capture_item_id", pa.string()),
    pa.field("raw_compaction_encrypted_content", pa.large_string()),
    pa.field("raw_compaction_envelope_chars", pa.int32()),
    pa.field("raw_compaction_sha256", pa.string()),
    pa.field("fresh_capture_id_matches_original", pa.bool_()),
    pa.field("stochastic_fresh_capture", pa.bool_()),
    pa.field("raw_envelope_is_plaintext", pa.bool_()),
    pa.field("decoder_model", pa.string()),
    pa.field("recovery_prompt_key", pa.string()),
    pa.field("recovery_candidate_count", pa.int32()),
    pa.field("recovery_candidates_metadata", CANDIDATE_TYPE),
    pa.field("selection_metric", pa.string()),
    pa.field("candidate_texts_retained", pa.bool_()),
    pa.field("recovery_best_text_raw", pa.large_string()),
    pa.field("training_target", pa.large_string()),
    pa.field("training_target_sha256", pa.string()),
    pa.field("target_status", pa.string()),
    pa.field("verified_plaintext", pa.bool_()),
    pa.field("label_is_gold", pa.bool_()),
    pa.field("inferred_compaction_instruction", pa.large_string()),
    pa.field("instruction_version", pa.string()),
    pa.field("ground_truth_fact_occurrences", pa.large_list(pa.string())),
    pa.field("ground_truth_facts_unique", pa.large_list(pa.string())),
    pa.field("recalled_facts_unique", pa.large_list(pa.string())),
    pa.field("missed_facts_unique", pa.large_list(pa.string())),
    pa.field("static_ground_truth_facts_unique", pa.large_list(pa.string())),
    pa.field("dynamic_ground_truth_facts_unique", pa.large_list(pa.string())),
    pa.field("static_recalled_facts_unique", pa.large_list(pa.string())),
    pa.field("dynamic_recalled_facts_unique", pa.large_list(pa.string())),
    pa.field("unique_fact_count", pa.int32()),
    pa.field("unique_fact_hits", pa.int32()),
    pa.field("unique_fact_recall", pa.float32()),
    pa.field("legacy_occurrence_fact_count", pa.int32()),
    pa.field("legacy_occurrence_fact_hits", pa.int32()),
    pa.field("legacy_occurrence_fact_recall", pa.float32()),
    pa.field("static_fact_recall", pa.float32()),
    pa.field("dynamic_fact_recall", pa.float32()),
    pa.field("lexical_token_support", pa.float32()),
    pa.field("target_identifier_count", pa.int32()),
    pa.field("identifier_support", pa.float32()),
    pa.field("unsupported_identifier_candidates", pa.large_list(pa.string())),
    pa.field("hallucination_verified", pa.bool_()),
    pa.field("refusal_flag", pa.bool_()),
    pa.field("error_flag", pa.bool_()),
    pa.field("truncation_status", pa.string()),
    pa.field("structurally_valid", pa.bool_()),
    pa.field("recovered_echo_tokens", pa.int64()),
    pa.field("compression_ratio", pa.float32()),
    pa.field("base_quality_score", pa.float32()),
    pa.field("quality_percentile_in_context_bin", pa.float32()),
    pa.field("quality_tier", pa.string()),
    pa.field("sample_weight", pa.float32()),
    pa.field("target_duplicate_rank", pa.int32()),
])

SFT_SCHEMA = pa.schema([
    pa.field("schema_version", pa.string(), False),
    pa.field("example_id", pa.string(), False),
    pa.field("split", pa.string(), False),
    pa.field("parent_window_id", pa.string(), False),
    pa.field("parent_window_sha256", pa.string(), False),
    pa.field("prefix_sha256", pa.string(), False),
    pa.field("quality_tier", pa.string(), False),
    pa.field("quality_score", pa.float32(), False),
    pa.field("sample_weight", pa.float32(), False),
    pa.field("curriculum_bucket", pa.string(), False),
    pa.field("actual_input_tokens", pa.int64(), False),
    pa.field("recovered_echo_tokens", pa.int64()),
    pa.field("compression_ratio", pa.float32()),
    pa.field("unique_fact_recall", pa.float32()),
    pa.field("dynamic_fact_recall", pa.float32()),
    pa.field("static_fact_recall", pa.float32()),
    pa.field("lexical_token_support", pa.float32()),
    pa.field("identifier_support", pa.float32()),
    pa.field("label_status", pa.string(), False),
    pa.field("verified_plaintext", pa.bool_(), False),
    pa.field("selection_metric", pa.string(), False),
    pa.field("instruction_version", pa.string(), False),
    pa.field("compaction_instruction", pa.large_string(), False),
    pa.field("messages", MESSAGE_TYPE, False),
    pa.field("assistant_target", pa.large_string(), False),
    pa.field("loss_scope", pa.string(), False),
    pa.field("source_raw_compaction_sha256", pa.string(), False),
])


def write_parquet(path: Path, records: list[dict], schema: pa.Schema) -> None:
    table = pa.Table.from_pylist(records, schema=schema)
    pq.write_table(
        table,
        path,
        compression="zstd",
        compression_level=9,
        use_dictionary=True,
        write_statistics=True,
        data_page_version="2.0",
        row_group_size=32,
    )


def to_sft(record: dict) -> dict:
    messages = [dict(message) for message in record["input_messages"]]
    messages.append({"role": "user", "content": INSTRUCTION})
    messages.append({"role": "assistant", "content": record["training_target"]})
    return {
        "schema_version": SCHEMA_VERSION,
        "example_id": record["example_id"],
        "split": record["split"],
        "parent_window_id": record["parent_window_id"],
        "parent_window_sha256": record["parent_window_sha256"],
        "prefix_sha256": record["prefix_sha256"],
        "quality_tier": record["quality_tier"],
        "quality_score": record["base_quality_score"],
        "sample_weight": record["sample_weight"],
        "curriculum_bucket": record["curriculum_bucket"],
        "actual_input_tokens": record["actual_input_tokens"],
        "recovered_echo_tokens": record["recovered_echo_tokens"],
        "compression_ratio": record["compression_ratio"],
        "unique_fact_recall": record["unique_fact_recall"],
        "dynamic_fact_recall": record["dynamic_fact_recall"],
        "static_fact_recall": record["static_fact_recall"],
        "lexical_token_support": record["lexical_token_support"],
        "identifier_support": record["identifier_support"],
        "label_status": "weak_pseudo_label_oracle_selected",
        "verified_plaintext": False,
        "selection_metric": record["selection_metric"],
        "instruction_version": record["instruction_version"],
        "compaction_instruction": INSTRUCTION,
        "messages": messages,
        "assistant_target": record["training_target"],
        "loss_scope": "final_assistant_message_only",
        "source_raw_compaction_sha256": record["raw_compaction_sha256"],
    }


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    rows = [json.loads(line) for line in SOURCE.open() if line.strip()]
    splits = assign_group_splits(rows)

    parent_sha: dict[str, str] = {}
    by_parent: dict[str, list[dict]] = defaultdict(list)
    for row in rows:
        by_parent[row["window_id"]].append(row)
    for parent, members in by_parent.items():
        full = max(members, key=lambda item: item["compaction"].get("input_tokens_api") or 0)
        parent_sha[parent] = sha256_text(canonical_messages(full["input_window"]))

    records = [
        compute_record(row, parent_sha[row["window_id"]], splits[row["window_id"]])
        for row in rows
    ]

    # Per-context-bin ranking prevents absolute recall from eliminating every long-context row.
    by_bin: dict[int, list[dict]] = defaultdict(list)
    for record in records:
        by_bin[record["context_50k_bin"]].append(record)
    for members in by_bin.values():
        ordered = sorted(
            members,
            key=lambda record: (
                record["dynamic_fact_recall"] if record["dynamic_fact_recall"] is not None else -1.0,
                record["unique_fact_recall"] if record["unique_fact_recall"] is not None else -1.0,
                record["base_quality_score"],
                record["example_id"],
            ),
        )
        denominator = max(1, len(ordered) - 1)
        for rank, record in enumerate(ordered):
            record["quality_percentile_in_context_bin"] = rank / denominator

    # Exact duplicate targets are not allowed to cross train/eval via separate examples.
    by_target: dict[str, list[dict]] = defaultdict(list)
    for record in records:
        by_target[record["training_target_sha256"]].append(record)
    for members in by_target.values():
        for rank, record in enumerate(sorted(members, key=lambda item: item["example_id"])):
            record["target_duplicate_rank"] = rank

    for record in records:
        structural = record["structurally_valid"] and record["target_duplicate_rank"] == 0
        unique_recall = record["unique_fact_recall"] or 0.0
        dynamic_recall = record["dynamic_fact_recall"] or 0.0
        ratio = record["compression_ratio"]
        strict = (
            structural
            and record["unique_fact_count"] >= 8
            and unique_recall >= 0.90
            and dynamic_recall >= 0.90
            and record["identifier_support"] >= 0.90
            and record["lexical_token_support"] >= 0.50
            and record["recovered_echo_tokens"] is not None
            and ratio is not None
            and ratio <= 0.60
            and record["recovery_prompt_key"] == "continue_knowledge"
        )
        broad = (
            structural
            and record["unique_fact_count"] >= 4
            and unique_recall >= 0.50
            and dynamic_recall >= 0.50
            and record["identifier_support"] >= 0.80
            and record["lexical_token_support"] >= 0.45
            and (ratio is None or ratio <= 0.80)
        )
        experimental = (
            structural
            and record["identifier_support"] >= 0.80
            and record["lexical_token_support"] >= 0.45
            and (ratio is None or ratio <= 0.80)
            and (record["quality_percentile_in_context_bin"] or 0.0) >= 0.40
        )
        if strict:
            record["quality_tier"] = "A_strict"
        elif broad:
            record["quality_tier"] = "B_broad"
        elif experimental:
            record["quality_tier"] = "C_experimental_context_balanced"
        else:
            record["quality_tier"] = "reject"

    # Reviewer-recommended window-normalized weighting: r^2 / accepted-prefix-count.
    accepted_by_window = Counter(
        record["parent_window_id"]
        for record in records
        if record["quality_tier"] != "reject"
    )
    raw_weights = []
    for record in records:
        if record["quality_tier"] == "reject":
            continue
        denominator = accepted_by_window[record["parent_window_id"]]
        weight = ((record["unique_fact_recall"] or 0.0) ** 2) / denominator
        raw_weights.append(weight)
        record["sample_weight"] = weight
    mean_weight = sum(raw_weights) / len(raw_weights) if raw_weights else 1.0
    for record in records:
        if record["quality_tier"] != "reject":
            record["sample_weight"] /= mean_weight

    strict_records = [record for record in records if record["quality_tier"] == "A_strict"]
    broad_records = [
        record for record in records if record["quality_tier"] in {"A_strict", "B_broad"}
    ]
    experimental_records = [
        record for record in records if record["quality_tier"] != "reject"
    ]
    strict_sft = [to_sft(record) for record in strict_records]
    broad_sft = [to_sft(record) for record in broad_records]
    experimental_sft = [to_sft(record) for record in experimental_records]

    outputs = {
        "compaction_artifacts.parquet": (records, ARTIFACT_SCHEMA),
        "compaction_sft_strict.parquet": (strict_sft, SFT_SCHEMA),
        "compaction_sft_broad.parquet": (broad_sft, SFT_SCHEMA),
        "compaction_sft_experimental_balanced.parquet": (experimental_sft, SFT_SCHEMA),
        "compaction_sft_train.parquet": (
            [record for record in broad_sft if record["split"] == "train"], SFT_SCHEMA
        ),
        "compaction_sft_validation.parquet": (
            [record for record in broad_sft if record["split"] == "validation"], SFT_SCHEMA
        ),
        "compaction_sft_test.parquet": (
            [record for record in broad_sft if record["split"] == "test"], SFT_SCHEMA
        ),
    }
    for name, (output_records, schema) in outputs.items():
        write_parquet(OUT / name, output_records, schema)

    split_counts = Counter(record["split"] for record in records)
    strict_counts = Counter(record["split"] for record in strict_records)
    broad_counts = Counter(record["split"] for record in broad_records)
    experimental_counts = Counter(record["split"] for record in experimental_records)
    tier_counts = Counter(record["quality_tier"] for record in records)
    file_info = {
        name: {
            "rows": len(output_records),
            "bytes": (OUT / name).stat().st_size,
            "sha256": file_sha256(OUT / name),
        }
        for name, (output_records, _) in outputs.items()
    }
    manifest = {
        "schema_version": SCHEMA_VERSION,
        "created_by": "scripts/build_parquet.py",
        "source": {
            "path": str(SOURCE.relative_to(ROOT)),
            "rows": len(rows),
            "sha256": file_sha256(SOURCE),
        },
        "data_contract_verdict": {
            "complete_input_context": True,
            "exact_fresh_remote_envelope": True,
            "original_discarded_envelope_restored": False,
            "verified_plaintext_compaction_summary": False,
            "sft_target_status": "weak_pseudo_label_oracle_selected",
            "gold_label": False,
        },
        "instruction": {
            "version": "inferred_handoff_v1",
            "terminal_role": "user",
            "text": INSTRUCTION,
            "is_known_remote_internal_prompt": False,
        },
        "splits": {
            "strategy": "stratified_by_nominal_size_then_grouped_by_parent_window_id",
            "seed": SPLIT_SEED,
            "all_artifacts": dict(split_counts),
            "strict": dict(strict_counts),
            "broad": dict(broad_counts),
            "experimental": dict(experimental_counts),
            "nested_prefix_leakage_prevented": True,
            "template_generalization_measured": False,
        },
        "tiers": {
            "counts": dict(tier_counts),
            "A_strict": (
                "Recommended only as a small warm-start/format-adaptation set; unique and dynamic "
                "fact recall >=0.90, grounded identifiers, echo count present, continue_knowledge."
            ),
            "B_broad": "Weaker pseudo-labels; unique and dynamic fact recall >=0.50.",
            "C_experimental_context_balanced": (
                "Ablation/long-context coverage only; selected by within-size-bin percentile, not "
                "absolute semantic fidelity. Do not use as production gold."
            ),
        },
        "recommended_training": {
            "file": "compaction_sft_train.parquet",
            "objective": "completion-only SFT",
            "loss_scope": "final assistant message only",
            "use_sample_weight": True,
            "curriculum": ["A_strict", "B_broad"],
            "warning": (
                "This is a synthetic weak-pseudo-label warm start, not enough evidence to claim it "
                "will make a model generally excellent at compaction."
            ),
        },
        "known_limitations": [
            "raw_compaction_encrypted_content is opaque ciphertext, not plaintext supervision",
            "recovery.best_text is a Luna reconstruction, not verified plaintext",
            "best recovery was oracle-selected using ground-truth fact substring hits",
            "candidate texts were not retained; only candidate metadata remains",
            "fresh recapture is stochastic and does not byte-restore the original discarded item",
            "fact occurrence arrays contain duplicates; all quality gates recompute unique values",
            "24 static sentinels repeat across generator templates; dynamic-salt recall is separate",
            "identifier support is a heuristic, not a verified hallucination/precision audit",
            "truncation status is unknown",
            "all conversations use fixed synthetic templates and content-family order",
            "group splits prevent prefix leakage but do not measure template generalization",
            "producer resume logic was not safe in general; current source has zero duplicate prefix hashes",
        ],
        "files": file_info,
    }
    manifest_path = OUT / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")
    print(json.dumps({
        "artifacts": len(records),
        "strict": len(strict_records),
        "broad": len(broad_records),
        "experimental": len(experimental_records),
        "tiers": dict(tier_counts),
        "files": file_info,
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
