---
title: "Non-stochastic Best Arm Identification and Hyperparameter Optimization"
authors: ["Kevin Jamieson", "Ameet Talwalkar"]
year: 2016
venue: "AISTATS-2016"
source_type: "peer-reviewed"
paper_url: "https://arxiv.org/abs/1502.07943"
pdf_path: "papers/academic/jamieson-2016-successive-halving.pdf"
accessed: "2026-09-04"
review_status: "skimmed"
evidence_confidence: "high"
---

# jamieson-2016-successive-halving — Non-stochastic Best Arm Identification and Hyperparameter Optimization

## Why this source is in the corpus

Directly studies reusable harness components, outer-loop optimization, self-modification, or the statistical controls needed to decide whether an update is a real improvement.

## Research question

How should a fixed evaluation budget be allocated among candidates whose observed losses converge nonstochastically toward final values?

## Harness mechanism studied

Successive Halving evaluates all surviving arms at increasing budgets and repeatedly eliminates the worse half; a doubling wrapper removes the need to know the sufficient budget.

## Method and experimental setup

Deterministic best-arm-identification theory for fixed arms with arbitrary, possibly nonmonotone, convergent loss sequences, plus hyperparameter-optimization examples.

## Main findings

- Successive Halving returns the best fixed arm once budget exceeds a gap-and-convergence threshold.
- Early elimination is justified only when each candidate has a valid convergence envelope; adaptive candidate invention is outside the theorem.

## Mathematical content

Let nu_i=lim_t l_{i,t}, nu_1<nu_2<=...<=nu_n, gamma_bar(t)=max_i gamma_i(t), and gamma_bar^{-1}(a)=min{t:gamma_bar(t)<=a}. Theorem 1 requires B>z_SH=2ceil(log_2 n) max_{2<=i<=n} i[1+gamma_bar^{-1}((nu_i-nu_1)/2)]; doubling uses at most a constant-factor overhead.

## Evidence quality and limitations

Candidates must be fixed, final losses must exist, and useful envelopes are usually unknown; rank reversals can eliminate the best arm; shared caches, correlated candidates, and adaptive generation are not represented.

## Important implementation details

Use for a frozen batch of harness candidates, define fidelity as tasks or rollout budget, audit ranking stability, and keep a final full-budget reevaluation of survivors.

## Claims this source supports

Multi-fidelity evaluation can reduce candidate-search cost when early scores have a defensible relation to final loss.

## Claims this source weakens or contradicts

The claim that low-budget benchmark performance safely eliminates arbitrary evolving agent designs.

## Relevance to a mathematics paper

Provides a sufficient cost threshold in terms of candidate gaps and convergence speed, enabling power and budget calculations.

## Connections to other sources

See the category and claim-level cross-references in [`INDEX.md`](INDEX.md) and the synthesis documents.

## Verification notes

Local PDF Section 3.1, Theorem 1 and z_SH on pp. 3-4, doubling guarantee, and anytime fallback discussion checked. The archived file parsed successfully: 13 pages, 46948 extractable characters, SHA-256 `52133bcd5f21b68964983cf77d15d51f10fc62fa67a22b5a2a8af4bbc82a91fa`.
