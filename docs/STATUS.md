# Current research status

Updated: September 22, 2026. This document is the current handoff; older scope documents are historical.

## Objective

Develop a mathematically precise and implementable study of repeated agent compaction when relevance is revealed over time. The target is a restricted compatibility result plus controlled evidence of whether the mechanism matters in tool-agent tasks.

The September 21 user-directed pivot prioritizes a new mechanism: **auditing a memory collision before compaction and certifying the cheapest allowed recovery or required retained distinction**. Stop using tighter constants in the same example as the main research advance. The existing mathematics remains a calibration result.

The September 22 feedback-loop investigation now connects that auditor to the
existing executable workflow. It supports a bounded propose-audit-repair loop,
but the strong critical-field baseline matches its feasible contracts. Treat
this as calibration and a useful negative result, not a better-compactor claim.
The subsequent [strict novelty audit](../research/FEEDBACK_NOVELTY_AUDIT_2026-09-22.md)
also reformulates the finite optimizer as accepted-strategy selection and weak
hypergraph coloring. Close architectural precedents further narrow the claim.
No general feedback-algorithm novelty is established. Historical study evidence
is unchanged; the new checks are offline and use zero model calls.
Milestone validation: all 310 tests passed, the repository validator reported
PASS with no errors, and the paper built with 33 cited sources.

## Established in this repository

- **September 22 novelty conclusion:** the [C40 reduction](../research/FEEDBACK_NOVELTY_AUDIT_2026-09-22.md) exactly expresses finite recovery as an accepted-strategy relation and extra memory as weak coloring of minimal unsafe groups. Forward enumeration agrees on 7,203 subset/budget comparisons and 1,029 colorings in the existing 343-table domain; independent color assignment also matches all 12 existing fixtures. These are additional representations of established methods, not a new algorithm or new task samples. Self-GC and black-box checking supply closer architectural/formal-methods precedents. Useful extraction from realistic workflows and matched-cost benefit remain unperformed.

- **September 22 feedback milestone:** the [execution-graded feedback adapter](../research/FEEDBACK_BEFORE_FORGETTING_2026-09-22.md) enforces two record-memory boundaries, derives accepted actions through restored terminal execution, and accumulates independently checked unsafe-group constraints. In the main fixture it repairs 32/48 successes to 48/48 in three audits; last-only feedback cycles. Critical-field retention also attains 48/48 with one audit. Across 48 constructed contracts and five methods, accumulated feedback, enumeration and the strong baseline certify the same 18 contracts; last-only feedback cycles in 15. Claims C37-C38. Eighteen focused tests include 1,872 independent forward controller comparisons and a separate algebraic check of the capacity/recovery sweep. Zero model calls.
- **September 22 channel controls:** a one-record priority child fails where an early-target treatment succeeds; a distinct value-dependent record-identity code also succeeds using four states and a public two-value catalog. Ordinary receipt submission on that coded memory succeeds only 24/48, while its catalog decoder succeeds 48/48. Partial probes miss an untested obligation, and late true-value feedback supplies an additional conditional bit. Claim C39. These are constructed controls, not natural-task evidence or compression of arbitrary receipts. The [prior-art note](../research/FEEDBACK_PRIOR_ART_2026-09-22.md) rules out novelty for generic feedback, cumulative constraints and finite refinement.

- **Latest September 21 direction:** the [compaction collision auditor](../research/COMPACTION_COLLISION_AUDIT_2026-09-21.md) is executable. It handles whole groups with identical retained/public state, multiple correct terminal actions, deterministic adaptive recovery, separately checked lower proofs, and minimum additional-state repairs valid before the future task is known. Twelve constructed specifications include a pairwise-pass/triple-fail case, adaptive versus fixed recovery costs of two versus four, versioned-archive access, and negative controls. Forward controller enumeration independently checks all 343 three-world accepted-action tables (2,401 subset values). Claims C35-C36. No model calls; no further forced compaction during rescue, semantic prose-equivalence inference, native integration, natural-task gain, or certified publication novelty.

