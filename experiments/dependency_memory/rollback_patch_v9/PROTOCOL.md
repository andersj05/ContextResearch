# Patch rollback factorial protocol — 2026-10-13 UTC

Status: frozen by each allocation's source snapshot before model dispatch.
This is a new development experiment. No old allocation or observed outcome is
relabelled as evidence from this protocol.

## Question and scope

Does deleting a model's failed code patch help it repair the same project when
every task fact is preserved? Does a diagnostic lesson help independently, and
does its effect depend on whether the failed patch remains visible?

The intervention changes explicit visible context. All arms start from the same
original two-file checkpoint. Thus this measures deletion of rejected work with
workspace restoration held constant. It does not measure provider-private
reasoning rollback, native session compaction, or restoration of a damaged live
repository. The project checkpoint is authored existing code with defects, not a
previously accepted model solution. Models emit complete replacement files; the
retained failed work is their actual unified diff against that checkpoint.

## Tasks and eligibility

Four authored Python families cover temporal routing, constrained interval
scheduling, revision-ledger accounting, and dependency/version resolution. Each
task contains a complete public contract, both original files, six public
examples, and eighteen disjoint held-out examples generated from the same
rules. Explicit policy variations and seeds change the instances. Authored
reference programs and separate small-instance oracles must agree on every
allocation's cases when the programs run in the pinned container.

The model is asked to produce its best repair and is never instructed to fail.
Exactly one shared initial attempt is made per task. An eligible fork requires
two valid allowlisted replacement files, successful executable output with a
public test mismatch, at least four changed nonempty diff lines, and a changed
Python AST after excluding source positions and standalone string expressions.
The host parses bounded source text for this check but never executes it. Malformed
outputs, syntax/runtime failures, timeouts, unchanged or insubstantial patches,
and public passes are recorded outside the natural executable-failure cohort.
No task is replaced to increase the number of eligible forks. The number of
changed lines and AST structure are operational thresholds, not proof of semantic difficulty;
saved patches permit substantive inspection.

## Independent factors

| Arm | Initial failed patch | Diagnostic lesson |
| --- | --- | --- |
| K0 | Retained | Absent |
| R0 | Deleted | Absent |
| KL | Retained | Present |
| RL | Deleted | Present |

Each arm receives exactly the same complete public task, original checkpoint,
public failed-test feedback, and three continuation attempts. Arm names are not
shown to the model. First continuation requests must be byte-identical after
normalizing only `failed_work` and `lesson`. This equality is checked against
the authoritative public task too, so equally corrupted arms cannot pass.

One independent lesson call sees the same failed patch and public feedback.
Its five closed categorical fields identify focus, suspected file, diagnosis,
next check, and confidence. The same result goes to both lesson arms. No free
text, code, exact solution values, extra fields, or full patch can be placed in
this channel. There are 9×4×9×6×3 = 5,832 possible lessons (less than 13 bits of
categorical choice); JSON framing bytes are not an information-bit measure.
The lesson intentionally communicates derived information about the failure.
This tests categorical diagnostic hints, not unrestricted prose reflection.

Deleting the failed diff does not delete its public feedback: `initial_feedback`
retains it throughout, separately from the latest receipt. Later patches and
feedback produced by each arm are retained normally. There is one intervention
at the matched fork, not repeated deletion after every failure.

## Repair budget and grading

Every arm can submit up to three further complete patches on this one fixed
task. Every received malformed/capped action consumes an attempt. The first
public pass stops that arm. Hidden results never influence prompts, retries,
eligibility, or stopping. The primary outcome is held-out correctness of that
first publicly accepted repair; an arm that exhausts its allowance without a
public pass scores zero. A public pass that fails held-out cases also scores
zero. Public recovery by attempt 1/2/3, held-out correctness of other submitted
patches, repeated candidates, patch size, and resources are descriptive
secondary diagnostics. An earlier patch passing hidden cases while failing
public cases is not a successful repair.

