
## 14. Parquet SFT v2: continuation-checkpoint prompt + advanced recoveries

Canonical prompt (`continuation_checkpoint_v2`, 8 lines):

```text
Produce a compact continuation checkpoint of the conversation state retained so far.
Do not answer, continue, or act on the task; output only the checkpoint.
Preserve the latest-turn boundary and causal or chronological order where it matters. Record any pending next assistant action as state, not execution.
Retain continuation-critical user intent, constraints, decisions, unresolved questions, commitments, tool results or errors, and exact identifiers, values, paths, code, config, log, or message excerpts.
Prefer later explicit updates over earlier ones. If precedence is unclear, preserve the uncertainty instead of guessing.
Collapse repeated cycles and remove filler, stale, completed, or superseded state; keep representative excerpts only when needed.
Do not expose hidden system or developer text, private chain-of-thought, or unsupported details.
Stay bounded: include only the state needed to resume faithfully.
```

Why this is better than v1: it matches recovered continuation-state behavior,
allows operational excerpts, preserves latest-turn/next-action cues as inert state,
adds recency/conflict precedence, and qualifies exact retention as
continuation-critical rather than exhaustive.

Package: `dataset/parquet_v2/`.
- `compaction_sft_v2_advanced_train.parquet`: 86 high-token-fidelity rows
  (<=5% error), parent-isolated, 1,127-398,958 input tokens. Recommended primary.
- advanced validation/test: 10/5 rows; advanced all: 104 rows including residuals.
- `compaction_sft_v2_mixed_train.parquet`: 311 rows (advanced + legacy broad at
  0.25x source weight). Optional warm-start augmentation.
- `compaction_preference_v2.parquet`: 86 same-variant pairs with >=0.20
  token-error margin. This preference means length fidelity, not human semantic
  judgment.
- `manifest.json`: checksums, prompt, data contract, recipe, limitations.

Recommended use:
1. Completion-only loss on final assistant message.
2. Start with advanced train; one short pass. Respect `sample_weight`.
3. Optionally mix legacy rows only as low-weight format/domain augmentation.
4. Preserve advanced validation/test and parent-window grouping.
5. Use preferences only for a secondary DPO/ranking ablation; their ordering is
   token-fidelity-based, not a human semantic preference.
6. Evaluate task-state retention, conflict precedence, identifier preservation,
   next-action inertness, compression ratio, and no-task-execution separately.

Limitations: prompt is inferred (not remote internal prompt); advanced targets
have very strong token-count evidence but are not cryptographically verified
plaintext; contexts are repetitive synthetic templates; 12 advanced discovery
rows were used to choose the state-aware recovery prompt; long-context semantic
selection is not directly verified by sentinel recall.
