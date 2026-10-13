# V6 difficulty screen: below the ceiling, but no eligible recovery cell

October 9, 2026. The authorized 18-task K/F screen has finished all 36 episode
dispositions. It admitted 165 calls against a 252-generation ceiling: 161 metered
responses and four retained unknowns. The unknown calls are never retried or
scored wrong. Four workers ran the episodes in 979.3 seconds, excluding preflight.
[Independent replay](live_screen_audit.json) reproduces every known response,
grade, outcome and accounting record and preserves the four missing outcomes.

K retains trial history and writes lessons after public mismatches. F starts
each action from the initial artifact and all released public packets, without
trial history, lessons or failure feedback. Both use Luna medium, three disclosure
stages and at most five candidate/progress actions. R was not run in this screen.

## Complete-episode success

Each cell contains two tasks per arm. Fractions below use known outcomes;
missing episodes are stated explicitly. These are small development cells.

| Family | Level | K success | F success | K episodes with a public mismatch | Calibration result |
|---|---:|---:|---:|---:|---|
| Bitvector program | 1 | 1/2 | 1/2 | 0 | Mixed success, but no rollback trigger |
| Bitvector program | 2 | 0/2 | 0/2 | 0 | Observed floor and no trigger |
| Bitvector program | 3 | 0/2 | 0/2 | 0 | Observed floor and no trigger |
| Constraint grid | 1 | 2/2 | 2/2 | 0 | Observed ceiling |
| Constraint grid | 2 | 1/2 | 0/2 | 0 | F floor and no K trigger |
| Constraint grid | 3 | 0/2 | 0/1; 1 missing | 0 | Floor/incomplete |
| Revision ledger | 1 | 2/2 | 2/2 | 0 | Observed ceiling |
| Revision ledger | 2 | 0 known; 2 missing | 1/1; 1 missing | 2 | Incomplete |
| Revision ledger | 3 | 0/2 | 0/2 | 1 | Observed floor |

Each arm solves 6/16 known episodes (37.5%), with two missing episodes. Its
fixed-18-task missingness bounds are 6/18 to 8/18, or 33.3% to 44.4%. These are
missing-outcome bounds, not population confidence intervals. Thus this constructed
mixture is clearly below the v5 ceiling, even if every unknown eventually proved
successful. It mixes easy and very hard levels rather than establishing a stable
intermediate-difficulty distribution. A cell result of 1/2 has a Wilson 95%
interval of approximately 9.5% to 90.5%.

## Why the selection is empty

The [frozen selection](screen_selection.json) nominates no cells. In particular,
the level-1 bitvector cell reaches 50% in both arms but has no K public mismatch.
Removing that prespecified requirement after observing the result would not
establish recoverable failure or justify a confirmatory rollback study.

Among 154 received action responses, 92 select `continue`, 44 pass a public
stage, and 18 produce a public mismatch. K has 49 progress-only actions and F has
43. Seventeen of the twenty known failed episodes exhaust the action budget
without any public mismatch. All grid/program episodes have zero public
mismatches. For example, one failed program episode repeatedly reports that no
verified program has been found and never submits a candidate in five actions.

The current controller intervenes after a checker rejection, so these deferrals
do not exercise rollback. A fresh provider thread receives only visible notes
and artifacts, not the previous call's private reasoning. A `continue` action
cannot preserve that opaque work. This is a limitation of the tested interface,
not evidence that deletion helps or harms model reasoning.

Every known failure is action-budget exhaustion. There are no observed malformed
record or context-capacity dispositions, so the capacity guard did not exclude
any cell. The four unknowns occur on action calls: both K ledger-level-2 episodes,
one F ledger-level-2 episode, and one F grid-level-3 episode. Their safe diagnostics
identify collection-phase provider/generation failures but do not establish the
underlying server cause.

## Resources and next design

Known usage totals 816,420 input tokens (including 186,624 cached), and 345,420
output tokens (including 334,411 reasoning). Calculated known usage is 5.9388960
planning credits, with 16.900 reserved for unknown calls. Planning credits are
declared accounting units, not actual subscription charges.

The next development candidate is a separately frozen screen requiring a best
complete candidate on every action, while still instructing the model not to
invent wrong attempts. It should use new seeds and retain K/F-only selection.
The current allocation is closed; its tasks, protocol snapshot, observations and
unknowns remain intact. Independent difficulty validation and any powered R/K
comparison remain unperformed. This screen contains no rollback-effect estimate
or statistical-significance finding.

Primary artifacts: [analysis](live_screen/analysis.json),
[execution](live_screen/execution.json), [authorization](screen_authorization.json),
[frozen manifest](prepared_screen_v2/manifest.json),
[source snapshot](prepared_screen_v2/source_snapshot.zip),
[client preflight](live_screen/preflight.json), and [replay audit](live_screen_audit.json).
