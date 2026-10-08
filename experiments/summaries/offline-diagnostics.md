# Offline diagnostics and evidence replays

[Catalog](../INDEX.md) · [Maintenance](../README.md)

Generated from [registry.csv](../registry.csv); original reports and frozen
contracts remain authoritative. Summaries describe the dated study scope.

## rollback-e0

**Rollback E0 controller and grader verification** — 2026-10-08 · offline-complete

Offline implementation passes 66 package tests including nine actual Docker checks and five additional archive evidence probes. Independent graders agree on 210,656 finite candidates; 12 scripted math episodes retain 144 fake calls and task-level analysis. The review bundle binds 12 math tasks and eight unsent calibration requests. The full 663-test repository suite also passes with no skips.

**Limits:** Engineering fixtures only: zero model calls or measured rollback benefit. Coding selection is tested with authored doubles; no real benchmark cohort is imported. Live transport, provider token accounting/access, pricing calibration and a separate allocation remain open. Synthetic dollars are not provider spend.

Read first: [research/ROLLBACK_E0_IMPLEMENTATION_2026-10-08.md](../../research/ROLLBACK_E0_IMPLEMENTATION_2026-10-08.md); [experiments/dependency_memory/results/rollback_e0_2026-10-08/README.md](../dependency_memory/results/rollback_e0_2026-10-08/README.md); [experiments/dependency_memory/rollback_pilot/README.md](../dependency_memory/rollback_pilot/README.md); [provenance/rollback_coding_source_review_2026-10-08.json](../../provenance/rollback_coding_source_review_2026-10-08.json).

Implementation: [experiments/dependency_memory/rollback_pilot](../dependency_memory/rollback_pilot); [scripts/verify_rollback_e0.py](../../scripts/verify_rollback_e0.py); [scripts/test_rollback_e0_evidence.py](../../scripts/test_rollback_e0_evidence.py).

Protocol: [experiments/dependency_memory/rollback_pilot/EXECUTION_CONTRACT.md](../dependency_memory/rollback_pilot/EXECUTION_CONTRACT.md); [experiments/dependency_memory/rollback_pilot/EXPERIMENT_SUITE.md](../dependency_memory/rollback_pilot/EXPERIMENT_SUITE.md); [experiments/dependency_memory/rollback_pilot/TASKS_AND_GRADING.md](../dependency_memory/rollback_pilot/TASKS_AND_GRADING.md); [experiments/dependency_memory/rollback_pilot/ANALYSIS_PLAN.md](../dependency_memory/rollback_pilot/ANALYSIS_PLAN.md).

Saved results: [experiments/dependency_memory/results/rollback_e0_2026-10-08](../dependency_memory/results/rollback_e0_2026-10-08); [experiments/dependency_memory/results/rollback_validation_2026-10-08](../dependency_memory/results/rollback_validation_2026-10-08).

## scope-static

**Static source-analysis control** — 2026-10-01 · offline-complete

Static analysis agrees on 51,566 finite rows across three inspected programs and a constructed late-key family. Common-codec static/authored contracts score 24/24; five saved model contracts do too and two remain oversized.

**Limits:** Finite heuristic, not universal semantic proof. Quota uses whole-input fallback; no new model calls or natural tasks.

Claims: [C64](../../paper/claims.csv).

Read first: [research/STATIC_SCOPE_CONTROL_2026-10-01.md](../../research/STATIC_SCOPE_CONTROL_2026-10-01.md).

Implementation: [experiments/dependency_memory/scope_static](../dependency_memory/scope_static).

Protocol: [experiments/dependency_memory/scope_static/PROTOCOL.md](../dependency_memory/scope_static/PROTOCOL.md).

Saved results: [experiments/dependency_memory/results/scope_static_2026-10-01.json](../dependency_memory/results/scope_static_2026-10-01.json).

## scope-codebook

**Common-codec and cached-outcome controls** — 2026-10-01 · offline-complete

On 24 imposed late queries, ordinary authored JSON scores 12/24 while the existing fixed-schema codec and cached public outcomes each score 24/24.

**Limits:** One inspected classifier and constructed queries; serialization improvement is not automatic scope inference.

Claims: [C58](../../paper/claims.csv).

Read first: [research/SCOPE_CODEBOOK_CONTROL_2026-10-01.md](../../research/SCOPE_CODEBOOK_CONTROL_2026-10-01.md).

Implementation: [experiments/dependency_memory/scope_codebook_control.py](../dependency_memory/scope_codebook_control.py).

Saved results: [experiments/dependency_memory/results/scope_codebook_control_2026-10-01.json](../dependency_memory/results/scope_codebook_control_2026-10-01.json).

