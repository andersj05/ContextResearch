---
title: "AI Agents That Matter"
authors: ["Sayash Kapoor", "Benedikt Stroebl", "Zachary S. Siegel", "Nitya Nadgir", "Arvind Narayanan"]
year: 2024
venue: "preprint"
source_type: "preprint"
paper_url: "https://arxiv.org/abs/2407.01502"
pdf_path: "papers/academic/kapoor-2024-agents-matter.pdf"
accessed: "2026-09-04"
review_status: "fully-reviewed"
evidence_confidence: "high"
---

# kapoor-2024-agents-matter — AI Agents That Matter

## Why this source is in the corpus

Makes model–harness–environment coupling observable in executable, long-horizon tasks.

## Research question

What evaluation practices distinguish useful agents from benchmark-optimized demonstrations?

## Harness mechanism studied

The paper treats accuracy and cost jointly, introduces simple repeated-sampling baselines, separates model-developer from downstream evaluation, and audits holdouts and reproducibility.

## Method and experimental setup

TMLR 2025 analysis with public reruns on HumanEval and HotpotQA, cost-Pareto methods, and audits of agent benchmarks.

## Main findings

- Across five runs on 164 HumanEval problems, LATS reaches 88.0% at 134.50 dollars while simple temperature warming reaches 93.2% at 2.45 dollars; the accuracy difference is not significant.
- LATS costs more than fifty times as much, and seven of 17 surveyed benchmarks lack holdouts.

## Mathematical content

A system is Pareto-dominated if another has at least its accuracy and no greater cost with one strict inequality; randomized mixtures convexify achievable accuracy-cost points.

## Evidence quality and limitations

HumanEval is short and public; costs depend on historical API prices; reruns may differ from authors' private setups; conclusions do not automatically extend to long stateful tasks.

## Important implementation details

Report fixed optimization cost and variable inference cost, use compute-matched simple baselines, hold out at the level of claimed generality, and release standardized code and logs.

## Claims this source supports

Cost control and sampling baselines are essential before crediting an agent architecture.

## Claims this source weakens or contradicts

Leaderboard accuracy alone as proof that search, reflection, or architecture caused improvement.

## Relevance to a mathematics paper

Provides the core Pareto and randomized-mixture mathematics for harness comparison.

## Connections to other sources

See the category and claim-level cross-references in [`INDEX.md`](INDEX.md) and the synthesis documents.

## Verification notes

Sections 2-6 and Appendix A checked for five-run protocol, 164 tasks, 88.0 and 93.2 results, 134.50 and 2.45 costs, holdout audit, formulas, and limitations. The archived file parsed successfully: 33 pages, 115819 extractable characters, SHA-256 `1681013e0421f9d193ca5bb556b566f50d1e5eaa43d7a9700a31ca3dd0e2ff7a`.
