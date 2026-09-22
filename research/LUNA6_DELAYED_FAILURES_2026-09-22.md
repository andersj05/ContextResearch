# New Luna calls: concrete delayed failures and the price of memory repair

September 22, 2026. Development evidence from constructed release handoffs;
publication novelty, held-out transfer and production savings remain unproved.

## Completed fixed pilot

The [main contract](../experiments/dependency_memory/luna6_revision/CONTRACT.md)
was committed as `136d589` before model answers. **117 fresh GPT-6 Luna medium
calls** completed, with no transport failure. The
[reconstructed evidence audit](../experiments/dependency_memory/results/luna6_revision_2026-09-22/report.md)
passes: exact public requests, fresh-thread settings, memory boundaries, source
hashes, independent gate grading and usage reconcile. Usage is 379,539 input
tokens (158,720 cached), 42,922 output tokens (35,102 reasoning), and **1.1282525
planning credits**, including the smoke call and unsuccessful decisions.
The mutable model alias supplies no immutable provider revision. Actual
experiment-attributable subscription debit is unknown.

Four histories each contain six service records. A 900-byte memory is retained
before a candidate pair is disclosed, then 440 bytes before the target and late
event are disclosed. The sixteen continuations per method reuse those four
histories. This is a controlled information-loss experiment, not sixteen
independent real incidents or a comparison with native provider compaction.

| Method | Exact success | Unsafe release decisions | Model credits | Cache-neutral credits |
|---|---:|---:|---:|---:|
| Prose summary | 12/16 | 0 | 0.3379850 | 0.3984650 |
| Structured summary | 8/16 | 1 | 0.2912620 | 0.3678700 |
| Checked replacement | 16/16 | 0 | 0.2653020 | 0.3361500 |
| Direct dependency rows | 16/16 | 0 | 0.0865340 | 0.1389500 |
| Indexed recovery | 16/16 | 0 | 0.0830870 | 0.1395350 |
| Full original history | 16/16 | 0 | 0.1293510 | 0.1777350 |

Memory-writing calls are included. Shared parent calls are charged in full to
each hypothetical method that uses them, so this table does not sum to actual
experiment usage. Cache-neutral accounting charges every input token at the
uncached rate; it is an arithmetic sensitivity check, not another model run.
Indexed recovery reads 12,404 bytes across its sixteen target queries. The
direct/indexed cost ranking reverses after removing cache discounts; no robust
ordering between those two methods is established.

Checked replacement improves the structured pipeline's observed outcomes while
using **8.9% fewer** model credits, or **8.6% fewer** without cache discounts.
This is an observed improvement at the same model-credit allowance. Its cost
remains much higher than direct retention, indexed recovery and full history.
The known gate can be represented directly; generating and replacing a proposal
is unnecessary overhead here. Repair and direct final requests are byte-identical.

## Concrete failure witnesses

1. **A blocker disappears at the second boundary.** In `w2-t0-e0-structured`,
   `delta-e58` has artifact `543e05fe` and open blocker `REL-543e`. The parent
   memory preserves that blocker. The child proposes 545 bytes, above the
   440-byte limit; its admitted prefix ends just after the passing CI results,
   before the blocker field. Following an irrelevant typography update, the
   final model emits `release` with no work. The executable gate requires
   `hold` and `blocker:REL-543e`. Repaired, direct, indexed and full-history
   continuations all return the correct blocked result. This is a simulated
   release decision; no deployment occurs.
2. **An unclipped summary drops negative evidence.** In handoff `w1`, the prose
   parent (875 bytes) and child (366 bytes) both fit. The child preserves CI
   results and artifact identities but omits the explicit empty blocker sets.
   Three of its four continuations return `inspect`, including an initially
   valid release. This is consistent with insufficient retained evidence;
   not every wrong work item is explained by that omission alone.
3. **Identifiers change before host clipping.** The unclipped `w3` structured
   parent changes `ember-0c4` to `ember-0c`. Its child then loses the selected
   service entirely to clipping. Separately, the unclipped `w2` prose parent
   replaces required-test identifier `integ` with `integration`; a later answer
   requests `ci:integration` rather than the required `ci:integ`. Semantically
   similar names are not interchangeable executable identifiers.

