---
title: "Polar: Agentic RL on Any Harness at Scale"
authors: ["Binfeng Xu", "Hao Zhang", "Shaokun Zhang", "Songyang Han", "Mingjie Liu", "Jian Hu", "Shizhe Diao", "Zhenghui Jin", "Yunheng Zou", "Michael Demoret", "Jan Kautz", "Yi Dong"]
year: 2026
venue: "preprint"
source_type: "preprint"
paper_url: "https://arxiv.org/abs/2605.24220"
pdf_path: "papers/academic/xu-2026-polar.pdf"
accessed: "2026-09-04"
review_status: "skimmed"
evidence_confidence: "medium"
---

# xu-2026-polar — Polar: Agentic RL on Any Harness at Scale

## Why this source is in the corpus

Directly treats the harness, its optimization, or its runtime semantics as the object of study.

## Research question

How can arbitrary existing harnesses produce token-faithful trajectories for asynchronous reinforcement learning?

## Harness mechanism studied

A black-box API proxy records model interactions, reconstructs training trajectories, prewarms runtimes, evaluates rollouts, and decouples trainers from harnesses.

## Method and experimental setup

Systems implementation validated by training agents across existing harnesses under asynchronous RL workloads.

## Main findings

- Polar makes the harness an interchangeable black box while retaining token-level learning signals.
- Decoupled rollout services improve utilization for long-running heterogeneous executions in the reported experiments.

## Mathematical content

Formalizes reconstruction from intercepted calls into trajectories consumed by an independent trainer; optimization guarantees depend on the downstream RL algorithm.

## Evidence quality and limitations

Training-infrastructure paper, benchmark and hardware dependence, and no claim that every hidden harness state is observable through API calls.

## Important implementation details

Separate rollout execution, trajectory reconstruction, evaluation, and training services; version the adapter and preserve token fidelity.

## Claims this source supports

Harness portability requires an explicit observation boundary and faithful trace reconstruction.

## Claims this source weakens or contradicts

API compatibility as sufficient for semantic equivalence between harnesses.

## Relevance to a mathematics paper

Connects harness traces to off-policy data and asynchronous queueing/resource-allocation models.

## Connections to other sources

See the category and claim-level cross-references in [`INDEX.md`](INDEX.md) and the synthesis documents.

## Verification notes

Abstract, system architecture, trajectory reconstruction, validation experiments, and limitations checked in the local PDF. The archived file parsed successfully: 17 pages, 46566 extractable characters, SHA-256 `a9f5a30f97fe5683444a7b4cd4b038b6dc2ff4eb160c4d523217deb8f610d77e`.
