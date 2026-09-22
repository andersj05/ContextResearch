# Related-work map for drafting

These are distinctions to verify and explain, not declarations of novelty. The detailed review is in the September 16 proposal and survey. The focused bibliography records verified titles and authors; outstanding final publication metadata are identified in its notes.

The [September 22 feedback comparison](../research/FEEDBACK_PRIOR_ART_2026-09-22.md)
adds explicit cumulative-constraint and refinement precedents. Our new execution
adapter is a finite calibration; feedback alone, persistence of old failures and
finite candidate elimination are not novelty claims. The critical-field baseline
matches it in the tested family.

| Work | Connection | Distinction to maintain |
|---|---|---|
| Nagle et al. [@nagle2024] | Black-box prompt rate–distortion and query visibility | Our updater cannot reread the original source after the first bottleneck. |
| Equitz and Cover [@equitz1991] | Compatibility of successively refined descriptions | Their classical coding result is not automatically the theorem for this finite shrinking-memory query protocol. |
| Kaspi and Merhav [@kaspi2013] | Causal coding with side information | Timing and encoder/decoder access must match before importing a bound. |
| Nayak [@nayak1999] | Random-access memory lower bounds | The classical entropy argument is an established foundation, not the proposed contribution. |
| DeMem [@demem2026] | Decision-based distortion and memory partitions | The reviewed formal encoder uses H and Q; our first encoding precedes the realized future subset/query. Do not claim DeMem lacks memory theory. |
| HiAgent [@hiagent2025] | Subgoal working memory and subtask summaries | Hierarchical summarization is already an implemented method. |
| MemoBrain [@memobrain2026] | Dependency-aware trajectory memory, folding and flushing | A dependency graph plus completed-subtask folding is not sufficient for a new method claim. |
| The Compaction Cliff [@compactioncliff2026] | Typed retention and exact constraints under assumptions | Constraint pinning and strong structured baselines must be compared fairly. |
| TRACE [@trace2026] | Paired continuations with restored state | Immediate continuation checks may miss a corrupted delayed obligation; inspect verifier scope. |
| The Complexity Trap [@complexitytrap2025] | Observation masking versus summarization | Strong simple baselines can compete; results in its harness are not savings against current Codex. |
| ARC [@arc2026] | Active internal context revision | The reviewed method separates reflection from external action generation. The proposed extension selects actions for their effect on future memory needs. |
| Side-information vending machines [@vending2009] | Actions jointly affect source-coding rate, distortion, and cost | Section II and Theorem 1 statement reviewed. Acquiring information to improve compression is established; our hard record budgets differ from the asymptotic coding setting. |
| Cascade vending machines [@cascadevending2012] | Multistage coding with costed side information | Definitions II-A/III-A and Proposition 1 reviewed. Intermediate encoding from received messages and local side information is close prior art; an exact reduction remains open. |
| Sequential coding for computing [@caching2016] | Cache before requests, followed by request-dependent updates | Section II gives the update encoder both source and request; our updater cannot reread the source. |
| Graph coloring [@graphcoloring] | Functional descriptions and confusability | Our exact branch signature induces a complete multipartite graph; the general graph viewpoint is established. |
| Functional compression [@functionalcoloring2010] | Characteristic graphs, graph powers, and conditional coloring entropy | The reviewed manuscript's definitions cover the signature viewpoint; its asymptotic rate characterization does not directly give our hard state-count and intermediate one-bit restriction. |
| Information-cost direct sum [@jain2003compression] | Information requirements across independent copies, including joint encodings | The information superadditivity step is established. The local work must be identified in the branch-signature and excess-error lemmas. |
| Optimal one-way direct sum [@jain2008directsum] | Linear scaling for classical public-coin one-way relations and indexed-copy problems | Overall-output success and receiver access differ from our average single-query error after replacing the parent by one bit; no exact coefficient or error-gap transfer is established. |
| Fixed-length coding foundations [@polyanskiywu2016coding] | Entropy and rate-distortion achievability | The joint-coding extension applies established coding theorems to branch-decision words; vector-coding gains and entropy versus support-size distinctions are not new principles. |
| Strategy alphabets and dual objectives [@dupuis2004strategies; @polyanskiywu2016coding] | Encode potential responses to side information and certify a supporting rate-distortion objective | These are established methods; the candidate contribution is the particular all-decoder quantitative penalty and exact certificate. |
| Hypergraph functional coding [@basu2022hypergraph] | A cascade codec re-encodes its received message | The checked II-A4/V-B formulation does not include our late block/omission reveal and one-bit replacement before the final coordinate; a timing-preserving reduction remains open. |
| Compaction survey and benchmark proposal [@compactionview2026] | Repeated compaction, query timing, reversibility, and recovery | Broad overlap. Our proposed differentiator is a restricted compatibility result plus an exact, costed timing intervention. Priority is unresolved. |

See the [September 18 positioning note](../research/LITERATURE_POSITIONING_2026-09-18.md) for reviewed sections, information-access distinctions, and the remaining novelty boundary.

Additional leads from the proposal: [query-visibility audit](https://arxiv.org/abs/2607.11942), [online KV compaction](https://arxiv.org/html/2608.00902v1), [MemRefine](https://arxiv.org/html/2606.13177v1), [caching with fallible predictions](https://proceedings.mlr.press/v80/lykouris18a.html), and [approximate information states](https://jmlr.org/papers/v23/20-1165.html).

The [September 19 scaling check](../research/SCALING_LITERATURE_CHECK_2026-09-19.md) records the primary sections reviewed and sharpens the attribution: functional signatures and information direct-sum methods are established [@functionalcoloring2010; @jain2003compression; @jain2008directsum]. Describe the local result as a specific finite delayed-query separation using those methods, with priority of the construction and constants unresolved. The distinctive restriction to preserve in any reduction is that the child forms its one-bit replacement before learning the final coordinate. If the final decoder may retain the parent instead, two raw bits per block already attain error 1/4, so a lower bound for that relaxed access model cannot establish our strict excess.

Outstanding novelty work: determine whether prior results imply the particular four-bit construction, exact 3k attainment threshold, or uniform gap at 2k under this access contract. The joint-signature graph's complete-multipartite interpretation and information superadditivity are not open novelty claims. The [September 18 derivation](../research/CREATIVE_RESEARCH_DIRECTIONS_2026-09-18.md) and [September 19 exact computation](../research/EXACT_CHAIN_OPTIMUM_2026-09-19.md) remain local results awaiting external review and specific priority comparison. Retain counterexamples to attractive but overbroad entropy claims.

## Compaction audit direction, September 21

The [new primary-source comparison](../research/COMPACTION_AUDIT_PRIOR_ART_2026-09-21.md)
covers WiCER's diagnostic refinement [@wicer2026], TRACE's paired execution
verifier [@trace2026], and Context Codec's typed commitment checks
[@contextcodec2026]. The finite auditor instead certifies a budget obstruction
over an entire collision group under all declared adaptive recovery policies.
That restricted protocol is a candidate contribution, not established priority.

The recurrence uses ordinary information-state planning [@subramanian2022ais],
and grouping inputs by shared acceptable outcomes has direct hypergraph coding
precedents [@basu2022hypergraph]. The pairwise/triple example is elementary.
Natural-task extraction, exact channel equality, scaling and comparison with a
simple critical-field baseline are open; the implementation is not evidence of
a new general semantic theory or measured model improvement.
