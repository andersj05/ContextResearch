# Exploratory patch rollback factorial protocol — 2026-10-13 UTC

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

The separate v9 calibration was too easy: all sixteen initial patches passed
public and private tests, yielding no natural failures. Its main-study gate
remains closed. V10 increased project size before observing any rollback contrast; v11 keeps that task design. This protocol increases project size before observing
any rollback contrast. Each two-file project combines eight components: five
from one leading family and one from each of the other three families. The
component families cover temporal routing, constrained interval scheduling,
revision-ledger accounting, and dependency/version resolution.

Every task contains all eight complete contracts and policies, both original
files, six compound public examples and eighteen disjoint compound held-out
examples. Expected compound answers come from independent component oracles.
Authored reference programs must pass every allocation's public and private
cases inside the pinned container. The v11 cohort and earlier calibrations use different
seeded component pools. Components recur within the v11 allocation (64 per
component family). These are 256 related composite tasks,
not 2,048 independent problems or independent real repositories. Component-local
closures prevent accidental policy sharing. The model may restructure code.

Total replacement source is capped at 32,768 UTF-8 bytes. The complete client
request body has a 4,194,304-byte bound; a runtime suite's input payload has
a 1,048,576-byte bound. The installed client also rejects input longer than
1,048,576 characters; conservatively enforce at most 1,048,576 UTF-8 bytes in
request text. JSON escaping overhead is included in the separate body bound.
The new transport adapter enforces both admission limits as the controller;
older studies' smaller adapters remain unchanged. Before live dispatch, check
full facts plus the initial failed patch and two later reference-sized patches
fit for every task. Constructed pathological patches/outputs can exceed the
client text bound; these are detected before dispatch and never truncated.
Report every capacity disposition. If any capacity stop occurs, the factorial
differences cannot be interpreted as isolated content effects, regardless of
direction. Keep all outcomes and do not replace tasks. No task facts may be
truncated to fit.

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
The generic categories do not name one of the eight components; limited
diagnostic specificity is part of this intervention and may limit its usefulness.

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

## Explicit unplanned departure and fixed exploratory allocation

V10's sixteen-task control-only calibration completed 22 known calls with zero
unknowns or capacity stops. Thirteen initial patches passed. Three substantive
natural patches failed; all three diagnostic lessons were valid and all three
K0 continuations repaired their project correctly on the first attempt. Its
frozen minimum was four eligible failures, so its original main-study gate
fails and stays closed. No deletion or lesson-arm outcomes were observed.

This v11 is an **unplanned exploratory follow-up informed by those control-only
results**, not the original gated v10 allocation or confirmatory evidence. The
launch prerequisite binds the entire original failed gate and audit, verifies
that headroom is its only failure, and verifies the exact observed three
failures and three correct controls. Calling it v11 does not erase the relaxed
feasibility policy. Earlier calibration evidence and source remain immutable.

Freeze exactly 256 NEW study tasks (64 per authored composite family), with
seed 2026101312, before any treatment outcome. The maximum is 3,584 admissions:
one shared prefix, one lesson on eligible failures, and twelve continuation
calls per task. Complete the cohort irrespective of effect direction or
eligible count; no task replacement, automatic retry or sample extension.
Every generated public context must differ from the v10 calibration, and all
reference programs must pass public and private tests in isolated Docker.
No extra calibration is selected to make this gate pass.

Model workers are capped at 32, with at most four grading containers. Ready
continuations take priority over unstarted prefixes, with deterministic frozen
arm order. This is not a guarantee of equal cache or sampling conditions.
Maintain all prior factor, task-fact, three-attempt, privacy, accounting and
capacity-invalidation contracts. Report every planned prefix disposition,
including unknown eligibility. Any capacity or global stop prevents an isolated
content-effect interpretation, regardless of the reported contrast direction.

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
2026101329) are descriptive only and require at least six complete relevant
tasks. No significance-based extension or population-equivalence claim is
permitted. Tasks share authored structure and reused components, including across leading
families; these intervals do not account for all such dependence and are not
population confidence intervals or evidence of independent real repositories. Unknown lesson calls
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
