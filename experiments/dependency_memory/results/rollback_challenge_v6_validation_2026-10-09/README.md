# Independent validation of revision-ledger level 2

October 9, 2026. Complete: the [live validation](LIVE_VALIDATION.md) has K=3/16,
F=7/16 and fails its frozen gate. All 190 calls are known and replay correctly.
The [screen](../rollback_challenge_v6_headroom_2026-10-09/LIVE_SCREEN.md) selects only
revision-ledger level 2, with K=2/4, F=2/4 and public rejections in all K episodes.
This phase uses new tasks to test whether that difficulty persists.

## Frozen allocation

- Sixteen new revision-ledger-level-2 tasks, seed `2026100971`.
- Thirty-two K/F episodes on Luna medium through the existing subscription.
- Three stages, five actions, candidates required on every action.
- The selected `allow_fresh_ceiling=true` rule is inherited unchanged.
- At most four workers and 224 generations, including writers and unknowns.
- No admitted request is retried. No R arm or rollback-effect estimate is included.

The [manifest](prepared/manifest.json) byte SHA-256 is
`756813e6dc53e35dfb10ff7f6910fa8d445374c6b13583ccb37fbe64f4cd1dac`.
All task identities are disjoint from the three earlier screens. The preparation
replays the selected screen before accepting its selection and freezes the
[same sources and protocol](prepared/source_snapshot.zip).

## Decision fixed before outcomes

All sixteen outcomes must be known in each arm. K must solve between 7 and 12
tasks inclusive; F must solve at least 7. At least four K episodes must include
a public mismatch. Neither control may have a context-capacity failure. The
whole selected cell must pass; no task or unfavorable outcome is removed.
If this gate fails, this design does not advance to confirmation.

If it passes, a new, fixed-size R/K allocation will use another seed and at least
260 pairs, following the recorded power assumption. Its analysis and full
generation bound must be frozen before the first confirmatory dispatch.
No significance outcome is guaranteed or used as a stopping rule.

## Readiness and budget

[Independent graders](prepared/verification.json) pass 1,536 witness/mutation
comparisons. The [offline rehearsal](rehearsal/analysis.json) has 144 scripted
responses across all 32 episodes; [receipt replay](rehearsal_audit.json) passes.
These are engineering checks, not observed difficulty. The source package's
37 tests and 259 scientific-check categories passed at the prior checkpoint.
The runner repeats its installed-client and request-isolation checks at launch.

[Authorization](validation_authorization.json) references the user's approval
for thousands of Luna requests without per-run reconfirmation. The
[campaign ledger](../rollback_challenge_v6_candidates_2026-10-09/campaign_budget.json)
records 373 earlier admissions plus 190 from this completed phase, totaling 563.
The original 224-call reservation is closed. Later designs use separate freezes
under the standing authorization and cannot extend this failed validation.
