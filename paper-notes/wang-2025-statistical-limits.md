---
title: "On the Statistical Limits of Self-Improving Agents"
authors: ["Charles L. Wang", "Keir Dorchen", "Peter Jin"]
year: 2025
venue: "preprint"
source_type: "preprint"
paper_url: "https://arxiv.org/abs/2510.04399"
pdf_path: "papers/academic/wang-2025-statistical-limits.pdf"
accessed: "2026-09-04"
review_status: "skimmed"
evidence_confidence: "medium"
---

# wang-2025-statistical-limits — On the Statistical Limits of Self-Improving Agents

## Why this source is in the corpus

Directly studies reusable harness components, outer-loop optimization, self-modification, or the statistical controls needed to decide whether an update is a real improvement.

## Research question

When is the family of predictors reachable by a self-improving agent distribution-free learnable, and how can accepted edits be made monotone?

## Harness mechanism studied

The analysis treats all policy-reachable hypotheses as one envelope; a capacity gate confines candidates to a fixed VC-bounded family and an independent validation gate requires a margin above uniform error.

## Method and experimental setup

Formal PAC and VC analysis of representational, architectural, metacognitive, and algorithmic self-modification; the key finite-sample result is a two-gate construction.

## Main findings

- Under the paper's assumptions, the reachable envelope is distribution-free PAC learnable iff it has finite VC dimension.
- If both incumbent and candidate stay in a fixed capped envelope and validation improves by 2epsilon_V+tau, every accepted edit lowers true risk by at least tau; capacity of each individual architecture is insufficient unless the union is bounded.

## Mathematical content

Theorem 1 gives the finite-VC boundary for G_reach. Theorem 2 and Corollary 5 use sup_{h in G_K}|R(h)-Rhat_V(h)|<=epsilon_V and accept when Rhat_V(h_new)<=Rhat_V(h_old)-(2epsilon_V+tau), yielding R(h_new)<=R(h_old)-tau and terminal excess risk O_tilde(sqrt[(K(m)+log(1/delta))/m]). Assumptions include iid fixed D, independent train and validation sets, bounded 0-1 loss, an ex-ante envelope, and gate integrity.

## Evidence quality and limitations

The core proof is standard uniform convergence applied to a union; defining a nonvacuous computable capacity proxy for real harness programs is unresolved; expanding or tuning the envelope on validation breaks the argument; distribution shift and evaluator misspecification remain; publication metadata currently conflict.

## Important implementation details

Make the reachable class explicit before validation, protect the gate from self-editing, include rejected candidates in the envelope, use a margin above two-sided uniform error, and audit on a locked set.

## Claims this source supports

A modest fixed-capacity self-improvement theorem can guarantee monotone population risk for accepted edits.

## Claims this source weakens or contradicts

The claim that an open-ended generator inherits the guarantee, that pointwise component capacity bounds the reachable union, or that a validation margin protects a mutable gate.

## Relevance to a mathematics paper

Provides the closest literature theorem to a fixed-class context-compiler promotion rule and identifies the remaining mathematical gap as capacity certification.

## Connections to other sources

See the category and claim-level cross-references in [`INDEX.md`](INDEX.md) and the synthesis documents.

## Verification notes

Local PDF Theorem 1 on pp. 7-9, Theorem 2 and Corollary 5 on pp. 7-10, gate-integrity discussion, and full proof on pp. 20-23 checked; PDF says TMLR 08/2026 while catalog status is preprint. The archived file parsed successfully: 27 pages, 78216 extractable characters, SHA-256 `4beb5268e1411213179662d4f0139df6ce3558e9015b790e2da2c33f03de4874`.
