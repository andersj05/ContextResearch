# What the rollback experiments actually measure

October 13, 2026 UTC. The older v6 comparison measures a policy that deletes
needed task evidence along with failed work. The corrected v7 pilot preserves
the evidence and correctly tests removal of one visible failed record, but it
does not establish a general benefit or harm from rollback. Its lesson usually
retains the failed answer, and its task budget mixes immediate recovery with
success on later stages.

## Where the information loss comes from

In v6, the controller puts each public transaction packet, candidate answer and
check receipt into the same `history` list. After a failure, R writes a lesson
and empties the entire list. It retains the current packet, last accepted
balance vector, feedback and lessons. Earlier packets survive only insofar as
the lesson preserves their content. K retains the original records. This is
an explicit controller deletion, not an observed context-window overflow or
native compaction event. See the [record construction](../experiments/dependency_memory/rollback_challenge_v6/engine.py)
and [inherited deletion](../experiments/dependency_memory/rollback_development_v5/engine.py).

The balance vector is a correct answer to an earlier question, but not enough
state to answer every later question. Later packets can replace or void a
transaction. Updating a balance therefore requires knowing the old winning
record for that transaction: its revision and tie-breaking sequence, accounts,
amount, and void status.

The following is an elementary illustration, not a sampled model result. Both
transactions transfer from account A to account B:

| Earlier history | T1 | T2 | Saved balances | Balances after a new revision voids T1 |
|---|---:|---:|---|---|
| First possible history | 10 | 20 | A = -30, B = 30 | A = -20, B = 20 |
| Second possible history | 15 | 15 | A = -30, B = 30 | A = -15, B = 15 |

Identical saved balances and an identical new packet require different answers.
No reasoning procedure can always recover the correct answer from those inputs
alone. A lesson that preserves only the reconciliation rules does not resolve
the ambiguity. A dictionary retaining the winning record for each transaction
would; winning void records must also survive so older revisions remain ignored.
That is an elementary sufficient-state baseline, not a new algorithm or a
measured model improvement.

The [saved v6 example](../experiments/dependency_memory/results/rollback_checkpoint_v7_2026-10-12/DIAGNOSIS.md)
has exactly this source-removal path: an earlier 26-record packet disappears,
the lesson describes general rules, and the next answer repeats the old balances
while noting that the earlier packet details are missing. A post hoc scan finds
earlier raw packets absent in 188 of 260 R episodes, across 280 received actions.
Some lessons may retain useful facts; this does not mean every one of those
episodes failed or that source loss explains the entire performance difference.

V6's negative whole-policy result remains valid: K solves 122/254 known outcomes
and R 64/258. The deficit persists under every completion of the eight missing
scores. However, it combines source deletion, failed-work deletion, lesson
quality and independently generated trajectories. It does not isolate the
effect of removing a failed attempt from an intact checkpoint. [Original result](../experiments/dependency_memory/results/rollback_challenge_v6_four_actions_confirmation_2026-10-09/LIVE_RUN.md).

## What the corrected pilot isolates

V7 gives both arms every released packet in a separate public dossier and the
same successful checkpoint, feedback, lesson and remaining allowance. Both
continue from one shared naturally failed attempt. K additionally sees that
attempt's candidate, brief note and receipt; R gets an empty `trial` field.

Reinspection of all 16 actual first request pairs confirms that only this field
differs and that both dossiers match the frozen source packets. The
[reproducible inspection](../scripts/inspect_rollback_information.py) and
[saved supplement](../experiments/dependency_memory/results/rollback_checkpoint_v7_2026-10-12/validity_reinspection_2026-10-13.json)
make zero model calls. They supplement the original frozen-source replay.

Both arms already retain the last accepted artifact. The failed candidate never
overwrites it: the engine updates the artifact only after a public pass. R does
not uniquely restore a damaged artifact or environment. Its treatment is removal
of a visible record from the next request.

The treatment is also small: the failed record field has median size 382 UTF-8
bytes, and the entire incorrect six-balance vector appears literally in 15/16
shared lessons. Deleting the original record usually leaves its wrong answer
visible in both arms. This is allowed by the protocol, but limits the question
being answered. A raw record can still have an effect through its note,
formatting, duplication or emphasis; the overlap does not prove that the
treatment has no effect. Bytes and literal overlap do not measure semantic
information loss. [Original pilot report](../experiments/dependency_memory/results/rollback_checkpoint_v7_2026-10-12/LIVE_PILOT.md).

Every action uses a fresh isolated request with no intentionally replayed
private reasoning or prior provider session. Neither arm preserves a private
calculation trace for the other to erase. The comparison concerns visible
context under the declared client access contract; it cannot establish what
happens when rolling back inaccessible reasoning state or native compaction.

## Recovery and final completion are different endpoints