## workflow-method

**Receipt-method redundancy and timing audit** — 2026-10-01 · offline-complete

158,340 grader queries, 5,652 proposals and 52,780 bounded chains agree with an independent exact-format specification. E0001 needs no parent evidence for its actual query.

**Limits:** Known exact-table grammar; does not equate stochastic writer behavior or establish natural-workflow benefit.

Claims: [C56, C57](../../paper/claims.csv).

Read first: [research/WORKFLOW_METHOD_AUDIT_2026-10-01.md](../../research/WORKFLOW_METHOD_AUDIT_2026-10-01.md).

Implementation: [experiments/dependency_memory/workflow_prospective](../dependency_memory/workflow_prospective).

Protocol: [experiments/dependency_memory/workflow_prospective/PROTOCOL.md](../dependency_memory/workflow_prospective/PROTOCOL.md).

Saved results: [experiments/dependency_memory/results/workflow_method_2026-10-01](../dependency_memory/results/workflow_method_2026-10-01).

## workflow-intake

**Observed workflow intake E0001** — 2026-10-01 · offline-complete

One inspected development task contains six successful actual command runs at two pinned checkpoints. Direct receipts fit both memory caps.

**Limits:** One task, not six independent episodes. Its actual final query is B-only sufficient; prospective/private evaluation counts remain zero.

Claims: [C55](../../paper/claims.csv).

Read first: [experiments/dependency_memory/workflow_intake/development/E0001/README.md](../dependency_memory/workflow_intake/development/E0001/README.md).

Implementation: [experiments/dependency_memory/workflow_intake](../dependency_memory/workflow_intake).

Saved results: [experiments/dependency_memory/workflow_intake/ledger.json](../dependency_memory/workflow_intake/ledger.json); [experiments/dependency_memory/workflow_intake/development/E0001](../dependency_memory/workflow_intake/development/E0001).

## evidence-use

**Retained-evidence decision audit** — 2026-10-01 · offline-complete

Across 319 observed finals and 53 errors, a hand-written public-rule guard contradicts 32 wrong proposals while leaving 39 correct proposals uncheckable.

**Limits:** Retrospective replay of overlapping prior studies; no new model calls or measured repaired-task gain. Completeness and authenticity remain uncertified.

Claims: [C53, C54](../../paper/claims.csv).

Read first: [research/EVIDENCE_USE_AUDIT_2026-10-01.md](../../research/EVIDENCE_USE_AUDIT_2026-10-01.md).

Implementation: [experiments/dependency_memory/evidence_use](../dependency_memory/evidence_use).

Protocol: [experiments/dependency_memory/evidence_use/PROTOCOL.md](../dependency_memory/evidence_use/PROTOCOL.md).

Saved results: [experiments/dependency_memory/results/evidence_use_2026-10-01](../dependency_memory/results/evidence_use_2026-10-01).

## decoder-handoff

**Decoder-compatible handoff correction** — 2026-09-24 · offline-complete

Replaying twelve saved parent proposals rejects six that passed the old ID check; deterministic fallback supports all 252 two-owner child handoffs.

**Limits:** Offline correction, not a rescore of old terminal decisions or a guarantee of complete/true retained evidence.

Claims: [C50](../../paper/claims.csv).

Read first: [research/DECODER_COMPATIBILITY_REPLAY_2026-09-24.md](../../research/DECODER_COMPATIBILITY_REPLAY_2026-09-24.md).

Implementation: [experiments/dependency_memory/cross_record_v2](../dependency_memory/cross_record_v2).

Saved results: [experiments/dependency_memory/results/cross_record_v2_parent_replay.json](../dependency_memory/results/cross_record_v2_parent_replay.json).

## historical-replay

**Historical workflow replay** — 2026-09-22 · offline-complete

Eight actual historical attempt records support imposed byte-limited continuations and synthetic cost frontiers. Direct receipts attain the same 24/24 repaired outcomes at lower synthetic cost than iterative repair.

**Limits:** Inspected development evidence and counterfactual conditions; no historical failure is attributed to compaction and no production savings are measured.

Claims: [C41, C42, C43](../../paper/claims.csv).

Read first: [research/HISTORICAL_WORKFLOW_REPLAY_2026-09-22.md](../../research/HISTORICAL_WORKFLOW_REPLAY_2026-09-22.md).

Implementation: [experiments/dependency_memory/workflow_replay](../dependency_memory/workflow_replay).

Protocol: [experiments/dependency_memory/workflow_replay/CONTRACT.md](../dependency_memory/workflow_replay/CONTRACT.md).

