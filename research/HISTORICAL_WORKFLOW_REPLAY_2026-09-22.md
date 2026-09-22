# Concrete delayed handoff failures from a real workflow

September 22, 2026. Exploratory offline replay, claims C41-C43. No new model
requests. [Executable contract](../experiments/dependency_memory/workflow_replay/CONTRACT.md),
[results](../experiments/dependency_memory/results/workflow_replay_report.md),
and [source-hashed certificate](../experiments/dependency_memory/results/workflow_replay_certificate.json).

## What was found

The completed transfer workflow contains a consequential distinction that a
short `failed` summary loses. The last attempt in each of four workers has status
`transport_failure`. Three requests had already generated and settled charges;
their answers were lost at the post-generation quota guard. The fourth stopped
before dispatch. These are observed historical events from generation source
commit `04141984d56fa0f80429d19dc45f589fef8ac5a6`, preserved in the
[continuation record](../docs/TRANSFER_CONTINUATION.md).

For the three dispatched cases, a later "retry failed work" plan would repeat
already generated cases. Holding every failed case would instead lose the
preflight case's eligible first submission. A correct handoff must also retain
the exact request identity and settled/reserved planning amounts, so that a
later budget calculation does not renew a spent allocation or erase uncertainty.
The new local witness executes these two proposed ID-list policies against the
original classifier: three duplicate-dispatch IDs versus one missed eligible ID.
It sends neither plan to a provider.

This is **not evidence that compaction caused the historical failures**. The
records and dispatch distinctions are real; deleting memory and imposing delayed
queries are new counterfactual interventions. Exact case IDs differ, so grouping
by status is also not an unrestricted information-theoretic impossibility proof.

## Evidence extraction and the two handoffs

Selection is the last two attempts from each worker, including four completed
controls and four failures. The eight records were inspected during development;
there is no held-out claim. Source files, array positions, canonical record hashes,
request hashes and the historical source commit remain identifiable. No raw logs
are copied into new tracked artifacts.

The original `classify_attempt` and `exact` function bodies in
[the continuation preparer](../scripts/prepare_transfer_continuation.py) are
compiled from their pinned AST nodes, without executing imports or top-level
code. Their outputs agree with the separately saved continuation certificate.
The new adapter is independently implemented and checked against those original
semantics on all eight records and 1,388 adversarial input configurations.

All methods first receive the same 53,736-byte canonical observation. After the
first byte-limited deletion, the public task reveals two worker numbers. After
the second, smaller deletion, it reveals one case ID among those workers. Six
worker pairs and four targets per pair give 24 routes over the same eight records.
Only serialized memory, public reveals and declared costed archive access reach
the continuation. The imposed routing and byte limits are designed diagnostics,
not observations of the original agent's workload distribution.

Memory counts identifiers, schema tags, masks, amounts, ordering and wrappers.
There is no binary receipt catalog. A lossless named-field projection takes 2,722
bytes for all records; an efficient fixed-schema encoding takes 1,649. Checked
decision receipts take 1,231. The latter store the task-relevant result rather
than every input to the public rule; they are not a general-purpose substitute
for the original evidence.

## Conditional improvement at matched resource limits

The replay prices one transferred UTF-8 byte at one unit, a tool invocation at
128 units, and a predicate/projection invocation at 0, 128 or 1,024 units. It
charges the initial observation, candidate writes and reads, the diagnosis
packet, both memory boundaries, public reveals, recovery, final output, and
completed work on unsuccessful routes. Costs are from the selected handoff;
historical model spending is outside this new replay. CPU time, archive storage
and indexing, tokenization and provider cache/billing effects are unmeasured.
These are **synthetic replay prices, not production total costs**.

With parent/child caps of 1,536/768 bytes, no archive, 128 units per check and a
common total allowance of 70,120 units:

| Memory method | Successful routes | Mean actual cost |
|---|---:|---:|
| Status summary | 0/24 | 57,353.75 |
| Named critical fields | 10/24 | 58,092.25 |
| Compact critical fields | 18/24 | 58,271.50 |
| Diagnose and repair | 24/24 | 62,471.12 |
| Direct checked receipts | 24/24 | 58,731.12 |

Whole-record recovery does not automatically remove the budget effect. On the
complete allowance frontier at the same caps and checker price, the first
threshold at which repair finishes all routes is **62,501 total units**, including
53,736 common input units. At that allowance, status succeeds on 3 routes, named
fields on 11, compact fields on 18, and both receipt methods on all 24. This is an
exact descriptive threshold selected from the complete frontier, not a
preregistered statistical test. Direct receipts already finish all 24 at 58,761
units, making them the stronger treatment to pursue.

Across 180 constructed resource contracts, repair beats compact fields in 17,
ties in 133 and loses in 30. It never beats direct receipts: 147 ties and 33
losses. Cheap projected retrieval and expensive up-front checks can reverse the
preference. All 45 exact allowance frontiers are retained, including unfavorable
regions. These cells are not independent evidence of prevalence or significance.

## Another delayed failure: losing the scope of a check

A checked result can itself become stale. Eleven separate controls compare
reuse after edits to historical records. The unchanged record and irrelevant
latency/quota edits permit reuse. A changed settlement, invalid reservation
ticket, previously absent usage or turn ID, changed case/request identity,
edited payload, or changed checker revision invalidates the receipt. Four of
these perturbations make a naive unscoped cached classification/accounting result
wrong; identity/version controls also reject reuse without relying on a changed
classification label.

The scope stamp includes the exact dependency projection, field presence,
case/request identity, actual request bytes and checker revision. Its check
reads and hashes current evidence; the source bytes and receipt size are reported.
It is not a free invalidation oracle. These are explicit synthetic perturbations,
separate from the immutable-artifact main replay. Trusted Python interfaces and
scope checks do not provide adversarial process isolation or cryptographic
authenticity of externally supplied data.

## Research decision

This completes one extraction-and-replay milestone beyond the small public-token
fixture. It supplies concrete failure plans, opaque real payloads, executable
obligations, two byte boundaries and a fully specified conditional cost frontier.
It does not establish automatic rule inference, a natural-task population effect,
compaction causality, native-harness superiority or measured monetary savings.

The useful repair here is the cheap direct checked receipt. The known public
rule makes iterative diagnosis redundant. Prefer that mechanism for the next
test, with scoped invalidation and an indexed archive as an equally informed
baseline. Freeze a different workflow's obligation structure and grader before
developing its extractor; do not call another sample of this inspected resume
workflow held-out transfer. A live run still needs a new model revision,
isolation contract, request ceiling and explicit spending allocation.

## Validation

All 326 repository tests pass, including 16 focused replay tests. The full offline
validator passes with no errors, regenerating the 180 contracts and 45 frontiers
and preserving historical model accounting and source provenance. The paper
builds with 33 cited sources. No model calls, live continuation or external
messages were made during this work.
