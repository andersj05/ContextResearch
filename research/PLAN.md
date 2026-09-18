# Research Plan

## Research question

What engineering mechanisms in an LLM harness measurably change an agent's capability,
reliability, cost, safety, and reproducibility, and which mathematical models are useful
for explaining or optimizing those mechanisms?

## Audience and intended use

The primary audience is a mathematics researcher preparing a paper. The corpus should
also be usable by an engineer who wants traceable design guidance rather than a list of
popular frameworks.

## Working definition

An **LLM harness** is the computational system around one or more model calls that selects
and transforms context, exposes actions, maintains state, schedules inference, interprets
outputs, executes effects, observes results, detects failures, and decides whether to
continue, retry, branch, verify, or stop.

This definition deliberately includes agent scaffolds, tool-use runtimes, coding-agent
harnesses, workflow engines, memory systems, evaluation harnesses, and multi-agent
orchestration when they determine model behavior.

## Scope

The broad corpus remains intact, but the active paper direction is the self-building and
self-improving-harness program specified in
[`SELF_IMPROVING_HARNESSES_PLAN.md`](SELF_IMPROVING_HARNESSES_PLAN.md). The focused work
treats context compilation as an editable harness component and separates candidate
search from statistically controlled promotion.

- Time: foundational work through the search date recorded in `SEARCH_LOG.md`.
- Geography: unrestricted; English-language sources are prioritized for feasible review.
- Academic topics: tool use, planning and search, reasoning scaffolds, reflection and
  verification, memory, context management, environment feedback, multi-agent systems,
  benchmark/harness sensitivity, automatic harness construction and revision, evaluation,
  reliability, and cost-aware inference.
- Engineering topics: open-source agent/coding harness architectures, execution loops,
  tool protocols, state and persistence, guardrails, observability, and evaluation.
- Mathematical topics: MDP/POMDP formulations, search and control, ensemble and
  self-consistency estimators, reliability/probability models, scaling laws, sequential
  decision rules, information-theoretic context selection, graph/workflow models,
  queueing/resource allocation, and benchmark statistics.

## Exclusions

- Pure model-architecture or training papers with no meaningful harness implication.
- Generic prompt collections without a documented method or evaluation.
- Marketing pages that do not expose implementation facts, measurements, or falsifiable claims.
- Duplicate versions of the same paper, except where version changes are material.
- Pirated or access-controlled copies; only author, publisher, repository, or other lawful
  public copies are archived.

## Source classes and priority

1. Original papers, proceedings, author manuscripts, official datasets, and standards.
2. Official repositories, documentation, architecture notes, and reproducible evaluations.
3. Methodologically transparent practitioner studies and engineering reports.
4. Commentary and social/forum material only as discovery signals or labeled anecdotes.

## Discovery and follow-up process

1. Map terminology and claim families; seed with surveys and landmark papers.
2. Search academic indexes, author pages, proceedings, and arXiv for each claim family.
3. Snowball backward through references and forward through closely related work.
4. Inventory representative open-source harnesses from official repositories and docs.
5. Search practitioner literature for implementation details and negative evidence.
6. Merge findings into the gap matrix, then run targeted searches for unsupported or
   contradictory consequential claims.
7. Spot-check high-impact claims against original PDFs/code and record version/access dates.
8. Stop when every synthesis section has primary evidence or an explicit limitation and
   additional searches produce predominantly duplicates or lower-quality corroboration.

## Evidence extraction

Every source note records bibliographic metadata, source class, problem, harness mechanism,
method, results, mathematical content, limitations, useful claims, and relevance. Numbers
must include their metric, denominator, benchmark/task set, baseline, and uncertainty when
reported. Claims must distinguish direct evidence from our inference.

## Planned deliverables

- A local PDF corpus with checksums and canonical URLs.
- A source catalog and claim-to-source ledger.
- A structured note for every included paper and important practitioner/harness source.
- Cross-source syntheses covering taxonomy, architectures, empirical evidence,
  mathematics, open-source implementations, practitioner evidence, and research gaps.
- A canonical `synthesis/report-source.md` that frames a defensible paper thesis.

## Success criteria

- Major claim families are represented by primary sources and important counterevidence.
- The corpus spans both academic abstractions and concrete harness implementations.
- Mathematical statements preserve assumptions, notation, and proof status.
- Benchmark claims are qualified by harness and evaluation configuration.
- Every archived file is traceable by URL, date, license/access status, and SHA-256 hash.
- Markdown files pass structural checks and local links resolve.

## Assumptions and limitations

- “Everything online” is treated as an exhaustive best-effort search, not a claim of
  literal completeness over an unbounded and fast-changing literature.
- Preprints may later change or be published; status is verified as of the access date.
- Repository behavior is version-specific. Notes should pin a release or commit where possible.
- Generated practitioner PDFs are avoided unless redistribution rights and rendering are clear;
  otherwise the canonical URL and a structured note preserve the evidence.
