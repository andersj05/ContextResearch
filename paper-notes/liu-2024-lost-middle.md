---
title: "Lost in the Middle: How Language Models Use Long Contexts"
authors: ["Nelson F. Liu", "Kevin Lin", "John Hewitt", "Ashwin Paranjape", "Michele Bevilacqua", "Fabio Petroni", "Percy Liang"]
year: 2024
venue: "TACL-2024"
source_type: "peer-reviewed"
paper_url: "https://arxiv.org/abs/2307.03172"
pdf_path: "papers/academic/liu-2024-lost-middle.pdf"
accessed: "2026-09-04"
review_status: "fully-reviewed"
evidence_confidence: "high"
---

# liu-2024-lost-middle — Lost in the Middle: How Language Models Use Long Contexts

## Why this source is in the corpus

Provides mechanisms and failure modes for state, retrieval, summarization, and bounded context.

## Research question

Does a long context window imply robust access to information at every position?

## Harness mechanism studied

The sole relevant document or key-value pair is moved through otherwise fixed long contexts.

## Method and experimental setup

Controlled multi-document QA and synthetic key-value retrieval vary relevant-position and context length across language models.

## Main findings

- Accuracy follows a U-shaped positional curve: beginning and end usually beat the middle.
- GPT-3.5 can fall below its 56.1% closed-book baseline for middle evidence, and some positional drops exceed 20 points.

## Mathematical content

A useful derived statistic is positional sensitivity max_j Acc(j)-min_j Acc(j); the paper itself is empirical rather than theorem-driven.

## Evidence quality and limitations

Models are 2023-era, tasks emphasize retrieval rather than long-horizon action, and later architectures may shift magnitudes.

## Important implementation details

Place critical instructions deliberately, retrieve or summarize instead of dumping context, and test location perturbations.

## Claims this source supports

Context arrangement is a causal harness variable.

## Claims this source weakens or contradicts

Nominal context length as evidence of uniformly usable memory.

## Relevance to a mathematics paper

Provides a controlled position variable and a simple robustness functional.

## Connections to other sources

See the category and claim-level cross-references in [`INDEX.md`](INDEX.md) and the synthesis documents.

## Verification notes

Position-controlled figures, closed-book comparison, document-count study, model coverage, and limitations checked in the local PDF. The archived file parsed successfully: 18 pages, 65406 extractable characters, SHA-256 `653b29619eae2ae4b361d7bdcdc06db4bedcb1b0eabe31814036beca8c1af0b1`.
