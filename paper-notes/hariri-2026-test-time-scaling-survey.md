---
title: "Test-Time Scaling in Reasoning LLMs: Inference Regimes, Evaluation, and Reproducibility"
authors: ["Mohsen Hariri", "Weicong Chen", "Nahal Shahini", "Vikash Singh", "Kai Ye", "Amirhossein Samandar", "Debargha Ganguly", "Sreehari Sankar", "Yanyan Zhang", "Shouren Wang", "Jerry Peng", "Biyao Zhang", "Michael Hinczewski", "Vipin Chaudhary"]
year: 2026
venue: "preprint"
source_type: "preprint"
paper_url: "https://arxiv.org/abs/2608.04001"
pdf_path: "papers/academic/hariri-2026-test-time-scaling-survey.pdf"
accessed: "2026-09-04"
review_status: "skimmed"
evidence_confidence: "medium"
---

# hariri-2026-test-time-scaling-survey — Test-Time Scaling in Reasoning LLMs: Inference Regimes, Evaluation, and Reproducibility

## Why this source is in the corpus

Supplies vocabulary and comparison axes for formalizing the harness as a composite decision system.

## Research question

What inference-time scaling regimes exist, and how reproducible are their reported gains?

## Harness mechanism studied

Repeated sampling, verification, search, adaptive allocation, and refinement under an inference budget.

## Method and experimental setup

Survey organizes test-time scaling methods, metrics, and reproducibility threats across reasoning tasks.

## Main findings

- Scaling inference can improve coverage but benefits depend on selection quality and task difficulty.
- Comparisons frequently confound generator, verifier, budget, and stopping policy.

## Mathematical content

Unifies compute allocation and best-of-N style objectives; mathematical claims belong to the underlying cited papers.

## Evidence quality and limitations

A new preprint survey; breadth exceeds the depth of independent reproduction.

## Important implementation details

Record the complete generator-search-verifier-stopping tuple and actual token or wall-clock cost.

## Claims this source supports

Test-time compute is a harness-controlled resource-allocation problem.

## Claims this source weakens or contradicts

The slogan that more samples monotonically improve deployable accuracy.

## Relevance to a mathematics paper

Motivates optimal-stopping, selection-error, and cost-constrained formulations.

## Connections to other sources

See the category and claim-level cross-references in [`INDEX.md`](INDEX.md) and the synthesis documents.

## Verification notes

Abstract, regime taxonomy, reproducibility discussion, and conclusion checked in the local PDF. The archived file parsed successfully: 54 pages, 182096 extractable characters, SHA-256 `d5ac888ca9d2f6b15ad3ce1b626bbcd403745805d15d38f750e7e0680d747e32`.
