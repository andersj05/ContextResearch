# Independent validation of the four-action ledger

October 9, 2026. The [eight-task screen](../rollback_challenge_v6_four_actions_2026-10-09/LIVE_SCREEN.md)
nominates intermediate-profile level 2 at K=5/8 and F=7/8. This cohort tests
the whole setting independently on sixteen new questions before any R/K call.

## Frozen allocation and gate

- Seed `2026101049`; sixteen new 28-transaction/six-account ledger tasks.
- Three stages and four candidate actions, unchanged from screening.
- Thirty-two K/F episodes, Luna medium through the existing subscription,
  at most four workers and 176 calls including writers and unknowns.
- The ledger profile, candidate requirement and both calibration flags are inherited.
- At least fourteen of sixteen scores must be known in each arm. For s observed
  successes and m missing scores, K requires s >= 7 and s+m <= 12; F requires
  s >= 7. Thus every completion meets K in [40%,75%] and F at least 40%.
- At least four scheduled K episodes must have a public mismatch. No capacity
  failure or global source/accounting stop is allowed. The whole cell must pass.
- No task is dropped; unknown identities are never retried or replaced.

The [manifest](prepared/manifest.json) byte SHA-256 is
`c1b0b2ce09ecda320f9efeb2ee5b8edd5ab51f6420f6371ed05eb10623082323`.
Task identities are disjoint from all prior allocations. Preparation replays the
source screen before accepting its nomination, and the [snapshot](prepared/source_snapshot.zip)
binds the same implementation.

Passing validation permits a new fixed 260-pair R/K cohort with another seed,
the same settings and at most 3,640 generations. The
[prospective analysis](confirmation_analysis_precommit.json) retains the exact
two-sided worst-completion decision at alpha 1/20 and the original complete-data
power assumptions. Bind the exact cohort and analysis before its first dispatch.
There is no interim significance stopping, sample extension, favorable filling
of missing scores or guarantee of an effect. No R arm is present in validation.

## Verification and authorization

All 1,536 [independent task checks](prepared/verification.json) and the
144-response [offline replay](rehearsal_audit.json) pass. The [readiness record](readiness.json)
binds the unchanged source, with [42 focused package tests](../rollback_challenge_v6_intermediate_2026-10-09/package_tests.txt),
[259 scientific check categories](../rollback_challenge_v6_intermediate_2026-10-09/scientific_validation_result.json),
and [792 full-suite passes plus nine optional Docker skips](../rollback_challenge_v6_intermediate_2026-10-09/full_unit_tests_summary.json).
Paper assembly also passes. Those checks are distinct from model observations.

[Authorization](validation_authorization.json) uses the user's standing
permission for thousands of Luna requests without per-run reconfirmation.
The [campaign ledger](../rollback_challenge_v6_candidates_2026-10-09/campaign_budget.json)
has 1,064 prior admissions plus this 176-call reservation, or 1,240 used/reserved
against the assistant-selected 8,000-call ceiling. Subscription only; no
purchases or API fallback. Every admitted action, writer and unknown counts.
