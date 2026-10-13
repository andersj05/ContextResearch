# Staged rollback development v5: interrupted model evaluation

October 8, 2026. **Closed with gaps.** The full 48-task live cohort was not
completed. No complete R/K pair exists in any track, so this run cannot identify
the primary rollback comparison. The saved software checks and replay pass;
those checks do not turn the incomplete cohort into a completed study.

Primary evidence: [live result record](../experiments/dependency_memory/results/rollback_development_v5_2026-10-08/LIVE_RUN.md),
[frozen protocol](../experiments/dependency_memory/rollback_development_v5/PROTOCOL.md),
[analysis](../experiments/dependency_memory/results/rollback_development_v5_2026-10-08/live/analysis.json),
[execution](../experiments/dependency_memory/results/rollback_development_v5_2026-10-08/live/execution.json),
[independent replay](../experiments/dependency_memory/results/rollback_development_v5_2026-10-08/launch_checks/live_audit_result.json),
and [post-run diagnostics](../experiments/dependency_memory/results/rollback_development_v5_2026-10-08/live_diagnostics.json).

## Contract and stop

The user explicitly approved the prepared all-track freeze. It contains 48
repository-authored tasks in four fixed families, three disclosure/action
horizons, two difficulty settings and two replicates per cell: 24 mathematical
planning tasks and 24 two-module Python repairs. The three tracks reuse these
tasks. All requests use `gpt-6-luna`, medium effort and the existing Codex
subscription; immutable server revision and provider sampling seed are unavailable.
The construction seed is 2026100857. Four workers reserve unique identities
centrally. Fresh source/client checks and eight excluded live calibration calls
passed before study admission.

At `2026-10-09T02:33:45.563457+00:00`, policy K action 8 on
`v5-ledger-long-hard-2` became an unknown dispatch. The preserved request has no
accepted response or metering. Only the exception class `DiagnosedProtocolError`
survives; the dispatcher discarded the available whitelisted diagnostic object.
The exact transport cause and whether a generation occurred are unestablished.
The last recorded quota snapshot before a completed call showed 43% weekly use
and ordinary usage allowed; that does not establish the state of the unknown call
or a cause of failure.

New admissions stopped under the frozen contract. In-flight calls drained, and
no identity was retried or reopened. There are 235 metered completions, comprising
eight excluded calibration and 227 study calls, plus one unresolved dispatch.
Thirty-six distinct study tasks were touched (19 math, 17 coding); twelve had no
dispatch. Of 768 jobs, 52 ran, 14 continuations were ineligible after initial
prefix success, and 702 were unstarted. The 16,904 possible call identities
retain 235 completed, one unknown and 16,668 never-dispatched dispositions.
Unused identities include unreachable slots and are not expected consumption.

## Observed outcomes and unidentified contrasts

Known terminal scores below apply to different partial subsets. Each independent
policy/memory arm still has a fixed 48-task denominator. The conditional mechanism
set has one observed eligible prefix, with no continuation scores.

| Track | Arm | Selected/eligible tasks | Known scores | Passes | Partial infrastructure stops |
|---|---|---:|---:|---:|---:|
| Policy | K | 48 | 3 | 2 | 1 |
| Policy | R | 48 | 13 | 13 | 0 |
| Policy | Z | 48 | 8 | 8 | 1 |
| Policy | G | 48 | 6 | 6 | 0 |
| Policy | F | 48 | 4 | 4 | 0 |
| Memory | K | 48 | 4 | 4 | 0 |
| Memory | R | 48 | 4 | 4 | 0 |
| Memory | G | 48 | 4 | 4 | 0 |
| Mechanism | K/R/Z/G/F/KE/RE, each | 1 | 0 | 0 | 0 |

Policy K's one known failure is `invalid_candidate`, an observed artifact-interface
failure distinct from the unknown transport outcome. Policy and memory together
have 46 known episode scores: 45 passes and that one failure. The mechanism track
has two initially successful prefixes and one eligible public mismatch; its seven
continuations were never dispatched. Shared-prefix calls are counted separately.

