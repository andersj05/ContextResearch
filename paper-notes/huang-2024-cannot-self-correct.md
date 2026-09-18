---
title: "Large Language Models Cannot Self-Correct Reasoning Yet"
authors: ["Jie Huang", "Xinyun Chen", "Swaroop Mishra", "Huaixiu Steven Zheng", "Adams Wei Yu", "Xinying Song", "Denny Zhou"]
year: 2024
venue: "ICLR-2024"
source_type: "peer-reviewed"
paper_url: "https://arxiv.org/abs/2310.01798"
pdf_path: "papers/academic/huang-2024-cannot-self-correct.pdf"
accessed: "2026-09-04"
review_status: "fully-reviewed"
evidence_confidence: "high"
---

# huang-2024-cannot-self-correct — Large Language Models Cannot Self-Correct Reasoning Yet

## Why this source is in the corpus

Supports analysis of inference-time search, feedback, stopping, and verifier error.

## Research question

Can LLMs improve reasoning through intrinsic self-correction when oracle information is removed?

## Harness mechanism studied

Repeated reconsideration, debate, and self-refinement are compared under oracle-stopping and equal-response-count controls.

## Method and experimental setup

GSM8K and related reasoning tasks use GPT-3.5 and GPT-4, transition accounting, stronger initial prompts, and compute-matched self-consistency.

## Main findings

- Oracle stopping raises GPT-3.5 GSM8K from 75.9 to 84.3, but intrinsic rounds reduce it to 75.1 and 74.7; GPT-4 falls 95.5 to 91.5 to 89.0.
- Compute-matched self-consistency scores 85.3/88.2 versus debate at 83.2/83.0.

## Mathematical content

Uses correct-to-incorrect and incorrect-to-correct transition counts and equal generation budgets; no universal impossibility theorem.

## Evidence quality and limitations

Tested models and prompts are dated; the title is broader than the evidence; later role and decoding conditions show narrow exceptions.

## Important implementation details

Audit transition directions, remove oracle stopping, and compare with a stronger first attempt and equal-cost resampling.

## Claims this source supports

Intrinsic correction often fails without new external information.

## Claims this source weakens or contradicts

Claims that asking a model to reconsider reliably improves reasoning.

## Relevance to a mathematics paper

Supports transition-matrix analysis of iterative correction and stopping bias.

## Connections to other sources

See the category and claim-level cross-references in [`INDEX.md`](INDEX.md) and the synthesis documents.

## Verification notes

GSM8K tables, oracle-stopping comparison, transition analysis, equal-response debate comparison, and limitations checked in the local PDF. The archived file parsed successfully: 17 pages, 57879 extractable characters, SHA-256 `15e1731e255ec6b217792a1e077926807da77e8e46b69e6c57dda30d67794761`.
