---
title: "Separating Signal from Noise in Coding Evaluations"
author_or_org: "OpenAI"
date: "2026-07-08"
source_type: "practitioner-report"
url: "https://openai.com/index/separating-signal-from-noise-coding-evaluations/"
version_or_commit: "web version accessed 2026-09-04"
accessed: "2026-09-04"
review_status: "reviewed"
evidence_confidence: "medium"
---

# openai-2026-swebench-pro-audit — Separating Signal from Noise in Coding Evaluations

## Why this source is in the corpus

This is a first-party audit of SWE-Bench Pro and a useful case study in how benchmark defects can exceed the score differences researchers often interpret as model or harness improvements.

## System or claim described

OpenAI reports that a substantial fraction of the 731-task public split is broken because prompts, hidden tests, and intended functionality do not consistently agree. It retracts its earlier recommendation to use the benchmark without stronger qualification.

## Architecture / mechanism

An automated datapoint-analysis pipeline inspected task instructions, metadata, model attempts, tests, and failure traces, flagging 286 tasks. The flagged subset then received repeated investigator-agent passes with researcher adjudication and, separately, reviews by five experienced software engineers per task with disagreement escalation.

## Empirical evidence

The agent-assisted review labeled 200 of 731 tasks (27.4%) broken; the human campaign labeled 249 (34.1%) broken. The two paths overlapped on the broad category in 74% of flagged cases. Reported defect classes were overly strict tests, underspecified prompts, low-coverage tests, and misleading prompts. These are source-reported results from a first-party audit, not an independent replication.

## Mathematical or formal content

The overall broken-task fractions are meaningful only if the flagged subset contains nearly all broken tasks. Because detailed human review was concentrated on initially flagged cases, the design identifies precision and category agreement in that subset more directly than the false-negative rate among unflagged tasks. A full prevalence interval requires a probability audit of both flagged and unflagged strata, followed by stratified weighting.

## What is directly evidenced

The report describes the pipeline, review protocol, labels, counts, and examples. It directly supports the claim that outcome tests can be simultaneously too strict, too weak, or misaligned with the visible task.

## What is interpretation or advocacy

The recommendation to prefer professionally authored evaluations and the approximate “30%” headline are the publisher's conclusions. Treating every affected task as unusable, or extrapolating the rate to other benchmarks, goes beyond the audit.

## Limitations, incentives, and likely biases

OpenAI evaluates its own models and helped popularize the predecessor benchmark, creating both reputational and product incentives. The initial filter selected the intensive-review sample, so unflagged-task recall remains crucial. The source does not provide a full independent adjudication artifact for every task.

## Transferable engineering lessons

Validate prompts, tests, reference patches, and successful as well as failed trajectories. Estimate both false positives and false negatives. A benchmark scorer is part of the harness and can dominate small leaderboard deltas.

## Connections to academic work

The result reinforces SWE-bench patch audits, SWE-bench+, SWE-rebench, and formal label-noise corrections in [`03-empirical-evidence-and-benchmark-validity.md`](../synthesis/03-empirical-evidence-and-benchmark-validity.md) and [`04-mathematical-foundations.md`](../synthesis/04-mathematical-foundations.md).

## Verification notes

The canonical page's headline, methodology, human-review protocol, counts, failure taxonomy, discussion, and worked example were inspected on 2026-09-04. No PDF snapshot was generated because redistribution and rendering rights were not clear; the canonical URL is preserved instead.
