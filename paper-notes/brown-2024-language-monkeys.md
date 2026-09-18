---
title: "Large Language Monkeys: Scaling Inference Compute with Repeated Sampling"
authors: ["Bradley Brown", "Jordan Juravsky", "Ryan Ehrlich", "Ronald Clark", "Quoc V. Le", "Christopher Ré", "Azalia Mirhoseini"]
year: 2024
venue: "preprint"
source_type: "preprint"
paper_url: "https://arxiv.org/abs/2407.21787"
pdf_path: "papers/academic/brown-2024-language-monkeys.pdf"
accessed: "2026-09-04"
review_status: "fully-reviewed"
evidence_confidence: "high"
---

# brown-2024-language-monkeys — Large Language Monkeys: Scaling Inference Compute with Repeated Sampling

## Why this source is in the corpus

Supports analysis of inference-time search, feedback, stopping, and verifier error.

## Research question

How far can repeated sampling increase the chance that at least one candidate is correct?

## Harness mechanism studied

Up to 10,000 samples per task are generated and evaluated by an oracle or available selector.

## Method and experimental setup

Four reasoning or coding tasks plus 250 SWE-bench Lite trajectories measure coverage curves and selector performance.

## Main findings

- SWE-bench Lite oracle coverage rises from 15.9% to 56%, above a cited 43% single-attempt result.
- Majority and reward-model selection plateau much earlier when no reliable automatic verifier exists.

## Mathematical content

Unbiased pass@k averages 1-C(N-C_i,k)/C(N,k); aggregate coverage is fit empirically by c=exp(a k^b).

## Evidence quality and limitations

Pass@k is oracle coverage, attempts are correlated and expensive, selector errors dominate deployment, and the empirical aggregate law is not per-task theory.

## Important implementation details

Report candidate coverage separately from selected accuracy, actual cost, latency, correlation, and verifier confusion.

## Claims this source supports

Sampling can expose latent solutions even when selection remains unsolved.

## Claims this source weakens or contradicts

Pass@k as reliability or practical task success.

## Relevance to a mathematics paper

Provides the combinatorial estimator later analyzed through mixture asymptotics.

## Connections to other sources

See the category and claim-level cross-references in [`INDEX.md`](INDEX.md) and the synthesis documents.

## Verification notes

Estimator, 10,000-sample setup, SWE-bench curve, selection plateau, scaling fit, and limitations checked in the local PDF. The archived file parsed successfully: 27 pages, 76196 extractable characters, SHA-256 `33889c6cb265ae11ed67e50070d3a31cd894036d8c9b404212a38df1783e8884`.
