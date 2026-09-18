# Statistical evidence guide

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
