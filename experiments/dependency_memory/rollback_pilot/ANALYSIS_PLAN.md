# Rollback analysis and interpretation

October 8, 2026. Review specification v0.2; no observed model outcomes.
The primary E2 question and contexts are in [the protocol](DRAFT_PROTOCOL.md).
This plan defines how to avoid mistaking additional feedback, retries or missing
observations for a deletion benefit.

## Cohort accounting

Every selected task gets one ledger row before a model request. Preserve the
sequence of initial dispositions: invalid checkpoint, no candidate, malformed
branch, capped response, syntax/runtime error, timeout, public pass, or eligible
public failure. After failure, record lesson and summary usability separately.
Record any later capacity or infrastructure stop without overwriting that history.

K/R primary eligibility requires a valid checkpoint interface, the objective
failure receipt and a usable common lesson. A lesson with a bad substantive claim
still qualifies if its interface is valid; never filter by whether it led to the
right answer. A failed generic summary blocks G only. L failure blocks K and R,
but need not block Z or G. Secondary comparisons use their specified common
eligible intersection and disclose its size.

Never replace initial tasks to obtain 24 failures. The top table always begins
with 12 selected math and 12 selected coding tasks. Report preparation failure
and continuation performance separately; neither disappears from policy cost.
Checkpoint content quality, branch length and lesson sufficiency are descriptive
flags, not post-outcome eligibility filters.

## Primary pilot effect

For eligible task i and continuation draw j=1,2, let y_iaj be 1 for a correct
terminal artifact in arm a and 0 for a known failed answer. Define:

```text
d_i = (y_iR1 + y_iR2)/2 - (y_iK1 + y_iK2)/2
Delta_domain = mean_i(d_i)
```

Report math and coding separately in percentage points. Also show each task's
four binary K/R outcomes; the same task's draws and arms are correlated. Do not
run a test that treats draws, assertions or tokens as independent task samples.
For at least six complete task pairs, a seeded 10,000-resample task bootstrap
(seed 20261009) may give a descriptive 95% interval. Below that, show individual
pairs and the range only. The small development sample supports no confirmatory
p-value, training-data generalization or proof of no effect.

## Missingness and preparation errors

Known malformed or capped terminal responses score 0. For unknown transport
outcomes, show complete-pair estimates and bounds over all scheduled eligible
pairs: assign each missing R score 0 and K score 1 for the lower bound; reverse
those assignments for the upper bound. Keep the denominator fixed at the
scheduled eligible task count and known answers unchanged. Count never-dispatched
slots after a stop as unknown, not successful, free or silently absent.

If either K or R cannot fit its fully rendered request, mark the primary pair
capacity-infeasible before dispatching either arm for that task. Report this
loss separately; it does not become a deletion success. Z/G may still be run
within their scheduled slots, with the resulting denominator stated. Capacity
effects on a complete policy belong in E4, where every selected task counts.

Shared preparation costs are charged once to the experiment's actual-spend
ledger. Standalone-policy projections charge the entire preparation a policy
would need, excluding experimental-only writers for other policies. Report both
ledgers; summing projected policy costs is not actual experimental spend.

## Secondary pilot measures

| Measure | Operational definition | Interpretation |
|---|---|---|
| R minus Z | Same eligible task and feedback; add L | Value of a generated lesson after deletion, including its cost |
| R minus G | Same eligible task; use targeted lesson versus generic summary | Representation comparison with matched maximum length, not matched realized content |
| Repeated rejected candidate | Exact same math values or identical code artifact reappears | Automatic, narrow behavioral diagnostic |
| Repeated refuted assumption | Blinded review finds the specific disproved proposition asserted again | Optional human coding; unresolved judgments remain unknown |
| Retained-fact loss | Blinded review identifies a previously supported useful fact absent from the next artifact/context | Exploratory; absence in a response does not prove internal forgetting |
| Effective deletion | Token counts of B and the complete K/R inputs; quoted B material retained in F/L | How large the actual context intervention was |
| Lesson sufficiency | L already contains a complete solution under retrospective grading | Writer may have solved the task before continuation |

