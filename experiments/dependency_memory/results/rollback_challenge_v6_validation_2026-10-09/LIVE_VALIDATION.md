# Five-action ledger validation fails its difficulty gate

October 9, 2026. All 32 K/F episodes finish with 190 known calls, no unknowns
and no global stop. [Independent replay](live_validation_audit.json) reproduces
every response, grade, outcome and accounting record. Elapsed time is 1,442.1
seconds excluding preflight.

| Control | Successes | Rate | Wilson 95% interval | Public mismatch episodes |
|---|---:|---:|---:|---:|
| K: retained history plus lessons | 3/16 | 18.75% | 6.6–43.0% | 16/16 |
| F: fresh public dossier | 7/16 | 43.75% | 23.1–66.8% | 15/16 |

The [frozen gate](validated_selection.json) fails because K is below the required
40–75% range. F meets its lower bound. All outcomes are known, with no malformed
records or context-capacity failures. No task is dropped, and this selection
cannot authorize a confirmation run. The earlier K=2/4 screen was too small to
establish stable intermediate difficulty; this independent result preserves that
uncertainty rather than reclassifying the gate.

Twelve of thirteen K failures had passed the first two stages when the five-action
budget expired; one had passed only the first stage. All nine F failures had
passed two stages. This motivates a [separate six-action screen](../rollback_challenge_v6_six_actions_2026-10-09/README.md)
on new tasks. It does not establish that another action will help. No R outcomes
have been observed, and no rollback effect or significance is estimated here.

Known usage is 1,380,397 input tokens, including 290,560 cached, and 484,822
output tokens, including 465,616 reasoning. The declared conversion yields
8.8575075 planning credits, not an actual subscription charge. All 190 calls
count in the [campaign budget](../rollback_challenge_v6_candidates_2026-10-09/campaign_budget.json),
bringing admissions under the broad authorization to 563.

Read [analysis](live_validation/analysis.json), [execution](live_validation/execution.json),
[manifest](prepared/manifest.json), [sealed inventory](live_validation/evidence_manifest.json),
and [original prospective design](README.md). The failed validation remains closed.
