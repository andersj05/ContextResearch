---
title: "Does SWE-Bench-Verified Test Agent Ability or Model Memory?"
authors: ["Thanosan Prathifkumar", "Noble Saji Mathews", "Meiyappan Nagappan"]
year: 2025
venue: "preprint"
source_type: "preprint"
paper_url: "https://arxiv.org/abs/2512.10218"
pdf_path: "papers/academic/prathifkumar-2025-swe-memory.pdf"
accessed: "2026-09-04"
review_status: "fully-reviewed"
evidence_confidence: "medium"
---

# prathifkumar-2025-swe-memory — Does SWE-Bench-Verified Test Agent Ability or Model Memory?

## Why this source is in the corpus

Makes model–harness–environment coupling observable in executable, long-horizon tasks.

## Research question

Does anomalously strong localization on SWE-bench Verified indicate model memory rather than agent skill?

## Harness mechanism studied

Models receive intentionally insufficient issue-only or issue-plus-path information and are asked to identify relevant files, then performance is compared with fresh benchmarks.

## Method and experimental setup

Recent empirical paper testing two Claude models on SWE-bench Verified, BeetleBox, and January and September 2025 SWE-rebench splits.

## Main findings

- The tested models perform about three times better on SWE-bench Verified overall and about six times better at finding edited files despite minimal project context.
- This is evidence of differential familiarity or exposure risk, not direct observation of training-set membership.

## Mathematical content

The statistic is a cross-dataset risk ratio under a negative-control-like information restriction; identification requires exchangeable task difficulty and repository familiarity.

## Evidence quality and limitations

Small model family, selected Python repositories, unequal datasets, issue text may contain localization clues, black-box training data, and recent nonreplicated work.

## Important implementation details

Match repositories and difficulty, use blinded post-cutoff tasks, preregister impossible-context probes, test more model families, and avoid labeling indirect evidence as confirmed leakage.

## Claims this source supports

Older public benchmarks may measure latent familiarity as well as current harness ability.

## Claims this source weakens or contradicts

Claiming that localization gaps alone prove exact memorization or quantify contamination prevalence.

## Relevance to a mathematics paper

Motivates negative controls, risk ratios, and sensitivity analysis for unobserved exposure.

## Connections to other sources

See the category and claim-level cross-references in [`INDEX.md`](INDEX.md) and the synthesis documents.

## Verification notes

Abstract and introduction checked for 500-task benchmark context, two Claude models, three-times and six-times gaps, comparison datasets, logic, and limitations. The archived file parsed successfully: 4 pages, 19575 extractable characters, SHA-256 `704998200abd6d5957ecdfcff52faa3a5bc9c14cf31d83b18f723128aeed393f`.
