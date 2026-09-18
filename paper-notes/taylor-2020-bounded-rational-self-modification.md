---
title: "Performance of Bounded-Rational Agents With the Ability to Self-Modify"
authors: ["Jakub Tětek", "Marek Sklenka", "Tomáš Gavenčiak"]
year: 2020
venue: "AAAI-2021"
source_type: "peer-reviewed"
paper_url: "https://arxiv.org/abs/2011.06275"
pdf_path: "papers/academic/taylor-2020-bounded-rational-self-modification.pdf"
accessed: "2026-09-04"
review_status: "skimmed"
evidence_confidence: "high"
---

# taylor-2020-bounded-rational-self-modification — Performance of Bounded-Rational Agents With the Ability to Self-Modify

## Why this source is in the corpus

Directly studies reusable harness components, outer-loop optimization, self-modification, or the statistical controls needed to decide whether an update is a real improvement.

## Research question

Does the harmless-self-modification result survive bounded optimization, utility error, belief error, or discount error?

## Harness mechanism studied

The Everitt-style self-modification model is perturbed by bounded optimization or bounded knowledge errors, and worst-case value loss is tracked over time.

## Method and experimental setup

Worst-case upper bounds with matching lower constructions up to constants for four bounded-rationality models in an infinite discounted setting.

## Main findings

- A self-modifying epsilon-optimizer can suffer value loss growing exponentially with time until it reaches the total discounted-value ceiling.
- Bounded utility, belief, or discount misspecification alone does not compound in the same way when optimization remains perfect, though each causes bounded loss.

## Mathematical content

Theorem 7 gives the worst-case scale f_opt^t(epsilon,gamma)=min{epsilon/gamma^{t-1},1/(1-gamma)} up to the paper's matching-constant lower bound. Other reported scales include f_util=2epsilon/(1-gamma); assumptions include instantaneous utility in [0,1], exponential discount gamma, modification independence, a dualistic agent, unlimited self-modification, and worst-case analysis.

## Evidence quality and limitations

The error model is a uniform bound rather than a realistic distribution; unlimited self-modification and infinite discounted horizons are stylized; results are worst case and do not predict typical LLM behavior; no corrigibility mechanism is modeled.

## Important implementation details

Measure per-update optimization error, limit edit scope and horizon, retain external rollback, and test whether small local mistakes compound across generations rather than assuming rational invariance.

## Claims this source supports

Bounded search can turn individually small decision errors into large long-run self-modification loss.

## Claims this source weakens or contradicts

The claim that the perfect-rationality invariance theorem degrades smoothly or negligibly when an agent is only approximately optimal.

## Relevance to a mathematics paper

Provides an explicit time-horizon growth law and a countermodel for any monotone self-improvement theorem lacking an exact promotion gate.

## Connections to other sources

See the category and claim-level cross-references in [`INDEX.md`](INDEX.md) and the synthesis documents.

## Verification notes

Local PDF abstract and Sections 1.1-2, Theorem 7 summary and assumptions, plus bounded-knowledge results in Sections 5.2-5.3 checked. The archived file parsed successfully: 20 pages, 66910 extractable characters, SHA-256 `496165baae99f4b68d8b66da46376454a918101cc840dbf1ecb76a28a8e04b2c`.
