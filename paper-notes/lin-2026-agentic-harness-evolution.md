---
title: "Agentic Harness Engineering: Observability-Driven Automatic Evolution of Coding-Agent Harnesses"
authors: ["Jiahang Lin", "Shichun Liu", "Chengjun Pan", "Lizhi Lin", "Shihan Dou", "Zhiheng Xi", "Xuanjing Huang", "Hang Yan", "Zhenhua Han", "Tao Gui", "Yu-Gang Jiang"]
year: 2026
venue: "preprint"
source_type: "preprint"
paper_url: "https://arxiv.org/abs/2604.25850"
pdf_path: "papers/academic/lin-2026-agentic-harness-evolution.pdf"
accessed: "2026-09-04"
review_status: "skimmed"
evidence_confidence: "medium"
---

# lin-2026-agentic-harness-evolution — Agentic Harness Engineering: Observability-Driven Automatic Evolution of Coding-Agent Harnesses

## Why this source is in the corpus

Directly treats the harness, its optimization, or its runtime semantics as the object of study.

## Research question

Can execution traces support automatic and attributable evolution of coding-agent harnesses?

## Harness mechanism studied

A closed loop with component, experience, and decision observability; proposed edits are reversible and paired with falsifiable predictions.

## Method and experimental setup

An evolving agent edits file-level harness components using distilled trajectory evidence and evaluates subsequent task outcomes.

## Main findings

- The work argues that layered trace distillation makes a heterogeneous harness action space tractable.
- Decision records connect each change to an expected effect, improving attribution compared with blind score hill-climbing.

## Mathematical content

Outer-loop optimization can be written as sequential noisy black-box search over harness code with logged hypotheses; no general convergence guarantee is established.

## Evidence quality and limitations

Recent preprint; multiple observability mechanisms move together; benchmark search can overfit and detailed external replication is absent.

## Important implementation details

Represent every editable component as versioned code, retain drill-down evidence, and accept changes only with measured validation.

## Claims this source supports

Observability can turn harness changes into auditable experiments.

## Claims this source weakens or contradicts

A rising optimization score as proof of general harness improvement.

## Relevance to a mathematics paper

Provides a sequential-experimental-design framing with noisy rewards and versioned interventions.

## Connections to other sources

See the category and claim-level cross-references in [`INDEX.md`](INDEX.md) and the synthesis documents.

## Verification notes

Abstract, three observability pillars, optimization loop, evaluation sections, and limitations checked in the local PDF. The archived file parsed successfully: 35 pages, 128412 extractable characters, SHA-256 `299f2633b4c13db7bed52434b4db7c48ea621993581014d30e7bcd036d3464df`.
