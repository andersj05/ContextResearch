# Data dictionary

All token counts are API-reported unless a field explicitly says adjusted or nominal.

## `examples_master.parquet`

| Field | Arrow type | Nullable | Meaning |
|---|---|---:|---|
| `schema_version` | `string` | False | Stable release schema identifier. |
| `example_id` | `string` | False | Stable identifier for one input-prefix/compaction observation. |
| `split` | `string` | False | Parent-window-isolated train, validation, or test assignment. |
| `parent_window_id` | `string` | False | Identifier of the full synthetic parent window from which this prefix was cut. |
| `parent_window_sha256` | `string` | False | SHA-256 of the complete parent window canonical serialization. |
| `prefix_sha256` | `string` | False | SHA-256 of the exact prefix message list used for compaction. |
| `stored_input_window_sha16` | `string` | True | Legacy truncated source SHA retained for backward joins. |
| `nominal_window_target_tokens` | `int64` | True | Requested generation size for the parent window; not an observed tokenizer count. |
| `cutoff_requested_tokens` | `int64` | True | Requested prefix cutoff budget used by the scaling harness. |
| `actual_input_tokens` | `int64` | True | API-reported input tokens for the compaction request; ground-truth token count for the prefix. |
| `input_message_count` | `int32` | True | Number of chat messages in the compacted prefix. |
| `input_messages` | `large_list<element: struct<role: string not null, content: large_string not null>>` | False | Complete role/content message sequence submitted for compaction. |
| `context_family` | `string` | False | Synthetic workload family used to generate the context. |
| `context_50k_bin` | `int64` | True | Lower bound of the 50,000-token context-size analysis bin. |
| `producer_model` | `string` | True | Model requested when producing the compaction envelope. |
| `capture_endpoint` | `string` | True | Remote API endpoint used to obtain the fresh envelope. |
| `capture_kind` | `string` | True | Capture path classification, here standalone cutoff compaction. |
| `original_discarded_item_id` | `string` | True | Item ID recorded during generation when full ciphertext was discarded. |
| `fresh_capture_item_id` | `string` | True | Item ID from the later full-envelope fresh recapture. |
| `fresh_capture_id_matches_original` | `bool` | True | Whether fresh and original item IDs match; false for every observation. |
| `stochastic_fresh_capture` | `bool` | True | True: this is a valid fresh instance for the same input, not byte restoration. |
| `raw_compaction_encrypted_content` | `large_string` | False | Exact opaque encrypted_content string returned by fresh remote /responses/compact/. |
| `raw_compaction_envelope_chars` | `int32` | True | Unicode character count of encrypted_content. |
| `raw_compaction_sha256` | `string` | True | SHA-256 of raw_compaction_encrypted_content. |
| `raw_envelope_is_plaintext` | `bool` | True | Always false; encrypted_content is opaque ciphertext. |
| `remote_compact_output_tokens` | `int64` | True | API-reported output tokens from the same fresh compact call that produced the retained envelope. |
| `legacy_decoder_model` | `string` | True | Decoder model used by the initial semantic recovery pass. |
| `legacy_recovery_prompt_key` | `string` | True | Winning legacy prompt family. |
| `legacy_selection_metric` | `string` | True | Explicit oracle selection rule used for the legacy weak label. |
| `legacy_recovery_text` | `large_string` | True | Initial semantic recovered-state candidate selected using synthetic sentinels. |
| `legacy_echo_input_tokens` | `int64` | True | API input-token count when legacy text was re-fed as one user message. |
| `legacy_adjusted_tokens` | `int64` | True | legacy_echo_input_tokens minus calibrated six-token message framing overhead. |
| `legacy_token_ratio` | `float` | True | legacy_adjusted_tokens / remote_compact_output_tokens. |
| `legacy_token_error` | `float` | True | Absolute value of 1 - legacy_token_ratio. |
| `legacy_candidate_metadata` | `large_list<element: struct<prompt_key: string, length_chars: int32, dump_length_chars: int32, input_tokens: int64, legacy_occurrence_fact_hits: int32>>` | True | Metadata for all initial recovery attempts; full candidate text was not retained in the legacy pass. |
| `advanced_available` | `bool` | False | Whether this example belongs to the selected advanced benchmark. |
| `advanced_benchmark_partition` | `string` | True | Discovery or pre-registered holdout partition. |
| `advanced_decoder_model` | `string` | True | Luna or Terra model yielding the selected advanced rendering. |
| `advanced_variant` | `string` | True | Advanced state-aware prompt variant yielding the selected rendering. |
| `advanced_replicate` | `int32` | True | Replicate number within the advanced candidate run. |
| `advanced_selection_pipeline` | `string` | True | Recorded best-of-N/fallback selection lineage. |
| `advanced_recovery_text` | `large_string` | True | Selected high-token-fidelity compacted-state rendering; not verified verbatim plaintext. |
| `advanced_echo_input_tokens` | `int64` | True | API token count when advanced recovery was re-fed as one user message. |
| `advanced_adjusted_tokens` | `int64` | True | advanced_echo_input_tokens minus calibrated six-token framing overhead. |
| `advanced_token_ratio` | `float` | True | advanced_adjusted_tokens / remote_compact_output_tokens. |
| `advanced_token_error` | `float` | True | Absolute value of 1 - advanced_token_ratio; primary recovery confidence metric. |
| `advanced_improves_legacy` | `bool` | True | Whether advanced token error is strictly below the paired legacy error. |
| `target_status` | `string` | False | Plain-language target provenance and confidence classification. |
| `verified_plaintext` | `bool` | False | Always false: no cryptographic or byte-exact plaintext oracle exists. |
| `label_is_gold` | `bool` | False | Always false: recovered states are pseudo-labels despite strong token evidence. |
| `ground_truth_fact_occurrences` | `large_list<element: string>` | True | Original occurrence-weighted synthetic sentinels; retained for backward reproduction only. |
| `ground_truth_facts_unique` | `large_list<element: string>` | True | Deduplicated sentinels known to occur in this exact input prefix. |
| `static_ground_truth_facts_unique` | `large_list<element: string>` | True | Deduplicated recurring generator sentinels. |
| `dynamic_ground_truth_facts_unique` | `large_list<element: string>` | True | Deduplicated per-block salts/tags and other dynamic sentinels. |
| `legacy_unique_fact_hits` | `int32` | True | Count of unique input sentinels appearing verbatim in legacy recovery. |
| `legacy_unique_fact_recall` | `float` | True | legacy_unique_fact_hits / count of unique input sentinels. |
| `legacy_dynamic_fact_hits` | `int32` | True | Count of unique dynamic sentinels appearing verbatim in legacy recovery. |
| `legacy_dynamic_fact_recall` | `float` | True | legacy_dynamic_fact_hits / count of unique dynamic sentinels. |
| `advanced_unique_fact_hits` | `int32` | True | Count of unique input sentinels appearing in advanced recovery. |
| `advanced_unique_fact_recall` | `float` | True | advanced unique sentinel recall; completeness is not expected for selective summaries. |
| `advanced_dynamic_fact_hits` | `int32` | True | Count of unique dynamic sentinels appearing in advanced recovery. |
| `advanced_dynamic_fact_recall` | `float` | True | Advanced dynamic sentinel recall. |
| `advanced_lexical_support` | `float` | True | Fraction of recovery output word tokens supported by the source context vocabulary. |
| `advanced_identifier_support` | `float` | True | Fraction of extracted identifier-like tokens supported by source identifiers. |
| `confidence_tier` | `string` | False | Machine-readable label tier; advanced A/B/C or legacy v1 tier. |
| `recommended_sft` | `bool` | False | True only for parent-train advanced rows with <=5% token error. |
| `recommended_evaluation` | `bool` | False | True for advanced rows in held-out validation/test folds. |
| `key_limitations` | `large_list<element: string>` | False | Per-row copy of load-bearing interpretation caveats. |

