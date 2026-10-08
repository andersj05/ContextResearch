# Mathematical rollback follow-up

The [protocol](PROTOCOL.md) freezes a new 32-task mathematical development cohort
after the [interrupted v3 study](../../../research/ROLLBACK_HARDER_DEVELOPMENT_2026-10-08.md).
Actor prompts, effort, isolation and acceptance checks are unchanged. The transport
adds whitelisted event counts and protocol reason codes without storing raw
provider/session logs. This is a separate allocation with no old task or identity.

Results belong in
[the dated package](../results/rollback_math_followup_v4_2026-10-08/).
There are eight excluded calibration calls and 416 possible task calls. Every
task is retained; unknown dispatch stops the entire cohort with no retry.

```powershell
python -m experiments.dependency_memory.rollback_math_followup_v4.checks --output <fresh-checks.json>
python -m experiments.dependency_memory.rollback_math_followup_v4.prepare_checks math --output <math_checks.json>
python -m experiments.dependency_memory.rollback_math_followup_v4.preflight --executable <pinned-codex.exe> --global-instructions <fixed-global-AGENTS.md> --scratch-root <scratch> --output <preflight.json>
python -m experiments.dependency_memory.rollback_math_followup_v4.run freeze --folder <fresh-launch-folder> --preflight <preflight.json> --math-checks <math_checks.json>
python -m experiments.dependency_memory.rollback_math_followup_v4.run launch --folder <frozen-launch-folder> --executable <pinned-codex.exe> --global-instructions <fixed-global-AGENTS.md> --scratch-root <actor-scratch>
python -m experiments.dependency_memory.rollback_math_followup_v4.verify --folder <closed-launch-folder> --regrade --output <fresh-verification.json>
```

The completed October 8 archive binds the original README from commit `1e927f8`.
This public copy received a relative-link repair after execution. Verify that
archive through [historical source replay](../../../scripts/verify_rollback_math_v4.py),
which reconstructs all original source bytes and runs the unchanged verifier:

```powershell
python scripts/verify_rollback_math_v4.py --folder experiments/dependency_memory/results/rollback_math_followup_v4_2026-10-08/launch_v4 --regrade --output <fresh-verification.json>
```

Results concern these three mathematical construction strata, conditional on
observed eligibility. No coding, benchmark, native-harness or manuscript upgrade
follows. The earlier unknown reservation remains unresolved and separate.
