---
title: "Scaling Large-Language-Model-based Multi-Agent Collaboration"
authors: ["Chen Qian", "Zihao Xie", "YiFei Wang", "Wei Liu", "Kunlun Zhu", "Hanchen Xia", "Yufan Dang", "Zhuoyun Du", "Weize Chen", "Cheng Yang", "Zhiyuan Liu", "Maosong Sun"]
year: 2024
venue: "preprint"
source_type: "preprint"
paper_url: "https://arxiv.org/abs/2406.07155"
pdf_path: "papers/academic/qian-2024-scaling-collaboration.pdf"
accessed: "2026-09-04"
review_status: "skimmed"
evidence_confidence: "medium"
---

# qian-2024-scaling-collaboration — Scaling Large-Language-Model-based Multi-Agent Collaboration

## Why this source is in the corpus

Provides communication, aggregation, or coordination mechanisms and their compute-matched counterevidence.

## Research question

How do agent count and communication topology affect a large collaboration network?

## Harness mechanism studied

MACNET organizes agents in directed acyclic graphs with chain, tree, mesh, layered, and irregular communication patterns.

## Method and experimental setup

Reasoning and generation benchmarks scale topology depth up to more than one thousand agent instances and fit a logistic performance curve.

## Main findings

- Performance rises and then saturates with scale in the reported settings; irregular topologies can outperform regular ones.
- Removing agent profiles drops average performance 3.67%, while random topologies use about 51.92% less time than mesh in one analysis.

## Mathematical content

A logistic curve is fit to performance versus agent count; graph topology controls dependency and communication cost, but the fit is empirical.

## Evidence quality and limitations

Enormous unmatched compute, correlated LLM calls, hand-selected topologies and roles, few tasks, and no evidence that the fitted law transfers.

## Important implementation details

Report graph, edge count, critical path, calls, tokens, wall time, and a single-agent or vote baseline at equal budget.

## Claims this source supports

Topology and saturation matter in multi-agent scaling.

## Claims this source weakens or contradicts

More than a thousand agents as automatically economical or a universal scaling law.

## Relevance to a mathematics paper

Supports graph, queueing, and saturating-production-function models.

## Connections to other sources

See the category and claim-level cross-references in [`INDEX.md`](INDEX.md) and the synthesis documents.

## Verification notes

Topology tables, thousand-agent scaling Figure 7, logistic fit, profile ablation, timing comparison, and limitations checked in the local PDF. The archived file parsed successfully: 18 pages, 74062 extractable characters, SHA-256 `218988f7944195a66d57383f4089b01151a3babf86e5e13a3d65b146baddda4f`.
