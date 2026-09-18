---
title: "Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks"
authors: ["Patrick Lewis", "Ethan Perez", "Aleksandra Piktus", "Fabio Petroni", "Vladimir Karpukhin", "Naman Goyal", "Heinrich Küttler", "Mike Lewis", "Wen-tau Yih", "Tim Rocktäschel", "Sebastian Riedel", "Douwe Kiela"]
year: 2020
venue: "NeurIPS-2020"
source_type: "peer-reviewed"
paper_url: "https://arxiv.org/abs/2005.11401"
pdf_path: "papers/academic/lewis-2020-rag.pdf"
accessed: "2026-09-04"
review_status: "fully-reviewed"
evidence_confidence: "high"
---

# lewis-2020-rag — Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks

## Why this source is in the corpus

Provides mechanisms and failure modes for state, retrieval, summarization, and bounded context.

## Research question

Can a generator retrieve and marginalize over an external nonparametric memory?

## Harness mechanism studied

A dense retriever selects Wikipedia passages and a sequence-to-sequence model conditions generation on one document per sequence or per token.

## Method and experimental setup

Knowledge-intensive QA, fact verification, and generation compare RAG variants with parametric and retrieval baselines; index-date swaps probe updateability.

## Main findings

- Dense retrieval generally improves knowledge tasks, although BM25 remains strongest on FEVER.
- Swapping 2016 and 2018 indexes changes generated world-leader answers to match the selected index about 70% and 68%, versus 12% and 4% for mismatched dates.

## Mathematical content

p_eta(z|x) is proportional to exp(d(z)^T q(x)); RAG-Sequence marginalizes one z over a sequence and RAG-Token marginalizes per output token.

## Evidence quality and limitations

Fine-tuned BART and DPR, old Wikipedia, provenance is not truth, and this is not a full agent-memory write or update system.

## Important implementation details

Version the corpus, expose retrieved passages, measure retrieval recall and generation grounding separately, and support invalidation.

## Claims this source supports

Changing external memory can causally update model outputs without changing weights.

## Claims this source weakens or contradicts

Retrieval as proof of factuality or resolution of conflicting state.

## Relevance to a mathematics paper

Provides latent-document marginalization equations and a clean external-memory intervention.

## Connections to other sources

See the category and claim-level cross-references in [`INDEX.md`](INDEX.md) and the synthesis documents.

## Verification notes

Retrieval equations, main task tables, BM25 exception, index-swap experiment, and limitations checked in the local PDF. The archived file parsed successfully: 19 pages, 69056 extractable characters, SHA-256 `23e3249e9a1e75418d82efecab0ea8c4d033b89c93742f63208d47ce01f21233`.
