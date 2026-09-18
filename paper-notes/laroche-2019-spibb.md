---
title: "Safe Policy Improvement with Baseline Bootstrapping"
authors: ["Romain Laroche", "Paul Trichelair", "Rémi Tachet des Combes"]
year: 2019
venue: "ICML-2019"
source_type: "peer-reviewed"
paper_url: "https://arxiv.org/abs/1712.06924"
pdf_path: "papers/academic/laroche-2019-spibb.pdf"
accessed: "2026-09-04"
review_status: "skimmed"
evidence_confidence: "high"
---

# laroche-2019-spibb — Safe Policy Improvement with Baseline Bootstrapping

## Why this source is in the corpus

Directly studies reusable harness components, outer-loop optimization, self-modification, or the statistical controls needed to decide whether an update is a real improvement.

## Research question

When can an offline reinforcement-learning policy improve on a deployed baseline without unacceptable degradation?

## Harness mechanism studied

SPIBB constrains a candidate policy to copy baseline policy pi_b on state-action pairs with count below N_Lambda and optimizes only in sufficiently covered regions.

## Method and experimental setup

Finite discounted-MDP theory, convergence and safe-improvement proofs, and experiments on random MDPs and a helicopter task.

## Main findings

- Pi_b-SPIBB converges to the constrained optimum in the maximum-likelihood MDP.
- With probability 1-delta, its true return is at least baseline return minus an explicit zeta; this is approximate safety, not guaranteed strict improvement.

## Mathematical content

Theorem 2 gives rho(pi_SPIBB,M*) >= rho(pi_b,M*)-zeta, where zeta = [4V_max/(1-gamma)]sqrt[(2/N_Lambda)log(2|X||A|2^{|X|}/delta)] - rho(pi_SPIBB,M_hat)+rho(pi_b,M_hat). Assumptions include a finite discounted MDP, offline counts, the MLE model, and the baseline constraint set.

## Evidence quality and limitations

The bound can be loose or vacuous and permits zeta degradation; software-agent states and actions are enormous and aliased; logged behavior may not give coverage; side effects and distribution shift violate the finite stationary MDP abstraction.

## Important implementation details

Map only a restricted harness controller to states and actions, retain baseline behavior in low-count regions, choose N_Lambda before evaluation, and report zeta or empirical coverage rather than saying safe without qualification.

## Claims this source supports

Baseline fallback is a principled mechanism for restricting self-changes where evidence is sparse.

## Claims this source weakens or contradicts

The claim that an unconstrained new agent policy is safe because its offline average score is higher.

## Relevance to a mathematics paper

Adds a coverage-dependent alternative to fixed-class validation and clarifies that non-regression guarantees can be one-sided and approximate.

## Connections to other sources

See the category and claim-level cross-references in [`INDEX.md`](INDEX.md) and the synthesis documents.

## Verification notes

Local PDF pp. 2-3, Theorems 1-2 and Equation 35; Appendix A.3 proof and empirical safety discussion checked. The archived file parsed successfully: 34 pages, 105980 extractable characters, SHA-256 `ebb7aa35960e803ff09eeabd0c1a8e53a790994ccff4c0a2e441a5faadaba10f`.
