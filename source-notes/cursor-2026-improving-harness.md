---
title: "Continually Improving Our Agent Harness"
author_or_org: "Stefan Heule and Jediah Katz / Cursor"
date: "2026-04-30"
source_type: "engineering-blog"
url: "https://cursor.com/blog/continually-improving-agent-harness"
version_or_commit: "web version accessed 2026-09-04"
accessed: "2026-09-04"
review_status: "reviewed"
evidence_confidence: "medium"
---

# cursor-2026-improving-harness — Continually Improving the Cursor Harness

## Why this source is in the corpus

This post describes a mature product loop that combines offline benchmarks, online randomized variants, retention signals, semantic user feedback, error taxonomy, and model-specific tool interfaces.

## System or claim described

Cursor treats each model-harness pairing as an independently tuned product. Candidate changes are evaluated with public benchmarks, CursorBench, real-usage A/B tests, operational metrics, code keep rate, and a model classifier of user follow-up satisfaction.

## Architecture / mechanism

The team tracks latency, token use, tool calls, cache hits, expected and unknown tool errors, user aborts, and timeouts. Per-tool and per-model baselines trigger anomaly alerts. A scheduled agent mines logs and creates or updates investigation tickets. Tool schemas are adapted to model training conventions—for example, patch editing versus string replacement—and prompts can mitigate model-specific context behavior.

## Empirical evidence

The post says a focused reliability effort reduced unexpected tool errors by an order of magnitude and brought all tool calls to at least two, often three, nines of reliability. It also reports shelving a more expensive summarizer after negligible online quality change. Exact samples, intervals, and causal estimators are not published.

## Mathematical or formal content

Keep rate is a delayed survival or retention outcome for generated code. Online harness comparison is an experiment over users or sessions and must handle interference, repeated users, task mix, and delayed outcomes. Operational error control benefits from per-model control charts rather than one global threshold.

## What is directly evidenced

The page exposes the measurement stack, error taxonomy, model-specific edit examples, improvement workflow, and reported internal observations.

## What is interpretation or advocacy

Code retention is only a proxy for correctness and value; users may retain poor code or replace good code during refactoring. A model classifier of satisfaction requires calibration and can inherit provider bias.

## Limitations, incentives, and likely biases

CursorBench, assignment rules, sample sizes, effects, and costs are mostly private. Product users self-select. The company benefits from claiming strong harness tuning. Multi-agent future claims are forecasts, not results.

## Transferable engineering lessons

Combine offline and online evidence, use durable user outcomes rather than only tool counts, stratify failures by model and tool, treat unknown errors as harness bugs, and never compare models without their actual production tool formats.

## Connections to academic work

The practice connects to HarnessBench, HAL, factorial model-harness analysis, context compaction studies, online experimentation, and cost-Pareto evaluation.

## Verification notes

The canonical page's measurement, keep-rate, error classification, automated diagnosis, per-model tuning, model-switching, and future-orchestration sections were checked on 2026-09-04.
