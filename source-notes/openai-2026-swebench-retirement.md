---
title: "Why SWE-bench Verified No Longer Measures Frontier Coding Capabilities"
author_or_org: "OpenAI"
date: "2026-02-23"
source_type: "practitioner-report"
url: "https://openai.com/index/why-we-no-longer-evaluate-swe-bench-verified/"
version_or_commit: "web version accessed 2026-09-04"
accessed: "2026-09-04"
review_status: "reviewed"
evidence_confidence: "medium"
---

# openai-2026-swebench-retirement — Retiring SWE-bench Verified at the Frontier

## Why this source is in the corpus

This report is an unusually explicit benchmark-maker reversal: the same organization that curated SWE-bench Verified concluded that tests and exposure made it unsuitable for frontier model launches.

## System or claim described

OpenAI audited 138 tasks that o3 failed inconsistently over 64 runs. At least six experienced engineers reviewed each case, with additional review after a flag. The report separates overly narrow tests, overly wide tests, other flaws, and evidence of training exposure.

## Architecture / mechanism

Narrow tests reject functionally correct alternatives; wide tests require behavior absent from the issue; environment differences spuriously fail; public gold patches can supply latent information that resolves underspecified tasks. These mechanisms break outcome and comparison validity even if the runner is deterministic.

## Empirical evidence

Of the 138 selected hard/frequently failed tasks, 59.4% had material test or description issues: 35.5% narrow, 18.8% wide, and 5.1% other. Frontier models reproduced some original fixes or details, and exposure correlated with success in the reported analyses. OpenAI stopped reporting the benchmark and recommended SWE-bench Pro.

## Mathematical or formal content

The 59.4% is a conditional estimate for a deliberately selected 27.6% subset, not an unbiased estimate for all 500 tasks. Let `F` denote frequent failure and `Q` a flawed task: the audit estimates `P(Q|F)`, not `P(Q)`. Extrapolating requires the unobserved `P(Q|not F)`.

## What is directly evidenced

The report gives selection, review procedure, taxonomy, counts, model-reproduction examples, and the policy decision to retire the score.

## What is interpretation or advocacy

Reproducing a patch is evidence of exposure but does not reveal where training exposure occurred or whether the model memorized versus learned from related code. The recommendation of a replacement benchmark should be audited independently.

## Limitations, incentives, and likely biases

The sample is intentionally biased toward unresolved tasks; contamination details for proprietary models are incomplete; some analyses are provider-run; and the recommended replacement has its own later audit questions. The report may understate flaws among easy passes or overstate their prevalence overall.

## Transferable engineering lessons

Audit both false positives and false negatives, report the sampling frame, distinguish conditional from population prevalence, rotate private tasks, and retire a benchmark when score movement no longer tracks the intended construct.

## Connections to academic work

The report corroborates but does not replace SWE-Bench+, PatchDiff, rigorous benchmark guidance, SWE-rebench, and SWE-memory. It is central counterevidence to unqualified leaderboard narratives.

## Verification notes

The canonical page's background, selected audit, reviewer procedure, flaw categories, contamination analysis, and retirement recommendation were checked on 2026-09-04. The selection-bias qualification above is our inference.
