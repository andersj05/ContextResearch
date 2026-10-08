# Rollback subscription implementation and calibration

October 8, 2026. Implementation, E1 calibration and both authored engineering
runs are complete and verified. **All 700 repository tests pass.** The corrected
run has one paired math recovery task: K and R each succeed on both draws.
That denominator fails the proposed feasibility screen and establishes no
reliable rollback advantage. The planned LiveCodeBench comparison is unperformed.
The user selected their existing Codex
subscription for GPT-6 Luna and explicitly removed token/cost budget concerns
for completing these tests. This supersedes the direct-API preference and
credential question; no API key is needed for this route.

The [versioned adapter](../experiments/dependency_memory/rollback_pilot/subscription/README.md)
uses the installed official Codex app-server and ChatGPT sign-in. Its
[E1 contract](../experiments/dependency_memory/rollback_pilot/subscription/CONTRACT.md)
separately records the authored calibration schedule, information access,
accounting assumptions and unknown-outcome stops. The [original E0 evidence](ROLLBACK_E0_IMPLEMENTATION_2026-10-08.md)
remains frozen. Scientific checkpoint C75 and draft v0.42 are unchanged.

The installed CLI is `0.162.0-alpha.2`. Fresh no-auth localhost probes verify
one HTTP attempt for ordinary output, attempted tool use, HTTP 503, truncated
stream, missing usage and duplicate answers. Additional probes bind the coding,
writer and K/R interfaces. The actor has fixed global instruction text and
allowlisted harness wrappers; every tool attempt is rejected. This is a
client-side audit, not proof of an empty tool registry or server-side internals.

No configurable 16,384-token output ceiling is established for this client.
The subscription amendment uses provider-default output and records the broader
published model envelope as a conditional planning assumption. Byte admission,
token telemetry, calculated credits and actual account usage remain separate.
The original API USD estimate cannot price these subscription calls.

All **eight live E1 requests completed**, passed their strict format checks and
returned complete token telemetry. The two terminal candidates were correct;
the coding answer passed all three retained tests in isolated Docker. No tool
items, unknown usage or identity retry was observed. The archive verifies eight
identities, 45 source bindings and 32 evidence files. This is calibration success,
not evidence of a rollback benefit.

| E1 usage | Observed value |
|---|---:|
| Input tokens | 21,568 |
| Cached input tokens | 0 |
| Output tokens, including reasoning | 1,509 |
| Reasoning subset | 514 |
| Calculated subscription planning credits | 0.0727825 |
| API-key model calls / API-dollar spend | 0 / 0 |

Actual subscription account charges are unavailable. The calculation uses
dated published credit rates, not API token prices, and does not add reasoning
twice. There was no token or cost budget stopping gate; unknown transport or
metering would still have stopped the allocation for scientific validity.

The [result bundle](../experiments/dependency_memory/results/rollback_subscription_2026-10-08/README.md)
keeps raw structured requests, visible final answers, usage events, append-only
SQLite accounting and verification separate from this finding. No opaque
reasoning transcript or credentials are archived.

The proposed LiveCodeBench cohort remains unprepared: source permissions and
reference programs are unresolved. A separately disclosed [authored source amendment](../experiments/dependency_memory/rollback_pilot/cohort_v1/CONTRACT.md)
provides twelve original coding tasks alongside the specified twelve math tasks
for a complete engineering pilot. Every coding reference passed all 13 retained
tests in Docker (156 executions total); ten additional runner invariants pass.
Its structural difficulty labels are not benchmark ratings.

## First authored run and language-contract correction

The [first 24-task run](../experiments/dependency_memory/results/rollback_subscription_2026-10-08/pilot_authored_v1/report.md)
completed 50 generations with no unknown usage or dispatches. Eleven math tasks
produced correct candidates; one produced no candidate after both allowed branch
steps. Six coding candidates passed all retained tests. Six other coding answers
were C++ and were rejected as syntax errors by the Python grader. The coding
actor statements omitted the Python 3.11 requirement: **this is an implementation
instruction gap**, not a clean measure of programming ability. Every response,
candidate, task disposition and unused call slot is preserved.

There were zero eligible public mismatches and therefore zero paired recovery
tasks. R minus K is unidentified, not zero. This fails the six-task feasibility
screen in both domains and does not establish rollback superiority or equivalence.
Six archive verification/tamper probes pass. Independent public checks and
retained-suite grading are repeated in Docker without any model request.