## `advanced_selected_examples.parquet`

| Field | Arrow type | Nullable | Meaning |
|---|---|---:|---|
| `schema_version` | `string` | False | Stable release schema identifier. |
| `example_id` | `string` | False | Stable identifier for one input-prefix/compaction observation. |
| `split` | `string` | False | Parent-window-isolated train, validation, or test assignment. |
| `parent_window_id` | `string` | False | Identifier of the full synthetic parent window from which this prefix was cut. |
| `parent_window_sha256` | `string` | False | SHA-256 of the complete parent window canonical serialization. |
| `prefix_sha256` | `string` | False | SHA-256 of the exact prefix message list used for compaction. |
| `stored_input_window_sha16` | `string` | True | Legacy truncated source SHA retained for backward joins. |
| `nominal_window_target_tokens` | `int64` | True | Requested generation size for the parent window; not an observed tokenizer count. |
| `cutoff_requested_tokens` | `int64` | True | Requested prefix cutoff budget used by the scaling harness. |
| `actual_input_tokens` | `int64` | True | API-reported input tokens for the compaction request; ground-truth token count for the prefix. |
| `input_message_count` | `int32` | True | Number of chat messages in the compacted prefix. |
| `input_messages` | `large_list<element: struct<role: string not null, content: large_string not null>>` | False | Complete role/content message sequence submitted for compaction. |
| `context_family` | `string` | False | Synthetic workload family used to generate the context. |
| `context_50k_bin` | `int64` | True | Lower bound of the 50,000-token context-size analysis bin. |
| `producer_model` | `string` | True | Model requested when producing the compaction envelope. |
| `capture_endpoint` | `string` | True | Remote API endpoint used to obtain the fresh envelope. |
| `capture_kind` | `string` | True | Capture path classification, here standalone cutoff compaction. |
| `original_discarded_item_id` | `string` | True | Item ID recorded during generation when full ciphertext was discarded. |
| `fresh_capture_item_id` | `string` | True | Item ID from the later full-envelope fresh recapture. |
| `fresh_capture_id_matches_original` | `bool` | True | Whether fresh and original item IDs match; false for every observation. |
| `stochastic_fresh_capture` | `bool` | True | True: this is a valid fresh instance for the same input, not byte restoration. |
| `raw_compaction_encrypted_content` | `large_string` | False | Exact opaque encrypted_content string returned by fresh remote /responses/compact/. |
| `raw_compaction_envelope_chars` | `int32` | True | Unicode character count of encrypted_content. |
| `raw_compaction_sha256` | `string` | True | SHA-256 of raw_compaction_encrypted_content. |
| `raw_envelope_is_plaintext` | `bool` | True | Always false; encrypted_content is opaque ciphertext. |
| `remote_compact_output_tokens` | `int64` | True | API-reported output tokens from the same fresh compact call that produced the retained envelope. |
| `legacy_decoder_model` | `string` | True | Decoder model used by the initial semantic recovery pass. |
| `legacy_recovery_prompt_key` | `string` | True | Winning legacy prompt family. |
| `legacy_selection_metric` | `string` | True | Explicit oracle selection rule used for the legacy weak label. |
| `legacy_recovery_text` | `large_string` | True | Initial semantic recovered-state candidate selected using synthetic sentinels. |
| `legacy_echo_input_tokens` | `int64` | True | API input-token count when legacy text was re-fed as one user message. |
| `legacy_adjusted_tokens` | `int64` | True | legacy_echo_input_tokens minus calibrated six-token message framing overhead. |
| `legacy_token_ratio` | `float` | True | legacy_adjusted_tokens / remote_compact_output_tokens. |
| `legacy_token_error` | `float` | True | Absolute value of 1 - legacy_token_ratio. |
| `legacy_candidate_metadata` | `large_list<element: struct<prompt_key: string, length_chars: int32, dump_length_chars: int32, input_tokens: int64, legacy_occurrence_fact_hits: int32>>` | True | Metadata for all initial recovery attempts; full candidate text was not retained in the legacy pass. |
| `advanced_available` | `bool` | False | Whether this example belongs to the selected advanced benchmark. |
| `advanced_benchmark_partition` | `string` | True | Discovery or pre-registered holdout partition. |
| `advanced_decoder_model` | `string` | True | Luna or Terra model yielding the selected advanced rendering. |
| `advanced_variant` | `string` | True | Advanced state-aware prompt variant yielding the selected rendering. |
| `advanced_replicate` | `int32` | True | Replicate number within the advanced candidate run. |
| `advanced_selection_pipeline` | `string` | True | Recorded best-of-N/fallback selection lineage. |
| `advanced_recovery_text` | `large_string` | True | Selected high-token-fidelity compacted-state rendering; not verified verbatim plaintext. |
| `advanced_echo_input_tokens` | `int64` | True | API token count when advanced recovery was re-fed as one user message. |
| `advanced_adjusted_tokens` | `int64` | True | advanced_echo_input_tokens minus calibrated six-token framing overhead. |
| `advanced_token_ratio` | `float` | True | advanced_adjusted_tokens / remote_compact_output_tokens. |
| `advanced_token_error` | `float` | True | Absolute value of 1 - advanced_token_ratio; primary recovery confidence metric. |
| `advanced_improves_legacy` | `bool` | True | Whether advanced token error is strictly below the paired legacy error. |
| `target_status` | `string` | False | Plain-language target provenance and confidence classification. |
| `verified_plaintext` | `bool` | False | Always false: no cryptographic or byte-exact plaintext oracle exists. |
| `label_is_gold` | `bool` | False | Always false: recovered states are pseudo-labels despite strong token evidence. |
| `ground_truth_fact_occurrences` | `large_list<element: string>` | True | Original occurrence-weighted synthetic sentinels; retained for backward reproduction only. |
| `ground_truth_facts_unique` | `large_list<element: string>` | True | Deduplicated sentinels known to occur in this exact input prefix. |
| `static_ground_truth_facts_unique` | `large_list<element: string>` | True | Deduplicated recurring generator sentinels. |
| `dynamic_ground_truth_facts_unique` | `large_list<element: string>` | True | Deduplicated per-block salts/tags and other dynamic sentinels. |
| `legacy_unique_fact_hits` | `int32` | True | Count of unique input sentinels appearing verbatim in legacy recovery. |
| `legacy_unique_fact_recall` | `float` | True | legacy_unique_fact_hits / count of unique input sentinels. |
| `legacy_dynamic_fact_hits` | `int32` | True | Count of unique dynamic sentinels appearing verbatim in legacy recovery. |
| `legacy_dynamic_fact_recall` | `float` | True | legacy_dynamic_fact_hits / count of unique dynamic sentinels. |
| `advanced_unique_fact_hits` | `int32` | True | Count of unique input sentinels appearing in advanced recovery. |
| `advanced_unique_fact_recall` | `float` | True | advanced unique sentinel recall; completeness is not expected for selective summaries. |
| `advanced_dynamic_fact_hits` | `int32` | True | Count of unique dynamic sentinels appearing in advanced recovery. |
| `advanced_dynamic_fact_recall` | `float` | True | Advanced dynamic sentinel recall. |
| `advanced_lexical_support` | `float` | True | Fraction of recovery output word tokens supported by the source context vocabulary. |
| `advanced_identifier_support` | `float` | True | Fraction of extracted identifier-like tokens supported by source identifiers. |
| `confidence_tier` | `string` | False | Machine-readable label tier; advanced A/B/C or legacy v1 tier. |
| `recommended_sft` | `bool` | False | True only for parent-train advanced rows with <=5% token error. |
| `recommended_evaluation` | `bool` | False | True for advanced rows in held-out validation/test folds. |
| `key_limitations` | `large_list<element: string>` | False | Per-row copy of load-bearing interpretation caveats. |

