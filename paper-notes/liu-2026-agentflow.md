---
title: "Synthesizing Multi-Agent Harnesses for Vulnerability Discovery"
authors: ["Hanzhi Liu", "Chaofan Shou", "Xiaonan Liu", "Hongbo Wen", "Yanju Chen", "Ryan Jingyang Fang", "Yu Feng"]
year: 2026
venue: "preprint"
source_type: "preprint"
paper_url: "https://arxiv.org/abs/2604.20801"
pdf_path: "papers/academic/liu-2026-agentflow.pdf"
accessed: "2026-09-04"
review_status: "fully-reviewed"
evidence_confidence: "medium"
---

# liu-2026-agentflow — Synthesizing Multi-Agent Harnesses for Vulnerability Discovery

## Why this source is in the corpus

Directly treats the harness, its optimization, or its runtime semantics as the object of study.

## Research question

Can typed multi-agent harness search use runtime failure signals to improve vulnerability discovery?

## Harness mechanism studied

A typed graph DSL spans roles, prompts, tools, communication topology, and retry protocol; an outer loop rewrites the graph from instrumented program feedback.

## Method and experimental setup

TerminalBench-2 with Claude Opus 4.6 and a Chrome vulnerability campaign with Kimi K2.5; synthesis trajectory, ablations, and disclosure results.

## Main findings

- AgentFlow reports 75 of 89 TerminalBench-2 tasks, or 84.3%, 2.9 points above the strongest cited hand-engineered entry.
- It reports ten previously unknown Chrome vulnerabilities, including disclosed critical sandbox escapes.

## Mathematical content

Harness search is program optimization over a typed graph; the paper reports ablations but no search-optimality guarantee.

## Evidence quality and limitations

Security claims are high stakes, leaderboard snapshot and models can change, discovery campaign lacks a randomized counterfactual, and the preprint is new.

## Important implementation details

Type-check generated graphs, ground feedback in program instrumentation, retain a full edit trajectory, and use independent disclosure confirmation.

## Claims this source supports

Runtime diagnostics can be more informative than scalar reward for harness synthesis.

## Claims this source weakens or contradicts

One successful security campaign as a general causal estimate for multi-agent architecture.

## Relevance to a mathematics paper

Connects typed graph search, causal failure attribution, and expensive black-box optimization.

## Connections to other sources

See the category and claim-level cross-references in [`INDEX.md`](INDEX.md) and the synthesis documents.

## Verification notes

Abstract, DSL, synthesis loop, TerminalBench Table 1, Chrome Table 2, disclosure notes, and limitations checked in the local PDF. The archived file parsed successfully: 14 pages, 82431 extractable characters, SHA-256 `896f1e7b49bacbb567aa2d4cad74db0afed738982b3863743f20cffed47d2ec7`.
