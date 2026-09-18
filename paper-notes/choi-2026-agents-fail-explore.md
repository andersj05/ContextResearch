---
title: "Multi-Agent LLMs Fail to Explore Each Other"
authors: ["Hyeong Kyu Choi", "Jiatong Li", "Wendi Li", "Xin Eric Wang", "Sharon Li"]
year: 2026
venue: "preprint"
source_type: "preprint"
paper_url: "https://arxiv.org/abs/2607.11250"
pdf_path: "papers/academic/choi-2026-agents-fail-explore.pdf"
accessed: "2026-09-04"
review_status: "fully-reviewed"
evidence_confidence: "medium"
---

# choi-2026-agents-fail-explore — Multi-Agent LLMs Fail to Explore Each Other

## Why this source is in the corpus

Provides communication, aggregation, or coordination mechanisms and their compute-matched counterevidence.

## Research question

Can structured peer exploration reduce regret when agents have heterogeneous capabilities?

## Harness mechanism studied

MACE uses an upper-confidence-style peer-selection policy to balance exploration of uncertain peers and exploitation of successful ones.

## Method and experimental setup

Partially observable stochastic-game formulation, HotpotQA contextual diversity, Math500 and GPQA parametric diversity, baselines, and regret proofs.

## Main findings

- Naive agents commit early or polarize, while MACE improves downstream metrics in heterogeneous settings.
- The benefit shrinks as capability diversity approaches zero.

## Mathematical content

Under stated assumptions MACE has order sqrt(T log T) cumulative regret, while a greedy non-exploring policy has Omega(delta T) regret where delta measures pool diversity.

## Evidence quality and limitations

Bandit assumptions simplify language interaction and reward stationarity; very recent preprint; empirical reward uses model- or task-specific scoring.

## Important implementation details

Track peer uncertainty and capability, use an explicit exploration coefficient, and separate exploration from final exploitation.

## Claims this source supports

Multi-agent orchestration has an exploration-exploitation problem, not only a communication problem.

## Claims this source weakens or contradicts

Prompting agents to interact as sufficient for efficient information discovery.

## Relevance to a mathematics paper

Provides the strongest regret-theoretic bridge from harness routing to bandits.

## Connections to other sources

See the category and claim-level cross-references in [`INDEX.md`](INDEX.md) and the synthesis documents.

## Verification notes

Theorems 1-2, Corollary 1, assumptions, regret figures, diversity experiments, and limitations checked in the local PDF. The archived file parsed successfully: 52 pages, 144176 extractable characters, SHA-256 `b6157ae2cdac52c1da59014ed12935212f59f40add913dd88db902ef575149c6`.
