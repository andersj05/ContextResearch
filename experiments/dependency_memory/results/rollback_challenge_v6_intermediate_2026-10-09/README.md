# Intermediate-size ledger screen

October 9, 2026. Complete: [K and F both solve 8/8](LIVE_SCREEN.md), with 68
known calls and no unknowns. The frozen selection is empty because K is at ceiling.
This prospective control-only screen uses 28 transaction IDs
over six accounts, between the original easy and hard ledger sizes. The
[five-action forty-transaction validation](../rollback_challenge_v6_validation_2026-10-09/LIVE_VALIDATION.md)
had K=3/16, and the [six-action screen](../rollback_challenge_v6_six_actions_2026-10-09/LIVE_SCREEN.md)
had K=2/8 with one missing F score. Both original negative gate decisions remain
closed. No v6 R-arm observation has been made.

## Frozen design

- Eight new level-2 tasks with `ledger_profile=intermediate`, seed `2026101001`.
- Three disclosure stages and five actions; a candidate is required each action.
- K/F controls only, Luna medium through the existing subscription, four workers.
- Sixteen episodes and at most 112 admissions, including writers and unknowns.
- The ledger's revision, voiding and balance rules are unchanged. Only its size
  profile differs; this is the same authored family, not a new benchmark family.
- New profile identities are separate from standard-profile identities even
  under the same seed. This allocation's task IDs are disjoint from all earlier runs.

The [manifest](prepared/manifest.json) byte SHA-256 is
`bfcc8994ad28fa85dfe2d6a6e7e16e27f1f9d3ae5fefce114cf91b3bbaff695e`.
Its [snapshot](prepared/source_snapshot.zip) freezes the exact generator, access,
grader and [protocol](../../rollback_challenge_v6/PROTOCOL.md). The intermediate
profile has 22/28/34 transaction IDs over 5/6/7 accounts at levels 1/2/3; only
level 2 is included here. The standard profile is unchanged.

## Selection fixed before outcomes

The `robust_control_missingness` option requires at least seven of eight scores
observed per arm. If s observed tasks pass and m scores are missing among N
scheduled tasks, the entire interval [s/N,(s+m)/N] must satisfy the existing
rate gate: K in [25%,85%], F in [25%,100%]. Thus eligibility cannot depend on
assuming a favorable unknown outcome. This interval describes missing scores,
not population uncertainty. Unknown identities are never retried or replaced.
At least one K episode must have a public mismatch; any capacity failure or
global source/accounting stop disqualifies the cell.

If nominated, the whole cell must validate on sixteen new tasks with a new seed
and identical settings. At least fourteen scores must be known per arm. Every
completion must put K in [40%,75%] and F at least 40%; at least four scheduled
K episodes must have a public mismatch, and there must be no capacity failures
or global stop. No failed cell or task is dropped. Both new flags and the size
profile are inherited unchanged by validation and confirmation.

Only successful validation allows a separately frozen 260-pair R/K allocation
on new identities. The [analysis precommit](confirmation_analysis_precommit.json)
retains the exact two-sided worst-completion test at alpha 1/20 and the original
complete-data power assumptions. It guarantees neither a real effect nor 80%
power under arbitrary missingness. No interim significance stopping or sample
extension is permitted. Bind the exact manifest and analysis source before
the first R/K call; preserve the ordinary engine report separately.

## Verification and authorization

All [42 package tests](package_tests.txt) pass, including exhaustive completion
checks, inherited immutable settings, unchanged actor inputs under calibration
flags, and independent checking of all intermediate ledger sizes. All 768
[task checks](prepared/verification.json) and the 72-response [offline replay](rehearsal_audit.json)
pass. The [readiness record](readiness.json) separates those fixtures from model
observations. The [repository-wide scientific validator](scientific_validation_result.json)
now passes all 259 check categories after the source change. The earlier
readiness record remains the original pre-run checkpoint.

The [allocation](screen_authorization.json) is covered by the user's standing
authorization for thousands of Luna requests without per-run reconfirmation.
The [campaign ledger](../rollback_challenge_v6_candidates_2026-10-09/campaign_budget.json)
has 667 admissions before this 112-call reservation, within the assistant's
8,000-call working ceiling. Existing-subscription calls only; no purchases or
API fallback. All admitted actions, writers and unknown calls count.
