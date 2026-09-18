---
title: "Optimal Search for the Best Alternative"
authors: ["Martin L. Weitzman"]
year: 1979
venue: "Econometrica-1979"
source_type: "peer-reviewed"
paper_url: "https://doi.org/10.2307/1910412"
pdf_path: "papers/academic/weitzman-1979-optimal-search.pdf"
accessed: "2026-09-04"
review_status: "skimmed"
evidence_confidence: "high"
---

# weitzman-1979-optimal-search — Optimal Search for the Best Alternative

## Why this source is in the corpus

Directly studies reusable harness components, outer-loop optimization, self-modification, or the statistical controls needed to decide whether an update is a real improvement.

## Research question

How should a decision maker order costly inspections of alternatives and decide when to stop searching?

## Harness mechanism studied

Each unopened box receives a reservation value balancing inspection cost against expected upside; search opens the highest-index box until the incumbent reward dominates all remaining indices.

## Method and experimental setup

Bayesian optimal-stopping analysis for independent alternatives with known reward distributions and inspection costs.

## Main findings

- Pandora's rule is optimal under its model: inspect in decreasing reservation value and stop when the best observed reward exceeds every unopened reservation value.
- The rule is not proved for correlated, endogenously generated harness candidates or learned value distributions.

## Mathematical content

For an undiscounted box i, reservation z_i solves c_i=E[(X_i-z_i)^+]. Independence, known distributions, fixed costs, recall of observed rewards, and the paper's expected net-reward objective are essential assumptions.

## Evidence quality and limitations

LLM-generated candidates share ancestry and evaluation information; distributions and costs are estimated and nonstationary; parallel evaluation and complementarities violate the box model; misspecified tails can badly rank indices.

## Important implementation details

Estimate cost and reward distributions for a fixed candidate pool, use reservation values as an auditable heuristic, and switch to a correlated-search or bandit analysis when outcomes share information.

## Claims this source supports

Cost-aware candidate evaluation should compare expected value of information with marginal evaluation cost and include an explicit stopping rule.

## Claims this source weakens or contradicts

The claim that always evaluate the most promising patch or exhaust a fixed retry budget is generally optimal, and the converse claim that Pandora's optimality transfers unchanged to agent search.

## Relevance to a mathematics paper

Provides a normative baseline for value-of-information scheduling and exposes exactly which dependence assumptions need new theory.

## Connections to other sources

See the category and claim-level cross-references in [`INDEX.md`](INDEX.md) and the synthesis documents.

## Verification notes

Local PDF theorem and reservation-value construction in the main model, ordering rule, stopping condition, and independence discussion checked. The archived file parsed successfully: 36 pages, 27274 extractable characters, SHA-256 `cdb601370aaba1972afd7677c72b0cec2bb0fbf3b21fd0ac534286b11a4ff518`.
