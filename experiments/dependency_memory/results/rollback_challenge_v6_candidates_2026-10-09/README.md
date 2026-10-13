# V6 candidate-required follow-up: completed

October 9, 2026. This is a separate six-question development screen informed by
the [completed initial control screen](../rollback_challenge_v6_2026-10-09/LIVE_SCREEN.md).
The user has now [authorized thousands of Luna requests](campaign_authorization.json)
for the research goal without per-run reconfirmation. The [six-question allocation](screen_authorization.json)
is complete with 56 metered responses against its 84-generation maximum, with
no unknowns. Read the [live finding](LIVE_SCREEN.md): all actions submit candidates,
but no task group qualifies under the original calibration rule.
The agent's additional campaign working ceiling is 6,000 admissions, including
writers and unknowns. The initial screen remains closed at 165 admissions.

## Why this follow-up

The initial screen is below the old ceiling: each control solves 6/16 known
episodes, with two missing outcomes each. But 92 of 154 received actions defer
candidate submission, and 17 of 20 known failures never reach a public mismatch.
No cell qualifies for difficulty validation. These are preserved negative
calibration results, not evidence about rollback's effect.

The new response contract requires the best complete candidate on every action,
even under uncertainty, and prohibits deliberately wrong attempts. Deferral is
an invalid received record; the controller never invents an answer or feedback.
The public graders, checkpoints, intervention policies, writer metering and
information isolation are unchanged. This is another development screen after
an interface change, not independent validation of the initial result.

## Fixed allocation

| Setting | Frozen value |
|---|---|
| Model / effort | `gpt-6-luna` / `medium`, existing subscription |
| Tasks | Two each: bitvector program level 1, constraint grid level 2, revision ledger level 2 |
| Root seed | `2026100943`; task identities are disjoint from the initial screen |
| Response contract | `require_candidates=true` |
| Arms | K retains trial history and writes lessons; F solves afresh from released packets |
| Episodes | 12: six paired K/F tasks |
| Stages / actions | Three disclosure stages, at most five actions per episode |
| Maximum generations | 84, including lesson writers and unknown admissions |
| Workers | At most four |
| Retry policy | No retries of admitted identities; unknowns remain missing |

The [manifest](prepared/manifest.json) SHA-256 is
`bdb1fd85c55aefe82fc44b3949faa76298a2e65add602ff43d5062ee4a10c7d6`.
The [source snapshot](prepared/source_snapshot.zip), [tasks](prepared/tasks.json),
and [protocol](../../rollback_challenge_v6/PROTOCOL.md) bind the design.
Task files contain evaluator witnesses and must not be passed wholesale to actors.
The [example requests](example_action_requests.json) expose only the allowed
first-action state for one task in each family.

The maximum combined admissions are 165 completed-screen admissions plus 84
proposed follow-up admissions, or 249. This arithmetic does not transfer the
closed screen's authorization to a new allocation; the later broad authorization
now covers this run and later separately frozen stages. No R arm, independent
difficulty validation, or powered comparison is included in this six-task screen.

## Offline verification

All six tasks pass [576 separate-formulation witness/mutation checks](prepared/verification.json).
The [rehearsal](rehearsal/analysis.json) executes all 12 fixture episodes with
54 scripted responses, four configured workers and a peak of four admitted
fixture calls. [Independent replay](rehearsal_audit.json) reproduces every
request, response, grade, episode and accounting record. Scripted answers use
evaluator witnesses and are not model performance or evidence of task difficulty.
The [33-test package log](checks/package_tests.txt) covers legacy compatibility,
the new response contract, task identities, inherited validation settings and
receipt replay. The earlier full-suite checkpoint is separate; it was not
rerun for this scoped response-contract change.

[Installed-client checks](client_preflight.json) also pass, including the new
candidate-only payload for all three families. They use a read-only subscription
catalog check and unauthenticated localhost probes, with zero model generations.
The live runner repeats its preflight before dispatch.

The [verification summary](verification_summary.json) records all checks,
including 259 passing scientific-validation categories, navigation/catalog checks,
the source freeze and disjoint task identities. The full scientific validator
does not replace the separately reported package tests or live evidence audits.
Its recorded pending-authorization state is historical and is superseded by
the later direct user authorization linked above.

The completed initial screen also passes [historical snapshot replay](../rollback_challenge_v6_2026-10-09/live_screen_snapshot_audit.json)
after the shared source changes: all 161 known calls and all four unknowns remain
intact. No old task, response, score or source snapshot was rewritten.

## Decision rule

Use the same control-only completeness, success-rate, public-mismatch and
capacity gates as the initial screen. A new cell must qualify before preparing
independent difficulty validation on at least eight new tasks per cell. Any
later confirmation requires its own fixed sample and allocation before R/K
outcomes. Failure to qualify is a valid reported outcome; neither the interface
change nor a sample-size calculation guarantees significance.