## `recovery_candidates.parquet`

| Field | Arrow type | Nullable | Meaning |
|---|---|---:|---|
| `schema_version` | `string` | False | Stable release schema identifier. |
| `candidate_id` | `string` | False | Stable row-unique identifier for one decoder candidate. |
| `example_id` | `string` | False | Stable identifier for one input-prefix/compaction observation. |
| `parent_window_id` | `string` | False | Identifier of the full synthetic parent window from which this prefix was cut. |
| `cutoff_requested_tokens` | `int64` | True | Requested prefix cutoff budget used by the scaling harness. |
| `prefix_sha256` | `string` | False | SHA-256 of the exact prefix message list used for compaction. |
| `input_tokens` | `int64` | True | API-reported input tokens associated with the candidate's source prefix. |
| `model` | `string` | True | Decoder model for this candidate or method. |
| `variant` | `string` | True | Recovery prompt/template variant. |
| `replicate` | `int32` | True | Candidate replicate index. |
| `raw_compaction_item_id` | `string` | True | Native compaction_summary item ID replayed to the decoder. |
| `raw_compaction_envelope_chars` | `int32` | True | Unicode character count of encrypted_content. |
| `reported_compact_output_tokens` | `int64` | True | Remote compact output-token target used for candidate scoring. |
| `decode_input_tokens` | `int64` | True | Decoder call input tokens. |
| `decode_output_tokens` | `int64` | True | Decoder call output tokens. |
| `decode_reasoning_tokens` | `int64` | True | Reasoning-token component reported for decoder output. |
| `decode_errors` | `large_list<element: string>` | True | Captured decoder/API errors serialized as strings. |
| `raw_output` | `large_string` | True | Unmodified decoder text before tagged-body extraction. |
| `extracted_text` | `large_string` | True | Candidate body after removing optional <dump> wrapper. |
| `extracted_chars` | `int32` | True | Character count of extracted_text. |
| `echo_input_tokens` | `int64` | True | API input tokens from re-feeding extracted_text. |
| `echo_overhead_tokens` | `int32` | True | Calibrated chat framing overhead subtracted from echo_input_tokens; six tokens. |
| `adjusted_extracted_tokens` | `int64` | True | echo_input_tokens - echo_overhead_tokens. |
| `token_ratio` | `float` | True | adjusted_extracted_tokens / reported_compact_output_tokens. |
| `extraction_error` | `float` | True | Absolute value of 1 - token_ratio. |
| `unique_fact_count` | `int32` | True | Number of deduplicated source sentinels. |
| `unique_fact_hits` | `int32` | True | Deduplicated source sentinels found in candidate text. |
| `unique_fact_recall` | `float` | True | unique_fact_hits / unique_fact_count. |
| `dynamic_fact_count` | `int32` | True | Number of deduplicated dynamic source sentinels. |
| `dynamic_fact_hits` | `int32` | True | Dynamic sentinels found in candidate text. |
| `dynamic_fact_recall` | `float` | True | dynamic_fact_hits / dynamic_fact_count. |
| `lexical_support` | `float` | True | Source-vocabulary lexical support score. |
| `identifier_support` | `float` | True | Source-identifier grounding score. |
| `refusal` | `bool` | True | Heuristic refusal marker. |
| `tagged_output` | `bool` | True | Whether output used the requested <dump> wrapper. |
| `baseline_prompt_key` | `string` | True | Paired legacy winning prompt key. |
| `baseline_text` | `large_string` | True | Paired legacy recovered text. |
| `baseline_echo_tokens` | `int64` | True | Paired legacy echo-back token count. |
| `selected_final` | `bool` | False | Whether this candidate is the final selected recovery for its example. |
| `benchmark_partition` | `string` | True | Discovery or holdout partition inherited from selected example. |

