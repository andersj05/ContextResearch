---
title: "The Self-Correction Illusion: Role Relabeling Gates Explicit Error Flagging in Large Language Models"
authors: ["Kuan-Yen Chen", "Fang-Yi Su", "Shih-Yen Lin", "Bao Li", "Jung-Hsien Chiang"]
year: 2026
venue: "preprint"
source_type: "preprint"
paper_url: "https://arxiv.org/abs/2606.05976"
pdf_path: "papers/academic/chen-2026-self-correction-illusion.pdf"
accessed: "2026-09-04"
review_status: "fully-reviewed"
evidence_confidence: "medium"
---

# chen-2026-self-correction-illusion — The Self-Correction Illusion: Role Relabeling Gates Explicit Error Flagging in Large Language Models

## Why this source is in the corpus

Supports analysis of inference-time search, feedback, stopping, and verifier error.

## Research question

Does the conversational role assigned to identical error text change whether a model flags it?

## Harness mechanism studied

A byte-identical wrong claim is relabeled as assistant thought, user input, tool output, or system memory before correction.

## Method and experimental setup

Twelve model-domain cells, controlled role relabeling, strict error-identification metrics, final-answer grading, and 10,000-sample paired bootstrap.

## Main findings

- Strict error identification rises by 23-93 points in 10 of 12 cells; Llama-70B math rises from 0 to 86.7 under memory role.
- Judge-verified final-answer changes are nonsignificant on two n=30 pools, and one memory condition falls from 70.0 to 56.7.

## Mathematical content

Uses paired correction-rate contrasts with a paired bootstrap; role is the controlled treatment.

## Evidence quality and limitations

Very recent preprint, small final-answer pools, chat-template dependence, and the diagnostic metric is not correctness.

## Important implementation details

Treat message role and provenance as part of context policy and evaluate error recognition separately from repaired answers.

## Claims this source supports

Harness serialization can gate whether a model criticizes identical content.

## Claims this source weakens or contradicts

Improved explicit error flagging as evidence of improved task accuracy.

## Relevance to a mathematics paper

Offers a clean categorical intervention for causal analysis of context encoding.

## Connections to other sources

See the category and claim-level cross-references in [`INDEX.md`](INDEX.md) and the synthesis documents.

## Verification notes

Role-control design, strict and final metrics, Table 11, paired bootstrap, and limitations checked in the local PDF. The archived file parsed successfully: 15 pages, 71947 extractable characters, SHA-256 `a79d3fb0bf8ee1e27c559d2a17cdf426a71de6958271d38b359bcc746521ef9e`.
