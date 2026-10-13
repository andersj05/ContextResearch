# Independent validation of the thirty-four-transaction ledger

October 9, 2026. Complete: the [live validation](LIVE_VALIDATION.md) has K=5/16
and F=9/16, with all 181 calls known and replayed. Its frozen gate fails.
The [eight-task screen](../rollback_challenge_v6_intermediate34_2026-10-09/LIVE_SCREEN.md)
nominates this setting at K=3/8 and F=5/8. This independent cohort checks the
whole selected cell on sixteen new questions before any R/K comparison.

## Frozen design

- Sixteen new intermediate-profile level-3 ledger tasks, seed `2026101023`.
- Thirty-four transaction IDs, seven accounts, up to five revisions, amounts
  through 200: the same generator settings as screening.
- Three stages, five actions and a required candidate each action.
- Thirty-two K/F episodes, Luna medium through the existing subscription,
  at most four workers and 224 calls including writers and unknown admissions.
- Both calibration flags and the ledger profile are inherited unchanged.
- No unknown identity is retried or replaced; no R arm is present.

The [manifest](prepared/manifest.json) byte SHA-256 is
`a1d087ac77f58d36539010cf911c550f6c1742d2f73d7681a908a6ec2d6a4fa7`.
All task IDs are new, and preparation replays the source screen before accepting
its nomination. The [snapshot](prepared/source_snapshot.zip) binds the same code.

## Decision fixed before outcomes

Each arm must have at least fourteen of sixteen scores observed. Let s be
observed successes and m missing outcomes. K requires s at least 7 and s+m at
most 12; F requires s at least 7. Thus every possible completion must satisfy
K in [40%,75%] and F at least 40%. At least four scheduled K episodes must have
a public mismatch. No capacity failure or global source/accounting stop is
allowed. The whole cell must pass; no failed task or outcome is removed.

Only a passing gate permits a new fixed 260-pair R/K allocation with another
seed, the same settings and a maximum of 4,680 generations. Bind its manifest
and [prospective analysis](confirmation_analysis_precommit.json) before the first
confirmation call. The single exact paired-test decision must survive every
completion of missing scores at alpha 1/20; the ordinary engine report remains
separate. There is no interim significance stopping or sample extension.
The complete-data power assumption does not guarantee power under arbitrary
missingness or establish that a real rollback effect exists.

## Checks and authorization

All 1,536 [independent task checks](prepared/verification.json) and the
144-response [offline replay](rehearsal_audit.json) pass. The same source has
[42 passing tests](../rollback_challenge_v6_intermediate_2026-10-09/package_tests.txt)
and [259 passing scientific check categories](../rollback_challenge_v6_intermediate_2026-10-09/scientific_validation_result.json).
The [readiness record](readiness.json) separates these checks from model outcomes.

[Authorization](validation_authorization.json) uses the user's standing
permission for thousands of Luna requests, with no per-run reconfirmation.
The [campaign budget](../rollback_challenge_v6_candidates_2026-10-09/campaign_budget.json)
has 823 prior admissions plus this 224-call reservation, or 1,047 used/reserved
against the assistant-selected 8,000-call ceiling. Subscription only; no
purchases or API fallback. The runner refreshes client and isolation checks
before dispatch.
