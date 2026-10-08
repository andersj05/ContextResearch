# Corrected Python-language engineering retest

Read the [frozen amendment](CONTRACT.md) and [organized finding](../../../../research/ROLLBACK_SUBSCRIPTION_2026-10-08.md).
This retests all version-1 tasks after adding the omitted Python 3.11 requirement.
It preserves the original evidence and is not an independent confirmation.

`authored.py` changes only the public language instruction and evaluator
provenance; problem contents, seeds, public examples, reserved tests and reference
programs remain identical. `run.py` is an explicitly versioned copy of the
version-1 orchestration with the new generator, allocation identity and reference
bindings. It reuses the sealed episode adapter and analysis. Exact source bytes,
tasks and schedule are frozen before requests. `reference_checks.py` re-executes
all twelve references in isolated Docker under the corrected actor bindings.