The following recount is post hoc and descriptive. The prespecified primary
endpoint remains final task success.

| Observation among 16 shared failures | Keep record | Remove record |
|---|---:|---:|
| Repairs the failed stage on the first continuation action | 13 | 10 |
| Repairs that stage at some point within the allowance | 14 | 14 |
| Completes all stages within the allowance | 10 | 8 |

There are four candidate actions for three stages. The shared failure consumes
the sole spare action. In all sixteen first request pairs, remaining actions
equal remaining stages. Every subsequent action must therefore pass to finish
the task. An arm can repair the original failure later and still have no action
left for the final stage.

One K trajectory and four R trajectories repair late. Three K trajectories and
two R trajectories repair immediately but fail a later stage. This explains how
the endpoint counts differ; it does not explain the model's internal cause of
any error. Both arms have the facts needed to compute the answers. Mistakes
could involve record selection, arithmetic or use of previous answers, and the
saved visible notes do not identify those mechanisms reliably.

The final R-minus-K estimate is -12.5 percentage points with the original
descriptive bootstrap interval [-37.5, +12.5]. Four terminal pairs disagree,
three favoring K and one R. Neither benefit, harm in a wider population, nor
equivalence follows from this small development pilot. Equal eventual repair
counts also do not prove equal recovery probabilities.

## The next scientific comparison

A more informative mechanism study would preserve all released evidence and
fork a substantive visible failed artifact, such as a proposed patch or explicit
search state, from one shared checkpoint. It would vary raw-record retention
and lesson content separately. A two-by-two comparison could cross keeping or
removing the raw failure with a shared model-written lesson or verifier feedback
alone. The lesson rule must be fixed before new outcomes; no hidden answer or
retrospective correction should enter it.

Measure immediate repair, eventual repair, later-stage success and terminal
success separately. Give enough continuation allowance to observe delayed
recovery, while also comparing complete policies at a matched total resource
budget that charges exploration and lesson writing. A stronger visible artifact
is still not access to private reasoning.

The distinct memory question needs a separate comparison of full packets,
balances alone and a transaction dictionary. A deterministic dictionary is an
upper control for representation sufficiency; it does not establish that a
model can extract and maintain that state reliably. Do not combine that
retention manipulation with branch deletion and then attribute the joint effect
to rollback alone.

The memory comparison remains a proposal. The patch factorial was subsequently
implemented as described below. The separately frozen
[v8 efficiency check](../experiments/dependency_memory/rollback_parallel_v8/PROTOCOL.md)
changes execution scheduling and integrity-check memory use, while retaining
v7's scientific intervention and its limitations. Its completed new cohort has
nineteen eligible pairs, with K=11/19 and R=8/19; a separate prefix is unknown.
The descriptive interval includes both harm and benefit. Those engineering
observations do not establish efficacy or justify an unplanned pooled test.
[Efficiency results and saved evidence](../experiments/dependency_memory/results/rollback_parallel_v8_2026-10-13/README.md).

More parallel calls can
improve throughput; they cannot resolve a mismatch between the intervention and
the intended research question. Earlier evidence and manuscript claims remain
unchanged.


## Fact-preserving patch experiments added later on October 13

[V9](../experiments/dependency_memory/results/rollback_patch_v9_2026-10-13/README.md)
implemented the requested two-by-two comparison, but all sixteen initial model
patches passed both public and private tests, so its main gate stayed closed.
[V10](../experiments/dependency_memory/results/rollback_patch_v10_2026-10-13/README.md)
enlarged the task into an eight-component, two-file project. Thirteen of sixteen
initial patches passed; three substantive executable patches failed public
cases. Ordinary retention without a lesson repaired all three on the next
attempt. The frozen minimum was four failures, so that main gate also stayed
closed. Neither calibration observed a deletion or lesson-arm outcome.

The [saved post hoc failure inspection](../experiments/dependency_memory/results/rollback_patch_v10_2026-10-13/failure_diagnostics.json)
identifies concrete resolver defects: a constraint discovered after visiting a
package was not checked; enabled feature dependencies were omitted; and root
version requirements were not enforced. These are visible code defects and
public input/output discrepancies, not observations of private reasoning.
All three actual K0 contexts retain the complete specification, original files,
examples and initial failure feedback, with no diagnostic lesson.

Those failed diffs occupy 22.6–23.6 kB and describe 7.4–8.8 kB model-written
replacement projects. Removing one discards useful partial implementation
alongside its local error. Some other component outputs were correct on the
shown failed public example; that does not prove those components correct for
all inputs. The next K0 patch passes the full saved suite, but there is no R
observation in these calibrations, so this inspection cannot show that deletion
helps or harms repair.

