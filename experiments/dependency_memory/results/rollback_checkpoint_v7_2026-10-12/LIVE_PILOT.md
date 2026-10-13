# Matched-checkpoint rollback: completed development pilot

October 12, 2026 local time; completed October 13 UTC. The corrected controller
preserves earlier task evidence and passes replay, but this small pilot does
**not establish a benefit from removing a failed visible record**. K solves
10/16 eligible tasks and R solves 8/16. The original information-loss diagnosis
remains separate from this new empirical comparison.

## What changed and what was actually tested

The [previous-result diagnosis](DIAGNOSIS.md) traces a source-loss path in v6:
rollback cleared earlier public transaction packets as well as unsuccessful
attempts. The retained balance vector was not a sufficient transaction history.
That result measures the whole old deletion-and-lesson policy, not deletion of
one failed branch from an intact checkpoint.

V7 saves the exact successful pre-failure context and retains all released
packets separately. One naturally failed prefix produces one shared lesson.
K keeps the failed candidate, brief visible note and receipt; R removes that
record. The first K/R requests otherwise contain byte-identical task evidence,
checkpoint, feedback, lesson, instructions, schema, model and remaining action
allowance. Independent checks compare both requests with the source packets,
so equal omissions from both arms cannot pass merely by matching each other.

Each later trajectory keeps its own new records normally. This is one deletion
of visible work, with a shared lesson, on fully available public evidence. It
does not roll back private reasoning, test native compaction, or test repeated
autonomous rollback. The [frozen protocol](../../rollback_checkpoint_v7/PROTOCOL.md)
defines the conditional terminal-success endpoint before dispatch.

## Fixed allocation and results

The allocation used 24 new authored intermediate-profile revision ledgers,
28 transaction IDs, six accounts, three disclosure stages and four candidate
actions. Model: `gpt-6-luna`, medium effort, subscription route, eight workers.
Construction seed: 2026101267. Immutable provider revision and sampling seed
are unavailable. The cohort was neither replaced nor extended.

| Disposition | Tasks |
|---|---:|
| Passed all stages in the shared prefix; no rollback pair | 8 |
| Natural failure with a valid lesson and remaining action; eligible pair | 16 |
| Invalid, unknown, capacity-limited or otherwise unusable prefix | 0 |

All 16 eligible pairs have both outcomes. Fifteen failures occurred after
earlier successful work: one at stage 1, eight at stage 2 and seven at stage 3.
Thus the corrected preservation boundary was exercised on real later-stage
failures, not only in scripted tests.

| Paired terminal outcome | Tasks |
|---|---:|
| Both succeed | 7 |
| Only K succeeds | 3 |
| Only R succeeds | 1 |
| Both fail | 5 |

K succeeds on **10/16 (62.5%)** and R on **8/16 (50.0%)**: R-minus-K is
**-12.5 percentage points**. The prespecified descriptive 10,000-resample task
bootstrap interval is **[-37.5, +12.5] percentage points**; the complete-pair
exact two-sided p-value is **0.625**, also descriptive. Only four pairs differ.
Neither superiority nor equivalence is established. These are selected failed
prefixes from one authored task family, not population recovery rates.

There are no missing outcomes, so missing-score completion bounds both equal
-12.5 percentage points. Those bounds are not a confidence interval. All
continuation losses are recorded as action-budget exhaustion; there are no
malformed candidates, output caps, unknown calls or global stops. The
[saved analysis](live_pilot/analysis.json) contains every task disposition.

## How strong was the deletion treatment?

The retained public dossier at the fork was 2,830-9,980 UTF-8 bytes (median
6,672.5). Successful checkpoint content was 61-712 bytes (median 375.5). The
K trial field was only 339-434 bytes (median 382); R replaces it with `[]`,
two bytes. These are representation sizes, not Shannon-information estimates.
The visible notes describe an attempted calculation; the model's private
calculation trace is not part of the treatment.

A clearly labeled [post hoc literal-overlap inspection](lesson_overlap_inspection.json)
finds the **entire failed six-balance vector in 15/16 shared lessons**. Both arms
therefore still saw those incorrect values in their lesson after R's raw record
was removed. The protocol explicitly permits branch-derived lesson content;
this is not a breach of the frozen comparison. It does mean that this pilot
mostly tests removing an additional presentation of the failed answer, rather
than removing that answer's information altogether. The scan is a literal
text check, not a semantic information measure or a prespecified efficacy test.

