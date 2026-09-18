#!/usr/bin/env python3
"""Build a self-contained frontier-lab compaction research release.

Requires pyarrow. The release separates opaque envelopes, weak legacy labels,
high-token-fidelity advanced recoveries, trainer views, candidates, statistics,
and paper/local method provenance.
"""
from __future__ import annotations

import hashlib
import json
import math
import shutil
import statistics
from collections import Counter, defaultdict
from pathlib import Path

import pyarrow as pa
import pyarrow.parquet as pq

ROOT = Path(__file__).resolve().parents[1]
RELEASE = ROOT / "release" / "compaction_frontier_v1"
DATA = RELEASE / "data"
DOCS = RELEASE / "docs"
CODE = RELEASE / "code"
TRAINER = RELEASE / "trainer_views"
FULL = ROOT / "dataset" / "datapoints_full.jsonl"
ARTIFACTS_V1 = ROOT / "dataset" / "parquet" / "compaction_artifacts.parquet"
ADV_SELECTED = ROOT / "dataset" / "advanced_recovery" / "selected_recoveries.jsonl"
ADV_CANDIDATES = ROOT / "dataset" / "advanced_recovery" / "all_candidates.jsonl"
ADV_SUMMARY = ROOT / "dataset" / "advanced_recovery" / "summary.json"
V2 = ROOT / "dataset" / "parquet_v2"
SCHEMA_VERSION = "compaction-frontier-release.v1"
ECHO_OVERHEAD = 6

STATIC_FACTS = {
    "0x3f8e91ab7c42d605", "MERGE-MANIFEST-88", "gen_stamp_0xA1B2C3",
    "cold.tier.backend:8443", "phi=1.618033", "m+n+p=193", "L=7*sqrt(3)",
    "det=4.2e-7", "QLARK-SEG-001", "0x9f33c12b8a4de071", "ring:3",
    "ttl=window=morn", "TRACE-7f9a2bc4", "0xdeadbeef", "drainer.wave=512",
    "mirror:ACK:8", "AURORA-SEGMENT-001", "skyhook.mirror.gateway:9229",
    "VLFN-CLOCK-88423", "CIPHER-ROT13-BLOOM-77", "rosebud.saltness.cairn:4410",
    "KX-ACCOUNT-HASH=0x7f9a", "nearest.neighbor=42", "query:alpha.09",
}

MESSAGE_TYPE = pa.large_list(pa.struct([
    pa.field("role", pa.string(), False),
    pa.field("content", pa.large_string(), False),
]))
LEGACY_CANDIDATE_TYPE = pa.large_list(pa.struct([
    pa.field("prompt_key", pa.string()),
    pa.field("length_chars", pa.int32()),
    pa.field("dump_length_chars", pa.int32()),
    pa.field("input_tokens", pa.int64()),
    pa.field("legacy_occurrence_fact_hits", pa.int32()),
]))

MASTER_SCHEMA = pa.schema([
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
    pa.field("input_messages", MESSAGE_TYPE, False),
    pa.field("context_family", pa.string(), False),
    pa.field("context_50k_bin", pa.int64()),
    pa.field("producer_model", pa.string()),
    pa.field("capture_endpoint", pa.string()),
    pa.field("capture_kind", pa.string()),
    pa.field("original_discarded_item_id", pa.string()),
    pa.field("fresh_capture_item_id", pa.string()),
    pa.field("fresh_capture_id_matches_original", pa.bool_()),
    pa.field("stochastic_fresh_capture", pa.bool_()),
    pa.field("raw_compaction_encrypted_content", pa.large_string(), False),
    pa.field("raw_compaction_envelope_chars", pa.int32()),
    pa.field("raw_compaction_sha256", pa.string()),
    pa.field("raw_envelope_is_plaintext", pa.bool_()),
    pa.field("remote_compact_output_tokens", pa.int64()),
    pa.field("legacy_decoder_model", pa.string()),
    pa.field("legacy_recovery_prompt_key", pa.string()),
    pa.field("legacy_selection_metric", pa.string()),
    pa.field("legacy_recovery_text", pa.large_string()),
    pa.field("legacy_echo_input_tokens", pa.int64()),
    pa.field("legacy_adjusted_tokens", pa.int64()),
    pa.field("legacy_token_ratio", pa.float32()),
    pa.field("legacy_token_error", pa.float32()),
    pa.field("legacy_candidate_metadata", LEGACY_CANDIDATE_TYPE),
    pa.field("advanced_available", pa.bool_(), False),
    pa.field("advanced_benchmark_partition", pa.string()),
    pa.field("advanced_decoder_model", pa.string()),
    pa.field("advanced_variant", pa.string()),
    pa.field("advanced_replicate", pa.int32()),
    pa.field("advanced_selection_pipeline", pa.string()),
    pa.field("advanced_recovery_text", pa.large_string()),
    pa.field("advanced_echo_input_tokens", pa.int64()),
    pa.field("advanced_adjusted_tokens", pa.int64()),
    pa.field("advanced_token_ratio", pa.float32()),
    pa.field("advanced_token_error", pa.float32()),
    pa.field("advanced_improves_legacy", pa.bool_()),
    pa.field("target_status", pa.string(), False),
    pa.field("verified_plaintext", pa.bool_(), False),
    pa.field("label_is_gold", pa.bool_(), False),
    pa.field("ground_truth_fact_occurrences", pa.large_list(pa.string())),
    pa.field("ground_truth_facts_unique", pa.large_list(pa.string())),
    pa.field("static_ground_truth_facts_unique", pa.large_list(pa.string())),
    pa.field("dynamic_ground_truth_facts_unique", pa.large_list(pa.string())),
    pa.field("legacy_unique_fact_hits", pa.int32()),
    pa.field("legacy_unique_fact_recall", pa.float32()),
    pa.field("legacy_dynamic_fact_hits", pa.int32()),
    pa.field("legacy_dynamic_fact_recall", pa.float32()),
    pa.field("advanced_unique_fact_hits", pa.int32()),
    pa.field("advanced_unique_fact_recall", pa.float32()),
    pa.field("advanced_dynamic_fact_hits", pa.int32()),
    pa.field("advanced_dynamic_fact_recall", pa.float32()),
    pa.field("advanced_lexical_support", pa.float32()),
    pa.field("advanced_identifier_support", pa.float32()),
    pa.field("confidence_tier", pa.string(), False),
    pa.field("recommended_sft", pa.bool_(), False),
    pa.field("recommended_evaluation", pa.bool_(), False),
    pa.field("key_limitations", pa.large_list(pa.string()), False),
])

CANDIDATE_SCHEMA = pa.schema([
    pa.field("schema_version", pa.string(), False),
    pa.field("candidate_id", pa.string(), False),
    pa.field("example_id", pa.string(), False),
    pa.field("parent_window_id", pa.string(), False),
    pa.field("cutoff_requested_tokens", pa.int64()),
    pa.field("prefix_sha256", pa.string(), False),
    pa.field("input_tokens", pa.int64()),
    pa.field("model", pa.string()),
    pa.field("variant", pa.string()),
    pa.field("replicate", pa.int32()),
    pa.field("raw_compaction_item_id", pa.string()),
    pa.field("raw_compaction_envelope_chars", pa.int32()),
    pa.field("reported_compact_output_tokens", pa.int64()),
    pa.field("decode_input_tokens", pa.int64()),
    pa.field("decode_output_tokens", pa.int64()),
    pa.field("decode_reasoning_tokens", pa.int64()),
    pa.field("decode_errors", pa.large_list(pa.string())),
    pa.field("raw_output", pa.large_string()),
    pa.field("extracted_text", pa.large_string()),
    pa.field("extracted_chars", pa.int32()),
    pa.field("echo_input_tokens", pa.int64()),
    pa.field("echo_overhead_tokens", pa.int32()),
    pa.field("adjusted_extracted_tokens", pa.int64()),
    pa.field("token_ratio", pa.float32()),
    pa.field("extraction_error", pa.float32()),
    pa.field("unique_fact_count", pa.int32()),
    pa.field("unique_fact_hits", pa.int32()),
    pa.field("unique_fact_recall", pa.float32()),
    pa.field("dynamic_fact_count", pa.int32()),
    pa.field("dynamic_fact_hits", pa.int32()),
    pa.field("dynamic_fact_recall", pa.float32()),
    pa.field("lexical_support", pa.float32()),
    pa.field("identifier_support", pa.float32()),
    pa.field("refusal", pa.bool_()),
    pa.field("tagged_output", pa.bool_()),
    pa.field("baseline_prompt_key", pa.string()),
    pa.field("baseline_text", pa.large_string()),
    pa.field("baseline_echo_tokens", pa.int64()),
    pa.field("selected_final", pa.bool_(), False),
    pa.field("benchmark_partition", pa.string()),
])

STAT_SCHEMA = pa.schema([
    pa.field("analysis_id", pa.string(), False),
    pa.field("cohort", pa.string(), False),
    pa.field("metric", pa.string(), False),
    pa.field("value", pa.float64()),
    pa.field("numerator", pa.int64()),
    pa.field("denominator", pa.int64()),
    pa.field("ci95_low", pa.float64()),
    pa.field("ci95_high", pa.float64()),
    pa.field("unit", pa.string()),
    pa.field("method", pa.large_string()),
    pa.field("source_artifact", pa.string()),
    pa.field("interpretation", pa.large_string()),
])

