---
title: "RestGPT: Connecting Large Language Models with Real-World RESTful APIs"
authors: ["Yifan Song", "Weimin Xiong", "Dawei Zhu", "Wenhao Wu", "Han Qian", "Mingbo Song", "Hailiang Huang", "Cheng Li", "Ke Wang", "Rong Yao", "Ye Tian", "Sujian Li"]
year: 2023
venue: "preprint"
source_type: "preprint"
paper_url: "https://arxiv.org/abs/2306.06624"
pdf_path: "papers/academic/song-2023-restgpt.pdf"
accessed: "2026-09-04"
review_status: "skimmed"
evidence_confidence: "medium"
---

# song-2023-restgpt — RestGPT: Connecting Large Language Models with Real-World RESTful APIs

## Why this source is in the corpus

Models the action interface through which a harness turns language outputs into state-changing operations.

## Research question

Can coarse-to-fine planning make general REST API specifications usable for complex instructions?

## Harness mechanism studied

A planner chooses endpoint sequences, an API executor constructs requests and parses responses, and a response module synthesizes the result.

## Method and experimental setup

Real REST APIs and RestBench tasks evaluate endpoint selection and multi-step execution against prompting and tool baselines.

## Main findings

- Coarse-to-fine planning narrows large specifications and supports multi-step API sequences.
- Executor-side response parsing is essential because raw REST payloads can overwhelm context.

## Mathematical content

Plans are sequences over endpoints with observation-conditioned refinement; no formal completeness or safety guarantee.

## Evidence quality and limitations

Small API/domain set, live-service drift, possible credential or side-effect constraints, and evaluator dependence.

## Important implementation details

Parse OpenAPI specs into relevant slices, limit returned fields, and distinguish planning errors from HTTP or schema failures.

## Claims this source supports

Context shaping and response normalization are core tool-harness functions.

## Claims this source weakens or contradicts

A correct endpoint sequence as sufficient for safe real-world action.

## Relevance to a mathematics paper

Motivates hierarchical planning with stochastic execution and bounded observations.

## Connections to other sources

See the category and claim-level cross-references in [`INDEX.md`](INDEX.md) and the synthesis documents.

## Verification notes

Abstract, three-module design, RestBench setup, main comparisons, error taxonomy, and conclusion checked in the local PDF. The archived file parsed successfully: 25 pages, 75055 extractable characters, SHA-256 `61e65633db1e073de1690a14f87a5c8104e4540012794b92f9d5eeb0d61a1b34`.
