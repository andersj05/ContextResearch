---
title: "On Over-fitting in Model Selection and Subsequent Selection Bias in Performance Evaluation"
authors: ["Gavin C. Cawley", "Nicola L. C. Talbot"]
year: 2010
venue: "JMLR-2010"
source_type: "peer-reviewed"
paper_url: "https://www.jmlr.org/papers/v11/cawley10a.html"
pdf_path: "papers/academic/cawley-2010-model-selection-overfitting.pdf"
accessed: "2026-09-04"
review_status: "skimmed"
evidence_confidence: "high"
---

# cawley-2010-model-selection-overfitting — On Over-fitting in Model Selection and Subsequent Selection Bias in Performance Evaluation

## Why this source is in the corpus

Directly studies reusable harness components, outer-loop optimization, self-modification, or the statistical controls needed to decide whether an update is a real improvement.

## Research question

Can optimization over a noisy model-selection criterion overfit that criterion and bias subsequent performance estimates?

## Harness mechanism studied

Hyperparameters are repeatedly chosen to minimize finite-sample validation or cross-validation error; the same noise becomes a search target, creating second-level overfitting.

## Method and experimental setup

Synthetic regression over 1000 realizations plus kernel-method comparisons on thirteen benchmark datasets and analysis of internal versus external cross-validation protocols.

## Main findings

- On the synthetic task, four-fold cross-validation error decreased monotonically while true test MSE began rising after roughly 30-40 optimization iterations.
- Across the thirteen datasets, a more flexible ARD kernel often lost to its nested RBF special case, and non-nested evaluation produced optimistic selection bias; model selection must be nested inside performance evaluation.

## Mathematical content

Let \hat R_J(\lambda) be a resampling estimate and \lambda^*=argmin_\lambda \hat R_J(\lambda); unbiasedness of each fixed \hat R_J(\lambda) does not imply unbiasedness of \hat R_J(\lambda^*). Nested or internal CV estimates the risk of the whole mapping D -> \lambda^*(D), rather than treating the selected \lambda^* as fixed.

## Evidence quality and limitations

This is empirical and methodological rather than a universal concentration theorem; the models and mainly small tabular benchmarks predate LLM agents; nested CV can be costly and still depends on iid and protocol assumptions.

## Important implementation details

Wrap the complete harness search, including prompt selection and stopping, inside the inner fold; reserve outer folds or a locked test set for estimating the selected procedure, not merely its final artifact.

## Claims this source supports

Harness variants can overfit an evaluator even when individual scores appear reasonable, so the search loop is part of the object under evaluation.

## Claims this source weakens or contradicts

The claim that an unbiased per-candidate validation estimator makes best-of-many harness selection unbiased.

## Relevance to a mathematics paper

Gives the second-level-risk decomposition and motivates nested estimators for an optimizer-plus-evaluator pair.

## Connections to other sources

See the category and claim-level cross-references in [`INDEX.md`](INDEX.md) and the synthesis documents.

## Verification notes

Local PDF pp. 6-7, Figure 2; pp. 13-14, Table 2; and pp. 16-24, internal/external protocols and Tables 4-8 checked. The archived file parsed successfully: 29 pages, 81612 extractable characters, SHA-256 `db01ac8fabef3064a0297bfcf64fb9791bf35c4d03be7a51f5862260adfca206`.
