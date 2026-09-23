# Cross-record recovery stress test

September 22, 2026. The [previous prospective schema study](SCHEMA_TRANSFER_PROSPECTIVE_2026-09-22.md)
found a narrow gain for automatic direct records over prompting on six
constructed traces, while target-indexed recovery remained cheaper and more
accurate. Its indexed control recovered a complete nested workflow record.
The present third study tests whether that control still dominates when each
workflow's dependencies are split across tool results. It is a constructed
stress test, not a replay of production traces or an unknown-domain test.

## Freeze and information contract

The [protocol](../experiments/dependency_memory/cross_record/FROZEN_PROTOCOL.md)
and four escrow/package development fixtures were committed at `17d56a6`.
The generic join, two narrow checks, direct-record control, fixed runner and
analyzer were frozen at `b7f7740`, before evaluation seeds were derived or any
evaluation model response. Twelve retry, CI and data-job evaluation fixtures
and their hashes were then frozen at `dbaa6fd`. Four seeds per family come
from the full implementation commit hash. The domain grammars themselves
were visible in the older study, so this is prospective at the value/response
level, not blind transfer to unseen schema definitions.

Each trace has seven workflows. A root record and one result for every
component tool share an exact opaque `workflow_key`; the results are shuffled.
At the first memory boundary the model or extractor sees the public JSON tool
schemas, results and task rule, but no candidate or future. Parent memory may
hold 7,000 UTF-8 bytes. Two candidate root IDs are then disclosed and child
memory may hold 2,600 bytes. Only after that is the exact target and one late
event disclosed. Each evaluation trace has an irrelevant edit, a repair, and
a gate-changing edit, for 36 paired final decisions. Private truth and grader
files never enter public model requests. Fresh-process/thread model calls do
not receive previous reasoning, provider history or archives; the index and
full-history arms have explicit, costed archive access after disclosure.

The generic extractor uses only standard schema/result signals and joins all
component results by the exact workflow key. It retains detected opaque IDs,
references, enum states and booleans in a compact field/row table. The first
check verifies detected exact ID values; the second verifies their root,
component and field-path associations. Neither check certifies unannotated
state semantics or the later model's decision. The table canonicalizes
repeated workflow keys into one joined row while retaining component identity
and associations. Missing/duplicate components or uncertain short strings
cannot receive a successful certificate.

The eight methods are strong prose prompting, unvalidated structured table
prompting, a checked structured proposal with conservative fallback, automatic
projection/checking, hand-written direct fields, indexed raw full-workflow
recovery, indexed recovery followed by generic projection, and full history.
The projected index is the strongest compact recovery control: it retrieves
the root and every related component, then serializes only the selected
workflow. It is charged for index build/storage, lookup and projection.

Development-only tests check reconstruction against the terminal grader,
order-invariant joining, scope swaps that preserve an identifier multiset,
identifier corruption, missing components, request timing and budget rotation.
Before the live run, 356 repository tests and the repository validator passed.
Mechanical evaluation preflight found a largest automatic parent of 3,284
bytes, child of 1,274 bytes, and public request of 13,012 bytes under the
16,000-byte transport limit; it did not inspect model outcomes or change the
frozen code. The fixed schedule is 348 GPT-6 Luna medium calls with a global
356-dispatch and 50-planning-credit ceiling. Exact provider token usage and
local CPU, reads and writes will be reported separately. Local conversion
weights are synthetic; direct-method authoring and actual subscription debit
are not measured.

## Results

The original frozen model schedule stopped after 199 dispatches: 198 fully
metered calls and one dispatched CI projected-index final with a provider
generation error and no answer/usage. Its [original completion
record](../experiments/dependency_memory/results/cross_record_2026-09-22/completion.json)
preserves the interruption. The 36-pair preregistered primary criterion is
therefore **unassessable**. No failed call is retried or filled in.

A [separate continuation protocol](../experiments/dependency_memory/cross_record_continuation/FROZEN_PROTOCOL.md)
and [ordered plan](../experiments/dependency_memory/cross_record_continuation/plan.json)
were committed at `f448e2c` before any further model call. The plan hashes all
209 original evidence files and contains only the 149 never-dispatched
identities. Its controller and analyzer were frozen at `258803e`. That
continuation completed all 149 calls without an additional transport failure.
The [combined saved-evidence analysis](../experiments/dependency_memory/results/cross_record_continuation_2026-09-22/analysis.json)
reconciles the exact 348-identity schedule: 347 metered answers and the one
permanent missing CI answer, with no duplicate identity. The original run
settled 1.9150415 token-derived planning credits and the extension 1.9097185,
for **3.8247600 known planning credits**. The missing call's usage is unknown;
7.65 credits were its conservative reservation, not observed debit. Total
completed-call usage is 1,339,996 input tokens (609,280 cached) and 147,652
output tokens (87,195 reasoning). The actual attributable subscription debit
is unknown.

