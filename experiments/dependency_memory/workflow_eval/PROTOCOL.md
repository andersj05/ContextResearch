# Observed repository handoff evaluation — packet v1

September 29, 2026. **Prepared offline; no model evaluation has run.**
The design, grader, prompts and development evidence are frozen by
`packet-lock.json`. Evaluation inputs and a live launch are not yet frozen.
This packet replaces neither historical study protocols nor their results.

## Question and decision

Does checked memory improve correct repository handoffs enough to justify its
full cost compared with direct records and indexed recovery?

The concrete task is to report whether a requested set of repository checks has
current successful evidence, identify the checks still needing work, and cite
the exact supporting runs. Source changes invalidate receipts for the old
snapshot. A newer failed run supersedes an older successful run on the same
snapshot. A build receipt also binds the exact current artifact bytes. This is
a handoff/reporting task; no answer actually publishes or deploys anything.

The available development capture is an actual execution of this repository's
tests, validator and paper build on the recorded clean commit. It is familiar,
locally collected evidence, **not an external or held-out workflow**. Its imposed
memory boundaries and mutated negative controls are constructed interventions.
The artifact/manifest environment remains a separate calibration reference.

## Source intake and split

Use four development episodes and twelve evaluation episodes from separate
actual edit/test/revise/build tasks. Only one development episode is supplied
today. Collect the remaining episodes from a fixed, recorded start date in
consecutive eligible order. Do not choose them for our method's failures or wins.
Record excluded episodes with reasons before seeing any method outputs.

An episode needs a pinned source snapshot, chronological command observations,
two declared handoff checkpoints, and a final snapshot/artifact inventory. A
successful command's output alone is not a repository snapshot. Include failed
commands, stale receipts, unchanged snapshots and cheap recovery when observed;
do not manufacture these and describe them as naturally occurring. No minimum
failure rate is an intake requirement. Short histories that fit the memory cap
remain easy controls and count in the denominator.

Keep an entire change task, its reruns, branches and derived continuations in
one split. Twelve episodes from one repository establish only that workload's
behavior; they are not twelve workflow families. Keep evaluator manifests and
raw evaluation traces outside the implementer's/actor's workspace after intake.
Commit their digests and the intake ledger before evaluation. A hash does not
make data private or establish that it was unseen. Record who inspected what.
If an evaluation episode is inspected while tuning, move it to development and
replace it by the next eligible episode **before launch**, recording the change.

The current capture cannot fill an evaluation slot. Do not relabel the existing
release, schema-transfer or cross-record fixtures as held-out evidence.

## Timing and information contract

1. All arms receive the same public check definitions, tool-result format,
   source observations up to checkpoint A, and the distribution of later tasks.
2. First handoff: at most **4,096 UTF-8 bytes** survive for memory arms.
3. Reveal the same actual intervening observations and requested check scope
   to every arm. Second handoff: at most **1,536 UTF-8 bytes** survive.
4. Reveal the final source-snapshot identifier, current artifact hashes and
   final required-check set. These are public observations, not grader labels.
   Obtain one terminal response per arm. No repair after grader feedback.

The required-check set must be a subset of the scope announced at checkpoint B.
The final artifact inventory reveals hashes, not historical success or run IDs.
Run IDs, revision identifiers, ordering, keys and delimiters count toward memory.
Reject an oversized memory as infeasible; never silently truncate JSON or hide
extra memory in filenames, model sessions, tools or metadata. Store the original
proposal as evaluator-only evidence and count its generation cost.

The actor has no repository filesystem, Git, shell, evaluator files, previous
conversation, opaque reasoning carryover, or unmetered tools. Supply only an
allowlisted serialized request in a fresh documented model context at each
boundary. The implemented offline functions are **not a process sandbox**.
Provider revision, continuity behavior, physical isolation and request logging
must be verified in a separate launch implementation. Supported native
compaction is a future comparison, not an arm silently approximated here.

## Five fixed arms

| Arm | Memory and access | Charged model calls per episode |
|---|---|---:|
| Checked candidate | Model-written receipt table at both boundaries, checked against the available public source; deterministic direct-record fallback on rejection | 2 writers + 1 final |
| Direct records | Hand-written public-rule projection; keep the latest receipt per snapshot/check, then the announced scope | 1 final |
| Indexed recovery | Preserve/index every raw observation, including failed/stale runs; retrieve all observations for the requested checks at final time | 1 final |
| Strong prose | Data-first memory prompt at both boundaries, with the same public rules and caps | 2 writers + 1 final |
| Full history | Entire chronological observation stream and final public state | 1 final |

All arms receive the same original evidence and public rule. Archive access is
an explicit intervention: the memory-only arms cannot read it. Indexed recovery
and full history deliberately have additional retained storage, which is
declared and charged; they do not get evaluator truth. Index all original
observations before the final target is known. Recovery must include later
failures and associated artifacts, not only matching successful receipts.
The full-history reference is not subject to the memory cap; count all tokens.

