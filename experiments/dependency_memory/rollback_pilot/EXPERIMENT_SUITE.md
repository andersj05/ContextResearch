# Rollback experiment suite

October 8, 2026. Design for review, version 0.2. All stages below are unperformed.
Start with the [review handoff](../../../docs/ROLLBACK_REVIEW_HANDOFF_2026-10-08.md).
The [pilot protocol](DRAFT_PROTOCOL.md) governs the first model comparison;
this document defines its place in the larger investigation.

## Questions and sequence

| Stage | Question | Design | What it can establish |
|---|---|---|---|
| E0 | Does the controller implement the intended intervention? | Offline render, grader, isolation, accounting and analysis checks | Engineering validity only |
| E1 | Can Luna use these interfaces within the caps? | Eight calibration requests on disclosed fixtures | Interface feasibility, not accuracy improvement |
| E2 | Does deleting the failed branch help recovery? | 24 initial tasks, four conditions, two continuations per condition | A development estimate conditional on publicly detected failure |
| E3 | Does the deletion effect repeat away from development tasks? | New fixed cohort, K versus R, one continuation each | A prespecified confirmation within the tested task distribution |
| E4 | Does a complete policy help at a fixed budget? | Five policies starting from the original task | End-to-end success and expenditure under a declared selector |
| E5 | Can the model decide when and where to roll back? | Automatic versus model-chosen rollback; native policy as a separate comparison | Value and failure modes of autonomous context management |

E1 and E2 share the proposed 320-call / USD 5 API envelope. E3 through E5
require separate frozen cohorts and allocations. No stage starts automatically
because an earlier one has completed. Negative and inconclusive outcomes remain
useful research outcomes; progression is not conditioned on obtaining a win.

## E0 offline acceptance

Build against the [execution contract](EXECUTION_CONTRACT.md), then demonstrate:

1. K and R have identical instructions, task, checkpoint, feedback and lesson.
   Only K contains B. Use fixed synthetic summaries for the routing test so an
   irrelevant B-only canary cannot legitimately migrate through L.
2. Malicious text in trial artifacts cannot alter renderer fields, roles, task
   identity or permitted inputs. No private grading field can be serialized.
3. Exact math graders agree with a separate exhaustive formulation. Check valid,
   invalid, out-of-domain, duplicate-key and malformed candidates.
4. The isolated coding runner grades reference and intentionally incorrect
   fixtures consistently, bounds resources, and denies undeclared channels.
5. Every dispatch has a prior reservation and stable identity; ambiguous outcomes
   stay reserved. A simulated crash cannot cause an automatic repeat dispatch.
6. Synthetic outcome tables reproduce known paired differences and missing-data
   bounds; a generic-summary failure does not remove valid K/R observations.

Freeze source, task and container hashes after these checks. This design packet
contains an illustrative fixture, not an implemented controller or E0 pass.

## E1 calibration schedule

Use two separate disclosed engineering tasks: the two-variable example in
[the fixture](review_example.json), and a small stdin/stdout sum program.
They never enter E2 or any held-out cohort. Deliberately incorrect branches in
calibration are fixtures, not naturally observed reasoning failures.

| Call | Input and requested output | Acceptance |
|---|---|---|
| 1 | Math checkpoint | Parseable checkpoint schema; task preserved |
| 2 | Coding checkpoint | Same interface in the other domain |
| 3 | Math trial from a fixed checkpoint | Candidate or explicit no-candidate status |
| 4 | Coding trial from a fixed checkpoint | Complete Python artifact or no-candidate status |
| 5 | Lesson from the fixed failed math branch | Schema and 1,024 visible-token cap |
| 6 | Generic summary from the fixed failed code branch | Schema and the same visible cap |
| 7 | K continuation on the math fixture | Parseable candidate; correct serialized input and usage |
| 8 | R continuation on the coding fixture | Parseable program; correct serialized input and usage |

Freeze both coding fixture bytes and all eight rendered requests during E0.
These eight calls exercise formats; K/R across different calibration tasks is
not an outcome comparison. Fresh independent requests use the proposed full
token limits. Do not intentionally exhaust the entire output allowance just to
test cap enforcement: audit the actual request field and metering.

Any missing usage, request mismatch, unsafe executor behavior, unsupported model
setting, provider-incomplete response or unusable format halts progression.
Preserve the call and revise the protocol before allocating another calibration.
A wrong but properly formed answer does not itself fail interface calibration.
Eight calls cannot certify rare transport failures or a server's hidden state.

## E2 conditional recovery pilot

