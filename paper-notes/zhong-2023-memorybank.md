---
title: "MemoryBank: Enhancing Large Language Models with Long-Term Memory"
authors: ["Wanjun Zhong", "Lianghong Guo", "Qiqi Gao", "He Ye", "Yanlin Wang"]
year: 2023
venue: "AAAI-2024"
source_type: "peer-reviewed"
paper_url: "https://arxiv.org/abs/2305.10250"
pdf_path: "papers/academic/zhong-2023-memorybank.pdf"
accessed: "2026-09-04"
review_status: "skimmed"
evidence_confidence: "medium"
---

# zhong-2023-memorybank — MemoryBank: Enhancing Large Language Models with Long-Term Memory

## Why this source is in the corpus

Provides mechanisms and failure modes for state, retrieval, summarization, and bounded context.

## Research question

Can a chat agent retain and update personalized memories across long interaction histories?

## Harness mechanism studied

A long-term store summarizes events, retrieves relevant memories, updates user personality, and applies an Ebbinghaus-inspired forgetting schedule.

## Method and experimental setup

Long-term dialogue and companion-style evaluations compare MemoryBank-enabled models with context-only or memory baselines.

## Main findings

- The system preserves selected facts and personalization beyond the immediate context in reported evaluations.
- Its forgetting and update machinery is a handcrafted memory policy rather than learned evidence that human forgetting is optimal for agents.

## Mathematical content

Memory strength and forgetting are inspired by an exponential retention curve; retrieval combines semantic similarity with time-dependent state.

## Evidence quality and limitations

Synthetic interactions, model-based evaluation, privacy and stale-memory risks, coupled summarization and retrieval, and no independent longitudinal replication.

## Important implementation details

Version each memory, retain provenance and time, permit correction or deletion, and evaluate false recall as well as recall.

## Claims this source supports

External memory can extend personalization beyond a context window.

## Claims this source weakens or contradicts

Human-memory metaphors as a validated optimal retention policy.

## Relevance to a mathematics paper

Supports decay, retrieval, and update equations with explicit stale-state error.

## Connections to other sources

See the category and claim-level cross-references in [`INDEX.md`](INDEX.md) and the synthesis documents.

## Verification notes

Abstract, memory lifecycle, forgetting formulation, dialogue experiments, ablations, and limitations checked in the local PDF. The archived file parsed successfully: 11 pages, 44790 extractable characters, SHA-256 `6c60f7f95a872de85179b770edaba584da7a30da37490522394a3e4888aa0059`.
