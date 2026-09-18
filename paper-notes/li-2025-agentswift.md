---
title: "AgentSwift: Efficient LLM Agent Design via Value-guided Hierarchical Search"
authors: ["Yu Li", "Lehui Li", "Zhihao Wu", "Qingmin Liao", "Jianye Hao", "Kun Shao", "Fengli Xu", "Yong Li"]
year: 2025
venue: "AAAI-2026"
source_type: "peer-reviewed"
paper_url: "https://arxiv.org/abs/2506.06017"
pdf_path: "papers/academic/li-2025-agentswift.pdf"
accessed: "2026-09-04"
review_status: "skimmed"
evidence_confidence: "medium"
---

# li-2025-agentswift — AgentSwift: Efficient LLM Agent Design via Value-guided Hierarchical Search

## Why this source is in the corpus

Directly studies reusable harness components, outer-loop optimization, self-modification, or the statistical controls needed to decide whether an update is a real improvement.

## Research question

Can hierarchical search jointly optimize workflow topology and the prompts, tools, memory, and model choice inside each agent node?

## Harness mechanism studied

A hierarchical design space represents nodes as model/prompt/tool/memory tuples and workflows as graphs; uncertainty-aware MCTS uses a learned value model to choose expensive evaluations.

## Method and experimental setup

AgentSwift trains or fits a surrogate over prior candidate evaluations, predicts mean and uncertainty, explores node and graph edits through MCTS, and evaluates selected architectures on seven reasoning, embodied, and tool-use benchmarks.

## Main findings

- The abstract reports an average +8.34% improvement across seven benchmarks; Table 2 reports surrogate R² 0.8068/0.8275 and Spearman 0.9026/0.8987 for two AgentSwift variants versus vanilla R² -4.059 and Spearman 0.2467.
- These are source-reported and the contribution of richer search space cannot be separated from surrogate quality, MCTS budget, or curated component primitives.

## Mathematical content

A node is (M_i,P_i,tau_i,F_i) and a workflow is (N,E); selection uses a value estimate plus uncertainty within an MCTS/upper-confidence allocation rule, without a finite-sample regret guarantee for this learned surrogate.

## Evidence quality and limitations

The component library constrains novelty, value-model data and evaluation budgets influence results, benchmark-specific search is costly, and no sealed reuse experiment proves persistent benefit on future distributions.

## Important implementation details

Define typed components and graph edits, learn candidate-value and uncertainty predictions, expand a two-level MCTS over node and workflow choices, fully execute promising candidates, and retain a Pareto or best-performing design.

## Claims this source supports

Joint co-search can cover more harness degrees of freedom while using a surrogate to ration expensive evaluations.

## Claims this source weakens or contradicts

Headline averages do not identify which edited artifact matters or establish superiority to simpler prompt or topology search at matched total cost.

## Relevance to a mathematics paper

Directly maps to hierarchical Bayesian/sequential optimization; surrogate calibration and selection bias are measurable mathematical failure points.

## Connections to other sources

See the category and claim-level cross-references in [`INDEX.md`](INDEX.md) and the synthesis documents.

## Verification notes

Local PDF abstract, formal design space, search algorithm, primary Table 1, surrogate Table 2, ablations, transfer analysis, and limitations were checked; no experiments rerun. The archived file parsed successfully: 18 pages, 71281 extractable characters, SHA-256 `4b47a70e925262a1b7441fb22318047725976d3f5adceb4265805d1fb884293a`.
