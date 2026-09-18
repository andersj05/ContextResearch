# Compaction Frontier Research Release v1

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