Human-reviewed measures require a fixed rubric, masked arm labels, independent
coding and reported disagreement before use. They are not prerequisites for the
objective primary endpoint. Do not spend unbudgeted model-judge calls on them.
String overlap is a representation measure, not a proof of semantic redundancy.

## Resource accounting

For every call report model identifier/effort, input tokens, cached input, cache
writes, output, reasoning subset, elapsed time, dispatch status and price version
when exposed. Use mutually exclusive input buckets; reasoning is already part
of output. Unknown fields remain unknown. Separate API billed usage, Codex
planning credits, local checker CPU time, wall-clock delay and archive bytes.

Record both creation and later use of summaries. Shortening a context can change
cache hits, subsequent output length and failure/retry behavior. A shorter prompt
does not by itself establish efficiency. E2's shared preparation and equal output
ceilings cannot establish an end-to-end budget advantage; E4 addresses that question.

## Confirmation analysis

E3 uses one K/R terminal draw per eligible task. Within each domain tabulate
both-correct, R-only-correct, K-only-correct and both-wrong counts. The primary
test is the exact two-sided paired discordance test: conditional on m discordant
pairs, compare R-only wins to Binomial(m, 0.5). With m=0, p=1. Test each domain
at alpha 0.025 and report effect estimates and uncertainty as well as p-values.
No pooled claim replaces a failed domain-specific result. This assumes the frozen
sampling scheme supports the intended task-level interpretation; assess clustering
by template/contest before freezing the power calculation.

The exact binomial interpretation requires independent, exchangeable discordance
directions under its null. If contest/template clustering or the final stratified
sampling violates that assumption, freeze a suitable stratified/cluster analysis
and redo the power calculation before E3. Do not retain an "exact" label for an
inapplicable model of the data.

Power planning in [the suite](EXPERIMENT_SUITE.md) is approximate. Validate it
under the final sampling and analysis implementation. Report sensitivity to
eligibility, discordance, clustering, multiple solutions and missingness.
No significance-based optional stopping, outcome-driven sample expansion or
post-hoc exclusion of unhelpful lessons is allowed.

## Complete policies and autonomy

For E4/E5, the denominator includes every selected task under every policy.
Preparation failures, malformed answers and budget exhaustion are policy outcomes.
Provider-unknown outcomes get explicit missingness bounds. Report terminal test
success at the common episode budget, actual dollars/tokens/latency, and whether
the budget, context, rollback or call cap ended the episode.

The public-test selector is identical across policies. Report selected-candidate
and final-actor-candidate results separately. Oracle selection using reserved tests
may appear only as a labeled upper bound, never as the primary deployable result.
Native-harness comparisons must declare extra memory/tools and distinguish a
whole-system result from the controlled visible-context comparison.

E5's 12 authored decision probes have separate correct/incorrect acceptance tables.
The main public-pass stop rule otherwise makes complete-correct-answer abandonment
unobservable. Report the probe's different feedback condition and do not interpret
its small authored sample as a natural rollback rate.

## Decision table for the handoff

| Observation | Supported interpretation | Next design action |
|---|---|---|
| R improves on K with informative uncertainty | Deletion helps conditional recovery in this setup | Confirm on a frozen new cohort; test full policy cost |
| R and G behave similarly | Generic compaction may provide the same practical benefit | Prefer the simpler justified policy; do not claim a unique lesson mechanism |
| R loses useful facts and performs worse | Removing the branch can harm these tasks | Investigate retention/checkpoint rules in a new development version |
| Success is similar and R uses fewer input tokens | Potential context savings, with quality difference unresolved | Measure full costs and establish a quality tolerance before an efficiency claim |
| Few initial failures or F/L reproduce most of B | Weak opportunity to test the proposed mechanism | Report feasibility; design genuinely harder/longer tasks separately |
| Benefits appear only with hidden-answer feedback | Benefit under oracle assistance | Keep it separate from autonomous or public-feedback claims |

## Required report outputs

Produce the all-task flow table, paired primary table per domain, every secondary
condition, missingness bounds, resource ledgers, failure examples selected by a
prespecified rule, and frozen artifact hashes. Keep raw records and failed starts.
Example selection: first task by frozen order in each outcome class, rather than
the most persuasive anecdote. Write the finding before updating any paper claim.
