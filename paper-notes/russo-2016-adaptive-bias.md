---
title: "How Much Does Your Data Exploration Overfit? Controlling Bias via Information Usage"
authors: ["Daniel Russo", "James Zou"]
year: 2016
venue: "IEEE-TIT-2020"
source_type: "peer-reviewed"
paper_url: "https://arxiv.org/abs/1511.05219"
pdf_path: "papers/academic/russo-2016-adaptive-bias.pdf"
accessed: "2026-09-04"
review_status: "skimmed"
evidence_confidence: "high"
---

# russo-2016-adaptive-bias — How Much Does Your Data Exploration Overfit? Controlling Bias via Information Usage

## Why this source is in the corpus

Directly studies reusable harness components, outer-loop optimization, self-modification, or the statistical controls needed to decide whether an update is a real improvement.

## Research question

How can expected selection bias from adaptive data exploration be bounded by the information used to choose the reported statistic?

## Harness mechanism studied

Mutual information between selected index T and the vector of realized statistics quantifies how strongly selection depends on their noise.

## Method and experimental setup

Information-theoretic upper bounds, matching Gaussian examples, extensions, and simulations for adaptive selection.

## Main findings

- Expected bias is controlled by the square root of mutual information, with a matching natural model showing the dependence is tight up to constants.
- Selecting among m possibilities gives a log m ceiling, but the theorem is an expectation bound rather than a one-run high-probability certificate.

## Mathematical content

Proposition 1: if every phi_i-mu_i is sigma-sub-Gaussian, |E[phi_T]-E[mu_T]| <= sigma sqrt(2 I(T;phi)). For averages of n iid sigma-sub-Gaussian observations, the right side is sigma sqrt(2I/n); since I<=H(T)<=log m, it is at most sigma sqrt(2log(m)/n).

## Evidence quality and limitations

Mutual information may be hard to compute; expectation control can hide tail risk; the finite-index corollary does not directly cover open-ended program synthesis; sub-Gaussian and iid assumptions need checking.

## Important implementation details

Limit score precision and diagnostics, estimate or upper-bound transcript information, cap the candidate family, and retain a high-probability outer validation gate.

## Claims this source supports

Evaluator leakage and candidate multiplicity have a quantitative bias cost even when the adaptive algorithm is otherwise arbitrary.

## Claims this source weakens or contradicts

The claim that the number of visible iterations alone determines bias or that the square-root formula is automatically a high-probability correction.

## Relevance to a mathematics paper

Provides the cleanest information-usage estimator for expected adaptive optimism and links feedback design to sample size.

## Connections to other sources

See the category and claim-level cross-references in [`INDEX.md`](INDEX.md) and the synthesis documents.

## Verification notes

Local PDF Proposition 1 on pp. 2-3, iid corollary, matching lower bound, and information-budget discussion checked. The archived file parsed successfully: 23 pages, 109520 extractable characters, SHA-256 `6cde2c14238f0440e1506458ff28cd609d26104dc232579a3fe0361ec42e7c38`.