The trusted host checks expected JSON values using exact typed serialization.
Candidate code only runs in a fresh Python 3.11 image pinned by digest, under
nonroot, read-only, network-disabled, no-host-mount isolation, bounded memory,
CPU, time, processes and output. One suite executes in one fresh container; all
inputs in that suite and within-suite Python module state are available to the
program. Expected answers remain outside the container. Public receipts can
show the first differing public case; private receipts contain aggregates only
and never enter model context. At most four grading containers run at once.

## Fixed calibration and main allocation

1. Freeze 16 calibration tasks (four per family), seed 2026101391, with a maximum
   of 80 admissions: initial attempt, one lesson on eligible tasks, and three K0
   repairs. No R or lesson-arm continuations are run, and no factorial effect is
   estimated. Feasibility requires all sixteen prefixes known, 4–13 eligible
   natural failures, at least one K0 repair passing public and private tests,
   all eligible lessons valid, no global stop, and successful independent replay
   of intact live evidence. This small control-only gate is not a power guarantee.
2. Only if the gate passes, freeze 256 new study tasks (64 per family), using a
   different split and seed 2026101392. The absolute maximum is 3,584 admissions:
   one prefix, one writer and twelve continuation calls per task. Complete the
   fixed allocation irrespective of effect direction or eligible count. Do not
   add tasks after examining outcomes. Failure of the calibration gate stops
   this main allocation; any later redesign requires a separately frozen study.

The two allocations admit at most 3,664 calls combined. Actual admissions should
be lower because public passes and ineligible prefixes end trajectories.
Model workers are capped at 32. Continuations become ready after their own
prefix is saved, with arm order shuffled deterministically before outcomes and
ready continuations preferred over unstarted prefixes. This avoids a global
prefix barrier; it does not equalize provider sampling or cache conditions.

## Estimands and uncertainty

Among the fixed cohort's eligible natural failures, report all four success
rates and these within-task contrasts, where symbols denote binary outcomes:

- Deletion without lesson: R0 − K0; deletion with lesson: RL − KL.
- Lesson with retention: KL − K0; lesson with deletion: RL − R0.
- Main deletion: ((R0 − K0) + (RL − KL))/2.
- Main lesson: ((KL − K0) + (RL − R0))/2.
- Interaction: (RL − KL) − (R0 − K0).

Report exact finite-cohort best/worst missing-outcome bounds for each contrast.
Paired task bootstrap intervals (10,000 draws within family, frozen seed
2026101399) are descriptive only and require at least six complete relevant
tasks. No significance-based extension or population-equivalence claim is
permitted. Tasks within an authored family share structure; a task bootstrap
does not make them independent real-world repositories. Unknown lesson calls
leave KL/RL missing while K0/R0 can continue. Do not drop these tasks from the
eligible denominator or assign missing outcomes zero. Unknown prefix calls
have unknown eligibility and are reported separately.

## Model, access and accounting

Use gpt-6-luna, medium reasoning, through the existing signed-in subscription.
The client/model catalog is checked and client hash recorded at launch. An
immutable provider weight revision and provider sampling seed are unavailable;
record that limitation rather than inventing either. Every call uses a fresh
isolated provider thread and process with no prior session, task filesystem,
archive, evaluator, or private reasoning replay. Retain the pinned client's
documented clock/helper observation limitations; do not claim inaccessible
server internals are audited. Actual serialized action, lesson and four-arm
contexts plus parallel dispatch are checked through unauthenticated loopback
before any live generation.

Every admission, including unknowns and lesson calls, counts against the frozen
cap. No automatic retries, repeated identity, task replacement, model fallback,
API-key use, or purchase. Shared prefix/writer calls are counted once in actual
spend. Standalone policy projections duplicate the common prefix; lesson arms
include the writer while no-lesson arms do not. Equal actor-attempt allowance
does not imply equal total compute, tokens, latency or dollars. Report metered
tokens, caching, wall time and unknowns; planning credits are not actual charges.

Raw requests, received responses, public/private grades, contexts, frozen
source, ledger, scheduling trace and unmatched dispositions are retained.
Independent replay reconstructs every admitted request and reruns all received
patches in isolated containers without contacting a model. Offline fixtures
that deliberately fail then emit reference code are labelled as controller
tests and excluded from empirical results.