Candidate certification requires complete relevant receipt tuples (check,
snapshot, run ID, return code and artifact bindings), exact source equality,
and preservation of later failures. At A check all public possible scopes; at
B check the announced scope using only the admitted parent plus new public
observations. Fallback may not reread source deleted at A. If fallback cannot
fit or coverage is unknown, report infeasible. No claim is made that the old
ID-only checker establishes these semantics. The candidate/arm runner remains
to be implemented and frozen on development data; the supplied packet has an
independent terminal grader and a direct-record feasibility diagnostic.

An execution guard is a separate secondary intervention applied identically
to the saved proposals of every arm, using only that arm's admitted evidence
and public rule. Report raw proposal quality and guarded outcome separately.
It may abstain on missing evidence; it may not read evaluator truth. Guard
implementation and its CPU/recovery cost must be frozen before evaluation.
No guard benefit is attributed to compression and no guard is implemented here.

## Independent terminal scoring

The answer is strict JSON with exactly `ready` (boolean), `needs_work` (sorted
check names), and `evidence` (check name to exact successful run ID). A check
needs work when no receipt exists for the final snapshot, its latest receipt
fails, or any artifact bound by that receipt differs from the final inventory.
Evidence contains exactly the current successful checks. Unknown checks,
extra fields, duplicate JSON keys, wrong types and fabricated IDs fail.
An always-abstain/always-rerun policy does not pass a ready case.

The grader reads the immutable complete observation ledger, never the
compactor's extracted facts. It executes no command specified by an input.
Offline controls cover a later failure, stale snapshot, replaced/missing build
artifact, irrelevant observations, malformed answers and fabricated evidence.
These controls check software invariants; they are not independent task trials.

Primary outcome is exact terminal success on **12 paired episodes**. Report
false-ready decisions separately, including reasons and exact evidence mismatch.
Classify failures with an evaluator-only post-hoc evidence audit: source lacks
evidence / lost at first boundary / lost at second boundary / recovery failed /
available evidence misused / ambiguous. Prose sufficiency may be unknown; do
not assign it from substring matching. Diagnostic truth never returns to actors.

## Budget, failures and analysis

There are nine scheduled calls per episode: five final calls and four writer
calls. Four development plus twelve evaluation episodes therefore permit at
most **144 provider dispatches (36 development, 108 evaluation)**. This is a
proposed ceiling, not current spending authority. All prior allocations stay
closed. Proposed provider-charge ceiling: **USD 20**, with no conversion from
subscription credits. A launch must pin an attributable billing route, prices,
per-call input/output limits and worst-case reservations within that ceiling.
Current authorized dispatches and spend are both zero; this package has no
provider client or dispatch command. Missing pricing/usage is unknown, not zero.

Use a deterministic balanced arm order from seed 20260929, unique immutable
request IDs and a ledger written before dispatch. Charge each hypothetical arm
its complete writers even if an implementation shares a proposal. No retries
after dispatch; on transport failure stop and preserve the request and unknown
usage. A later continuation needs a separately frozen plan. Missing paired
answers leave the primary criterion unassessable; report bounded outcomes and
complete-pair exploration without silently changing denominators.

Record input/cache/output tokens in mutually exclusive buckets, measured
provider charges, local CPU and elapsed time, bytes read/written, index creation
and storage duration, retrievals, failed attempts and human setup time. Archive
storage is nonzero even if a price is unavailable. Report raw resource vectors,
cache-discounted and cache-neutral model costs. Price local resources in a table
frozen before evaluation; unpriced resources prohibit a total-cost claim.

Engineering go criterion: compared with **both** direct and indexed arms, the
candidate has no extra false-ready decisions and either (a) at least two more
successful episodes at no greater total priced cost, or (b) at least equal
success with at least 20% lower total priced cost. The improvement must persist
under both cache views. Also report prompting and full-history results. These
are prespecified practical screening margins, not a powered significance test.
Twelve episodes can justify a larger study, not a general superiority claim.

If candidate loses or ties at higher cost, stop expanding the mechanism for
this workload and document the simpler baseline result. If full history fails,
diagnose execution difficulty before attributing failures to memory. If all
arms succeed cheaply or direct records fit easily, retain that finding rather
than shrinking caps after seeing results. Any later harder study is separate.

## Freeze and launch checklist

`packet-lock.json` binds the protocol, prompts, grader, preflight code, tests and
development capture bytes. `python -m experiments.dependency_memory.workflow_eval.packet`
checks these offline and returns a **packet-ready / launch-not-ready** report.
It is deliberately not a model launcher. Freeze changes by creating a new
packet version and explaining the reason; never rewrite a completed run.

Before a launch: acquire/split the remaining real episodes; independently review
the grader; implement all five arms, staged views and diagnostics; test isolation
and recovery; pin model/revision, exact API parameters, prompts, price table,
request/token caps and reservations; freeze evaluation input digests and all
144 request identities (including the development allocation); then obtain the
bounded launch authorization. One completed development capture does not satisfy
any missing gate. Results remain **unperformed**.
