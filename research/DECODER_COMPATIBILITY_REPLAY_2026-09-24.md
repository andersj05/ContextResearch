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
pair handoffs**, with largest child tables of 858–1,274 bytes. Seven offline
tests include a constructed repeated-key proposal that passes v1 but fails
v2, exact owner selection in the presence of a colliding non-owner value,
and a valid ID certificate whose state value is wrong.

These are deterministic checks on already inspected constructed data. The
replay does not reuse old child-model responses under changed parent inputs,
invoke a final model, repair the 18 checked-arm errors, estimate full cost,
or turn the original 35-pair exploratory comparison into a new prospective
result. The ID certificate still permits a wrong but schema-valid state, and
all retained facts can still be misinterpreted at terminal execution. It is a
software handoff fix, not an execution-safety or performance result.

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
