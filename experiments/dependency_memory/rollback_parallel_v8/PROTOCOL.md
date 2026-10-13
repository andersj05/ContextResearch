# Parallel rollback runner v8: efficiency validation

Frozen October 13, 2026 UTC under the user's request for more workers and more
efficient execution. This is engineering development. Preserve all v7 sources,
raw evidence and closed allocations. This protocol does not extend v7 for an
effect estimate or repair its known lesson-overlap limitation.

## Changes and invariants

Default concurrency increases from eight to sixteen; the bounded implementation
supports one through thirty-two workers. The model remains `gpt-6-luna`, medium
effort, existing subscription only. No API key, purchase, retry or model fallback.
Each allocation freezes its worker count and complete generation ceiling.

The scheduler admits at most one worker job per slot. As soon as a task's prefix
has been durably saved and its pair contract checked, its continuations become
ready. Ready continuations have priority over unstarted prefixes; frozen
manifest rank breaks ties. No worker waits on a queued child. Ineligible tasks
still receive explicit no-call continuation dispositions. The ledger remains
the authoritative generation cap, identity guard and global-stop boundary.

The v7 action/lesson prompts, checkpoint and public-evidence preservation,
single-deletion treatment and conditional descriptive outcome analysis are
retained. V8 copies the engine only to use new study/call identities; serialized
actor inputs must match v7 for identical task/state. No new public fact, oracle
answer, private reasoning or provider session is introduced. Lessons may repeat
the failed candidate, as they did in 15/16 v7 pairs; this is not a test that
removes every trace of failure.

Full executable SHA-256 checks remain before every generation, using a reusable
1 MiB buffer instead of loading the whole executable. Metadata checks supplement
the full hash; they do not replace it. Do not cache a hash based on timestamp or
size, reuse provider processes/threads, or skip source/account/channel checks.
The inherited check-to-process-launch race is not claimed to be eliminated.
Independent actual-payload loopback cases can run in parallel; each session is
fresh and unauthenticated, with no model generation.

Fresh per-call processes and scratch directories, disabled empty MCP inventory,
pinned declarations, one-answer/usage and one-generation constraints remain.
The v7 clock-plus-answer observation limitation also remains: zero observed tool
events does not prove zero attempted helpers. A later helper result cannot be
consumed by another generation. See the [v7 access contract](../rollback_checkpoint_v7/PROTOCOL.md).
Immutable model revision, provider sampling seed and actual subscription debit
are unavailable; no unsupported provider-internal claims are made.

## Three distinct forms of efficiency evidence

1. **Offline fixed-duration replay.** Read the sealed v7 calls and hold each
   job's first-admission-to-last-completion duration fixed. Compare two-phase
   and pipelined schedules at 8, 16 and 32 workers. Report the old-policy
   reconstruction error against recorded wall time. This assumes unchanged
   service durations and cannot establish provider scaling or rate-limit behavior.
2. **Executed local controls.** Run three repetitions of each schedule with
   sleep durations equal to 0.005 times those recorded service times. Check job
   coverage, dependencies, concurrency and no repeated work. Separately measure
   complete executable-hash equality, local time and allocation in fresh Python
   processes. Synthetic timings and hashing diagnostics are not model trials.
3. **Live subscription checks.** Run the fixed throughput probe below, then the
   new pipelined pilot. They run serially, with no overlapping model work from
   this task. Record every admission, output, usage, unknown and stop. Report
   worker peaks from durable ledger transitions and pipeline overlap from
   admissions before the final prefix completion. The separate monotonic
   scheduler trace is not claimed to be a provider-server timeline.

## Fixed live throughput probe: 64 calls

Use the initial-stage requests for the first sixteen tasks in the frozen new
cohort. Four serial batches each run the same sixteen serialized requests, with
worker counts **8, 16, 16, 8**. These are intentional repeated-prompt measurements,
not retries: every batch has distinct frozen call identities. No task outcome
chooses which call runs next. Exactly 64 possible admissions; no replacements.

Measure each batch's controller wall time, known completions, unknowns, peak
admissions, input/cached/output/reasoning usage and per-call elapsed time. Pool
the two batch times per worker count; report the eight-worker time divided by
the sixteen-worker time only if all 64 calls are known. Retain batch detail.
This is a descriptive local ABBA timing comparison, not a population speedup
or causal guarantee: repeated prompts, cache warming, provider load, output
length, order and time can affect latency. No rollback efficacy claim is based
on these initial-stage answers. Batches never overlap. A missing call remains
missing; systematic faults stop later admissions.

## Fixed pipelined pilot: at most 192 calls

New cohort seed 2026101368, 24 intermediate-profile level-2 revision ledgers,
28 transaction IDs, six accounts, three stages and four actions. Use sixteen
workers. Maximum calls are 192, including shared lessons and unknowns, by the
same `j + 1 + 2(H-j) <= 2H` bound as v7. The combined new live ceiling is
**256 calls**, comprising 64 throughput calls plus at most 192 pilot calls.
These are new identities; do not reopen a previous allocation.

This pilot verifies actual higher concurrency, dependency-ready execution,
channel preservation, complete accounting and independent replay/regrading.
Complete it regardless of effect direction. Report all 24 dispositions and
conditional K/R outcomes descriptively, including missingness. Comparing its
wall time with v7's different cohort is operational context, not an isolated
causal speedup estimate. No sample extension, minimum-pair extension, manuscript
claim upgrade or confirmatory test follows from this engineering allocation.

Unknowns stop only the affected trajectory, keeping their reservations. Prefix
or lesson unknowns prevent dependent continuations. Account, source, isolation,
duplicate-identity, metering or evidence-write faults stop admission globally;
already admitted calls drain. Every launch marker is exclusive.

## Gates and completion

Before dispatch, verify worker counts 16 and 32 offline, exact v7/v8 request
equivalence, persisted-parent scheduling, ready priority, frozen rank, local
unknown handling, global-stop handling, duplicate rejection, all job/call slots,
streamed-hash integrity and current-client 16-way loopback. Freeze source,
cohort, protocol, analysis and probe schedule; run a scripted pilot and replay.

After both live checks, independently reconcile every saved request and ledger
event, verify original task grades, serialized pair contracts, job order,
scheduler trace, peaks, unknowns and sealed hashes. Retain failed gates and all
observations. Faster execution is an engineering outcome, not evidence that
rollback improves answer quality or deployed context compression.
