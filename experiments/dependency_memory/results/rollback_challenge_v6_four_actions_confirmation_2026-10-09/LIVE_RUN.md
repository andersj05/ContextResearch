# Fixed four-action rollback comparison

Closed 2026-10-10T03:09:05.759896+00:00. Rollback has lower task success under the prespecified exact paired decision. The result survives every feasible completion of missing binary scores.

## Fixed cohort and primary decision

The run contains exactly 260 new intermediate-profile level-2 ledger tasks,
520 K/R episodes, three stages and four actions per episode. Its
[cohort and analysis envelope](confirmation_envelope.json) froze before the
first live R dispatch, after independent K=9/16 and F=12/16 validation.
All 520 scheduled episodes have final dispositions; no interim effect check, significance
stopping, task replacement or sample extension was used.

| Arm | Known successes | Known-score rate | Descriptive Wilson 95% interval on known scores | Missing scores | Episodes with public mismatch |
|---|---:|---:|---:|---:|---:|
| K | 122/254 | 48.03% | 42.0%–54.2% | 6 | 200 |
| R | 64/258 | 24.81% | 19.9%–30.4% | 2 | 203 |

There are 252/260 complete pairs: 29 R-only successes and
87 K-only successes. The sharp fixed-denominator R-minus-K
effect bounds are **[-24.62, -21.54] percentage points**.
These describe uncertainty from missing scores; they are not population
confidence intervals. Known-score arm intervals do not resolve missingness
and carry no population-coverage guarantee under outcome-dependent missingness.

The primary maximum-completion exact two-sided paired p-value is
**2.4820775e-07**, compared with alpha 0.05.
The complete-case exact p-value is 6.4715304e-08; when
outcomes are missing it is descriptive. No missing score is imputed.
The [prospectively amended analysis](amended_primary_analysis.json) preserves
the [standard engine analysis](live_confirmation/analysis.json) separately.

## Execution, replay and resources

[Independent replay](live_confirmation_audit.json) passes for every saved
response, job, grade, source binding and accounting record. There are
2,496 metered completions and
8 retained unknown admissions. The global
stop field is `null` (no global stop). Runtime is 206.3 minutes,
excluding preflight. Per-arm dispositions are:

```json
{
  "K": {
    "action_budget_exhausted": 132,
    "correct": 122,
    "infrastructure_stop": 6
  },
  "R": {
    "action_budget_exhausted": 194,
    "correct": 64,
    "infrastructure_stop": 2
  }
}
```

The following resource comparison uses only the same 252 complete-pair
tasks and includes each arm's lesson-writer calls. It is descriptive.

| Resource | K | R | R relative to K |
|---|---:|---:|---:|
| Input tokens | 6,503,361 | 5,920,991 | -8.95% |
| Output tokens, including reasoning | 2,019,225 | 1,987,907 | -1.55% |
| Planning credits | 37.672 | 35.855 | -4.82% |

Across every known call, usage is 12,732,738 input
tokens including 3,476,480 cached, and
4,110,434 output tokens including
3,810,659 reasoning. The declared conversion yields
75.3901900 planning credits. These are accounting units,
not actual subscription charges; charges are unavailable. Every admitted
action, writer and unknown counts in the campaign total of
3,698 admissions.

## Interpretation limits

This estimates the whole rollback policy on one authored task family with
independent K/R model draws and lesson writers. R deletes all visible raw
trial history after a mismatch while retaining lessons, current feedback and
the last accepted artifact. It does not roll back model weights or establish
how inaccessible provider state works. Each action/writer uses a fresh thread
with tools disabled and no archive or opaque-state replay.

The result does not establish new-family generalization, population
equivalence, or a deployed-harness benefit. The original power calculation
assumed a ten-point effect, 30% discordance and complete observation; it is
not an assurance of empirical power, especially with missing outcomes.
Immutable provider revision and sampling seed are unavailable. Earlier
calibration choices used K/F controls only and remain fully recorded.

Read [closeout](confirmation_closeout.json), [execution](live_confirmation/execution.json),
[sealed inventory](live_confirmation/evidence_manifest.json), [manifest](prepared/manifest.json),
[readiness](readiness.json), and the [frozen analysis](confirmation_analysis_precommit.json).
