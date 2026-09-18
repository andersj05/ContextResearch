# Research map and authority

## Active documents

| Read for | Document | Evidence status |
|---|---|---|
| Current task and next steps | [Status](STATUS.md) | Current handoff |
| Formal model, finite proof, implementation plan | [September 16 proposal](../research/LIVE_DEPENDENCY_RESEARCH_PROPOSAL_2026-09-16.md) | Checked finite example; proposed general research |
| Harness mechanisms and cost model | [Compaction survey](../research/CONTEXT_MANAGEMENT_SURVEY_2026-09-16.md) | Dated official-source and pinned-code review |
| Mathematical connections | [Mathematics addendum](../research/CONTEXT_COMPACTION_MATHEMATICS_2026-09-16.md) | Established foundations and conditional deductions |
| Native-state and cache controls | [Experiment protocol](EXPERIMENT_PROTOCOL.md) | Planned experimental contract |
| Completed computations | [Prototype README](../experiments/dependency_memory/README.md) | Reproducible offline diagnostics |
| Scaling extensions and proposed next contribution | [September 18 research memo](../research/CREATIVE_RESEARCH_DIRECTIONS_2026-09-18.md) | Local derivations; see the audit for corrected scope and analytic entropy proof |
| Proof validity and remaining novelty questions | [Local proof audit](../research/PROOF_AUDIT_2026-09-18.md) | Local analytic audit and independent computational formulations; external review open |
| Scripted actions and delayed terminal outcomes | [Artifact/manifest environment](../experiments/dependency_memory/ARTIFACT_WORKFLOW.md) | 320 constructed development configurations; no LLM trial |
| Current writing | [Paper workspace](../paper/README.md) | Draft; incomplete results clearly marked |

## Broader inherited library

The migration preserves 171 academic PDFs and their notes, 219 source records, 32 implementation notes, and 16 practitioner/benchmark notes. The September 4 corpus included a broader self-improving-harness agenda. It remains useful for source discovery and experimental validity, but its earlier recommended thesis does not supersede the current finite-memory question.

Use [the academic index](../paper-notes/INDEX.md), [the implementation index](../source-notes/INDEX.md), [source catalog](../catalog/sources.csv), and [historical overview](../HARNESS_CORPUS_README.md). A migration is not a new review of every source. Some inherited metadata are older than the active review; for example, the active survey identifies Nagle et al.'s NeurIPS 2024 publication while the earlier broad catalog labels its arXiv entry as a preprint. Resolve such differences explicitly before publication.

## Historical compaction release

Read [the qualified September 11 inspection](../research/COMPACTION_FRONTIER_REVERSE_ENGINEERING.md) before the supplied [release](../compaction_frontier_v1/docs/README.md).

- Its claimed 2,061 compaction observations and 104 selected renderings are package contents, not new experiments in this project.
- Token-length agreement does not prove recovered plaintext identity or expose a provider's algorithm.
- The release's original paths and collection dependencies are not all present; its historical build scripts are not an end-to-end reproducible pipeline here.
- Its trainer views are not certified gold labels.
- [The older technical explanation](../research/CODEX_COMPACTION_TECHNICAL.md) makes stronger statements about hidden mechanisms than the data justify. Preserve it as historical material, not as authority for the paper.

## Source snapshots

The [September 16 snapshots](../sources/harness-snapshots/2026-09-16/README.md) contain the source slices and GitHub tree records used for the harness survey. They are evidence snapshots, not runnable installations or current branches. Upstream repository names, commit IDs, and local hashes are retained.

## Precedence when documents disagree

For project scope, use current status and recorded decisions. For empirical claims, use original source evidence and reproducible results, not a newer document merely because it is newer. For the paper, every substantive claim should identify its assumptions and evidence in [the claim register](../paper/claims.csv). Unresolved disagreements should remain visible.
