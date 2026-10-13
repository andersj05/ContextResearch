# Fact-preserving patch rollback factorial

This new study tests deletion of a failed executable patch and diagnostic
lesson content independently. Read the [protocol](PROTOCOL.md) and the
[saved run record](../results/rollback_patch_v9_2026-10-13/README.md).

Every request retains the full specification, both original files and all
public examples. A naturally failed model patch supplies four matched arms:
K0 retains the patch, R0 deletes it, KL retains it with a categorical lesson,
and RL deletes it with the same lesson. Each arm has three repair attempts on
one fixed task. Private test results never enter prompts or stopping rules.

`tasks.py` authors four Python project families with independent small-instance
oracles. `runtime.py` runs patches only in pinned, isolated Docker containers.
`contexts.py` allowlists public information, and `engine.py` checks that the
first four continuation requests differ only in patch visibility and lesson.
`prepare.py` freezes tasks, source, identities and budgets. `runner.py` reuses
the existing isolated subscription transport and bounded durable dispatcher.
`analysis.py` separates the two factors, interaction, missingness and resources;
`audit.py` reconstructs requests and regrades saved responses without a model.

Live allocations are single-use. Do not reopen or retry an admitted identity.
Model observations, offline reference execution and deliberately wrong-once
controller fixtures are different evidence types. Source files must remain
unchanged after preparation; later improvements require a new version.

From the repository root, the supported sequence is:

```powershell
python -m unittest discover -s experiments/dependency_memory/rollback_patch_v9 -t . -v
python -m experiments.dependency_memory.rollback_patch_v9 prepare experiments/dependency_memory/results/rollback_patch_v9_2026-10-13/calibration_bundle --split calibration --per-family 4 --workers 32
python -m experiments.dependency_memory.rollback_patch_v9 run experiments/dependency_memory/results/rollback_patch_v9_2026-10-13/calibration_bundle experiments/dependency_memory/results/rollback_patch_v9_2026-10-13/calibration_live --live
python -m experiments.dependency_memory.rollback_patch_v9 audit experiments/dependency_memory/results/rollback_patch_v9_2026-10-13/calibration_bundle experiments/dependency_memory/results/rollback_patch_v9_2026-10-13/calibration_live experiments/dependency_memory/results/rollback_patch_v9_2026-10-13/calibration_live_replay_audit.json
python -m experiments.dependency_memory.rollback_patch_v9 prepare experiments/dependency_memory/results/rollback_patch_v9_2026-10-13/study_bundle --split study --seed 2026101392 --per-family 64 --workers 32 --gate-folder experiments/dependency_memory/results/rollback_patch_v9_2026-10-13/calibration_live
python -m experiments.dependency_memory.rollback_patch_v9 run experiments/dependency_memory/results/rollback_patch_v9_2026-10-13/study_bundle experiments/dependency_memory/results/rollback_patch_v9_2026-10-13/study_live --live
python -m experiments.dependency_memory.rollback_patch_v9 audit experiments/dependency_memory/results/rollback_patch_v9_2026-10-13/study_bundle experiments/dependency_memory/results/rollback_patch_v9_2026-10-13/study_live experiments/dependency_memory/results/rollback_patch_v9_2026-10-13/study_live_replay_audit.json
```

Preparation and replay require the already-installed pinned Docker image.
Live execution additionally requires restored included subscription quota and
passing actual-client preflight. Main preparation refuses a failed or unaudited
calibration. The sixteen-task control calibration permits at most 80 calls;
the 256-task factorial study permits at most 3,584. See saved evidence for which
steps have actually run, instead of interpreting these commands as outcomes.
