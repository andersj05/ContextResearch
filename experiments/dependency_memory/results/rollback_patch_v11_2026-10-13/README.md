# Patch rollback results — October 13, 2026

The fixed exploratory study is complete: **256 projects, 417 admitted calls,
408 known responses and nine preserved unknowns**. Twenty-eight initial patches
qualified as substantive executable failures. **No terminal-success advantage
from rollback was observed, and repair success was near the ceiling.** This does not establish
that deletion or lessons have no effect in harder tasks.

[Independent response replay](study_live_recovered_replay_audit.json) reconstructs
all 417 admissions and reruns received patches in isolated Docker. The separate
[independent arithmetic audit](independent_analysis_audit.json) verifies the
four arms, seven contrasts, missingness bounds, stopping and cumulative accounting.

Every arm had the full specifications, original two-file checkpoint, six public
examples, and identical initial failure feedback. Only two fields changed:
retention/deletion of the actual failed unified diff and its short note, and
absence/presence of the same categorical lesson. All arms got three repair
attempts on the same task. The first public pass stopped that arm; success
required the accepted candidate also to pass the terminal suite. Each terminal
container received the six public plus eighteen reserved cases in the frozen
order; the separate public container received six. Private grades never entered
actor context. Workspace restoration was held constant. This tests visible
failed-work deletion, not rollback of provider-private reasoning.

| Condition | Correct / known terminal outcomes | Unknown | Correct on first repair / known first repairs |
|---|---:|---:|---:|
| K0: keep patch, no lesson | 27/27 | 1 | 23/27 |
| R0: delete patch, no lesson | 27/27 | 1 | 22/28 |
| KL: keep patch + lesson | 28/28 | 0 | 23/28 |
| RL: delete patch + lesson | 27/28 | 0 | 24/28 |

The two missing terminal outcomes concern different tasks; there are 26 complete
quartets. R0's missing outcome occurred after a received first repair. Unknowns
are not failures, successes, or silently discarded cases. The first-repair
counts show that later attempts mattered, but neither factor consistently won
on immediate repair either.

**Contrasts and uncertainty.** Differences below are percentage points, with
positive values favoring deletion or adding a lesson as named. Bounds enumerate
all possible binary completions of the two missing arms across the fixed
28 eligible tasks. They are not population confidence intervals and do not
cover the seven unknown initial outcomes whose eligibility cannot be determined.

| Contrast | Complete-case mean | Complete tasks | Fixed-cohort missingness bounds |
|---|---:|---:|---:|
| Deletion without lesson | +0.00 | 26 | -3.57 to +3.57 |
| Deletion with lesson | -3.57 | 28 | -3.57 to -3.57 |
| Lesson with patch kept | +0.00 | 27 | +0.00 to +3.57 |
| Lesson with patch deleted | -3.70 | 27 | -3.57 to +0.00 |
| Average deletion | -1.92 | 26 | -3.57 to +0.00 |
| Average lesson | -1.92 | 26 | -1.79 to +1.79 |
| Interaction | -3.85 | 26 | -7.14 to +0.00 |

The task bootstraps in the [saved analysis](study_live_recovered/analysis.json)
are descriptive only. All-tie comparisons produce [0,0] intervals because the
observed pairs all tie; those intervals do not establish equivalence. Components
recur across these authored projects, so task resampling also does not capture
all dependence or generalization to real repositories.

**What information was removed?** No task-defining facts were deleted. The
failed patches nevertheless contained usable computation: actual implementation
choices and already-correct fixes. Diffs were 22,183–24,294 bytes with 461–515
changed nonempty lines. Removing a failed attempt discards its correct work
alongside its defects, even though the full specification still permits the
solution to be reconstructed.

