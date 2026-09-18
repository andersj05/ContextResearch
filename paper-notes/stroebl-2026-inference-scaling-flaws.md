---
title: "Inference Scaling fLaws: Limits of LLM Resampling with Imperfect Verifiers"
authors: ["Benedikt Stroebl", "Sayash Kapoor", "Arvind Narayanan"]
year: 2026
venue: "ICLR-2026"
source_type: "peer-reviewed"
paper_url: "https://arxiv.org/abs/2411.17501"
pdf_path: "papers/academic/stroebl-2026-inference-scaling-flaws.pdf"
accessed: "2026-09-04"
review_status: "fully-reviewed"
evidence_confidence: "high"
---

# stroebl-2026-inference-scaling-flaws — Inference Scaling fLaws: Limits of LLM Resampling with Imperfect Verifiers

## Why this source is in the corpus

Provides estimators or asymptotic models needed to distinguish coverage, reliability, and deployable utility.

## Research question

When does resampling become harmful under an imperfect verifier?

## Harness mechanism studied

A generator produces candidates and a verifier selects or accepts them with nonzero false positives and false negatives.

## Method and experimental setup

Probabilistic analysis plus HumanEval and MBPP experiments estimate generator accuracy, verifier errors, and utility under repeated sampling.

## Main findings

- More samples create more true positives and more false positives; with realistic negative utility for false acceptance, the optimum can be fewer than ten samples.
- Generator correctness and test-suite false-positive rates are strongly correlated in the reported code tasks.

## Mathematical content

Selection utility is derived from generator and verifier joint probabilities rather than 1-(1-p)^k alone; optimal k depends on false-positive cost.

## Evidence quality and limitations

Applies to verifier-selected resampling, not every adaptive refinement method; empirical tasks and test suites are limited.

## Important implementation details

Estimate the joint generator-verifier confusion process, set an explicit false-positive utility, and stop when marginal expected utility is nonpositive.

## Claims this source supports

Inference scaling has a finite or negative-value region when verification is imperfect.

## Claims this source weakens or contradicts

The claim that more samples monotonically improve useful capability.

## Relevance to a mathematics paper

Provides the central decision-theoretic correction to oracle pass@k.

## Connections to other sources

See the category and claim-level cross-references in [`INDEX.md`](INDEX.md) and the synthesis documents.

## Verification notes

Core probability model, optimal-sample examples, HumanEval/MBPP error correlations, utility assumptions, and limitations checked in the local PDF. The archived file parsed successfully: 33 pages, 86854 extractable characters, SHA-256 `b0f844bc5223bd39231e316b05db251e77dd9b92cdc2bd124b84a9fdafdbc200`.
