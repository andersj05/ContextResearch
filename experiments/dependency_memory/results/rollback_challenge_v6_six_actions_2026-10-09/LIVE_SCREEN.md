# Six-action ledger screen remains below the target

October 9, 2026. All sixteen episode dispositions are saved after 103 known
calls and one unknown admission. There is no global stop. Both the
[original-source audit](live_screen_audit.json) and [historical replay](live_screen_snapshot_audit.json)
pass, preserving the unknown. Elapsed time is 759.2 seconds excluding preflight.

| Control | Known successes | Scheduled outcomes | Missingness bounds |
|---|---:|---:|---:|
| K | 2/8 | 8 | 25.0–25.0% |
| F | 5/7 | 8 | 62.5–75.0% |

K remains near the floor. Its Wilson 95% interval is approximately 7.1–59.1%.
All eight K episodes have public mismatches. No received candidate is malformed,
no action defers a candidate, and no capacity failure occurs. The third action
of one F episode is unknown (`DiagnosedProtocolError`); its trajectory stops
without retry, while other episodes finish. Its score remains missing.

The [original frozen selection](screen_selection.json) is empty because complete
control outcomes are required. A future conservative missing-score rule must
not retroactively alter it. This is a small new cohort, not a paired causal test
of adding an action. No R outcome or rollback-effect estimate is available.
The next [intermediate-size ledger screen](../rollback_challenge_v6_intermediate_2026-10-09/README.md)
returns to five actions and reduces task size on new identities.

Known usage is 806,614 input tokens, including 144,896 cached, and 249,646
output tokens, including 238,124 reasoning. Known usage converts to 4.8110940
planning credits under the declared accounting rule; the unknown retains its
separate reservation. These are not actual account charges. All 104 admissions
count in the [campaign ledger](../rollback_challenge_v6_candidates_2026-10-09/campaign_budget.json),
bringing the additional campaign total to 667. Read [analysis](live_screen/analysis.json),
[execution](live_screen/execution.json), [manifest](prepared/manifest.json),
and [sealed inventory](live_screen/evidence_manifest.json).
