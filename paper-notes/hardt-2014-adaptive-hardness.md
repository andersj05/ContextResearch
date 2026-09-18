---
title: "Preventing False Discovery in Interactive Data Analysis Is Hard"
authors: ["Moritz Hardt", "Jonathan Ullman"]
year: 2014
venue: "FOCS-2014"
source_type: "peer-reviewed"
paper_url: "https://arxiv.org/abs/1408.1655"
pdf_path: "papers/academic/hardt-2014-adaptive-hardness.pdf"
accessed: "2026-09-04"
review_status: "skimmed"
evidence_confidence: "high"
---

# hardt-2014-adaptive-hardness — Preventing False Discovery in Interactive Data Analysis Is Hard

## Why this source is in the corpus

Directly studies reusable harness components, outer-loop optimization, self-modification, or the statistical controls needed to decide whether an update is a real improvement.

## Research question

Are there computational limits to answering a very large number of adversarially adaptive statistical queries from one finite sample?

## Harness mechanism studied

An adaptive analyst uses fingerprinting-code-style attacks to reconstruct enough information about the sample to force inaccurate answers; cryptographic assumptions make the attack compatible with computationally bounded oracles.

## Method and experimental setup

Worst-case complexity-theoretic lower bounds for interactive statistical-query answering.

## Main findings

- Assuming one-way functions, no computationally efficient oracle with n samples can accurately answer on the order of n^{3+o(1)} adversarial adaptive statistical queries in the paper's regime.
- The result rules out unlimited efficient reuse in a formal worst case, not a practical numerical limit for benign LLM harness search.

## Mathematical content

The formal game uses bounded statistical queries q:X->[0,1], constant target accuracy and failure probability, an adaptive polynomial-time analyst, and a cryptographic hardness assumption. The lower bound complements mechanisms supporting roughly quadratic query counts in related regimes.

## Evidence quality and limitations

Conditional on cryptography and worst-case adversaries; constants and exponents do not translate directly to benchmark submissions; queries are statistical functions rather than arbitrary stateful code execution; benign analysts may overfit much less.

## Important implementation details

Treat protected-evaluator reuse as a finite resource, rotate or refresh audit tasks, and do not infer safety from an inability to observe current overfitting.

## Claims this source supports

There are principled computational barriers to a universally reusable exact evaluator under adaptivity.

## Claims this source weakens or contradicts

The claim that enough mechanism engineering can make one finite benchmark answer arbitrarily many rich adaptive questions with unchanged validity.

## Relevance to a mathematics paper

Provides a negative boundary that motivates finite feedback budgets, fresh data, and explicit gaps rather than universal reusable-holdout promises.

## Connections to other sources

See the category and claim-level cross-references in [`INDEX.md`](INDEX.md) and the synthesis documents.

## Verification notes

Local PDF theorem statements, fingerprinting reduction overview, computational assumptions, and discussion of the n^{3+o(1)} barrier checked. The archived file parsed successfully: 31 pages, 73311 extractable characters, SHA-256 `308e6e4ff3b5c7668da1ec62b614b5e9034f674050668a6e9c79554c367990d8`.
