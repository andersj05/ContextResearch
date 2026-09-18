---
title: "AgentBoard: An Analytical Evaluation Board of Multi-turn LLM Agents"
authors: ["Chang Ma", "Junlei Zhang", "Zhihao Zhu", "Cheng Yang", "Yujiu Yang", "Yaohui Jin", "Zhenzhong Lan", "Lingpeng Kong", "Junxian He"]
year: 2024
venue: "NeurIPS-2024"
source_type: "peer-reviewed"
paper_url: "https://arxiv.org/abs/2401.13178"
pdf_path: "papers/academic/ma-2024-agentboard.pdf"
accessed: "2026-09-04"
review_status: "skimmed"
evidence_confidence: "medium"
---

# ma-2024-agentboard — AgentBoard: An Analytical Evaluation Board of Multi-turn LLM Agents

## Why this source is in the corpus

Makes model–harness–environment coupling observable in executable, long-horizon tasks.

## Research question

Can evaluation expose partial progress and failure mechanisms instead of only final success?

## Harness mechanism studied

AgentBoard standardizes partially observable, multi-turn tasks and introduces progress-rate and capability diagnostics alongside success rate.

## Method and experimental setup

NeurIPS 2024 datasets paper integrating nine environments and analyzing multiple models by task difficulty, trajectory progress, and subskill.

## Main findings

- Progress rate distinguishes agents that make useful intermediate advances from those that fail immediately despite identical zero final reward.
- Diagnostic labels expose planning, grounding, memory, navigation, world-model, and self-reflection bottlenecks.

## Mathematical content

Progress is a shaped task-specific function and therefore changes the measurement construct; comparisons require checking monotonicity and scale comparability.

## Evidence quality and limitations

Intermediate milestones require author judgment and differ by environment; progress can reward detours; model and harness versions are dated; a unified dashboard does not make metrics commensurate.

## Important implementation details

Version milestone definitions, release trajectory scorers, report success and progress jointly, and test whether progress predicts independent final outcomes.

## Claims this source supports

Trace-level and partial-credit measurements can be more informative than sparse terminal reward.

## Claims this source weakens or contradicts

Treating any shaped progress score as objective or interchangeable with task success.

## Relevance to a mathematics paper

Motivates survival and multistate models over trajectories rather than one terminal Bernoulli.

## Connections to other sources

See the category and claim-level cross-references in [`INDEX.md`](INDEX.md) and the synthesis documents.

## Verification notes

Abstract, framework figure, progress-rate definition, capability analysis, included environments, and limitations checked in the local PDF. The archived file parsed successfully: 38 pages, 133303 extractable characters, SHA-256 `05299b4bd716de2769ec6f23ff358db1dbef6b2eac7a643e9e3e8eed0e62c2ef`.
