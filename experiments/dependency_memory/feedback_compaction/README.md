# Feedback before forgetting

An offline adapter and finite repair loop using the existing executable receipt
environment and collision auditor. No LLM or network calls.

```powershell
python -m experiments.dependency_memory.feedback_compaction.run
python -m unittest experiments.dependency_memory.feedback_compaction.test_feedback_compaction -v
```

The runner writes [a report](../results/feedback_compaction_report.md) and
[a source-hashed certificate](../results/feedback_compaction_certificate.json).
The full repo validator regenerates both in memory and checks for staleness.

- `workflow.py`: two actual record boundaries, visible-only parent/child
  selection, restored execution to derive accepted outcomes and tool responses.
- `feedback.py`: full audit, checked unsafe-group witnesses, accumulated or
  last-only constraints, failure-only enumeration and strong static controls.
- `run.py`: five methods across 48 contracts, complete primary traces, timing,
  partial-probe, identifier-channel and late-oracle controls.
- `test_feedback_compaction.py`: independent forward controllers, algebraic
  feasibility, channel access, executable replays and accounting invariants.

There are eight constructed worlds and six manifest/target continuations. Every
key/revision has a public two-token catalog. Revision tokens share an original
binary coordinate by design. The parent schema is fixed before the manifest;
the default child is fixed before the target. Constraints are synthesized
offline across worlds, not sent as realized-instance hints to the executor.

Memory is counted in tagged records with JSON bytes separate. Final archive
recovery costs three synthetic units. Nine other workflow units are charged
per episode. Offline work is reported as operation counts and is not equated
with those action prices or claimed to be free. The final recovery phase has
no further forced compaction; this is not a general bounded-memory planner.

`certified` concerns every declared route/world under the chosen candidate and
allowed final recovery policies. `exhausted_family` concerns only the finite
schema/child family. `cycle` and `round_limit` certify neither feasibility nor
impossibility. Ordinary retained-receipt execution is reported separately from
an optimal public-catalog decoder. All candidates may rely on fixed public code,
but source-specific feedback/history is absent after deletion.

The main loop repairs a weak schema, while the strong critical-fields baseline
matches it with fewer full audits. The identifier control attains four states
with one tagged record, demonstrating why records cannot be equated with bits.
These are constructed software diagnostics, not natural tasks, model trials,
matched-total-cost savings, semantic extraction or publication novelty.

[Research findings](../../../research/FEEDBACK_BEFORE_FORGETTING_2026-09-22.md)
and [next-stage design](../../../docs/FEEDBACK_RESEARCH_PROTOCOL.md).
