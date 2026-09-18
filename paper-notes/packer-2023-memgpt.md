---
title: "MemGPT: Towards LLMs as Operating Systems"
authors: ["Charles Packer", "Sarah Wooders", "Kevin Lin", "Vivian Fang", "Shishir G. Patil", "Ion Stoica", "Joseph E. Gonzalez"]
year: 2023
venue: "preprint"
source_type: "preprint"
paper_url: "https://arxiv.org/abs/2310.08560"
pdf_path: "papers/academic/packer-2023-memgpt.pdf"
accessed: "2026-09-04"
review_status: "fully-reviewed"
evidence_confidence: "high"
---

# packer-2023-memgpt — MemGPT: Towards LLMs as Operating Systems

## Why this source is in the corpus

Provides mechanisms and failure modes for state, retrieval, summarization, and bounded context.

## Research question

Can virtual-memory ideas extend usable context beyond a model's physical window?

## Harness mechanism studied

A controller pages between main context and recall or archival stores, evicts history, summarizes recursively, and lets the model call memory functions.

## Method and experimental setup

Deep-memory conversational retrieval and long-document tasks compare context summarization with searchable tiered memory across GPT models.

## Main findings

- Deep-memory retrieval rises from 38.7 to 66.9 for GPT-3.5, 32.1 to 92.5 for GPT-4, and 35.3 to 93.4 for GPT-4 Turbo.
- The baseline sees a lossy summary while MemGPT can search preserved history, so the gain mainly demonstrates information retention and retrieval.

## Mathematical content

A memory hierarchy with paging, eviction, recursive summarization, and context-pressure thresholds parallels virtual memory but has no bounded-recall theorem.

## Evidence quality and limitations

Small author-built tasks, unequal retained information, no component ablations, and search or paging errors remain possible.

## Important implementation details

Separate working, recall, and archival stores; expose pressure, page-in, page-out, and summarization events in traces.

## Claims this source supports

External paging can make more historical information accessible than a lossy fixed summary.

## Claims this source weakens or contradicts

Virtual context as literally unlimited or equivalent to having all history in attention.

## Relevance to a mathematics paper

Enables cache and paging models with retrieval miss and summarization-loss probabilities.

## Connections to other sources

See the category and claim-level cross-references in [`INDEX.md`](INDEX.md) and the synthesis documents.

## Verification notes

Table 2, memory hierarchy, paging tools, context-pressure logic, baselines, and limitations checked in the local PDF. The archived file parsed successfully: 13 pages, 57200 extractable characters, SHA-256 `9f674bcff69c86f11c813dcfad613d8841f5f8ed17979e3c4df06a91df7762e0`.
