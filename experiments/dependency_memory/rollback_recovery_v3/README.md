# Harder-task rollback development study

The [frozen protocol](PROTOCOL.md) defines a prospective cohort of 64 original
constructed tasks after the earlier pilot lacked recovery opportunities. GPT-6
Luna uses the existing Codex subscription: low initial effort and medium effort
for both writers and all recovery arms. All four 16-task accounting blocks are
fixed before any model outcome. Coding variants share eight algorithmic families.

Preparation and live evidence are saved under
[the dated result package](../results/rollback_recovery_v3_2026-10-08/).
The [finite math certificate](../results/rollback_recovery_v3_2026-10-08/math_checks.json),
[coding reference executions](../results/rollback_recovery_v3_2026-10-08/reference_checks.json)
and [installed-client probes](../results/rollback_recovery_v3_2026-10-08/preflight.json)
are offline checks, not model trials. The main archive separately retains
calibration, model outputs, all 832 possible task slots, isolated grading,
matched-arm contexts, task/family analyses and complete usage accounting.

```powershell
python -m experiments.dependency_memory.rollback_recovery_v3.checks --output <fresh-offline-checks.json>
python -m experiments.dependency_memory.rollback_recovery_v3.run freeze --folder <fresh-launch-folder> --preflight <preflight.json> --reference-checks <reference_checks.json> --math-checks <math_checks.json>
python -m experiments.dependency_memory.rollback_recovery_v3.run launch --folder <frozen-launch-folder> --executable <audited-codex.exe> --global-instructions <audited-global-AGENTS.md> --scratch-root <empty-actor-workspaces>
python -m experiments.dependency_memory.rollback_recovery_v3.verify --folder <completed-launch-folder> --regrade --output <fresh-verification.json>
```

Freeze and launch each allocation once. Never retry an unknown identity or start
a later block after unresolved dispatch. Results describe this constructed,
changed-effort development policy; they do not establish benchmark performance,
native compaction improvements, or inference to unseen task families. Optional
independent human ratings and the original benchmark proposal remain unperformed.
