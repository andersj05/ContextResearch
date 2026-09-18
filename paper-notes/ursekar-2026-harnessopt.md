---
title: "HarnessOpt-Bench: Evaluating LLMs at Harness Optimization"
authors: ["Varun Ursekar", "Apaar Shanker", "Yash Maurya", "Shehab Yasser", "Vijay S. Kalmath", "Veronica Chatrath", "Yuan Xue"]
year: 2026
venue: "preprint"
source_type: "preprint"
paper_url: "https://arxiv.org/abs/2608.06301"
pdf_path: "papers/academic/ursekar-2026-harnessopt.pdf"
accessed: "2026-09-04"
review_status: "fully-reviewed"
evidence_confidence: "medium"
---

# ursekar-2026-harnessopt — HarnessOpt-Bench: Evaluating LLMs at Harness Optimization

## Why this source is in the corpus

Directly treats the harness, its optimization, or its runtime semantics as the object of study.

## Research question

How should a model's ability to optimize a stochastic and expensive harness be benchmarked?

## Harness mechanism studied

A trusted environment exposes a seed harness and development feedback, meters evaluation, hides test data, versions candidates, and scores a nominated final harness.

## Method and experimental setup

Five frontier optimizer models under shared and native coding harnesses, four downstream tasks, 111 scored runs, repeated held-out evaluation.

## Main findings

- Optimizer models separate more than the coding harnesses they use; native coding harnesses are not consistently superior.
- Gains vary strongly by task and seed, and selected validation winners can underperform on held-out tests.

## Mathematical content

Defines normalized held-out gain over a pinned seed and analyzes noisy search under fixed target-evaluation budgets; confidence bands are heuristic rather than formal tests.

## Evidence quality and limitations

Only four tasks and 111 runs, optimizer inference left uncapped, seed harness is a strong task-specific prior, and all results are new.

## Important implementation details

Isolate credentials and test state, meter target-agent evaluations, preserve every candidate, and require one nominated final version.

## Claims this source supports

Harness optimization is measurable only with held-out state and enforced budgets.

## Claims this source weakens or contradicts

A self-improving score trace as evidence of general improvement.

## Relevance to a mathematics paper

Supplies a bilevel, noisy-budgeted optimization protocol and normalized response variable.

## Connections to other sources

See the category and claim-level cross-references in [`INDEX.md`](INDEX.md) and the synthesis documents.

## Verification notes

Abstract, trusted-execution Figure 1, objective, Tables 1-3, budget accounting, validation-test comparison, and limitations checked in the local PDF. The archived file parsed successfully: 27 pages, 59150 extractable characters, SHA-256 `7e8e92f025ede0b279990a9de59827669ef143ca7bd8e1ced56faea7def28152`.
