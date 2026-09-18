---
title: "Introducing SWE-bench Verified"
author_or_org: "OpenAI and SWE-bench contributors"
date: "2024-08-13; updated 2025-02-24"
source_type: "practitioner-report"
url: "https://openai.com/index/introducing-swe-bench-verified/"
version_or_commit: "page update 2025-02-24, accessed 2026-09-04"
accessed: "2026-09-04"
review_status: "reviewed"
evidence_confidence: "high"
---

# openai-2024-swebench-verified — Introducing SWE-bench Verified

## Why this source is in the corpus

This report documents the human curation and containerized harness that turned a benchmark revision into the dominant coding-agent measure—and provides a later lesson in why validated benchmarks still age.

## System or claim described

Professional developers screened 1,699 SWE-bench tasks for clear specifications, reasonable scope, and appropriate tests. Three experts independently reviewed each task, producing a 500-task subset and public annotations. A Docker evaluation harness standardized execution.

## Architecture / mechanism

Agents receive an issue and pre-fix repository but not tests, generate a patch, and must pass fail-to-pass and pass-to-pass tests. The curation adds human task-validity judgments and difficulty estimates; containerization reduces environment drift.

## Empirical evidence

The report says GPT-4o reached 33.2% with the best tested scaffold, versus 16% on original SWE-bench. For GPT-4 on SWE-bench Lite, cited scaffold results ranged from 2.7% to 28.3%. The page explicitly notes that distribution shift toward easier tasks may explain part of the increase.

## Mathematical or formal content

The reported scaffold range is a model-by-harness interaction example. Because filtering changes the task distribution, score changes do not estimate only label correction; difficulty-stratified comparisons are required.

## What is directly evidenced

The page provides criteria, sample counts, reviewer protocol, annotations, harness link, score tables, and limitations.

## What is interpretation or advocacy

The original statement that the subset more reliably measures capability was justified by the 2024 audit but was later weakened by new evidence. Human consensus does not prove exhaustive tests.

## Limitations, incentives, and likely biases

Reviewer screening cannot anticipate all valid implementations or future contamination. The subset is public and small. OpenAI used it in preparedness and model communications. Later audits were selected from remaining difficult cases and must also be bounded carefully.

## Transferable engineering lessons

Publish annotations and exclusions, use several independent reviewers, containerize execution, stratify by difficulty, and schedule re-audits as models expose previously hidden grader flaws.

## Connections to academic work

This report extends SWE-bench and is challenged by SWE-Bench+, the PatchDiff study, the Agentic Benchmark Checklist, SWE-memory, SWE-rebench, and OpenAI's 2026 retirement report.

## Verification notes

The canonical page's protocol, counts, metrics, scaffold range, difficulty analysis, harness description, and limitations were checked on 2026-09-04.
