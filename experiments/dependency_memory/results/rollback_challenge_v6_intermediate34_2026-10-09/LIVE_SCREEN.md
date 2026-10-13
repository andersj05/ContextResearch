# Thirty-four-transaction ledger qualifies for independent validation

October 9, 2026. All sixteen episodes finish with 88 known calls, no unknowns
and no global stop. [Independent replay](live_screen_audit.json) reproduces every
response, grade, outcome and accounting record. Elapsed time is 598.5 seconds
excluding preflight.

| Control | Success | Rate | Wilson 95% interval | Public mismatch episodes |
|---|---:|---:|---:|---:|
| K | 3/8 | 37.5% | 13.7–69.4% | 7/8 |
| F | 5/8 | 62.5% | 30.6–86.3% | 7/8 |

There are no malformed-record or capacity failures. Every received action
submits a candidate. The [frozen selection](screen_selection.json) nominates
the intermediate-profile level-3 ledger. Both controls are within their
screening ranges, all scores are observed, and there are public rejections
that could require recovery. The missing-score rule does not affect this decision.

Eight tasks remain a small calibration sample. K's point rate is below the
later 40% validation minimum, with wide sampling uncertainty. The separately
frozen [sixteen-task validation](../rollback_challenge_v6_intermediate34_validation_2026-10-09/README.md)
must test that range on new identities before confirmation. No R arm has been
observed, no rollback effect is estimated, and the nomination does not guarantee
that validation will pass.

Known usage is 650,183 input tokens, including 127,232 cached, and 205,960 output
tokens, including 196,819 reasoning. The declared conversion yields 3.9136855
planning credits, not actual charges. All 88 calls count in the
[campaign ledger](../rollback_challenge_v6_candidates_2026-10-09/campaign_budget.json),
bringing admissions to 823, including the prior unknown. Read
[closeout](control_closeout.json), [analysis](live_screen/analysis.json),
[execution](live_screen/execution.json), [manifest](prepared/manifest.json),
and [sealed inventory](live_screen/evidence_manifest.json).