- **Earlier September 21 milestone:** a [decoder-complete certificate](../research/DECODER_COMPLETE_FRONTIER_2026-09-21.md) proves **0.2618989799 < lim_k D_k(2k) < 0.2618989801**. The lower inequality holds for every finite k. All 1,679,616 unordered decoder tables, including repeated and noncomplementary pairs, are covered by 4,751 disjoint orbits. Exact integer comparisons and outward rational logarithms support the converse for arbitrary joint encoders and block-dependent decoders. The upper bound is asymptotic coding from a rational channel; no finite code at that error is supplied. This raises the uniform guaranteed excess above 1/4 by more than sixfold. Claim C34; external correctness and publication novelty remain open. No model calls.

- **September 21 joint-coding milestone:** an explicit two-block, four-bit parent achieves error 283/1024, strictly below the one-block 9/32 optimum at the same two bits per block. All 6,144 outcomes are checked. Repeating pairs beats 9/32 for every k >= 2. This is an achievable construction, not the exact two-block optimum.
- A rational branch-decision test channel and standard coding achievability give limsup D_k(2k) <= 101/384 (about 26.30%). Its information is strictly below two bits, certified by an integer inequality. This is an analytic asymptotic bound, not a finite implemented encoder at that error.
- The same [joint-coding note](../research/JOINT_BLOCK_CODING_2026-09-21.md) proves the threshold for approaching error 1/4 is 4-(5/8)log2(5), about 2.5488 bits per block, including achievability with floor(k times that rate) bits. Exact finite attainment still needs 3k bits. The proof uses the existing signature lemma and established coding methods; external review and novelty remain open. No model requests were made in this phase.

