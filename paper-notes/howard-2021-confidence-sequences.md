---
title: "Time-uniform, Nonparametric, Nonasymptotic Confidence Sequences"
authors: ["Steven R. Howard", "Aaditya Ramdas", "Jon McAuliffe", "Jasjeet Sekhon"]
year: 2021
venue: "Annals-of-Statistics-2021"
source_type: "peer-reviewed"
paper_url: "https://arxiv.org/abs/1810.08240"
pdf_path: "papers/academic/howard-2021-confidence-sequences.pdf"
accessed: "2026-09-04"
review_status: "skimmed"
evidence_confidence: "high"
---

# howard-2021-confidence-sequences — Time-uniform, Nonparametric, Nonasymptotic Confidence Sequences

## Why this source is in the corpus

Directly studies reusable harness components, outer-loop optimization, self-modification, or the statistical controls needed to decide whether an update is a real improvement.

## Research question

How can uncertainty be quantified uniformly over time so that monitoring and optional stopping remain valid?

## Harness mechanism studied

Nonnegative supermartingales, Ville's inequality, stitching, and mixture boundaries produce confidence sequences that cover simultaneously at all times.

## Method and experimental setup

General nonparametric, nonasymptotic theory for scalar and matrix adapted processes, with empirical-Bernstein and other concrete boundaries.

## Main findings

- A confidence sequence satisfies simultaneous coverage over an unbounded horizon and therefore remains valid at arbitrary stopping times.
- Stitched and mixture boundaries adapt to intrinsic variance, but their validity is tied to a declared adapted process and sub-psi condition.

## Mathematical content

A confidence sequence obeys P(for all t>=1: theta_t in CI_t)>=1-alpha. If exp{lambda S_t-psi(lambda)V_t} is dominated by a nonnegative supermartingale, a linear uniform boundary is u(v)=log(l_0/alpha)/lambda + psi(lambda)v/lambda; stitching yields curved boundaries of order sqrt[V_t log log V_t] in sub-Gaussian cases.

## Evidence quality and limitations

One confidence sequence does not correct selection among an adaptively expanded family; dependence and conditional-mgf assumptions must hold; unbounded or heavy-tailed losses need different constructions; boundaries can be conservative early.

## Important implementation details

For a prespecified incumbent-candidate paired-loss stream, maintain an anytime upper confidence bound on the mean difference and promote only when it is below a negative margin; allocate alpha across candidates or use a joint supermartingale.

## Claims this source supports

Harness trials may stop when evidence is sufficient without invalidating a fixed-horizon interval, provided the sequential process was specified correctly.

## Claims this source weakens or contradicts

Repeated peeking at ordinary fixed-n confidence intervals or p-values and stopping at the first favorable result.

## Relevance to a mathematics paper

Provides the optional-stopping-safe statistical gate needed for cost-aware sequential harness evaluation.

## Connections to other sources

See the category and claim-level cross-references in [`INDEX.md`](INDEX.md) and the synthesis documents.

## Verification notes

Local PDF Definition 1 and sub-psi construction on pp. 4-5, Lemma 1 on p. 6, stitched Theorem 1 on pp. 7-8, and confidence-sequence definition in Section 1 checked. The archived file parsed successfully: 48 pages, 154164 extractable characters, SHA-256 `eb3efd547349adfbff25514ae0854c142cd29b96b398be38c9000d69a2f64ca8`.
