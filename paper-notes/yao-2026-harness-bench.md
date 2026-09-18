---
title: "Harness-Bench: Measuring Harness Effects across Models in Realistic Agent Workflows"
authors: ["Yilun Yao", "Xinyu Tan", "Chao-Hsuan Liu", "Yaoming Li", "Zhengyang Wang", "Wenhan Yu", "Zhewen Tan", "Yuxuan Tian", "Guangxiang Zhao", "Lin Sun", "Xiangzheng Zhang", "Tong Yang"]
year: 2026
venue: "preprint"
source_type: "preprint"
paper_url: "https://arxiv.org/abs/2605.27922"
pdf_path: "papers/academic/yao-2026-harness-bench.pdf"
accessed: "2026-09-04"
review_status: "fully-reviewed"
evidence_confidence: "medium"
---

# yao-2026-harness-bench — Harness-Bench: Measuring Harness Effects across Models in Realistic Agent Workflows

## Why this source is in the corpus

Directly treats the harness, its optimization, or its runtime semantics as the object of study.

## Research question

How much do harness configurations change outcomes when tasks, budgets, validators, and environments are shared?

## Harness mechanism studied

A diagnostic execution layer records native harness behavior, artifacts, traces, constraints, permissions, usage, and recovery.

## Method and experimental setup

106 manually reviewed sandboxed offline tasks, multiple model backends and harness configurations, and 5,194 trajectories under common protocols.

## Main findings

- Substantial completion, process-quality, efficiency, and failure-mode variation appears across model-harness pairings.
- The design supports reporting a pairing rather than attributing the joint score to the base model.

## Mathematical content

The natural analysis is a model-by-harness interaction matrix with task blocking and shared budgets; the paper is mainly empirical and does not establish a universal effect law.

## Evidence quality and limitations

New preprint, only 106 constructed tasks, incomplete factorial coverage, and native behavior complicates strict treatment equivalence.

## Important implementation details

Preserve native execution but normalize task state, budgets, validation, telemetry, and final artifacts.

## Claims this source supports

Harness choice is an empirically material treatment variable.

## Claims this source weakens or contradicts

Cross-paper model rankings that omit harness configuration.

## Relevance to a mathematics paper

Directly motivates blocked factorial estimation of model, harness, and interaction effects.

## Connections to other sources

See the category and claim-level cross-references in [`INDEX.md`](INDEX.md) and the synthesis documents.

## Verification notes

Abstract, task construction, common protocol, 5,194-trajectory scope, metrics, and limitations checked in the local PDF. The archived file parsed successfully: 16 pages, 53725 extractable characters, SHA-256 `859570aa22270af5203be6042595cce1add19dcef2976db748550462ceb2709e`.
