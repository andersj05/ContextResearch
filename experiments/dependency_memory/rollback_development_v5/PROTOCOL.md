# Staged rollback development v5

October 8, 2026. **Preparation only; model outcomes unperformed.** This is a new
development allocation responding to the [v4 evaluation](../../../research/ROLLBACK_MATH_FOLLOWUP_2026-10-08.md).
The user requested all development tasks and efficient parallel launch preparation,
not a live launch in this turn. Old cohorts and unresolved reservations stay closed.

## Cohort and scientific purpose

There are exactly **48 distinct tasks**: four construction families x three
horizons x two difficulty settings x two replicates. Construction seed is
2026100857; every instance has a different deterministic seed. Scheduling and
routing supply 24 mathematics tasks. Event-ledger repair and dependency-resolver
repair supply 24 two-module Python tasks. These are repository-authored tasks,
not benchmark samples. The four families are fixed strata, not 48 independent
families. Difficulty labels are generator settings, not measured Luna ratings.

| Horizon | Maximum candidate actions | Public disclosure stages |
|---|---:|---:|
| Short | 2 | 1 |
| Medium | 10 | 4 |
| Long | 30 | 8 |

The short control discloses all requirements initially and leaves room for a
failed first candidate and one recovery. Medium/long tasks reveal additional
requirements after successful public checks. Each packet contains actual new
constraints or executable examples; there are no padding-only turns. Every
proposal is a complete artifact, and an actor may finish early. `continue`
consumes an action without a candidate. No actor is told to produce a failure.

Difficulty changes job/graph size and programming interactions; horizon changes
the disclosure partition and action allowance. Thus horizon is a joint
timing/computation manipulation, **not an isolated causal effect of text length**.
Record realized steps, stage depth, bytes and tokens rather than calling every
30-action allowance a 30-step trajectory. A short/ceiling/floor outcome remains
in the report. The tasks are calibration evidence even if the new design is easy.

Scheduling requires integer start times satisfying time windows, resource
exclusion, precedence and late coupling constraints. Routing requires a feasible
directed tour, ordered visits, arrival windows and return budget. Any satisfying
answer is accepted. The planted witness is private and never used in feedback.
Routing graders are checked over every permutation; scheduling checks cover
the witness, random assignments and local perturbations, not its whole space.

Coding actors replace `engine.py` and `rules.py`. Ledger requirements combine
money rounding, refunds, discount/tax order, currencies, revision selection,
cutoffs and void/opening balances. Resolver requirements combine version ranges,
transitive constraints, roots, exclusions, pins, feature gates and cycles, with
a deterministic tie rule. Public examples accompany each disclosed rule. Reserved
tests exercise the same declared final specification and never produce actor
feedback. A pass means success on the frozen suite, not universal correctness.

## Three separately analysed tracks

All tracks reuse the same 48 tasks. Their calls and trajectories are repeated
measurements, not additional independent tasks. Default preparation includes all
three; `prepare --tracks ...` can freeze a separately scoped allocation before
any outcomes. Track selection cannot change after the freeze.

1. **Mechanism:** one shared medium-effort trajectory stops at its first
   well-formed public mismatch with at least one candidate action remaining.
   Two independent writers receive the same state: one lesson L, one generic
   summary S. Fork K, R, Z, G, F, KE and RE from copies of that exact state. Each
   continuation uses the remaining action allowance and one draw. Subsequent
   continuation history accumulates normally; there are no further experimental
   deletions in this track. This isolates the initial representation change.
2. **Policy:** K, R, Z, G and F each begin independently from the original task.
   The applicable intervention repeats after each eligible public mismatch.
   All 48 selected tasks count, including initial successes, malformed outputs,
   budget exhaustion, capacity loss and preparation failure.
3. **Memory:** independently started K, R and G policies additionally receive
   a common scheduled compression procedure after passing stages 2 and 4, if
   work remains. This yields zero, one or two imposed cuts depending on horizon
   and actual progress. A writer replaces history and prior memory with at most
   4,096 visible UTF-8 bytes. This track is kept separate from ordinary rollback.

| Arm | Failure-boundary context |
|---|---|
| K | Current task/packet, common environment checkpoint, raw trial, public feedback, L |
| R | Same as K with raw trial removed |
| Z | Same checkpoint and feedback; raw trial removed, no new lesson |
| G | Raw trial and previous memory replaced by S; same checkpoint and feedback |
| F | Fresh solve from original artifact and all **released** public packets; no trial, lesson or failure receipt |
| KE / RE | K/R using the identical mechanically copied public receipt instead of a model-written lesson |

KE/RE distinguish the deletion contrast under an evidence-only lesson from the
contrast under a lesson that can retain uncertainty. They do not certify every
model-written statement. Comparing R to RE changes both lesson content and its
writer; it is secondary, not another isolated deletion effect. Optional semantic
ratings of refuted assumptions remain unperformed; exact candidate recurrence
and violations of earlier released requirements are automatic diagnostics.

The host checkpoint includes the last publicly accepted artifact. It is copied
identically for K/R and KE/RE. Deletion is a visible-history intervention, not
erasure of the artifact or manipulation of private provider reasoning. A failed
candidate is not committed to this environment checkpoint. Both requests in
each primary pair must fit before either is launched. An unusable L prevents
K/R, an unusable S prevents G; other arms keep their prespecified dispositions.

