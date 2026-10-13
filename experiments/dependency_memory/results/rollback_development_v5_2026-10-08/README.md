# Rollback development v5 preparation

Prepared October 8, 2026 (America/New_York; timestamps use UTC). **Zero live model
generations.** These files certify software, task references and interface checks;
they do not establish Luna difficulty, a rollback advantage or a scientific result.

Read the [implementation and launch instructions](../../rollback_development_v5/README.md)
and [frozen protocol](../../rollback_development_v5/PROTOCOL.md).

## Frozen cohort

The [task catalog](prepared/TASK_CATALOG.md) lists 48 unique authored instances:
four families, three horizons, two difficulty settings and two replicates per
cell. There are 24 mathematical planning tasks and 24 two-module Python repairs.
Short/medium/long tasks allow 2/10/30 candidate actions and disclose requirements
in 1/4/8 stages. The longer tasks add constraints and executable examples; their
length is not produced by padding. Difficulty labels remain uncalibrated.

The [task data](prepared/tasks.json), [manifest](prepared/manifest.json),
[bundle hashes](prepared/bundle.json) and [source snapshot](prepared/source_snapshot.zip)
bind the complete task set, protocols, controller, graders, audited transport
dependencies, 768 jobs and 16,904 possible call identities. The tighter
state-machine ceiling is **13,640 generations including eight calibration calls**.
Most identities can remain unused. Three tracks reuse the same 48 tasks and are
reported separately: common-failure recovery, independent full policies and
repeated memory compression. These are not 768 independent tasks.

## Reference and interface checks

[Task verification](prepared/task_checks.json) passes all 24 math and 24 coding
tasks. It compares 158,912 mathematical candidate/stage checks with an independent
formulation, exhaustively enumerating route permutations but not scheduling
assignments. All 24 authored Python references pass 960 public/reserved cases in
the digest-pinned Docker runtime; each of the 24 initial buggy projects fails
the final suite. This verifies the frozen tests, not universal program correctness.

[Installed-client preflight](client_preflight/preflight.json) passes 36 local
mock probes: ten inherited transport cases, fourteen v5 cases, four concurrent
clients and eight concurrent clients. The near-limit probe serializes a complete
125,404-byte request under the conservative 131,072-byte body bound. The checked
client is `codex-cli 0.162.0-alpha.2`, using the
existing ChatGPT subscription and medium effort. Read-only account discovery and
unauthenticated loopback probes generated **no model output**. The inherited
`E2_v02_launch_ready: false` field concerns the old, unverified 16,384-output-token
cap; v5 explicitly declares that no configurable output cap is established.

The [full-cohort offline audit](offline_audit.json) passes: all 768 jobs and 4,080
scripted calls replay, the ledger records a peak of four admitted calls, and all
reported outcomes and usage reconcile. The [retained rehearsal](offline_rehearsal.zip)
contains the complete typed requests/responses, jobs, accounting database,
analysis and sealed inventory. Its [archive record](offline_rehearsal_archive.json)
binds 8,936 files, 65,512,543 uncompressed bytes and the archive SHA-256.
Scripted actor success is not model evidence. The fixture deliberately inserts a
first failure and then supplies private reference answers solely to exercise
controller routes; those answers are unavailable to live actors.

To inspect the saved evidence without calling a model, extract the rehearsal to
a new ignored directory, then run:

```powershell
Expand-Archive -LiteralPath experiments/dependency_memory/results/rollback_development_v5_2026-10-08/offline_rehearsal.zip -DestinationPath tmp/v5-saved-rehearsal
python -m experiments.dependency_memory.rollback_development_v5.run audit --bundle experiments/dependency_memory/results/rollback_development_v5_2026-10-08/prepared --output tmp/v5-saved-rehearsal
```

The [full scientific repository validator](repository_scientific_validation.json)
passes all its 259 reported check categories. **All 744 distinct repository
tests pass**, including all 26 new v5 invariants: [full discovery](repository_unit_tests.txt)
passes 735 and initially skips nine opt-in Docker checks; a [separate
pinned-runtime run](repository_docker_tests.txt) passes those exact nine. The
[test record](repository_unit_tests.json) preserves both runs with no remaining
unexecuted checks. Paper assembly,
catalog consistency and navigation checks also pass. The [readiness record](readiness.json)
binds those checks to this preparation. No new model or natural-workflow
observations are made.

## Launch boundary

Use the explicit launch command in the implementation README after preparation.
Four workers are the default, with a maximum of eight. Launch refreshes preflight
and runs eight excluded live calibration calls before admitting task jobs. Each
generation has a fresh process/thread and a centrally reserved identity. Unknown
dispatch stops new admissions while already admitted calls drain. No automatic
retries, API fallback, purchase fallback or reopened historical allocations.

Every complete arm retains its actual token and writer costs. The study matches
candidate-action/call allowances, not exact tokens or dollars. Provider revision,
sampling seed and actual subscription charges are unavailable. Preserve ceiling,
floor and missing outcomes; assess difficulty using controls after the fixed
cohort. A later difficulty redesign requires new task IDs and a new freeze.
