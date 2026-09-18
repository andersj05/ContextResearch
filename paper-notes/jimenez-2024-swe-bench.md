---
title: "SWE-bench: Can Language Models Resolve Real-World GitHub Issues?"
authors: ["Carlos E. Jimenez", "John Yang", "Alexander Wettig", "Shunyu Yao", "Kexin Pei", "Ofir Press", "Karthik Narasimhan"]
year: 2024
venue: "ICLR-2024"
source_type: "peer-reviewed"
paper_url: "https://arxiv.org/abs/2310.06770"
pdf_path: "papers/academic/jimenez-2024-swe-bench.pdf"
accessed: "2026-09-04"
review_status: "fully-reviewed"
evidence_confidence: "high"
---

# jimenez-2024-swe-bench — SWE-bench: Can Language Models Resolve Real-World GitHub Issues?

## Why this source is in the corpus

Makes model–harness–environment coupling observable in executable, long-horizon tasks.

## Research question

Can language models resolve real repository issues under executable tests?

## Harness mechanism studied

A model receives an issue plus a repository snapshot, retrieves or reads code, emits a patch, and is scored by fail-to-pass and regression tests.

## Method and experimental setup

ICLR 2024 benchmark construction from merged GitHub pull requests; 2,294 tasks across 12 Python repositories, with execution filters and baseline model evaluations.

## Main findings

- The original best baseline, Claude 2 with BM25 retrieval, resolved 1.96% of tasks.
- Repository-level repair requires long-context localization, editing, and test execution, making the harness part of the measured system.

## Mathematical content

Resolved rate is the sample mean of an all-required-tests-pass indicator; it is a binary outcome whose uncertainty should be clustered by repository.

## Evidence quality and limitations

Tests are an imperfect behavioral oracle; repositories and languages are narrow; public issues and patches create later exposure risk; model and harness effects are confounded.

## Important implementation details

Pin repository commits and images, preserve the exact patch application and test commands, report retrieval/context policy, token and cost budgets, and audit task tests.

## Claims this source supports

Executable, stateful environments are necessary for meaningful coding-agent evaluation.

## Claims this source weakens or contradicts

A benchmark score as an intrinsic property of a model or a complete measure of correctness.

## Relevance to a mathematics paper

Supports Bernoulli success models, repository-clustered intervals, and measurement-error corrections.

## Connections to other sources

See the category and claim-level cross-references in [`INDEX.md`](INDEX.md) and the synthesis documents.

## Verification notes

Abstract and pages 1-3 checked for task count, repository count, collection pipeline, scoring setup, and the 1.96% baseline; local PDF is the ICLR version. The archived file parsed successfully: 52 pages, 153686 extractable characters, SHA-256 `f7e8e1df64129742b8199a21a042734519a823a1dafd6f48f8f3ddcfb48ee296`.
