# Composite patch rollback v10 — October 13, 2026

The corrected calibration is frozen under source snapshot
`e867522292208ff5017893f966016ee2faca205e9542fbc0fa851429c372eda4`.
The live control calibration completed **22 known model calls, zero unknowns**
in 108.34 seconds. Thirteen initial patches passed both public and private tests.
Three meaningful failed patches each repaired correctly on the first ordinary
K0 continuation. All three categorical lessons were valid; no capacity or global
stop occurred. The original gate requires four failures, so **3 < 4 and the main
allocation remains closed**. No deletion or lesson-arm outcomes were measured.

[Independent replay](calibration_live_replay_audit.json) reconstructs every call,
checks all three factorial contracts and regrades all patches in isolated Docker.
The [failed gate](calibration_gate.json), [analysis](calibration_live/analysis.json)
and [accounting](calibration_live/accounting.json) remain sealed. Metered usage:
714,186 input tokens (8,960 cached), 58,061 output (15,343 reasoning), 2.4910675
planning credits. Actual subscription debit is unavailable.

An [explicitly unplanned v11 follow-up](../rollback_patch_v11_2026-10-13/README.md)
uses this control-only evidence to prepare a fresh fixed exploratory cohort.
This is a transparent departure from the feasibility rule, not a passing v10
gate or a confirmatory allocation.

The separate v9 calibration passed all sixteen initial patches and its main
study stayed closed. This new [protocol](../../rollback_patch_v10/PROTOCOL.md)
uses eight-component two-file projects, preserves all task specifications and
public feedback, and crosses actual failed-patch deletion with categorical
lesson presence. Each branch can repair the same task three times. There are
four authored composite families, with reused components within each allocation.

## Preparation evidence

- [Task reference execution](validation/task_validation.json): all sixteen
  calibration references pass public and private tests in isolated Docker.
- [Client validation](validation/client_preflight.json): actual localhost
  serialization, 32 parallel probes, exact input boundary and full later-repair
  context; **zero model calls**.
- [Context validation](validation/context_validation_v2.json): every calibration
  and main design retains all public facts. Largest normal third-repair input:
  213,980 UTF-8 bytes, within the 1,048,576-byte text limit.
- [Corrected scripted fixture replay](fixture_run_v2_replay_audit.json): four
  deliberately failed fixtures and twenty-four scripted responses, zero model
  calls. Controller validation is separate from empirical evidence.

The original `fixture_bundle` and unlaunched `calibration_bundle` preserve a
prelaunch byte-bound-only version. Its scripted replay passed, but actual client
preflight exposed a separate one-million-character limit. The
[discovery record](validation/client_capacity_discovery.json) has zero model
calls. The corrected `_v2` bundles enforce both complete-body and conservative
UTF-8 request-text limits. No facts are truncated. A capacity stop prevents
interpreting any factorial contrast as an isolated content effect; all outcomes
still remain reported. Earlier bundles are not relaunched or overwritten.
