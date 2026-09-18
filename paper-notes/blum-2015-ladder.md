---
title: "The Ladder: A Reliable Leaderboard for Machine Learning Competitions"
authors: ["Avrim Blum", "Moritz Hardt"]
year: 2015
venue: "ICML-2015"
source_type: "peer-reviewed"
paper_url: "https://arxiv.org/abs/1502.04585"
pdf_path: "papers/academic/blum-2015-ladder.pdf"
accessed: "2026-09-04"
review_status: "skimmed"
evidence_confidence: "high"
---

# blum-2015-ladder — The Ladder: A Reliable Leaderboard for Machine Learning Competitions

## Why this source is in the corpus

Directly studies reusable harness components, outer-loop optimization, self-modification, or the statistical controls needed to decide whether an update is a real improvement.

## Research question

Can a public leaderboard report useful progress to an adaptive sequence of submissions without rapidly overfitting the holdout?

## Harness mechanism studied

The Ladder reports a rounded score only when a submission beats the running best by a step eta, thereby bounding the depth and description length of the adaptive transcript.

## Method and experimental setup

Theoretical leaderboard analysis for iid samples and bounded loss, adversarial-attack analysis, and experiments on Kaggle submission files.

## Main findings

- The Ladder controls error of the reported running best for fully adaptive submissions.
- With a tuned eta its leaderboard error is O((log(kn)/n)^(1/3)), but it does not provide valid estimates for every submitted candidate.

## Mathematical content

Theorem 3.1 states P(|min_{i<=t} R_D(f_i)-R_t| > epsilon+eta) <= exp[-2 epsilon^2 n + (1/eta+2)log(4t/eta)+1] for t<=k, iid sample size n, and loss in [0,1]. The proof encodes the adaptive tree and applies Hoeffding plus a union bound.

## Evidence quality and limitations

The cube-root rate is weaker than fresh fixed-candidate estimation; the guarantee targets only the best-so-far scalar score; rich diagnostics, patches, traces, or exact per-task feedback can leak much more; later randomized mechanisms can improve rates.

## Important implementation details

Publish only material rounded improvements, retain the incumbent score otherwise, predeclare eta, and do not expose per-instance failures from the protected set.

## Claims this source supports

A promotion leaderboard can provide sparse improvement feedback with an explicit adaptive-validity guarantee.

## Claims this source weakens or contradicts

The practice of returning exact full diagnostics for every harness attempt while treating the board as statistically untouched.

## Relevance to a mathematics paper

Provides a finite-sample bridge from transcript compression to an adaptive leaderboard error bound.

## Connections to other sources

See the category and claim-level cross-references in [`INDEX.md`](INDEX.md) and the synthesis documents.

## Verification notes

Local PDF pp. 3-7, bounded-loss setup, Algorithm Ladder, Theorem 3.1, Claim 3.2, and proof checked. The archived file parsed successfully: 16 pages, 40543 extractable characters, SHA-256 `957ef4739df371a0a778360f0db4252a62f7c85abcd8343f581cd6250b1d31fe`.
