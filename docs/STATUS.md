# Current research status

Updated: September 18, 2026. This document is the current handoff; older scope documents are historical.

## Objective

Develop a mathematically precise and implementable study of repeated agent compaction when relevance is revealed over time. The target is a restricted compatibility result plus controlled evidence of whether the mechanism matters in tool-agent tasks.

## Established in this repository

- A causal two-stage model: see all values, compress, learn a candidate subset, compress again, then learn the queried coordinate.
- Standard counting and random-access lower bounds, with explicit assumptions and attribution.
- A finite four-bit obstruction: with a random three-coordinate subset and a final one-bit memory, attaining 25% error requires at least three initial bits. Two initial bits cannot attain 25%, although each isolated bottleneck permits error at most 25%.
- An analytic eight-state lower bound, an exhaustive 256-assignment certificate, and an explicit three-bit witness graded on 192 cases.
- A conservative two-bit chain-error lower bound of 49/192. The exact optimum remains unknown here.
- A deterministic record-retention diagnostic with revisions and observable retirement events: 810 configurations, deliberately constructed to expose plain LRU's weakness. This does not compare LLMs or native harnesses.
- Thirty-seven offline tests and reproducible outputs, including an independent tuple/sign audit and deterministic environment invariants.
- A state-changing artifact/manifest environment with two forced record-memory boundaries, optional costed early inspection, revisions, delayed obligations, a terminal verifier, and paired restoration of context and environment. Only scripted policies are implemented.
- A locally audited block-family derivation: attaining error 1/4 requires exactly 3k parent bits; with 2k parent bits the error is greater than 1/4 + 1/512 for every k. The proof allows joint encoding across blocks. The audit supplies an analytic entropy lemma and checks 4,096 oriented branch assignments independently. External proof review and novelty comparison remain open.
- A 320-configuration artifact/manifest development matrix and an explicit paired delayed-failure witness. In the 16 tight/cheap structured-policy cases, early inspection succeeds 16/16 versus 9/16 without it, costing 11 versus 10 synthetic action units. With ample initial memory, both succeed 16/16 and inspection adds cost. These are constructed scripted diagnostics, not independent trials or LLM gains.
- A separate leave-one-out generalization whose exact-memory lower bound grows, but whose excess error can vanish. This motivates distinguishing an exact-optimum obstruction from a robust error gap.
- A source-pinned survey of Codex, Pi, and OMP; supporting academic and official documentation review.
- A focused literature comparison covering source-coding actions, cascade access, functional compression, and a July 2026 compaction survey. The signature proof has an elementary complete-multipartite graph interpretation; a new general graph principle is not claimed. See the [positioning note](../research/LITERATURE_POSITIONING_2026-09-18.md).

## Not yet established

- Novelty and external validation of the locally audited scaling argument, or a practically large composition penalty.
- An exact optimum for the obstructed two-bit chain.
- Natural-language compiler performance, learned retirement accuracy, or closed-loop LLM-agent results.
- Cost or quality gains over native provider compaction.
- The internal training objective, prompt, or algorithm of a proprietary compaction service.

## Next bounded tasks

1. Complete an external review and novelty comparison of the scaling argument. The local audit found no block-proof defect, supplied an analytic entropy lemma, and corrected the leave-one-out domain to even n >= 4.
2. Assess and tighten the robust block-family gap. Investigate costed actions that reveal dependencies before a binding compaction, with explicit comparison to action-dependent side-information coding.
3. Draft the introduction, model, and finite-example sections using the claim register. These sections can progress before model experiments.
4. Design a small controlled LLM pilot after the information-access and reasoning-state controls are fixed. The proposed 36-run pilot is for debugging, not a powered benchmark.
5. Use the completed deterministic environment to specify a model adapter with isolated evaluator state and held-out task templates. A metered recovery condition, automatic witness minimization, and native-provider baselines remain unimplemented.

## Implementation refinement from September 18

The discussion of classifier-based deletion reinforces cache-aware timing, retention of failed attempts, and recoverable evidence. It adds a prominent experimental control: client-side history edits can invalidate provider-managed reasoning state. Compare supported native compaction with a clearly specified intervention; record reasoning continuity and all available memory channels. See [the protocol](EXPERIMENT_PROTOCOL.md).

## Working locations

- [Paper drafting](../paper/README.md)
- [Full proposal and proof](../research/LIVE_DEPENDENCY_RESEARCH_PROPOSAL_2026-09-16.md)
- [Creative directions, scaling derivations, and action-policy proposal](../research/CREATIVE_RESEARCH_DIRECTIONS_2026-09-18.md)
- [Local proof audit and remaining review boundaries](../research/PROOF_AUDIT_2026-09-18.md)
- [Prototype](../experiments/dependency_memory/README.md)
- [Deterministic environment and information contract](../experiments/dependency_memory/ARTIFACT_WORKFLOW.md)
- [Deterministic environment results](../experiments/dependency_memory/results/artifact_workflow_report.md)
- [Research map and cautions](RESEARCH_MAP.md)
- [Setup validation](../provenance/SETUP_VALIDATION.md)

The migration preserved the original source folder as a backup. `ContextResearch` is the working repository for this paper. No paid model runs were launched during setup.
