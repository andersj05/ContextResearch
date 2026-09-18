---
title: "Debate or Vote: Which Yields Better Decisions in Multi-Agent Large Language Models?"
authors: ["Hyeong Kyu Choi", "Xiaojin Zhu", "Sharon Li"]
year: 2025
venue: "NeurIPS-2025"
source_type: "peer-reviewed"
paper_url: "https://papers.nips.cc/paper_files/paper/2025/hash/934252acd87f254d5d4672fbde283bd2-Abstract-Conference.html"
pdf_path: "papers/academic/choi-2025-debate-or-vote.pdf"
accessed: "2026-09-04"
review_status: "fully-reviewed"
evidence_confidence: "high"
---

# choi-2025-debate-or-vote — Debate or Vote: Which Yields Better Decisions in Multi-Agent Large Language Models?

## Why this source is in the corpus

Provides communication, aggregation, or coordination mechanisms and their compute-matched counterevidence.

## Research question

Do debate messages add expected correctness beyond majority voting?

## Harness mechanism studied

Five agents either vote independently or update beliefs through centralized, decentralized, or sparse debate for multiple rounds.

## Method and experimental setup

Seven benchmarks, Qwen2.5-7B and Llama3.1-8B, two to five rounds, a Dirichlet-Categorical belief model, and targeted correction interventions.

## Main findings

- Qwen majority averages 0.7691 versus best debate 0.7377; Llama majority 0.7242 versus best debate 0.6990; more rounds often worsen results.
- The theory explains ordinary homogeneous debate as a martingale unless updates are directionally biased.

## Mathematical content

If Delta separates the top two expected beliefs and N>K/Delta^2, a majority-vote lower bound is given; under matching expected neighbor belief, debate beliefs form a martingale.

## Evidence quality and limitations

The belief-update model idealizes natural language, only two open models, and targeted interventions depend on identifying correction direction.

## Important implementation details

Use voting as baseline, measure belief transitions, and require an asymmetric evidence mechanism before paying for rounds.

## Claims this source supports

Simple ensembling is often stronger than unconstrained debate.

## Claims this source weakens or contradicts

Debate itself as a source of positive expected drift.

## Relevance to a mathematics paper

Provides peer-reviewed majority bounds and a martingale theorem directly relevant to a math paper.

## Connections to other sources

See the category and claim-level cross-references in [`INDEX.md`](INDEX.md) and the synthesis documents.

## Verification notes

Table 1, Theorems 1-2 and assumptions, round ablations, interventions, and limitations checked in the local PDF. The archived file parsed successfully: 33 pages, 100607 extractable characters, SHA-256 `0a731f56e50d0fcee9a191e58f586b88d1c7084e75de5f1990b5a103986c0b56`.
