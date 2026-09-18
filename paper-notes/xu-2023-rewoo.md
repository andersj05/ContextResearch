---
title: "ReWOO: Decoupling Reasoning from Observations for Efficient Augmented Language Models"
authors: ["Binfeng Xu", "Zhiyuan Peng", "Bowen Lei", "Subhabrata Mukherjee", "Yuchen Liu", "Dongkuan Xu"]
year: 2023
venue: "preprint"
source_type: "preprint"
paper_url: "https://arxiv.org/abs/2305.18323"
pdf_path: "papers/academic/xu-2023-rewoo.pdf"
accessed: "2026-09-04"
review_status: "skimmed"
evidence_confidence: "medium"
---

# xu-2023-rewoo — ReWOO: Decoupling Reasoning from Observations for Efficient Augmented Language Models

## Why this source is in the corpus

Models the action interface through which a harness turns language outputs into state-changing operations.

## Research question

Can planning be decoupled from tool observations to reduce repeated prompt and token costs?

## Harness mechanism studied

A planner writes a full plan with variable placeholders, workers execute tools, and a solver combines stored evidence.

## Method and experimental setup

Reasoning and knowledge tasks compare ReWOO with interleaved augmented-language-model baselines on accuracy and token usage.

## Main findings

- Decoupling avoids repeated full-context model calls and reduces reported token consumption while retaining competitive accuracy.
- The efficiency comes at the cost of less observation-conditioned replanning.

## Mathematical content

A plan is an acyclic sequence with symbolic evidence variables; token complexity falls by avoiding repeated prefixes, but robustness to failed steps is not guaranteed.

## Evidence quality and limitations

Tasks permit mostly predictable plans, tools are controlled, models are dated, and failure recovery is weaker than in closed-loop methods.

## Important implementation details

Use symbolic handles for tool outputs and distinguish plan-time dependencies from execution-time evidence.

## Claims this source supports

Planner-worker separation can improve latency and context efficiency.

## Claims this source weakens or contradicts

Open-loop plans as universally preferable to feedback-driven control.

## Relevance to a mathematics paper

Enables comparison of open-loop and closed-loop control under shared information budgets.

## Connections to other sources

See the category and claim-level cross-references in [`INDEX.md`](INDEX.md) and the synthesis documents.

## Verification notes

Abstract, planner-worker-solver design, token accounting, benchmark comparisons, failure discussion, and conclusion checked in the local PDF. The archived file parsed successfully: 25 pages, 78816 extractable characters, SHA-256 `1847bb42b9efb3a2860ca48edc962ee9c9b7d3e0359887ea596e1b23084de9ff`.