The four conditions are K = C+B+F+L, R = C+F+L, Z = C+F,
and G = C+F+S. The [task specification](TASKS_AND_GRADING.md) fixes the
proposed construction and selection rules. The [analysis plan](ANALYSIS_PLAN.md)
defines denominators, outcomes and interpretation.

Each of 24 tasks uses at most one checkpoint call, two branch calls, one lesson,
one summary and eight terminal calls: 13 maximum. Success without a public failure
is retained in the cohort but does not generate a manufactured rollback episode.
Both domains have 12 tasks. Two terminal draws measure sampling variation on one
task; they do not create 48 independent tasks.

At completion, inspect interface failures, eligible-task counts, length removed,
lesson errors and paired outcomes. Fewer than six eligible K/R tasks in either
domain makes that domain primarily a feasibility result. Six is an operational
screen, not a power threshold or statistical claim. If tasks are too easy, change
the next development cohort in a dated amendment; never replace completed tasks.

## E3 held-out confirmation

Freeze a new cohort after E2 and before inspecting its model outcomes. Exclude
calibration, pilot and pre-exposed benchmark tasks and near duplicates. Hold out
generator seeds and problem identities; this is not a claim of unseen training
data. Keep the E2 task rules unless a separately declared transfer experiment
changes them.

Use K and R only, one terminal draw each. Maximum preparation is one checkpoint,
two branch calls and one common lesson, followed by two continuations: six calls
per initial task. Pair within each task; grade after both continuations. The
primary effect remains conditional on a public failure and a usable common
lesson. Record all initial-task dispositions and preparation costs.

Choose cohort size using an explicit target before the held-out launch. Proposed
target: detect a 10 percentage point recovery difference with 80% power, treating
math and coding as two primary tests and using two-sided alpha 0.025 per domain.
For planning, let q be the chance that paired binary K/R outcomes disagree and
e be the initial-task eligibility rate. A normal approximation is:

```text
n_eligible ~= (2.2414 + 0.8416)^2 * (q - 0.10^2) / 0.10^2
N_initial  = ceiling(n_eligible / e)
```

This follows from Var(R-K) = q - delta^2 for binary pairs. It is an approximation,
not a certified power result. For q=0.5 and e=0.5 it suggests about 466 eligible
pairs and 932 initial tasks per domain. A round 1,000 initial tasks per domain
would allow 12,000 task calls, plus eight new calibration calls, with a conditional
model-token ceiling of USD 147.554304 at the current design's caps and rates.
That scale is a planning illustration, not the selected E3 sample or allocation.

Evaluate power across plausible q and e, including values less favorable than
the small pilot estimates, with the actual exact test before freezing N. If the
eligible dataset pool is too small, choose a larger prespecified pool or report a
precision-limited study. Do not duplicate tasks to reach the nominal sample size
or collect until a significant result appears.

## E4 complete policies at a common resource budget

Proposed development cohort: 60 new tasks, 30 per domain, preserving the three
families/difficulty strata. Run each task independently under five policies.
All policies receive the same original task, model settings, public checker and
selector. Each owns its trajectory; no shared winning branch or lesson is injected.

| Policy | Context after a failed candidate | Additional work charged |
|---|---|---|
| A ordinary repair | Keep the accumulated visible history and feedback | No writer |
| K repair with lessons | Keep history and append a new lesson | One lesson call per detected failure |
| R rollback with lessons | Keep the pre-trial checkpoint, feedback and lesson | The same writer interface; discard that trial suffix |
| G generic compaction | Keep the checkpoint, feedback and generic summary | One compactor call per detected failure |
| I independent retries | Original task only for each new attempt | No previous candidate, feedback or lesson enters the actor |

For this first complete-policy comparison, every solver call emits a candidate;
the persistent checkpoint is the original task. Label R as restart-with-lessons
in this setting. Do not claim preservation of substantial prior progress. E5
introduces movable checkpoints after this simpler policy comparison is understood.

For K/R, each writer sees that policy's current active state, new candidate and
public feedback. R's next active state is original task plus latest feedback and
the newly accumulated lesson; the writer can preserve useful earlier lessons.
G applies the analogous recursive summary. A/K retain all prior visible records.
All active contexts have the same 32,768-token cap. Reaching it ends that policy's
episode with a capacity disposition; no undeclared automatic compaction occurs.
Report cap-limited results separately from cases in which every policy fit.

