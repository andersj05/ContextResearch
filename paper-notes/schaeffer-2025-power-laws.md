---
title: "How Do Large Language Monkeys Get Their Power (Laws)?"
authors: ["Rylan Schaeffer", "Joshua Kazdan", "John Hughes", "Jordan Juravsky", "Sara Price", "Aengus Lynch", "Erik Jones", "Robert Kirk", "Azalia Mirhoseini", "Sanmi Koyejo"]
year: 2025
venue: "ICML-2025"
source_type: "peer-reviewed"
paper_url: "https://arxiv.org/abs/2502.17578"
pdf_path: "papers/academic/schaeffer-2025-power-laws.pdf"
accessed: "2026-09-04"
review_status: "fully-reviewed"
evidence_confidence: "high"
---

# schaeffer-2025-power-laws — How Do Large Language Monkeys Get Their Power (Laws)?

## Why this source is in the corpus

Provides estimators or asymptotic models needed to distinguish coverage, reliability, and deployable utility.

## Research question

Why can benchmark-average repeated-sampling curves look polynomial when each task's failure decays exponentially?

## Harness mechanism studied

A heterogeneous distribution of single-attempt success probabilities mixes per-task geometric failure curves.

## Method and experimental setup

Theory plus empirical inference-scaling datasets compare direct curve fitting with forecasts derived from the distribution of task success probabilities.

## Main findings

- Each task has iid failure (1-p_i)^k, but a heavy density of tasks near p=0 makes the benchmark average decay like a power law.
- Distribution-based exponent forecasts have about an order-of-magnitude lower relative error or require two to four orders less compute.

## Mathematical content

If f(p) is asymptotic to C p^(b-1) near zero, then E[(1-p)^k] is asymptotic to C Gamma(b) k^(-b).

## Evidence quality and limitations

Assumes iid attempts with fixed per-task p; adaptive search, correlated samples, changing task mixtures, and verifier selection fall outside the theorem.

## Important implementation details

Estimate per-task difficulty distribution and correlations before extrapolating aggregate scaling.

## Claims this source supports

Observed aggregate power laws can be mixture effects rather than per-task laws.

## Claims this source weakens or contradicts

A universal power law intrinsic to every task or model.

## Relevance to a mathematics paper

Offers a clean asymptotic theorem and a mathematically promising thesis component.

## Connections to other sources

See the category and claim-level cross-references in [`INDEX.md`](INDEX.md) and the synthesis documents.

## Verification notes

Theorem assumptions and proof, empirical forecast comparison, heavy-tail diagnostics, and limitations checked in the local PDF. The archived file parsed successfully: 46 pages, 139487 extractable characters, SHA-256 `f92c1a62f7e7a5aac8e9d0622fb4dca3ae85e4b735465c08702e80bf709cae65`.
