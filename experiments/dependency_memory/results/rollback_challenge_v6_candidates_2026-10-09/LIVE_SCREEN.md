# Candidate-required screen: answers replace deferrals, original selection remains empty

October 9, 2026. The six-question follow-up finishes all twelve K/F episodes with
56 metered responses, no unknowns and no global stop. All 49 action responses
submit candidates; seven additional calls write lessons. Four workers finish in
401.3 seconds excluding preflight. Both the [original audit](live_screen_audit.json)
and [historical-source replay](live_screen_snapshot_audit.json) reproduce all
received calls, grades, outcomes and accounting records.

| Family / level | K success | F success | K episodes with a public mismatch |
|---|---:|---:|---:|
| Bitvector program / 1 | 2/2 | 2/2 | 0 |
| Constraint grid / 2 | 2/2 | 0/2 | 1 |
| Revision ledger / 2 | 1/2 | 2/2 | 2 |

K solves 5/6 complete episodes and F solves 4/6. All three failures exhaust the
five-action budget. There are no progress-only actions, malformed records,
context-capacity failures or missing outcomes. Because these are new tasks and
provider draws, the difference from the earlier screen is not an isolated causal
estimate of the response-interface change.

The [frozen selection](screen_selection.json) is empty. The program cell is at
the observed ceiling, the grid cell combines K's ceiling with F's floor, and the
ledger cell is excluded by F's ceiling. Keep this result under its original rule;
do not retroactively mark the ledger cell eligible. With only two tasks, an
observed 1/2 rate has a Wilson 95% interval of about 9.5% to 90.5%, and 2/2 has
an interval of about 34.2% to 100%.

The ledger pattern motivates a new development design: allow a fresh control to
establish solvability at high success while requiring the history-retaining K
control to remain below the ceiling. This is control-informed design adaptation
before any R outcome, not evidence that rollback helps. The next screen uses
new seeds and a manifest-bound rule; independent difficulty validation and a
fixed-size R/K comparison remain necessary.

Known usage is 284,936 input tokens, including 43,008 cached, and 135,616 output
tokens, including 129,549 reasoning tokens. Its declared accounting conversion
is 2.3107720 planning credits, not an actual subscription charge. All 56 admitted
calls count against the [additional campaign working ceiling](campaign_budget.json).
The earlier eighteen-question screen remains closed at 165 admissions.

Primary evidence: [analysis](live_screen/analysis.json),
[execution](live_screen/execution.json), [manifest](prepared/manifest.json),
[source snapshot](prepared/source_snapshot.zip), [authorization](screen_authorization.json),
and [sealed inventory](live_screen/evidence_manifest.json). No R arm was run and
no rollback-effect or statistical-significance result is claimed.