Saved results: [experiments/dependency_memory/results/workflow_replay_certificate.json](../dependency_memory/results/workflow_replay_certificate.json); [experiments/dependency_memory/results/workflow_replay_report.md](../dependency_memory/results/workflow_replay_report.md).

## novelty-reduction

**Independent strategy/coloring reformulation** — 2026-09-22 · offline-complete

Recovery and extra memory are reformulated as accepted strategies and weak coloring, with independent finite comparisons.

**Limits:** Established methods and close prior work; these checks do not create new task samples or establish algorithmic novelty.

Claims: [C40](../../paper/claims.csv).

Read first: [research/FEEDBACK_NOVELTY_AUDIT_2026-09-22.md](../../research/FEEDBACK_NOVELTY_AUDIT_2026-09-22.md).

Implementation: [experiments/dependency_memory/novelty_audit](../dependency_memory/novelty_audit).

Saved results: [experiments/dependency_memory/results/feedback_novelty_certificate.json](../dependency_memory/results/feedback_novelty_certificate.json); [experiments/dependency_memory/results/feedback_novelty_report.md](../dependency_memory/results/feedback_novelty_report.md).

## feedback-loop

**Feedback before forgetting** — 2026-09-22 · offline-complete

Accumulated failure constraints repair the main fixture from 32/48 to 48/48 successful executions; latest-only feedback cycles. Forty-eight constructed contracts retain information-channel controls.

**Limits:** Strong static critical-field retention matches the loop. No generic feedback novelty or practical superiority.

Claims: [C37, C38, C39](../../paper/claims.csv).

Read first: [research/FEEDBACK_BEFORE_FORGETTING_2026-09-22.md](../../research/FEEDBACK_BEFORE_FORGETTING_2026-09-22.md).

Implementation: [experiments/dependency_memory/feedback_compaction](../dependency_memory/feedback_compaction).

Saved results: [experiments/dependency_memory/results/feedback_compaction_certificate.json](../dependency_memory/results/feedback_compaction_certificate.json); [experiments/dependency_memory/results/feedback_compaction_report.md](../dependency_memory/results/feedback_compaction_report.md).

## collision-audit

**Finite collision auditor** — 2026-09-21 · offline-complete

Twelve constructed specifications supply whole-group recovery certificates and minimum extra-state repairs, with independent controller comparisons.

**Limits:** Declared finite worlds and tools; no general prose-equivalence checker, natural-task or model gain.

Claims: [C35, C36](../../paper/claims.csv).

Read first: [research/COMPACTION_COLLISION_AUDIT_2026-09-21.md](../../research/COMPACTION_COLLISION_AUDIT_2026-09-21.md).

Implementation: [experiments/dependency_memory/collision_audit](../dependency_memory/collision_audit).

Saved results: [experiments/dependency_memory/results/collision_audit_certificate.json](../dependency_memory/results/collision_audit_certificate.json); [experiments/dependency_memory/results/collision_audit_report.md](../dependency_memory/results/collision_audit_report.md).

## heldout-renderers

**Held-out clue renderer checkpoint** — 2026-09-19 · offline-complete

Four reserved dependency families pass 120 form and 240 pair/target semantic checks.

**Limits:** Offline renderer checks only; held-out provider integration and evaluation remain unperformed.

Claims: [C28](../../paper/claims.csv).

Read first: [docs/HELDOUT_RENDERERS.md](../../docs/HELDOUT_RENDERERS.md).

Implementation: [experiments/dependency_memory/heldout_renderers.py](../dependency_memory/heldout_renderers.py); [experiments/dependency_memory/audit_heldout_renderers.py](../dependency_memory/audit_heldout_renderers.py).

Saved results: [experiments/dependency_memory/results/heldout_renderer_audit.json](../dependency_memory/results/heldout_renderer_audit.json); [experiments/dependency_memory/results/heldout_renderer_report.md](../dependency_memory/results/heldout_renderer_report.md).

## revision-replay

**Post-hoc grading of original selections** — 2026-09-19 · offline-complete

Independent grading finds three strict parent-retention deficits among 36 saved selections; every observed child choice is conditionally optimal.

**Limits:** Reuses the first development answers; zero new model calls and no measured repair.

Claims: [C26](../../paper/claims.csv).

Read first: [experiments/dependency_memory/results/revision_analysis_report.md](../dependency_memory/results/revision_analysis_report.md).

Implementation: [experiments/dependency_memory/revision_analysis.py](../dependency_memory/revision_analysis.py).

