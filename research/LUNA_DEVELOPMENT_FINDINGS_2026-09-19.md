# Luna development findings and independent result check

September 19, 2026. The first bounded Luna development tranche completed under the [v0.4 launch contract](../docs/LUNA_DEVELOPMENT_RUN.md). This note reads the completed [summary](../experiments/dependency_memory/results/luna_development_2026-09-19/summary.json), [request ledger](../experiments/dependency_memory/results/luna_development_2026-09-19/requests.jsonl), and [manifest](../experiments/dependency_memory/results/luna_development_2026-09-19/manifest.json). The [generated report](../experiments/dependency_memory/results/luna_development_2026-09-19/report.md) contains every scheduled decision and episode.

The run used `gpt-5.6-luna` through the existing managed Codex subscription, low reasoning effort, and the default service tier. The model name is a mutable alias, not an immutable revision. All **96 attempted requests** completed valid decisions: 12 Stage-A inspection decisions and 84 requests across 36 Stage-B episodes. There were no policy or transport failures and no held-out requests. Every accepted response recorded the prescribed `session_budget_exceeded` harness termination; this is not a claim that 96 native agent turns completed normally.

## Inspection decisions against the exact reference

Ten of the 12 Stage-A choices matched the exact success-one reference with guaranteed optimal downstream retention. The two disagreements were opposite decisions in the revision cells, preserved as separate observations:

| Cell | Replicate | Actual choice | Exact preferred choice | Actual expected extra cost | Exact excess cost |
|---|---|---|---|---|---|
| `revision_cheap_recovery` | 1 | Inspect | Skip | 1 | 1/5 |
| `revision_costly_recovery` | 1 | Skip | Inspect | 8/5 | 3/5 |

Replicate 0 matched the reference in both cells. Both replicates also matched in the four other cells. Summed excess expected cost was **4/5 synthetic units**, or **1/15 per decision**. These fractions were recomputed directly from each stored Boolean response and the exact population calibration, rather than inferred from cell names. The repeated decisions are not independent task samples, and 10/12 is a descriptive development count rather than a general accuracy estimate.

## Retention, recovery, and realized cost

All 36 Stage-B episodes succeeded, but only **21/36** had the required current receipt before recovery; **15/36** used recovery. Reliable scripted recovery makes terminal success insensitive to even empty retention, as the prior fake-client control demonstrated. The informative differences here are availability and synthetic completion cost.

| Arm | Episodes / successes | Pre-recovery availability | Recoveries | Inspections | Total synthetic cost | Realized cost above same-choice fixed reference |
|---|---|---|---|---|---|---|
| Never inspect | 12 / 12 | 3/12 | 9 | 0 | 154 | 16 |
| Always inspect | 12 / 12 | 10/12 | 2 | 12 | 140 | 8 |
| Model selective | 12 / 12 | 8/12 | 4 | 7 | 137 | 4 |
| All arms | 36 / 36 | 21/36 | 15 | 19 | 431 | 28 |

The last column compares each completed episode with the policy fixed from the public routing population, using that episode's same inspection choice and exact fixture. It is a realized comparison on one route, **not an exact regret bound for Luna's full policy**. In particular, when child capacity is one and both candidates are available, either candidate is an optimal uniform-target tie choice. Losing this one realized target to a different tie choice does not establish a population retention error.

Selective cost was 17 units below never-inspect and three below always-inspect across these twelve paired development cases. The complete per-cell differences matter more than the aggregate:

| Cell | Mode | Selective minus never cost | Selective minus always cost |
|---|---|---|---|
| `ample_parent` | Explicit | 0 | -1 |
| `ample_parent` | Inferred | 0 | -1 |
| `cheap_recovery` | Explicit | 0 | 0 |
| `cheap_recovery` | Inferred | 0 | 0 |
| `costly_recovery` | Explicit | -3 | 0 |
| `costly_recovery` | Inferred | -3 | 0 |
| `revision_cheap_recovery` | Explicit | -3 | 0 |
| `revision_cheap_recovery` | Inferred | -3 | 0 |
| `revision_costly_recovery` | Explicit | 1 | 0 |
| `revision_costly_recovery` | Inferred | -7 | 0 |
| `small_child` | Explicit | 1 | 0 |
| `small_child` | Inferred | 0 | -1 |

These are synthetic action units, excluding model tokens, subscription accounting, and wall time. They do not establish dollar savings or improvement over a deployed harness.

## A concrete development issue to investigate

