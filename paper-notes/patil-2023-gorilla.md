---
title: "Gorilla: Large Language Model Connected with Massive APIs"
authors: ["Shishir G. Patil", "Tianjun Zhang", "Xin Wang", "Joseph E. Gonzalez"]
year: 2023
venue: "preprint"
source_type: "preprint"
paper_url: "https://arxiv.org/abs/2305.15334"
pdf_path: "papers/academic/patil-2023-gorilla.pdf"
accessed: "2026-09-04"
review_status: "skimmed"
evidence_confidence: "medium"
---

# patil-2023-gorilla — Gorilla: Large Language Model Connected with Massive APIs

## Why this source is in the corpus

Models the action interface through which a harness turns language outputs into state-changing operations.

## Research question

Can retrieval-grounded fine-tuning reduce hallucinated API calls and adapt to changing documentation?

## Harness mechanism studied

A retriever supplies current API documents to a fine-tuned LLaMA model that generates calls under constrained evaluation.

## Method and experimental setup

APIBench spans model-hub APIs; Gorilla, GPT-family baselines, retrieval variants, and document changes are compared.

## Main findings

- Gorilla reports better API-call generation than GPT-4 in its benchmark and fewer hallucinated APIs.
- Retrieval enables adaptation to changed documentation, but retrieval and fine-tuning effects are not always isolated.

## Mathematical content

API correctness can be viewed as exact or AST-level structured prediction conditioned on retrieved documentation.

## Evidence quality and limitations

Project-authored benchmark, rapidly drifting APIs, limited semantic execution checks, and model-data-training differences.

## Important implementation details

Version API documentation, separate retrieval recall from call validity, and validate executable arguments rather than string similarity alone.

## Claims this source supports

Fresh documentation and constrained output formats can reduce tool hallucination.

## Claims this source weakens or contradicts

Benchmark API-call accuracy as general evidence of long-horizon agency.

## Relevance to a mathematics paper

Provides a conditional structured-prediction framing with retrieval error.

## Connections to other sources

See the category and claim-level cross-references in [`INDEX.md`](INDEX.md) and the synthesis documents.

## Verification notes

Abstract, retrieval architecture, APIBench construction, hallucination analysis, document-change experiment, and limitations checked in the local PDF. The archived file parsed successfully: 18 pages, 60885 extractable characters, SHA-256 `1aeae54095cdae3a3ebaa29f7af0919d666e0c87d961848ae85b991b3c022718`.
