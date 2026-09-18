---
title: "Adaptive Auto-Harness: Sustained Self-Improvement for Agentic System Deployment on Open-Ended Task Streams"
authors: ["Zewen Liu", "Zhan Shi", "Yisi Sang", "Bing He", "Minhua Lin", "Tianxin Wei", "Dakuo Wang", "Benoit Dumoulin", "Wei Jin", "Hanqing Lu"]
year: 2026
venue: "preprint"
source_type: "preprint"
paper_url: "https://arxiv.org/abs/2606.01770"
pdf_path: "papers/academic/liu-2026-adaptive-auto-harness.pdf"
accessed: "2026-09-04"
review_status: "skimmed"
evidence_confidence: "medium"
---

# liu-2026-adaptive-auto-harness — Adaptive Auto-Harness: Sustained Self-Improvement for Agentic System Deployment on Open-Ended Task Streams

## Why this source is in the corpus

Directly studies reusable harness components, outer-loop optimization, self-modification, or the statistical controls needed to decide whether an update is a real improvement.

## Research question

Can a meta-harness synthesize and evolve a task-specific hierarchy of analyst, researchers, builder, and verifier while routing retrieval by problem needs?

## Harness mechanism studied

A fixed outer controller grows a harness tree, routes evidence retrieval across resource tiers, and optionally uses verifier or human feedback to revise generated roles and procedures.

## Method and experimental setup

The paper compares no-evolution, MetaHarness, multi-agent, adaptive, and full variants on PolyBench, CTF, and FutureX, with retrieval-tier and component ablations.

## Main findings

- PolyBench Table 2 reports no-evolve 22.2, MetaHarness 50.8, multi-agent 79.8, adaptive 77.4, and full 80.9; CTF full is 50.2 versus A-Evolve 45.2.
- On FutureX, multi-agent 49.5 exceeds full 47.3, while richer retrieval tiers move 34.0→47.6→57.1 in a separate comparison, so evidence access and team structure can matter more than evolutionary revision.

## Mathematical content

The controller searches a harness tree under empirical benchmark reward, with routing as a conditional policy; no formal regret, safe-improvement, or attribution theorem separates retrieval from adaptation.

## Evidence quality and limitations

2026 preprint; mixed and externally changing resources, multi-agent variant sometimes beats full evolution, different evidence tiers confound architecture, and no sealed future-time evaluation or full cost normalization is shown.

## Important implementation details

Run an analyst, spawn parallel researchers with routed sources, synthesize a builder plan, verify outputs, update a tree of role/prompt configurations from feedback, and optionally request a human gate.

## Claims this source supports

Task-conditioned hierarchy and verification can yield large gains over a non-evolving baseline in research-heavy environments.

## Claims this source weakens or contradicts

Contradicts a universal evolution benefit: the simpler multi-agent system wins one benchmark and retrieval depth independently explains large changes.

## Relevance to a mathematics paper

Calls for factorial decomposition of architecture, retrieval, verifier, and update effects rather than a single full-minus-base contrast.

## Connections to other sources

See the category and claim-level cross-references in [`INDEX.md`](INDEX.md) and the synthesis documents.

## Verification notes

Local PDF architecture, Table 2 and CTF/FutureX tables, retrieval-tier and component ablations, and limitations were checked; no rerun was performed. The archived file parsed successfully: 23 pages, 81540 extractable characters, SHA-256 `50454c1eec069b668b515c6d322e4c5ac55f24655298b3381f91f461a9c39b3e`.
