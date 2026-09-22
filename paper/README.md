# Paper workspace

Working title: **Repeated Context Compression with Delayed Task Dependencies**. The title, venue, and authorship are provisional.

## Documents to edit

- [Manuscript](manuscript.md): the main paper entry point, including the finite example, locally audited scaling result, scripted recovery comparison, completed Luna studies, and limitations.
- [Living findings draft](findings-draft.md): a short account of what we know, what the new results change, and the next milestone. Update it together with the claim register as evidence changes.
- [Outline](outline.md): section-by-section argument and remaining work.
- [Related-work map](related-work.md): nearby results and the distinctions a novelty argument must address.
- [Claim register](claims.csv): what may currently be stated, with evidence and limitations.
- [Bibliography](references.bib): stable citation keys and known metadata. Entries with incomplete metadata say so.

Use `[@citation-key]` citations in Markdown. The builder checks keys and appends readable references to the assembled Markdown. Its HTML preview is a self-contained reading copy with headings and linked citations; it does not typeset LaTeX mathematics. The editable document is always `paper/manuscript.md`, not a generated preview.

```powershell
python scripts/build_paper.py
python scripts/validate_context_repo.py
```

Generated files are under ignored `build/paper/`. No external typesetting software is required to begin drafting.

## Current draft and update discipline

Living draft v0.15 adds the [historical workflow replay](../research/HISTORICAL_WORKFLOW_REPLAY_2026-09-22.md), claims C41-C43. Eight real attempt records support counterfactual delayed handoff failures, byte-limited receipt repair and conditional synthetic cost frontiers. Direct receipts outperform iterative repair costs. Scope controls test reuse/invalidation. The evidence was inspected during development; there is no held-out, compaction-causal or production-saving claim.

Living draft v0.14 adds the [strict novelty audit](../research/FEEDBACK_NOVELTY_AUDIT_2026-09-22.md), claim C40. The finite recovery/repair objective is explicitly reformulated as accepted strategies and weak coloring, with independent checks. Close architectural precedents further narrow the claim: no general feedback-algorithm novelty or practical superiority is established. Realistic evidence extraction and measured utility remain open systems questions.

Living draft v0.13 adds the [execution-graded feedback loop](../research/FEEDBACK_BEFORE_FORGETTING_2026-09-22.md), claims C37-C39. The finite loop repairs a weak schema and exposes cycling and information-channel mistakes, while the strong critical-field baseline matches it. Two actual record boundaries and 48 constructed contracts are implemented. No LLM, natural-task or matched-total-cost advantage is established; generic feedback and cumulative constraints are attributed to prior work.

Living draft v0.12 adds the [compaction collision auditor](../research/COMPACTION_COLLISION_AUDIT_2026-09-21.md), claims C35-C36. This is a user-directed research pivot to executable whole-group failure and recovery certificates, with 12 constructed diagnostics and a finite repair codebook. Established dynamic programming and hypergraph methods are attributed; publication novelty, natural-task integration and practical improvement remain open. Prior mathematical and model-study evidence is preserved.

Living draft v0.11 adds the [decoder-complete rate-two certificate](../research/DECODER_COMPLETE_FRONTIER_2026-09-21.md), claim C34: a strict limiting-error interval (0.2618989799, 0.2618989801) and an all-k lower bound allowing every decoder. The standard-library verifier covers 1,679,616 decoder tables. Publication novelty and external correctness review remain open.

Living draft v0.10 added the [September 21 joint-coding extension](../research/JOINT_BLOCK_CODING_2026-09-21.md), claims C31-C33: a finite two-block improvement, an asymptotic upper bound at rate two, and the approximately 2.5488-bit threshold for approaching the child optimum. The earlier model studies are unchanged. The explicit finite witness is executable; the long-block results are analytic existence statements, with novelty and external review open.

The manuscript now incorporates the [exact finite-chain optimum](../research/EXACT_CHAIN_OPTIMUM_2026-09-19.md), [locally audited scaling derivation](../research/PROOF_AUDIT_2026-09-18.md), and [exact restricted recovery results](../experiments/dependency_memory/results/recovery_frontier_report.md). External review and novelty remain open. The short findings draft is versioned and dated; v0.3 added the [correctness audit](../research/CORRECTNESS_AUDIT_2026-09-19.md) and its refinements to the [staged pilot](../docs/LLM_PILOT_SPEC.md). For a new result, update its claim-register evidence and limitation, then the relevant manuscript/draft paragraphs and `docs/STATUS.md`. Keep the negative controls and avoid turning experiment plans into reported outcomes. Realistic agent performance remains unresolved.

Templates: [derivation](templates/derivation.md), [source note](templates/source-note.md), [experiment plan](templates/experiment-plan.md). The [current protocol](../docs/EXPERIMENT_PROTOCOL.md) is the governing experimental specification.

Living draft v0.9 includes the 96-request Luna tranche (C25), exact post-hoc parent/child grading (C26), the revision-direction design (C27), the offline held-out clue checkpoint (C28), the completed 24-request follow-up (C29), and the completed 1,536-request matched retention study (C30). The latter's primary comparison yields a small normalized benefit whose descriptive interval includes zero; improvement is not established. The follow-up's 24 optimal choices concern a separate simplified task and do not establish a fix for the first workflow. The earlier fake controls remain C24. No native-harness superiority or external endorsement is established; held-out request integration and evaluation remain unfinished.