Propose USD 0.10 of model usage per task-policy episode and a safety limit of
24 generation calls, including writers. Reserve each call's worst-case cost
before dispatch, then release only verified unused reserve. All policies follow
the same admission rule. Report stranded budget caused by reservation and any
call-cap binding; an equal ceiling does not mean identical actual expenditure.
300 task-policy episodes give a USD 30 episode ceiling; propose USD 31 including
eight calibration requests. The request ceiling is 7,208. Local execution costs
and elapsed time are separate reported resources.

Evaluate every candidate on all public tests. Stop at the first full public pass,
or when no further call fits. A controller stores the candidate with the largest
public-test pass count, breaking ties by earlier generation; this deployable
selector applies to all five policies. Its candidate archive is a declared
channel used only for terminal submission, never fed back to the actor. Also
report final-actor-candidate performance. Private tests never select a candidate,
stop an episode or choose a policy. For math, the public exact checker already
establishes validity; label this feedback advantage when comparing domains.

Primary E4 contrast is R versus K in selected terminal success at the common
budget. R versus A/G/I are prespecified secondary comparisons; report all, not
only the weakest baseline. This 60-task stage is development, not a powered
universal-efficiency claim. Any confirmatory replication needs its own fixed size.

## E5 checkpoint choice and native comparison

Proposed development cohort: 60 new tasks with the E4 strata and per-episode
resource rules. Three controller policies each emit the same concise action
record alongside a candidate: KEEP, SAVE_CHECKPOINT, or ROLLBACK(checkpoint_id).
All candidate checks use the same public evidence.

- **Append:** retain history; action suggestions are logged but not enacted.
- **Automatic rollback:** enact SAVE_CHECKPOINT at a call boundary; roll back to
  the newest saved checkpoint after an objective public failure. Ignore a proposed
  rollback without that evidence.
- **Chosen rollback:** enact a model-selected rollback to any saved checkpoint
  before the candidate's branch, with a charged lesson. It may act without an
  objective contradiction, which is part of the treatment.

The model sees IDs and concise descriptions of available checkpoints, not all
archived payloads. Restoring one exposes its saved text and must be logged and
costed as declared archive access. A replacement lesson may retain evidence from
the discarded suffix. Checkpoints contain visible state only, never opaque
reasoning. Maintain at most four checkpoints; evict the oldest non-root one on
overflow under the same rule in both rollback policies.

Use the call-boundary action interface in [POLICY_PROMPTS.md](POLICY_PROMPTS.md)
and freeze its implementation and prompts before launch. Cap each policy at three
rollbacks, 24 total calls and USD 0.10 per episode. End on a full public pass,
budget/cap exhaustion or explicit final submission. The three policies yield
180 episodes and a USD 18 episode ceiling. Together with eight calibration calls
and the 12 diagnostic calls below, the request ceiling is 4,340 and the model
usage reservation is at most USD 18.24576; propose USD 19.

Measure terminal success, unsupported rollbacks without objective contradiction,
rollback frequency/depth, repeated failed routes and information loss. The main
loop stops on a public pass, so it cannot measure abandonment of an already
correct complete answer. Correlations between long branches and failure do not
prove that branch length caused the failure.

Add a separately reported 12-call decision probe: six math and six coding fixtures,
with three correct and three incorrect completed candidates in each domain.
These are authored diagnostic fixtures, not natural model branches. Their labels
come from exact or reserved grading during preparation and are withheld from the
actor. Supply the task and candidate without a correctness receipt; ask once
whether to KEEP_FINAL or RECONSIDER, with a brief reason. Do not execute a repair
or provide feedback. Measure correct candidates rejected and incorrect candidates
accepted, with their fixed denominators. This probe tests judgment under withheld
feedback, not the success or cost of the main public-feedback policy. Never pool
its decisions with the 60-task policy outcomes.

A **native-harness** arm is a separate practical comparison on the same new tasks
only after its model identity, tools, opaque state, accounting and token controls
are documented. Add at most 60 episodes and USD 6 of nominal episode budget only
under an enforceable route-specific contract. It is outside the USD 19 proposal;
subscription credits cannot be substituted for these dollars. Report the complete
system difference, not an isolated visible-context effect. If native limits cannot
be matched, report a resource curve or leave this comparison unavailable.

## What remains outside the first suite

Very long contexts, repeated delayed-dependency compression and competition-math
transfer require additional designs. In particular, E2's naturally short branches
do not test deleting 100k tokens. Add length experiments using genuine longer
trajectories; fabricated repetitions are stress fixtures, not natural reasoning
evidence. MATH-500 must use problem-derived checks or an explicitly labeled
correctness-oracle condition. None of these transfers is funded by the pilot.
