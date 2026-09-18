---
title: "Generalization in Adaptive Data Analysis and Holdout Reuse"
authors: ["Cynthia Dwork", "Vitaly Feldman", "Moritz Hardt", "Toniann Pitassi", "Omer Reingold", "Aaron Roth"]
year: 2015
venue: "NeurIPS-2015"
source_type: "peer-reviewed"
paper_url: "https://arxiv.org/abs/1506.02629"
pdf_path: "papers/academic/dwork-2015-adaptive-holdout.pdf"
accessed: "2026-09-04"
review_status: "skimmed"
evidence_confidence: "high"
---

# dwork-2015-adaptive-holdout — Generalization in Adaptive Data Analysis and Holdout Reuse

## Why this source is in the corpus

Directly studies reusable harness components, outer-loop optimization, self-modification, or the statistical controls needed to decide whether an update is a real improvement.

## Research question

How can a finite holdout be reused adaptively while preserving statistical validity?

## Harness mechanism studied

Thresholdout limits information leakage through differential privacy and noisy threshold feedback; SparseValidate exploits short transcripts; approximate max-information unifies both routes.

## Method and experimental setup

Theoretical analysis for adaptive statistical procedures on iid samples, plus a synthetic demonstration of ordinary holdout overfitting.

## Main findings

- Thresholdout can validate exponentially many queries in n when the number of detected overfitting events is at most quadratic in n under its parameter regime.
- Low-sensitivity private feedback and bounded-description transcripts preserve generalization, but only with explicit privacy, sensitivity, and sampling assumptions.

## Mathematical content

For pure epsilon-DP A and S~P^n, Theorem 20 gives I_inf^beta(S;A(S)) <= log(e)[epsilon^2 n/2 + epsilon sqrt(n ln(2/beta)/2)]. A B-bit transcript induces at most 2^B branches, so a fixed-procedure failure probability beta is at most 2^B beta after a direct union bound.

## Evidence quality and limitations

Results assume iid data and the specified algorithmic channel; statistical-query guarantees require bounded range or sensitivity; privacy noise and threshold budgets reduce feedback utility; arbitrary code-execution benchmarks do not automatically fit the query model.

## Important implementation details

Keep development data open, expose the holdout only through a versioned low-information gate, budget threshold crossings, record the whole feedback transcript, and use fresh audit data for final reporting.

## Claims this source supports

A reusable harness evaluator must control information released to the adaptive generator rather than relying only on secrecy.

## Claims this source weakens or contradicts

The claim that a hidden benchmark remains an independent test set after repeated exact-score feedback.

## Relevance to a mathematics paper

Supplies high-probability adaptive-generalization machinery via max-information and a quantitative feedback-capacity lens.

## Connections to other sources

See the category and claim-level cross-references in [`INDEX.md`](INDEX.md) and the synthesis documents.

## Verification notes

Local PDF full version, Sections 3-4, Theorem 20 on pp. 12-13, and Thresholdout guarantees on pp. 14-18 checked. The archived file parsed successfully: 29 pages, 95496 extractable characters, SHA-256 `dcfbb9aa401c62949123be2d74787c4f9cca48597f18860760ef1580ddb4bc71`.
