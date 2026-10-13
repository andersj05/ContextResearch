# Challenge v6 preparation and live difficulty screen

October 9, 2026. **The Luna-medium control screen is complete and replay-verified.**
Both arms solve 6/16 known episodes, with two missing each, but no difficulty
cell passes the frozen recovery-selection gate. Read the [live finding](LIVE_SCREEN.md).

The [new protocol](../../rollback_challenge_v6/PROTOCOL.md) separates control-only
screening, independent difficulty validation, and fixed-size rollback comparison.
The [implementation guide](../../rollback_challenge_v6/README.md) contains commands.
All v5 sources, allocations and observations remain unchanged.

## Saved artifacts

- [User authorization](screen_authorization.json): the 18-question Luna-medium
  K/F screen, capped at 252 generations on the existing subscription.
- [Live screen](live_screen/analysis.json): 36 final episode dispositions,
  161 metered responses and four unknowns, with 165 total admissions against
  the 252-generation cap. [Replay](live_screen_audit.json) passes;
  [selection](screen_selection.json) nominates no cells.
- [Prepared manifest](prepared_screen_v2/manifest.json): 18 seeded tasks, three families,
  three levels, two replicates, three public stages and five candidate actions.
  K/F screening only; 36 episodes and a maximum of 252 generations, writers included.
- [Tasks and private witnesses](prepared_screen_v2/tasks.json): evaluator material; never
  passed wholesale to a model. Use the `preview` command to see an actor request.
- [Independent verification](prepared_screen_v2/verification.json): every stage witness
  passes; 1,728 witness/mutation comparisons agree across separate grader formulations.
- [Offline execution](screen_rehearsal_v2/execution.json) and [analysis](screen_rehearsal_v2/analysis.json):
  36 scripted episodes with 162 fixture responses, four configured workers, a peak
  of three admitted calls, and no unresolved
  fixture calls. This deliberately uses oracle answers after a scripted error;
  its success rate is not model performance or difficulty evidence.
- [Independent replay](offline_audit_v2.json) reproduces every received fixture call
  and every episode. [Example actor inputs](example_actor_requests.json) show
  one medium-level question per family without witnesses or future packets.
- [Power plan](power_plan.json): assuming a 10 percentage-point paired effect and
  30% discordance, 260 independent pairs give approximately 81.88% power on the
  20-pair planning grid. This is a planning calculation, not a measured effect.
- [Installed-client preflight](client_preflight.json): read-only subscription
  checks and unauthenticated loopback probes pass, including all three new
  family payloads. This check made zero model generations and is repeated at launch.
- [Power sensitivity](power_sensitivity.json): at the same assumed 30% discordance,
  a 5-point effect needs 980 pairs and a 15-point effect needs 120 pairs on the
  20-pair planning grid for at least 80% power. These are alternative planning
  scenarios, not extra live allocations or measured rollback effects.
- [Earlier verification summary](verification_summary.json): all 26 then-current package tests and
  780 distinct repository tests have passing results across the full run and
  exact rechecks. The initial sandbox run's filesystem errors, two failed subtests
  and nine skipped Docker cases remain in the controlled logs; all affected
  cases pass unchanged on the host. Full scientific validation passes 259 check
  categories; catalog/navigation checks and the paper build pass.
- [Initial-screen package checks](checks/capacity_package_tests.txt): all 28 tests passed,
  including two new checks that capacity failures cannot establish calibration
  difficulty or allow a nominated validation mixture to advance.
- [Capacity-guard verification](capacity_guard_verification.json): the source
  freeze, unchanged task records, both rehearsals' replay, 259 scientific check
  categories, navigation checks and the paper build pass. The entire unittest
  suite was not rerun after this scoped guard; its earlier checkpoint is retained.
- [Capacity probe](capacity_probe.json), with its [archived script](capacity_probe_source.zip):
  36,126 scripted paths across three text-size profiles exercise the actual engine,
  public graders and admission checks. These are offline fixtures, not model trials.

The earlier `prepared/` and `simulation/` directories preserve the first engineering
rehearsal before reporting/recovery checks were finalized. `prepared_screen/` and
`screen_rehearsal/` preserve the next freeze, before the capacity calibration guard.
All contain no live observations and are superseded for dispatch by
`prepared_screen_v2/`. [Historical snapshot replay](previous_screen_snapshot_audit.json)
passes for the previous screen's 162 fixtures. Every older source bundle is preserved.

The capacity probe uses that previous screen's bound engine and tasks. Concise
notes and lessons fit on every tested path (maximum admission bound 113,892 bytes).
Maximum-size plain-text records cause one task/arm case, the largest ledger K,
to reach 132,876 bytes against the 131,072-byte limit. Maximum escaping causes
twenty task/arm cases to reach the limit; the largest attempted bound is 159,355.
These paths share prefixes, and the stress padding does not simulate model
semantics or establish a probability of overflow. Candidate sizes stay near the
reference witnesses, so this is not a bound over every accepted output.

The updated selection rule preserves capacity failures in all reported outcomes
but prevents their cells from qualifying as difficult. A capacity failure in
either control also blocks the whole nominated validation mixture. No task or
live observation was removed, and the 18 task records are unchanged.

The saved screen uses three stages/five actions, so independent validation must
preserve those settings. With eight tasks per nominated cell, validation costs
at most 112 generations per cell. A two-arm 260-pair confirmation at five actions
would cost at most 4,680 generations; more cells may require rounding the pair count
up to maintain balance. These are separate allocations, not part of the screen.

## Completed authorized screen

The user explicitly approved Luna medium with a 252-generation cap on October 9.
The runner refreshed its installed-client, account and prompt checks before any
generation. Its fixed allocation is now closed. The 92 progress-only actions
among 154 received actions motivate a separate follow-up requiring a candidate
on every action; that follow-up has not been authorized by this allocation.
Original sources and evidence remain in their frozen bundles. As the shared
environment evolves, use `audit --snapshot` to replay this completed screen.
Statistical significance is not guaranteed by calibration.

[Historical snapshot replay](live_screen_snapshot_audit.json) now passes after
the follow-up source change, reproducing all 161 received calls and preserving
the four unknowns. The [six-question follow-up](../rollback_challenge_v6_candidates_2026-10-09/README.md)
is separately prepared with new task identities and an 84-generation ceiling;
no follow-up model calls have been made.
