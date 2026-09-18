---
title: "Self-Consistency Improves Chain of Thought Reasoning in Language Models"
authors: ["Xuezhi Wang", "Jason Wei", "Dale Schuurmans", "Quoc Le", "Ed Chi", "Sharan Narang", "Aakanksha Chowdhery", "Denny Zhou"]
year: 2022
venue: "ICLR-2023"
source_type: "peer-reviewed"
paper_url: "https://arxiv.org/abs/2203.11171"
pdf_path: "papers/academic/wang-2022-self-consistency.pdf"
accessed: "2026-09-04"
review_status: "fully-reviewed"
evidence_confidence: "high"
---

# wang-2022-self-consistency — Self-Consistency Improves Chain of Thought Reasoning in Language Models

## Why this source is in the corpus

Supports analysis of inference-time search, feedback, stopping, and verifier error.

## Research question

Does sampling diverse reasoning paths and voting improve chain-of-thought answers?

## Harness mechanism studied

Independent stochastic chain-of-thought samples are aggregated by the modal extracted answer.

## Method and experimental setup

Multiple reasoning benchmarks and model scales compare greedy chain-of-thought with roughly 40 sampled paths and optional weighting.

## Main findings

- Reported gains include 17.9 points on GSM8K, 11.0 on SVAMP, 12.2 on AQuA, 6.4 on StrategyQA, and 3.9 on ARC-Challenge.
- The method spends many more generations and assumes the modal answer is likely correct.

## Mathematical content

The estimator is a-hat=argmax_a sum_i 1[a_i=a], optionally likelihood weighted; it is a Monte Carlo mode estimator, not a correctness guarantee.

## Evidence quality and limitations

Correlated errors reduce effective sample size, extraction rules affect votes, and majority can amplify a shared misconception.

## Important implementation details

Log each sample, extraction rule, vote distribution, and actual generation count; compare at equal cost.

## Claims this source supports

Sampling plus aggregation is a strong simple baseline for more elaborate search.

## Claims this source weakens or contradicts

Multi-agent or tree-search gains that are not compared with compute-matched voting.

## Relevance to a mathematics paper

Provides a basic ensemble estimator and motivates correlation-aware effective sample size.

## Connections to other sources

See the category and claim-level cross-references in [`INDEX.md`](INDEX.md) and the synthesis documents.

## Verification notes

Main result tables, sampling and voting equation, weighting ablation, sample counts, and limitations checked in the local PDF. The archived file parsed successfully: 24 pages, 90721 extractable characters, SHA-256 `1a49ce0373afc89d2d6e97fb1aa8230f6b818c70590d732a3187f753f4df6aba`.
