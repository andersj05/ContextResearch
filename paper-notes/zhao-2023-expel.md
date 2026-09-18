---
title: "ExpeL: LLM Agents Are Experiential Learners"
authors: ["Andrew Zhao", "Daniel Huang", "Quentin Xu", "Matthieu Lin", "Yong-Jin Liu", "Gao Huang"]
year: 2023
venue: "AAAI-2024"
source_type: "peer-reviewed"
paper_url: "https://arxiv.org/abs/2308.10144"
pdf_path: "papers/academic/zhao-2023-expel.pdf"
accessed: "2026-09-04"
review_status: "skimmed"
evidence_confidence: "medium"
---

# zhao-2023-expel — ExpeL: LLM Agents Are Experiential Learners

## Why this source is in the corpus

Provides mechanisms and failure modes for state, retrieval, summarization, and bounded context.

## Research question

Can an agent learn reusable natural-language insights and examples from prior task trajectories without fine-tuning?

## Harness mechanism studied

Training trajectories are compared to extract general insights; similar successful experiences are retrieved as in-context examples at evaluation time.

## Method and experimental setup

HotpotQA, ALFWorld, and WebShop use practice tasks, success and failure trajectories, retrieval, insight ablations, and Reflexion combinations.

## Main findings

- ExpeL retrieve-only reports 54.5-60.4% across ALFWorld rounds compared with ReAct plus Reflexion at 40.3-54.4%; adding Reflexion reaches 59.0-64.2%.
- Benefits vary by domain and depend on a stronger model extracting valid insights.

## Mathematical content

Experience E changes an in-context policy without parameter updates; retrieval uses embedding similarity and a learned insight set.

## Evidence quality and limitations

Practice and evaluation distributions may overlap, models extract and judge advice, retries differ, and stored hallucinated insights can harm later tasks.

## Important implementation details

Preserve provenance from insight to trajectories, validate advice on held-out tasks, and age or remove harmful memories.

## Claims this source supports

Cross-task experiential memory can improve a frozen agent.

## Claims this source weakens or contradicts

All reflection-like gains as within-task self-correction or parameter learning.

## Relevance to a mathematics paper

Supports case-based learning and empirical-Bayes views of nonparametric policy adaptation.

## Connections to other sources

See the category and claim-level cross-references in [`INDEX.md`](INDEX.md) and the synthesis documents.

## Verification notes

Tables 1-3 and 5, training and retrieval algorithms, insight examples, ablations, and limitations checked in the local PDF. The archived file parsed successfully: 38 pages, 72846 extractable characters, SHA-256 `01e533d81fb4a5f91797c073a9b1929acbaa64da45a592b26563ca7d135024f3`.
