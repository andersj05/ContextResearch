# Thirty-four-transaction validation fails the K lower bound

October 9, 2026. All 32 K/F episodes finish with 181 known calls and no unknowns
or global stop. [Independent replay](live_validation_audit.json) passes for every
response, grade, outcome and accounting record. Elapsed time is 1,080.0 seconds
excluding preflight.

| Control | Success | Rate | Wilson 95% interval | Public mismatch episodes |
|---|---:|---:|---:|---:|
| K | 5/16 | 31.25% | 14.2–55.6% | 16/16 |
| F | 9/16 | 56.25% | 33.2–76.9% | 12/16 |

The [frozen validation gate](validated_selection.json) fails because K is below
40%. There are no malformed-record or capacity failures, and all scores are
known, so the missing-score rule does not affect the decision. The selected
cell is not dropped or reclassified; it cannot authorize confirmation.
No R arm has been observed and no rollback effect is estimated.

The next [four-action screen](../rollback_challenge_v6_four_actions_2026-10-09/README.md)
uses new 28-transaction tasks. Earlier completion timings motivate its action
allowance, but do not measure behavior under that new allowance. It must screen
and validate independently before a fixed comparison.

Known usage is 1,335,222 input tokens including 266,240 cached, and 410,246
output tokens including 391,134 reasoning. The declared conversion yields
7.8670900 planning credits, not actual charges. All 181 calls count in the
[campaign ledger](../rollback_challenge_v6_candidates_2026-10-09/campaign_budget.json),
bringing admissions to 1,004, including the prior single unknown. Read
[closeout](control_closeout.json), [analysis](live_validation/analysis.json),
[execution](live_validation/execution.json), [manifest](prepared/manifest.json),
and [sealed inventory](live_validation/evidence_manifest.json).