Inspection of the four discordant trajectories also cautions against a single
mechanism story. In `fb6ba184e61254a6` and `ae9128f45eab886f`, both arms first
correct the original stage-two failure to the same balances, then differ on
the next stage. One favors R and the other K. In `303b4616295958d3`, R eventually
corrects stage two but has no action left for stage three. The remaining
discordance, `fe6a51dba9b1ec94`, follows a stage-three failure with one action
left. These are descriptions of saved trajectories, not proof of anchoring,
forgetting or any private reasoning mechanism. Full IDs and call references
remain in [execution](live_pilot/execution.json).

## Execution, costs and audit

The run completed all 72 job dispositions with **130 known model calls**:
78 shared-prefix/lesson calls, 26 K continuation calls and 26 R continuation
calls. This is below the frozen 192-admission ceiling. Of 312 possible call
identities, 130 completed and 182 were never dispatched; mutually exclusive
possible identities are not additional observations. No call was retried.

Measured controller wall time was **463.54 seconds (7.73 minutes)**, excluding
preflight and replay. Peak admitted concurrency was **eight**, independently
reconstructed from the ledger. Summed call elapsed time was 2,964.86 seconds;
that is not sequential runtime or a measured parallel-speedup baseline.

Actual recorded usage across all 130 calls is 750,914 input tokens (including
149,248 cached tokens) and 245,850 output tokens (including 235,423 reasoning
tokens). Count subsets once. The inherited accounting conversion reports
4.6146020 planning credits; it is not an actual account charge or API-dollar
price. Actual subscription debit is unavailable; API-key calls are zero.
Standalone arm projections in analysis overlap in their shared prefix and
must not be added as actual spend.

The [frozen-source audit](live_pilot_audit.json) passes all 130 received-request
replays, all 16 matched-context contracts, all 114 independent action grades,
fixed job/call-slot accounting, unique-thread and usage checks, and source and
evidence hashes. Independent grades comprise 83 public passes and 31 public
mismatches. Replay itself makes zero model calls.

The installed client initially failed preflight before any model admission
because it exposed generic resource helpers absent from the older contract.
That [zero-admission failure](preflight_failure.json) is preserved. A reviewed
v7-only adapter pinned the actual declarations and required an empty disabled
MCP inventory before each call, then froze a new bundle with the **same cohort**.
Its nine negative/positive transport cases, 14 actual payloads and eight-way
loopback preflight passed before this live run. Historical modules were not
changed.

One client observation limit remains disclosed: a synthetic clock-helper call
accompanied by an answer can lack an exposed tool event. Its diagnostic is
saved separately, not counted as a successful tool-rejection test. The client
permits only one model generation and no later generation can consume a helper
result; subsequent task calls replay only the explicit answer. The contract
does not claim that every attempted tool call is observable or that provider
internals are known. See the protocol's compatibility amendment.

## What to make of the evidence

1. The large v6 deficit remains evidence against its whole lossy policy. It
   does not demonstrate that a clean checkpoint rollback is generally harmful.
2. V7 verifies that task facts and successful context can be preserved while
   deleting exactly one visible record. Its observed direction still favors
   keeping the record, but this sample is too small and the treatment too narrow
   to establish a general advantage, disadvantage or equivalence.
3. The lesson frequently retains the failed answer. A stronger mechanism study
   should distinguish raw-record removal from removal of branch-derived content
   in the lesson, and use substantive visible failed work such as an attempted
   patch or explicit search state. Longer private reasoning cannot be inferred
   from the short notes tested here.
4. If the research question instead concerns compact memory, compare full
   evidence, balances alone and a transaction-level sufficient dictionary under
   an explicit access contract. That would test retention separately from the
   branch-removal mechanism. The dictionary is an elementary baseline, not a
   novel result or a model-tested method here.

These follow-ups are proposals, not additional performed experiments. No
confirmation allocation, manuscript claim upgrade or automatic sample extension
follows from this pilot. Comparing its rates directly with v6 cannot identify
the effect of fixing source loss: the study design and information access differ.

## Evidence location

The authoritative allocation is [prepared_client_2026-10-12](prepared_client_2026-10-12/manifest.json),
manifest SHA-256 `e2c08056c382692eac346ede944d474df14bcb9cfa8d51fcf38d858010a962dd`;
its source snapshot SHA-256 is
`aa5c83e1372945ed0707d4b053b7533defd30f31d8e18c222c93099f478dae5f`.
The [live evidence manifest](live_pilot/evidence_manifest.json) seals the run.
[Scripted rehearsal replay](rehearsal_client_audit.json) is offline controller
evidence, explicitly distinct from the live observations above. After completion,
only test import paths were repaired for repository-root unittest discovery;
the archived experimental source and live evidence remain unchanged. Repository
verification details are recorded in [validation.json](validation.json).
