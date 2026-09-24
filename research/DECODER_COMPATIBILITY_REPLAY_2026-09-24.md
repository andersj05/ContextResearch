# Parent certificates must compose with the child decoder

September 24, 2026. The [cross-record stress test](CROSS_RECORD_RECOVERY_2026-09-22.md)
found a specific implementation defect in its checked-proposal arm. A parent
could pass the exact-ID and relationship test while containing repeated
per-component `workflow_key` columns. The later child decoder supported only
the canonical joined paths and rejected those columns. Six affected evaluated
traces lost their checked child memory. The original study and its negative
terminal comparison remain frozen.

## Versioned correction

The new [compatibility module](../experiments/dependency_memory/cross_record_v2/compatibility.py)
adds a parent certificate before source deletion. It verifies supported field
paths, scalar types and enums, exact detected IDs and associations, unique
owner selection, and a 2,600-byte bound for every possible two-owner child.
After the branch audit below, it also runs the actual child check on every
pair before certifying a parent.
After candidates arrive, the selector matches only the root owner field; a
matching value in another field cannot divert selection. The child check
accepts only paths available in the parent. An incompatible model proposal
uses the deterministic projection as a fallback while source evidence is
still available. If that fallback fails the same certificate, the handoff is
infeasible. The old v1 implementation is not modified.

The [read-only replay](../experiments/dependency_memory/results/cross_record_v2_parent_replay.json)
uses the twelve saved structured parent proposals, including the original and
separately frozen continuation episode files. It checks the frozen v1 source
fingerprints and verifies matching parent bytes where both phases have an
episode. The v1 ID check passes nine parents. The v2 parent check passes
three. Of the six newly rejected proposals, all have unsupported parent
paths; two other proposals have unsupported paths and already failed v1, and
one fails the ID/relationship check. With fallback, all twelve admitted
parents can form and certify every possible two-owner child: **252 of 252
pair handoffs**, with largest child tables of 858–1,274 bytes. The original seven offline
tests included a constructed repeated-key proposal that passes v1 but fails
v2, exact owner selection in the presence of a colliding non-owner value,
and a valid ID certificate whose state value is wrong.

These are deterministic checks on already inspected constructed data. The
replay does not reuse old child-model responses under changed parent inputs,
invoke a final model, repair the 18 checked-arm errors, estimate full cost,
or turn the original 35-pair exploratory comparison into a new prospective
result. The ID certificate still permits a wrong but schema-valid state, and
all retained facts can still be misinterpreted at terminal execution. It is a
software handoff fix, not an execution-safety or performance result.

## Branch audit: counterexample and correction

A September 24 audit of branch commit `9442d73` found a second composition
failure despite all 368 existing tests passing. Add an ordinary string field
`description` to a development source, with values longer than 64 UTF-8 bytes.
The detector ignores that non-ID prose. A proposed parent can retain the same
IDs and add a schema-valid short `description`. The initial v2 certificate
accepts it: every two-row selection fits. But the child checker reclassifies
that short untyped string as unknown coverage and rejects the selected child.
Thus the initial implementation did not establish its advertised implication
for all supported inputs, although its saved twelve-parent replay was correct.

The corrected parent certificate executes the actual child check for every
owner pair while source evidence is still available. The counterexample now
receives `child_incompatible`, and a certified source projection replaces it
before deletion. Strict table parsing also rejects duplicate JSON members,
nonfinite numeric values and invalid string encodings; non-string proposals
return failure instead of crashing before fallback. Capacity tests use a
separate row-slicing serialization, including exact-cap and one-byte-short
cases. Row/column permutation controls preserve decoded source values.

The expanded sixteen-test module includes the counterexample, malformed-input
controls, failed-fallback behavior and missing/stale replay checks. The
repository validator now recomputes the committed replay rather
than leaving that comparison only to the test suite. Regeneration leaves the
saved 12-parent/252-pair diagnostic unchanged. These are software regression
checks, not new task samples or model observations.

Validation after the correction: 377 offline tests pass, the repository
validator reports PASS including 12 admitted parents and 252 owner pairs, and
the paper builds with 34 cited sources. No new model call was made.

A further negative control removes `scan.state` entirely and still passes
both certificates. Together with the wrong-state control, this makes the
boundary explicit: handoff compatibility does not establish retention of all
decision-relevant facts. No semantic or terminal-performance claim is added.

## Research decision

Further model calls on these known constructed grammars would mainly tune to
inspected failures. The next empirical test should freeze an externally
observed executable workflow, its delayed obligations and independent
terminal executor **before** fitting the extractor. The same source, public
side information, memory limits, archive permissions and terminal tasks must
be available to strong data-first prompting, hand-written direct receipts,
raw full-workflow indexed recovery, and full history. Compare terminal
success and total cost, including extraction, checking, index storage,
recovery, model calls and failed actions. Keep a separate execution guard arm:
its domain rule and cost must be explicit, since checking IDs cannot validate
a `publish` decision. If suitable untouched workflows cannot be obtained,
report that limit rather than promote another constructed replay as external
evidence. No new model allocation is implied by this decision.
