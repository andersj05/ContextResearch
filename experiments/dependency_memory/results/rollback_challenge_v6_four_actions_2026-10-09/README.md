# Four-action screen on the twenty-eight-transaction ledger

October 9, 2026. Complete: the [live screen](LIVE_SCREEN.md) has K=5/8 and
F=7/8, with 60 known calls and a qualifying selection for independent validation.
The [34-transaction validation](../rollback_challenge_v6_intermediate34_validation_2026-10-09/LIVE_VALIDATION.md)
ends below the target at K=5/16, F=9/16. The earlier 28-transaction, five-action
screen had K=F=8/8. Its [observed completion timings](../rollback_challenge_v6_intermediate_2026-10-09/four_action_timing_diagnostic.json)
show six K and seven F episodes finishing within four actions. This is a
post-hoc timing diagnostic, not a measured four-action success rate: a different
remaining-action count can change model behavior. It motivates this new screen.
All earlier gate decisions remain closed. No R outcome has been observed.

## Frozen allocation

- Eight new intermediate-profile level-2 ledger tasks, seed `2026101037`.
- Twenty-eight transaction IDs, six accounts, up to four revisions per ID and
  amounts through 150; the same size profile that previously reached ceiling.
- Three disclosure stages and **four** actions, each requiring a candidate.
  This leaves one possible failed attempt on a successful three-stage episode.
- Sixteen K/F episodes, Luna medium through the existing subscription, four workers.
- At most 88 calls including writers and unknown admissions; no identity retries.

The [manifest](prepared/manifest.json) byte SHA-256 is
`bff1f8082ca320e91cf7010d27828dff957a9c2bc973efa30befe8055dd6a62f`.
Its [source snapshot](prepared/source_snapshot.zip) uses the same implementation
as the other intermediate-profile allocations. No engine, grader or selection
code changes. All task identities are new.

## Prospective selection and comparison

The [existing conservative gate](../../rollback_challenge_v6/PROTOCOL.md) requires
at least seven of eight scores known per arm. Every completion must place K in
[25%,85%] and F at least 25%, with a K public mismatch and no capacity failure
or global stop. Missing scores stay missing. A failed screen is preserved.

If nominated, independently validate the whole cell on sixteen new tasks with
the same four-action allowance. At least fourteen outcomes per arm must be
known, every completion must put K in [40%,75%] and F at least 40%, and at least
four scheduled K episodes must have a public mismatch. Capacity failures and
global stops disqualify the cell. No failed tasks are dropped.

Only successful validation permits a new fixed 260-pair R/K cohort with another
seed and a maximum of 3,640 generations. The [prospective primary analysis](confirmation_analysis_precommit.json)
keeps the same exact two-sided worst-completion test at alpha 1/20 and the
complete-data power assumptions. Bind that analysis and the exact cohort before
the first R/K dispatch. No interim significance stopping, sample extension,
unknown retry or guaranteed effect. The ordinary engine report remains separate.

## Verification and authorization

All 768 [independent task checks](prepared/verification.json) and the 72-response
[offline replay](rehearsal_audit.json) pass. The [readiness record](readiness.json)
binds identical source files to the [42-test implementation](../rollback_challenge_v6_intermediate_2026-10-09/package_tests.txt),
which also passes [259 scientific check categories](../rollback_challenge_v6_intermediate_2026-10-09/scientific_validation_result.json).
The [complete repository unittest suite](../rollback_challenge_v6_intermediate_2026-10-09/full_unit_tests_summary.json)
finishes with 792 passes and nine optional Docker skips; paper assembly passes.
Fixtures and post-hoc timings are distinct from new model observations.

[Authorization](screen_authorization.json) is covered by the user's standing
permission for thousands of Luna requests without per-run reconfirmation.
The [campaign ledger](../rollback_challenge_v6_candidates_2026-10-09/campaign_budget.json)
records 1,004 prior admissions plus this 88-call reservation, within the
assistant-selected 8,000-call working ceiling. Subscription only; no purchases
or API fallback. All admitted actions, writers and unknowns count.
