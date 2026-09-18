---
title: "Automated Design of Agentic Systems"
authors: ["Shengran Hu", "Cong Lu", "Jeff Clune"]
year: 2024
venue: "ICLR-2025"
source_type: "peer-reviewed"
paper_url: "https://arxiv.org/abs/2408.08435"
pdf_path: "papers/academic/hu-2024-adas.pdf"
accessed: "2026-09-04"
review_status: "skimmed"
evidence_confidence: "high"
---

# hu-2024-adas — Automated Design of Agentic Systems

## Why this source is in the corpus

Directly studies reusable harness components, outer-loop optimization, self-modification, or the statistical controls needed to decide whether an update is a real improvement.

## Research question

Can a meta-agent automatically discover new agent programs by searching an open-ended code space?

## Harness mechanism studied

A meta-agent mutates executable Python agent code, retrieves inspirations from an archive of prior programs and scores, and preserves high-performing discoveries.

## Method and experimental setup

Meta Agent Search iteratively samples code-defined agent systems, executes them on development tasks, stores code/performance in an archive, and evaluates selected designs and transfer under fixed executor models.

## Main findings

- Table 1 reports CoT 64.2/28.0/65.4/29.2 and prompt optimization 69.1/30.6/67.6/32.9 versus Meta Agent Search 79.4/53.4/69.6/34.6 on DROP/MGSM and transfer settings; this is +13.6 DROP F1 and +14.4 MGSM points over the listed baselines.
- Transfer gains include +25.9 on GSM8K and +13.2 on GSM-Hard, but search cost, unrestricted code generation, archive reuse, and benchmark contamination are not ruled out, and the domains are mostly short-answer reasoning.

## Mathematical content

The target is A-star in argmax_A E_{x~D}[s(A(x),y)] over executable programs; the implemented archive-guided stochastic search has no completeness, optimality, or generalization theorem.

## Evidence quality and limitations

Open-ended code is unsafe and hard to normalize for compute; the meta-agent sees repeated development feedback; comparisons mix search spaces and budgets; confidence intervals cover sampling but not adaptive selection bias.

## Important implementation details

Seed an archive with hand-written agents, prompt the meta-agent with archive exemplars, generate executable code mutations, sandbox and score them, append viable programs, and transfer the selected program without retraining.

## Claims this source supports

Whole-agent code and control flow can be optimized, and archived designs can transfer across related tasks.

## Claims this source weakens or contradicts

The paper does not establish autonomous open-ended improvement or fair superiority over constrained workflow search once search and inference budgets are equalized.

## Relevance to a mathematics paper

Formalizes agent design as black-box program optimization and motivates complexity, safety, and adaptive-validation penalties on the search objective.

## Connections to other sources

See the category and claim-level cross-references in [`INDEX.md`](INDEX.md) and the synthesis documents.

## Verification notes

Local PDF abstract, formal problem, algorithm, Table 1, bootstrap confidence-interval note, transfer study, and limitations were checked; values were not reproduced. The archived file parsed successfully: 34 pages, 117310 extractable characters, SHA-256 `32eb1c1a6888e35fae0f618e33c58698b54d9c49bc063fef91ee591719fca376`.
