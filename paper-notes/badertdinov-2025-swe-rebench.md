---
title: "SWE-rebench: An Automated Pipeline for Task Collection and Decontaminated Evaluation of Software Engineering Agents"
authors: ["Ibragim Badertdinov", "Alexander Golubev", "Maksim Nekrashevich", "Anton Shevtsov", "Simon Karasik", "Andrei Andriushchenko", "Maria Trofimova", "Daria Litvintseva", "Boris Yangel"]
year: 2025
venue: "NeurIPS-2025"
source_type: "peer-reviewed"
paper_url: "https://arxiv.org/abs/2505.20411"
pdf_path: "papers/academic/badertdinov-2025-swe-rebench.pdf"
accessed: "2026-09-04"
review_status: "skimmed"
evidence_confidence: "high"
---

# badertdinov-2025-swe-rebench — SWE-rebench: An Automated Pipeline for Task Collection and Decontaminated Evaluation of Software Engineering Agents

## Why this source is in the corpus

Makes model–harness–environment coupling observable in executable, long-horizon tasks.

## Research question

Can continuously collected fresh repository tasks reduce contamination and standardize software-agent evaluation?

## Harness mechanism studied

An automated pipeline mines issue-pull-request pairs, builds environments, validates tests, scores quality, and continually refreshes a benchmark.

## Method and experimental setup

NeurIPS 2025 datasets paper with 21,336 verified Python tasks from 3,468 repositories plus comparisons between fresh tasks and SWE-bench Verified.

## Main findings

- The pipeline produces more than 21,000 interactive tasks and enables evaluation on post-training-cutoff issues.
- Some models lose more performance on fresh tasks than others, consistent with benchmark exposure but not proof of memorization.

## Mathematical content

A freshness gap is a difference of proportions across nonidentical task distributions; causal contamination inference requires adjustment for task difficulty and repository mix.

## Evidence quality and limitations

Automation can admit noisy or weak tests; freshness changes both exposure and distribution; training cutoffs are not fully observable; only Python repositories are covered.

## Important implementation details

Publish collection timestamps, task provenance, environment build logs, quality scores, model cutoffs, and matched difficulty analyses; rotate hidden test sets.

## Claims this source supports

Dynamic benchmarks and transparent harness reporting reduce one source of leaderboard invalidity.

## Claims this source weakens or contradicts

A pre-cutoff versus post-cutoff gap as definitive proof that a model memorized tasks.

## Relevance to a mathematics paper

Motivates covariate-adjusted freshness studies and temporal generalization models.

## Connections to other sources

See the category and claim-level cross-references in [`INDEX.md`](INDEX.md) and the synthesis documents.

## Verification notes

Abstract and pages 1-3 checked for pipeline stages, 21,336 tasks, 3,468 repositories, decontamination claim, and stated caveats. The archived file parsed successfully: 40 pages, 107894 extractable characters, SHA-256 `5d514a4d2bb375763bd12f71140a79e721e29adab8ec192ebd7215d7c93c4d8c`.
