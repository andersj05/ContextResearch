# Rollback E0 implementation and verification

October 8, 2026. **Offline engineering acceptance; no model experiment or rollback
benefit measured.** This implements the first step of the
[review handoff](../docs/ROLLBACK_REVIEW_HANDOFF_2026-10-08.md). The model pilot and
later policies remain unperformed. C75 and living draft v0.42 are unchanged.

## What is implemented

The [package](../experiments/dependency_memory/rollback_pilot/README.md) supplies
typed public/evaluator records, strict model-output parsing, canonical request
rendering, the prescribed math generator, independent exact checks, public and
reserved-test grading, a pinned Docker executor, deterministic coding intake,
durable reservations, a scripted controller and task-level analysis.

K/R have identical instructions, original task, checkpoint, feedback and lesson.
Only K contains the trial. Continuations reconstruct two text messages; neither
condition receives evaluator material, prior responses, provider handles, opaque
reasoning, archives or tools. Routing canaries test removal of raw branch text;
public feedback and lessons may legitimately retain some branch information.

Every call has an append-only `planned -> reserved -> dispatched -> completed`
history. An unknown response/usage locks liability and stops new dispatches.
Crashes and duplicate identities cannot cause automatic retries. Request caps
are tested before dispatch, including the common K/R pair. Writer failures block
only their dependent conditions; known malformed/capped terminal answers score
zero, while ambiguous and never-dispatched scheduled answers remain unknown.

## Checked evidence

| Check | Result and scope |
|---|---|
| Package tests | [66 passed, zero skips/errors/failures](../experiments/dependency_memory/results/rollback_e0_2026-10-08/package_checks.json), including nine actual container integration tests |
| Exact math agreement | [12 certificates](../experiments/dependency_memory/results/rollback_e0_2026-10-08/math_certificates.json), covering 204,768 bounded equation assignments and 5,888 listed-color assignments; separate malformed, unlisted-color and bound probes |
| Scripted controller | [12 authored episodes, 144 fake calls](../experiments/dependency_memory/results/rollback_e0_2026-10-08/scripted_controller/tasks.jsonl); exact requests, responses, preparations and event ledger are retained |
| Analysis | [Saved tables](../experiments/dependency_memory/results/rollback_e0_2026-10-08/analysis.json) report full flow, all arms, domain-specific pairs, secondary intersections, missingness bounds and synthetic projections |
| Preparation | [Manifest](../experiments/dependency_memory/results/rollback_e0_2026-10-08/launch_review/manifest.json) binds 12 math tasks, eight calibration requests, 156 potential math slots, 32 source files and runtime metadata |
| Archive verifier | Five evidence probes pass: changed responses, extra files, falsified mathematical counts and missing reservations are detected, including semantic changes with updated archive hashes |

The scripted solver intentionally emits a rejected candidate, then supplies the
evaluator witness in every arm. Its scores check orchestration and analysis; they
are not model observations or evidence that lessons/removal improve reasoning.
The synthetic shared ledger evaluates to USD 0.0478070 under the review's rates
and byte-based fixtures. **Actual provider spend is USD 0.** Standalone projections
include the preparation each policy would need and cannot be summed as spend.

The [runtime audit](../experiments/dependency_memory/results/rollback_e0_2026-10-08/launch_review/runtime_audit.json)
records Docker 29.7.2 and Python 3.11.17 in
`python:3.11-slim@sha256:0dd364ba7e10242f07755449e3a3d0e35f9efd987952737b90def6709ab0c5ce`.
Actual probes verify reference/wrong-program grading, fresh scratch, non-root
execution, read-only base storage, absent host files/credentials, disabled external
network, CPU/memory/process limits, bounded output, timeout handling and teardown.
No benchmark corpus or reference solution was downloaded. Local runtime/development
work is separate from provider dollars.

Docker engine startup and the official runtime image download were local setup
actions. These tests do not certify resistance to every container/kernel escape.
Implementation choices follow the official [Docker container controls](https://docs.docker.com/engine/containers/run/)
and [Python resource-limit interface](https://docs.python.org/3.11/library/resource.html),
inspected October 8. No literature review status or paper claim is upgraded.

## Remaining live gates

1. A real 12-task lite release_v6 coding cohort with pinned source/loader revision,
   source-specific license review, complete retained tests, references and exposure exclusions.
2. A live endpoint adapter with audited actual fields, no continuity/tools and no hidden retries.
3. Provider tokenizer, complete-request overhead and enforceable generated-token cap checks.
4. Model revision and current account access, without inventing a dated snapshot.
5. Fresh rate/metering calibration and mutually exclusive billing buckets.
6. A separately recorded E1/E2 launch allocation; the USD 5 proposal remains unallocated.

The [review bundle](../experiments/dependency_memory/results/rollback_e0_2026-10-08/launch_review/)
retains these gates as false/null rather than claiming a launch-ready 24-task cohort.
The normalized coding selector is tested with explicitly authored metadata doubles;
those doubles are never eligible pilot tasks. Real data rights and reference
provenance cannot be established by format validation alone.

The separate [static coding-source intake](../provenance/rollback_coding_source_review_2026-10-08.json)
records a candidate revision and loader/card hashes. It checks the release selector
and declared schema without downloading task files or executing third-party code.
Conflicting license labels and an uninspected metadata field leave the required
rights/reference checks unresolved; the E0 manifest remains unchanged.

## Reproduction and preservation

Follow the [package commands](../experiments/dependency_memory/rollback_pilot/README.md#offline-commands).
The default repository validator includes archive/request/cost bindings and
independent finite mathematical regeneration; navigation-only validation does not.
The [archive manifest](../experiments/dependency_memory/results/rollback_e0_2026-10-08/archive_manifest.json)
binds every controlled result file and the verifier. Source changes require new
verification and a new evidence identity; do not overwrite this checkpoint.

Development-check failures and their fixes are retained in the bounded verification
record. Full-repository scientific tests, validation and paper assembly have their
own dated verification evidence; the package count does not imply those broader
checks completed at the same time.

The [repository verification](../experiments/dependency_memory/results/rollback_validation_2026-10-08/README.md)
records all **663 scientific tests passing**, full existing numerical regeneration
PASS, and 16 saved-evidence validator tests passing. Final catalog/navigation,
sealed E0 verification and the 48-source paper build are recorded separately;
the broad validator's startup catalog count is preserved rather than rewritten.