- A causal two-stage model: see all values, compress, learn a candidate subset, compress again, then learn the queried coordinate.
- Standard counting and random-access lower bounds, with explicit assumptions and attribution.
- A finite four-bit obstruction: with a random three-coordinate subset and a final one-bit memory, attaining 25% error requires at least three initial bits. Two initial bits cannot attain 25%, although each isolated bottleneck permits error at most 25%.
- An analytic eight-state lower bound, an exhaustive 256-assignment certificate, and an explicit three-bit witness graded on 192 cases.
- An [exact two-bit chain optimum of 9/32](../research/EXACT_CHAIN_OPTIMUM_2026-09-19.md), from complete enumeration of 171,798,901 four-cell parent partitions. There are 128 attaining partitions; the witness makes 54 errors on 192 outcomes. This sharpens the historical 49/192 lower bound and gives a one-block excess of 1/32 over the isolated later task.
- A deterministic record-retention diagnostic with revisions and observable retirement events: 810 configurations, deliberately constructed to expose plain LRU's weakness. This does not compare LLMs or native harnesses.
- Offline tests and reproducible outputs, including independent proof formulations, exact decision-tree checks, finite-chain decoder checks, pilot scheduling, and deterministic environment invariants. The [correctness audit](../research/CORRECTNESS_AUDIT_2026-09-19.md) reran the full native chain search and fixed witness-capacity and candidate-order validation gaps. Routine validation now regenerates all original diagnostic contents; `--exact-chain-compiler clang` additionally reruns the full search.
- A state-changing artifact/manifest environment with two forced record-memory boundaries, optional costed early inspection, revisions, delayed obligations, a terminal verifier, and paired restoration of context and environment. Scripted policies, fake controls, a Luna development tranche, and separate revision/retention diagnostics are implemented and recorded below.
- A locally audited block-family derivation: attaining error 1/4 requires exactly 3k parent bits; with 2k parent bits the error is greater than 1/4 + 1/512 for every k. The proof allows joint encoding across blocks. The audit supplies an analytic entropy lemma and checks 4,096 oriented branch assignments independently. External proof review and novelty comparison remain open.
- A 320-configuration artifact/manifest development matrix and an explicit paired delayed-failure witness. In the 16 tight/cheap structured-policy cases, early inspection succeeds 16/16 versus 9/16 without it, costing 11 versus 10 synthetic action units. With ample initial memory, both succeed 16/16 and inspection adds cost. These are constructed scripted diagnostics, not independent trials or LLM gains.
- A separate leave-one-out generalization whose exact-memory lower bound grows, but whose excess error can vanish. This motivates distinguishing an exact-optimum obstruction from a robust error gap.
- A source-pinned survey of Codex, Pi, and OMP; supporting academic and official documentation review.
- A focused literature comparison covering source-coding actions, cascade access, functional compression, and a July 2026 compaction survey. The signature proof has an elementary complete-multipartite graph interpretation; a new general graph principle is not claimed. See the [positioning note](../research/LITERATURE_POSITIONING_2026-09-18.md).
- A metered late-recovery channel and an exact reference over uniform candidate/target routes for atomic-record selection. The [recovery results](../experiments/dependency_memory/results/recovery_frontier_report.md) include 2,640 scripted episodes and 3,000 exact configurations. Cheap recovery can dominate inspection; the public revision rule materially changes the break-even cost. This is a restricted record-selection reference, separate from the bit-chain optimum and from any LLM policy optimum.
- A short [living findings draft](../paper/findings-draft.md) and updated [manuscript](../paper/manuscript.md), with claim IDs and evidence links separating local mathematics, constructed diagnostics, completed model development observations, and unperformed extensions.
- A [two-stage pilot design](LLM_PILOT_SPEC.md) with an executable offline schedule and six exact calibration cells. The historical full schedule reserves 432 requests; only its 96-request development tranche has run under the [amended transport contract](LUNA_DEVELOPMENT_RUN.md). The four held-out clue renderers now have an [offline semantic checkpoint](HELDOUT_RENDERERS.md), covering 120 forms and 240 pair/target checks; provider integration and held-out launch remain unfinished. These are software checks, not model trials. The [source review](../research/PILOT_EVALUATION_REVIEW_2026-09-19.md) adds interactive evaluation and information-sufficient controls.
- Pilot v0.2 explicitly measures pre-recovery availability and completion cost: reliable scripted recovery makes even empty retention succeed. Fixed-policy comparisons on the reserved routes reveal two sample ties despite strict population preferences; family and route effects are confounded. These limits are now explicit, with no change to the reserved routes or spending ceiling.

The [Luna development run](../experiments/dependency_memory/results/luna_development_2026-09-19/report.md) completed **96/96 valid requests**, with no transport or schema failures, using the existing ChatGPT subscription, low reasoning effort, and the mutable `gpt-5.6-luna` alias. Stage A selected the exact lower-cost action in 10/12 decisions; the two disagreements involved revisions. Stage B completed 36/36 episodes, with required evidence available before recovery in 21/36 and recovery needed in 15. Never/always/model-selected inspection had availability 3/12, 10/12, and 8/12 and synthetic total costs 154, 140, and 137. These descriptive totals reuse one route and do not establish superiority or population effects.

Reported usage was 276,048 input and 27,140 output tokens (reasoning included in output). Conservative planning usage was **2.5395 credit equivalents**, within the 20-equivalent cap; actual experiment-attributable subscription debit is unknown. No API billing, credit purchase, reset redemption, repair request, or held-out call was used. The launch code was frozen in `d22d9df`; the saved manifest fingerprints code, model catalog, client, settings, and instructions. See the [findings note](../research/LUNA_DEVELOPMENT_FINDINGS_2026-09-19.md) for checks and limitations. Fixed task-independent instructions and three wrappers were declared; this is not a native-harness comparison or a certification of remote internals.