The sole observed terminal failure illustrates this distinction. On project
`v11-study-composite_revision_ledger-83e899db4637da30`, the initial patch had
fixed refund handling but still chose wrong dependency versions. Its shared
lesson said `dependencies / missing_constraint`, with high confidence. K0,
R0 and KL repaired the project on their first attempt. RL reintroduced a refund
bug from the original checkpoint, then repeated it through all three attempts:
`1998 + 1318 = 3316` instead of the required `1998 - 1318 = 680`.

The [source inspection](inspection/sole_failure_source_review/review.json) binds
byte-exact extracts to the saved candidates. In the [first RL repair](inspection/sole_failure_source_review/RL_attempt1_rules.py.txt),
line 220 passes `refunds=False`, disabling the sign reversal on lines 37–38.
The initial patch and the other arms implement that reversal. Thus the deleted
artifact contained a useful fix. This one sampled regression cannot prove
that deletion or the lesson caused it: R0 also deleted the patch and succeeded.
A dependency-focused hint failing to preserve other repaired components is a
plausible interpretation, not an observed internal reasoning mechanism.
The [component-level case diagnostic](rollback_loss_case_diagnostic.json)
records the requirement text, affected solver bindings and all three RL submissions.

**Posthoc check of partial progress.** The [component replay](component_progress.json)
re-executes 157 distinct saved candidates, preserving the exact six-public and
24-terminal batches. All 358 references to saved public/terminal receipts agree.
The [original-checkpoint comparison](base_component_progress.json) executes
all 28 original checkpoints on those same batches. All 224 checkpoint component
instances fail at least one terminal case, while 158 components in the initial
failed patches pass all 24. Those 158 are therefore verified partial fixes on
the saved tests, not merely correct code already available in the checkpoint.
The remaining 66 component instances fail at least one case.

| Condition | Verified fixes with an observed value regression on first repair | First-repair fixes unassessed | Regressions in terminal submitted repair | Terminal fixes unassessed |
|---|---:|---:|---:|---:|
| K0 | 0 | 6 | 0 | 6 |
| R0 | 7, across 3 projects | 0 | 0 | 6 |
| KL | 0 | 7 | 0 | 0 |
| RL | 7, across 3 projects | 0 | 3, in the sole failed project | 0 |

For a matched comparison, the [paired counts](component_preservation_pairs.json)
restrict each contrast to the same verified fixes observed in both conditions.
First-repair regressions are K0/R0 **0 versus 6 among 152 assessed fixes**
(two R0 projects), and KL/RL **0 versus 7 among 151** (three RL projects).
The extra raw R0 regression above has no observed K0 counterpart. At the last
submitted repair, matched regressions are K0/R0 **0 versus 0 among 146** and
KL/RL **0 versus 3 among 158**. Missing values remain outside those denominators.

Missing replies and a whole-project execution failure explain unassessed
component values; zero observed value regressions is not a claim that the
retention conditions never fail. The final three RL regressions are ledger
components02/04/05 on the already-inspected project. Component instances share
code and recur across projects, so these are descriptive posthoc counts, not
independent trials or a causal mediation estimate. Passing 24 cases also does
not prove correctness on all possible inputs. There were 370 new offline Docker
batches and zero additional model calls. An unused first diagnostic plan had
proposed eighteen-only private inputs; it was corrected before execution to the
frozen 24-case terminal batch in [plan v2](component_progress_plan_v2.json).
The original study and its grades were never changed.

**Scope of the lesson test.** The factor separates lesson presence from deletion.
It tests five closed categorical fields, not unrestricted natural-language
reflection, accurate-versus-inaccurate lessons, or detailed summaries of all
completed fixes. All 28 lessons were schema-valid and claimed high confidence;
20 diagnosed a missing constraint, four a wrong selection, two a wrong order
and two a wrong state update. Confidence is a model output, not a calibration
result. The lesson cannot reproduce the patch, but it also cannot name a
specific component or preserve all useful implementation detail.

