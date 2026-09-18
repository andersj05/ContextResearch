# Related-work map for drafting

These are distinctions to verify and explain, not declarations of novelty. The detailed review is in the September 16 proposal and survey. Bibliography entries with abbreviated titles or missing authors are explicitly marked as incomplete.

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

Additional leads from the proposal: [query-visibility audit](https://arxiv.org/abs/2607.11942), [online KV compaction](https://arxiv.org/html/2608.00902v1), [MemRefine](https://arxiv.org/html/2606.13177v1), [caching with fallible predictions](https://proceedings.mlr.press/v80/lykouris18a.html), and [approximate information states](https://jmlr.org/papers/v23/20-1165.html).

Outstanding novelty work: review functional compression and characteristic/confusability graph formulations; determine whether the proposed joint-signature characterization is already an immediate special case; identify a structural family whose result adds something beyond the finite illustration. Retain counterexamples to attractive but overbroad entropy claims.