The [offline controls](DEVELOPMENT_PILOT.md) remain separate evidence: optimal and forget-all selectors each complete 36 episodes with availability 26/36 and 0/36. An [external review packet](../research/EXTERNAL_REVIEW_PACKET_2026-09-19.md) is prepared; nobody has been contacted.

The [revision-aware offline grading](../experiments/dependency_memory/results/revision_analysis_report.md) is complete. Seventeen saved parent choices are graded over all 30 unrevealed routes, while 19 are conditioned on their already visible pair. Exactly three parents have strict deficits, all in uninspected revision conditions; the remaining 33 attain the same-view reference. All 36 observed child choices are conditionally optimal. This reuses the first run and makes zero new model calls.

A further local prelaunch review corrected two prospective accounting/failure defects: unknown optional cache-write usage remains unknown inside budget metadata, and a complete metered but malformed answer is a policy failure that does not halt later cases. Genuine transport or usage uncertainty still stops the tranche. Offline regressions and the saved-evidence auditor cover these paths; the original 96 answers, costs, and public diagnostic requests remain unchanged.

The separately authorized [revision diagnostic](../research/REVISION_LUNA_FINDINGS_2026-09-19.md) then completed **24/24 valid requests** with no failures. All selected pairs are optimal: refresh-first selects `job-4/job-5` in 8/8, refresh-last selects `job-0/job-1` in 8/8, and no-refresh selects the same low pair in 8/8 (all full pairs tie there). All eight matched directional shifts equal eight. This is observed rule-sensitive behavior in the simplified, optimal-child-guaranteed task, not proof that the first workflow errors were fixed. Usage is 66,200 input and 5,651 output tokens, or **0.58328 conservative credit equivalents** under the separate 12-equivalent cap; attributable subscription debit is unknown. The saved-evidence audit passes. Those two completed allocations account for 120 model requests, with no held-out requests, API billing, purchases, or resets.

The [matched transfer study](../research/TRANSFER_LUNA_FINDINGS_2026-09-19.md) is complete at its fixed **1,536 unique model requests across 32 blocks and 48 conditions**. The [pooled report](../experiments/dependency_memory/results/transfer_luna_2026-09-19_continuation/report.md) records **1,533 valid selections, 1,422 optimal**, and three missing answers from fully metered transport failures in the original phase. None of those missing answers belongs to the primary comparison. There were no other transport failures among dispatched requests, policy failures, or incomplete cases. Refresh-present cells have 912 optimal selections among 1,022 valid answers; no-refresh cells have 510 among 511. The sole no-refresh deficit is a valid empty selection; all full two-record selections tie there. There are 111 strict deficits overall, including that one underfill.

All **128 primary matched pairs in 32 blocks** are complete. In workflow/unspecified/refresh-present cells, generic guidance yields 114/128 optimal selections and prospective guidance 118/128. Paired regret favors prospective guidance in 13 pairs, generic guidance in nine, and ties in 106. The prespecified mean normalized regret benefit is **107/5120 (0.02090)**, with a descriptive 95% block-bootstrap interval **[-0.0203125, 0.060546875]** that includes zero: **no confirmed improvement**. Raw regret benefit is -7/1920 for six jobs and 71/8448 for twelve jobs. These results do not establish prospective advice alone as a solution. The child capacity was nonbinding and the later selector was not run, so this remains an isolated early-retention study, not evidence of repeated-compaction or natural-task gains.

The [independent final audit](../experiments/dependency_memory/results/transfer_luna_2026-09-19_continuation/independent_audit.json) passes, including request identity, independent route grading, cumulative accounting, and source hashes against frozen Git blobs. The zero-generation `999f14d` launch remains preserved; source `0414198` dispatched 888 requests, retaining 885 answers and the three permanent failures. The [separate continuation](TRANSFER_CONTINUATION.md), frozen at `f9012a2`, completed only the 648 never-dispatched cases with no failures. The failed zero-generation preparation at `cfa1ba9` and its correction remain documented in the [decision record](DECISIONS.md). Across saved phases there were 1,541 host attempts and no repeated model request. Public inputs, schedule, scoring, and analysis stayed fixed; the historical first-eight-block checkpoint was not used to change them.

