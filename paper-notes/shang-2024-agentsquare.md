---
title: "AgentSquare: Automatic LLM Agent Search in Modular Design Space"
authors: ["Yu Shang", "Yu Li", "Keyu Zhao", "Likai Ma", "Jiahe Liu", "Fengli Xu", "Yong Li"]
year: 2024
venue: "ICLR-2025"
source_type: "peer-reviewed"
paper_url: "https://arxiv.org/abs/2410.06153"
pdf_path: "papers/academic/shang-2024-agentsquare.pdf"
accessed: "2026-09-04"
review_status: "skimmed"
evidence_confidence: "high"
---

# shang-2024-agentsquare — AgentSquare: Automatic LLM Agent Search in Modular Design Space

## Why this source is in the corpus

Directly studies reusable harness components, outer-loop optimization, self-modification, or the statistical controls needed to decide whether an update is a real improvement.

## Research question

Can modular agent components be recombined automatically to discover better agent systems across heterogeneous environments?

## Harness mechanism studied

An agent is factored into planning, reasoning, tool-use, and memory modules; search composes catalogued module implementations and scores complete agents.

## Method and experimental setup

AgentSquare builds a component library from prior agents, uses a surrogate-assisted search procedure to propose tuples A=(P,R,T,M), evaluates them on six benchmarks, and studies transfer and module choices.

## Main findings

- Table 1 reports AgentSquare scores 0.607/0.695/0.781/0.524/0.583/0.669 on WebShop/ALFWorld/SciWorld/M3Tool/TravelPlanner/PDDL versus ADAS 0.521/0.543/0.754/0.475/0.373/0.568.
- The search starts from human-engineered modules and uses a surrogate and extra evaluations whose cost is excluded from the task scores, so results support recombination within a curated space rather than autonomous invention.

## Mathematical content

The formal problem is argmax over the Cartesian product P×R×T×M of an empirical evaluator; the surrogate estimates candidate value but the paper proves no regret or generalization bound.

## Evidence quality and limitations

Component boundaries and implementations are manually curated, benchmark metrics are heterogeneous, optimization budgets and inference calls differ, and module interactions make marginal attribution difficult.

## Important implementation details

Index existing planning, reasoning, tool, and memory modules; encode each candidate as a four-part tuple; use predicted and observed performance to choose evaluations; retain the best configuration per domain.

## Claims this source supports

Modular harness interfaces create a tractable architecture-search space and can outperform whole-program search in several environments.

## Claims this source weakens or contradicts

The result does not show that automatically generated modules are better or that the discovered tuple remains best under a new model, budget, or environment.

## Relevance to a mathematics paper

A factorial discrete-design formulation makes component interactions, surrogate error, and multiple-comparison corrections explicit.

## Connections to other sources

See the category and claim-level cross-references in [`INDEX.md`](INDEX.md) and the synthesis documents.

## Verification notes

Local PDF formal tuple, search algorithm, Table 1, component and transfer analyses, and limitations were checked; no independent evaluation was run. The archived file parsed successfully: 25 pages, 85220 extractable characters, SHA-256 `5d83a6ba6a64a1b79364200a98a733fbaa32e9dad826ffe7b8433a9e9d0aa57a`.
