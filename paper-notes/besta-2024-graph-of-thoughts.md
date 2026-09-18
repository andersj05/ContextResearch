---
title: "Graph of Thoughts: Solving Elaborate Problems with Large Language Models"
authors: ["Maciej Besta", "Nils Blach", "Ales Kubicek", "Robert Gerstenberger", "Michal Podstawski", "Lukas Gianinazzi", "Joanna Gajda", "Tomasz Lehmann", "Hubert Niewiadomski", "Piotr Nyczyk", "Torsten Hoefler"]
year: 2024
venue: "AAAI-2024"
source_type: "peer-reviewed"
paper_url: "https://arxiv.org/abs/2308.09687"
pdf_path: "papers/academic/besta-2024-graph-of-thoughts.pdf"
accessed: "2026-09-04"
review_status: "skimmed"
evidence_confidence: "medium"
---

# besta-2024-graph-of-thoughts — Graph of Thoughts: Solving Elaborate Problems with Large Language Models

## Why this source is in the corpus

Supports analysis of inference-time search, feedback, stopping, and verifier error.

## Research question

Do graph-shaped transformations generalize linear chains and trees for reasoning workflows?

## Harness mechanism studied

Thought vertices are generated, scored, aggregated, refined, and connected by a developer-specified graph of operations.

## Method and experimental setup

Sorting, set operations, keyword counting, and document merging compare graph programs with chain and tree prompting on quality and cost.

## Main findings

- Aggregation and refinement let multiple partial solutions share information rather than only branch independently.
- Reported gains are task- and graph-specific; the graph itself encodes substantial human problem structure.

## Mathematical content

A directed graph represents thought states and transformations; execution is a graph-rewrite or dataflow process without a general optimality theorem.

## Evidence quality and limitations

Few engineered tasks, hand-designed graphs, changing call counts, and limited evidence that a graph transfers to unseen problem families.

## Important implementation details

Treat prompts as node programs, record edge dependencies and reducers, and charge every generation and aggregation call.

## Claims this source supports

Harness control topology can be richer than a while loop or tree.

## Claims this source weakens or contradicts

Graph structure as automatically superior to simpler workflows at equal information and compute.

## Relevance to a mathematics paper

Connects harness orchestration to DAGs, graph rewriting, and resource scheduling.

## Connections to other sources

See the category and claim-level cross-references in [`INDEX.md`](INDEX.md) and the synthesis documents.

## Verification notes

Abstract, graph formalism, operation definitions, benchmark and cost tables, and limitations checked in the local PDF. The archived file parsed successfully: 63 pages, 172280 extractable characters, SHA-256 `73caa3c05813105e5db38edfbb58e1b660771a00dfdb74768c8845e15263c5da`.
