---
title: "Scaling LLM Test-Time Compute Optimally can be More Effective than Scaling Model Parameters"
authors: ["Charlie Snell", "Jaehoon Lee", "Kelvin Xu", "Aviral Kumar"]
year: 2024
venue: "preprint"
source_type: "preprint"
paper_url: "https://arxiv.org/abs/2408.03314"
pdf_path: "papers/academic/snell-2024-test-time-compute.pdf"
accessed: "2026-09-04"
review_status: "fully-reviewed"
evidence_confidence: "high"
---

# snell-2024-test-time-compute — Scaling LLM Test-Time Compute Optimally can be More Effective than Scaling Model Parameters

## Why this source is in the corpus

Supports analysis of inference-time search, feedback, stopping, and verifier error.

## Research question

How should inference compute be allocated by prompt difficulty?

## Harness mechanism studied

A policy chooses between iterative revision and verifier-guided sampling and allocates more calls only where expected value is high.

## Method and experimental setup

MATH problems, PaLM-2 models, a process verifier, difficulty bins estimated from many samples, and FLOP-matched comparisons with larger models.

## Main findings

- Difficulty-conditioned allocation can match or beat best-of-N with up to four times fewer generations.
- Extra inference helps easy and intermediate problems more than the hardest ones in this setup.

## Mathematical content

The objective maximizes expected correctness under a generation budget; training and inference FLOPs are approximated by 6ND_pre and 2ND_inf.

## Evidence quality and limitations

Difficulty bins use 2,048 samples and ground truth, estimator overhead is omitted from deployment, and results rely on MATH, PaLM-2, and a custom verifier.

## Important implementation details

Charge difficulty estimation, publish allocation policy, and compare total compute rather than sample count alone.

## Claims this source supports

Adaptive test-time resource allocation can outperform uniform scaling.

## Claims this source weakens or contradicts

More inference compute or a single strategy as uniformly beneficial across difficulty.

## Relevance to a mathematics paper

Directly frames harness design as budgeted value-of-computation optimization.

## Connections to other sources

See the category and claim-level cross-references in [`INDEX.md`](INDEX.md) and the synthesis documents.

## Verification notes

Allocation objective, FLOP assumptions, difficulty-bin construction, main comparisons, and limitations checked in the local PDF. The archived file parsed successfully: 37 pages, 91846 extractable characters, SHA-256 `ded7b20b51493258c5ce2a1a024cd33dd752de1fa3373d1207620da4cfe24545`.
