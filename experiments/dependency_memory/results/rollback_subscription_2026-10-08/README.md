# Rollback subscription implementation and live results

October 8, 2026. The [finding](../../../../research/ROLLBACK_SUBSCRIPTION_2026-10-08.md)
describes the user's selected subscription route and its limitations.

Implementation and testing are complete: **700 repository tests pass**, and
115 GPT-6 Luna medium generations have known metering. The corrected 24-task
run has one paired math recovery case, K=[1,1] and R=[1,1], too few to establish
an advantage. All twelve corrected coding candidates pass their retained suites.
This is an authored engineering pilot and same-cohort retest; the proposed
LiveCodeBench comparison remains unperformed.

| Stage | Complete generations | Calculated planning credits |
|---|---:|---:|
| Excluded E1 calibration | 8 | 0.0727825 |
| Preserved instruction-gap run | 50 | 1.0515735 |
| Corrected Python-language retest | 57 | 1.0641780 |
| Total | 115 | 2.1885340 |

Actual subscription account charges are unavailable. Reasoning is part of output,
and retesting these 24 tasks does not create 48 independent tasks.

- [Offline checks](offline_checks.json): 19 scientific access, accounting and
  failure-semantics tests pass; no model calls.
- [Frozen E1 manifest](calibration_v1/manifest.json): eight authored calibration
  requests, new authorization, current client hashes and isolated runtime.
- [Installed-client preflight](calibration_v1/preflight.json): ten unauthenticated
  localhost probes, current signed-in model catalog and sanitized quota snapshot.
- [Runtime audit](calibration_v1/runtime_audit.json): pinned Python 3.11 Docker
  image, fixed limits and actual isolated interpreter execution.

- [Live E1 outcomes](calibration_v1/summary.json): all eight strict formats valid;
  both terminal answers correct; complete metering, no unknown dispatches.
- [E1 evidence manifest](calibration_v1/evidence_manifest.json): 32 bound evidence
  files; 45 frozen source bindings; append-only ledger reconciled with exports.
- [Authored coding references](authored_reference_checks.json): 12 reference
  programs pass all 156 retained test executions in Docker; zero model calls.
- [First authored run](pilot_authored_v1/report.md): all 24 tasks preserved,
  50 complete generations, no eligible paired recovery cases. Six coding answers
  were C++ under statements that omitted the Python execution-language contract.
- [First archive probes](archive_checks_v1.json): one positive verification and
  five semantic tamper probes pass; no model calls.
- [Corrected references](corrected_reference_checks.json) and
  [language invariants](language_offline_checks.json): all 156 retained reference
  tests and two cohort-wide correction checks pass.
- [Corrected frozen retest](pilot_python_v2/manifest.json): explicit Python 3.11
  requirement, same 24 tasks and exact suites, new launch identities before answers.
- [Corrected outcomes](pilot_python_v2/report.md) and [full analysis](pilot_python_v2/analysis.json):
  every task, all four conditions, paired and secondary denominators, missingness
  and resource projections. G is unscheduled after an oversized summary.
- [Corrected archive probes](archive_checks_v2.json) and [independent Docker regrading](verification_pilot_v2.json):
  six probes pass; all public dispositions and scored retained suites agree.
- [First-run independent regrading](verification_pilot_v1.json): earlier C++
  syntax outcomes and successful retained grades are reproduced.
- [Current repository tests](final_repository_checks.json): 700/700 pass, no
  failures, errors or skips; [structured progress](final_repository_checks.progress.jsonl).
- [Full scientific validation](repository_validation.json) and [paper build](paper_build.json).
- [Final navigation and catalog validation](navigation_checks.json).
- [Combined machine-readable summary](summary.json) and [implementation issues](implementation_notes.json).

E1 used 21,568 input and 1,509 output tokens (514 reasoning included in output),
calculated as 0.0727825 planning credits. Actual account charges are unavailable.
The E0 archive and old studies are preserved. Calibration and reference checks
do not establish rollback benefit; the authored pilot is a disclosed change from
the proposed benchmark task source.

The first run is retained as evidence of the instruction gap. Its calculated
usage is 1.0515735 planning credits. Version 2 is a post-observation engineering
retest of the same tasks; it is not an independent cohort or confirmation.
