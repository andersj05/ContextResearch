# Rollback development v5: staged tasks and parallel runner

**Prepared development software; no live study has run.** Read the
[protocol](PROTOCOL.md) before launching. There are 48 seeded tasks, 24 math and
24 real two-module Python repairs, at two difficulty settings and three horizons.
The short control has one disclosure and two actions; medium/long tasks have
four/eight disclosures and ten/thirty actions. Difficulty remains uncalibrated
until Luna runs. Scripted test successes are not model evidence.

The separately analysed tracks are a seven-arm matched-failure mechanism study,
five independently started complete policies, and three policies with repeated
scheduled memory cuts. All use Luna medium. The default is four parallel workers,
with an audited global admission bound and no automatic retries. A failed/unknown
call stops new work while already admitted calls finish.

## Files

- [Task generation](tasks.py), [mathematical rules](math_tasks.py) and
  [two-module coding projects](coding_tasks.py).
- [Visible contexts](contexts.py), [episode controller](engine.py),
  [parallel scheduler](schedule.py), [accounting](accounting.py),
  [subscription adapter](dispatch.py).
- [Independent verification](verification.py), [client preflight](preflight.py),
  [excluded calibration](calibration.py), [invariant tests](test_design.py),
  [explicitly scripted simulation](simulation.py), [analysis](analysis.py).
- [Command entry point](run.py), [immutable preparation](prepare.py).

The canonical [preparation evidence](../results/rollback_development_v5_2026-10-08/README.md)
contains the frozen 48-task catalog, retained source snapshot and offline checks.

## Prepare and check

Run from the repository root. Use new output directories; frozen bundles and
launched identities are never overwritten.

```powershell
python -m unittest experiments.dependency_memory.rollback_development_v5.test_design -v
python -m experiments.dependency_memory.rollback_development_v5.run prepare --bundle tmp/v5-review
python -m experiments.dependency_memory.rollback_development_v5.run verify --bundle tmp/v5-review
python -m experiments.dependency_memory.rollback_development_v5.run simulate --bundle tmp/v5-review --output tmp/v5-simulation --workers 4
python -m experiments.dependency_memory.rollback_development_v5.run audit --bundle tmp/v5-review --output tmp/v5-simulation
python -m experiments.dependency_memory.rollback_development_v5.run preflight --bundle tmp/v5-review --output tmp/v5-client-check
```

`verify` needs the existing digest-pinned Docker runtime. `preflight` reads the
existing subscription account/model availability and exercises the installed
client against an **unauthenticated local mock**; it generates no model output.
It may require execution outside the Codex workspace sandbox for local Docker
and app-server access. Neither command purchases credits or requests an API key.

`simulate` uses disclosed oracle fixtures and synthetic token usage. Its fake
actor deliberately fails the first attempt to test all recovery routes. That
behavior is confined to the fixture; live prompts explicitly prohibit fabricated
failures. Its coding runner recognizes authored reference programs and does not
execute code on the host. Actual reference execution is separately checked by
`verify` inside Docker.

## Later live launch

The requested preparation does not launch Luna. After choosing the launch time,
the prepared bundle supports one explicit command:

```powershell
python -m experiments.dependency_memory.rollback_development_v5.run launch --bundle experiments/dependency_memory/results/rollback_development_v5_2026-10-08/prepared --output experiments/dependency_memory/results/rollback_development_v5_2026-10-08/live --workers 4 --live
```

The launch refreshes account/client preflight, verifies all source/task bindings,
runs eight excluded format/transport calibration requests, and only then admits
the task jobs. It uses the installed `codex.exe`, existing ChatGPT subscription,
and declared global instructions. No API key, model fallback or purchase fallback.
Model alias revision and provider sampling seed remain unavailable. A later
client/source change causes a stop and requires a newly reviewed preparation.

With all tracks, 768 possible jobs reuse 48 tasks. There are 16,904 frozen call
identities including calibration, with a tighter 13,640-generation state-machine
ceiling; early successes generally leave many unused. These are allocation
bounds, not independent trials or expected consumption. Four workers is the
default for bounded concurrency; `--workers 8` is supported by the central ledger.
Account limits can still stop a run. Do not run multiple copies of the launcher.

## Outputs and interpretation

Requests, typed responses, the durable ledger, every job/slot disposition,
analysis and an evidence inventory are saved under the new output directory.
`audit` reconstructs the requests and outcomes, reconciles every known call and
usage total, and checks that the saved analysis follows those recorded outcomes.
An incomplete or unreplayable archive fails verification; it cannot acquire a
successful audit simply because its hashes are internally consistent.
Study summaries separate conditional recovery from whole-policy success and
from repeated compression. All strata and controls remain visible; preparation
losses, capacity failures and missing outcomes are not quietly discarded.

Candidate-action and call allowances are matched; exact tokens, output reasoning,
writer overhead and latency are measured. This is not a fixed-dollar experiment,
and planning credits are not actual account charges. Historical v3/v4 evidence
and their unresolved reservations remain unchanged.
