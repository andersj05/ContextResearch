---
title: "STALE: Can LLM Agents Know When Their Memories Are No Longer Valid?"
authors: ["Hanxiang Chao", "Yihan Bai", "Rui Sheng", "Tianle Li", "Yushi Sun"]
year: 2026
venue: "preprint"
source_type: "preprint"
paper_url: "https://arxiv.org/abs/2605.06527"
pdf_path: "papers/academic/chao-2026-stale.pdf"
accessed: "2026-09-04"
review_status: "fully-reviewed"
evidence_confidence: "medium"
---

# chao-2026-stale — STALE: Can LLM Agents Know When Their Memories Are No Longer Valid?

## Why this source is in the corpus

Provides mechanisms and failure modes for state, retrieval, summarization, and bounded context.

## Research question

Can memory agents detect when later evidence implicitly invalidates an earlier belief?

## Harness mechanism studied

STALE creates implicit conflicts and probes state resolution, premise resistance, and related update behavior over up to 150K-token histories.

## Method and experimental setup

400 expert-validated conflicts, 1,200 queries, more than 100 topics, multiple models and memory frameworks, and retrieval-versus-resolution analysis.

## Main findings

- The best plain model scores 55.2%, while most memory frameworks score below 10%.
- LightMem retrieves new evidence in 77.5% of selected cases yet still fails state resolution 56.1% and premise resistance 99.0%, showing retrieval is not adjudication.

## Mathematical content

Latent state S_t maps attributes to current values; implicit conflict requires new memory to entail the negation of an old value under background knowledge.

## Evidence quality and limitations

Generated dialogues, LLM judge, new author benchmark, framework configuration sensitivity, and the authors' own method reaches 68%.

## Important implementation details

Store temporal provenance and explicit supersession edges; test whether retrieved contradictions actually update active state.

## Claims this source supports

Memory validity and retrieval availability are distinct capabilities.

## Claims this source weakens or contradicts

High retrieval recall as evidence of correct belief revision.

## Relevance to a mathematics paper

Offers a temporal-state logic and separate retrieval and update failure probabilities.

## Connections to other sources

See the category and claim-level cross-references in [`INDEX.md`](INDEX.md) and the synthesis documents.

## Verification notes

Benchmark construction, latent-state definition, retrieval diagnostics, framework results, and limitations checked in the local PDF. The archived file parsed successfully: 37 pages, 115691 extractable characters, SHA-256 `388f71f1eb952e7d7e7b19c2f25bfc744c47efa8ee00a548093b949432495109`.
