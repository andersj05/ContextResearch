# Revision-aware retention: offline analysis of the completed Luna run

September 19, 2026. This analysis reuses the saved development requests. It makes **zero new model calls** and leaves the original run unchanged.

All **36 first-boundary selections** were graded against the best atomic-record parent with the same inspection choice and public view. The 17 uninspected selections each face all 30 equiprobable candidate/target routes. For the 19 inspected selections, the visible manifest fixes the pair, leaving two possible targets. Grading those answers across unobserved manifests would invent counterfactual model behavior.

There are **3 strict parent-selection deficits**, all in uninspected revision cases. The other 33 selections attain their same-view ideal-child reference. All 36 observed second-boundary selections are optimal conditional on the records actually visible there; this does not establish optimal child choices on unseen routes.

| Scenario | Rendering | First keys | Exact availability | Best same-view availability | Availability gap | Expected recovery-cost gap |
|---|---|---|---|---|---|---|
| revision_cheap_recovery | explicit_labels | job-1, job-2 | 3/5 | 4/5 | 1/5 | 4/5 |
| revision_cheap_recovery | inferred_dependencies | job-0, job-1 | 8/15 | 4/5 | 4/15 | 16/15 |
| revision_costly_recovery | inferred_dependencies | job-1, job-2 | 3/5 | 4/5 | 1/5 | 8/5 |

The cost gaps use each row's recovery price and hold inspection fixed. They are exact losses of these fixed parent choices with an optimal child selector, not estimates of total model-policy regret. Pooling the three gaps across reused prompts would not create independent trials.

## Why the public revision rule changes the best parent

Let n jobs be ordered lexicographically with ranks 0 through n−1. A pair is uniform among all unordered pairs, and its final target is uniform within the pair. With at least two child slots, no revision, and a fixed retained set F, ideal downstream availability is |F|/n: all equal-size parent sets tie. With revision of the smaller candidate, the refreshed target supplies 1/2 availability independently of F. A retained rank j is the unrevised larger candidate in exactly j pairs, so

```text
p(F; revised, child capacity ≥ 2) = 1/2 + sum(j for j in F) / [n(n−1)].
```

For n=6 and two parent slots, ranks 4 and 5 uniquely maximize this expression at 4/5. Ranks 0 and 1 give 8/15; ranks 1 and 2 give 3/5. Thus choosing the smallest keys is harmless under the symmetric no-revision population but strictly worse under this particular revision schedule.

With one child slot and no revision, availability is [C(n,2) − C(n−|F|,2)] / [n(n−1)]; equal-size parents still tie. With one child slot and revision it is exactly 1/2 for every parent, because one fresh candidate is always available and the second boundary can retain only one. Zero child capacity gives zero availability. Six parent slots preserve all initial records; child capacity then supplies the binding limit. The JSON includes all 32 combinations of revision on/off and parent/child capacities 0, 1, 2, and 6, with full-capacity value distributions. These are offline controls, not model observations.

## Every saved selection

`Population` means all 30 routes before any manifest; `Manifest` means the two targets of the already visible pair. The exact fractions assume optimal downstream retention. Actual availability is the outcome on the single realized route.

