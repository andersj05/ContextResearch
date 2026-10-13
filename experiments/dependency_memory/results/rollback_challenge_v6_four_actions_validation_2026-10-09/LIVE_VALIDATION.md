# Independent four-action validation passes

October 9, 2026. All thirty-two episodes finish with 130 known calls, no
unknowns and no global stop. [Independent replay](live_validation_audit.json)
passes for every response, grade, outcome and accounting record. Elapsed time
is 793.0 seconds excluding preflight.

| Control | Success | Rate | Wilson 95% interval | Public mismatch episodes |
|---|---:|---:|---:|---:|
| K, retained history | 9/16 | 56.25% | 33.2–76.9% | 13/16 |
| F, fresh released context | 12/16 | 75.0% | 50.5–89.8% | 7/16 |

There are no malformed-record or capacity failures. Every received action
submits a candidate. The whole intermediate-profile level-2 ledger cell
passes its [frozen validation gate](validated_selection.json): K lies within
40–75%, F is at least 40%, and at least four K episodes have public mismatches.
All scores are known, so the conservative missing-score rule does not affect
this decision. No failed cell or task is dropped.

This establishes measured headroom in this development cohort and permits
a separately frozen comparison. It does not prove a stable population rate,
a rollback effect, or a benefit from the four-action allowance. The screen
and validation contain no R arm. Earlier failed gates remain closed.

Known usage is 725,561 input tokens including 207,872 cached, and 235,567 output
tokens including 223,350 reasoning. The declared conversion gives 4.2907780
planning credits, not actual charges. All 130 calls count in the
[campaign budget](../rollback_challenge_v6_candidates_2026-10-09/campaign_budget.json),
bringing admissions to 1,194, including the earlier unknown.

Read [closeout](control_closeout.json), [analysis](live_validation/analysis.json),
[execution](live_validation/execution.json), [manifest](prepared/manifest.json),
the [sealed inventory](live_validation/evidence_manifest.json), and the
[prospective confirmation analysis](confirmation_analysis_precommit.json).
