---
title: "Are Solved Issues in SWE-bench Really Solved Correctly?"
authors: ["You Wang", "Michael Pradel", "Zhongxin Liu"]
year: 2026
venue: "ICSE-2026"
source_type: "peer-reviewed"
paper_url: "https://arxiv.org/abs/2503.15223"
pdf_path: "papers/academic/wang-2026-swe-solved-correctly.pdf"
accessed: "2026-09-04"
review_status: "fully-reviewed"
evidence_confidence: "high"
---

# wang-2026-swe-solved-correctly — Are Solved Issues in SWE-bench Really Solved Correctly?

## Why this source is in the corpus

Makes model–harness–environment coupling observable in executable, long-horizon tasks.

## Research question

Do SWE-bench-passing patches actually implement the intended behavior?

## Harness mechanism studied

PatchDiff executes all developer tests and generates differential tests that compare agent patches with developer patches, followed by manual correctness review.

## Method and experimental setup

ICSE 2026 empirical study of plausible patches from CodeStory, LearnByInteract, and OpenHands on SWE-bench Verified.

## Main findings

- On average, 7.8% of plausible patches fail when all developer test files are run; 29.6% exhibit behavior different from the oracle patch.
- Manual review finds 28.6% of a 77-patch suspicious sample certainly incorrect; extrapolation estimates 11.0% incorrect plausible patches and 6.4 percentage-point average score inflation.

## Mathematical content

The 6.4-point estimate extrapolates a sampled conditional incorrectness rate to all suspicious patches and should carry sampling and tool-level uncertainty.

## Evidence quality and limitations

Differential behavior can be legitimate; generated tests can be wrong; only three tools and one benchmark are studied; the inflation figure depends on an even-distribution extrapolation.

## Important implementation details

Run all repository tests, add differential and metamorphic tests, blind manual reviewers, publish uncertainty for extrapolation, and preserve both generated and developer patches.

## Claims this source supports

Passing benchmark tests is not equivalent to semantic correctness.

## Claims this source weakens or contradicts

Unit-test success as an exhaustive or noise-free outcome measure.

## Relevance to a mathematics paper

Supports sensitivity-specificity models for graders and two-phase audit estimators.

## Connections to other sources

See the category and claim-level cross-references in [`INDEX.md`](INDEX.md) and the synthesis documents.

## Verification notes

Abstract and pages 1-2 checked for 7.8%, 29.6%, 77-patch sample, 28.6%, 11.0% extrapolation, 6.4-point inflation, methods, and caveats. The archived file parsed successfully: 13 pages, 82851 extractable characters, SHA-256 `b2db368d3c9632795c0c719270184b88a5602122a9e5515c51e6acc669af555f`.