| Scenario | Rendering | Arm | View | First keys | Exact / best | Parent gap | Actual available | Child gap on observed view |
|---|---|---|---|---|---|---|---|---|
| ample_parent | explicit_labels | always_inspect | Manifest | 0, 1, 2, 3, 4, 5 | 1 / 1 | 0 | True | 0 |
| ample_parent | explicit_labels | model_selective | Population | 0, 1, 2, 3, 4, 5 | 1 / 1 | 0 | True | 0 |
| ample_parent | explicit_labels | never_inspect | Population | 0, 1, 2, 3, 4, 5 | 1 / 1 | 0 | True | 0 |
| ample_parent | inferred_dependencies | always_inspect | Manifest | 0, 1, 2, 3, 4, 5 | 1 / 1 | 0 | True | 0 |
| ample_parent | inferred_dependencies | model_selective | Population | 0, 1, 2, 3, 4, 5 | 1 / 1 | 0 | True | 0 |
| ample_parent | inferred_dependencies | never_inspect | Population | 0, 1, 2, 3, 4, 5 | 1 / 1 | 0 | True | 0 |
| cheap_recovery | explicit_labels | always_inspect | Manifest | 2, 4 | 1 / 1 | 0 | True | 0 |
| cheap_recovery | explicit_labels | model_selective | Population | 0, 1 | 1/3 / 1/3 | 0 | False | 0 |
| cheap_recovery | explicit_labels | never_inspect | Population | 0, 1 | 1/3 / 1/3 | 0 | False | 0 |
| cheap_recovery | inferred_dependencies | always_inspect | Manifest | 2, 4 | 1 / 1 | 0 | True | 0 |
| cheap_recovery | inferred_dependencies | model_selective | Population | 0, 1 | 1/3 / 1/3 | 0 | False | 0 |
| cheap_recovery | inferred_dependencies | never_inspect | Population | 0, 1 | 1/3 / 1/3 | 0 | False | 0 |
| costly_recovery | explicit_labels | always_inspect | Manifest | 2, 4 | 1 / 1 | 0 | True | 0 |
| costly_recovery | explicit_labels | model_selective | Manifest | 2, 4 | 1 / 1 | 0 | True | 0 |
| costly_recovery | explicit_labels | never_inspect | Population | 0, 1 | 1/3 / 1/3 | 0 | False | 0 |
| costly_recovery | inferred_dependencies | always_inspect | Manifest | 2, 4 | 1 / 1 | 0 | True | 0 |
| costly_recovery | inferred_dependencies | model_selective | Manifest | 2, 4 | 1 / 1 | 0 | True | 0 |
| costly_recovery | inferred_dependencies | never_inspect | Population | 0, 1 | 1/3 / 1/3 | 0 | False | 0 |
| revision_cheap_recovery | explicit_labels | always_inspect | Manifest | 2, 4 | 1 / 1 | 0 | True | 0 |
| revision_cheap_recovery | explicit_labels | model_selective | Manifest | 2, 4 | 1 / 1 | 0 | True | 0 |
| revision_cheap_recovery | explicit_labels | never_inspect | Population | 1, 2 | 3/5 / 4/5 | 1/5 | False | 0 |
| revision_cheap_recovery | inferred_dependencies | always_inspect | Manifest | 2, 4 | 1 / 1 | 0 | True | 0 |
| revision_cheap_recovery | inferred_dependencies | model_selective | Manifest | 2, 4 | 1 / 1 | 0 | True | 0 |
| revision_cheap_recovery | inferred_dependencies | never_inspect | Population | 0, 1 | 8/15 / 4/5 | 4/15 | False | 0 |
| revision_costly_recovery | explicit_labels | always_inspect | Manifest | 2, 4 | 1 / 1 | 0 | True | 0 |
| revision_costly_recovery | explicit_labels | model_selective | Manifest | 2, 4 | 1 / 1 | 0 | True | 0 |
| revision_costly_recovery | explicit_labels | never_inspect | Population | 4, 5 | 4/5 / 4/5 | 0 | True | 0 |
| revision_costly_recovery | inferred_dependencies | always_inspect | Manifest | 2, 4 | 1 / 1 | 0 | True | 0 |
| revision_costly_recovery | inferred_dependencies | model_selective | Manifest | 2, 4 | 1 / 1 | 0 | True | 0 |
| revision_costly_recovery | inferred_dependencies | never_inspect | Population | 1, 2 | 3/5 / 4/5 | 1/5 | False | 0 |
| small_child | explicit_labels | always_inspect | Manifest | 2, 4 | 1/2 / 1/2 | 0 | False | 0 |
| small_child | explicit_labels | model_selective | Manifest | 2, 4 | 1/2 / 1/2 | 0 | False | 0 |
| small_child | explicit_labels | never_inspect | Population | 0, 1 | 3/10 / 3/10 | 0 | False | 0 |
| small_child | inferred_dependencies | always_inspect | Manifest | 2, 4 | 1/2 / 1/2 | 0 | False | 0 |
| small_child | inferred_dependencies | model_selective | Population | 0, 1 | 3/10 / 3/10 | 0 | False | 0 |
| small_child | inferred_dependencies | never_inspect | Population | 0, 1 | 3/10 / 3/10 | 0 | False | 0 |

The three inspected small-child episodes that missed the realized target are target tie outcomes, not conditional expectation deficits. The no-inspection, no-revision choices likewise cannot be called parent errors merely because their chosen pair missed this route. The strict revision deficits are different: their ranking is worse across the declared population, even before knowing the realized pair.

## Reproduction and limits

```powershell
python experiments/dependency_memory/revision_analysis.py
python -m unittest discover -s experiments/dependency_memory -p test_revision_analysis.py -v
```

Source requests and summaries are hashed in [the JSON certificate](revision_analysis.json). Original evidence is in [the Luna run report](luna_development_2026-09-19/report.md). The calculations distinguish first-boundary loss from second-boundary choice using saved public requests only. They do not identify model reasoning, establish a population success rate for its unobserved policy, measure a new intervention, or use held-out tasks.
