# Research document index

Use [current status](../docs/STATUS.md) for direction and the
[experiment catalog](../experiments/INDEX.md) for outcomes. This directory holds
the detailed derivations, findings and interpretations those summaries cite.
Read by topic rather than loading every dated note.

| Topic | Entry points |
|---|---|
| Question and intuition | [Plain-language guide](PLAIN_LANGUAGE_GUIDE_2026-09-19.md), [formal proposal](LIVE_DEPENDENCY_RESEARCH_PROPOSAL_2026-09-16.md) |
| Rollback experiments | [Information loss and what the experiments measure](ROLLBACK_INFORMATION_BOUNDARY_2026-10-13.md), [completed staged-development allocation and verified replay](ROLLBACK_STAGED_CONTINUATION_2026-10-09.md), [immutable first phase](ROLLBACK_STAGED_DEVELOPMENT_2026-10-08.md), [completed mathematical follow-up](ROLLBACK_MATH_FOLLOWUP_2026-10-08.md), [continuation protocol](../experiments/dependency_memory/rollback_development_v5_continuation/PROTOCOL.md), [October 7 prior-art review](ROLLBACK_PILOT_DESIGN_2026-10-07.md), [original pilot and suite](../experiments/dependency_memory/rollback_pilot/README.md) |
| Mathematical results and certificates | [All mathematical summaries](../experiments/summaries/mathematical-checks.md), [proof audit](PROOF_AUDIT_2026-09-18.md), [full rate curve](UNRESTRICTED_RATE_CURVE_2026-10-02.md) |
| Finite code improvements | [Latest priced construction](EXACT_PRICED_GROUP_CODE_2026-10-02.md), [loss-weighted control](LOSS_WEIGHTED_OVERFLOW_2026-10-02.md), [formal convergence and finite limits](DETERMINISTIC_NEAR_LIMIT_CODE_2026-10-02.md) |
| Model observations | [All model summaries](../experiments/summaries/model-studies.md), [Luna 6 failures](LUNA6_DELAYED_FAILURES_2026-09-22.md), [cross-record findings](CROSS_RECORD_RECOVERY_2026-09-22.md), [scope-inference findings](SCOPE_INFERENCE_FINDINGS_2026-10-01.md) |
| Workflow checks and evidence use | [Offline summaries](../experiments/summaries/offline-diagnostics.md), [method audit](WORKFLOW_METHOD_AUDIT_2026-10-01.md), [evidence-use audit](EVIDENCE_USE_AUDIT_2026-10-01.md), [static scope control](STATIC_SCOPE_CONTROL_2026-10-01.md) |
| Literature and novelty | [Positioning](LITERATURE_POSITIONING_2026-09-18.md), [scaling comparison](SCALING_LITERATURE_CHECK_2026-09-19.md), [collision-audit prior art](COMPACTION_AUDIT_PRIOR_ART_2026-09-21.md), [feedback novelty audit](FEEDBACK_NOVELTY_AUDIT_2026-09-22.md), [focused source guide](../sources/READING_GUIDE.md) |
| Provider mechanisms and historical transport | [Dated survey](CONTEXT_MANAGEMENT_SURVEY_2026-09-16.md), [mathematical connections](CONTEXT_COMPACTION_MATHEMATICS_2026-09-16.md), [transport](CODEX_SUBSCRIPTION_TRANSPORT_2026-09-19.md), [isolation](LUNA_ISOLATION_FOLLOWUP_2026-09-19.md), [accounting](LUNA_ACCOUNTING_FOLLOWUP_2026-09-19.md) |
| External review and experimental validity | [Review packet](EXTERNAL_REVIEW_PACKET_2026-09-19.md), [correctness audit](CORRECTNESS_AUDIT_2026-09-19.md), [evaluation source review](PILOT_EVALUATION_REVIEW_2026-09-19.md), [protocol](../docs/EXPERIMENT_PROTOCOL.md) |

New dated findings belong here, linked from their catalog record; claims belong
in [paper/claims.csv](../paper/claims.csv). Dates describe review/evidence scope,
not present provider behavior. Follow [placement rules](../docs/REPOSITORY_STRUCTURE.md).

## Historical material

Earlier starter plans, gap matrices, search logs, and self-improvement plans preserve the history of the investigation. They are useful background and may recommend a broader direction than the current paper.

The [compaction-release inspection](COMPACTION_FRONTIER_REVERSE_ENGINEERING.md) qualifies what the supplied data establish. The older [Codex technical explanation](CODEX_COMPACTION_TECHNICAL.md) contains overstrong descriptions of hidden internals and is retained for provenance, not as the paper's authority. Interactive HTML files in this directory are historical illustrations, not validated models of proprietary behavior.
