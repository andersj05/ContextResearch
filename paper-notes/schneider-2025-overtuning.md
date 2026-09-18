---
title: "Overtuning in Hyperparameter Optimization"
authors: ["Lennart Schneider", "Bernd Bischl", "Matthias Feurer"]
year: 2025
venue: "AutoML-2025"
source_type: "peer-reviewed"
paper_url: "https://arxiv.org/abs/2506.19540"
pdf_path: "papers/academic/schneider-2025-overtuning.pdf"
accessed: "2026-09-04"
review_status: "skimmed"
evidence_confidence: "high"
---

# schneider-2025-overtuning — Overtuning in Hyperparameter Optimization

## Why this source is in the corpus

Directly studies reusable harness components, outer-loop optimization, self-modification, or the statistical controls needed to decide whether an update is a real improvement.

## Research question

How often does continued hyperparameter optimization improve validation error while worsening the true performance of the incumbent?

## Harness mechanism studied

The optimizer repeatedly replaces the incumbent by validation rank; overtuning measures how far the current incumbent's test error has risen above the best earlier incumbent's test error.

## Method and experimental setup

Formal definitions plus a large reanalysis of public HPO trajectories from seven benchmark collections and mixed-model analyses of metric, resampling, dataset, learner, and optimizer factors.

## Main findings

- About 60% of eligible HPO runs showed no overtuning, 70% had relative overtuning below 0.1, and 90% below 1.0.
- Roughly 10% were severe enough to erase the observed improvement over the initial or default configuration; effects were usually mild but occasionally large.

## Mathematical content

For incumbent lambda_t*=argmin_{lambda in {lambda_1,...,lambda_t}} val(lambda), overtuning is ot_t=test(lambda_t*)-min_{s<=t}test(lambda_s*). Relative overtuning divides this by test(lambda_1*)-min_{s<=t}test(lambda_s*). Nonzero validation-test gap is necessary but not sufficient for overtuning.

## Evidence quality and limitations

The analysis conditions severity on runs with more than 0.001 test improvement and excludes about 38.5% as numerically unstable or negligible; reused benchmark trajectories were not designed for this paper; test labels permit retrospective oracle calculations unavailable in deployment; causal claims from mixed models remain limited.

## Important implementation details

Track the full incumbent trajectory, evaluate snapshots on an outer set, report absolute and relative overtuning, and consider early stopping or resampling reshuffles without using the outer test trajectory for live decisions.

## Claims this source supports

Longer or more aggressive harness optimization can reverse real progress even while the inner evaluator improves.

## Claims this source weakens or contradicts

The meme that evaluator overfitting always becomes catastrophic, and the opposite meme that more search is harmless; the observed distribution contains both mostly mild and material tail cases.

## Relevance to a mathematics paper

Supplies operational estimands for time-horizon degradation and a direct empirical target for a harness-search study.

## Connections to other sources

See the category and claim-level cross-references in [`INDEX.md`](INDEX.md) and the synthesis documents.

## Verification notes

Local PDF Definition 3.1-3.2 on pp. 2-3, dataset construction on pp. 5-6, Figure 2 and prevalence results, and mixed-model/limitations sections checked. The archived file parsed successfully: 43 pages, 128340 extractable characters, SHA-256 `08c5c9e2286bc70187632483d2a3bfd27586e805992e92026f83ff43f8e37376`.
