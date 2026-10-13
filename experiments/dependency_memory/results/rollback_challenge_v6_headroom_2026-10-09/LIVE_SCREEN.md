# Harder-level screen selects revision-ledger level 2

October 9, 2026. All 48 K/F episodes finish with 317 metered responses, no
unknown calls and no global stop, against the 336-generation ceiling. Four
workers take 2,825.1 seconds excluding preflight. [Independent replay](live_screen_audit.json)
reproduces every received call, grade, episode and accounting record.

| Family / level | K success | F success | K episodes with a public mismatch |
|---|---:|---:|---:|
| Bitvector program / 2 | 0/4 | 1/4 | 4/4 |
| Bitvector program / 3 | 0/4 | 0/4 | 4/4 |
| Constraint grid / 2 | 1/4 | 0/4 | 3/4 |
| Constraint grid / 3 | 0/4 | 0/4 | 4/4 |
| Revision ledger / 2 | 2/4 | 2/4 | 4/4 |
| Revision ledger / 3 | 0/4 | 0/4 | 4/4 |

The [frozen selection](screen_selection.json) nominates only revision-ledger
level 2. Both controls solve 50% and all K episodes include a public rejection,
so it offers observed opportunities for recovery without a control ceiling.
This cell also meets the original, stricter F upper bound; allowing F ceiling
does not determine the selection in this particular screen. The other five
cells are at a K or F floor. Every received action submits a candidate; no
malformed-record or context-capacity disposition occurs.

Four tasks remain a small development screen. A 2/4 success rate has a Wilson
95% interval of approximately 15.0% to 85.0%. It does not establish stable
intermediate difficulty. The [independent validation](../rollback_challenge_v6_validation_2026-10-09/README.md)
therefore uses sixteen new ledger tasks before any R/K comparison. Neither
successful screening nor a power calculation guarantees statistical significance.

Known usage totals 1,896,383 input tokens, including 428,544 cached, and 888,516
output tokens, including 837,147 reasoning. The declared conversion is
14.8831835 planning credits, not an actual subscription charge. All 317 calls
count in the [campaign budget](../rollback_challenge_v6_candidates_2026-10-09/campaign_budget.json),
bringing additional campaign admissions to 373 before validation.

Primary artifacts: [analysis](live_screen/analysis.json),
[execution](live_screen/execution.json), [manifest](prepared/manifest.json),
[source snapshot](prepared/source_snapshot.zip), [authorization](screen_authorization.json),
and [sealed inventory](live_screen/evidence_manifest.json). The prior two screens
and their empty selections remain intact. No R arm was run in this screen.
