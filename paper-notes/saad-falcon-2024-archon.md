---
title: "Archon: An Architecture Search Framework for Inference-Time Techniques"
authors: ["Jon Saad-Falcon", "Adrian Gamarra Lafuente", "Shlok Natarajan", "Nahum Maru", "Hristo Todorov", "Etash Guha", "E. Kelly Buchanan", "Mayee Chen", "Neel Guha", "Christopher Ré", "Azalia Mirhoseini"]
year: 2024
venue: "ICML-2025"
source_type: "peer-reviewed"
paper_url: "https://arxiv.org/abs/2409.15254"
pdf_path: "papers/academic/saad-falcon-2024-archon.pdf"
accessed: "2026-09-04"
review_status: "skimmed"
evidence_confidence: "medium"
---

# saad-falcon-2024-archon — Archon: An Architecture Search Framework for Inference-Time Techniques

## Why this source is in the corpus

Directly studies reusable harness components, outer-loop optimization, self-modification, or the statistical controls needed to decide whether an update is a real improvement.

## Research question

Can inference-time architectures that combine several models and critique/ranking layers be optimized automatically under quality and cost budgets?

## Harness mechanism studied

Archon composes generation, ranking, critique, verification, and fusion layers with model assignments, then uses Bayesian optimization to search architecture and budget choices.

## Method and experimental setup

The study evaluates many candidate Archon configurations across instruction-following and reasoning benchmarks, constructs quality-cost Pareto fronts, and compares optimized systems with frontier single-model calls.

## Main findings

- The abstract reports an average +15.1% over models including o1, GPT-4o, and Claude 3.5 in the authors’ evaluation and presents Pareto-efficient quality/cost configurations.
- The aggregate combines different tasks, model pools, and call counts; optimization is offline and benchmark-specific, so it does not identify a portable architecture effect or show that gains persist after total search cost is charged.

## Mathematical content

Bayesian optimization models utility f(a) over discrete layered architectures a and selects evaluations with an acquisition function subject to token, latency, or dollar budgets; no global optimum or generalization guarantee is supplied.

## Evidence quality and limitations

Multiple proprietary model backbones and extra samples confound harness versus model effects, benchmark-specific offline search can overfit, aggregate improvement is hard to interpret, and reproducibility depends on changing APIs.

## Important implementation details

Enumerate allowed layer types and model pools, evaluate initial architectures, fit a surrogate, propose budget-feasible layer/model combinations, retain the quality-cost Pareto set, and deploy a selected stack.

## Claims this source supports

Model routing and critic/fusion structure can be optimized as harness variables with explicit budget constraints.

## Claims this source weakens or contradicts

A multi-model ensemble’s gain is not proof that the orchestration is intrinsically better than equal-cost sampling, and benchmark-specific selection may not transfer.

## Relevance to a mathematics paper

A concrete constrained Bayesian-optimization and Pareto-front formulation for inference-time harness design.

## Connections to other sources

See the category and claim-level cross-references in [`INDEX.md`](INDEX.md) and the synthesis documents.

## Verification notes

Local PDF abstract, architecture/search description, main performance tables, Pareto analyses, budget studies, and limitations were checked; the +15.1% is source-reported, not independently pooled. The archived file parsed successfully: 35 pages, 126341 extractable characters, SHA-256 `7531f7bd335276b326b0230d0cc000ef022251079330a7f7c2e278defad7f3ef`.