**All initial outcomes remain visible.** Of 256 initial calls, 213 passed both
public and terminal tests; four passed public tests but failed terminal tests;
28 were eligible public mismatches; two had runtime errors, one a syntax error
and one a timeout; seven were unreceived. The factorial is conditional on the
28 detected executable mismatches, not every possible failure. First reported
mismatches involved revision-ledger components in 13 tasks, dependencies in
nine, intervals in three and routes in three. These actual failure families
must not be confused with the project's leading-family label.

**Operational history and limits.** V9 had no natural failures; v10 had three,
below its frozen minimum of four. Both main gates remain closed. V11 was
explicitly frozen as an unplanned exploratory follow-up before treatment
outcomes. Its [original allocation](study_bundle/manifest.json) has 256 fresh
tasks and a 3,584-admission ceiling, not an outcome-selected extension.

The [first phase](study_live_replay_audit.json) stopped on an internal quota-read
RPC error after 289 admissions (284 known, five unknown), despite available
included usage. Before inspecting treatment effects, an [operational amendment](../../rollback_patch_v11_resume/PROTOCOL.md)
froze receipt-preserving recovery of only never-admitted work. The
[recovery manifest](recovery_bundle/manifest.json) binds the old evidence;
recovery added 128 calls (124 known, four unknown). Every old unknown and receipt
is unchanged. There were no context-capacity failures and no further global
stop, but the inherited interruption **permanently fails the original isolated
content-effect interpretation gate**. Results remain descriptive. Provider
weights and sampling seeds are not pinned; all arms used fresh isolated Luna
threads with the declared client/helper limitations.

**Resources.** The 417-call study used 13,620,089 metered input tokens (including
526,848 cached) and 1,178,731 output tokens (including 318,067 reasoning tokens).
Do not add those subcategories again. Active collection phases totaled 742.52
seconds (12.38 minutes); offline preparation and validation are excluded. Actual
subscription debit is unavailable. Frozen planning units total 47.598952 for
known calls, with separate unknown reservations; these are not observed charges.
The two preceding calibrations add 38 known calls, giving 455 admissions for
v9–v11 together, not 455 independent rollback trials.

On the same 26 complete quartets, standalone K0 and R0 projections both require
56 calls including their shared prefix and both solve 26/26. Deletion uses
11.40% fewer input tokens and 8.57% fewer planning units, while summed call time
is 3.84% higher. These descriptive totals do not establish a speedup or equal
compute. Lesson policies include a charged writer call. Overlapping standalone
projections cannot be summed as actual study spend.

**Verification.** The [recovery fixture](recovery_fixture_run_replay_audit.json)
and [independent fixture analysis](validation/recovery_fixture_independent_analysis.json)
make zero model calls. All 24 recovery invariant tests pass. The
[test-coverage reconciliation](validation/test_coverage_with_recovery.json)
accounts for all 1,052 core test IDs: 1,038 passes and fourteen optional Docker
skips, combining the earlier full suite and new focused tests without claiming
unchanged tests were rerun. The five [component-inspection tests](validation/component_progress_tests.json)
and two [base-comparison tests](validation/base_progress_tests.json) also pass;
these are additional script tests outside core discovery. Actual Docker replay
is separate. The
[full repository validator](validation/full_validator_after_refresh.json)
passes all 259 check categories; the paper builds with 48 cited sources.

Original source snapshot: `231e2e3fce97ff5e35e7076ea1f3e11ed526faf755b1c58a15a005889fd1bea2`.
Recovery source snapshot: `13327d2f096e1e27c25c96a43c7aae91553bd6de960a55d1a4d97c23c9c83750`.

This study answers a narrower question more cleanly than the old packet-deletion
experiment: facts survive, failed code is substantive, and deletion is separated
from a categorical hint. It still has a strong repair ceiling and an operational
interruption. A future study could compare preserving verified partial fixes
against deleting the whole failed attempt, with a separately frozen, richer
lesson intervention. That study has not been run; no new allocation is opened
by this report.
