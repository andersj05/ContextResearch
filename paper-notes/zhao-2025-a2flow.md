---
title: "A2Flow: Automating Agentic Workflow Generation via Self-Adaptive Abstraction Operators"
authors: ["Mingming Zhao", "Xiaokang Wei", "Yuanqi Shao", "Kaiwen Zhou", "Lin Yang", "Siwei Rao", "Junhui Zhan", "Zhitang Chen"]
year: 2025
venue: "AAAI-2026"
source_type: "peer-reviewed"
paper_url: "https://arxiv.org/abs/2511.20693"
pdf_path: "papers/academic/zhao-2025-a2flow.pdf"
accessed: "2026-09-04"
review_status: "skimmed"
evidence_confidence: "high"
---

# zhao-2025-a2flow — A2Flow: Automating Agentic Workflow Generation via Self-Adaptive Abstraction Operators

## Why this source is in the corpus

Directly studies reusable harness components, outer-loop optimization, self-modification, or the statistical controls needed to decide whether an update is a real improvement.

## Research question

Can workflow search improve by first mining reusable operators from expert demonstrations?

## Harness mechanism studied

An operator miner turns expert traces into parameterized modules with prompt, memory, and function structure; AFlow then searches compositions of those modules.

## Method and experimental setup

A2Flow extracts and validates operators from demonstrations, instantiates them as o_k=f_k(input,P,M), runs workflow search, and evaluates general reasoning, code, and embodied tasks against AFlow and other baselines.

## Main findings

- The abstract reports +2.4 points on general tasks, +19.3 on embodied tasks, and 37% lower resource use; relative to AFlow it reports +4.5 on DROP and +4.1 on MATH, with HumanEval an exception.
- Because operators are mined from expert demonstrations and search cost is excluded from runtime efficiency, the result is guided library construction rather than from-scratch self-building.

## Mathematical content

Operators are functions o_k=f_k(x,P_k,M_k), and workflow search maximizes empirical task score over their compositions; no bound connects demonstration coverage to operator completeness or out-of-sample gain.

## Evidence quality and limitations

Expert demonstrations and human-chosen extraction schemas carry substantial prior knowledge, one benchmark exception is reported, offline mining/search cost is not fully amortized, and transfer beyond the benchmark families is limited.

## Important implementation details

Parse expert trajectories into reusable operator candidates, validate and deduplicate them, expose a typed operator library, run AFlow-style composition search, and deploy the selected workflow.

## Claims this source supports

Reusable mid-level operators can make architecture search more effective and resource-efficient than a fixed generic vocabulary.

## Claims this source weakens or contradicts

Weakens claims that workflow optimizers discover capabilities autonomously; expert traces and library quality are load-bearing, and improvement is not universal.

## Relevance to a mathematics paper

Suggests a two-stage optimization with library-estimation error plus composition-search error and an explicit amortization problem.

## Connections to other sources

See the category and claim-level cross-references in [`INDEX.md`](INDEX.md) and the synthesis documents.

## Verification notes

Local PDF formal operator definition, extraction/search algorithms, main result tables, AFlow comparisons including HumanEval, resource analysis, and limitations were checked; no replication was run. The archived file parsed successfully: 19 pages, 69458 extractable characters, SHA-256 `57dd3d938c69f60ff006f61fc5e78ace6fb72ee0a5ccad191fcd5263a75931ca`.