The public revision rule refreshes the lexicographically first member of the eventual candidate pair. Under six jobs, a two-record parent, a two-record child, and no early inspection, a fixed retained pair with indices `a,b` has ideal downstream pre-recovery availability `1/2 + (a+b)/30`. The first term covers the revised smaller candidate. For each retained job with index `j`, exactly `j` of the 30 equiprobable candidate/target routes need that unrevised larger candidate. Retaining `job-4` and `job-5` therefore gives 4/5, whereas `job-0`/`job-1` gives 8/15 and `job-1`/`job-2` gives 3/5. An offline enumeration of all 30 routes using these three fixed pairs independently reproduced those fractions; it made no further model calls.

In the revision never-inspect episodes, Luna retained `job-0`/`job-1` for cheap/inferred, `job-1`/`job-2` for cheap/explicit and costly/inferred, and `job-4`/`job-5` for costly/explicit. In the first three, the actual required `job-4` was already absent from the second request. The second selector could not restore its payload; recovery was needed later. The costly/explicit case retained both candidates after the refresh and avoided recovery.

This identifies a public-rule-sensitive parent-selection question for a future development amendment. It does not reveal Luna's internal reasoning, prove a specific dependency-inference failure, or justify editing and rerunning the completed tranche. A later diagnostic should distinguish understanding the asymmetric refresh rule from arbitrary tie selection under the symmetric no-revision condition, with a new frozen schedule and budget.

## Information and result checks

An independent read-only check of the completed artifacts found:

- All 96 public requests passed canonical reserialization and request-hash checks, with no inspected evaluator scenario, episode, route, seed, or reference-cost labels in the request text.
- Every stored response passed its strict host schema/selection validator; all completed rows recorded the expected guard termination and zero observed tool events.
- Across the 36 first/second retention pairs, 120 discarded-original-token checks found no deleted payload reappearing in a second request.
- All 36 pre-recovery outcomes were recomputed from the stored second-boundary visible records, selected keys, and latest required receipt. All synthetic costs were independently recomputed as mandatory cost 10, plus inspection when chosen, plus the configured recovery charge when unavailable. Every result matched the saved summary.

These checks concern saved public requests and provider metadata. They do not turn the synthetic complete-wire audit into a capture of production provider internals. Fixed global instructions, the three pure wrappers, and the rollout reminder remain declared public background under the launch contract.

The read-only [result-audit script](../scripts/audit_luna_results.py) reproduces these checks and the three 30-route parent-pair formula comparisons. Its [sanitized certificate](../experiments/dependency_memory/results/luna_development_2026-09-19/independent_audit.json) records the checked counts, exact arithmetic, result hashes, and script hash without request bodies or credentials. Reproduce it without model or network calls:

```powershell
python scripts/audit_luna_results.py --run-dir experiments/dependency_memory/results/luna_development_2026-09-19 --output experiments/dependency_memory/results/luna_development_2026-09-19/independent_audit.json
```

Manifest content hash: `a88f9e53d6a3f80fabb2f5f77900aa5c63c7d58d22b24a3704417b1826c4aadb`. Request-audit content hash: `7b4d83a3658ad913932f02bd682cd869f94177800886665f3a67e4604d579ef3`.

## Usage and accounting limits

The 96 completed attempts reported 276,048 input tokens, including 61,952 cached-input tokens, and 27,140 output tokens, including 24,944 reasoning-output tokens. Reasoning is not added to output again. Summed per-attempt measured latency was 1,057.09 seconds, including each attempt's surrounding client work; this is not a pure model-generation latency measure.

The conservative planning equivalent settled at **2.5395 credits** against the 20-credit-equivalent ceiling. The basic-rate estimate was **1.915656 credits**. There were no uncertain held reservations, credit purchases, or reset redemptions. The configured additional API spending allowance was US$0, with no API-key fallback. These equivalents are token-derived accounting estimates, not observed subscription debits or dollar invoices.

The optional cache-write counter is locally defaulted to zero if the app-server omits it. That value does **not** establish zero cache writes. The conservative budget charges all input at its 6.25-credit-per-million planning rate and retains the stated margin assumption; cache-write use and actual credit debit are not separately established by this run. Account limits and balance movement are shared with other work and cannot be wholly attributed to the experiment.

## Evidence boundary and next step

The first run establishes that the bounded managed-subscription interface executed the development schedule and exposed useful debugging differences. It does not establish general superiority, independent-trial significance, natural-task generalization, an LLM-optimal memory policy, or a native-compaction comparison. One synthetic template and one route were reused across modes, cells, and arms. The reserved held-out families remain unrun; even their eventual tiny sample is a debugging exercise.

Preserve this run unchanged. Any follow-up should first specify a new development question, such as the public revision asymmetry, then freeze its renderer/instructions, paired routes, accounting, and budget before another request. External mathematical review and novelty assessment remain separate open work.
