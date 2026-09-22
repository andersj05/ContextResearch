# Schema-derived memory checks on newly frozen workflow traces

September 22, 2026. The [frozen protocol](../experiments/dependency_memory/schema_checks/FROZEN_PROTOCOL.md),
[saved-evidence audit](../experiments/dependency_memory/results/schema_checks_2026-09-22/analysis.json),
and [reconciled report](../experiments/dependency_memory/results/schema_checks_2026-09-22/reconciled_report.md)
document a small test of automatic retention across two memory boundaries. The
terminal grader and six evaluation traces were committed in `36b7748`; the local
price assumptions in `284405d`; the extractor, tests, and 72-call launcher in
`75ab94f`. No evaluation model answer was available when those commits froze.

## What was tested

The user chose newly constructed traces because the repository had no untouched
retry, CI, or data-job traces. Two development and two evaluation traces were
generated for each of retry handling, CI handoffs, and multi-stage data jobs.
The evaluation values and late events were frozen as files with hashes before
extractor development; the schemas and obligation families were shared across
development and evaluation. These are held-out **instances**, not held-out
schema structures or observed production incidents.

Each trace contains four tool results. At the first boundary, 2,600 UTF-8 bytes
can survive. Two candidates are then disclosed, and 1,300 bytes can survive the
second boundary. Only afterward does the selected target and a late event become
visible. Two continuations per trace yield 12 paired terminal cases. The final
model must give the exact action, target ID, and outstanding work set; `inspect`
or malformed output fails. A fresh model process/thread handles each request,
with no archive, prior reasoning item, or evaluator file in the accepted
response's inputs. Indexed recovery is separately declared and metered.

Tool schemas mark `format: opaque-id`, `x-reference`, and `x-ephemeral` leaves.
One generic extractor retains the other scalar leaves as field/row tables. Its
two checks compare the exact annotated IDs and each reference's owner, field
path, and value before deleting the source at each boundary. Development
mutations establish that shortened IDs and references reassociated with another
owner are rejected. The second check reads only the bounded parent memory.
Unannotated state is deliberately **not certified** by these narrow checks.
The automatic arm constructs and verifies its own deterministic table; it does
not audit or repair arbitrary model-written prose. Missing schema annotations
produce unknown coverage. The hand-written direct arm uses family-specific
minimal field lists and excludes the human cost of designing them.

## Frozen matched comparison

GPT-6 Luna medium made all 72 scheduled managed-subscription calls. The
saved-evidence audit reconciles 230,898 input tokens (100,352 cached), 15,971
output tokens (10,558 reasoning), and **0.5510905 planning credits**. This is
dated token-based planning cost, not attributable account debit. Both model
memory writes and every terminal call are counted. The strong data-first prompt
clipped none of its six parent or six child memories.

| Arm | Exact failures / 12 | Model calls | Model credits | Experimental total credits* |
|---|---:|---:|---:|---:|
| Stronger prompting | 0 | 24 | 0.2537065 | 0.25370650 |
| Automatic schema table + checks | 0 | 12 | 0.0725445 | 0.07312518 |
| Hand-written direct records | 0 | 12 | 0.0667650 | 0.06701018 |
| Indexed recovery | 0 | 12 | 0.0628880 | 0.06299562 |
| Full history | 0 | 12 | 0.0951865 | 0.09561754 |

*The precise [reconciled table](../experiments/dependency_memory/results/schema_checks_2026-09-22/reconciled_report.md)
uses preregistered synthetic prices of 0.0001 credit per local CPU second and
0.00000001 per locally read byte. The launch's Windows `process_time_ns` timer
quantized short local operations to zero. A separate, post-run, high-resolution
[development-trace calibration](../experiments/dependency_memory/results/schema_checks_2026-09-22/local_calibration.json)
estimates at most 2.1 ms of extractor/check work across six traces using the
largest measured batch for each family. The displayed automatic total includes
that sensitivity adjustment. This is not a per-run CPU measurement or full
production cost. Raw source and recovery bytes remain separately recorded.

The matched allowance is the prompting arm's 0.2537065 experimental credits;
all arms fit. Automatic retention uses fewer model credits than prompting, but
hand-written direct records and indexed recovery are cheaper. With **zero
prompting failures**, the preregistered primary condition of *fewer terminal
failures at equal or lower total measured cost* is **not met**. The automatic
arm ties direct records in terminal outcomes. All 12 cases are correlated,
constructed continuations; no significance or production-benefit conclusion
follows from the tie. Claims about novel automatic identification of critical
facts remain unestablished.

## Interpretation and next discriminating test

This run establishes that the generic annotated-schema table fits the imposed
limits and preserves the tested IDs/roles on new values without model memory
writers. It does not establish that the checks improve outcomes when strong
prompting is already correct. The prior four-history development failures did
not transfer to these easier frozen cases. The self-check of deterministic
extraction validates serialization invariants, but a test of checking
model-proposed memory still needs to run.

A next test would freeze external tool traces before inspecting their outcomes,
hold out at least one schema/obligation structure, and include examples where
the annotated fields are incomplete or misleading. It should compare a checked
model proposal with direct schema extraction, hand-written records, indexed
recovery, and strong prompting under a total cost allowance. That design must
grade real terminal obligations and account for the annotation and adapter
authoring work. These are future requirements, not results of this run.