Version 1 used 151,734 input tokens (12,544 cached) and 56,037 output tokens
(38,868 reasoning included), calculated as **1.0515735 planning credits**.
Its 50 generations are separate from eight E1 calibration generations.

A [version-2 amendment](../experiments/dependency_memory/rollback_pilot/cohort_v2/CONTRACT.md)
adds the explicit Python 3.11 standard-library requirement to every coding actor
statement. All 24 tasks are retested, including previous successes; problem
contents, reference programs, reserved tests, task IDs and ordering are identical.
Two language-contract invariants and all 156 repeated reference-test executions
pass. The new [manifest](../experiments/dependency_memory/results/rollback_subscription_2026-10-08/pilot_python_v2/manifest.json)
binds the complete corrected cohort, sources and separate 312-call allocation
before outcomes. This is a post-observation engineering retest of the same tasks;
the two runs cannot be added as independent cohorts or called confirmation.

## Corrected run: objective results

The [corrected run](../experiments/dependency_memory/results/rollback_subscription_2026-10-08/pilot_python_v2/report.md)
completed **57 generations**, with no unknown dispatch or metering. All twelve
coding candidates passed their thirteen retained tests. Math had ten correct
initial candidates, one eligible public failure and one task without a candidate
after both allowed branch steps. No task was replaced and no failure was forced.

| Domain | Selected tasks | Initial correct | Public failure tasks | Paired K/R tasks | R minus K |
|---|---:|---:|---:|---:|---|
| Math | 12 | 10 | 1 | 1 | 0 percentage points, one observed task |
| Coding | 12 | 12 | 0 | 0 | Unidentified |

The sole paired task is `math-coloring-02`, the first tie in frozen task order.
The model encoded entire allowed-color lists as integers outside the public
bounds. Its public receipt reported value 3 outside [0,2]. With identical C/F/L,
K scores [1,1], R [1,1] and Z [1,0]. G is unperformed because the generated
summary exceeded the 1,024-visible-byte cap; its paid generation is retained.
No continuation repeats the exact rejected candidate. Optional blinded human
measures remain unreviewed and are not used as evidence of a mechanism.

R minus Z is 50 percentage points on this same single task. It is a descriptive
observation, not a general lesson-benefit claim. There is no eligible R/G
comparison, bootstrap interval or confirmatory p-value. The observed [0,0]
missingness bounds for R minus K concern missing data, not statistical uncertainty.
Both domains fall below the prespecified six-pair feasibility screen.

R used 3,260 input tokens per terminal draw versus K's 3,522, but produced more
output tokens. The two R terminal calls used 0.05225 calculated planning credits
versus K's 0.0413725. Shorter input did not produce lower calculated terminal
cost in this case. Standalone policy projections are separate views of observed
episodes; they are not independently run policies or additive actual charges.

## Combined usage and verification

| Stage | Complete generations | Calculated planning credits |
|---|---:|---:|
| E1 calibration | 8 | 0.0727825 |
| First authored instruction-gap run | 50 | 1.0515735 |
| Corrected same-cohort retest | 57 | 1.0641780 |
| Total | 115 | 2.1885340 |

Combined usage is 348,967 input tokens (50,176 cached), 114,321 output tokens
and a 79,448-token reasoning subset already included in output. There were no
API-key calls, API-dollar charges, unknown dispatches or identity retries.
Calculated credits are not actual subscription account charges. These are 24
unique study tasks retested, plus excluded calibration fixtures; they are not
48 independent tasks.

The [machine-readable summary](../experiments/dependency_memory/results/rollback_subscription_2026-10-08/summary.json)
independently prices the combined exclusive token buckets and reconciles the
stage ledgers. The complete current repository suite passes **700/700**, with
zero failures, errors or skips. Ten installed-client localhost probes and all
156 reference-test executions per version pass. Both archives pass one positive
verification plus five semantic tamper probes, and every scored retained suite
and public candidate disposition was independently rechecked in isolated Docker.
The corrected archive binds 63 source files, 179 evidence files and all 312
possible call slots. The original E0 and E1 archives remain verifiable.

Full scientific repository regeneration and paper assembly pass; the updated
navigation/catalog check is recorded separately. There are still 75 manuscript
claims, 63 bibliography entries and 48 cited paper sources. No claim was upgraded.
The [implementation notes](../experiments/dependency_memory/results/rollback_subscription_2026-10-08/implementation_notes.json)
retain development errors and the language correction. E3/E4/E5 remain plans.
The implementation is ready for a separately designed harder/longer task cohort;
this small engineering study does not justify a rollback-superiority or native
harness-performance assertion.
