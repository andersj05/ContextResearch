# Rollback challenge v6

Three new authored task families, exact graders, independent checks, a parallel
subscription runner, immutable freezes, receipt replay, control-only calibration
and a fixed-size paired test. **Difficulty is unmeasured until live calibration.**
The existing v5 experiment is not modified or reopened. See the [protocol](PROTOCOL.md).

## Task examples

- **Constraint grid:** complete a 4x4, 6x6 or 9x9 grid subject to row/column/box
  uniqueness, irregular cage sums, inequalities and gradually released givens.
- **Bitvector program:** find at most 3, 5 or 7 add/XOR/multiply/rotate operations
  matching a growing table of input/output examples. Any matching program passes.
- **Revision ledger:** reconcile balances across 18, 40 or 80 transaction IDs
  with out-of-order replacements and voids. Later packets revise earlier data.

All candidates are integer arrays. The program DSL runs in a finite interpreter;
there is no execution of arbitrary model-supplied Python. Private witnesses and
future packets stay out of actor requests. The ledger and grid families provide
different sources of history dependence; difficulty does not rely on padding.

## Offline preparation and verification

Run from the repository root with the existing Python installation. No new Python
packages, API key or Docker setup are needed for these finite task families.
Live dispatch uses the existing audited Luna-medium subscription client.

```powershell
python -m unittest experiments.dependency_memory.rollback_challenge_v6.test_challenge -v
python -m experiments.dependency_memory.rollback_challenge_v6.run prepare --output tmp/v6-screen --max-calls 414
python -m experiments.dependency_memory.rollback_challenge_v6.run preview --bundle tmp/v6-screen --task-index 0
python -m experiments.dependency_memory.rollback_challenge_v6.run simulate --bundle tmp/v6-screen --output tmp/v6-fixture --workers 4
python -m experiments.dependency_memory.rollback_challenge_v6.run audit --bundle tmp/v6-screen --run tmp/v6-fixture
python -m experiments.dependency_memory.rollback_challenge_v6.run power --effect .10 --discordance .30 --output tmp/v6-power.json
```

Use fresh paths for every preparation/run. A source change invalidates an existing
freeze. Simulation explicitly uses oracle fixtures; it cannot establish difficulty,
select live cells or produce a confirmatory p-value.

A smaller initial screen fits a 300-generation allocation:

```powershell
python -m experiments.dependency_memory.rollback_challenge_v6.run prepare --output tmp/v6-small-screen --stages 3 --actions 5 --max-calls 300
```

This has 18 tasks and at most 252 generations, including all K lessons. The later
validation must use the same three-stage/five-action settings. Validation and
confirmation need separate allocations; a screen alone does not satisfy them.

## Live screen, separate difficulty validation, then confirmation

After the model and bounded subscription allocation are settled, the runner
refreshes client/account checks and audits actual prompts against a loopback
endpoint before its first generation. No purchase or provider/model fallback.

```powershell
python -m experiments.dependency_memory.rollback_challenge_v6.run launch --bundle tmp/v6-screen --output tmp/v6-screen-live --workers 4 --live
python -m experiments.dependency_memory.rollback_challenge_v6.run audit --bundle tmp/v6-screen --run tmp/v6-screen-live
python -m experiments.dependency_memory.rollback_challenge_v6.run select --bundle tmp/v6-screen --run tmp/v6-screen-live --output tmp/v6-selected.json
python -m experiments.dependency_memory.rollback_challenge_v6.run prepare --split validation --seed 2026100929 --replicates 8 --selection tmp/v6-selected.json --output tmp/v6-validation
```

If no cell qualifies, the selection is empty and validation cannot launch. If
some qualify, launch and audit the separately budgeted validation bundle, then:

```powershell
python -m experiments.dependency_memory.rollback_challenge_v6.run validate --bundle tmp/v6-validation --run tmp/v6-validation-live --selection tmp/v6-selected.json --output tmp/v6-validated.json
```

Context-capacity failures stay in reported outcomes and denominators. A cell
with such a failure in K or F cannot be nominated, and a capacity failure during
validation prevents the entire nominated mixture from advancing. This avoids
mistaking a request-admission limit for model difficulty.

Confirmation preparation requires `--selection tmp/v6-validated.json`,
`--power-plan tmp/v6-power.json`, a new `--seed`, `--split confirmation`, and
enough `--replicates` per selected cell to cover the planned pair count. For
example, three selected cells and a 260-pair plan require 87 replicates per cell
(261 tasks). `--arms K R` is the minimum primary comparison. Add Z/G/F before
freezing if descriptive controls are needed. The CLI prints the full maximum
generation allocation before any live call; `--max-calls` enforces a chosen cap.

