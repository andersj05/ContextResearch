# Historical workflow memory replay

September 22, 2026. Offline and exploratory; zero new model calls.

Eight real attempt records supply counterfactual handoffs. The original transport failures were observed; their attribution to compaction was not.

## Concrete delayed obligation

Three final worker attempts dispatched and settled before their answers were lost. The fourth stopped before dispatch. All four say `transport_failure`. A later resumption plan must exclude the three dispatched cases and allow only the preflight case's first submission, subject to the separate full-study checks.

The original pure classifier and the saved continuation certificate agree on every selected record. Exact case IDs, request hashes and planning credit amounts remain bound together.

A local proposed plan that retries all four failed-status attempts contains three duplicate-dispatch IDs. Holding all four loses the one eligible first submission. Neither plan is executed against a provider; these are explicit failure witnesses for status-only rules.

## Two byte boundaries

Common initial observation: **53,736 UTF-8 bytes**, charged to every method. Untruncated status / fields / compact fields / receipts: **1116 / 2722 / 1649 / 1231 bytes**.

At 1,536 parent bytes, 768 child bytes, no archive, 16,384 additional cost units and 128 units per checker invocation:

| Method | Correct / 24 routes | Pre-recovery available | Mean actual cost | Checker calls / 24 |
|---|---:|---:|---:|---:|
| status | 0 | 0 | 57353.75 | 0 |
| fields | 10 | 10 | 58092.25 | 10 |
| compact_fields | 18 | 18 | 58271.50 | 18 |
| repair | 24 | 24 | 62471.12 | 384 |
| direct_receipts | 24 | 24 | 58731.12 | 192 |

The 24 routes enumerate delayed worker-pair and target reveals over the same eight records. They are not independent trials. All methods have the same total allowance; cheaper runs are not padded.

With whole-record archive recovery available, the first exact frontier threshold where repair completes every route is **62,501 total units** (8,765 above common input). At that same allowance the successful route counts are: status 3/24, fields 11/24, compact_fields 18/24, repair 24/24, direct_receipts 24/24. This is a descriptive threshold from the complete frontier, not a preregistered statistical comparison.

## Full resource comparison

The 180-contract grid varies both byte caps, allowance, checker price and archive access. Each cell has five methods and 24 routes. Counts below describe this constructed grid, not estimated prevalence.

| Comparator | Repair wins | Ties | Repair loses |
|---|---:|---:|---:|
| status | 27 | 136 | 17 |
| fields | 22 | 131 | 27 |
| compact_fields | 17 | 133 | 30 |
| direct_receipts | 0 | 147 | 33 |

The JSON includes all 45 exact allowance frontiers, including every method's completion-cost threshold, and actual spending on failed runs. The direct-receipt baseline has the same representation with less work; specific diagnosis is not needed once the rule is known.

## Receipt invalidation

A separate scope control binds checker revision, critical-field presence/values, case identity and actual request payload. Irrelevant latency/quota edits permit reuse. Relevant evidence, absent-to-present fields, identity, payload or checker changes invalidate it. These edits are constructed perturbations of historical records.

The cache check reads current evidence: its byte cost is explicit in the JSON. It does not claim free validation, and it is separate from the main immutable-record replay.

## Reproduce and interpret

```powershell
python -m experiments.dependency_memory.workflow_replay.run
python -m unittest discover -s experiments/dependency_memory/workflow_replay -t . -v
```

See [the frozen exploratory contract](../workflow_replay/CONTRACT.md) and [source-hashed results](workflow_replay_certificate.json). UTF-8 transfer, checker calls and tool calls have explicitly synthetic prices. CPU time, archive indexing/storage, tokens, cache changes and production billing are unmeasured. These results establish a replay capability and conditional budget improvements over weaker summaries, not a deployed-agent improvement or a novel feedback algorithm.