| Primary R minus K contrast | Complete task pairs | Fixed-denominator missingness bounds |
|---|---:|---|
| Conditional mechanism, observed eligible set | 0 | [-100,+100] percentage points |
| Independent full policies, 48 tasks | 0 | [-70.83,+95.83] percentage points |
| Repeated-memory policies, 48 tasks | 0 | [-91.67,+91.67] percentage points |

No primary mean, bootstrap interval, confirmatory test or paired resource contrast
is estimable. Comparing the raw R=13 and K=2 policy pass counts would confound arm
with which tasks ran before the stop. Unstarted prefixes also prevent identifying
mechanism eligibility over the complete cohort. This is incomplete development
evidence, not evidence for superiority, equivalence or a negative treatment effect.

## Realized trajectories and difficulty

Some long tasks reached eight disclosure stages and a successful policy episode
used nine candidate actions, while the allowance was thirty. The memory track
made 13 scheduled compression calls; its 12 completed episodes passed their frozen
suites, with one further interrupted episode. These are actual model observations
under the declared fresh-thread access contract, not oracle fixtures, but remain
unpaired partial subsets. No policy R failure-boundary lesson/deletion was invoked
in its 13 completed episodes; those episodes therefore do not measure recovery.

K/F controls cover only seven known policy scores across unequal cells; some
cells have no known control result. The proposed 40-75% recovery range and
long-history target cannot be assessed on the complete fixed cohort. Preserve
the observed easy cases and missing cells; do not exclude them or extend this
allocation to seek a favorable effect. A redesign needs new identities and a
separate freeze.

## Metering and accounting

| Scope | Metered calls | Input tokens | Cached subset | Output incl. reasoning | Reasoning subset | Planning credits |
|---|---:|---:|---:|---:|---:|---:|
| Study | 227 | 1,031,469 | 294,912 | 235,312 | 156,041 | 4.8565205 |
| Excluded calibration | 8 | 22,018 | 0 | 4,926 | 3,419 | 0.1166200 |
| Known total | 235 | 1,053,487 | 294,912 | 240,238 | 159,460 | 4.9731405 |

The unknown dispatch retains a separate 4.225 planning-credit reservation. That
reservation is not measured usage, and planning credits are not actual subscription
charges or API dollars. Mechanism common preparation consumed 17 known calls and
0.2792270 planning credits once in the actual study total; no stand-alone-policy
projection is claimed. Task execution wall time was 825.344482 seconds with peak
four active jobs; the launch command including preflight/calibration took
969.095558 seconds. Concurrent offline verification is a timing limitation.

## Verification, reporting limits and next gate

Independent live replay regrades all 52 executed jobs, consumes every one of the
235 known generations, reconciles every job/slot disposition and metering total,
and verifies peak admission four. The preserved archive contains 1,248 files and
12,076,674 uncompressed bytes. Replay and archiving make zero model calls.

The frozen analysis contains a descriptive prefix-label defect: it defaults
unstarted prefixes to `eligible_public_mismatch`, printing 46 under that label.
Actual execution has 45 unstarted prefixes, two initial passes and one eligible
mismatch. The supplemental diagnostics explicitly repair that presentation;
primary eligibility filters and paired denominators remain correct. Preserve the
frozen analysis and source bytes rather than silently replacing them.

All 744 distinct repository tests pass across initial discovery, exact affected
rechecks and nine isolated Docker tests. Original sandbox cleanup/replace errors
and the early recheck import-path mistake remain in the retained logs; the
corrected 61-identity outside-sandbox run passes every affected test. The 26 v5
invariants, all 48 references, 36 client mocks and the 768-job/4,080-call fresh
scripted replay pass. Full scientific validation passes 259 categories and paper
assembly checks 48 cited sources. See the [coverage record](../experiments/dependency_memory/results/rollback_development_v5_2026-10-08/launch_checks/repository_test_coverage.json).

Before any separately approved new live allocation, persist the safe exception
diagnostic before cleanup and arrange earlier paired coverage in the scheduler.
Neither change can recover this unknown outcome or retrospectively complete a
pair. Provider behavior, native compaction, held-out confirmation and actual
charges remain unestablished. Historical reservations, C75 and draft v0.42 are unchanged.
