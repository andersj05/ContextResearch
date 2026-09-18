---
title: "HuggingGPT: Solving AI Tasks with ChatGPT and its Friends in Hugging Face"
authors: ["Yongliang Shen", "Kaitao Song", "Xu Tan", "Dongsheng Li", "Weiming Lu", "Yueting Zhuang"]
year: 2023
venue: "NeurIPS-2023"
source_type: "peer-reviewed"
paper_url: "https://arxiv.org/abs/2303.17580"
pdf_path: "papers/academic/shen-2023-hugginggpt.pdf"
accessed: "2026-09-04"
review_status: "skimmed"
evidence_confidence: "medium"
---

# shen-2023-hugginggpt — HuggingGPT: Solving AI Tasks with ChatGPT and its Friends in Hugging Face

## Why this source is in the corpus

Models the action interface through which a harness turns language outputs into state-changing operations.

## Research question

Can an LLM orchestrate many specialist models through a common model-hub interface?

## Harness mechanism studied

Four stages: task planning, model selection, model execution, and response generation over Hugging Face models.

## Method and experimental setup

Prototype system and qualitative or task demonstrations across language, vision, audio, and multimodal workloads.

## Main findings

- The controller decomposes compound requests and composes outputs from heterogeneous expert models.
- The work establishes feasibility more strongly than comparative reliability or efficiency.

## Mathematical content

A dependency graph represents subtasks and execution order; model selection is an LLM-mediated routing problem without a proven optimal policy.

## Evidence quality and limitations

Heavy dependence on ChatGPT, model descriptions, live endpoints, and qualitative cases; no broad cost-matched ablation.

## Important implementation details

Separate planning from selection and execution, preserve intermediate artifacts, and make dependency and failure propagation visible.

## Claims this source supports

Natural language can serve as a coordination interface across specialist tools.

## Claims this source weakens or contradicts

A compelling demo as evidence of robust autonomous orchestration.

## Relevance to a mathematics paper

Motivates DAG scheduling with stochastic node success and routing error.

## Connections to other sources

See the category and claim-level cross-references in [`INDEX.md`](INDEX.md) and the synthesis documents.

## Verification notes

Abstract, four-stage architecture, dependency representation, demonstrations, failure discussion, and conclusion checked in the local PDF. The archived file parsed successfully: 27 pages, 93484 extractable characters, SHA-256 `5add5f7ff9041299c305769d49615e1ac2de2229e17c46e0811d1a60f94d6e3b`.