## Exploratory results and criterion

The original 36-pair primary criterion stays **unassessable** because the
original protocol stopped at the provider error and forbade resumption. The
separate extension yields **35 fully answered paired futures**. The one
incomplete future is excluded as a whole from that matched subset. Its
descriptive result is negative for the proposed automatic-direct mechanism:

| Method | Exact failures / 35 complete pairs | Exact failures / 36 scheduled | Known experimental total credits |
|---|---:|---:|---:|
| Strong prose prompt | 3 | 3 | 0.87246417172 |
| Unvalidated structured prompt | 6 | 6 | 0.96379203239 |
| Checked structured proposal | 18 | 18 | 1.0302089537 |
| Automatic direct | 7 | 7 | 0.34358725611 |
| Hand-written direct | 4 | 4 | 0.19375442753 |
| Indexed raw full-workflow recovery | 1 | 1 | 0.2261409081 |
| Indexed projected recovery | 6 | 7, including one missing answer | >=0.28192155505 |
| Full history | 6 | 6 | 0.44485017696 |

The totals charge every available model call and measured local CPU, reads,
writes and index storage under the frozen synthetic weights. The indexed
projected total is a **lower bound**, because one model call has unknown usage
and the interrupted recovery's local timer was not saved. Other totals include
the one final call for the incomplete pair; the 35-pair failure column is a
matched outcome comparison, not a recomputed 35-pair cost schedule. Automatic
costs less than either prompted method but fails more often than both, and
hand-written direct plus indexed raw are both cheaper and more accurate.
These observations do not satisfy the user's fewer-failures-at-no-greater-cost
criterion or establish the candidate contribution. The indexed raw control
retrieved the root and every related component, with index construction,
storage and reads charged at the declared synthetic price.

The family split matters. Automatic fails 1/12 retry, 2/12 CI and 4/12
data-pipeline decisions. Strong prose fails 2/12, 0/12 and 1/12 respectively;
hand-written direct fails 4/12, 0/12 and 0/12; indexed raw fails 1/12, 0/12
and 0/12. This is a small constructed sample of correlated futures, not an
estimate of a population effect.

## What failed

All twelve automatic parent and child tables pass the exact-ID and
owner/component/path checks. Neither automatic nor hand-written direct
projection is infeasible, and no prompted or checked parent/child memory is
clipped. An independent reconstruction applies the frozen terminal rule to
the retained automatic and direct tables and obtains the correct decision on
**all 36 futures** for each. Structured memory is reconstructably sufficient
on 35/36; prose is not machine-parsed by this diagnostic. The automatic arm's
seven errors therefore arise in the final model's interpretation of sufficient
retained data. They include an omitted billing scope after a late retry
attempt change, two spurious CI scope obligations, one wrong data output ID,
and three data-job decisions with incorrect work or action. One automatic
data-job final says `publish` where the frozen rule requires `hold` for an
approval-scope mismatch. This was a simulated terminal answer; no external
job was published.

The raw indexed control makes only one error, omitting a billing scope after
the late retry-attempt change. The compact projected index has six model
errors on 35 answered calls despite reconstructably sufficient tables; its
seventh scheduled failure is the transport gap. That contrast suggests final
presentation and reasoning matter even when the fact set is adequate. It does
not isolate formatting as a cause, because the raw and projected requests
also differ in amount of redundant source material.

The checked structured-proposal arm has a separate implementation defect.
Nine of twelve model parent tables pass its narrow ID/relationship check.
In six of those cases the model also includes per-component `workflow_key`
columns from the source results. The check ignores these extra columns and
passes; the later child schema restriction rejects them as unsupported because
the generic joined table had canonicalized the repeated key. Those six traces
receive empty checked child memory and account for 18 `unparsed` finals.
Only three checked child proposals pass; three other child proposals trigger
a fallback. The arm's 18/36 errors therefore should not be interpreted as a
general failure of automatic checking or a fair comparison of a corrected
checker. A future version must align the parent certificate with the child
decoder, accept reconstructable repeated join keys or conservatively fall
back before deleting source evidence. Correcting it on these evaluated traces
would be post hoc and cannot repair this frozen result.

## Remaining claim boundary

The generic projection demonstrated deterministic retention sufficiency on
these 36 constructed futures. It did **not** reduce terminal failures versus
strong prompting or the hand-written/raw-index controls under the fixed
comparison. The domain grammars were already visible, local prices are
synthetic, human authoring and provider infrastructure are unmeasured, and
one provider call has unknown usage. External observed workflows and a
separately frozen corrected checker remain future tests. No novelty or
production cost advantage is established here.
