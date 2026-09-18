---
title: "Agentless: Demystifying LLM-based Software Engineering Agents"
authors: ["Chunqiu Steven Xia", "Yinlin Deng", "Soren Dunn", "Lingming Zhang"]
year: 2024
venue: "FSE-2025"
source_type: "peer-reviewed"
paper_url: "https://arxiv.org/abs/2407.01489"
pdf_path: "papers/academic/xia-2024-agentless.pdf"
accessed: "2026-09-04"
review_status: "fully-reviewed"
evidence_confidence: "high"
---

# xia-2024-agentless — Agentless: Demystifying LLM-based Software Engineering Agents

## Why this source is in the corpus

Makes model–harness–environment coupling observable in executable, long-horizon tasks.

## Research question

Can a simple staged pipeline compete with autonomous software agents?

## Harness mechanism studied

Agentless separates repository localization, patch generation, and test-based patch validation instead of running an open-ended tool loop.

## Method and experimental setup

FSE 2025 paper evaluating a deliberately simple pipeline on SWE-bench Lite and Verified, with localization and repair analyses.

## Main findings

- The revised paper reports 32% on SWE-bench Lite, 96 of 300 tasks, at roughly 0.70 dollars per task.
- The result shows that structured decomposition and candidate selection can rival more elaborate agents, but earlier 27.33% and 0.34-dollar figures remain widely repeated.

## Mathematical content

Candidate validation is a best-of-n selection problem; fair comparison requires conditioning on total calls, tokens, tests observed, and selector error.

## Evidence quality and limitations

The pipeline uses benchmark tests and multiple candidates; reported numbers changed across versions; a simple architecture is not automatically a clean causal ablation of autonomy.

## Important implementation details

Version every prompt and result, disclose the candidate count and validation information, and cite the revised rather than superseded score.

## Claims this source supports

Small explicit pipelines are strong controls for claims about elaborate interactive harnesses.

## Claims this source weakens or contradicts

Framework complexity as a prerequisite for high software-repair scores.

## Relevance to a mathematics paper

Supports cost-aware selection models and sequential pipeline reliability analysis.

## Connections to other sources

See the category and claim-level cross-references in [`INDEX.md`](INDEX.md) and the synthesis documents.

## Verification notes

Revised score, task count, cost, architecture, prior-number warning, and limitations checked against the local PDF. The archived file parsed successfully: 25 pages, 96898 extractable characters, SHA-256 `1675c2dcd5ecaef47e8a4356062f60be642cee82e1bbacb044c9d047dce4c856`.
