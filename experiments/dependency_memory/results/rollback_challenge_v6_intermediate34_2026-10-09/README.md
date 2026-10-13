# Thirty-four-transaction ledger screen

October 9, 2026. Complete: the [live screen](LIVE_SCREEN.md) has K=3/8 and
F=5/8, with 88 known calls and a passing nomination for independent validation.
The [28-transaction screen](../rollback_challenge_v6_intermediate_2026-10-09/LIVE_SCREEN.md)
ends at K=F=8/8, while the original forty-transaction five-action validation
has K=3/16. This new control-only allocation tests another existing setting of
the intermediate profile. All earlier gate decisions remain unchanged, and
no v6 R-arm outcome has been observed.

## Frozen allocation

- Eight new level-3 ledger tasks, `ledger_profile=intermediate`, seed `2026101011`.
- Thirty-four transaction IDs over seven accounts, up to five revisions per ID
  and transfer amounts from 1 through 200. The preceding level-2 setting had
  28 IDs, six accounts, up to four revisions and amounts through 150. This is
  a new task distribution, not an isolated causal test of transaction count.
- Three disclosure stages, five actions and a required candidate each action.
- Sixteen K/F episodes, Luna medium through the existing subscription, four workers.
- At most 112 calls including writers and unknown admissions; no identity retries.

The [manifest](prepared/manifest.json) byte SHA-256 is
`1429dad37ed292ae9dd5b52e6d7362dc9827c8429ecf487943114fada1e88a69`.
The [source snapshot](prepared/source_snapshot.zip) is identical in source bindings
to the preceding intermediate screen; no engine, grader or calibration code changes.
All task IDs are new. The [readiness record](readiness.json) binds 768 independent
task checks, a passing 72-response [rehearsal replay](rehearsal_audit.json), and
the same [42 passing package tests](../rollback_challenge_v6_intermediate_2026-10-09/package_tests.txt).

## Prospective decisions and authorization

The [same protocol](../../rollback_challenge_v6/PROTOCOL.md) requires K in
[25%,85%], F at least 25%, and at least seven of eight outcomes known per arm.
Every completion of a missing score must satisfy the rate bounds. At least
one K public mismatch is required; capacity failures and global stops disqualify
the cell. These are empirical missingness bounds, not confidence intervals.
No old screen is reclassified under this rule.

If nominated, validate all of this cell on sixteen new tasks with a new seed
and identical settings. At least fourteen scores per arm must be known, every
completion must put K in [40%,75%] and F at least 40%, and at least four K
episodes must have a public mismatch. Capacity failures or a global stop block
validation. Only then freeze a new 260-pair R/K cohort with the
[prospective primary analysis](confirmation_analysis_precommit.json). Its entire
allocation runs without interim significance stopping or sample extension.
The same completion-bound inference, exact alpha 1/20 and complete-observation
power assumptions apply. No beneficial or significant result is guaranteed.

[Authorization](screen_authorization.json) uses the user's standing permission
for thousands of Luna requests, without another per-run approval. The
[campaign budget](../rollback_challenge_v6_candidates_2026-10-09/campaign_budget.json)
records 735 earlier admissions plus this 112-call reservation, within the
assistant-selected 8,000-call ceiling. Subscription only; no purchases or API fallback.
