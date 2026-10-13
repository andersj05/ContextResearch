# Exploratory patch rollback v11

This is an explicitly unplanned development follow-up. The v10 calibration
produced three meaningful failures and three correct ordinary repairs, missing
its frozen minimum of four failures. That original gate remains failed. The
new [protocol](PROTOCOL.md) freezes 256 fresh tasks before any deletion or
lesson-arm outcomes, with at most 3,584 subscription calls and 32 workers.

The factorial retains every task fact and separates visible failed-patch
deletion from categorical diagnostic lessons. All arms restore the same base
files and get three repair attempts. Imported runtime, transport, analysis and
scheduler contracts remain unchanged. The engine is the verified state machine
with a new study identity through its version-local common module.

See [saved evidence](../results/rollback_patch_v11_2026-10-13/README.md).