EXPERIMENT_SCHEMA = pa.schema([
    pa.field("experiment_record_id", pa.string(), False),
    pa.field("source_path", pa.string(), False),
    pa.field("source_sha256", pa.string(), False),
    pa.field("source_row", pa.int64(), False),
    pa.field("experiment_stage", pa.string(), False),
    pa.field("control_condition", pa.string(), False),
    pa.field("window_id", pa.string()),
    pa.field("cutoff_requested_tokens", pa.int64()),
    pa.field("prefix_sha256", pa.string()),
    pa.field("input_tokens", pa.int64()),
    pa.field("model", pa.string()),
    pa.field("variant", pa.string()),
    pa.field("replicate", pa.int32()),
    pa.field("raw_compaction_item_id", pa.string()),
    pa.field("reported_compact_output_tokens", pa.int64()),
    pa.field("echo_input_tokens", pa.int64()),
    pa.field("adjusted_extracted_tokens", pa.int64()),
    pa.field("token_ratio", pa.float32()),
    pa.field("extraction_error", pa.float32()),
    pa.field("refusal", pa.bool_()),
    pa.field("raw_output", pa.large_string()),
    pa.field("extracted_text", pa.large_string()),
    pa.field("matches_final_selection", pa.bool_(), False),
    pa.field("record_json", pa.large_string(), False),
])

SOURCE_SCHEMA = pa.schema([
    pa.field("source_path", pa.string(), False),
    pa.field("source_role", pa.large_string(), False),
    pa.field("source_sha256", pa.string(), False),
    pa.field("source_rows", pa.int64()),
    pa.field("materialized_into", pa.large_list(pa.string()), False),
    pa.field("bundled_verbatim", pa.bool_(), False),
])

METHOD_SCHEMA = pa.schema([
    pa.field("method_id", pa.string(), False),
    pa.field("name", pa.string(), False),
    pa.field("provenance", pa.string(), False),
    pa.field("provider_surface", pa.string()),
    pa.field("model", pa.string()),
    pa.field("prompt_or_template", pa.large_string()),
    pa.field("sampling", pa.string()),
    pa.field("selection", pa.string()),
    pa.field("fallback", pa.string()),
    pa.field("observed_result", pa.large_string()),
    pa.field("recommended_use", pa.large_string()),
    pa.field("source_citation", pa.large_string()),
])


FIELD_DESCRIPTIONS = {
    "schema_version": "Stable release schema identifier.",
    "example_id": "Stable identifier for one input-prefix/compaction observation.",
    "candidate_id": "Stable row-unique identifier for one decoder candidate.",
    "split": "Parent-window-isolated train, validation, or test assignment.",
    "parent_window_id": "Identifier of the full synthetic parent window from which this prefix was cut.",
    "parent_window_sha256": "SHA-256 of the complete parent window canonical serialization.",
    "prefix_sha256": "SHA-256 of the exact prefix message list used for compaction.",
    "stored_input_window_sha16": "Legacy truncated source SHA retained for backward joins.",
    "nominal_window_target_tokens": "Requested generation size for the parent window; not an observed tokenizer count.",
    "cutoff_requested_tokens": "Requested prefix cutoff budget used by the scaling harness.",
    "actual_input_tokens": "API-reported input tokens for the compaction request; ground-truth token count for the prefix.",
    "input_tokens": "API-reported input tokens associated with the candidate's source prefix.",
    "input_message_count": "Number of chat messages in the compacted prefix.",
    "input_messages": "Complete role/content message sequence submitted for compaction.",
    "context_family": "Synthetic workload family used to generate the context.",
    "context_50k_bin": "Lower bound of the 50,000-token context-size analysis bin.",
    "producer_model": "Model requested when producing the compaction envelope.",
    "capture_endpoint": "Remote API endpoint used to obtain the fresh envelope.",
    "capture_kind": "Capture path classification, here standalone cutoff compaction.",
    "original_discarded_item_id": "Item ID recorded during generation when full ciphertext was discarded.",
    "fresh_capture_item_id": "Item ID from the later full-envelope fresh recapture.",
    "fresh_capture_id_matches_original": "Whether fresh and original item IDs match; false for every observation.",
    "stochastic_fresh_capture": "True: this is a valid fresh instance for the same input, not byte restoration.",
    "raw_compaction_encrypted_content": "Exact opaque encrypted_content string returned by fresh remote /responses/compact/.",
    "raw_compaction_envelope_chars": "Unicode character count of encrypted_content.",
    "raw_compaction_sha256": "SHA-256 of raw_compaction_encrypted_content.",
    "raw_envelope_is_plaintext": "Always false; encrypted_content is opaque ciphertext.",
    "remote_compact_output_tokens": "API-reported output tokens from the same fresh compact call that produced the retained envelope.",
    "legacy_decoder_model": "Decoder model used by the initial semantic recovery pass.",
    "legacy_recovery_prompt_key": "Winning legacy prompt family.",
    "legacy_selection_metric": "Explicit oracle selection rule used for the legacy weak label.",
    "legacy_recovery_text": "Initial semantic recovered-state candidate selected using synthetic sentinels.",
    "legacy_echo_input_tokens": "API input-token count when legacy text was re-fed as one user message.",
    "legacy_adjusted_tokens": "legacy_echo_input_tokens minus calibrated six-token message framing overhead.",
    "legacy_token_ratio": "legacy_adjusted_tokens / remote_compact_output_tokens.",
    "legacy_token_error": "Absolute value of 1 - legacy_token_ratio.",
    "legacy_candidate_metadata": "Metadata for all initial recovery attempts; full candidate text was not retained in the legacy pass.",
    "advanced_available": "Whether this example belongs to the selected advanced benchmark.",
    "advanced_benchmark_partition": "Discovery or pre-registered holdout partition.",
    "advanced_decoder_model": "Luna or Terra model yielding the selected advanced rendering.",
    "advanced_variant": "Advanced state-aware prompt variant yielding the selected rendering.",
    "advanced_replicate": "Replicate number within the advanced candidate run.",
    "advanced_selection_pipeline": "Recorded best-of-N/fallback selection lineage.",
    "advanced_recovery_text": "Selected high-token-fidelity compacted-state rendering; not verified verbatim plaintext.",
    "advanced_echo_input_tokens": "API token count when advanced recovery was re-fed as one user message.",
    "advanced_adjusted_tokens": "advanced_echo_input_tokens minus calibrated six-token framing overhead.",
    "advanced_token_ratio": "advanced_adjusted_tokens / remote_compact_output_tokens.",
    "advanced_token_error": "Absolute value of 1 - advanced_token_ratio; primary recovery confidence metric.",
    "advanced_improves_legacy": "Whether advanced token error is strictly below the paired legacy error.",
    "target_status": "Plain-language target provenance and confidence classification.",
    "verified_plaintext": "Always false: no cryptographic or byte-exact plaintext oracle exists.",
    "label_is_gold": "Always false: recovered states are pseudo-labels despite strong token evidence.",
    "ground_truth_fact_occurrences": "Original occurrence-weighted synthetic sentinels; retained for backward reproduction only.",
    "ground_truth_facts_unique": "Deduplicated sentinels known to occur in this exact input prefix.",
    "static_ground_truth_facts_unique": "Deduplicated recurring generator sentinels.",
    "dynamic_ground_truth_facts_unique": "Deduplicated per-block salts/tags and other dynamic sentinels.",
    "legacy_unique_fact_hits": "Count of unique input sentinels appearing verbatim in legacy recovery.",
    "legacy_unique_fact_recall": "legacy_unique_fact_hits / count of unique input sentinels.",
    "legacy_dynamic_fact_hits": "Count of unique dynamic sentinels appearing verbatim in legacy recovery.",
    "legacy_dynamic_fact_recall": "legacy_dynamic_fact_hits / count of unique dynamic sentinels.",
    "advanced_unique_fact_hits": "Count of unique input sentinels appearing in advanced recovery.",
    "advanced_unique_fact_recall": "advanced unique sentinel recall; completeness is not expected for selective summaries.",
    "advanced_dynamic_fact_hits": "Count of unique dynamic sentinels appearing in advanced recovery.",
    "advanced_dynamic_fact_recall": "Advanced dynamic sentinel recall.",
    "advanced_lexical_support": "Fraction of recovery output word tokens supported by the source context vocabulary.",
    "advanced_identifier_support": "Fraction of extracted identifier-like tokens supported by source identifiers.",
    "confidence_tier": "Machine-readable label tier; advanced A/B/C or legacy v1 tier.",
    "recommended_sft": "True only for parent-train advanced rows with <=5% token error.",
    "recommended_evaluation": "True for advanced rows in held-out validation/test folds.",
    "key_limitations": "Per-row copy of load-bearing interpretation caveats.",
    "model": "Decoder model for this candidate or method.",
    "variant": "Recovery prompt/template variant.",
    "replicate": "Candidate replicate index.",
    "raw_compaction_item_id": "Native compaction_summary item ID replayed to the decoder.",
    "reported_compact_output_tokens": "Remote compact output-token target used for candidate scoring.",
    "decode_input_tokens": "Decoder call input tokens.",
    "decode_output_tokens": "Decoder call output tokens.",
    "decode_reasoning_tokens": "Reasoning-token component reported for decoder output.",
    "decode_errors": "Captured decoder/API errors serialized as strings.",
    "raw_output": "Unmodified decoder text before tagged-body extraction.",
    "extracted_text": "Candidate body after removing optional <dump> wrapper.",
    "extracted_chars": "Character count of extracted_text.",
    "echo_input_tokens": "API input tokens from re-feeding extracted_text.",
    "echo_overhead_tokens": "Calibrated chat framing overhead subtracted from echo_input_tokens; six tokens.",
    "adjusted_extracted_tokens": "echo_input_tokens - echo_overhead_tokens.",
    "token_ratio": "adjusted_extracted_tokens / reported_compact_output_tokens.",
    "extraction_error": "Absolute value of 1 - token_ratio.",
    "unique_fact_count": "Number of deduplicated source sentinels.",
    "unique_fact_hits": "Deduplicated source sentinels found in candidate text.",
    "unique_fact_recall": "unique_fact_hits / unique_fact_count.",
    "dynamic_fact_count": "Number of deduplicated dynamic source sentinels.",
    "dynamic_fact_hits": "Dynamic sentinels found in candidate text.",
    "dynamic_fact_recall": "dynamic_fact_hits / dynamic_fact_count.",
    "lexical_support": "Source-vocabulary lexical support score.",
    "identifier_support": "Source-identifier grounding score.",
    "refusal": "Heuristic refusal marker.",
    "tagged_output": "Whether output used the requested <dump> wrapper.",
    "baseline_prompt_key": "Paired legacy winning prompt key.",
    "baseline_text": "Paired legacy recovered text.",
    "baseline_echo_tokens": "Paired legacy echo-back token count.",
    "selected_final": "Whether this candidate is the final selected recovery for its example.",
    "benchmark_partition": "Discovery or holdout partition inherited from selected example.",
    "analysis_id": "Stable analysis family identifier.",
    "cohort": "Population or subgroup to which the statistic applies.",
    "metric": "Machine-readable metric name.",
    "value": "Statistic value.",
    "numerator": "Event count for rate metrics.",
    "denominator": "Population count for rate metrics.",
    "ci95_low": "Lower 95% confidence bound where applicable.",
    "ci95_high": "Upper 95% confidence bound where applicable.",
    "unit": "Value unit or ratio definition.",
    "method": "Estimator, interval, test, or selection method.",
    "source_artifact": "Release artifact from which the statistic can be recomputed.",
    "interpretation": "Caveat or intended interpretation.",
    "method_id": "Stable recovery/training method identifier.",
    "name": "Human-readable method name.",
    "provenance": "Paper-authored, local adaptation, or inferred training instruction.",
    "provider_surface": "API/item surface to which the method applies.",
    "prompt_or_template": "Exact local prompt where available, otherwise faithful bounded method description.",
    "sampling": "Candidate count and sampling protocol.",
    "selection": "Candidate ranking/selection rule.",
    "fallback": "Fallback model or procedure.",
    "observed_result": "Observed result on this dataset/surface.",
    "recommended_use": "Safe research or training role.",
    "source_citation": "Paper section or local artifact establishing provenance.",
    "experiment_record_id": "Stable identifier for one raw experimental observation in one source log.",
    "source_row": "Zero-based row ordinal within the source JSONL.",
    "experiment_stage": "Paper control, prompt discovery, null control, holdout, fallback, rescue, or chunk probe stage.",
    "control_condition": "Native compaction_summary envelope or no-envelope prompt-only control.",
    "record_json": "Canonical lossless JSON serialization of the complete original experimental record.",
    "matches_final_selection": "Whether this raw observation matches a final selected output; duplicate source logs can yield multiple matches per example.",
    "source_path": "Repository-relative source artifact path.",
    "source_role": "Role in constructing the release.",
    "source_sha256": "SHA-256 of the source artifact.",
    "source_rows": "Logical record count where applicable.",
    "materialized_into": "Release artifacts containing the source's relevant data.",
    "bundled_verbatim": "Whether the source file itself is included in the release.",
}

