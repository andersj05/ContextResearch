---
title: "Harness Engineering: Anatomy, Architecture, and Evolution of Coding Agents -- A Source-Code Study of Eleven Systems"
authors: ["Paul Barbaste", "Tristan Darrigol", "Germain Vu", "Tom Wiltberger"]
year: 2026
venue: "preprint"
source_type: "preprint"
paper_url: "https://arxiv.org/abs/2609.00006"
pdf_path: "papers/academic/barbaste-2026-harness-anatomy.pdf"
accessed: "2026-09-04"
review_status: "skimmed"
evidence_confidence: "high"
---

# barbaste-2026-harness-anatomy — Harness Engineering: Anatomy, Architecture, and Evolution of Coding Agents -- A Source-Code Study of Eleven Systems

## Why this source is in the corpus

Directly treats the harness, its optimization, or its runtime semantics as the object of study.

## Research question

What do production coding-agent harnesses actually implement in source code?

## Harness mechanism studied

Seven canonical subsystems covering loop, tools, context, safety, orchestration, persistence, and extension surfaces.

## Method and experimental setup

Source-code anatomy of eleven production coding harnesses plus one meta-harness contrast; it describes and compares rather than ranks them.

## Main findings

- The systems share a small model-action-observation core but diverge substantially in state ownership, context policy, recovery, and safety.
- Thirteen cross-cutting patterns show that product labels hide materially different runtime semantics.

## Mathematical content

The paper gives structural decompositions and state-machine intuition but no performance theorem or causal estimator.

## Evidence quality and limitations

All systems are moving targets; the sample favors coding agents; absence of benchmarking means prevalence is not effectiveness.

## Important implementation details

Pin repository commit, provider layer, loop semantics, state store, tool protocol, and containment policy when citing any system.

## Claims this source supports

Harnesses are independently specifiable software systems whose mechanisms can be compared.

## Claims this source weakens or contradicts

Framework names alone as adequate experimental treatment labels.

## Relevance to a mathematics paper

Its subsystem coding supports a categorical design matrix for later factorial studies.

## Connections to other sources

See the category and claim-level cross-references in [`INDEX.md`](INDEX.md) and the synthesis documents.

## Verification notes

Abstract, sampling protocol, subsystem anatomy, cross-system tables, and conclusion checked in the local PDF. The archived file parsed successfully: 83 pages, 278048 extractable characters, SHA-256 `e81b5a4855adda8cc5e46db0a05cd69e0d0d542bd49cec6b157c17e6001395d7`.
