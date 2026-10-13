# Rollback development v5: stopped live allocation

October 8, 2026, America/New_York; machine timestamps use UTC.
**Closed with gaps after an unknown transport failure. The full live cohort was
not completed, and no complete R/K pair was observed.** Read the
[finding](../../../../research/ROLLBACK_STAGED_DEVELOPMENT_2026-10-08.md) for scope,
arm counts and missingness bounds.

The user explicitly approved the complete frozen allocation:
[approval record](launch_approval.json). It used the existing Codex subscription,
`gpt-6-luna`, medium effort and four workers. The
[preparation record](README.md), [task catalog](prepared/TASK_CATALOG.md) and
[protocol](../../rollback_development_v5/PROTOCOL.md) retain the original freeze.
All three tracks reuse the same 48 constructed tasks. The 768 jobs and
13,640-generation ceiling are allocation bounds, not independent trials or
expected consumption. Historical allocations remain closed.

## Observed execution

All eight excluded live calibration calls passed. The study then recorded
227 metered completions and one unknown dispatch: **235 metered completions
including calibration**. Thirty-six distinct study tasks received a dispatch;
twelve received none. Fifty-two jobs actually ran, fourteen continuations were
ineligible after initial prefix success, and 702 jobs remained unstarted. Every
one of the 768 jobs and 16,904 possible call identities has a saved disposition.

The unknown identity is policy K, action 8, `v5-ledger-long-hard-2`, observed at
`2026-10-09T02:33:45.563457+00:00`. Its request survives, but there is no accepted
typed response or metering. The ledger records only `DiagnosedProtocolError`;
the more specific whitelisted transport diagnostic was not persisted. Its exact
cause and whether a generation occurred remain unknown. New admissions stopped
atomically, already admitted calls drained, and no dispatched identity was retried.

Policy and memory produced 46 known episode scores: 45 passes and one observed
`invalid_candidate` failure. Three other started episodes remain partial because
of the infrastructure stop. These arms reached different tasks before the stop;
their raw success counts cannot establish a treatment comparison. The mechanism
track produced two initially successful prefixes and one eligible mismatch, but
none of its matched continuations ran. Difficulty calibration remains incomplete.

Total recorded usage, including calibration, is 1,053,487 input tokens, of which
294,912 were cached, and 240,238 output tokens, including 159,460 reasoning
tokens. Calculated planning credits are 4.9731405, plus a separate unresolved
4.225 reservation. Actual subscription charges are unavailable. The primary
R/K resource contrast has no complete pairs.

## Evidence and verification

- [Live analysis and durable accounting](live/analysis.json),
  [execution](live/execution.json), [slot dispositions](live/slot_dispositions.json),
  and [sealed inventory](live/evidence_manifest.json).
- [Passing independent live replay](launch_checks/live_audit_result.json): all
  235 metered completions replay, 52 executed jobs regrade, all 768 job and
  16,904 slot dispositions reconcile, and peak admission is four. This is an
  evidence-integrity pass, not completion of the model cohort.
- [Complete live archive](live_evidence.zip) and its
  [file/hash record](live_evidence_archive.json): 1,248 files and 12,076,674
  uncompressed bytes. Archiving and replay made zero model calls.
- [Post-run diagnostics](live_diagnostics.json) and the
  [retained summary source](launch_checks/diagnostic_summary_source.py).
  The frozen analysis mislabels 45 unstarted prefixes in its descriptive
  `prefix_dispositions` count; diagnostics explicitly correct this to 45
  unstarted, two initial passes and one eligible mismatch. Primary eligibility
  filters and paired denominators are unaffected. Frozen output bytes remain intact.

All 744 distinct repository tests pass across the retained discovery, exact
affected-test rechecks and nine opt-in Docker checks:
[coverage record](launch_checks/repository_test_coverage.json). Initial sandbox
temp cleanup and atomic-replace failures remain in the logs; all 61 affected
identities pass in the outside-sandbox recheck. No scientific source was changed.

Fresh gates pass all [48 task references](launch_checks/fresh_task_checks.json),
nine [Docker isolation tests](launch_checks/docker_tests.json), and 36
[installed-client mocks](launch_checks/client_preflight/preflight.json) without
source/client drift. The [fresh scripted audit](launch_checks/scripted_audit_result.json)
replays all 768 jobs and 4,080 fixture calls; its
[retained rehearsal](launch_checks/fresh_rehearsal.zip) includes the exact review
bundle and simulation. Scripted outputs are not model observations.
The [full scientific validator](launch_checks/scientific_validation_result.json)
passes 259 check categories, and [paper assembly](launch_checks/paper_build.json)
passes with 48 cited sources. Final catalog/navigation checks are recorded at
closeout separately from this scientific check.

## Reproduce without model calls

From the repository root, with access to the existing digest-pinned Docker runtime:

```powershell
python -m experiments.dependency_memory.rollback_development_v5.run audit --bundle experiments/dependency_memory/results/rollback_development_v5_2026-10-08/prepared --output experiments/dependency_memory/results/rollback_development_v5_2026-10-08/live
```

To verify the archival copy instead, extract `live_evidence.zip` to a new ignored
directory and substitute that directory as `--output`. Preserve the source
snapshot and original bindings. The exclusive `prepared/launch_started.json`
marker prevents reopening this allocation.

A future live study needs a separate reviewed freeze. Preserve whitelisted
exception diagnostics and arrange early paired coverage before that launch.
Do not infer a provider fix, a rollback advantage, equivalence, or native-harness
improvement from this stopped development run. C75 and living draft v0.42 are unchanged.
