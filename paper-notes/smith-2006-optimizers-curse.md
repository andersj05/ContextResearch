---
title: "The Optimizer's Curse: Skepticism and Postdecision Surprise in Decision Analysis"
authors: ["James E. Smith", "Robert L. Winkler"]
year: 2006
venue: "Management-Science-2006"
source_type: "peer-reviewed"
paper_url: "https://doi.org/10.1287/mnsc.1050.0451"
pdf_path: "papers/academic/smith-2006-optimizers-curse.pdf"
accessed: "2026-09-04"
review_status: "skimmed"
evidence_confidence: "high"
---

# smith-2006-optimizers-curse — The Optimizer's Curse: Skepticism and Postdecision Surprise in Decision Analysis

## Why this source is in the corpus

Directly studies reusable harness components, outer-loop optimization, self-modification, or the statistical controls needed to decide whether an update is a real improvement.

## Research question

Why is the estimated value of the selected best alternative systematically too optimistic even when each estimate is unbiased?

## Harness mechanism studied

Taking an argmax over noisy estimates selects both signal and favorable estimation error; Bayesian shrinkage is proposed as disciplined post-selection skepticism.

## Method and experimental setup

General proposition under conditional unbiasedness, illustrative analytic examples, and decision-analysis simulations.

## Main findings

- The selected estimate weakly overstates the selected alternative's true value in expectation; the inequality is strict whenever a wrong alternative can be selected.
- Dependence changes magnitude but not the proposition's sign under its assumptions.

## Mathematical content

If E[V_i | mu_1,...,mu_n]=mu_i and i*=argmax_i V_i, Proposition 1 gives E[mu_{i*}-V_{i*}]<=0, strictly below zero if misselection has positive probability. No independence or Gaussian assumption is required for the sign.

## Evidence quality and limitations

The theorem gives no universal magnitude; conditional unbiasedness can fail; true values and evaluation noise may drift; Bayesian correction depends on a credible prior and likelihood.

## Important implementation details

Report post-selection uncertainty, use a fresh gate or hierarchical shrinkage for the promoted harness, and model correlation rather than multiplying an iid winner's-curse formula.

## Claims this source supports

Best-of-many evaluator gains require correction even when every fixed candidate score is unbiased.

## Claims this source weakens or contradicts

The claim that unbiased benchmark scores remain unbiased after selecting their maximum, while also weakening the overclaim that all selection optimism has the same size.

## Relevance to a mathematics paper

Supplies the minimal sign theorem for evaluator overoptimization and distinguishes it from stronger distribution-specific bounds.

## Connections to other sources

See the category and claim-level cross-references in [`INDEX.md`](INDEX.md) and the synthesis documents.

## Verification notes

Local PDF pp. 1-4, conditional-unbiasedness setup and Proposition 1; dependence examples and Bayesian remedies checked. The archived file parsed successfully: 12 pages, 60244 extractable characters, SHA-256 `c5e9b6e38f9eae8959114fbdc56399cf6747ff1c4820305f7e311b12e4b35f7e`.
