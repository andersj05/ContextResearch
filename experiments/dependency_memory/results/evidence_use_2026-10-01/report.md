# Retained evidence and final decision audit

October 1, 2026. Post-hoc offline replay; zero new model calls.

368 scheduled finals: 319 observed, 3 transport gaps and 46 never dispatched.
Pooled counts reconcile the ledger; these are correlated observations, not independent trials.

| Study / arm | Raw correct / observed | Wrong contradicted | Wrong consistent | Wrong uncheckable | Correct contradicted / uncheckable | Derived correct / available |
|---|---:|---:|---:|---:|---:|---:|
| cross_record / automatic | 29/36 | 7 | 0 | 0 | 0 / 0 | 36/36 |
| cross_record / checked | 18/36 | 1 | 0 | 17 | 0 / 1 | 18/18 |
| cross_record / direct | 32/36 | 4 | 0 | 0 | 0 / 0 | 36/36 |
| cross_record / full | 30/36 | 6 | 0 | 0 | 0 / 0 | 36/36 |
| cross_record / indexed_projected | 29/35 | 6 | 0 | 0 | 0 / 0 | 35/35 |
| cross_record / indexed_raw | 35/36 | 1 | 0 | 0 | 0 / 0 | 36/36 |
| cross_record / prompt | 33/36 | 0 | 0 | 3 | 0 / 33 | 0/0 |
| cross_record / structured | 30/36 | 6 | 0 | 0 | 0 / 0 | 35/36 |
| workflow_executed / checked | 2/2 | 0 | 0 | 0 | 0 / 0 | 2/2 |
| workflow_executed / direct | 2/3 | 1 | 0 | 0 | 0 / 0 | 3/3 |
| workflow_executed / full | 2/2 | 0 | 0 | 0 | 0 / 0 | 2/2 |
| workflow_executed / indexed | 3/3 | 0 | 0 | 0 | 0 / 0 | 3/3 |
| workflow_executed / prose | 2/2 | 0 | 0 | 0 | 0 / 2 | 0/0 |
| workflow_live / checked | 4/4 | 0 | 0 | 0 | 0 / 0 | 4/4 |
| workflow_live / direct | 4/4 | 0 | 0 | 0 | 0 / 0 | 4/4 |
| workflow_live / full | 4/4 | 0 | 0 | 0 | 0 / 0 | 4/4 |
| workflow_live / indexed | 4/4 | 0 | 0 | 0 | 0 / 0 | 4/4 |
| workflow_live / prose | 3/4 | 0 | 0 | 1 | 0 / 3 | 0/0 |

Failure classes:

- empty_terminal_memory: 17
- retained_readout_disagrees_with_full_ledger: 1
- reviewed_retained_obligation_misused: 1
- uncheckable_representation: 3
- wrong_proposal_despite_matching_retained_readout: 31

The actor-side check reads only admitted memory and the already public rule/state. Full ledgers and intermediate memories are evaluator-only. The three outcomes are consistency, contradiction and uncheckable representation.

A contradicted answer can be vetoed, but no repair call or new execution occurs. A consistent answer can still be wrong if memory omitted or changed evidence. Correct prose answers can become uncheckable under this typed parser; that abstention cost must be reported. No overall guard or compression gain is inferred.

The single reviewed prose obligation preserves a repository success which the final answer omits. That bounded human reading does not give the actor an automatic prose decoder.

The associated tests include a same-memory/different-history omission witness: a later failed run can be absent from retained memory without changing any guard input. The guard therefore cannot authenticate completeness. Explicit provenance/coverage would be additional state to budget and validate prospectively.

The JSON includes every identity, original answer, diagnostic, input hashes, missing disposition and counterfactual readout. Historical primary outcomes and costs remain unchanged. Batched local measurements are saved separately and are not priced.