## `recovery_experiment_runs.parquet`

| Field | Arrow type | Nullable | Meaning |
|---|---|---:|---|
| `experiment_record_id` | `string` | False | Stable identifier for one raw experimental observation in one source log. |
| `source_path` | `string` | False | Repository-relative source artifact path. |
| `source_sha256` | `string` | False | SHA-256 of the source artifact. |
| `source_row` | `int64` | False | Zero-based row ordinal within the source JSONL. |
| `experiment_stage` | `string` | False | Paper control, prompt discovery, null control, holdout, fallback, rescue, or chunk probe stage. |
| `control_condition` | `string` | False | Native compaction_summary envelope or no-envelope prompt-only control. |
| `window_id` | `string` | True | See artifact-specific README and method catalog. |
| `cutoff_requested_tokens` | `int64` | True | Requested prefix cutoff budget used by the scaling harness. |
| `prefix_sha256` | `string` | True | SHA-256 of the exact prefix message list used for compaction. |
| `input_tokens` | `int64` | True | API-reported input tokens associated with the candidate's source prefix. |
| `model` | `string` | True | Decoder model for this candidate or method. |
| `variant` | `string` | True | Recovery prompt/template variant. |
| `replicate` | `int32` | True | Candidate replicate index. |
| `raw_compaction_item_id` | `string` | True | Native compaction_summary item ID replayed to the decoder. |
| `reported_compact_output_tokens` | `int64` | True | Remote compact output-token target used for candidate scoring. |
| `echo_input_tokens` | `int64` | True | API input tokens from re-feeding extracted_text. |
| `adjusted_extracted_tokens` | `int64` | True | echo_input_tokens - echo_overhead_tokens. |
| `token_ratio` | `float` | True | adjusted_extracted_tokens / reported_compact_output_tokens. |
| `extraction_error` | `float` | True | Absolute value of 1 - token_ratio. |
| `refusal` | `bool` | True | Heuristic refusal marker. |
| `raw_output` | `large_string` | True | Unmodified decoder text before tagged-body extraction. |
| `extracted_text` | `large_string` | True | Candidate body after removing optional <dump> wrapper. |
| `matches_final_selection` | `bool` | False | Whether this raw observation matches a final selected output; duplicate source logs can yield multiple matches per example. |
| `record_json` | `large_string` | False | Canonical lossless JSON serialization of the complete original experimental record. |

