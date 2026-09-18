---
title: "HarnessDev: Can LLMs Create and Evolve Their Own Agent Harness?"
authors: ["Yuhao Wu", "Jingyuan Zhang", "Jiajun Shi", "Xinping Lei", "Qingshui Gu", "Yuxuan Zhang", "Zexuan Wang", "Chen He", "Chen Huang", "Maojia Song", "Zhiyuan Zeng", "Shaowen Wang", "Jinkai Liu", "Yunfeng Shi", "Jiaheng Liu", "Shen Yan", "Wenhao Huang", "Ge Zhang", "Wenxuan Zhang"]
year: 2026
venue: "preprint"
source_type: "preprint"
paper_url: "https://arxiv.org/abs/2609.01437"
pdf_path: "papers/academic/wu-2026-harnessdev.pdf"
accessed: "2026-09-04"
review_status: "fully-reviewed"
evidence_confidence: "medium"
---

# wu-2026-harnessdev — HarnessDev: Can LLMs Create and Evolve Their Own Agent Harness?

## Why this source is in the corpus

Directly treats the harness, its optimization, or its runtime semantics as the object of study.

## Research question

Can models create runnable harnesses and then improve them without overfitting?

## Harness mechanism studied

Creation from a weak seed followed by feedback-driven evolution; capability is measured on held-out tasks and efficiency by executor-model tokens.

## Method and experimental setup

Six creator models, four domains, five downstream benchmarks and 2,207 unique held-out instances; fixed-runtime comparisons test transfer.

## Main findings

- Generated harnesses lag mature references on code and search or research but match or exceed selected references on writing and ML experimentation.
- Evolution gains are unstable, transfer only partially, and depend strongly on the model that later executes the harness.

## Mathematical content

A two-stage program-synthesis and black-box optimization problem with held-out utility and token cost; no convergence guarantee.

## Evidence quality and limitations

Published three days before the cutoff, many creator-executor-domain interactions, reference quality varies, and final-selection noise is substantial.

## Important implementation details

Separate creator from executor, freeze candidate code, use hidden tasks, and measure transfer across runtime models as well as cost.

## Claims this source supports

Harness creation and evolution are distinct capabilities with limited cross-model portability.

## Claims this source weakens or contradicts

Recursive self-improvement as monotone, stable, or model-independent.

## Relevance to a mathematics paper

Supports a meta-optimization formulation with transfer and generalization error.

## Connections to other sources

See the category and claim-level cross-references in [`INDEX.md`](INDEX.md) and the synthesis documents.

## Verification notes

Abstract, benchmark construction, Creation and Evolution protocols, 2,207-instance scope, held-out results, and limitations checked in the local PDF. The archived file parsed successfully: 41 pages, 129680 extractable characters, SHA-256 `1231454f0ae5ccffdb3d031dc8f42eae0cbbaeb61dcd25dddb1855074697dfc0`.
