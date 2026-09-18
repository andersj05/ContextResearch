---
title: "Meta-Harness: End-to-End Optimization of Model Harnesses"
authors: ["Yoonho Lee", "Roshen Nair", "Qizheng Zhang", "Kangwook Lee", "Omar Khattab", "Chelsea Finn"]
year: 2026
venue: "preprint"
source_type: "preprint"
paper_url: "https://arxiv.org/abs/2603.28052"
pdf_path: "papers/academic/lee-2026-meta-harness.pdf"
accessed: "2026-09-04"
review_status: "skimmed"
evidence_confidence: "medium"
---

# lee-2026-meta-harness — Meta-Harness: End-to-End Optimization of Model Harnesses

## Why this source is in the corpus

Directly treats the harness, its optimization, or its runtime semantics as the object of study.

## Research question

Can an agent optimize complete harness code using prior source, traces, and scores?

## Harness mechanism studied

An outer-loop proposer reads every prior candidate through a filesystem and edits storage, retrieval, context, and control code.

## Method and experimental setup

Online text classification, 200 IMO-level retrieval-augmented math problems over five held-out models, and TerminalBench-2 compare discovered and hand-built harnesses.

## Main findings

- Meta-Harness reports a 7.7-point classification gain with four times fewer context tokens.
- One discovered math harness improves accuracy by 4.7 points on average across five held-out models and coding harnesses surpass selected hand-engineered baselines.

## Mathematical content

Noisy black-box optimization over programs; the objective is validation performance subject to implicit compute and context costs, without a global convergence theorem.

## Evidence quality and limitations

Author-selected tasks and search budgets, possible validation overfitting, expensive outer-loop compute, and a very recent preprint.

## Important implementation details

Retain full candidate history and traces rather than compressing feedback to a scalar; freeze a final candidate before held-out testing.

## Claims this source supports

Rich execution history can support automatic harness optimization that transfers across some models.

## Claims this source weakens or contradicts

Validation-set improvement as a guarantee of general or safe recursive self-improvement.

## Relevance to a mathematics paper

Provides a concrete bilevel optimization target for a mathematics paper.

## Connections to other sources

See the category and claim-level cross-references in [`INDEX.md`](INDEX.md) and the synthesis documents.

## Verification notes

Abstract, optimizer architecture, three task families, held-out-model result, cost claims, and limitations checked in the local PDF. The archived file parsed successfully: 26 pages, 83480 extractable characters, SHA-256 `7d9b90f53a9f4801a090f1a4acb843340cde81e4f865f97d53fff2a6a570eb73`.
