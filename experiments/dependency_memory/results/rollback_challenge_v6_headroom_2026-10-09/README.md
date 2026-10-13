# V6 harder-level control screen: allow a strong fresh control

October 9, 2026. This screen is complete: 317 known calls, no unknowns, and
revision-ledger level 2 selected with K=2/4 and F=2/4. Read the [live finding](LIVE_SCREEN.md).
The
[earlier six-task result](../rollback_challenge_v6_candidates_2026-10-09/LIVE_SCREEN.md)
is preserved with its empty original selection: K solves 5/6, F solves 4/6,
all 49 actions submit candidates, and all 56 calls are known. In ledger level 2,
K solves 1/2 while F solves 2/2, motivating a different prospective calibration
rule. That two-task pattern is not a rollback-effect estimate.

## Frozen design

- Twenty-four new tasks: four replicates at levels 2 and 3 in each of the three
  families: bitvector programs, constraint grids and revision ledgers.
- Root seed `2026100959`, with identities disjoint from both completed screens.
- K/F controls only, Luna medium, existing subscription, at most four workers.
- Three disclosure stages and at most five actions per episode.
- A best complete candidate is required on every action; intentional errors
  are prohibited. Actor information, graders and interventions are unchanged.
- Forty-eight episodes; at most 336 model generations including writers and
  unknown admissions. No admitted identity is retried.
- `allow_fresh_ceiling=true` is frozen in the manifest. It does not appear in
  actor inputs and cannot be changed by later validation or confirmation.

The [manifest](prepared/manifest.json) byte SHA-256 is
`8a1dc0eed43e950eec80ce716af2c53273afbc24954e54bde8c7a3dc9727b8a9`.
The [source snapshot](prepared/source_snapshot.zip) preserves the exact code and
[protocol](../../rollback_challenge_v6/PROTOCOL.md) before any new outcome.

## Prospective selection and validation

The retained-history control K must still have room for improvement. Screening
requires complete K/F outcomes, K success from 25% through 85%, F success at least
25%, at least one K episode with a public mismatch, and no capacity failures.
Within each family choose the eligible tier nearest K=57.5%, breaking ties toward
the smaller tier. F may reach 100%; it establishes solvability rather than the
required failure rate. No R outcomes enter selection.

Validate exactly the nominated mixture on sixteen new tasks per cell, using a
new root seed and the same settings. The entire mixture must have complete
outcomes, K success from 40% through 75%, F success at least 40%, public mismatches
on at least 25% of K episodes, and no capacity failures. No inconvenient cell is
dropped. A failed screen or validation is preserved and cannot establish success
for this design. Confirmation, if reached, uses another new seed and a fixed
sample size chosen before any R/K outcomes; significance is not guaranteed.

The original two-sided success-rate gates remain the default for old designs.
Neither completed screen is retrospectively reclassified under this new rule.

A [prospective confirmation analysis amendment](confirmation_analysis_precommit_v2.json)
is now frozen before any v6 R-arm observation. If validation succeeds, the future
confirmation will reject only when the exact paired-test result survives every
feasible completion of missing scores. The [separate completion-bound proof and checks](../rollback_missingness_bound_2026-10-09/README.md)
bind that implementation. The ordinary engine report stays intact, including its
missing-score p-value suppression; the amendment will be reported separately.
The exact cohort, manifest and this analysis source must be bound before the
first confirmation call. Its complete-data power assumption does not guarantee
80% power under arbitrary missingness. The current K/F selection rule is unchanged.

## Authorization, accounting and checks

The user's [broad Luna authorization](../rollback_challenge_v6_candidates_2026-10-09/campaign_authorization.json)
covers this [336-generation allocation](screen_authorization.json) and the later
bounded stages without per-run reconfirmation. The [campaign budget](../rollback_challenge_v6_candidates_2026-10-09/campaign_budget.json)
records 373 completed admissions across both follow-up screens plus the next
224-call validation reservation against the
agent-selected 6,000-additional-admission working ceiling. The earlier eighteen-task
screen and all v5 allocations remain closed. The [independent validation](../rollback_challenge_v6_validation_2026-10-09/README.md)
uses sixteen new ledger level-2 tasks and the same frozen candidate requirement.

All [37 package tests](checks/package_tests.txt) pass, including four scientific
invariants for the new gate: K must remain below ceiling, missingness/capacity
and whole-mixture requirements remain, the rule is inherited unchanged, and
actor requests are identical across calibration-rule flags.
[Independent task checks](prepared/verification.json) pass 2,304 witness/mutation
comparisons. The [offline rehearsal](rehearsal/analysis.json) has 216 scripted
responses across all 48 episodes, and its [replay](rehearsal_audit.json) passes.
These fixtures use evaluator answers and are not empirical difficulty evidence.
The live runner refreshes client and request-isolation checks before dispatch.
The [verification summary](verification_summary.json) also records 259 passing
repository-wide scientific check categories and passing navigation checks.
The entire unittest suite was not rerun for this scoped calibration-rule change;
its earlier checkpoint is retained separately. Live outcomes remain separate
from all these implementation checks.
