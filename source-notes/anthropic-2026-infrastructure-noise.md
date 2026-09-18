---
title: "Quantifying Infrastructure Noise in Agentic Coding Evals"
author_or_org: "Anthropic"
date: "2026-02-05"
source_type: "engineering-blog"
url: "https://www.anthropic.com/engineering/infrastructure-noise"
version_or_commit: "web version accessed 2026-09-04"
accessed: "2026-09-04"
review_status: "reviewed"
evidence_confidence: "medium"
---

# anthropic-2026-infrastructure-noise — Infrastructure Noise in Coding Evals

## Why this source is in the corpus

This is direct practitioner evidence that CPU, RAM, enforcement policy, and infrastructure failures can change an agent benchmark more than reported model gaps.

## System or claim described

Runtime resources are part of the treatment in an interactive coding evaluation. Two nominally identical model-agent configurations do not take the same test if time, CPU, memory, networking, or resource enforcement differs.

## Architecture / mechanism

Anthropic ran Terminal-Bench 2.0 on Kubernetes and varied resource configurations and enforcement. Hard ceilings killed tasks that temporarily exceeded recommendations; pod errors created failures unrelated to model behavior. The proposed remedy is to document and enforce resources as rigorously as prompts and sampling.

## Empirical evidence

The reported gap between least- and most-resourced setups is six percentage points with `p < 0.01`. Infrastructure errors reached six percent in calibration. Across a moderate range, the observed score spread was just under two points; the authors recommend skepticism for sub-three-point gaps without matched configuration.

## Mathematical or formal content

Observed score can be decomposed into capability failure and infrastructure censoring. If infrastructure independently fails with probability `q`, observed success is at most `(1-q)p`; dependence on task resource demand makes simple correction inadequate. Resource configuration should therefore appear as a factorial covariate, not residual noise.

## What is directly evidenced

The page gives the benchmark, cluster implementation, resource contrast, observed differences, significance test, and operational error diagnosis.

## What is interpretation or advocacy

The three-point skepticism threshold is a practical heuristic, not a universal confidence bound. Findings on Terminal-Bench do not quantify infrastructure effects on every benchmark.

## Limitations, incentives, and likely biases

The full task-by-condition data and model may not be public; resource configurations are tied to one cluster and benchmark; multiple testing and task clustering details matter. Anthropic has incentives in model comparisons.

## Transferable engineering lessons

Pin VM images and limits, record enforcement semantics, separate infra errors from agent failures, repeat borderline tasks, report resource sensitivity, and include configuration in the experimental estimand.

## Connections to academic work

This result reinforces Stop Comparing Agents Without Disclosing the Harness, HAL, SWE-bench environment cautions, and rigorous benchmark-validity work.

## Verification notes

The canonical page's setup, six-point result, error rate, moderate-range spread, statistical claim, and recommendations were checked on 2026-09-04.