The fixed primary test can detect an effect in either direction. It does not
promise a benefit or statistical significance. Complete-case tests with missing
outcomes and all calibration analyses remain descriptive.

## Evidence and recovery

Each bundle saves task and source snapshots plus independent grader verification.
Each run saves requests, responses, job outcomes, analysis, SQLite metering and
a sealed inventory. All failed/unknown tasks retain their fixed denominators.
Inspect `analysis.json` for control success intervals, failure eligibility,
realized history bytes, paired outcomes and complete-pair resource totals.

A sealed global-stop run may be continued with `--prior <old-run>` and a fresh
output path. Known calls are replayed locally; unknown identities are never
resent. A completed allocation cannot be extended. Unsealed/crashed execution
must first be reconciled; never delete its launch marker to rerun it.

After code evolves, `audit --snapshot --bundle <bundle> --run <run>` verifies
the archive and replays using its historical source in a temporary directory.
Live dispatch and difficulty selection still require the current source to match
the frozen bundle. Historical replay cannot authorize a changed live allocation.

## Follow-up after the first live screen

The [completed screen](../results/rollback_challenge_v6_2026-10-09/LIVE_SCREEN.md)
is below the old ceiling, but nominates no cells: most known failures use the
allowed `continue` response without a checker rejection. A new screen can require
the model's best complete candidate on every action, without requesting deliberate
mistakes. This changes the response contract and uses new task identities.

```powershell
python -m experiments.dependency_memory.rollback_challenge_v6.run prepare --seed 2026100943 --cells bitvector_program:1 constraint_grid:2 revision_ledger:2 --replicates 2 --stages 3 --actions 5 --require-candidates --max-calls 84 --output tmp/v6-candidate-screen
```

This prepares six tasks and twelve K/F episodes; it makes no model calls. The
follow-up is covered by the user's later broad Luna authorization. Later validation/confirmation inherit
the selected response contract automatically and reject an incompatible override.
Analysis now reports candidate and progress-only action counts per control cell.
Use `audit --snapshot` for the original screen after these source changes.

The completed six-task follow-up also nominates no cells under its original
gate. A new, explicitly frozen `--allow-fresh-ceiling` option retains K's
non-ceiling requirement while allowing F to establish solvability at 100%.
It cannot reclassify a closed screen. The [protocol](PROTOCOL.md) specifies the
new screening and independent-validation rates and their rationale. The flag
is inherited by later phases and never appears in actor inputs.

```powershell
python -m experiments.dependency_memory.rollback_challenge_v6.run prepare --seed 2026100959 --cells bitvector_program:2 bitvector_program:3 constraint_grid:2 constraint_grid:3 revision_ledger:2 revision_ledger:3 --replicates 4 --stages 3 --actions 5 --require-candidates --allow-fresh-ceiling --max-calls 336 --output tmp/v6-headroom-screen
```

This next development screen has 24 tasks and 48 K/F episodes. Use sixteen
independent validation tasks per selected cell and freeze confirmation size
before inspecting R/K outcomes. The user's authorization for thousands of Luna
requests covers these bounded stages without asking again before each run.

## Intermediate ledger sizes and conservative missing-score calibration

The independent forty-transaction validation is too difficult (K=3/16), and
allowing six actions yields K=2/8 with one missing F score. Both original gate
decisions remain closed. A new `--ledger-profile intermediate` provides
22/28/34 transaction IDs over 5/6/7 accounts while retaining the same exact
ledger rules. It is restricted to ledger tasks, uses distinct task identities
and is inherited by validation and confirmation. The standard profile is
unchanged.

For newly frozen controls, `--robust-control-missingness` requires the entire
fixed-denominator success interval to satisfy the rate gate, whether each
missing score is a pass or failure. At least seven eighths of scores must be
known, with at least eight scheduled tasks per screening cell and sixteen per
validation cell. Public mismatches, whole-mixture and capacity checks remain;
a global stop blocks eligibility. This flag changes only calibration and is
inherited unchanged. It does not retry or impute unknown outcomes and does not
reclassify old selections. See the [prospective protocol](PROTOCOL.md).

```powershell
python -m experiments.dependency_memory.rollback_challenge_v6.run prepare --seed 2026101001 --cells revision_ledger:2 --ledger-profile intermediate --replicates 8 --stages 3 --actions 5 --require-candidates --allow-fresh-ceiling --robust-control-missingness --max-calls 112 --output tmp/v6-intermediate-screen
```
