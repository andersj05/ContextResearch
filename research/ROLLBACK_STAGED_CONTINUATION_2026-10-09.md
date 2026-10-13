# Staged rollback v5: complete allocation after the continuation amendment

October 9, 2026. **Fixed allocation complete with four retained unknowns;
independent replay/regrading passed.**
All 768 jobs have final dispositions. No global stop or unstarted global-stop job
remains. The cumulative record has 2,124 metered completions, including eight
excluded calibration calls, and four unresolved dispatches. No admitted identity
was repeated. The 48-task cohort is unchanged; its four missing episode scores
remain missing.

Primary evidence: [amended result directory](../experiments/dependency_memory/results/rollback_development_v5_continuation_2026-10-08/README.md),
[primary analysis](../experiments/dependency_memory/results/rollback_development_v5_continuation_2026-10-08/live/analysis.json),
[execution](../experiments/dependency_memory/results/rollback_development_v5_continuation_2026-10-08/live/execution.json),
[continuation protocol](../experiments/dependency_memory/rollback_development_v5_continuation/PROTOCOL.md)
and [immutable first phase](ROLLBACK_STAGED_DEVELOPMENT_2026-10-08.md).

## What changed

The user explicitly amends the rule that an unknown dispatch stops the whole
allocation. Unknown calls now end only their affected trajectories, preserving
their missing scores and reservations. Independent jobs continue. Source/client,
account allowance, isolation and accounting failures remain global stops.

The new phase imports original calls, events and thread identities into a fresh
cumulative ledger. Completed outcomes and the original unresolved K call are
carried forward. Two healthy partial trajectories restore eleven verified saved
responses before their next never-admitted identities. The routing Z episode
finishes correctly; the memory G episode encounters a later unrelated response
failure. Existing passed calibration is reused without another generation.

The continuation admits 1,892 new identities: 1,889 metered completions and three
unknowns. Original 235 completions and one unknown remain unchanged. All 1,321
files in the first phase's sealed closeout pass a separate integrity check.
All stages use Luna medium, four workers, fresh provider threads and the same
declared information-access contract. The cumulative 13,640-generation ceiling,
construction seed 2026100857, task artifacts, graders and action limits remain.
Failure handling and execution timing were amended after observations; this is
development evidence.

## Quality comparisons

| Track | Scheduled R/K pairs | Complete pairs | R successes on complete pairs | K successes | R minus K | Descriptive task interval |
|---|---:|---:|---:|---:|---:|---|
| Conditional mechanism | 3 eligible | 3 | 3 | 3 | 0 pp | Fewer than six pairs |
| Independent policies | 48 | 46 | 45 | 45 | 0 pp | [-6.52,+6.52] pp |
| Repeated memory cuts | 48 | 48 | 48 | 48 | 0 pp | [0,0] pp from observed ties |

Policy has one R-only success, one K-only success and 44 ties. Its fixed
48-task missingness bounds are [-2.08,+2.08] pp. All memory pairs tie at success.
The zero memory bootstrap interval is a consequence of resampling only the
observed all-success outcomes; it does not establish population equivalence.
Neither track supplies a measured quality advantage here.

Only three of 48 common prefixes yield an eligible public mismatch. Forty-four
pass the public stages initially and one ends with a runtime error. All seven
matched continuations pass on each eligible task, including removal alone,
generic summary, a fresh solve and the mechanical-receipt lesson ablation.
This remains below the six-pair threshold for a mechanism interval.

Whole-policy marginals are K=46/47 known plus one missing, R=46/47 plus one
missing, Z=48/48, G=47/48 and F=47/48. Memory K/R each pass 48/48; G passes
46/46 known with two missing. The four known policy failures remain observed
failures, distinct from unresolved transport outcomes. Across independent
episodes and matched continuations there are 401 known scores: 397 passes and
four failures. The 315 ineligible mechanism continuations are explicit skips.
Repeated tracks reuse the same 48 tasks and cannot be pooled as independent
trials.

## Difficulty and history burden

All twelve K/F control-cell point estimates exceed the prespecified 40–75%
calibration target. Most are 100%; short-hard F and long-moderate K are 87.5%.
Long-hard K has seven known scores and one missing, with all seven passing.
These are descriptive small-cell observations, not exclusions or retuned tasks.

Long control cells use a median of eight candidate actions, despite an allowance
of thirty. Median visible raw K trial history is 2,135 bytes in long-moderate
and 2,609 bytes in long-hard. Those history summaries include observed actions
from the partial episode. The nominal long horizon rarely produces heavy
history pressure in these families. Persistent checkpoints and generic controls
remain strong. A separate harder cohort would need new identities and a fresh
freeze; it has not been run here.

## Metering and verification

Resource comparisons below use only the same complete-pair tasks. They count
every arm call, including its writers and compression calls. Mechanism common
preparation is charged once and excluded from the paired continuation totals.

| Track | Complete pairs | R input-token change relative to K | Output including reasoning | Calculated planning credits |
|---|---:|---:|---:|---:|
| Mechanism | 3 | -34.62% | -22.70% | -29.65% |
| Independent policies | 46 | +5.17% | +9.01% | +7.21% |
| Repeated memory cuts | 48 | +4.22% | +3.27% | +3.57% |

The small conditional mechanism set has lower recorded R resource use. Whole
policies and memory have higher R totals, with unchanged mean quality. These are
descriptive outcomes, not proof of a general resource effect or actual charge
savings. The [derived task comparisons](../experiments/dependency_memory/results/rollback_development_v5_continuation_2026-10-08/cumulative_diagnostics.json)
retain every paired task and numerator/denominator.

Known usage is 9,665,544 input tokens, including 3,472,384 cached tokens, and
2,260,637 output tokens, including 1,565,587 reasoning tokens. Reasoning is a
subset of output and is counted once. Calculated usage is 44.6089585 planning
credits; 16.900 credits remain reserved for four unknowns. Actual account charges
are unavailable. There are no API-key calls or purchase/model fallbacks.

All 754 distinct repository tests have passing results, including ten
continuation and nine actual Docker isolation tests. Two Windows atomic-replace
errors in the full run pass unchanged on exact recheck; original failures and
passing rechecks remain visible. Full scientific validation passes 259 check
categories and paper assembly passes with 48 cited sources. Independent
[live replay/regrading](../experiments/dependency_memory/results/rollback_development_v5_continuation_2026-10-08/launch_checks/live_audit_result.json)
reconstructs all 2,124 received generations, reconciles all four unknowns,
verifies all 453 executed jobs plus 315 dependency skips, and matches every
one of the 16,904 slot dispositions. Peak admitted calls is four; original
receipts, metering and reported analysis agree. It makes zero model calls.

Read the [cumulative live report](../experiments/dependency_memory/results/rollback_development_v5_continuation_2026-10-08/LIVE_RUN.md)
for the complete comparison tables and evidence links. All runnable jobs are
finished; no unknown identity was retried or replaced by a zero score.

Immutable provider revision and sampling seed are unavailable. Four authored
families, a strong ceiling, small conditional sample, possible nonrandom
infrastructure missingness and joint changes to disclosure timing/action
allowance limit interpretation. No superiority, equivalence, deployed-harness
or native-compaction gain follows. C75 and manuscript v0.42 remain unchanged.
