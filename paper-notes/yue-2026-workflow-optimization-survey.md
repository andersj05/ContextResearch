---
title: "From Static Templates to Dynamic Runtime Graphs: A Survey of Workflow Optimization for LLM Agents"
authors: ["Ling Yue", "Kushal Raj Bhandari", "Ching-Yun Ko", "Dhaval Patel", "Shuxin Lin", "Nianjun Zhou", "Jianxi Gao", "Pin-Yu Chen", "Shaowu Pan"]
year: 2026
venue: "preprint"
source_type: "preprint"
paper_url: "https://arxiv.org/abs/2603.22386"
pdf_path: "papers/academic/yue-2026-workflow-optimization-survey.pdf"
accessed: "2026-09-04"
review_status: "skimmed"
evidence_confidence: "medium"
---

# yue-2026-workflow-optimization-survey — From Static Templates to Dynamic Runtime Graphs: A Survey of Workflow Optimization for LLM Agents

## Why this source is in the corpus

Directly studies reusable harness components, outer-loop optimization, self-modification, or the statistical controls needed to decide whether an update is a real improvement.

## Research question

How should workflow optimization be classified by structure, timing, editable variables, feedback, and evaluation?

## Harness mechanism studied

The survey models workflows as agentic computation graphs and separates reusable templates, run-specific realized graphs, and execution traces, with offline, pre-execution, and in-execution structure determination.

## Method and experimental setup

The authors synthesize static and dynamic methods across graph plasticity, node and structure variables, metric/verifier/preference/trace feedback, and propose reporting effectiveness, efficiency, robustness, and graph properties.

## Main findings

- The survey’s main empirical contribution is a structured literature map, not a new effect estimate; it distinguishes graph-determination time and plasticity modes none/select/generate/edit.
- Its minimum-reporting proposal explicitly argues that downstream score alone is insufficient, but the survey does not validate that protocol prospectively or meta-analyze optimizer effects.

## Mathematical content

An ACG template is G-bar=(V,E,Phi,Sigma,A), a realized graph is G_run, and a trace tau contains states, actions, observations, and costs; quality-cost utility is conceptual rather than a proved estimator.

## Evidence quality and limitations

2026 preprint; inclusion and scope labels are author judgments; the rapidly changing corpus and heterogeneous metrics preclude causal ranking; no formal systematic-review risk-of-bias or pooled statistics are given.

## Important implementation details

For each method, record template versus realized graph, node parameters, topology/routing/scheduling, determination time, plasticity, feedback signal, execution trace, task quality, cost, robustness, and structural variation.

## Claims this source supports

A rigorous harness study must specify exactly which graph is optimized, when it changes, and what signal and cost drive the update.

## Claims this source weakens or contradicts

Taxonomy placement and survey frequency do not establish effectiveness, and dynamic generation is not automatically better than static selection.

## Relevance to a mathematics paper

Provides a unifying graph state space and a multidimensional evaluation schema useful for formal experimental design.

## Connections to other sources

See the category and claim-level cross-references in [`INDEX.md`](INDEX.md) and the synthesis documents.

## Verification notes

Local PDF abstract, glossary, Sections 2–8, comparison cards, appendix classification tables, and conclusion were checked; no independent literature completeness audit was done. The archived file parsed successfully: 31 pages, 115626 extractable characters, SHA-256 `d1cc2287aaa143213bbd11d5ad77a1bb781a7015ed9bb71eceb4b42767a1a5c8`.
