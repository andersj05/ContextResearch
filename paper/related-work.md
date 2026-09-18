# Related-work map for drafting

These are distinctions to verify and explain, not declarations of novelty. The detailed review is in the September 16 proposal and survey. The focused bibliography records verified titles and authors; outstanding final publication metadata are identified in its notes.

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
| Compaction survey and benchmark proposal [@compactionview2026] | Repeated compaction, query timing, reversibility, and recovery | Broad overlap. Our proposed differentiator is a restricted compatibility result plus an exact, costed timing intervention. Priority is unresolved. |

See the [September 18 positioning note](../research/LITERATURE_POSITIONING_2026-09-18.md) for reviewed sections, information-access distinctions, and the remaining novelty boundary.

Additional leads from the proposal: [query-visibility audit](https://arxiv.org/abs/2607.11942), [online KV compaction](https://arxiv.org/html/2608.00902v1), [MemRefine](https://arxiv.org/html/2606.13177v1), [caching with fallible predictions](https://proceedings.mlr.press/v80/lykouris18a.html), and [approximate information states](https://jmlr.org/papers/v23/20-1165.html).

Outstanding novelty work: review functional compression and characteristic/confusability graph formulations; determine whether the proposed joint-signature characterization is already an immediate special case; compare the new block-family scaling argument with direct-sum and coding results. The [September 18 derivation](../research/CREATIVE_RESEARCH_DIRECTIONS_2026-09-18.md) is a local mathematical result awaiting independent review and novelty comparison. Retain counterexamples to attractive but overbroad entropy claims.
