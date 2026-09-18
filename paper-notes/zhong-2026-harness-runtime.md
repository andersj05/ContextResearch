---
title: "AI Harness Engineering: A Runtime Substrate for Foundation-Model Software Agents"
authors: ["Hailin Zhong", "Shengxin Zhu"]
year: 2026
venue: "preprint"
source_type: "preprint"
paper_url: "https://arxiv.org/abs/2605.13357"
pdf_path: "papers/academic/zhong-2026-harness-runtime.pdf"
accessed: "2026-09-04"
review_status: "skimmed"
evidence_confidence: "medium"
---

# zhong-2026-harness-runtime — AI Harness Engineering: A Runtime Substrate for Foundation-Model Software Agents

## Why this source is in the corpus

Directly treats the harness, its optimization, or its runtime semantics as the object of study.

## Research question

What runtime responsibilities are required for verifiable software-agent work?

## Harness mechanism studied

Eleven responsibilities and an H0-H3 ladder that progressively adds context, evidence, attribution, verification, and intervention records.

## Method and experimental setup

The framework is applied to a controlled validation task and compares the evidence structure of episode packages at successive harness levels.

## Main findings

- Higher levels produce reproduction logs, failure attribution, deterministic requirement checks, and structured verification rather than only a final patch.
- The study demonstrates auditability artifacts, not a broad task-success improvement.

## Mathematical content

A run can be modeled as a trace-valued transition system; the ladder is an ordinal architecture scale, not a validated interval metric.

## Evidence quality and limitations

Two-author preprint, narrow validation task, and no randomized performance comparison.

## Important implementation details

Store each run as a versioned episode package containing inputs, actions, observations, changes, checks, and interventions.

## Claims this source supports

Correctness evidence and failure attribution are first-class harness outputs.

## Claims this source weakens or contradicts

Patch production alone as evidence that an issue is solved.

## Relevance to a mathematics paper

Motivates trace semantics and evidence-valued outcomes rather than binary reward alone.

## Connections to other sources

See the category and claim-level cross-references in [`INDEX.md`](INDEX.md) and the synthesis documents.

## Verification notes

Abstract, eleven responsibilities, H0-H3 ladder, validation task, and conclusion checked in the local PDF. The archived file parsed successfully: 16 pages, 50376 extractable characters, SHA-256 `a1e2d7ce307c662411ca6bd5f833d7dae7f122ce6ef1ddd6d2370e82575b2fb9`.
