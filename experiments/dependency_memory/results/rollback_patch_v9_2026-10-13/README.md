# Fact-preserving patch rollback v9 — October 13, 2026

The frozen control-only calibration completed **16 initial model patches; all
16 passed both public and held-out tests**. There were zero eligible naturally
failed patches, zero unknown calls and no global stop. The calibration gate
fails for lack of failure headroom; the main study remains unperformed. This
is a task-difficulty ceiling, with no evidence for or against rollback.

The [protocol](../../rollback_patch_v9/PROTOCOL.md) fixes all task facts and
separates failed-patch retention from categorical diagnostic lesson presence.
All arms restore the same original workspace. The three-attempt repair budget
is on the same task. No repair or lesson call was needed in this calibration.

## Frozen evidence

- [Calibration bundle](calibration_bundle/manifest.json), [analysis](calibration_live/analysis.json),
  [execution](calibration_live/execution.json), [accounting](calibration_live/accounting.json).
- [Independent replay](calibration_live_replay_audit.json): every admitted request
  reconstructed and every received patch regraded in the pinned Docker image.
- [Closed calibration gate](calibration_gate.json).
- [Scripted fixture replay](fixture_run_replay_audit.json): four deliberately
  failed reference-controller examples, 24 scripted responses, **zero model
  calls**. These are implementation checks, not model failures or effect data.

The live calls record 104,937 input tokens (3,584 cached), 17,422 output tokens
(7,162 reasoning), and 0.4720535 planning credits. Planning credits are not an
observed subscription charge. Luna used medium reasoning; an immutable model
weight revision and provider sampling seed are unavailable. The actual pinned
client configuration, hash and runtime audit are saved with the run.

## Validation and next study

The full offline suite covered all 980 discovered test IDs: 966 passed and 14
optional Docker checks skipped. Separate actual Docker runtime and task checks
passed, as did the full scientific repository validator (259 check categories).
Saved records are in [validation](validation/full_validator.json) and
[full test results](validation/full_tests_v2/summary.json).

The source snapshot is `420d45e2214c9e57316b28eb07d730704db5424f8d0831321c74ba3c88209d21`.
This source and allocation remain closed. A [separate v10 calibration](../rollback_patch_v10_2026-10-13/README.md)
increases project size before any factorial outcomes have been observed. It
does not relabel these sixteen successes or reopen this main-study gate.
