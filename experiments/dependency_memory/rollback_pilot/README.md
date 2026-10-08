# Luna rollback experiments and review package

October 8, 2026. **E0 implemented and checked; model stages remain unperformed.**
This is a separate study, not a continuation of a closed allocation. Read the
[implementation finding](../../../research/ROLLBACK_E0_IMPLEMENTATION_2026-10-08.md)
and [saved E0 report](../results/rollback_e0_2026-10-08/report.md) for the current
checkpoint. The design documents below retain their original review status.

**Start with the [review handoff](../../../docs/ROLLBACK_REVIEW_HANDOFF_2026-10-08.md).**
It explains the intervention, an example, the staged experiments, review choices
and implementation order without requiring the full technical packet.

- [Research and source comparison](../../../research/ROLLBACK_PILOT_DESIGN_2026-10-07.md)
- [Draft protocol](DRAFT_PROTOCOL.md)
- [Draft prompt interfaces](PROMPTS.md)
- [Experiment suite and later policies](EXPERIMENT_SUITE.md)
- [Task selection and grading](TASKS_AND_GRADING.md)
- [Controller and data contract](EXECUTION_CONTRACT.md)
- [Analysis and interpretation](ANALYSIS_PLAN.md)
- [Later policy prompts](POLICY_PROMPTS.md)
- [Machine-readable design](design_manifest.json) and [authored example](review_example.json)

Question: after the same failed exploration and the same feedback/lesson, does
removing the failed branch improve recovery relative to retaining it?

Proposed model cohort: 12 exactly checkable math tasks and 12 coding tasks; four
continuation conditions and two draws per condition. All 12 math instances and
the eight disclosed calibration requests are bound in the
[offline review manifest](../results/rollback_e0_2026-10-08/launch_review/manifest.json).
The real coding cohort and live transport/allocation remain open. No model request
can be issued by this implementation: its only transport is scripted.

The intervention changes explicit model inputs between calls. It does not edit
Luna's private reasoning tokens or directly manipulate its KV cache. Conditional
recovery, end-to-end success and total-cost benefit are separate outcomes.

## Implementation and access boundaries

| Module | Purpose |
|---|---|
| [records.py](records.py), [contexts.py](contexts.py) | Strict immutable actor artifacts, separate evaluator type, ordered context rendering and copied K/R fields |
| [math_tasks.py](math_tasks.py), [independent_math.py](independent_math.py), [grading.py](grading.py) | Prespecified generation, independent exhaustive feasibility, public receipts and separate terminal grading |
| [code_runner.py](code_runner.py), [coding_tasks.py](coding_tasks.py) | Digest-pinned isolated Python runtime and deterministic source/license/reference-gated coding selection |
| [accounting.py](accounting.py), [schedule.py](schedule.py), [controller.py](controller.py), [transport.py](transport.py) | Transactional append-only dispatch events, fixed slots, failure dispositions and fake transport |
| [analysis.py](analysis.py) | Task-level contrasts, missingness bounds, secondary intersections and separate synthetic cost projections |
| [prepare.py](prepare.py), [offline.py](offline.py), [checks.py](checks.py) | Source-bound preparation, controlled E0 evidence and structured test records |

The coding runtime receives one test input and its own source. Expected outputs,
other tests, repository paths and credentials stay outside the container. It uses
no host mounts, disabled network, non-root execution, a read-only base filesystem,
512 MiB memory, one CPU, 32 processes and fresh bounded scratch. No host-execution
fallback exists. The saved [runtime audit](../results/rollback_e0_2026-10-08/launch_review/runtime_audit.json)
records the actual engine and Python 3.11.17 image digest. Passing the probes is
bounded engineering evidence, not certification of Docker or its kernel.

Input admission currently uses conservative UTF-8 byte units plus synthetic
overhead. These are explicitly **not provider token counts**. Published prices in
the review packet are design assumptions for accounting fixtures, not measured
provider charges. Actual model calls and API spend are zero.

## Offline commands

Run from the repository root. Output paths are examples; choose a new identity
for each run. Existing ledgers, bundles and saved evidence cannot be overwritten.

```powershell
# Core tests; the nine actual Docker tests are explicitly skipped without a digest.
python -m experiments.dependency_memory.rollback_pilot.checks --output tmp/rollback_core_checks.json

# All 66 package tests, including actual isolation checks, using the saved local image.
python -m experiments.dependency_memory.rollback_pilot.checks --output tmp/rollback_all_checks.json --docker-image python:3.11-slim@sha256:0dd364ba7e10242f07755449e3a3d0e35f9efd987952737b90def6709ab0c5ce

# Freeze math/tasks/schedule and the eight calibration requests; no launch authority.
python -m experiments.dependency_memory.rollback_pilot.prepare --output tmp/rollback_new_review

# A fresh controlled, explicitly scripted E0 run. Requires passing bound checks for acceptance.
python -m experiments.dependency_memory.rollback_pilot.offline --output tmp/rollback_new_e0 --checks tmp/rollback_all_checks.json --docker-image python:3.11-slim@sha256:0dd364ba7e10242f07755449e3a3d0e35f9efd987952737b90def6709ab0c5ce

# Read-only verification of the saved archive, including independent mathematics.
python scripts/verify_rollback_e0.py --directory experiments/dependency_memory/results/rollback_e0_2026-10-08
python -m unittest scripts.test_rollback_e0_evidence -v
```

The integration command requires a running Docker engine and that local image.
There is no automatic image pull. Generic-summary failure blocks G only; a lesson
failure blocks K/R only. K capacity failure blocks the pair before either arm
dispatches. Missing usage or a possible dispatch locks the reservation and stops
the launch; reopening the ledger never silently repeats that call.

## Next preparation gates

Acquire and normalize the actual lite release_v6 inventory, source revision and
loader bytes; review source-specific permissions; acquire references; verify every
retained test under this runtime; then select four tasks in each difficulty stratum.
The loader rejects missing attestations and preserves exclusions and shortfalls.
Authored sum/selection fixtures never substitute for the benchmark cohort.

Audit a separately implemented live endpoint, retries, token counting, metering,
model/account access and current prices before freezing a new E1/E2 allocation.
The proposed 320-call / USD 5 ceiling is not an allocation. E3/E4/E5 remain separate
unperformed designs. C75 and living draft v0.42 remain the scientific paper checkpoint.
