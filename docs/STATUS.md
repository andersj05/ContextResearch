# Current research status

Updated: September 19, 2026. This document is the current handoff; older scope documents are historical.

## Objective

Develop a mathematically precise and implementable study of repeated agent compaction when relevance is revealed over time. The target is a restricted compatibility result plus controlled evidence of whether the mechanism matters in tool-agent tasks.

## Established in this repository

- A causal two-stage model: see all values, compress, learn a candidate subset, compress again, then learn the queried coordinate.
- Standard counting and random-access lower bounds, with explicit assumptions and attribution.
- A finite four-bit obstruction: with a random three-coordinate subset and a final one-bit memory, attaining 25% error requires at least three initial bits. Two initial bits cannot attain 25%, although each isolated bottleneck permits error at most 25%.
- An analytic eight-state lower bound, an exhaustive 256-assignment certificate, and an explicit three-bit witness graded on 192 cases.
- An [exact two-bit chain optimum of 9/32](../research/EXACT_CHAIN_OPTIMUM_2026-09-19.md), from complete enumeration of 171,798,901 four-cell parent partitions. There are 128 attaining partitions; the witness makes 54 errors on 192 outcomes. This sharpens the historical 49/192 lower bound and gives a one-block excess of 1/32 over the isolated later task.
- A deterministic record-retention diagnostic with revisions and observable retirement events: 810 configurations, deliberately constructed to expose plain LRU's weakness. This does not compare LLMs or native harnesses.
- Offline tests and reproducible outputs, including independent proof formulations, exact decision-tree checks, finite-chain decoder checks, pilot scheduling, and deterministic environment invariants. The [correctness audit](../research/CORRECTNESS_AUDIT_2026-09-19.md) reran the full native chain search and fixed witness-capacity and candidate-order validation gaps. Routine validation now regenerates all original diagnostic contents; `--exact-chain-compiler clang` additionally reruns the full search.
- A state-changing artifact/manifest environment with two forced record-memory boundaries, optional costed early inspection, revisions, delayed obligations, a terminal verifier, and paired restoration of context and environment. Scripted policies and the development fake-client interface are implemented; no model evaluation has run.
- A locally audited block-family derivation: attaining error 1/4 requires exactly 3k parent bits; with 2k parent bits the error is greater than 1/4 + 1/512 for every k. The proof allows joint encoding across blocks. The audit supplies an analytic entropy lemma and checks 4,096 oriented branch assignments independently. External proof review and novelty comparison remain open.
- A 320-configuration artifact/manifest development matrix and an explicit paired delayed-failure witness. In the 16 tight/cheap structured-policy cases, early inspection succeeds 16/16 versus 9/16 without it, costing 11 versus 10 synthetic action units. With ample initial memory, both succeed 16/16 and inspection adds cost. These are constructed scripted diagnostics, not independent trials or LLM gains.
- A separate leave-one-out generalization whose exact-memory lower bound grows, but whose excess error can vanish. This motivates distinguishing an exact-optimum obstruction from a robust error gap.
- A source-pinned survey of Codex, Pi, and OMP; supporting academic and official documentation review.
- A focused literature comparison covering source-coding actions, cascade access, functional compression, and a July 2026 compaction survey. The signature proof has an elementary complete-multipartite graph interpretation; a new general graph principle is not claimed. See the [positioning note](../research/LITERATURE_POSITIONING_2026-09-18.md).
- A metered late-recovery channel and an exact reference over uniform candidate/target routes for atomic-record selection. The [recovery results](../experiments/dependency_memory/results/recovery_frontier_report.md) include 2,640 scripted episodes and 3,000 exact configurations. Cheap recovery can dominate inspection; the public revision rule materially changes the break-even cost. This is a restricted record-selection reference, separate from the bit-chain optimum and from any LLM policy optimum.
- A short [living findings draft](../paper/findings-draft.md) and updated [manuscript](../paper/manuscript.md), with claim IDs and evidence links separating local mathematics, constructed diagnostics, and unperformed model work.
- A [two-stage pilot design](LLM_PILOT_SPEC.md) with an executable offline schedule and six exact calibration cells. It reserves 12 decision requests and 180 paired workflow episodes (432 requests maximum), with no model calls completed. The development renderer and requests now exist; provider isolation, accounting, and held-out renderers remain launch gates. The [source review](../research/PILOT_EVALUATION_REVIEW_2026-09-19.md) adds interactive evaluation and information-sufficient controls.
- Pilot v0.2 explicitly measures pre-recovery availability and completion cost: reliable scripted recovery makes even empty retention succeed. Fixed-policy comparisons on the reserved routes reveal two sample ties despite strict population preferences; family and route effects are confounded. These limits are now explicit, with no change to the reserved routes or spending ceiling.

