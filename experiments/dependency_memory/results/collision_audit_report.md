# Compaction collision audit: constructed results

September 21, 2026. No model calls. Costs are synthetic recovery units.

The auditor searches entire groups of histories with identical retained and public
channels. It returns an optimal adaptive recovery policy and a separately checked
obstruction below that cost. A repair label is chosen before the future task is known.

| Specification | Budget | Worst recovery cost | Extra retained states | Extra fixed bits |
|---|---:|---:|---:|---:|
| three_way_compatibility | 0 | 1 | 2 | 1 |
| rollback_with_archive | 2 | 3 | 2 | 1 |
| rollback_archive_expired | 2 | impossible | 2 | 1 |
| adaptive_sharded_recovery | 1 | 2 | 2 | 1 |
| harmless_lost_detail | 0 | 0 | 1 | 0 |
| public_evidence_control | 2 | 0 | 1 | 0 |
| affordable_archive_control | 3 | 3 | 1 | 0 |
| adaptive_recovery_budget_two | 2 | 2 | 1 | 0 |
| binary_receipt_budget_0 | 0 | 3 | 8 | 3 |
| binary_receipt_budget_1 | 1 | 3 | 4 | 2 |
| binary_receipt_budget_2 | 2 | 3 | 2 | 1 |
| binary_receipt_budget_3 | 3 | 3 | 1 | 0 |

## Checkable counterexample

Three histories permit builds {A,B}, {B,C}, and {A,C}. All share the same retained
summary and public state. Each of the three pairs admits a shared build, so every
pair passes a zero-recovery feasibility check. The whole group has no shared build.
One recovery unit resolves it; with zero units, two retained message states suffice
and one does not. This is an elementary set-intersection example, not a new theorem.

## Adaptive tools change the diagnosis

The eight-world sharded archive takes two recovery units adaptively (directory, then
the indicated shard). Any fixed batch of queries costs at least four. A one-bit
pre-compaction codebook repair permits recovery within one unit. That bit describes
a finite partition, not an LLM token or a measured natural-language summary improvement.

## Revisions and negative controls

Reading the latest workspace cannot recover an overwritten original receipt. A
versioned archive rescues it at three units; without that archive, this fixture is
unrecoverable. The late rollback trace is selected from the declared catalog, not
synthesized from arbitrary program executions. Free public evidence, a common valid
answer, and adequate recovery budgets each remove the need for extra retained states.

## Scope

All results are exact only for the supplied finite worlds, terminal accepted-action
sets, deterministic read-only tools, and positive integer recovery prices. The full
model is known; world identity is hidden from the controller. Tool outputs remain
available during recovery. There is no second forced compaction, stochastic tool,
side effect, semantic summary-equivalence inference, native-agent integration, or
empirical performance claim. Worst-case zero-error guarantees are deliberately
stronger than average task success. The codebook is not a practical compressor.

Reproduce with python -m experiments.dependency_memory.collision_audit.run.

[Research note](../../../research/COMPACTION_COLLISION_AUDIT_2026-09-21.md).
