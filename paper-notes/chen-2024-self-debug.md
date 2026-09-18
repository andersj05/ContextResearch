---
title: "Teaching Large Language Models to Self-Debug"
authors: ["Xinyun Chen", "Maxwell Lin", "Nathanael Schärli", "Denny Zhou"]
year: 2024
venue: "ICLR-2024"
source_type: "peer-reviewed"
paper_url: "https://arxiv.org/abs/2304.05128"
pdf_path: "papers/academic/chen-2024-self-debug.pdf"
accessed: "2026-09-04"
review_status: "skimmed"
evidence_confidence: "medium"
---

# chen-2024-self-debug — Teaching Large Language Models to Self-Debug

## Why this source is in the corpus

Supports analysis of inference-time search, feedback, stopping, and verifier error.

## Research question

Can models explain and repair generated code using execution or self-generated feedback?

## Harness mechanism studied

A debug loop conditions revisions on code explanations, unit-test outcomes, or simulated execution traces.

## Method and experimental setup

Program-synthesis benchmarks compare direct generation with multiple self-debugging feedback variants and iteration budgets.

## Main findings

- Execution feedback generally provides a stronger correction signal than unguided reconsideration.
- Explanation can help expose intent and localize errors, but repeated debugging also incurs extra calls and may overfit visible tests.

## Mathematical content

The loop is an iterative repair policy over program and feedback state; observed pass rate is conditional on test-oracle coverage.

## Evidence quality and limitations

Generated or public tests can be incomplete, models and tasks are small, and feedback variants change information content.

## Important implementation details

Keep hidden tests separate, record every candidate and failing test, and distinguish syntax, runtime, and semantic repair.

## Claims this source supports

Executable feedback is a strong harness signal for code agents.

## Claims this source weakens or contradicts

Passing self-generated or visible tests as proof of semantic correctness.

## Relevance to a mathematics paper

Enables Markov repair-chain and imperfect-verifier analysis.

## Connections to other sources

See the category and claim-level cross-references in [`INDEX.md`](INDEX.md) and the synthesis documents.

## Verification notes

Abstract, feedback variants, iteration protocol, result tables, error analysis, and limitations checked in the local PDF. The archived file parsed successfully: 78 pages, 193519 extractable characters, SHA-256 `020e06b1fb9e1d4b6c33016a9471e8bd31f8ecfd7a22335d85956c14efa39f75`.