The [development pilot implementation](DEVELOPMENT_PILOT.md) now passes fake-client controls for exact public requests, deletion, evaluator-label exclusion, budgets, and failure accounting. Optimal and forget-all controls each complete 36 development episodes in 96 fake requests; pre-recovery availability differs (26/36 versus 0/36). Existing ChatGPT sign-in is verified and GPT-5.6-Luna is selected, but the [transport review](../research/CODEX_SUBSCRIPTION_TRANSPORT_2026-09-19.md) leaves live dispatch blocked pending context/tool isolation, provider retry accounting, and generation/credit bounds. An [external review packet](../research/EXTERNAL_REVIEW_PACKET_2026-09-19.md) is prepared; nobody has been contacted.

## Not yet established


- Novelty and external validation of the locally audited scaling argument, or a practically large composition penalty.
- A matching exact error formula for arbitrary jointly encoded blocks; the one-block 1/32 excess does not replace the independently proved all-k bound.
- Natural-language compiler performance, learned retirement accuracy, or closed-loop LLM-agent results.
- Cost or quality gains over native provider compaction.
- The internal training objective, prompt, or algorithm of a proprietary compaction service.

## Next bounded tasks

1. Close the [Codex subscription transport gates](../research/CODEX_SUBSCRIPTION_TRANSPORT_2026-09-19.md): verify actual outbound context/tools, underlying retry counts, and generation/credit bounds. Existing ChatGPT sign-in is verified and GPT-5.6-Luna is selected. The [development interface and fake runner](DEVELOPMENT_PILOT.md) are complete; live execution remains disabled. The first tranche remains at most 96 requests; no API-key billing fallback is authorized.
2. Obtain external review of the exact finite search/reduction and block-family proof, and deepen the novelty comparison with functional compression/direct-sum results. The targeted literature comparison narrows the contribution but does not settle priority.
3. Complete and freeze the four held-out renderers before any held-out call. The tiny sample remains debugging evidence. Automatic witness minimization and native-provider baselines remain unimplemented.
4. Consider imperfect clues, unreliable recovery, and multiple obligations only as separately specified extensions. The current exact frontier should remain a calibration reference with its assumptions intact.
5. Update the living draft, manuscript, and claim register together when evidence changes. The conservative gap may be tightened later, but that is not required to test the cost-aware behavioral hypothesis.

## Implementation refinement from September 18

The discussion of classifier-based deletion reinforces cache-aware timing, retention of failed attempts, and recoverable evidence. It adds a prominent experimental control: client-side history edits can invalidate provider-managed reasoning state. Compare supported native compaction with a clearly specified intervention; record reasoning continuity and all available memory channels. See [the protocol](EXPERIMENT_PROTOCOL.md).

## Working locations

- [Paper drafting](../paper/README.md)
- [Short living findings draft](../paper/findings-draft.md)
- [Full proposal and proof](../research/LIVE_DEPENDENCY_RESEARCH_PROPOSAL_2026-09-16.md)
- [Creative directions, scaling derivations, and action-policy proposal](../research/CREATIVE_RESEARCH_DIRECTIONS_2026-09-18.md)
- [Local proof audit and remaining review boundaries](../research/PROOF_AUDIT_2026-09-18.md)
- [Exact four-bit chain computation](../research/EXACT_CHAIN_OPTIMUM_2026-09-19.md)
- [Prototype](../experiments/dependency_memory/README.md)
- [Deterministic environment and information contract](../experiments/dependency_memory/ARTIFACT_WORKFLOW.md)
- [Deterministic environment results](../experiments/dependency_memory/results/artifact_workflow_report.md)
- [Exact recovery comparison](../experiments/dependency_memory/results/recovery_frontier_report.md)
- [Research map and cautions](RESEARCH_MAP.md)
- [Setup validation](../provenance/SETUP_VALIDATION.md)

The migration preserved the original source folder as a backup. `ContextResearch` is the working repository for this paper. No paid model runs were launched during setup.
