---
title: "WebArena: A Realistic Web Environment for Building Autonomous Agents"
authors: ["Shuyan Zhou", "Frank F. Xu", "Hao Zhu", "Xuhui Zhou", "Robert Lo", "Abishek Sridhar", "Xianyi Cheng", "Tianyue Ou", "Yonatan Bisk", "Daniel Fried", "Uri Alon", "Graham Neubig"]
year: 2023
venue: "ICLR-2024"
source_type: "peer-reviewed"
paper_url: "https://arxiv.org/abs/2307.13854"
pdf_path: "papers/academic/zhou-2023-webarena.pdf"
accessed: "2026-09-04"
review_status: "skimmed"
evidence_confidence: "high"
---

# zhou-2023-webarena — WebArena: A Realistic Web Environment for Building Autonomous Agents

## Why this source is in the corpus

Makes model–harness–environment coupling observable in executable, long-horizon tasks.

## Research question

Can web agents be evaluated in realistic, reproducible, stateful websites?

## Harness mechanism studied

WebArena provides self-hosted functional sites, knowledge resources, browser actions, task-specific execution evaluators, and resettable states.

## Method and experimental setup

ICLR 2024 environment and benchmark with long-horizon tasks across e-commerce, forums, software collaboration, and content management, plus human and agent baselines.

## Main findings

- The best reported GPT-4-based agent reaches 14.41% end-to-end success versus 78.24% for humans.
- Real execution exposes grounding, planning, and recovery failures not visible in static web demonstrations.

## Mathematical content

Success is a task-specific conjunction of final-state and content checks; uncertainty should be stratified by site and evaluator type.

## Evidence quality and limitations

Self-hosted replicas simplify the live web; evaluators can omit acceptable outcomes; action spaces and observation representations strongly affect results; model versions are old.

## Important implementation details

Pin site images and data, disclose observation pruning and action grammar, reset state, archive traces, and audit evaluators for alternate correct paths.

## Claims this source supports

Reproducible stateful environments are a core harness and benchmark contribution.

## Claims this source weakens or contradicts

The 14.41% result as a timeless property of GPT-4 or evidence that only the model matters.

## Relevance to a mathematics paper

Supports site-stratified Bernoulli models and conjunctive-task reliability analysis.

## Connections to other sources

See the category and claim-level cross-references in [`INDEX.md`](INDEX.md) and the synthesis documents.

## Verification notes

Abstract and benchmark sections checked for domains, evaluator design, 14.41% agent and 78.24% human results, and limitations. The archived file parsed successfully: 22 pages, 78150 extractable characters, SHA-256 `f9731b92bc3d29a2ea7b5f9cb46b48540c76bc3f84a57e0c48fc37ea73107f95`.
