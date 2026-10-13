# Parallel rollback runner efficiency results

October 13, 2026 UTC. Sixteen workers complete the fixed live throughput probe
in 26.36% less pooled batch time than eight workers. The new controller also
starts continuations as their own prefixes finish and reduces executable-hash
allocation from about 334 MB to 1.05 MB. These are engineering improvements;
the scientific intervention retains v7's limitations. Read the separate
[rollback information audit](../../../../research/ROLLBACK_INFORMATION_BOUNDARY_2026-10-13.md)
for what the rollback outcomes mean.

## Implementation

The scheduler releases a continuation only after its own prefix is durably saved
and its context contract checked. It no longer waits for every unrelated prefix.
Ready continuations have priority, with frozen manifest rank breaking ties.
Default concurrency is sixteen; offline fixtures verify bounded operation
through thirty-two. Fresh processes, independent threads, source checks,
admission accounting and the single-generation boundary remain in place.

Every executable integrity check still reads and hashes the full file, using a
reusable 1 MiB buffer. Across six alternating fresh-process measurements, median
Python allocation peak falls from 334,122,804 to 1,051,085 bytes, about 99.69%.
Native process peak working set falls from 363.0 MB to 29.9 MB; this includes
interpreter overhead. The single-hash median time changes from 0.397 to 0.362
seconds. All digests match. These measurements concern hashing, not the memory
of the entire model client or provider. [Local diagnostic](hashing_benchmark.json).

## Fixed live throughput comparison

Four serial batches use the same sixteen initial-stage prompts with distinct
frozen call identities. The order is eight, sixteen, sixteen, eight workers.
All 64 admissions complete with known usage, no retry, no unknown and no stop.

| Batch | Workers | Completed calls | Controller seconds | Verified peak admissions |
|---|---:|---:|---:|---:|
| 1 | 8 | 16 | 37.571 | 8 |
| 2 | 16 | 16 | 29.673 | 16 |
| 3 | 16 | 16 | 23.205 | 16 |
| 4 | 8 | 16 | 34.231 | 8 |

Each worker count completes 32 calls. Pooled time is **71.802 seconds at eight
workers versus 52.879 seconds at sixteen**, a descriptive 1.358x throughput
ratio and 26.36% elapsed reduction. This is a measured local comparison, not a
guarantee that doubling concurrency halves latency. Repeated prompts, cache
warming, different generated lengths, provider load and batch order can matter.
Offline repository checks also ran on the host during this probe, so local load
was not held constant. No other model allocation from this task overlapped it.

The [frozen-source probe audit](live_throughput_audit.json) verifies identical
prompts, serial batches, every response and usage receipt, per-batch caps and
timing consistency. [Raw analysis](live_throughput/analysis.json).

## Pipelined operation on a new cohort

The separately frozen pilot contains 24 new ledgers, sixteen workers and a
192-call ceiling. It completes all 72 job dispositions in **287.14 seconds**
(4.79 minutes), excluding preflight and replay. There are 135 known model calls
and one retained unknown admission, with no global stop or retry. The unknown
is a prefix action with a recorded provider-or-generation failure; its
dependent pair remains unavailable. It is not a scored model failure or evidence
that concurrency caused the transport loss.

Frozen-source replay verifies all 135 received responses, all nineteen matched
context contracts and 116 independent action grades. Ledger reconstruction
confirms peak concurrency sixteen and **49 continuation admissions before the
last prefix completed**, demonstrating that the old phase barrier is gone.
The separate scheduler trace verifies all 72 jobs and durable parent ordering.

Four prefixes pass all stages; nineteen naturally fail and yield complete
conditional pairs. K solves 11/19 and R 8/19: five K-only successes, two R-only,
six joint successes and six joint failures. The descriptive R-minus-K estimate
is -15.79 percentage points, with bootstrap interval [-42.11, +10.53]. These are
engineering-cohort observations, not a new confirmatory rollback study or a
sample extension of v7. Do not pool the runs into an unplanned efficacy test.

The source packets and successful checkpoint remain available in both arms;
only the original failed record is removed, and a shared lesson can retain its
content. Private reasoning is not manipulated. Comparing this pilot's wall time
or scores with v7's different cohort does not isolate the effect of scheduling
or information preservation. [Pilot analysis](live_pilot/analysis.json),
[execution](live_pilot/execution.json), [frozen protocol](../../rollback_parallel_v8/PROTOCOL.md).

Known pilot usage is 807,707 input tokens including 205,056 cached, and 263,271
output tokens including 252,044 reasoning. Subsets must not be added twice. The
recorded conversion gives 4.8487790 planning credits plus a separate 4.225-credit
reservation for the unknown. These are not measured subscription debit or API
dollars. Both live allocations together use **200 admissions: 199 known and one
unknown**, below the frozen combined 256-call ceiling. API-key calls are zero.

## Offline scheduling evidence and limits

Holding all v7 job service times fixed, the old eight-worker two-phase schedule
replays in 461.53 seconds, within 2.01 seconds of its recorded wall time. A
sixteen-worker pipeline takes 239.76 seconds under those assumptions, about
48.05% less than that replay baseline. Three repetitions of each of six scaled
sleep workloads also exercise actual scheduling, dependencies and coverage.
These are counterfactual and synthetic checks, not live speedup estimates.
[Scheduler diagnostic](scheduler_benchmark.json).

The current cohort initially exposes only 24 independent prefixes and at most
48 concurrent trajectories. Sixty-four workers cannot all be occupied by it.
Larger concurrency needs a separately frozen allocation with enough ready jobs
and its own capacity validation. The implementation is not claimed to have
performed 64 concurrent live calls.

## Verification and evidence

The focused v8 suite passes 46 tests. Full repository discovery accounts for
all 902 test IDs across 97 modules: **893 pass and nine optional Docker tests
skip**, with zero failures, errors or retries. Eight local test processes finish
in 547.92 seconds. The scientific validator passes all 259 checks, and paper
assembly checks 48 cited sources. The unchanged-source scientific tests are
distinct from the later information-audit script and navigation checks.

Read [test coverage](full_tests/summary.json), [scientific validation](scientific_validation.log),
[scripted rehearsal audit](rehearsal_audit.json), [probe audit](live_throughput_audit.json)
and [pilot audit](live_pilot_audit.json). Every audit itself makes zero model calls.
The [source bundle](prepared/bundle.json) binds the source snapshot with SHA-256
`808e653272e08138ec2dc34624a999f0aed7d97d2b1b275cc61d1d1a35f39b32`.
Original v6/v7 sources, allocations and raw results remain unchanged.
