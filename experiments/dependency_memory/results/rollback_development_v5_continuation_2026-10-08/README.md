# Authorized v5 continuation

Status: all 768 jobs have final dispositions; independent live replay/regrading
has passed. The cumulative ledger has 2,124 metered completions (eight
excluded calibration) and four unknowns, with no global stop and no repeated
identity. The three R/K quality estimates are tied; controls show a strong
ceiling. Read the [cumulative results](LIVE_RUN.md),
[derived comparisons](cumulative_diagnostics.json),
[independent audit](launch_checks/live_audit_result.json) and
[dated finding](../../../../research/ROLLBACK_STAGED_CONTINUATION_2026-10-09.md).

All 754 distinct repository tests have passing
results, including ten continuation invariants and nine Docker isolation checks.
Two existing Windows file-replacement errors passed unchanged on exact recheck;
the [reconciliation](launch_checks/test_reconciliation.json) preserves both
failed and passing records. The user
explicitly authorizes amending the global-unknown stop and finishing the fixed
v5 allocation using Luna medium and four workers.

Read the [continuation protocol](../../rollback_development_v5_continuation/PROTOCOL.md)
and [runner](../../rollback_development_v5_continuation/README.md). The
[original phase](../rollback_development_v5_2026-10-08/LIVE_RUN.md) is immutable:
235 completed generations and one unknown remain recorded exactly once.
Unknown trajectories stay missing, independent jobs continue, and two healthy
partial trajectories restore verified receipts before the next unsent identity.

The same 48 tasks, 768 jobs and 13,640 cumulative generation ceiling apply.
The [prepared manifest](prepared/manifest.json) binds the unchanged original
allocation, sealed prior phase and amended source. The eight passed calibration
calls are reused without new provider generations. Fresh client hashes match the
original phase; new safe diagnostics classify local and systemic failures.
Preparation, tests and replay are offline; the primary analysis distinguishes
them from provider observations. Failure handling and
execution timing were amended after initial observations; no confirmation or
native-harness result is implied.

The raw archive `live_evidence.zip` and final `closeout.json` are written last by
the [archive helper](launch_checks/archive_evidence.py). The archive retains
repository-relative paths, the original prepared bundle and phase, current
cumulative evidence, and every bound Python/protocol source. Credentials and
uncontrolled session logs are excluded.