Here the potential loss is **available computational progress**, not missing
task-defining facts. The deleted code may contain useful derived choices,
implementation details and checks that the model would have to reconstruct.
Because the complete task is still available, the intended solution remains
derivable in principle. Calling this task-information destruction would conflate
an information boundary with the bounded ability to recompute a solution.
Deletion may also remove misleading code or repeated wrong choices; the causal
balance requires the new matched comparison.

The [v11 study](../experiments/dependency_memory/results/rollback_patch_v11_2026-10-13/README.md)
is an explicitly unplanned exploratory follow-up after v10 missed its gate,
with a fresh fixed 256-task cohort chosen before any treatment outcome. It
crosses failed-patch retention with a shared categorical diagnostic lesson,
allows three repairs of the same task, and holds the restored workspace and
all source facts fixed. It is not the original gated confirmation. Diagnostic
hints have five closed categorical fields; they cannot copy a code patch or
full numerical answer. The generic categories also lack component targeting,
so this is a deliberately narrow lesson intervention.

Actual client probes found a separate request-text limit beyond body bytes.
Both are now enforced without truncation. Complete ordinary histories fit; any
capacity stop invalidates an isolated content-effect interpretation while all
outcomes remain reported. This guards against mistaking a client admission
failure for a benefit of deleting information. V11 has now completed as described
below; earlier claims stay intact.


## Completed fact-preserving factorial

The [completed v11 report](../experiments/dependency_memory/results/rollback_patch_v11_2026-10-13/README.md)
records 256 initial calls and 417 total admissions, with 408 known responses
and nine unknowns. Twenty-eight naturally failed executable patches qualified.
Keeping the patch without a lesson solved 27/27 known outcomes; deletion without
a lesson also solved 27/27, with one missing outcome in each condition on
different tasks. Keeping plus lesson solved 28/28, while deletion plus lesson
solved 27/28. This is a strong repair ceiling, not evidence of equivalence or
an established general benefit from either intervention.

The original phase stopped on an internal quota-read RPC error despite available
included usage. A source-frozen amendment, chosen before treatment effects were
inspected, completed only unsent work. All old requests, responses, events and
unknowns remained unchanged. Both phases and all received patches independently
replay. The inherited global stop permanently fails the original isolated-content
interpretation gate. The contrasts are descriptive, with exact finite-cohort
missingness bounds conditional on the 28 observed eligible tasks; they do not
resolve eligibility for seven unreceived initial outcomes.

The [source-level regression inspection](../experiments/dependency_memory/results/rollback_patch_v11_2026-10-13/inspection/sole_failure_source_review/review.json)
shows what deleting useful progress can mean. The only failed terminal repair
was deletion plus lesson on a project whose initial patch had corrected refund
signs but still mishandled dependency versions. The shared categorical lesson
focused on missing dependency constraints. All other arms solved the project on
the next attempt. The failed arm reintroduced the checkpoint's refund bug and
kept it through three repairs: it computed 1998 + 1318 = 3316 where the stated
rule required 1998 - 1318 = 680. Its later patches fixed the dependency error
but left the refund regression.

The refund rule was never removed from actor context. What disappeared was the
actual implementation of an already-computed fix. This supports a precise
information-boundary description: the rollback deletes useful derived work
alongside wrong work, while the task remains solvable from the supplied facts.
It does not prove why the model regressed, or that deletion or the lesson caused
this one sampled outcome; the no-lesson deletion arm succeeded. The categorical
lesson factor also does not test detailed summaries that preserve all repaired
components, or accurate versus inaccurate lesson content.

A [posthoc checkpoint/component check](../experiments/dependency_memory/results/rollback_patch_v11_2026-10-13/base_component_progress.json)
makes the partial-progress claim concrete: all 224 original checkpoint component
instances fail at least one of the 24 frozen terminal cases, while 158 component
instances in the failed initial patches pass all 24. Thus those 158 are actual
new fixes on the saved tests, not correct checkpoint code that deletion leaves
available. First repairs in R0 and RL each introduce seven observed regressions
among those fixes, spread across three projects per condition. No value
regressions are observed in K0/KL, but six/seven component values respectively
are unassessed because of a missing response or whole-project execution failure.
Most observed regressions recover later; three remain in the sole RL failure.
Restricting to the same fixes assessed in both arms gives first-repair K0/R0
regressions of 0 versus 6 among 152, and KL/RL of 0 versus 7 among 151; see the
[matched counts](../experiments/dependency_memory/results/rollback_patch_v11_2026-10-13/component_preservation_pairs.json).
These related component counts are posthoc descriptions, not independent trials
or proof that deletion caused the differences. The 370 diagnostic Docker batches
use exact original public and terminal inputs and make zero model calls.

The next scientific question would be whether preserving verified partial
fixes changes the tradeoff, crossed with a separately specified richer lesson.
That comparison is unperformed and requires a new frozen allocation. The
completed cohort is not extended or retroactively tuned to produce a win.
