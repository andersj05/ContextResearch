---
title: "LongMemEval: Benchmarking Chat Assistants on Long-Term Interactive Memory"
authors: ["Di Wu", "Hongwei Wang", "Wenhao Yu", "Yuwei Zhang", "Kai-Wei Chang", "Dong Yu"]
year: 2024
venue: "ICLR-2025"
source_type: "peer-reviewed"
paper_url: "https://arxiv.org/abs/2410.10813"
pdf_path: "papers/academic/wu-2024-longmemeval.pdf"
accessed: "2026-09-04"
review_status: "fully-reviewed"
evidence_confidence: "high"
---

# wu-2024-longmemeval — LongMemEval: Benchmarking Chat Assistants on Long-Term Interactive Memory

## Why this source is in the corpus

Provides mechanisms and failure modes for state, retrieval, summarization, and bounded context.

## Research question

How well do assistants extract, reason over, update, and abstain on multi-session memories?

## Harness mechanism studied

A 500-question benchmark embeds evidence in scalable histories and probes extraction, cross-session, temporal, update, and abstention abilities.

## Method and experimental setup

Long-context models and nine memory systems are compared with oracle evidence, retrieval variants, timestamps, and query expansion.

## Main findings

- GPT-4o drops from 0.870 oracle accuracy to 0.606 on long histories, about 30.3%; other models drop roughly 36-66%.
- Extracted-user-fact indexing adds 9.4 points recall@k and 5.4 points QA accuracy; timestamp methods add 6.8-11.3 points recall in temporal queries.

## Mathematical content

Separates retrieval recall from downstream answer accuracy; evaluation uses an LLM grader reported above 97% human agreement.

## Evidence quality and limitations

Constructed histories, only 500 questions, judge dependence, and oracle evidence gives more information than practical systems.

## Important implementation details

Evaluate memory writes, retrieval, update conflict, time, abstention, and answer generation separately.

## Claims this source supports

Long-term memory failure is not just retrieval and persists even with long context windows.

## Claims this source weakens or contradicts

A single memory-recall number as adequate evaluation.

## Relevance to a mathematics paper

Provides a staged error decomposition and paired efficiency-accuracy metrics.

## Connections to other sources

See the category and claim-level cross-references in [`INDEX.md`](INDEX.md) and the synthesis documents.

## Verification notes

Tables 1-2, oracle-versus-long-history results, retrieval ablations, grader agreement, and limitations checked in the local PDF. The archived file parsed successfully: 28 pages, 104768 extractable characters, SHA-256 `05c5d055201466a241a56e082cdd02d39ad566fa04b3804891983e4e069a3fda`.
