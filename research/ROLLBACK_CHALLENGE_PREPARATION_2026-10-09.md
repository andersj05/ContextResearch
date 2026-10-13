# Harder rollback questions: control-only calibration environment

October 9, 2026. **Initial live screen complete; no qualifying recovery cell.**
The [live finding](../experiments/dependency_memory/results/rollback_challenge_v6_2026-10-09/LIVE_SCREEN.md)
records 161 metered responses, four retained unknowns and successful replay.
Both controls solve 6/16 known episodes, with two missing each. The original
preparation and its offline checks are documented below; they remain separate
from these model observations.

The user asks for questions that avoid the v5 ceiling and an efficient environment
for estimating rollback's effect. The v5 finding motivates a new allocation, not
editing or extending the completed cohort. See the [protocol](../experiments/dependency_memory/rollback_challenge_v6/PROTOCOL.md),
[implementation](../experiments/dependency_memory/rollback_challenge_v6/README.md),
and [prepared evidence](../experiments/dependency_memory/results/rollback_challenge_v6_2026-10-09/README.md).

The candidates add three different demands: constrained grid search, synthesis
of finite bitvector programs, and reconciliation of out-of-order transaction
revisions. Three levels per family span 4x4 to 9x9 grids, three to seven program
operations, and 18 to 80 transaction IDs. These are authored questions with exact
checkers, not external benchmark samples or a claim of novel task types.

The eighteen prepared tasks disclose real records over three stages and allow
five candidate actions. Both screening arms, K and F, run on every task; lessons
are charged. Their complete worst-case allocation is 252 generations. The longer
four-stage/eight-action design is also implementable but would require its own
414-generation screen and would not inherit the smaller design's calibration.

Difficulty selection never sees R outcomes. It nominates tiers from K/F controls,
then validates the complete nominated mixture on new seeds with at least eight
tasks per cell. Any ceiling/floor remains in the report; failed validation does
not silently remove a cell. Confirmation requires that gate, new seeds and a
fixed sample-size plan before any treatment results. A standard exact paired test
is implemented, including explicit missingness and a prohibition on confirmatory
p-values from incomplete pairs or fixtures. A useful test may still find no effect.

The environment freezes tasks, sources and identities, uses up to four workers,
retains metering for all calls, and isolates unknown dispatches to their trajectories.
Receipt replay reconstructs prompts, grades and outcomes independently of live
generation. The offline 36-episode screen rehearsal records 162 scripted responses
and passes replay. Witness/mutation verification contains 1,728 candidate checks;
all 28 package tests pass, including exhaustive small-word DSL operations,
historical-source replay and a stopped-run continuation with no repeated dispatch.
These are implementation checks, not provider observations.

An additional [offline capacity probe](../experiments/dependency_memory/results/rollback_challenge_v6_2026-10-09/capacity_probe.json)
finds that concise fixture text fits every tested path, while maximum-size
plain-text notes/lessons can exhaust the admission bound on one largest-ledger K
case. Extreme escaping produces more capacity failures. This is a schema-size
stress fixture, not observed model behavior or an estimated failure rate.
The updated calibration gate therefore rejects capacity-limited cells without
dropping their outcomes or denominators. Validation requires the entire nominated
mixture to remain free of capacity failures. Two new tests cover both gates.
The revised source is frozen in `prepared_screen_v2`; its 36-episode rehearsal
again has 162 fixture responses and passes independent replay. The prior screen
is retained and passes replay against its historical source snapshot.
The [updated verification record](../experiments/dependency_memory/results/rollback_challenge_v6_2026-10-09/capacity_guard_verification.json)
confirms all 28 then-current package tests, 259 scientific validation categories and
the paper build. The earlier full unittest checkpoint is preserved separately;
the complete unittest suite was not rerun after this scoped calibration change.

Read-only subscription/client verification and unauthenticated loopback probes
also pass for all three new family payloads, with zero model generations. The
sandbox initially closed app-server; the same check passed on the host. This is
not an authentication failure or a reason to change the user's credentials.

The [verification reconciliation](../experiments/dependency_memory/results/rollback_challenge_v6_2026-10-09/verification_summary.json)
records the earlier passing results for 780 distinct repository tests, with the
26-test package run covering one test added during the full run. The initial
779-test sandbox run reports 75 permission errors, two failing subtests and nine
skipped Docker cases. All 61 distinct affected test cases and all nine Docker
checks pass unchanged on the host; the original logs remain. Full scientific
validation passes 259 categories, and the paper builds with 48 cited sources.

Fresh-thread visible-state access and failure-boundary deletion follow the v5
contract. No submitted Python or arbitrary code is executed in the new finite DSL.
Private witnesses and future packets are withheld; earlier accepted artifacts
remain a declared information channel. There is no claim about native compaction
or inaccessible provider reasoning state. C75 and the manuscript remain unchanged.