All four structured child proposals exceed their cap. Across parent and child
memories, prose has four clipped proposals and structured has five. Thus the
pilot **does not isolate semantic summarization loss from truncation**. Both
effects occur in saved evidence. The supplied gate rules occupy much of several
child summaries even though those rules are supplied again in the final prompt.
That observation motivates the prospectively frozen follow-up below.

## Why cheap checking is not yet a new general method

The checker conservatively substitutes a hand-written projection of the known
gate dependencies. It preserves service identity, artifact, approval scope, CI
scope, required tests, CI results and blockers. It sees only available evidence:
the second projection is reconstructed from the bounded first projection.
The retained sizes are 769 bytes initially and 311–321 bytes later. No hidden
late target or event is used. This is not automatic semantic checking of prose,
minimal repair, or extraction from unseen code.

The per-call CPU timer is too coarse to resolve the individual checks: saved
zero readings must not be read as free computation. The separate repeated
[local calibration](../experiments/dependency_memory/results/luna6_revision_2026-09-22/local_cost_calibration.json)
measures medians of 0.1875 ms for direct serialization, 0.5 ms for replacement
checking and 0.1875 ms for indexing/serialization across all four histories.
Disk infrastructure, adapter development and arbitrary text extraction are not
included. Costs begin at the handoff; prior workflow execution is also unmeasured.
Consequently this is not a fully monetized production-total-cost result.

Relative to full-history access, direct retention leaves only **0.0428170**
observed credits, or **0.0387850** cache-neutral credits, for an additional
extractor across this four-history workload before losing its measured cost
advantage. This is a post-hoc break-even calculation, conditional on preserving
the same outcomes. No automatic extractor was run. Cheap memory alone does not
make expensive extraction pay.

The [prior-art comparison](LUNA6_SCOPE_PRIOR_ART_2026-09-22.md) covers typed
retention, pinning and verification. No broad novelty claim survives those
comparisons. The new evidence is the saved failure/cost behavior of this model
under the declared access contract.

## Stronger prompt control

After inspecting the main pilot, the
[data-first follow-up](../docs/LUNA6_DATA_FIRST_FOLLOWUP.md) was frozen in
`8d8a358`: 24 additional calls on the same four histories, with the same model,
caps, timing and final grader. Its memory prompt explicitly announces repeated
public rules and prioritizes service facts and exact identifiers. It introduces
no checker or archive. This addresses a possible weakness in the initial
baseline, but it is a development prompt package, not a held-out or single-factor
causal experiment.

All 24 follow-up calls completed, and their independent request/usage audit
passes. **None of its eight memories is clipped**, but it succeeds on **12/16**
decisions, with no unsafe release. Cost is **0.1908300 planning credits**, or
**0.2714700** without cache discounts. Both studies together use **141 calls and
1.3190825 planning credits**, within the shared 144-call/20-credit ceilings.
Combined usage is 456,012 input tokens (194,560 cached), 49,345 output tokens
(39,589 reasoning). [Combined report](../experiments/dependency_memory/results/luna6_memory_report.md).

The surviving failures are not caused by host truncation:

- In `w0`, the child is only 219 bytes, but changes `atlas-99c` to `atlas-99`.
  Both continuations for the original service fail. The memory also stops
  retaining an explicit current-artifact field.
- That child keeps birch's approval `1120b4ed` and CI artifact `f6cafa82`, then
  labels CI as stale relative to the approval. The actual current artifact is
  `f6cafa82`; the stale object is the approval. The later model returns the
  approval ID as the artifact and requests CI reruns instead of approval.
  This is a concrete semantic-role corruption across the memory boundary.
- In `w3`, an unclipped 602-byte parent changes `ember-0c4` to `ember-0c`.
  Its 257-byte child repeats the shortened identifier. The unchanged-state
  continuation returns `inspect` despite the original evidence permitting release.

These observations support an engineering target beyond clipping: cheap checks
for exact identities and the roles of reference values. They do not establish
that every decoder error is information-theoretically forced. One continuation
even resolves the shortened ember name after a different late event. Learned
decoding and semantic ambiguity still contribute.

The stronger prompt is cheaper than checked replacement but less accurate in
this sample. Direct dependency rows and indexed recovery remain better observed
points in both success and model-credit cost. A small shared-schema adapter can
preserve roles cheaply; deriving that adapter automatically and validating it
on a new workflow remain the next substantive tests. No publication novelty or
deployed-agent cost gain is claimed. Claims C44-C46.