## Access, effort and budgets

Every stage uses `gpt-6-luna`, **medium** effort, through the existing Codex
subscription. There is no API-key, purchase, fallback model or fallback provider.
The alias is mutable; immutable server revision and provider sampling seed are
unavailable. The source seed does not claim provider determinism. Official model
and app-server pages were checked October 8, 2026; actual client behavior is
verified against the installed binary and an unauthenticated localhost endpoint.

The original persistent task contract, current packet and checkpoint artifact
are explicit inputs. Previous requirements remain in visible history/memory;
only F gets the complete released public dossier every call. Future packets,
reserved outputs, reference programs, source seeds, evaluator state and run logs
are inaccessible to the actor. F is an explicitly stronger public-evidence
reconstruction control; its full input cost is charged. It is not called an
irreversible-memory condition. All other actors have no archive retrieval.

Each request starts a fresh process/thread with empty workspace, no previous
turns, no opaque reasoning replay, no files/tools/network capabilities and the
audited fixed global instructions. Source IDs and outcome labels do not reveal
an experimental arm. The controller alone executes submitted Python in a pinned,
network-disabled, read-only Docker container without host mounts. Private
expected outputs stay in the host grader. Tool attempts invalidate the transport.

All arms in a horizon have the same candidate-action cap H. Policy/memory arms
also share an upper bound of 2H total generations: a nonfinal action can require
at most one writer. Writers and compression therefore count in actual total cost;
they are not free. This is an action/call-bounded comparison, **not a verified
equal-token or equal-dollar experiment**. No configurable output-token cap is
established on this subscription route. Complete serialized requests are bounded
by 131,072 UTF-8 bytes, writers by 4,096 bytes, submitted Python by 32,768 bytes.
These byte limits are not token counts. Existing conditional model envelopes and
planning-credit conversion remain declared; actual account charges are unknown.

With all three tracks there are 768 possible jobs and **16,896 task call identities**,
plus eight excluded calibration identities. Identities include unreachable slots;
they are not a prediction of actual use. The state machine permits at most
13,632 task generations plus eight calibration generations: mechanism <=7H-4,
policy <=8H-3 and memory <=6H-3 per task. Calibration must pass before study jobs
begin. No old allocation is reused. No model calls are made by preparation,
verification, preflight mocks or simulation.

## Parallel execution and failure handling

Use four workers by default; one through eight are supported and recorded.
Each worker advances one independent trajectory sequentially. Shared-prefix
children become runnable only after public feedback and common writers are
durably saved. Frozen seeded ordering distributes arms/strata through the queue;
completion order does not select cases. Provider time/order effects remain a
limitation because sampling seeds and immutable revision are unavailable.

A central SQLite transaction reserves each unique call before dispatch and
enforces the global in-flight bound. Save exact allowed requests, typed responses,
usage and whitelisted transport diagnostics. Never retry a dispatched identity.
Unknown dispatch/metering atomically stops all new admission; requests admitted
before that stop are allowed to drain and retain their actual usage. At most the
worker limit can be admitted at once. Undispatched jobs/slots remain explicit.
An exclusive marker on the bundle prevents relaunch into a different output
folder. An existing dispatched ledger cannot be reopened for execution.

Source/client drift, exhausted subscription allowance, unsafe/unavailable code
execution or malformed transport stops the allocation. A received malformed
candidate/writer is an observed interface/policy failure, not infrastructure
missingness and not a retry. A response observation deadline is an unknown
dispatch, never a wrong-answer score. A killed controller is not permission to
resume unknown calls; audit its ledger and preserve unresolved reservations.

## Analysis and subsequent decisions

Primary development contrast is task-paired R minus K, separately for mechanism,
policy and memory, with domain, family, horizon and difficulty breakdowns.
Mechanism is conditional on the observed common public failure; the other tracks
use every selected task. Missing outcomes retain fixed-denominator bounds.
Task bootstrap intervals are descriptive only; no confirmatory p-value, family
generalization or equivalence claim follows. Report all controls and KE/RE.

Include total input/cache/output/reasoning usage, planning credits, call and wall
time, successes, repeated rejected candidates, earlier-requirement violations,
realized action/stage depth and bytes removed. Reasoning is a subset of output.
Mechanism shared preparation is charged once in actual study totals and reported
separately; any per-policy allocation of it is explicitly a projection. Complete
policy episodes are independently run and directly metered.

After the fixed cohort, use **control** results to assess whether recovery is in
the suggested 40-75% range and whether long tasks really produced long histories.
This is a design target, not an exclusion or stopping rule. Report ceiling/floor
or low eligibility honestly; any redesign gets new task IDs and a new freeze.
Do not search for a positive rollback effect by extending this allocation.
Held-out confirmation, powered sample size and native-harness comparison remain
separate future studies.

## Official interface references

- [GPT-6 Luna](https://developers.openai.com/api/docs/models/gpt-6-luna)
- [Codex app-server](https://learn.chatgpt.com/docs/app-server)

These pages describe public interfaces, not inaccessible server internals or
measured subscription charges. The frozen client audit is the operational gate.