The user authorized the 18-question Luna-medium screen with a maximum of 252
existing-subscription generations. Its complete allocation admits 165 calls and
is now closed. The frozen selection nominates no cells: 92 of 154 received actions
defer candidate submission, and 17 of 20 known failed episodes have no public
mismatch. Thus the screen establishes a lower aggregate success rate but not a
suitable intermediate-difficulty recovery distribution. A separate follow-up
requiring a best candidate on every action is [prepared with new seeds](../experiments/dependency_memory/results/rollback_challenge_v6_candidates_2026-10-09/README.md).
Its six questions pass 576 separate-formulation checks, all 33 current package
tests pass, and a 54-response scripted rehearsal passes independent replay.
The separately frozen allocation has 12 K/F episodes and at most 84 generations;
no follow-up model calls had been made at that preparation checkpoint.
The user subsequently [authorized thousands of Luna requests](../experiments/dependency_memory/results/rollback_challenge_v6_candidates_2026-10-09/campaign_authorization.json)
without per-run reconfirmation. The six-question screen is now running under
that later authorization, with an agent-selected 6,000-additional-admission
working ceiling covering screening, validation and a fixed-size comparison.
This supersedes the pending-allocation state without reopening the initial screen.

The [candidate-required screen](../experiments/dependency_memory/results/rollback_challenge_v6_candidates_2026-10-09/LIVE_SCREEN.md)
then finishes with 56 known calls, K=5/6 and F=4/6. All 49 actions submit candidates;
the original selection is still empty. Ledger level 2 has K=1/2 and F=2/2, with
public mismatches in both K episodes. Preserve this small-sample result and its
original rule. A [new 24-question screen](../experiments/dependency_memory/results/rollback_challenge_v6_headroom_2026-10-09/README.md)
finishes under a prospective calibration rule that retains K headroom but
allows F to establish solvability at 100%. It covers levels 2 and 3 in each family,
four new replicates per cell, with 317 known calls and no unknowns. All 37 package tests,
2,304 independent task checks and the 216-response offline replay pass. Sixteen
new validation tasks per selected cell precede any fixed-size R/K comparison.
Only ledger level 2 qualifies, with K=2/4, F=2/4 and public mismatches in all four
K episodes. This cell also satisfies the original stricter fresh-control bound.
The [independent validation](../experiments/dependency_memory/results/rollback_challenge_v6_validation_2026-10-09/README.md)
is now running with a new seed and at most 224 generations. The rule change is
informed only by controls, with no R outcomes inspected.

The [sixteen-task validation](../experiments/dependency_memory/results/rollback_challenge_v6_validation_2026-10-09/LIVE_VALIDATION.md)
finishes with 190 known calls and no unknowns. K solves 3/16, below the frozen
40% minimum; F solves 7/16. The whole-cell gate fails and no confirmation may
use that selection. All calls, grades and accounting replay correctly. Twelve
of thirteen K failures pass two stages before exhausting five actions.
A separately frozen [six-action screen](../experiments/dependency_memory/results/rollback_challenge_v6_six_actions_2026-10-09/README.md)
therefore uses eight new ledger tasks, with at most 136 K/F calls. Its 768
independent checks and 72-response rehearsal pass. This control-informed
adaptation precedes any R observation and must independently validate again.
The agent raises its own campaign working ceiling to 8,000 within the user's
standing authorization; the 563 previous admissions remain counted.

The [six-action follow-up](../experiments/dependency_memory/results/rollback_challenge_v6_six_actions_2026-10-09/LIVE_SCREEN.md)
closes with K=2/8, F=5/7 known and one missing F score. Both audits pass and the
original complete-outcome selection stays empty. The new
[intermediate ledger screen](../experiments/dependency_memory/results/rollback_challenge_v6_intermediate_2026-10-09/README.md)
uses 28 transaction IDs over six accounts, returning to five actions, on eight
new tasks. Its conservative control gate requires every missing-score completion
to meet the rate bounds and at least seven eighths observed. The old negative
selections remain unchanged. All 42 package tests and the 72-response replay
pass; at most 112 calls are reserved under the standing broad authorization.

## Completed fixed comparison, October 10 UTC

The [final 260-task study](../experiments/dependency_memory/results/rollback_challenge_v6_four_actions_confirmation_2026-10-09/LIVE_RUN.md) finds headroom and a
statistically significant negative whole-policy result: K=122/254 known,
R=64/258 known; 87 K-only versus 29 R-only successes among 252 complete pairs.
The conservative maximum-completion p-value is 2.4820775e-7. The fixed-denominator
R-minus-K bounds from missing scores are [-24.62,-21.54] percentage points;
these are not population confidence intervals. All 2,496 known responses replay;
eight unknowns remain missing. No v6 R outcome informed calibration or sample size,
and no interim effect checks or sample extension were used. This result concerns
the authored ledger family and this policy's deletion of all raw history,
including earlier packets, with lesson and checkpoint retention. It does not
identify the isolated cause of the loss or establish general rollback behavior.
