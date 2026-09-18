---
title: "SWE-Bench+: Enhanced Coding Benchmark for LLMs"
authors: ["Reem Aleithan", "Haoran Xue", "Mohammad Mahdi Mohajer", "Elijah Nnorom", "Gias Uddin", "Song Wang"]
year: 2024
venue: "preprint"
source_type: "preprint"
paper_url: "https://arxiv.org/abs/2410.06992"
pdf_path: "papers/academic/aleithan-2024-swe-bench-plus.pdf"
accessed: "2026-09-04"
review_status: "fully-reviewed"
evidence_confidence: "medium"
---

# aleithan-2024-swe-bench-plus — SWE-Bench+: Enhanced Coding Benchmark for LLMs

## Why this source is in the corpus

Makes model–harness–environment coupling observable in executable, long-horizon tasks.

## Research question

How much can solution leakage and weak tests inflate SWE-bench results?

## Harness mechanism studied

The study manually compares successful generated patches with reference patches, classifies leaked solutions and weak tests, then constructs a post-cutoff filtered benchmark.

## Method and experimental setup

2024 preprint auditing 251 successful SWE-agent plus GPT-4 patches and evaluating several agents on SWE-Bench+.

## Main findings

- Among audited successes, 32.67% contain solution leakage and 31.08% are suspicious because weak tests accept divergent changes; filtering drops the reported rate from 12.47% to 3.97%.
- More than 94% of original issues predate tested model cutoffs; on SWE-Bench+ the same system scores 0.55%, but distribution shift prevents attributing the entire gap to contamination.

## Mathematical content

The corrected rate is a post-stratified proportion after human labels; contamination inference is not identified without controlling task difficulty and repository/date shifts.

## Evidence quality and limitations

Preprint; a single system drives the detailed audit; reference-patch difference need not imply incorrectness; human coding can err; freshness is only an exposure proxy.

## Important implementation details

Blind dual-review patch labels, measure test mutation adequacy, match tasks by difficulty and repository, and distinguish solution-in-prompt leakage from possible training exposure.

## Claims this source supports

Benchmark artifacts and graders can create large score inflation.

## Claims this source weakens or contradicts

A pre-cutoff date as proof of memorization, or every patch differing from the reference as incorrect.

## Relevance to a mathematics paper

Supports label-noise correction, selection-bias analysis, and bounded contamination claims.

## Connections to other sources

See the category and claim-level cross-references in [`INDEX.md`](INDEX.md) and the synthesis documents.

## Verification notes

Abstract and pages 1-3 checked for 251 patches, 32.67%, 31.08%, 12.47-to-3.97 correction, over-94% timing, SWE-Bench+ rates, and caveats. The archived file parsed successfully: 14 pages, 45808 extractable characters, SHA-256 `5b845ad1617b5abb71f5ab2c11831ea0dde7a6a25f43e618056327c3e782ea2c`.