Saved results: [experiments/dependency_memory/results/revision_analysis.json](../dependency_memory/results/revision_analysis.json); [experiments/dependency_memory/results/revision_analysis_report.md](../dependency_memory/results/revision_analysis_report.md).

## pilot-fake-controls

**Development pilot fake-client controls** — 2026-09-19 · offline-complete

Offline interface and deletion controls complete 36 episodes for both optimal and forget-all selectors, with evidence availability 26/36 versus 0/36.

**Limits:** Fake-client results are not model observations. The separately frozen live development tranche has its own record.

Claims: [C24](../../paper/claims.csv).

Read first: [docs/DEVELOPMENT_PILOT.md](../../docs/DEVELOPMENT_PILOT.md).

Implementation: [experiments/dependency_memory/run_development_pilot.py](../dependency_memory/run_development_pilot.py); [experiments/dependency_memory/pilot_interface.py](../dependency_memory/pilot_interface.py); [experiments/dependency_memory/pilot_report.py](../dependency_memory/pilot_report.py).

Saved results: [experiments/dependency_memory/results/development_pilot_audit.json](../dependency_memory/results/development_pilot_audit.json).

## recovery-frontier

**Exact restricted recovery frontier** — 2026-09-19 · offline-complete

An exact success/cost frontier for the declared atomic-record selectors is checked through 2,640 scripted episodes and 3,000 calculated configurations.

**Limits:** Reliable recovery, a restricted selector class and synthetic prices; configuration counts are not independent trials.

Claims: [C17, C18, C19, C20](../../paper/claims.csv).

Read first: [experiments/dependency_memory/RECOVERY_FRONTIER.md](../dependency_memory/RECOVERY_FRONTIER.md).

Implementation: [experiments/dependency_memory/recovery_frontier.py](../dependency_memory/recovery_frontier.py); [experiments/dependency_memory/run_recovery_frontier.py](../dependency_memory/run_recovery_frontier.py).

Saved results: [experiments/dependency_memory/results/recovery_frontier_summary.json](../dependency_memory/results/recovery_frontier_summary.json); [experiments/dependency_memory/results/recovery_frontier_report.md](../dependency_memory/results/recovery_frontier_report.md); [experiments/dependency_memory/results/recovery_episodes.csv](../dependency_memory/results/recovery_episodes.csv); [experiments/dependency_memory/results/recovery_grid.csv](../dependency_memory/results/recovery_grid.csv).

## artifact-workflow

**Scripted artifact/manifest environment** — 2026-09-18 · offline-complete

320 constructed configurations exercise two record boundaries, revisions and delayed verification. In 16 tight/cheap cases, structured retention succeeds 16/16 with inspection versus 9/16 without.

**Limits:** Synthetic action costs; record-memory budgets are not token budgets. No LLM trial or held-out claim.

Claims: [C14, C15](../../paper/claims.csv).

Read first: [experiments/dependency_memory/ARTIFACT_WORKFLOW.md](../dependency_memory/ARTIFACT_WORKFLOW.md).

Implementation: [experiments/dependency_memory/artifact_workflow.py](../dependency_memory/artifact_workflow.py); [experiments/dependency_memory/run_artifact_workflow.py](../dependency_memory/run_artifact_workflow.py).

Saved results: [experiments/dependency_memory/results/artifact_workflow_summary.json](../dependency_memory/results/artifact_workflow_summary.json); [experiments/dependency_memory/results/artifact_workflow_report.md](../dependency_memory/results/artifact_workflow_report.md); [experiments/dependency_memory/results/artifact_workflow_witness.json](../dependency_memory/results/artifact_workflow_witness.json); [experiments/dependency_memory/results/artifact_workflow.csv](../dependency_memory/results/artifact_workflow.csv).

## record-retention

**Record-retention baseline diagnostic** — 2026-09-16 · offline-complete

810 constructed configurations compare LRU with dictionary retention using explicit sound retirement events; a long-lived anchor exposes the intended LRU failure.

**Limits:** Configurations are not independent model trials. Record slots and serialized bytes are distinct units; no superiority over deployed harnesses.

Claims: [C06](../../paper/claims.csv).

Read first: [experiments/dependency_memory/README.md](../dependency_memory/README.md).

Implementation: [experiments/dependency_memory/experiment.py](../dependency_memory/experiment.py).

Saved results: [experiments/dependency_memory/results/workflow_retention.csv](../dependency_memory/results/workflow_retention.csv); [experiments/dependency_memory/results/summary.json](../dependency_memory/results/summary.json); [experiments/dependency_memory/results/example_events.json](../dependency_memory/results/example_events.json).