LIMITATIONS = [
    "The raw envelope is exact opaque ciphertext, not plaintext supervision.",
    "Fresh recapture is stochastic and does not byte-restore the discarded original envelope.",
    "Advanced token-count agreement is strong evidence but not proof of verbatim plaintext.",
    "Best-of-N selection optimizes token length and creates selection optimism.",
    "Synthetic contexts use repetitive templates and recurring sentinel values.",
    "Sentinel recall measures input-prefix facts, not unknown summary-selected fact precision.",
]


def load_jsonl(path):
    return [json.loads(line) for line in path.open() if line.strip()]


def unique(values):
    return list(dict.fromkeys(values or []))


def sha256_text(value):
    return hashlib.sha256(value.encode()).hexdigest()


def file_sha256(path):
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        while chunk := handle.read(1024 * 1024):
            digest.update(chunk)
    return digest.hexdigest()


def write_parquet(path, rows, schema):
    table = pa.Table.from_pylist(rows, schema=schema)
    table = table.replace_schema_metadata({
        b"schema_version": SCHEMA_VERSION.encode(),
        b"artifact_name": path.name.encode(),
        b"producer": b"scripts/build_frontier_release.py",
        b"plaintext_claim": b"No recovered target is verified plaintext",
    })
    pq.write_table(table, path, compression="zstd", compression_level=9,
                   use_dictionary=True, write_statistics=True,
                   data_page_version="2.0", row_group_size=32)


def wilson(k, n, z=1.96):
    p = k / n
    denominator = 1 + z * z / n
    center = (p + z * z / (2 * n)) / denominator
    half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / denominator
    low = 0.0 if k == 0 else max(0.0, center - half)
    high = 1.0 if k == n else min(1.0, center + half)
    return low, high


def stat(rows, analysis_id, cohort, metric, value, numerator=None, denominator=None,
         ci=None, unit=None, method=None, source=None, interpretation=None):
    rows.append({
        "analysis_id": analysis_id, "cohort": cohort, "metric": metric,
        "value": value, "numerator": numerator, "denominator": denominator,
        "ci95_low": ci[0] if ci else None, "ci95_high": ci[1] if ci else None,
        "unit": unit, "method": method, "source_artifact": source,
        "interpretation": interpretation,
    })


