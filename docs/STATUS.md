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
- Seventeen offline tests and reproducible committed outputs.
- A source-pinned survey of Codex, Pi, and OMP; supporting academic and official documentation review.

## Not yet established

- Novelty of a general theorem, or a scaling law for a nontrivial dependency family.
- An exact optimum for the obstructed two-bit chain.
- Natural-language compiler performance, learned retirement accuracy, or closed-loop agent results.
- Cost or quality gains over native provider compaction.
- The internal training objective, prompt, or algorithm of a proprietary compaction service.

## Next bounded tasks

1. Audit the finite proof and compare its exact formulation with functional compression, causal source coding, and successive refinement.
2. Select one family of dependency subsets and seek a compatibility bound or construction that scales.
3. Draft the introduction, model, and finite-example sections using the claim register. These sections can progress before model experiments.
4. Design a small controlled LLM pilot after the information-access and reasoning-state controls are fixed. The proposed 36-run pilot is for debugging, not a powered benchmark.
5. Extend to one state-changing environment with a deterministic delayed terminal verifier if the pilot identifies a useful effect.

## Implementation refinement from September 18

The discussion of classifier-based deletion reinforces cache-aware timing, retention of failed attempts, and recoverable evidence. It adds a prominent experimental control: client-side history edits can invalidate provider-managed reasoning state. Compare supported native compaction with a clearly specified intervention; record reasoning continuity and all available memory channels. See [the protocol](EXPERIMENT_PROTOCOL.md).

## Working locations

- [Paper drafting](../paper/README.md)
- [Full proposal and proof](../research/LIVE_DEPENDENCY_RESEARCH_PROPOSAL_2026-09-16.md)
- [Prototype](../experiments/dependency_memory/README.md)
- [Research map and cautions](RESEARCH_MAP.md)
- [Setup validation](../provenance/SETUP_VALIDATION.md)

The migration preserved the original source folder as a backup. `ContextResearch` is the working repository for this paper. No paid model runs were launched during setup.
