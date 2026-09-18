---
title: "HiAgent: Hierarchical Working Memory Management for Solving Long-Horizon Agent Tasks with Large Language Model"
authors: ["Mengkang Hu", "Tianxing Chen", "Qiguang Chen", "Yao Mu", "Wenqi Shao", "Ping Luo"]
year: 2025
venue: "ACL-2025"
source_type: "peer-reviewed"
paper_url: "https://arxiv.org/abs/2408.09559"
pdf_path: "papers/academic/hu-2025-hiagent.pdf"
accessed: "2026-09-04"
review_status: "fully-reviewed"
evidence_confidence: "medium"
---

# hu-2025-hiagent — HiAgent: Hierarchical Working Memory Management for Solving Long-Horizon Agent Tasks with Large Language Model

## Why this source is in the corpus

Provides mechanisms and failure modes for state, retrieval, summarization, and bounded context.

## Research question

Can hierarchical working-memory summaries preserve progress on long-horizon tasks while reducing tokens?

## Harness mechanism studied

Observation summarization and trajectory retrieval organize within-trial history into hierarchical subgoals and compressed evidence.

## Method and experimental setup

Five long-horizon agent tasks compare a standard message history with HiAgent, component ablations, and task-decomposition baselines.

## Main findings

- Average success rises from 21% to 42% and progress from 38.61 to 62.55.
- Context tokens fall 35.02% and runtime 19.42%; per-task effects vary and one progress metric falls by 1.5 points.

## Mathematical content

Working memory is a hierarchy over trajectory segments; statistical tests assess reported improvements but no information-retention bound is given.

## Evidence quality and limitations

Only five tasks, model and summarizer dependence, aggregate averages hide heterogeneous cells, and summary faithfulness is not independently audited.

## Important implementation details

Retain raw trajectory references behind summaries, retrieve by active subgoal, and report both efficiency and lost-detail errors.

## Claims this source supports

Structured within-run memory can improve long-horizon efficiency.

## Claims this source weakens or contradicts

Compression as uniformly lossless or every task benefiting equally.

## Relevance to a mathematics paper

Supports hierarchical state abstraction with information-loss and cost tradeoffs.

## Connections to other sources

See the category and claim-level cross-references in [`INDEX.md`](INDEX.md) and the synthesis documents.

## Verification notes

Table 1, Table 2 ablations, Table 3 decomposition comparison, significance analysis, and limitations checked in the local PDF. The archived file parsed successfully: 17 pages, 78892 extractable characters, SHA-256 `5e907a1013077f79041640294229f702c91a3b23673bed9649fb1bc773a4e25b`.
