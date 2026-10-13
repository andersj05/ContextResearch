# The 28-transaction intermediate ledger reaches ceiling

October 9, 2026. Both K and F solve all eight tasks. All 68 calls are known,
with no global stop, malformed record or capacity failure. Six K episodes and
three F episodes have public mismatches before eventual success. Median action
counts are four for K and three for F.

[Independent replay](live_screen_audit.json) passes for every response, grade,
outcome and accounting record. The [frozen selection](screen_selection.json)
nominates no cells because K=100% exceeds its 85% screening upper bound.
Allowing a fresh-control ceiling or bounded missing scores does not change
that decision. All outcomes are observed.

This new size profile is too easy on this small sample. Eight successes have
a Wilson 95% interval of approximately 67.6–100%, so the result is a calibration
observation, not proof of population saturation. It is not a paired comparison
against the earlier larger ledger tasks. No R arm has been observed.
The next [34-transaction screen](../rollback_challenge_v6_intermediate34_2026-10-09/README.md)
uses new tasks and another existing level of the same size profile.

Known usage is 385,340 input tokens including 103,936 cached, and 129,584 output
tokens including 122,242 reasoning. The declared conversion is 2.3492940 planning
credits, not an actual charge. Elapsed time is 357.0 seconds excluding preflight.
The [campaign ledger](../rollback_challenge_v6_candidates_2026-10-09/campaign_budget.json)
now records 735 admissions, including the earlier single unknown.

Read [closeout](control_closeout.json), [analysis](live_screen/analysis.json),
[execution](live_screen/execution.json), [manifest](prepared/manifest.json),
and [sealed inventory](live_screen/evidence_manifest.json).
