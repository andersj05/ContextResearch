# Decoder-compatible cross-record handoff check

This is a versioned offline correction to the [frozen v1 study](../cross_record/FROZEN_PROTOCOL.md).
The v1 source, requests, answers, and outcome scoring are unchanged.

The parent certificate requires:

1. A decodable field/row table within the 7,000-byte parent cap, with only
   paths, scalar types, and enum values supported by the public joined schema.
2. The v1 exact-ID and owner/path relationship check against the original
   public tool results while those results still exist.
3. A unique owner for every row and a child table within 2,600 bytes that passes
   the actual child checker for **every** possible pair of owner IDs, before
   the pair is disclosed. Selection and serialization alone are insufficient.

Both boundaries reject duplicate JSON members, nonfinite numbers (including
float overflow), and malformed string encodings. Invalid proposals produce
failed verdicts so that the parent fallback can run.

Selection after candidate disclosure matches the exact owner field. A child
proposal is checked against the bounded parent and cannot introduce paths
missing there. A failed parent proposal is replaced by the deterministic
projection before source deletion; if even that projection cannot be certified,
the handoff is infeasible. Repeated per-component `workflow_key` aliases are
rejected rather than passed through to a decoder that does not support them.

This certificate covers format, ID associations, and handoff reachability. It
does **not** require retention of non-ID state fields or prove that their values
equal the source, that a future event is applied correctly, or that a terminal
model answer is safe. A parent missing `scan.state` can pass. The terminal rule
and an execution guard are separate concerns.

Run `python -m experiments.dependency_memory.cross_record_v2.replay` to
recompute the [saved-parent diagnostic](../results/cross_record_v2_parent_replay.json).
It reads the original and separately frozen continuation episodes, confirms
their shared parent bytes when both contain one, and makes no model call. It
does not reuse the old child proposals or rescore terminal decisions. Run
`python -m unittest experiments.dependency_memory.cross_record_v2.test_compatibility -v`
for owner-selection, alias, type, capacity, malformed-input, and composition
tests. The repository validator also recomputes the saved replay and rejects
missing or changed results. See the [branch audit](../../../research/DECODER_COMPATIBILITY_REPLAY_2026-09-24.md#branch-audit-counterexample-and-correction)
for the counterexample that motivated checking the actual child contract.
