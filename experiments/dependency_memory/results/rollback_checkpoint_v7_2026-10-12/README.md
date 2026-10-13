# Matched checkpoint rollback v7 development pilot

Completed October 12 local / October 13 UTC: **K 10/16, R 8/16** eligible
paired tasks, with 130 known calls, no unknowns, eight concurrent workers and
a passing frozen-source audit. Read the [primary finding](LIVE_PILOT.md).
This small development result establishes neither benefit nor equivalence.

New October 12 allocation: 24 intermediate-profile revision ledgers, three
disclosure stages, four candidate actions, eight parallel Luna-medium workers,
and at most 192 admitted subscription generations. Read the
[frozen design](../../rollback_checkpoint_v7/PROTOCOL.md) and
[implementation guide](../../rollback_checkpoint_v7/README.md).
The [diagnosis of the previous result](DIAGNOSIS.md) traces the deleted facts
through source code and an actual saved model request.

The study holds the pre-failure checkpoint, every released public packet,
feedback and one shared lesson fixed. K retains the first failed visible trial;
R removes only that trial. Only naturally failed prefixes with an action left
and a valid shared lesson produce a pair. Initial successes and missing outcomes
remain separately reported. This is development evidence, not confirmation.

The authoritative allocation is [prepared_client_2026-10-12](prepared_client_2026-10-12/manifest.json),
with [scripted rehearsal](rehearsal_client_2026-10-12/analysis.json),
[rehearsal audit](rehearsal_client_audit.json), [live observations](live_pilot/analysis.json)
and [live audit](live_pilot_audit.json). Initial `prepared/`, `rehearsal/` and
`live/` paths preserve the earlier zero-admission client-preflight failure;
they are not another model allocation. Audit reports and repository check logs
stay outside sealed run directories. No admitted identity is reopened.

The key v6 limitation is source loss: clearing history deleted earlier public
transaction packets as well as failed candidates. A balance vector need not
retain the transaction-level information needed for later revisions. V7 instead
tests branch removal with full released evidence. Cross-study success-rate
differences cannot isolate the causal effect of this repair.

The treatment also has a useful qualification: a [post hoc inspection](lesson_overlap_inspection.json)
finds the failed balance vector repeated in 15 of 16 shared lessons. Removing
the raw record usually did not remove those values from the input. This pilot
tests raw-record retention conditional on a lesson; it does not test erasure of
all failed-answer information or private reasoning. See the primary finding
for uncertainty, accounting, validation and proposed next questions.
