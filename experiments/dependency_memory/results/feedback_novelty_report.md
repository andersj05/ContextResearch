# Novelty audit: finite representation checks

September 22, 2026. Elementary reductions, not a new algorithm or model experiment.

A recovery policy can be treated as an output symbol. A group is safe when
some budget-bounded policy is valid in every member. Minimal unsafe groups
form forbidden hyperedges; memory labels are a weak coloring of those edges.

Forward enumeration checks 343 accepted-action tables
at budgets [0, 1, 2]: 7,203 nonempty
subset/budget checks and 1,029 repair-coloring checks.
Distinct policy output vectors at these budgets: [3, 15, 27].

These reuse the September 21 three-world domain, extending its independent
checks to the strategy and forbidden-hyperedge representations. They are not
new independent tasks or additional model trials.

| Existing fixture | Budget | Minimum repair states | Minimal unsafe groups |
|---|---:|---:|---:|
| three_way_compatibility | 0 | 2 | 1 |
| rollback_with_archive | 2 | 2 | 1 |
| rollback_archive_expired | 2 | 2 | 1 |
| adaptive_sharded_recovery | 1 | 2 | 54 |
| harmless_lost_detail | 0 | 1 | 0 |
| public_evidence_control | 2 | 1 | 0 |
| affordable_archive_control | 3 | 1 | 0 |
| adaptive_recovery_budget_two | 2 | 1 | 0 |
| binary_receipt_budget_0 | 0 | 8 | 28 |
| binary_receipt_budget_1 | 1 | 4 | 56 |
| binary_receipt_budget_2 | 2 | 2 | 32 |
| binary_receipt_budget_3 | 3 | 1 | 0 |

The fixture checks derive feasibility from the existing recovery DP, then
compare an independent color-assignment search with its repair partition DP.
Only the three-world check also derives feasibility by forward policy enumeration.

For the pairwise-compatible triple, the single forbidden edge is the entire
triple. Two colors suffice. Replacing that edge by all pair conflicts would
incorrectly demand three colors; retaining only genuinely unsafe pairs would
incorrectly allow one. Higher-order compatibility matters, but is established
hypergraph structure rather than a new information principle.

Scope: finite public models, deterministic read-only tools, positive integer
costs, worst-case zero error, exact retained/public equality, and no additional
memory boundary during recovery. Fixed state labels exclude shared codebook size
and are not token or byte budgets. No source-coding rate theorem is imported.

[Novelty verdict and derivation](../../../research/FEEDBACK_NOVELTY_AUDIT_2026-09-22.md).
