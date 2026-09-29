# Luna 6 on executed workflows with narrower queries

September 29, 2026. The live schedule was frozen at `d7cb8e8`.
**Original run stopped; separate extension pending analysis.** Request 17
(`tests_later_failure-prose-final`) timed out with no answer or usage event.
Sixteen answers cost 0.1742595 known planning credits; the failed request keeps
its 7.65-credit reservation. The [separate continuation](../experiments/dependency_memory/workflow_executed_continuation/CONTRACT.md)
can dispatch only the 91 untouched identities within the original combined
20-credit ceiling. The original complete 12-case criterion is unassessable.

## Why this follow-up

The [previous development comparison](WORKFLOW_LUNA6_COMPARISON_2026-09-29.md)
used one real repository capture and three mutations of its metadata. Every
terminal question requested all three checks. The direct representation was
cheap and successful, while indexing offered little opportunity to narrow the
history. This separate follow-up keeps all five methods and byte caps, varies
check scope, and executes deliberately controlled source/runtime changes.

## What was executed

The [capture](../experiments/dependency_memory/workflow_executed/capture.json)
contains twelve scripted scenarios from one small Python project: an arithmetic
function and tests, a source/documentation/readiness-marker check, and a Markdown
and HTML build. All 48 observations come from subprocess executions. Seven runs
actually return failure. Capture wall time is 8.2420484 seconds; collector CPU
time is 0.5 seconds, excluding child-process CPU. Raw stdout/stderr total 19,099
bytes without padding. Source/runtime bytes and generated artifact contents are
retained with hashes. There are fifteen source snapshots across the twelve cases.

The scenarios cover unchanged success, later test failure, recovered tests,
later repository-check failure, recovered repository check, replaced HTML,
missing HTML, untested new source, partially checked revision, late selection
of an older source, an irrelevant failed check, and fail/recover/fail on unchanged
source. The collector never substitutes a fabricated exit code or hash. An
offline test reexecutes all 48 source/runtime combinations and verifies return
codes and artifact bytes; a separate expected-work table checks the grader.

These are **constructed workload scenarios with observed execution outputs**.
They are not naturally occurring incidents, separate workflow families or
untouched evaluation data. The author inspected all cases. This work does not
fill any of the original packet's twelve real-workflow evaluation slots.

## Methods and timing

Checked and prose methods each use two writers and a final call. Direct records,
indexed raw recovery and full history each use one final call. Thus the fixed
schedule contains 108 model requests. All writers count toward cost.

At the first boundary, memory-only methods retain at most 4096 UTF-8 bytes. New
observations and a possible-check scope then arrive. At the second boundary,
1536 bytes survive. Only afterward does the final source/artifact inventory and
a subset of that check scope arrive. The source identity is not revealed early.
Both writers get an explicit explanation of scope. Checked/direct keep latest
receipts for the scoped checks on every still-possible source, using the bounded
parent and new observations only. Their fixed direct child tables range from
203 to 1185 bytes, so none requires rejection for capacity in this casebook.

Indexing retains every original observation and retrieves every run for the final
requested checks. Eleven final queries request fewer than all three checks.
Failed and stale runs remain in the index; full history reads every run. This is
an explicitly declared archive advantage, with storage and retrieval measured
separately. The terminal grader scans the complete raw ledger independently of
the memory policy. Null evidence fields are only a provider-schema serialization
detail; the host removes them before exact grading.

## Limits

The decision rule asks whether the latest recorded check on the final source has
successful evidence with matching artifacts. Source hashes exclude explicitly
declared runtime state. This tests that reporting contract, not arbitrary source
correctness or the claim that an old receipt predicts every later environment.
No autonomous task-solving or native-compaction result is measured.

The mutable `gpt-6-luna` alias runs at medium reasoning and default Standard tier
through the same pinned client/profile as the prior pilot. A fresh four-control
no-auth audit preceded dispatch. Every call gets a fresh process, empty cwd and
ephemeral thread; the declared wrapper/clock registry remains visible, while
accepted outputs have no tool use. No internal provider-erasure claim follows.

The allocation is separately bounded to 108 calls and 20 planning credits with
7.65 reserved per single in-flight call, no retries and no model fallback.
The dated rates remain 2.5 input, 0.25 cached input and 12.5 output credits per
million tokens. These are token-derived planning costs; actual account debit,
human setup and fully monetized infrastructure cost remain unknown.

Local read/write counters measure serialized inputs and outputs of memory/index
operations, not operating-system I/O. Index byte-duration follows the interleaved
study schedule, including other arms' calls, rather than an isolated deployment.
These resource vectors must not be treated as measured production prices. Do
not pool this denominator with the previous pilot or interpret a different score
as an improvement caused by a model or prompt change: the casebook has changed.

## Evidence and reproduction

- [Frozen contract](../experiments/dependency_memory/workflow_executed/CONTRACT.md)
- [Launch manifest](../experiments/dependency_memory/results/workflow_executed_2026-09-29/manifest.json)
- [Fresh transport preflight](../experiments/dependency_memory/results/workflow_executed_2026-09-29/preflight.json)
- [Implementation and offline checks](../experiments/dependency_memory/workflow_executed/README.md)

After completion, the analyzer reconstructs every public request, rechecks memory
admission and local byte accounting, reconciles all usage, and grades terminal
answers without another model call. Before dispatch all 407 offline tests and
the repository validator passed. No prompt or case is revised after observing
live answers.

```powershell
python -m experiments.dependency_memory.workflow_executed.analyze experiments/dependency_memory/results/workflow_executed_2026-09-29
```
