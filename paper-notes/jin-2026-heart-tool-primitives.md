---
title: "Harness Engineering in LLM Tool Use via Agent-Native Reusable Tool Primitives"
authors: ["Haibo Jin", "Suijin Wang", "Xucheng Yu", "Haojing Luo", "Haohan Wang"]
year: 2026
venue: "preprint"
source_type: "preprint"
paper_url: "https://arxiv.org/abs/2609.01736"
pdf_path: "papers/academic/jin-2026-heart-tool-primitives.pdf"
accessed: "2026-09-04"
review_status: "fully-reviewed"
evidence_confidence: "low"
---

# jin-2026-heart-tool-primitives — Harness Engineering in LLM Tool Use via Agent-Native Reusable Tool Primitives

## Why this source is in the corpus

Directly treats the harness, its optimization, or its runtime semantics as the object of study.

## Research question

Can natural-language tool wrappers and retrieval reduce schema brittleness and catalog overload?

## Harness mechanism studied

Tool Primitives wrap APIs with an LLM interface; ToolFace retrieves from 25,519 functions; planner, router, executor, and verifier stages orchestrate calls.

## Method and experimental setup

ToolBench evaluation plus 50 curated real tasks, commercial baselines, a verifier, and at most three replanning attempts.

## Main findings

- HEART reports 75.1% ToolBench pass and 75.7% win, only 1.7 and 1.9 points above its strongest commercial baseline.
- On 50 curated tasks it reports 84% versus a 22% commercial-model average.

## Mathematical content

Defines a tool set, primitive mapping, sufficiency decision, verifier family, and replanning budget B=3; no theorem.

## Evidence quality and limitations

Three-day-old v1 at the cutoff, author registry and curated tasks, and several components change together.

## Important implementation details

Retrieve only relevant wrappers, normalize heterogeneous schemas behind natural language, and make verification and retry budgets explicit.

## Claims this source supports

Tool interface design and catalog selection can be major harness variables.

## Claims this source weakens or contradicts

Large headline gains as attributable to one primitive without factorial ablation.

## Relevance to a mathematics paper

Supplies typed mappings and bounded-loop notation for tool orchestration.

## Connections to other sources

See the category and claim-level cross-references in [`INDEX.md`](INDEX.md) and the synthesis documents.

## Verification notes

Abstract, architecture, Table 1, 50-task study, verifier and budget definitions checked in the local PDF. The archived file parsed successfully: 21 pages, 72958 extractable characters, SHA-256 `1e741d517eb9593cb7f4f07a5542d04288e86ad2a4c0c8260d9976f1ec08dfee`.
