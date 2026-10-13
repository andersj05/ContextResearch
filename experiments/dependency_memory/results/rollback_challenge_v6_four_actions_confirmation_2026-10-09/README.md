# Fixed four-action rollback confirmation

October 9, 2026. Independent [validation](../rollback_challenge_v6_four_actions_validation_2026-10-09/LIVE_VALIDATION.md)
passes at K=9/16 and F=12/16, with all 130 calls known and replayed.
This new allocation compares rollback with retained history on 260 new tasks.
No v6 R outcome existed when its [envelope](confirmation_envelope.json) froze.

## Allocation and information access

- Seed `2026101063`; 260 intermediate-profile level-2 revision-ledger questions,
  each with 28 transaction IDs, six accounts, three stages and four actions.
- Exactly 520 K/R episodes. Both arms write a lesson after a public mismatch
  when another action remains. K retains trial history; R then deletes all raw
  trial history, including earlier packets stored there. Lessons, the last
  accepted artifact and current feedback survive. Failed candidates are never
  committed. Writers are independent, so this estimates the whole policy effect.
- Luna medium, existing subscription, four workers, randomized arm order within
  each task. Fresh isolated provider thread per action or writer, tools disabled;
  only the allowlisted public state is sent. No archive or opaque-state replay.
- Full bound: 3,640 admitted generations, including writers and unknowns. No
  admitted identity is retried. Unknowns stop only their own trajectory; global
  source, account, isolation or accounting faults stop admissions.
- Immutable provider revision and provider sampling seed are unavailable.
  The manifest binds client-visible model selection and exact source snapshots.

The [manifest](prepared/manifest.json) byte SHA-256 is
`64cf6a5de2af437daef899a4f92520d2d702586d079fb1aacf97ef25b50244d8`. The [source snapshot](prepared/source_snapshot.zip)
and [analysis envelope](confirmation_envelope.json) bind the exact cohort,
implementation, prior validation, statistical source and proof checks before
the first live R dispatch. Every task identity is new.

## Fixed analysis

The primary contrast is complete-episode binary success R minus K. The
[prospective analysis](confirmation_analysis_precommit.json) uses the two-sided
exact paired test at alpha 1/20. With missing outcomes, reject only if the
maximum p-value over every feasible binary completion is at most 1/20. Keep
missing scores missing; report sharp fixed-denominator effect bounds separately
from population uncertainty. Preserve the standard engine report and label the
prospective amendment separately. A failed source/access/accounting audit cannot
support confirmation.

Run the entire fixed allocation. Do not inspect interim R/K effects or p-values,
stop for significance, extend the sample, or replace inconvenient tasks. The
power plan gives about 81.88% power for a ten-percentage-point difference with
30% discordance and complete observation. This does not guarantee an effect,
power under arbitrary missingness, or generalization beyond the authored family.
Resource and arm-rate summaries are secondary and descriptive.

## Readiness and standing authorization

All 24,960
task checks are in [verification](prepared/verification.json).
The [scripted rehearsal](rehearsal_audit.json) replays
2600 fixture responses for 520
episodes; it is not model evidence. The unchanged source has
[42 focused tests](../rollback_challenge_v6_intermediate_2026-10-09/package_tests.txt),
[259 scientific check categories](../rollback_challenge_v6_intermediate_2026-10-09/scientific_validation_result.json),
and [792 full-suite passes with nine optional Docker skips](../rollback_challenge_v6_intermediate_2026-10-09/full_unit_tests_summary.json).
Paper assembly passes. [Readiness](readiness.json) records the bindings.

The human's [standing authorization](../rollback_challenge_v6_candidates_2026-10-09/campaign_authorization.json)
covers thousands of Luna requests without per-run reconfirmation. At the allocation freeze, the campaign
had 1,194 prior admissions, including one unknown, plus this 3,640-call
reservation: 4,834 used/reserved against the assistant's 8,000-call working
ceiling. Subscription only; no purchases or API fallback. Planning credits
are derived accounting units, not actual account charges.

The run is complete. Read the [final results](LIVE_RUN.md),
[independent replay](live_confirmation_audit.json), and
[prospectively amended primary analysis](amended_primary_analysis.json).
K solves 122/254 known tasks and R 64/258; the conservative paired p-value
is 2.4820775e-7 in the direction of lower rollback success. All 520 episodes
have final dispositions; 2,496 calls are known and eight remain unknown.
