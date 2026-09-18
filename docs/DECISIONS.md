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

Open decisions: target venue, authorship, selected dependency family, exact chain optimum, model/environment for the pilot, spending budget, and power analysis. None is silently fixed by the repository setup.
