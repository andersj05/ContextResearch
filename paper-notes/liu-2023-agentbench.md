---
title: "AgentBench: Evaluating LLMs as Agents"
authors: ["Xiao Liu", "Hao Yu", "Hanchen Zhang", "Yifan Xu", "Xuanyu Lei", "Hanyu Lai", "Yu Gu", "Hangliang Ding", "Kaiwen Men", "Kejuan Yang", "Shudan Zhang", "Xiang Deng", "Aohan Zeng", "Zhengxiao Du", "Chenhui Zhang", "Sheng Shen", "Tianjun Zhang", "Yu Su", "Huan Sun", "Minlie Huang", "Yuxiao Dong", "Jie Tang"]
year: 2023
venue: "ICLR-2024"
source_type: "peer-reviewed"
paper_url: "https://arxiv.org/abs/2308.03688"
pdf_path: "papers/academic/liu-2023-agentbench.pdf"
accessed: "2026-09-04"
review_status: "skimmed"
evidence_confidence: "medium"
---

# liu-2023-agentbench — AgentBench: Evaluating LLMs as Agents

## Why this source is in the corpus

Makes model–harness–environment coupling observable in executable, long-horizon tasks.

## Research question

How can agent behavior be compared across diverse interactive environments?

## Harness mechanism studied

AgentBench wraps operating-system, database, knowledge-graph, game, household, shopping, and web environments behind a unified interaction and scoring layer.

## Method and experimental setup

ICLR 2024 benchmark evaluating 29 API and open-source models in eight environments with per-environment scores and failure analysis.

## Main findings

- Commercial systems substantially outperform the tested open models, while long-term reasoning, decision making, and instruction following dominate observed failures.
- Code-oriented training has mixed effects across agent tasks rather than a uniformly positive effect.

## Mathematical content

The aggregate score is a weighted combination of heterogeneous task metrics; it should not be treated as a natural single-scale measurement without sensitivity analysis.

## Evidence quality and limitations

Environments, prompts, model APIs, and scoring units differ; versions are dated; aggregation can hide opposite per-domain effects; harness configuration is not held constant across all models.

## Important implementation details

Report every environment score, normalization and weight, prompt/action parser, timeout, invalid-action handling, and model snapshot instead of only the aggregate.

## Claims this source supports

Broad evaluation needs multiple interactive domains and failure-level evidence.

## Claims this source weakens or contradicts

One scalar leaderboard score as a stable or causally interpretable measure of general agency.

## Relevance to a mathematics paper

Supports multilevel models and rank-sensitivity analysis across heterogeneous domains.

## Connections to other sources

See the category and claim-level cross-references in [`INDEX.md`](INDEX.md) and the synthesis documents.

## Verification notes

Abstract and benchmark sections checked for eight environments, 29 models, failure taxonomy, aggregate construction, and limitations. The archived file parsed successfully: 58 pages, 176073 extractable characters, SHA-256 `9c780e35fc0b2de6c2e21e0572f6aaaadcf7ecdd56d63cfaae2b415bc0dc83c3`.
