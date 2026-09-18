---
title: "Multi-agent Architecture Search via Agentic Supernet"
authors: ["Guibin Zhang", "Luyang Niu", "Junfeng Fang", "Kun Wang", "Lei Bai", "Xiang Wang"]
year: 2025
venue: "preprint"
source_type: "preprint"
paper_url: "https://arxiv.org/abs/2502.04180"
pdf_path: "papers/academic/zhang-2025-maas.pdf"
accessed: "2026-09-04"
review_status: "skimmed"
evidence_confidence: "high"
---

# zhang-2025-maas — Multi-agent Architecture Search via Agentic Supernet

## Why this source is in the corpus

Directly studies reusable harness components, outer-loop optimization, self-modification, or the statistical controls needed to decide whether an update is a real improvement.

## Research question

Can a learned supernet choose a different multi-agent architecture and inference budget for each query?

## Harness mechanism studied

A probabilistic continuous agentic supernet assigns query-conditioned probabilities to nodes, edges, and operations, from which a realized architecture is sampled or selected.

## Method and experimental setup

MaAS optimizes the supernet on task rewards with resource-aware terms, instantiates query-specific systems, and evaluates performance, cost, cross-dataset transfer, and cross-backbone transfer on six benchmarks.

## Main findings

- The abstract reports that MaAS uses 6–45% of the inference cost of compared handcrafted or automated multi-agent systems while outperforming them by 0.54–16.89%.
- These ranges are source-reported across heterogeneous comparisons; offline supernet/search training is not included in the inference-cost ratio and no single matched cell establishes both extrema simultaneously.

## Mathematical content

The method optimizes expected task utility under a stochastic architecture distribution with a cost penalty or constraint; continuous relaxations estimate gradients over discrete structures, but no optimality or calibration theorem is given.

## Evidence quality and limitations

Offline optimization cost is separated from inference cost, comparators have different architecture spaces, query difficulty may correlate with benchmark identity, and transfer is demonstrated on limited related datasets/models.

## Important implementation details

Construct an overcomplete agent graph, learn query-conditioned routing and operation weights, sample/derive a sparse realized graph per input, and trade task reward against model/tool/token resource use.

## Claims this source supports

Dynamic harnesses can allocate computation by input rather than deploy a single maximal workflow.

## Claims this source weakens or contradicts

Cost-efficiency headlines are incomplete without amortizing supernet training and controlling architecture search space and model calls.

## Relevance to a mathematics paper

Offers a constrained stochastic-network optimization formulation for quality-cost Pareto analysis and conditional computation.

## Connections to other sources

See the category and claim-level cross-references in [`INDEX.md`](INDEX.md) and the synthesis documents.

## Verification notes

Local PDF abstract, problem formulation, training method, main performance/cost tables, transfer studies, and limitations were checked; reported ranges were not independently recomputed. The archived file parsed successfully: 19 pages, 70493 extractable characters, SHA-256 `1f7a580667049d3f7ac879c9ef9b3d206e22ae5f52ee18ab1b52fe0b312bc0b0`.