def main():
    if RELEASE.exists():
        shutil.rmtree(RELEASE)
    for directory in (DATA, DOCS, CODE, TRAINER):
        directory.mkdir(parents=True, exist_ok=True)
    full = load_jsonl(FULL)
    raw_capture_rows = load_jsonl(ROOT / "raw" / "raw_big.jsonl")
    raw_capture_by = {(row["window_id"], row["cutoff_budget_tokens"]): row for row in raw_capture_rows}
    artifacts = pq.read_table(ARTIFACTS_V1).to_pylist()
    artifact_by = {(row["parent_window_id"], row["cutoff_requested_tokens"]): row for row in artifacts}
    selected = load_jsonl(ADV_SELECTED)
    selected_by = {(row["window_id"], row["cutoff_budget_tokens"]): row for row in selected}
    candidates = load_jsonl(ADV_CANDIDATES)

    master = []
    for source in full:
        compaction = source["compaction"]
        key = (source["window_id"], compaction["cutoff_budget_tokens"])
        artifact = artifact_by[key]
        advanced = selected_by.get(key)
        recovery = source["recovery"]
        raw_capture = raw_capture_by[key]
        raw_item = raw_capture["compaction_items"][0]
        remote_tokens = raw_capture.get("output_tokens")
        legacy_echo = recovery.get("best_echo_tokens")
        legacy_adjusted = max(0, legacy_echo - ECHO_OVERHEAD) if legacy_echo is not None else None
        legacy_ratio = legacy_adjusted / remote_tokens if legacy_adjusted is not None and remote_tokens else None
        facts_occ = source.get("ground_truth_facts") or []
        facts = unique(facts_occ)
        static = [fact for fact in facts if fact in STATIC_FACTS]
        dynamic = [fact for fact in facts if fact not in STATIC_FACTS]
        legacy_text = recovery.get("best_text") or ""
        legacy_hits = [fact for fact in facts if fact in legacy_text]
        legacy_dynamic_hits = [fact for fact in dynamic if fact in legacy_text]
        if advanced:
            confidence = (
                "A_high_token_fidelity_le_2pct" if advanced["extraction_error"] <= 0.02
                else "B_high_token_fidelity_le_5pct" if advanced["extraction_error"] <= 0.05
                else "C_advanced_residual"
            )
            target_status = "high_token_fidelity_recovered_state_not_verified_plaintext"
        else:
            confidence = artifact["quality_tier"]
            target_status = "legacy_weak_pseudo_label_oracle_fact_selected"
        legacy_candidates = [{
            "prompt_key": row.get("prompt_key"), "length_chars": row.get("len"),
            "dump_length_chars": row.get("dump_len"), "input_tokens": row.get("input_tokens"),
            "legacy_occurrence_fact_hits": row.get("n_fact_hits"),
        } for row in recovery.get("candidates") or []]
        master.append({
            "schema_version": SCHEMA_VERSION,
            "example_id": artifact["example_id"],
            "split": artifact["split"],
            "parent_window_id": source["window_id"],
            "parent_window_sha256": artifact["parent_window_sha256"],
            "prefix_sha256": artifact["prefix_sha256"],
            "stored_input_window_sha16": source.get("input_window_sha"),
            "nominal_window_target_tokens": artifact["nominal_window_target_tokens"],
            "cutoff_requested_tokens": compaction["cutoff_budget_tokens"],
            "actual_input_tokens": compaction["input_tokens_api"],
            "input_message_count": len(source["input_window"]),
            "input_messages": source["input_window"],
            "context_family": "synthetic_cycle_code_math_json_logs_dialogue_search",
            "context_50k_bin": artifact["context_50k_bin"],
            "producer_model": compaction.get("producer_model"),
            "capture_endpoint": artifact["capture_endpoint"],
            "capture_kind": compaction.get("kind"),
            "original_discarded_item_id": compaction["compaction_items"][0]["id"],
            "fresh_capture_item_id": raw_item["id"],
            "fresh_capture_id_matches_original": raw_capture.get("id_matches_stored"),
            "stochastic_fresh_capture": True,
            "raw_compaction_encrypted_content": raw_item["encrypted_content"],
            "raw_compaction_envelope_chars": raw_item["enc_len"],
            "raw_compaction_sha256": artifact["raw_compaction_sha256"],
            "raw_envelope_is_plaintext": False,
            "remote_compact_output_tokens": remote_tokens,
            "legacy_decoder_model": "gpt-5.6-luna",
            "legacy_recovery_prompt_key": recovery.get("best_prompt_key"),
            "legacy_selection_metric": "oracle_max_ground_truth_fact_occurrence_hits_then_length",
            "legacy_recovery_text": legacy_text,
            "legacy_echo_input_tokens": legacy_echo,
            "legacy_adjusted_tokens": legacy_adjusted,
            "legacy_token_ratio": legacy_ratio,
            "legacy_token_error": abs(1 - legacy_ratio) if legacy_ratio is not None else None,
            "legacy_candidate_metadata": legacy_candidates,
            "advanced_available": advanced is not None,
            "advanced_benchmark_partition": advanced.get("benchmark_partition") if advanced else None,
            "advanced_decoder_model": advanced.get("model") if advanced else None,
            "advanced_variant": advanced.get("variant") if advanced else None,
            "advanced_replicate": advanced.get("replicate") if advanced else None,
            "advanced_selection_pipeline": advanced.get("selection_pipeline") if advanced else None,
            "advanced_recovery_text": (advanced.get("extracted_text") or advanced.get("raw_output")) if advanced else None,
            "advanced_echo_input_tokens": advanced.get("echo_input_tokens") if advanced else None,
            "advanced_adjusted_tokens": advanced.get("adjusted_extracted_tokens") if advanced else None,
            "advanced_token_ratio": advanced.get("token_ratio") if advanced else None,
            "advanced_token_error": advanced.get("extraction_error") if advanced else None,
            "advanced_improves_legacy": advanced.get("improves_baseline_error") if advanced else None,
            "target_status": target_status,
            "verified_plaintext": False,
            "label_is_gold": False,
            "ground_truth_fact_occurrences": facts_occ,
            "ground_truth_facts_unique": facts,
            "static_ground_truth_facts_unique": static,
            "dynamic_ground_truth_facts_unique": dynamic,
            "legacy_unique_fact_hits": len(legacy_hits),
            "legacy_unique_fact_recall": len(legacy_hits) / len(facts) if facts else None,
            "legacy_dynamic_fact_hits": len(legacy_dynamic_hits),
            "legacy_dynamic_fact_recall": len(legacy_dynamic_hits) / len(dynamic) if dynamic else None,
            "advanced_unique_fact_hits": advanced.get("unique_fact_hits") if advanced else None,
            "advanced_unique_fact_recall": advanced.get("unique_fact_recall") if advanced else None,
            "advanced_dynamic_fact_hits": advanced.get("dynamic_fact_hits") if advanced else None,
            "advanced_dynamic_fact_recall": advanced.get("dynamic_fact_recall") if advanced else None,
            "advanced_lexical_support": advanced.get("lexical_support") if advanced else None,
            "advanced_identifier_support": advanced.get("identifier_support") if advanced else None,
            "confidence_tier": confidence,
            "recommended_sft": bool(advanced and advanced["extraction_error"] <= 0.05 and artifact["split"] == "train"),
            "recommended_evaluation": bool(advanced and artifact["split"] != "train"),
            "key_limitations": LIMITATIONS,
        })
    write_parquet(DATA / "examples_master.parquet", master, MASTER_SCHEMA)

    selected_keys = {
        (row["window_id"], row["cutoff_budget_tokens"], row["model"], row["variant"], row["replicate"])
        for row in selected
    }
    candidate_rows = []
    for candidate_ordinal, row in enumerate(candidates):
            key = (row["window_id"], row["cutoff_budget_tokens"])
            artifact = artifact_by[key]
            usage = row.get("decode_usage") or {}
            candidate_key = (key[0], key[1], row["model"], row["variant"], row["replicate"])
            candidate_rows.append({
                "schema_version": SCHEMA_VERSION,
                "candidate_id": sha256_text(repr((candidate_key, candidate_ordinal)))[:32],
                "example_id": artifact["example_id"],
                "parent_window_id": row["window_id"],
                "cutoff_requested_tokens": row["cutoff_budget_tokens"],
                "prefix_sha256": artifact["prefix_sha256"],
                "input_tokens": row.get("input_tokens"),
                "model": row.get("model"), "variant": row.get("variant"),
                "replicate": row.get("replicate"),
                "raw_compaction_item_id": row.get("raw_compaction_item_id"),
                "raw_compaction_envelope_chars": row.get("raw_compaction_envelope_chars"),
                "reported_compact_output_tokens": row.get("reported_compact_output_tokens"),
                "decode_input_tokens": usage.get("input_tokens"),
                "decode_output_tokens": usage.get("output_tokens"),
                "decode_reasoning_tokens": (usage.get("output_tokens_details") or {}).get("reasoning_tokens"),
                "decode_errors": [str(value) for value in row.get("decode_errors") or []],
                "raw_output": row.get("raw_output"),
                "extracted_text": row.get("extracted_text"),
                "extracted_chars": row.get("extracted_chars"),
                "echo_input_tokens": row.get("echo_input_tokens"),
                "echo_overhead_tokens": ECHO_OVERHEAD,
                "adjusted_extracted_tokens": row.get("adjusted_extracted_tokens"),
                "token_ratio": row.get("token_ratio"),
                "extraction_error": row.get("extraction_error"),
                "unique_fact_count": row.get("unique_fact_count"),
                "unique_fact_hits": row.get("unique_fact_hits"),
                "unique_fact_recall": row.get("unique_fact_recall"),
                "dynamic_fact_count": row.get("dynamic_fact_count"),
                "dynamic_fact_hits": row.get("dynamic_fact_hits"),
                "dynamic_fact_recall": row.get("dynamic_fact_recall"),
                "lexical_support": row.get("lexical_support"),
                "identifier_support": row.get("identifier_support"),
                "refusal": row.get("refusal"), "tagged_output": row.get("tagged_output"),
                "baseline_prompt_key": row.get("baseline_best_prompt_key"),
                "baseline_text": row.get("baseline_best_text"),
                "baseline_echo_tokens": row.get("baseline_echo_tokens"),
                "selected_final": candidate_key in selected_keys,
                "benchmark_partition": selected_by.get(key, {}).get("benchmark_partition"),
            })
    write_parquet(DATA / "recovery_candidates.parquet", candidate_rows, CANDIDATE_SCHEMA)

    experiment_sources = {
        "advanced_recovery_benchmark.jsonl": "paper_template_benchmark",
        "advanced_recovery_v2.jsonl": "prompt_discovery",
        "advanced_recovery_scale.jsonl": "state_exact_scale_discovery",
        "advanced_recovery_scale_null.jsonl": "no_envelope_control",
        "advanced_recovery_120.jsonl": "preregistered_holdout_luna",
        "advanced_recovery_120_terra.jsonl": "targeted_terra_fallback",
        "advanced_recovery_terra_fallback.jsonl": "early_terra_fallback",
        "advanced_recovery_n50.jsonl": "best_of_50_rescue",
        "advanced_recovery_rescue_luna.jsonl": "bounded_luna_rescue",
        "advanced_recovery_rescue_terra.jsonl": "bounded_terra_rescue",
        "chunk_recovery_probe.jsonl": "paper_figure37_chunk_probe",
    }
    selected_signatures = {
        (row["window_id"], row["cutoff_budget_tokens"], row.get("model"),
         row.get("variant"), row.get("replicate"), row.get("extracted_text"))
        for row in selected
    }
    experiment_rows = []
    experiment_paths = []
    for source_name, stage in experiment_sources.items():
        source_path = ROOT / "raw" / source_name
        source_digest = file_sha256(source_path)
        experiment_paths.append(source_path)
        for source_row, row in enumerate(load_jsonl(source_path)):
            key = (row.get("window_id"), row.get("cutoff_budget_tokens"))
            signature = (key[0], key[1], row.get("model"), row.get("variant"),
                         row.get("replicate"), row.get("extracted_text"))
            record_json = json.dumps(row, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
            experiment_rows.append({
                "experiment_record_id": sha256_text(f"{source_name}:{source_row}:{record_json}")[:32],
                "source_path": str(source_path.relative_to(ROOT)),
                "source_sha256": source_digest,
                "source_row": source_row,
                "experiment_stage": stage,
                "control_condition": "no_envelope_prompt_only" if stage == "no_envelope_control" else "native_compaction_summary_envelope",
                "window_id": key[0],
                "cutoff_requested_tokens": key[1],
                "prefix_sha256": artifact_by.get(key, {}).get("prefix_sha256"),
                "input_tokens": row.get("input_tokens"),
                "model": row.get("model"),
                "variant": row.get("variant"),
                "replicate": row.get("replicate"),
                "raw_compaction_item_id": row.get("raw_compaction_item_id"),
                "reported_compact_output_tokens": row.get("reported_compact_output_tokens"),
                "echo_input_tokens": row.get("echo_input_tokens"),
                "adjusted_extracted_tokens": row.get("adjusted_extracted_tokens"),
                "token_ratio": row.get("token_ratio"),
                "extraction_error": row.get("extraction_error"),
                "refusal": row.get("refusal"),
                "raw_output": row.get("raw_output"),
                "extracted_text": row.get("extracted_text"),
                "matches_final_selection": signature in selected_signatures,
                "record_json": record_json,
            })
    write_parquet(DATA / "recovery_experiment_runs.parquet", experiment_rows, EXPERIMENT_SCHEMA)

    selected_master = [row for row in master if row["advanced_available"]]
    write_parquet(DATA / "advanced_selected_examples.parquet", selected_master, MASTER_SCHEMA)

    # Statistical evidence table.
    stats = []
    advanced_rows = [row for row in master if row["advanced_available"]]
    holdout = [row for row in advanced_rows if row["advanced_benchmark_partition"] == "holdout"]
    discovery = [row for row in advanced_rows if row["advanced_benchmark_partition"] == "discovery"]
    for cohort, cohort_rows in (("advanced_all", advanced_rows), ("advanced_holdout", holdout), ("advanced_discovery", discovery)):
        errors = [row["advanced_token_error"] for row in cohort_rows]
        ratios = [row["advanced_token_ratio"] for row in cohort_rows]
        stat(stats, "advanced_token_fidelity", cohort, "n", len(cohort_rows), denominator=len(cohort_rows), unit="rows", source="advanced_selected_examples.parquet")
        stat(stats, "advanced_token_fidelity", cohort, "median_extraction_error", statistics.median(errors), unit="absolute_ratio_error", source="advanced_selected_examples.parquet")
        stat(stats, "advanced_token_fidelity", cohort, "mean_extraction_error", statistics.mean(errors), unit="absolute_ratio_error", source="advanced_selected_examples.parquet")
        stat(stats, "advanced_token_fidelity", cohort, "median_token_ratio", statistics.median(ratios), unit="recovered/reported", source="advanced_selected_examples.parquet")
        for tolerance in (0.005, 0.01, 0.02, 0.05, 0.1, 0.2):
            count = sum(error <= tolerance for error in errors)
            stat(stats, "advanced_token_fidelity", cohort, f"within_{tolerance:.3f}", count / len(errors), numerator=count, denominator=len(errors), ci=wilson(count, len(errors)), unit="rate", method="Wilson score 95% CI", source="advanced_selected_examples.parquet")
        x = [row["remote_compact_output_tokens"] for row in cohort_rows]
        y = [row["advanced_adjusted_tokens"] for row in cohort_rows]
        mx, my = statistics.mean(x), statistics.mean(y)
        covariance = sum((a - mx) * (b - my) for a, b in zip(x, y))
        varx = sum((a - mx) ** 2 for a in x)
        vary = sum((b - my) ** 2 for b in y)
        r = covariance / math.sqrt(varx * vary)
        slope = covariance / varx
        stat(stats, "advanced_token_fidelity", cohort, "pearson_r", r, unit="correlation", source="advanced_selected_examples.parquet")
        stat(stats, "advanced_token_fidelity", cohort, "r_squared", r * r, unit="variance_fraction", source="advanced_selected_examples.parquet")
        stat(stats, "advanced_token_fidelity", cohort, "linear_slope", slope, unit="tokens/tokens", source="advanced_selected_examples.parquet")
        stat(stats, "advanced_token_fidelity", cohort, "linear_intercept", my - slope * mx, unit="tokens", source="advanced_selected_examples.parquet")

    # Cohort, paired-method, candidate-pool, and scaling summaries.
    by_bin = defaultdict(list)
    for row in master:
        by_bin[row["context_50k_bin"]].append(row)
    for bin_start, cohort_rows in sorted(by_bin.items()):
        cohort = f"input_{bin_start}_{bin_start + 50000}"
        input_values = [row["actual_input_tokens"] for row in cohort_rows]
        output_values = [row["remote_compact_output_tokens"] for row in cohort_rows]
        envelope_values = [row["raw_compaction_envelope_chars"] for row in cohort_rows]
        compression = [out / inp for inp, out in zip(input_values, output_values)]
        legacy_known = [row for row in cohort_rows if row["legacy_token_error"] is not None]
        advanced_known = [row for row in cohort_rows if row["advanced_available"]]
        for metric, value, unit in (
            ("rows", len(cohort_rows), "rows"),
            ("input_tokens_median", statistics.median(input_values), "tokens"),
            ("input_tokens_max", max(input_values), "tokens"),
            ("compact_output_tokens_median", statistics.median(output_values), "tokens"),
            ("envelope_chars_median", statistics.median(envelope_values), "characters"),
            ("envelope_chars_max", max(envelope_values), "characters"),
            ("compact_to_input_ratio_median", statistics.median(compression), "compact_tokens/input_tokens"),
            ("legacy_echo_pair_count", len(legacy_known), "rows"),
            ("advanced_count", len(advanced_known), "rows"),
        ):
            stat(stats, "context_scaling", cohort, metric, float(value), unit=unit, source="examples_master.parquet")
        if legacy_known:
            stat(stats, "context_scaling", cohort, "legacy_token_error_median", statistics.median(row["legacy_token_error"] for row in legacy_known), unit="absolute_ratio_error", source="examples_master.parquet")
            recalls = [row["legacy_unique_fact_recall"] for row in legacy_known if row["legacy_unique_fact_recall"] is not None]
            if recalls:
                stat(stats, "context_scaling", cohort, "legacy_unique_fact_recall_median", statistics.median(recalls), unit="rate", source="examples_master.parquet")
        if advanced_known:
            stat(stats, "context_scaling", cohort, "advanced_token_error_median", statistics.median(row["advanced_token_error"] for row in advanced_known), unit="absolute_ratio_error", source="examples_master.parquet")

    for split_name, count in sorted(Counter(row["split"] for row in master).items()):
        stat(stats, "dataset_splits", split_name, "rows", float(count), denominator=len(master), unit="rows", method="Parent-window-isolated deterministic split", source="examples_master.parquet")
    for tier, count in sorted(Counter(row["confidence_tier"] for row in master).items()):
        stat(stats, "confidence_tiers", tier, "rows", float(count), denominator=len(master), unit="rows", source="examples_master.parquet")

    paired = [row for row in advanced_rows if row["legacy_token_error"] is not None]
    paired_wins = sum(row["advanced_token_error"] < row["legacy_token_error"] for row in paired)
    if paired:
        sign_p = sum(math.comb(len(paired), i) for i in range(paired_wins, len(paired) + 1)) / (2 ** len(paired))
        stat(stats, "paired_recovery_comparison", "advanced_vs_legacy", "paired_rows", len(paired), denominator=len(paired), unit="rows", source="examples_master.parquet")
        stat(stats, "paired_recovery_comparison", "advanced_vs_legacy", "advanced_win_rate", paired_wins / len(paired), numerator=paired_wins, denominator=len(paired), ci=wilson(paired_wins, len(paired)), unit="rate", method="Strictly lower token-count error; Wilson 95% CI", source="examples_master.parquet")
        stat(stats, "paired_recovery_comparison", "advanced_vs_legacy", "one_sided_sign_test_p", sign_p, unit="probability", method="Exact binomial sign test under p=0.5", source="examples_master.parquet")
        stat(stats, "paired_recovery_comparison", "advanced_vs_legacy", "median_legacy_error", statistics.median(row["legacy_token_error"] for row in paired), unit="absolute_ratio_error", source="examples_master.parquet")
        stat(stats, "paired_recovery_comparison", "advanced_vs_legacy", "median_advanced_error", statistics.median(row["advanced_token_error"] for row in paired), unit="absolute_ratio_error", source="examples_master.parquet")

    by_variant = defaultdict(list)
    for row in candidate_rows:
        if row["extraction_error"] is not None:
            by_variant[(row["model"], row["variant"])].append(row)
    for (model_name, variant), cohort_rows in sorted(by_variant.items()):
        cohort = f"{model_name}:{variant}"
        errors = [row["extraction_error"] for row in cohort_rows]
        refusals = sum(bool(row["refusal"]) for row in cohort_rows)
        stat(stats, "candidate_pool", cohort, "candidates", len(cohort_rows), unit="rows", source="recovery_candidates.parquet")
        stat(stats, "candidate_pool", cohort, "median_extraction_error", statistics.median(errors), unit="absolute_ratio_error", source="recovery_candidates.parquet")
        stat(stats, "candidate_pool", cohort, "refusal_rate", refusals / len(cohort_rows), numerator=refusals, denominator=len(cohort_rows), ci=wilson(refusals, len(cohort_rows)), unit="rate", method="Wilson score 95% CI", source="recovery_candidates.parquet")
        within = sum(error <= 0.05 for error in errors)
        stat(stats, "candidate_pool", cohort, "within_0.050", within / len(errors), numerator=within, denominator=len(errors), ci=wilson(within, len(errors)), unit="rate", method="Wilson score 95% CI", source="recovery_candidates.parquet")

    legacy_pairs = [row for row in master if row["legacy_adjusted_tokens"] is not None]
    legacy_x = [row["remote_compact_output_tokens"] for row in legacy_pairs]
    legacy_y = [row["legacy_adjusted_tokens"] for row in legacy_pairs]
    legacy_mx, legacy_my = statistics.mean(legacy_x), statistics.mean(legacy_y)
    legacy_cov = sum((a - legacy_mx) * (b - legacy_my) for a, b in zip(legacy_x, legacy_y))
    legacy_varx = sum((a - legacy_mx) ** 2 for a in legacy_x)
    legacy_vary = sum((b - legacy_my) ** 2 for b in legacy_y)
    legacy_r = legacy_cov / math.sqrt(legacy_varx * legacy_vary)
    stat(stats, "legacy_token_fidelity", "all_echo_pairs", "n", len(legacy_pairs), unit="rows", source="examples_master.parquet")
    stat(stats, "legacy_token_fidelity", "all_echo_pairs", "pearson_r", legacy_r, unit="correlation", source="examples_master.parquet")
    stat(stats, "legacy_token_fidelity", "all_echo_pairs", "median_token_ratio", statistics.median(row["legacy_token_ratio"] for row in legacy_pairs), unit="recovered/reported", source="examples_master.parquet")
    for tolerance in (0.05, 0.1, 0.2):
        count = sum(row["legacy_token_error"] <= tolerance for row in legacy_pairs)
        stat(stats, "legacy_token_fidelity", "all_echo_pairs", f"within_{tolerance:.2f}", count / len(legacy_pairs), numerator=count, denominator=len(legacy_pairs), ci=wilson(count, len(legacy_pairs)), unit="rate", method="Wilson score 95% CI", source="examples_master.parquet")

    all_output = [row["remote_compact_output_tokens"] for row in master]
    all_envelope = [row["raw_compaction_envelope_chars"] for row in master]
    all_input = [row["actual_input_tokens"] for row in master]
    for metric, values, unit in (
        ("remote_compact_output_tokens", all_output, "tokens"),
        ("raw_envelope_chars", all_envelope, "characters"),
        ("actual_input_tokens", all_input, "tokens"),
    ):
        stat(stats, "distribution", "master", f"{metric}_min", min(values), unit=unit, source="examples_master.parquet")
        stat(stats, "distribution", "master", f"{metric}_median", statistics.median(values), unit=unit, source="examples_master.parquet")
        stat(stats, "distribution", "master", f"{metric}_mean", statistics.mean(values), unit=unit, source="examples_master.parquet")
        stat(stats, "distribution", "master", f"{metric}_max", max(values), unit=unit, source="examples_master.parquet")
    stat(stats, "capture_reproducibility", "fresh_recapture", "item_id_match_rate", sum(row["fresh_capture_id_matches_original"] for row in master) / len(master), numerator=sum(row["fresh_capture_id_matches_original"] for row in master), denominator=len(master), ci=wilson(sum(row["fresh_capture_id_matches_original"] for row in master), len(master)), unit="rate", method="Fresh item ID equals originally stored item ID", source="examples_master.parquet", interpretation="Zero matches confirms fresh recapture is not byte restoration.")

    # Controls and prior baseline statistics, machine-readable constants backed by saved artifacts.
    control_values = [
        ("no_envelope_best_of_10", "median_extraction_error", 0.9894908896956349, "Null prompt without native item."),
        ("paper_figure35_best_of_5", "median_extraction_error", 0.9602011625732576, "Exact paper single-turn template on compaction_summary."),
        ("paper_figure36_best_of_5", "median_extraction_error", 0.9457208891305826, "Exact paper multi-injection template on compaction_summary."),
        ("paper_chunk_probe", "error_case_1", 0.25392670157068065, "Bounded Figure-37 approximation."),
        ("paper_chunk_probe", "error_case_2", 0.5739130434782609, "Bounded Figure-37 approximation."),
        ("paper_chunk_probe", "error_case_3", 1.0177514792899407, "Bounded Figure-37 approximation."),
        ("target_permutation_test", "empirical_p_upper", 0.00001, "100,000 permutations preserving best-of-10 selection; none matched."),
        ("echo_overhead_calibration", "input_message_overhead_tokens", 6.0, "x repeated 1/10/100 -> API input 7/16/106."),
        ("legacy_1778_pairs", "pearson_r", 0.8772618343170507, "Legacy recovery vs remote output tokens."),
        ("legacy_1778_pairs", "median_ratio_after_overhead", 1.2329875270361537, "Legacy recovery adjusted echo/reported."),
        ("legacy_1778_pairs", "within_0.05", 0.09392575928008999, "Legacy token-count agreement."),
    ]
    for cohort, metric, value, interpretation in control_values:
        stat(stats, "controls_and_baselines", cohort, metric, value, unit="various", source="saved benchmark artifacts", interpretation=interpretation)

    # Envelope scaling and data coverage.
    stat(stats, "dataset_coverage", "master", "rows", len(master), denominator=len(master), unit="rows", source="examples_master.parquet")
    stat(stats, "dataset_coverage", "master", "parent_windows", len({row["parent_window_id"] for row in master}), unit="windows", source="examples_master.parquet")
    stat(stats, "dataset_coverage", "master", "input_tokens_min", min(row["actual_input_tokens"] for row in master), unit="tokens", source="examples_master.parquet")
    stat(stats, "dataset_coverage", "master", "input_tokens_max", max(row["actual_input_tokens"] for row in master), unit="tokens", source="examples_master.parquet")
    stat(stats, "dataset_coverage", "master", "input_tokens_sum", sum(row["actual_input_tokens"] for row in master), unit="tokens", source="examples_master.parquet")
    stat(stats, "dataset_coverage", "advanced", "rows", len(advanced_rows), unit="rows", source="advanced_selected_examples.parquet")
    stat(stats, "dataset_coverage", "advanced", "input_tokens_median", statistics.median(row["actual_input_tokens"] for row in advanced_rows), unit="tokens", source="advanced_selected_examples.parquet")
    stat(stats, "dataset_coverage", "advanced", "input_tokens_max", max(row["actual_input_tokens"] for row in advanced_rows), unit="tokens", source="advanced_selected_examples.parquet")

    write_parquet(DATA / "statistical_evidence.parquet", stats, STAT_SCHEMA)

    methods = [
        {
            "method_id": "paper_gpt_fig35", "name": "GPT Figure 35 transcription",
            "provenance": "paper_authored", "provider_surface": "encrypted reasoning item",
            "model": "gpt-5.6-luna", "prompt_or_template": "Attach native thought; assistant offers <transcribed>; user says 'Yes please. But do it exactly.'; native item replayed.",
            "sampling": "up to 50 candidates in paper evaluation", "selection": "minimum |1-extracted/billed reasoning tokens| after refusal filtering", "fallback": "gpt-5.6-terra if error>0.1",
            "observed_result": "On this compaction_summary surface, best-of-5 median error 0.9602.",
            "recommended_use": "Negative/control method for compaction_summary; appropriate to paper's reasoning-item surface.",
            "source_citation": "Panfilov et al. 2026, arXiv:2608.09867, Appendix C.2 Figure 35.",
        },
        {
            "method_id": "paper_gpt_fig36", "name": "GPT Figure 36 repeated injection",
            "provenance": "paper_authored", "provider_surface": "encrypted reasoning item",
            "model": "gpt-5.6-luna", "prompt_or_template": "Native item injected three times in source template; exact duplicate request; Understood; Proceed.",
            "sampling": "up to 50 candidates", "selection": "minimum token-count extraction error", "fallback": "Terra if error>0.1",
            "observed_result": "On compaction_summary, best-of-5 median error 0.9457.",
            "recommended_use": "Negative/control on compaction_summary.",
            "source_citation": "Panfilov et al. 2026, Appendix C.2 Figure 36.",
        },
        {
            "method_id": "paper_gpt_fig37", "name": "GPT Figure 37 chunk continuation",
            "provenance": "paper_authored_with_local_approximation", "provider_surface": "encrypted reasoning item",
            "model": "gpt-5.6-luna", "prompt_or_template": "First 40 recovered tokens then exact continuation request; stitch word overlap; local surface lacks max_output_tokens so prompt-capped <=45 tokens.",
            "sampling": "bounded 3 cases, <=6 chunks", "selection": "stitched output token error", "fallback": None,
            "observed_result": "Errors 0.254, 0.574, 1.018; two refusals.",
            "recommended_use": "Methodology record, not selected recovery route.",
            "source_citation": "Panfilov et al. 2026, Appendix C.2 Figure 37.",
        },
        {
            "method_id": "local_legacy_semantic", "name": "Legacy semantic state recovery",
            "provenance": "local_adaptation", "provider_surface": "standalone /responses/compact compaction_summary",
            "model": "gpt-5.6-luna", "prompt_or_template": "continue_knowledge and facts_list, 2 attempts each",
            "sampling": "best-of-4", "selection": "oracle synthetic fact occurrence hits then length", "fallback": None,
            "observed_result": "2061 rows; old occurrence-weighted recall inflated by duplicate facts; 1778 token pairs r=0.877, median adjusted ratio 1.233.",
            "recommended_use": "Weak pseudo-label/ablation only; preserve oracle-selection provenance.",
            "source_citation": "Local scripts recover_big.py and dataset notes sections 10-12.",
        },
        {
            "method_id": "local_state_exact", "name": "Advanced compacted-state recovery",
            "provenance": "local_adaptation_informed_by_paper_selection", "provider_surface": "standalone /responses/compact compaction_summary",
            "model": "gpt-5.6-luna then Terra fallback", "prompt_or_template": "Reproduce compacted conversation state closely without expanding/re-summarizing/answering; preserve order and identifiers; output only state.",
            "sampling": "Luna best-of-10; Terra best-of-10 if error>0.1; bounded rescue", "selection": "minimum |1-(echo_tokens-6)/compact_output_tokens| after refusal filtering", "fallback": "Terra and two bounded semantic prompts",
            "observed_result": "104 rows: median error 0.00521; 101/104 <=5%; holdout 89/92 <=5%; r=0.99887 overall.",
            "recommended_use": "High-token-fidelity SFT/research tier, still not verified verbatim plaintext.",
            "source_citation": "Local advanced recovery package; paper metric/fallback adapted from Appendix C.2.",
        },
        {
            "method_id": "sft_prompt_v2", "name": "Continuation checkpoint SFT instruction",
            "provenance": "local_inferred_prompt_independently_reviewed", "provider_surface": "trainer terminal user prompt",
            "model": None, "prompt_or_template": json.loads((V2 / "manifest.json").read_text())["canonical_prompt"]["text"],
            "sampling": None, "selection": None, "fallback": None,
            "observed_result": "8-line domain-neutral prompt bundled in trainer views; not remote internal prompt.",
            "recommended_use": "Canonical completion-only SFT instruction.",
            "source_citation": "Local Parquet v2 manifest and analysis section 14.",
        },
    ]
    write_parquet(DATA / "method_catalog.parquet", methods, METHOD_SCHEMA)

    # Repository-relative source lineage. Large JSONLs are materialized into Parquet, not duplicated.
    source_specs = [
        (FULL, "Canonical merged contexts, fresh envelope, legacy recovery, and fidelity source.", ["data/examples_master.parquet"], False),
        (ROOT / "raw" / "raw_big.jsonl", "Same-call fresh /responses/compact/ envelope and API token metadata.", ["data/examples_master.parquet"], False),
        (ARTIFACTS_V1, "Legacy v1 normalized identities, hashes, folds, and quality tiers.", ["data/examples_master.parquet"], False),
        (ADV_SELECTED, "Final 104 advanced selected recoveries.", ["data/examples_master.parquet", "data/advanced_selected_examples.parquet"], False),
        (ADV_CANDIDATES, "Assembled retained advanced candidate pool.", ["data/recovery_candidates.parquet"], False),
        (ADV_SUMMARY, "Saved advanced recovery summary, confidence intervals, and limitations.", ["data/statistical_evidence.parquet", "docs/advanced_recovery_summary.json"], True),
        (ROOT / "raw" / "advanced_recovery_120.jsonl", "Luna best-of-10 state_exact candidate run.", ["data/recovery_candidates.parquet"], False),
        (ROOT / "raw" / "advanced_recovery_120_terra.jsonl", "Targeted Terra best-of-10 fallback candidates.", ["data/recovery_candidates.parquet"], False),
        (ROOT / "raw" / "advanced_recovery_rescue_luna.jsonl", "Bounded Luna rescue candidates.", ["data/recovery_candidates.parquet"], False),
        (ROOT / "raw" / "advanced_recovery_rescue_terra.jsonl", "Bounded Terra rescue candidates.", ["data/recovery_candidates.parquet"], False),
        (ROOT / "raw" / "advanced_recovery_n50.jsonl", "Luna best-of-50 final rescue candidates.", ["data/recovery_candidates.parquet"], False),
        (ROOT / "raw" / "advanced_recovery_v2.jsonl", "Twelve-envelope discovery benchmark used to choose state_exact.", ["data/statistical_evidence.parquet"], False),
        (V2 / "manifest.json", "Canonical SFT v2 prompt, trainer-view provenance, counts, and checksums.", ["trainer_views/manifest.json"], True),
        (ROOT / "notes" / "ANALYSIS.md", "Human-readable experiment analysis and limitations.", ["docs/ANALYSIS.md"], True),
    ]
    experiment_path_set = set(experiment_paths)
    source_specs = [
        (path, role, list(dict.fromkeys(materialized + (["data/recovery_experiment_runs.parquet"] if path in experiment_path_set else []))), bundled)
        for path, role, materialized, bundled in source_specs
    ]
    known_source_paths = {path for path, _, _, _ in source_specs}
    for path in experiment_paths:
        if path not in known_source_paths:
            source_specs.append((
                path,
                f"Raw experimental log for {experiment_sources[path.name]}.",
                ["data/recovery_experiment_runs.parquet"],
                False,
            ))
            known_source_paths.add(path)
    analysis_artifact_paths = sorted(set(
        list((ROOT / "raw").glob("*_summary.json"))
        + list((ROOT / "raw").glob("fidelity*.json"))
        + list((ROOT / "raw").glob("spend*.json"))
        + [ROOT / "raw" / "scale_progress.json"]
        + list((ROOT / "dataset").glob("*summary.json"))
        + [ROOT / "dataset" / "manifest.json", ROOT / "dataset" / "advanced_recovery" / "manifest.json", ROOT / "dataset" / "parquet" / "manifest.json"]
    ))
    for path in analysis_artifact_paths:
        if path not in known_source_paths:
            bundle_name = str(path.relative_to(ROOT)).replace("/", "__")
            source_specs.append((
                path,
                "Compact machine-readable run summary, manifest, spend accounting, or fidelity analysis artifact.",
                [f"docs/analysis_artifacts/{bundle_name}"],
                True,
            ))
            known_source_paths.add(path)
    source_rows = []
    for path, role, materialized, bundled in source_specs:
        if path.suffix == ".parquet":
            row_count = pq.read_metadata(path).num_rows
        elif path.suffix == ".jsonl":
            with path.open() as handle:
                row_count = sum(1 for line in handle if line.strip())
        else:
            row_count = None
        source_rows.append({
            "source_path": str(path.relative_to(ROOT)),
            "source_role": role,
            "source_sha256": file_sha256(path),
            "source_rows": row_count,
            "materialized_into": materialized,
            "bundled_verbatim": bundled,
        })
    write_parquet(DATA / "source_provenance.parquet", source_rows, SOURCE_SCHEMA)

    # Copy trainer views, code, and curated docs.
    for path in V2.glob("*.parquet"):
        shutil.copy2(path, TRAINER / path.name)
    shutil.copy2(V2 / "manifest.json", TRAINER / "manifest.json")
    for path in sorted((ROOT / "scripts").iterdir()):
        if path.is_file() and path.suffix in {".py", ".sh"}:
            shutil.copy2(path, CODE / path.name)
    (CODE / "requirements.txt").write_text("pyarrow>=19\n")
    shutil.copy2(ROOT / "notes" / "ANALYSIS.md", DOCS / "ANALYSIS.md")
    shutil.copy2(ADV_SUMMARY, DOCS / "advanced_recovery_summary.json")
    shutil.copy2(ROOT / "dataset" / "parquet" / "manifest.json", DOCS / "legacy_parquet_manifest.json")
    analysis_docs = DOCS / "analysis_artifacts"
    analysis_docs.mkdir(parents=True, exist_ok=True)
    for path in analysis_artifact_paths:
        bundle_name = str(path.relative_to(ROOT)).replace("/", "__")
        shutil.copy2(path, analysis_docs / bundle_name)

    # Human-readable release docs and schema dictionary.
    readme = """# Compaction Frontier Research Release v1

This release packages 2,061 first-party synthetic remote-compaction observations,
104 high-token-fidelity recovered compacted states, 1,410 retained final-pipeline
candidates, lossless paper/control/discovery/holdout experiment logs, statistical
evidence, paper/local method provenance, trainer views, and reproducible code.

## Start here
- Research: `data/examples_master.parquet`, `data/statistical_evidence.parquet`,
  `data/method_catalog.parquet`.
- Advanced recoveries: `data/advanced_selected_examples.parquet` and
  `data/recovery_candidates.parquet`.
- All method-development and control logs: `data/recovery_experiment_runs.parquet`.
- Source lineage: `data/source_provenance.parquet`; compact original JSON analyses are
  under `docs/analysis_artifacts/`.
- Training: `trainer_views/compaction_sft_v2_advanced_train.parquet`.
- Optional augmentation: `trainer_views/compaction_sft_v2_mixed_train.parquet`.
- Preferences: `trainer_views/compaction_preference_v2.parquet`.

## Data contract
- Exact complete synthetic input context: yes.
- Exact fresh remote `/responses/compact/` opaque envelope: yes.
- Original discarded envelope byte-restored: no; fresh recapture is stochastic.
- Verified plaintext compaction summary: no.
- Advanced state recovery: very strong token-count evidence, not cryptographic
  proof of verbatim identity.

## Recommended SFT
Use completion-only loss on the final assistant message and respect sample
weights. Preserve parent-window splits. Treat validation/test as held out. The
advanced training set spans roughly 1k-399k input tokens.

## Citation
Method inspiration: Panfilov et al., *Stealing Reasoning Traces from Proprietary
LLM APIs*, arXiv:2608.09867 (2026). Paper-authored reasoning-item templates are
separated from local compaction-summary adaptations in `method_catalog.parquet`.
"""
    (DOCS / "README.md").write_text(readme)
    citation = """cff-version: 1.2.0
title: Compaction Frontier Research Release
type: dataset
version: 1.0.0
date-released: 2026-08-12
message: Cite this dataset release and Panfilov et al. arXiv:2608.09867 for recovery-method inspiration.
references:
  - type: article
    title: Stealing Reasoning Traces from Proprietary LLM APIs
    authors:
      - family-names: Panfilov
        given-names: Alexander
      - family-names: Schmotz
        given-names: David
      - family-names: Shumailov
        given-names: Ilia
      - family-names: Beurer-Kellner
        given-names: Luca
      - family-names: Schaeffer
        given-names: Joachim
      - family-names: Prabhu
        given-names: Ameya
      - family-names: Geiping
        given-names: Jonas
      - family-names: Andriushchenko
        given-names: Maksym
    year: 2026
    url: https://arxiv.org/abs/2608.09867
    identifiers:
      - type: arxiv
        value: 2608.09867
"""
    (DOCS / "CITATION.cff").write_text(citation)

    schemas = {}
    for name in ("examples_master.parquet", "advanced_selected_examples.parquet", "recovery_candidates.parquet", "recovery_experiment_runs.parquet", "statistical_evidence.parquet", "method_catalog.parquet", "source_provenance.parquet"):
        schema = pq.read_schema(DATA / name)
        schemas[name] = [{"name": field.name, "type": str(field.type), "nullable": field.nullable, "description": FIELD_DESCRIPTIONS.get(field.name, "See artifact-specific README and method catalog.")} for field in schema]
    (DOCS / "SCHEMAS.json").write_text(json.dumps(schemas, indent=2) + "\n")
    dictionary_lines = ["# Data dictionary", "", "All token counts are API-reported unless a field explicitly says adjusted or nominal.", ""]
    for artifact_name, fields in schemas.items():
        dictionary_lines.extend([f"## `{artifact_name}`", "", "| Field | Arrow type | Nullable | Meaning |", "|---|---|---:|---|"])
        for field in fields:
            meaning = field["description"].replace("|", "\\|").replace("\n", " ")
            dictionary_lines.append(f"| `{field['name']}` | `{field['type']}` | {field['nullable']} | {meaning} |")
        dictionary_lines.append("")
    (DOCS / "DATA_DICTIONARY.md").write_text("\n".join(dictionary_lines) + "\n")

    experiment_design = """# Experiment design and evidence contract

## Scope and data origin
All contexts are deterministic, first-party synthetic conversations generated on the
researcher's own authorized ChatGPT/Codex account. They mix code, math, JSON, logs,
dialogue, and search-style blocks with measurable synthetic sentinels. No third-party
user conversations, credentials, or personal data are included.

## Remote surfaces
The producer endpoint was `https://chatgpt.com/backend-api/codex/responses/compact`
(the exact recorded string has no trailing slash). The ordinary
responses surface required SSE streaming. Standalone compact returned one
`compaction_summary` item with `id` and opaque `encrypted_content`. A separate
server-side context-management `compaction` item was fixed-size and did not yield
earlier state under decoder replay; it is not the principal target in this release.

## Scale and context ceiling
The master table contains 2,061 prefix observations across 308 parent windows. API
input-token counts, not character estimates, are authoritative. The dataset reaches
398,958 input tokens. Separate ceiling probes accepted about 449,035 tokens and
rejected a 455,000-token target on the tested Luna/backend configuration; these probes
establish an empirical 2026-08 session limit, not a contractual model limit.

## Envelope capture
The generation run initially retained item IDs and envelope lengths but discarded full
ciphertext. `capture_raw.py` later repeated the exact input prefix against remote
`/responses/compact` and retained the complete fresh `encrypted_content`. All 2,061
fresh item IDs differed from the original IDs. Therefore each row is an exact valid
(input -> fresh remote envelope) observation, but not byte restoration of the original
stochastic envelope instance. The master table takes envelope bytes and output-token
usage from the same fresh call.

## Recovery methods
Panfilov et al. (arXiv:2608.09867) demonstrated weak-decoder replay of provider-native
encrypted reasoning items, used native-item injection templates (Appendix C.2 Figures
35/36), chunk continuation (Figure 37), best-of-N refusal-filtered sampling, and
token-count extraction error. We reproduced the exact GPT template structure as
controls, then adapted the selection principle to standalone `compaction_summary`
items. The paper's encrypted reasoning item and this state-like compaction item are not
assumed identical.

The winning local `state_exact` request was:

> Reproduce the compacted conversation state you currently retain as closely as
> possible without expanding, re-summarizing, or answering the task. Preserve ordering
> and exact identifiers. Output only that compacted state.

Luna ran best-of-10; cases over 10% error received Terra best-of-10 and bounded rescue
variants. Candidate selection minimized $|1-(T_{echo}-6)/T_{compact}|$ after refusal
filtering. Every candidate and selection lineage is retained.

## Token calibration
A one-message echo calibration with 1, 10, and 100 repeated one-token strings produced
7, 16, and 106 API input tokens, establishing a six-token framing overhead on the
tested endpoint. `adjusted_*_tokens = echo_input_tokens - 6`. Remote compact output
tokens are the target count. This controls tokenization without relying on a local
tokenizer.

## Confidence ladder
1. **Exact observation:** complete input prefix, API usage, and fresh opaque envelope.
2. **High-token-fidelity recovered state:** advanced candidate whose adjusted echo count
   closely matches compact output usage; A <=2%, B <=5%, C residual.
3. **Weak pseudo-label:** legacy semantic recovery selected with synthetic fact-oracle
   assistance.
4. **Verified plaintext:** unavailable; every row is explicitly false.

Token-count identity is strong length evidence, not byte identity. Near-equal-length
paraphrases remain possible. Candidate lexical/identifier support and envelope-conditioned
null controls add independent evidence but do not make the target gold plaintext.

## Leakage and splits
Every prefix from one parent window stays in one deterministic split. Advanced
discovery rows were used to choose `state_exact`; the 92-row advanced holdout was not.
Trainer validation/test folds are parent-isolated, and the optional mixed training set
excludes broad rows whose parents occur in advanced validation/test.

## Primary limitations
- Repetitive synthetic generator templates underrepresent natural software-agent and
  long-form conversational diversity.
- Sentinel recall only measures known input facts and is not a completeness oracle for
  the remote summary.
- Best-of-N token-error selection creates selection optimism; use the pre-registered
  holdout statistics for generalization claims.
- Provider behavior, model aliases, and context ceilings can change after capture.
- No license grant is asserted by this package; users must evaluate applicable API
  terms and research-use requirements.
"""
    (DOCS / "EXPERIMENT_DESIGN.md").write_text(experiment_design)

    statistical_guide = """# Statistical evidence guide

`data/statistical_evidence.parquet` is a tidy long-form table. Rate rows retain
numerators, denominators, and Wilson 95% intervals. Recomputable rows name their
source Parquet. Control constants name the saved benchmark source; the corresponding
raw candidates, summaries, scripts, and provenance hashes are bundled or indexed.
The lossless original records are queryable in `recovery_experiment_runs.parquet`; the
`record_json` column prevents schema normalization from discarding nested fields.

## Ground-truth confidence metrics
- `remote_compact_output_tokens`: output usage from the same compact call as the envelope.
- `echo_input_tokens`: usage after re-feeding recovered text as one user message.
- `adjusted_extracted_tokens`: echo count minus six-token calibrated framing overhead.
- `token_ratio`: adjusted recovered / reported compact output.
- `extraction_error`: absolute deviation from ratio 1; this is the primary ranker.
- `lexical_support` and `identifier_support`: source grounding checks.
- Unique/dynamic fact recall: sentinel preservation, not summary completeness.

## Strongest pre-registered evidence
The 92-envelope holdout was not used to select the state-aware prompt. It records
median token error near 0.52%, 89/92 within 5%, near-unit recovered-vs-reported token
fit, and replication across Luna/Terra fallback. Exact current values and Wilson
intervals should be queried from the statistical table rather than copied from prose.

## Controls
A no-envelope prompt control had roughly 98.9% median token error, exact paper
Figure-35/36 templates had roughly 96.0%/94.6% median error on this different surface,
and 100,000 target-label permutations produced no match as good as the observed
state-exact pairing. These controls argue against prompt-length coincidence. They do
not establish verbatim identity.

## Appropriate claims
Supported: envelope-conditioned recovered state, strong token-count agreement,
continuation-oriented qualitative structure, and useful high-confidence pseudo-labels.
Not supported: decrypted bytes, hidden reasoning extraction from these rows, exact
verbatim plaintext, or a gold target guaranteed by cryptography.
"""
    (DOCS / "STATISTICAL_GUIDE.md").write_text(statistical_guide)

    # Manifest every file except manifest/checksums themselves, then write checksums.
    entries = {}
    for path in sorted(RELEASE.rglob("*")):
        if path.is_file() and path.name not in {"manifest.json", "SHA256SUMS"}:
            entries[str(path.relative_to(RELEASE))] = {
                "bytes": path.stat().st_size,
                "sha256": file_sha256(path),
                "parquet_rows": pq.read_metadata(path).num_rows if path.suffix == ".parquet" else None,
            }
    manifest = {
        "release": "compaction_frontier_v1",
        "schema_version": SCHEMA_VERSION,
        "created": "2026-08-12",
        "files": entries,
        "counts": {"master_examples": len(master), "advanced_selected": len(selected_master), "advanced_candidates": len(candidate_rows), "experiment_records": len(experiment_rows), "statistics": len(stats), "methods": len(methods), "source_artifacts": len(source_rows)},
        "primary_claim": "High token-count fidelity provides strong evidence of recovered compacted state, not proof of verbatim plaintext.",
        "rights_and_data_origin": {"synthetic_data": "No third-party user data; user-account first-party API generations. No new license grant is asserted.", "paper": "Citation only; paper text is not redistributed."},
    }
    (RELEASE / "manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")
    checksum_lines = [f"{meta['sha256']}  {name}" for name, meta in sorted(entries.items())]
    checksum_lines.append(f"{file_sha256(RELEASE / 'manifest.json')}  manifest.json")
    (RELEASE / "SHA256SUMS").write_text("\n".join(checksum_lines) + "\n")
    print(json.dumps(manifest["counts"], indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
