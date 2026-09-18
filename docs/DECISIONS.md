# Research decisions

These entries record the working interpretation of the discussion. Dates identify when a direction was adopted or documented, not an experimental result.

| Date | Decision | Reason and remaining question |
|---|---|---|
| 2026-09-16 | Separate output shaping, masking, summaries, opaque compaction, retrieval, and KV compression. | They change different information channels and have different cost models. |
| 2026-09-16 | Focus the first mathematical study on delayed dependencies and successive memory bottlenecks. | Finite encoders allow exact checks; a generic semantic theory is too broad for the first result. |
| 2026-09-16 | Treat the four-bit obstruction as a checked example, not a novelty claim. | Generalization and comparison with classical coding literature remain necessary. |
| 2026-09-16 | Use no archive in the first diagnostic, then evaluate equally metered recovery separately. | Retrieval changes the information constraints and invalidates a naive whole-system use of no-archive lower bounds. |
| 2026-09-18 | Make provider-managed reasoning continuity explicit in the experiment protocol. | Visible history edits can alter opaque state; a comparison must identify what it actually changes. |
| 2026-09-18 | Prefer a practical first intervention alongside supported native compaction. | Test dependency records and timing against a functioning native baseline with total-run accounting. |
| 2026-09-18 | Make `ContextResearch` the paper's working repository and preserve the original folder as a migration backup. | Keep the destination's existing Git history, import provenance, and avoid losing the broader source library. |
| 2026-09-18 | Use plain Markdown for the first drafts, with BibTeX references and an offline preview builder. | Documents remain easy for people and agents to edit; venue formatting can be selected once the paper has a clearer contribution. |

The [September 18 exploratory memo](../research/CREATIVE_RESEARCH_DIRECTIONS_2026-09-18.md) adds block and leave-one-out dependency families, a local robust-gap derivation, and an action-policy proposal. Its methodological recommendation is to require robustness to nonzero excess error before treating an exact-memory obstruction as practically important. These are research candidates, not a commitment to a model, environment, budget, or paper claim of novelty.

The user authorized a proof audit and one deterministic environment, with frequent commits on `task/` branches. The local audit preserves the block result, adds an analytic entropy lemma, and corrects the leave-one-out domain. Its independent formulations are not independent external review. The first environment will use a small artifact/manifest workflow and declared record budgets and action costs; it will not launch model calls.

The completed deterministic matrix uses five resource/availability settings, eight development seeds, two revision conditions, and four scripted policies. Its 320 configurations are diagnostics. The budgeted inspection rule has a declared two-unit price ceiling, so expensive inspection can trade success for cost; no optimality or cost-normalized superiority is claimed. A separately constructed paired witness restores context and environment and compares retention at equal cost. Source and fixture hashes plus fresh regeneration checks anchor the outputs.

Open decisions: target venue, authorship, final dependency family, exact chain optimum, model for the pilot, spending budget, and power analysis. None is silently fixed by the repository setup.

## September 18: autonomous follow-up and living draft

The user authorized research direction, further investigation, and a short draft to maintain as findings accumulate. Work continues on `task/recovery-frontier-draft`. The focused literature comparison narrows the claim: graph signatures, costed information acquisition, and repeated-compaction evaluation already have close precedents. The next bounded milestone is metered recovery plus an exact finite record-selection reference, followed by a concise findings draft and an updated manuscript. This milestone uses no model services; paid/model-dependent experiments still need their specified protocol.
