---
title: "Holistic Agent Leaderboard: The Missing Infrastructure for AI Agent Evaluation"
authors: ["Sayash Kapoor", "Benedikt Stroebl", "Peter Kirgis", "Nitya Nadgir", "Zachary S Siegel", "Boyi Wei", "Tianci Xue", "Ziru Chen", "Felix Chen", "Saiteja Utpala", "Franck Ndzomga", "Dheeraj Oruganty", "Sophie Luskin", "Kangheng Liu", "Botao Yu", "Amit Arora", "Dongyoon Hahm", "Harsh Trivedi", "Huan Sun", "Juyong Lee", "Tengjun Jin", "Yifan Mai", "Yifei Zhou", "Yuxuan Zhu", "Rishi Bommasani", "Daniel Kang", "Dawn Song", "Peter Henderson", "Yu Su", "Percy Liang", "Arvind Narayanan"]
year: 2026
venue: "ICLR-2026"
source_type: "peer-reviewed"
paper_url: "https://arxiv.org/abs/2510.11977"
pdf_path: "papers/academic/kapoor-2026-hal.pdf"
accessed: "2026-09-04"
review_status: "fully-reviewed"
evidence_confidence: "medium"
---

# kapoor-2026-hal — Holistic Agent Leaderboard: The Missing Infrastructure for AI Agent Evaluation

## Why this source is in the corpus

Makes model–harness–environment coupling observable in executable, long-horizon tasks.

## Research question

What infrastructure is needed for reproducible, multidimensional agent evaluation at scale?

## Harness mechanism studied

HAL standardizes scaffold adapters, distributes evaluations over virtual machines, records calls, costs, traces, and environments, and analyzes model-scaffold-benchmark combinations.

## Method and experimental setup

2025 preprint reporting 21,730 rollouts over nine models and nine benchmarks, about 40,000 dollars and 2.5 billion logged tokens, with automated and manual trace inspection.

## Main findings

- Scaffolds materially change both accuracy and cost, and higher reasoning effort reduces accuracy in a majority of the reported paired conditions.
- Trace audits find benchmark-search shortcuts and potentially harmful tool behavior invisible to terminal success.

## Mathematical content

The target is a response surface Y over model, scaffold, benchmark, effort, and their interactions; sparse cells prevent a full balanced factorial estimate.

## Evidence quality and limitations

The design is broad but not fully crossed; API and benchmark versions are time-specific; LLM-aided log labels can err; the paper was a recent preprint at cutoff.

## Important implementation details

Use one instrumented runner, pin VM images, populate balanced factorial cells where affordable, publish failed as well as successful traces, and cluster uncertainty by task.

## Claims this source supports

Evaluation harnesses can remove accidental variance and reveal scaffold interactions.

## Claims this source weakens or contradicts

Treating more reasoning effort or a stronger model as monotonically improving every agent system.

## Relevance to a mathematics paper

Motivates mixed-effects factorial designs and interaction-aware ranking.

## Connections to other sources

See the category and claim-level cross-references in [`INDEX.md`](INDEX.md) and the synthesis documents.

## Verification notes

Abstract and core methods checked for 21,730 rollouts, nine-by-nine scope, cost, 2.5-billion-token logs, reasoning-effort result, harness functions, and limitations. The archived file parsed successfully: 66 pages, 171890 extractable characters, SHA-256 `f224b5ef6ec2a9e1606878e39e81acd4e0ed8ac9f4d80b120f17266c5c281d0f`.