Total usage was **4,768,512 input tokens** (including 2,412,032 cached) and **632,736 output tokens** (including 595,880 reasoning tokens). Conservative planning cost was **48.78528000 credit equivalents**, including 20.52866750 in the continuation, within the 200-equivalent cap; uncertain reservations are zero and attributable subscription debit remains unknown. The continuation used the existing-subscription route under the declared credit-backed quota policy, with no API billing, purchases, resets, repair requests, or held-out calls. The [descriptive findings summary](../experiments/dependency_memory/results/transfer_luna_2026-09-19_continuation/findings_summary.json) preserves all condition counts and overlapping error-pattern labels; those labels do not identify internal mechanisms. The earlier 120 model requests remain separate historical allocations.

## Not yet established

- Novelty and external validation of the locally audited scaling argument, or a practically large composition penalty.
- A closed-form error formula or full rate-distortion curve for arbitrary jointly encoded blocks. The limiting rate-two error is now certified within (0.2618989799, 0.2618989801); the exact two-block optimum and efficient finite codes remain open.
- Natural-language compiler performance, learned retirement accuracy, or unrestricted closed-loop LLM-agent results. The completed model work covers only isolated inspection and atomic-record selection.
- Cost or quality gains over native provider compaction.
- The internal training objective, prompt, or algorithm of a proprietary compaction service.

## Next bounded tasks

The constructed execution adapter is complete; arbitrary natural-task extraction
is not. The next bounded task is to prepare pinned local task snapshots with
opaque payloads, executable obligations and a declared information contract,
where the retention rule must be inferred rather than supplied directly. Use the
[feedback research protocol](FEEDBACK_RESEARCH_PROTOCOL.md): equally informed
critical-field retention, generic revision, last-only and accumulated diagnosis,
two binding memory limits, and full resource accounting. Freeze development and
evaluation continuations before optimizing the policy. No new live launch is
specified; model revision, sample size, seeds, transport and spend cap remain
unfilled. The present strong-baseline tie is a reason to downgrade practical
superiority, not to scale up repetitions of the same fixture. Exact semantic
collisions, tractable sound verification, native integration and novelty remain
open. General generated continuation search remains unimplemented. The strict
novelty audit adds concrete gates: replayable evidence extraction, correct reuse
and invalidation of prior checks, and a matched-cost comparison or useful audit
decisions beyond strong simple retention. These are candidate engineering
contributions, not a new verification principle.

The decoder-complete phase resolved the rate-two interval to 2e-10. Further decimal tightening is deprioritized. External correctness/priority review remains useful, while the earlier behavioral tasks below remain separately specified follow-ups rather than a request to reuse completed launch allocations.

1. Specify and validate offline a follow-up with a binding downstream memory boundary and a declared later-selector policy. Preserve exact calibration, missing outcomes, and channel accounting; the completed [transfer study](TRANSFER_STUDY.md) does not test this setting. Prepare a separately versioned contract and bounded allocation before any new model launch; this next task does not automatically start model calls.
2. Obtain external review of the exact finite search/reduction and block-family proof, and deepen the novelty comparison with functional compression/direct-sum results. The targeted literature comparison narrows the contribution but does not settle priority.
3. Integrate the four [implemented held-out clue renderers](HELDOUT_RENDERERS.md) into a versioned request/runner contract, validate information deletion and controls, and freeze the complete launch before any held-out call. A more naturalistic workflow remains an unperformed extension, and the tiny reserved sample remains debugging evidence. General executable-continuation minimization and native-provider baselines remain unimplemented; the new finite auditor minimizes world subsets and selects among declared traces only.
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
