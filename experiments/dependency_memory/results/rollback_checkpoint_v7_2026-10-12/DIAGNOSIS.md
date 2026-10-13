# What the previous rollback experiment establishes

October 12, 2026. This is a code and saved-request diagnosis, not a new model
experiment or a causal decomposition of the v6 effect.

## The measured result is real, but its target is narrower than intended

The [fixed v6 comparison](../rollback_challenge_v6_four_actions_confirmation_2026-10-09/LIVE_RUN.md)
has K=122/254 known outcomes and R=64/258. Among 252 complete pairs, K alone
succeeds on 87 and R alone on 29. The result is negative under every completion
of the eight missing outcomes. This supports a negative finding about that
whole deletion-and-lesson policy on these authored ledger questions. It does
not isolate the effect of removing a failed attempt from an intact checkpoint.

## The controller deletes facts as well as failed work

The [v6 engine](../../rollback_challenge_v6/engine.py) appends a record containing
the current public packet, candidate and receipt into `state["history"]`.
Its inherited [intervention](../../rollback_development_v5/engine.py) empties the
entire history for R. The accepted artifact is only the current balance vector;
it is not a saved copy of the model-visible pre-failure context. Earlier packets
can therefore disappear even if they were used in successful earlier stages.

The task contract requires choosing the largest revision for each transaction
ID, resolving ties by sequence, excluding selected void records, and recomputing
all balances. A later record can replace a transaction from an earlier packet.
To do that from a previous balance vector, the solver needs to know the old
transaction contribution and whether the new record supersedes it. Aggregate
balances do not generally preserve that information.

An elementary illustration, not a sampled task: suppose A and B both transfer
money from account 0 to account 1. Amounts (10,20) and (15,15) give the same
balance vector (-30,30). A later instruction to void A should give (-20,20) in
the first history and (-15,15) in the second. The same saved balance and same
new instruction require different answers. No decoder can always recover the
right answer from those two inputs alone. Transaction-level retained state
would distinguish them.

## A saved model trajectory exhibits the failure path

Task `v6-confirmation-revision_ledger-8adc30a1caf2af0f` passes its first packet
of 26 records with the six balances `[37,-14,223,-130,-108,-8]`. Its stage-two
candidate then fails the public balance-0 check. The R-arm lesson
records general revision rules and feedback, without copying the old ledger.

The [next saved request](../rollback_challenge_v6_four_actions_confirmation_2026-10-09/live_confirmation/requests/54838cccf1bf274693aeb052961beca3921e76a9ff952fbdcb5e9bb5d6454bcb.json)
has empty history. In its [saved response](../rollback_challenge_v6_four_actions_confirmation_2026-10-09/live_confirmation/responses/54838cccf1bf274693aeb052961beca3921e76a9ff952fbdcb5e9bb5d6454bcb.json),
the model repeats the accepted balances and writes: “Retained the supplied
balances; the earlier packet details needed to reconcile revisions are not
included.” This statement is consistent with the actual supplied context.

This example proves an observed source-removal path, not that every R failure
has that cause or that it explains the entire measured deficit. A lesson may
preserve some facts in other cases. Deleted byte counts are not measurements
of Shannon information, and retained token counts do not establish sufficiency.
Fresh isolated requests also mean that private reasoning or a provider session
does not provide an intentionally available recovery channel in this harness.

A [post hoc scan of all saved received R actions](v6_source_loss_inspection.json)
finds this structural condition in **188 of 260 R episodes**, across 280 action
requests: stage two or three, empty raw history and public dossier, and retained
lesson memory. That means earlier packets were absent from the raw evidence
channels. The scan does not assert that lessons retained no facts, that each
deleted packet was necessary, or that these 188 tasks all failed.

## The corrected question

The [v7 protocol](../../rollback_checkpoint_v7/PROTOCOL.md) holds all released
public evidence and the full successful pre-failure checkpoint fixed. Both
continuations start from one shared naturally failed candidate, the same public
feedback and the same lesson. K retains the raw failed trial; R removes it.
No arm label appears in the actor input. The first requests must be identical
after removal of that one field, with independent checks against the original
packets to catch a mistaken omission from both arms.

This measures the marginal effect of retaining that visible failure, conditional
on its shared lesson and on a natural qualifying failure. It does not erase
everything learned from failure: the lesson can carry failed values or useful
observations. It does not manipulate private reasoning. The first pilot checks
execution and estimates a small conditional effect; it cannot establish a
general advantage or equivalence. Better scores than v6 would not by themselves
identify the effect of the repair, because the information environment changes.

For the broader research, rollback quality depends on the information boundary:
what counts as checkpoint, what is removable trial, and what facts future work
may need. The old study usefully demonstrates the risk of treating a task's
latest answer as if it were a sufficient memory of the task.

Under this specific ledger contract, a natural compact checkpoint would retain
the winning record for each transaction ID, including revision, tie-breaking
sequence, source, destination, amount and void flag. Preserve winning void
records as well: they determine that a later-arriving older revision must be
ignored. Updating that dictionary with a new packet and summing active transfers
is an elementary sufficient-state construction for these rules, not a novel
memory method or a measured model result. Testing that compact representation
would be a separate memory experiment from v7's full-evidence branch comparison.
