# V5 continuation with failures confined to their trajectories

The [amendment](PROTOCOL.md) permits continuing v5 after the original unknown
dispatch. Original frozen source and evidence remain intact. Completed or unknown
identities are never retried; unrelated jobs continue. Shared writer losses are
confined to their dependent arms. Safe transport diagnostics are retained.

The new phase imports the original cumulative ledger, restores receipt-replayable
trajectories, and dispatches only never-admitted identities. It uses the same
48-task cohort, Luna medium, four workers and original 13,640-generation ceiling,
counting all earlier admissions. The existing calibration is reused; client mocks
and account/source checks are refreshed without model output.

```powershell
python -m unittest experiments.dependency_memory.rollback_development_v5_continuation.test_continuation -v
python -m experiments.dependency_memory.rollback_development_v5_continuation.run prepare --bundle experiments/dependency_memory/results/rollback_development_v5_2026-10-08/prepared --prior experiments/dependency_memory/results/rollback_development_v5_2026-10-08/live --output experiments/dependency_memory/results/rollback_development_v5_continuation_2026-10-08/prepared
python -m experiments.dependency_memory.rollback_development_v5_continuation.run launch --prepared experiments/dependency_memory/results/rollback_development_v5_continuation_2026-10-08/prepared --output experiments/dependency_memory/results/rollback_development_v5_continuation_2026-10-08/live --workers 4 --live
python -m experiments.dependency_memory.rollback_development_v5_continuation.run audit --prepared experiments/dependency_memory/results/rollback_development_v5_continuation_2026-10-08/prepared --output experiments/dependency_memory/results/rollback_development_v5_continuation_2026-10-08/live
```

Never start multiple launchers. A later authorized continuation can use another
verified phase after an actual global capacity/service stop, preserving every
earlier admission. Completed phase directories are sealed rather than reopened.
