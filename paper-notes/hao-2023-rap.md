---
title: "Reasoning with Language Model is Planning with World Model"
authors: ["Shibo Hao", "Yi Gu", "Haodi Ma", "Joshua Jiahua Hong", "Zhen Wang", "Daisy Zhe Wang", "Zhiting Hu"]
year: 2023
venue: "EMNLP-2023"
source_type: "peer-reviewed"
paper_url: "https://arxiv.org/abs/2305.14992"
pdf_path: "papers/academic/hao-2023-rap.pdf"
accessed: "2026-09-04"
review_status: "fully-reviewed"
evidence_confidence: "medium"
---

# hao-2023-rap — Reasoning with Language Model is Planning with World Model

## Why this source is in the corpus

Supports analysis of inference-time search, feedback, stopping, and verifier error.

## Research question

Can a frozen LLM act as both world model and policy inside Monte Carlo tree search?

## Harness mechanism studied

MCTS expands LLM-proposed actions and predicted next states using likelihood, confidence, self-evaluation, and task heuristics as reward.

## Method and experimental setup

Blocksworld, logical reasoning, and plan generation compare RAP search with prompting and reasoning baselines.

## Main findings

- For Blocksworld at 2, 4, and 6 steps, RAP-20 reports 1.00, 0.88, and 0.42 versus GPT-4 CoT at 0.50, 0.63, and 0.40.
- The abstract's 33% relative gain applies to plan generation and depends on engineered rewards.

## Mathematical content

MCTS uses selection, expansion, simulation, and backpropagation; reward is a weighted mixture of model probabilities and task signals.

## Evidence quality and limitations

The LLM world model is not calibrated, rewards expose task knowledge, search is expensive, and tasks are small or symbolic.

## Important implementation details

Separate transition prediction, value estimation, task heuristics, and search budget in any ablation.

## Claims this source supports

World-model-guided search is a plausible harness mechanism for planning.

## Claims this source weakens or contradicts

The label planning as evidence of a task-general or accurate world model.

## Relevance to a mathematics paper

Supplies a control and MCTS formulation with measurable model and heuristic errors.

## Connections to other sources

See the category and claim-level cross-references in [`INDEX.md`](INDEX.md) and the synthesis documents.

## Verification notes

Blocksworld tables, reward definition, MCTS algorithm, computation settings, and limitations checked in the local PDF. The archived file parsed successfully: 20 pages, 74893 extractable characters, SHA-256 `3babff1eb4eb47d19dd9eb5a5bb11d433c34370e308c0be9ad75ea7d8ab76dfe`.
