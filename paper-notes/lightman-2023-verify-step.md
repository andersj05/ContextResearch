---
title: "Let's Verify Step by Step"
authors: ["Hunter Lightman", "Vineet Kosaraju", "Yura Burda", "Harri Edwards", "Bowen Baker", "Teddy Lee", "Jan Leike", "John Schulman", "Ilya Sutskever", "Karl Cobbe"]
year: 2023
venue: "preprint"
source_type: "preprint"
paper_url: "https://arxiv.org/abs/2305.20050"
pdf_path: "papers/academic/lightman-2023-verify-step.pdf"
accessed: "2026-09-04"
review_status: "fully-reviewed"
evidence_confidence: "medium"
---

# lightman-2023-verify-step — Let's Verify Step by Step

## Why this source is in the corpus

Supports analysis of inference-time search, feedback, stopping, and verifier error.

## Research question

Does process supervision rank mathematical solutions better than outcome-only supervision?

## Harness mechanism studied

A process reward model scores each reasoning step and selects among many sampled solutions.

## Method and experimental setup

MATH data, process and outcome annotations, reward-model training, active learning, and best-of-1860 selection on a retained test subset.

## Main findings

- On the retained subset, process supervision reaches 78.2% at best-of-1860 versus 72.4% for outcome supervision and 69.6% majority vote.
- Active learning is reported as 2.6 times as label efficient.

## Mathematical content

Solution score is the product of per-step correctness probabilities, which creates acknowledged length bias.

## Evidence quality and limitations

4,500 original MATH test problems entered training and only 500 were retained; PRM and ORM data scales are not strictly matched; 1,860 samples per problem is extreme.

## Important implementation details

Keep evaluation problems untouched, match supervision data and generator, and report length effects and selection cost.

## Claims this source supports

Local process labels can provide better selection signal than final-answer labels in this setup.

## Claims this source weakens or contradicts

Headline results as a clean process-versus-outcome causal estimate or ordinary inference budget.

## Relevance to a mathematics paper

Provides a product-of-step-probabilities model and a concrete source of calibration bias.

## Connections to other sources

See the category and claim-level cross-references in [`INDEX.md`](INDEX.md) and the synthesis documents.

## Verification notes

Best-of-1860 table, scoring equation, active-learning result, dataset split, supervision mismatch, and limitations checked in the local PDF. The archived file parsed successfully: 29 pages, 53177 extractable characters, SHA-256 `fbd170e2042c32950c3fe97d3a558d89e8a8dffaadc942e774ccb4b751abc123`.
