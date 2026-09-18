# LLM Harness Engineering Research Corpus

This repository is a reproducible research corpus for a mathematics-oriented study of
LLM harness engineering: the software and protocol layer that surrounds a language
model with context assembly, tools, state, planning, execution, verification, recovery,
and evaluation.

The project distinguishes three kinds of evidence:

1. academic research and preprints;
2. official documentation and source code for open-source harnesses;
3. practitioner reports, engineering essays, and other non-peer-reviewed sources.

## Repository map

- `papers/academic/` — original research PDFs, named by year and first author.
- `papers/practitioner/` — practitioner PDFs when an official or legally accessible PDF exists.
- `paper-notes/` — one consistently structured Markdown note per academic paper.
- `source-notes/` — one consistently structured Markdown note per non-academic source or harness.
- `synthesis/` — cross-source findings, mathematical material, comparisons, and research agenda.
- `catalog/` — machine-readable source inventory and claim-to-source ledger.
- `research/` — scope, search log, gap matrix, and quality-control records.

## Current status

The expanded deep-research snapshot is current as of **2026-09-04**:

- **171 academic PDFs** (5,390 pages), each with a structured paper note;
- **16 practitioner/benchmark reports**, each with a structured evidence note;
- **32 version-pinned harness implementations**, including 14 optimizer and
  self-evolution implementations;
- **219 unified source records** and a bounded claim-to-source ledger;
- twelve cross-source synthesis documents plus a canonical report.

Start with [`synthesis/00-executive-map.md`](synthesis/00-executive-map.md) or read the
cohesive [`synthesis/report-source.md`](synthesis/report-source.md). The recommended
mathematics-paper direction is now a bounded self-improving context compiler: combine
task-relevant rate--distortion with a statistically valid promotion gate and test whether
adaptive search gains survive sealed evaluation. Alternatives are compared in
[`synthesis/08-paper-thesis-options.md`](synthesis/08-paper-thesis-options.md).

## Main research documents

1. [`Definitions and taxonomy`](synthesis/01-definitions-and-taxonomy.md)
2. [`Architecture and design patterns`](synthesis/02-architecture-and-design-patterns.md)
3. [`Empirical evidence and benchmark validity`](synthesis/03-empirical-evidence-and-benchmark-validity.md)
4. [`Mathematical foundations`](synthesis/04-mathematical-foundations.md)
5. [`Open-source and public harness implementations`](synthesis/05-open-source-harnesses.md)
6. [`Practitioner evidence`](synthesis/06-practitioner-evidence.md)
7. [`Research agenda`](synthesis/07-research-agenda.md)
8. [`Paper thesis options`](synthesis/08-paper-thesis-options.md)
9. [`Self-building and self-improving harnesses`](synthesis/09-self-building-and-self-improving-harnesses.md)
10. [`Mathematics of harness improvement`](synthesis/10-mathematics-of-harness-improvement.md)
11. [`Self-improving experimental blueprint`](synthesis/11-self-improving-experimental-blueprint.md)

Source-level navigation is available in [`paper-notes/INDEX.md`](paper-notes/INDEX.md),
[`source-notes/INDEX.md`](source-notes/INDEX.md), and
[`catalog/sources.csv`](catalog/sources.csv). Search scope and stopping criteria are in
[`research/PLAN.md`](research/PLAN.md), [`research/SEARCH_LOG.md`](research/SEARCH_LOG.md),
and [`research/GAP_MATRIX.md`](research/GAP_MATRIX.md). The latest automated integrity
and link audit is recorded in [`research/VALIDATION.md`](research/VALIDATION.md).

## Evidence labels

- **Peer reviewed** — accepted archival publication.
- **Preprint** — academic manuscript without verified archival acceptance.
- **Official implementation evidence** — project documentation, repository, code, or release notes.
- **Practitioner evidence** — experience report or technical argument without academic review.
- **Anecdotal** — useful for hypothesis formation, not for causal or general claims.

No benchmark number is treated as a property of a model alone unless the source controls
or reports the complete harness, prompt, tool, sampling, budget, and evaluation protocol.

## Important limits

“Everything online” is interpreted as broad best-effort coverage to mechanism saturation,
not literal completeness over a changing web. Seventy-one academic items are preprints.
Practitioner pages were not converted into PDFs when redistribution rights were unclear;
their canonical URLs, dates, and reviewed findings are preserved in `source-notes/`.
