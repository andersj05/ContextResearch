# Experiment catalog

Generated from [registry.csv](registry.csv). Edit the registry, then run
`python scripts/build_experiment_index.py`. Dates describe the evidence checkpoint,
not when this index was built. Read [current status](../docs/STATUS.md) first.

A row is a study or diagnostic family, **not** an independent trial. Continuations
are grouped with their original study; dispatches, valid answers and host attempts
must not be added across overlapping reports. Plans and retrospective replays are
separate from observed model outcomes. Imported third-party releases are outside
this catalog; see [scope and maintenance](README.md).

## Model studies

[Read all 14 summaries](summaries/model-studies.md).

| Study | Evidence date | Status |
|---|---|---|
| [Rollback subscription adapter and E1 calibration](summaries/model-studies.md#rollback-subscription) | 2026-10-08 | completed |
| [Harder-task rollback development study](summaries/model-studies.md#rollback-recovery-v3) | 2026-10-08 | closed-with-gaps |
| [Corrected Python-language subscription engineering retest](summaries/model-studies.md#rollback-python-retest) | 2026-10-08 | completed |
| [Authored subscription rollback engineering pilot](summaries/model-studies.md#rollback-authored-pilot) | 2026-10-08 | completed |
| [Source-only scope inference and launch phases](summaries/model-studies.md#scope-inference) | 2026-10-01 | closed-with-gaps |
| [Executed-workflow comparison and stopped suffix](summaries/model-studies.md#workflow-executed) | 2026-09-29 | closed-with-gaps |
| [Observed-handoff development comparison](summaries/model-studies.md#workflow-live) | 2026-09-29 | completed |
| [Cross-record stress test and continuation](summaries/model-studies.md#cross-record) | 2026-09-22 | closed-with-gaps |
| [Different-schema prospective test](summaries/model-studies.md#schema-transfer) | 2026-09-22 | completed |
| [Annotated-schema transfer test](summaries/model-studies.md#schema-checks) | 2026-09-22 | completed |
| [Luna 6 memory pilot and prompt follow-up](summaries/model-studies.md#luna6-memory) | 2026-09-22 | completed |
| [Matched retention transfer study](summaries/model-studies.md#retention-transfer) | 2026-09-19 | closed-with-gaps |
| [Separate revision-direction diagnostic](summaries/model-studies.md#revision-diagnostic) | 2026-09-19 | completed |
| [First Luna development tranche](summaries/model-studies.md#luna-development) | 2026-09-19 | completed |

## Mathematical checks and coding constructions

[Read all 21 summaries](summaries/mathematical-checks.md).

| Study | Evidence date | Status |
|---|---|---|
| [Exact-priced larger-group construction](summaries/mathematical-checks.md#priced-code) | 2026-10-02 | completed |
| [Loss-weighted overflow and allocation bounds](summaries/mathematical-checks.md#weighted-overflow) | 2026-10-02 | completed |
| [Deterministic convergence construction](summaries/mathematical-checks.md#greedy-code) | 2026-10-02 | completed |
| [Coordinated equal-loss response construction](summaries/mathematical-checks.md#tie-code) | 2026-10-02 | completed |
| [Hard-cap entropy construction](summaries/mathematical-checks.md#entropy-code) | 2026-10-02 | completed |
| [Query-prior allocation and timing](summaries/mathematical-checks.md#query-priors) | 2026-10-02 | completed |
| [Conditional six-block construction](summaries/mathematical-checks.md#conditional-code) | 2026-10-02 | completed |
| [Finite trellis construction](summaries/mathematical-checks.md#trellis-code) | 2026-10-02 | completed |
| [Full unrestricted asymptotic rate curve](summaries/mathematical-checks.md#full-rate-curve) | 2026-10-02 | completed |
| [Balanced-source complementary completion](summaries/mathematical-checks.md#decoder-completion) | 2026-10-02 | completed |
| [Parent-rate support spectrum](summaries/mathematical-checks.md#parent-rate-spectrum) | 2026-10-01 | completed |
| [Unrestricted three-block converse](summaries/mathematical-checks.md#all-decoder-cover) | 2026-10-01 | completed |
| [Complementary three-block converse](summaries/mathematical-checks.md#complementary-cover) | 2026-10-01 | completed |
| [Restricted three-block converse](summaries/mathematical-checks.md#three-block-cover) | 2026-10-01 | completed |
| [Explicit three-block witness](summaries/mathematical-checks.md#three-block-witness) | 2026-10-01 | completed |
| [Decoder-complete rate-two frontier](summaries/mathematical-checks.md#decoder-frontier) | 2026-09-21 | completed |
| [Two-block witness and asymptotic threshold](summaries/mathematical-checks.md#joint-block) | 2026-09-21 | completed |
| [Exact four-bit chain optimum](summaries/mathematical-checks.md#exact-chain) | 2026-09-19 | completed |
| [Scaling, leave-one-out and independent proof checks](summaries/mathematical-checks.md#scaling-audit) | 2026-09-19 | completed |
| [Four-bit parent/child compatibility](summaries/mathematical-checks.md#parent-compatibility) | 2026-09-16 | completed |
| [Single-cut coding and reveal timing](summaries/mathematical-checks.md#single-cut) | 2026-09-16 | completed |

## Offline diagnostics and evidence replays

[Read all 17 summaries](summaries/offline-diagnostics.md).

| Study | Evidence date | Status |
|---|---|---|
| [Rollback E0 controller and grader verification](summaries/offline-diagnostics.md#rollback-e0) | 2026-10-08 | offline-complete |
| [Static source-analysis control](summaries/offline-diagnostics.md#scope-static) | 2026-10-01 | offline-complete |
| [Common-codec and cached-outcome controls](summaries/offline-diagnostics.md#scope-codebook) | 2026-10-01 | offline-complete |
| [Receipt-method redundancy and timing audit](summaries/offline-diagnostics.md#workflow-method) | 2026-10-01 | offline-complete |
| [Observed workflow intake E0001](summaries/offline-diagnostics.md#workflow-intake) | 2026-10-01 | offline-complete |
| [Retained-evidence decision audit](summaries/offline-diagnostics.md#evidence-use) | 2026-10-01 | offline-complete |
| [Decoder-compatible handoff correction](summaries/offline-diagnostics.md#decoder-handoff) | 2026-09-24 | offline-complete |
| [Historical workflow replay](summaries/offline-diagnostics.md#historical-replay) | 2026-09-22 | offline-complete |
| [Independent strategy/coloring reformulation](summaries/offline-diagnostics.md#novelty-reduction) | 2026-09-22 | offline-complete |
| [Feedback before forgetting](summaries/offline-diagnostics.md#feedback-loop) | 2026-09-22 | offline-complete |
| [Finite collision auditor](summaries/offline-diagnostics.md#collision-audit) | 2026-09-21 | offline-complete |
| [Held-out clue renderer checkpoint](summaries/offline-diagnostics.md#heldout-renderers) | 2026-09-19 | offline-complete |
| [Post-hoc grading of original selections](summaries/offline-diagnostics.md#revision-replay) | 2026-09-19 | offline-complete |
| [Development pilot fake-client controls](summaries/offline-diagnostics.md#pilot-fake-controls) | 2026-09-19 | offline-complete |
| [Exact restricted recovery frontier](summaries/offline-diagnostics.md#recovery-frontier) | 2026-09-19 | offline-complete |
| [Scripted artifact/manifest environment](summaries/offline-diagnostics.md#artifact-workflow) | 2026-09-18 | offline-complete |
| [Record-retention baseline diagnostic](summaries/offline-diagnostics.md#record-retention) | 2026-09-16 | offline-complete |

## Prepared studies and unperformed evaluations

[Read all 4 summaries](summaries/planned-studies.md).

| Study | Evidence date | Status |
|---|---|---|
| [Luna rollback experiment design and review](summaries/planned-studies.md#rollback-pilot) | 2026-10-08 | prepared |
| [Prospective workflow method v1](summaries/planned-studies.md#prospective-method) | 2026-10-01 | prepared |
| [Observed-workflow evaluation packet](summaries/planned-studies.md#workflow-evaluation-plan) | 2026-09-29 | prepared |
| [Historical staged pilot and held-out extension](summaries/planned-studies.md#pilot-plan) | 2026-09-19 | prepared |

## Shared infrastructure and verification records

[Read all 2 summaries](summaries/infrastructure.md).

| Study | Evidence date | Status |
|---|---|---|
| [October 2 scientific checkpoint](summaries/infrastructure.md#october-closeout) | 2026-10-02 | checkpoint |
| [Shared transport and preparation audits](summaries/infrastructure.md#runtime-support) | 2026-10-01 | offline-complete |