## `statistical_evidence.parquet`

| Field | Arrow type | Nullable | Meaning |
|---|---|---:|---|
| `analysis_id` | `string` | False | Stable analysis family identifier. |
| `cohort` | `string` | False | Population or subgroup to which the statistic applies. |
| `metric` | `string` | False | Machine-readable metric name. |
| `value` | `double` | True | Statistic value. |
| `numerator` | `int64` | True | Event count for rate metrics. |
| `denominator` | `int64` | True | Population count for rate metrics. |
| `ci95_low` | `double` | True | Lower 95% confidence bound where applicable. |
| `ci95_high` | `double` | True | Upper 95% confidence bound where applicable. |
| `unit` | `string` | True | Value unit or ratio definition. |
| `method` | `large_string` | True | Estimator, interval, test, or selection method. |
| `source_artifact` | `string` | True | Release artifact from which the statistic can be recomputed. |
| `interpretation` | `large_string` | True | Caveat or intended interpretation. |

## `method_catalog.parquet`

| Field | Arrow type | Nullable | Meaning |
|---|---|---:|---|
| `method_id` | `string` | False | Stable recovery/training method identifier. |
| `name` | `string` | False | Human-readable method name. |
| `provenance` | `string` | False | Paper-authored, local adaptation, or inferred training instruction. |
| `provider_surface` | `string` | True | API/item surface to which the method applies. |
| `model` | `string` | True | Decoder model for this candidate or method. |
| `prompt_or_template` | `large_string` | True | Exact local prompt where available, otherwise faithful bounded method description. |
| `sampling` | `string` | True | Candidate count and sampling protocol. |
| `selection` | `string` | True | Candidate ranking/selection rule. |
| `fallback` | `string` | True | Fallback model or procedure. |
| `observed_result` | `large_string` | True | Observed result on this dataset/surface. |
| `recommended_use` | `large_string` | True | Safe research or training role. |
| `source_citation` | `large_string` | True | Paper section or local artifact establishing provenance. |

## `source_provenance.parquet`

| Field | Arrow type | Nullable | Meaning |
|---|---|---:|---|
| `source_path` | `string` | False | Repository-relative source artifact path. |
| `source_role` | `large_string` | False | Role in constructing the release. |
| `source_sha256` | `string` | False | SHA-256 of the source artifact. |
| `source_rows` | `int64` | True | Logical record count where applicable. |
| `materialized_into` | `large_list<element: string>` | False | Release artifacts containing the source's relevant data. |
| `bundled_verbatim` | `bool` | False | Whether the source file itself is included in the release. |

