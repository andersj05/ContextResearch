---
title: "ScoreFlow: Mastering LLM Agent Workflows via Score-based Preference Optimization"
authors: ["Yinjie Wang", "Ling Yang", "Guohao Li", "Mengdi Wang", "Bryon Aragam"]
year: 2025
venue: "preprint"
source_type: "preprint"
paper_url: "https://arxiv.org/abs/2502.04306"
pdf_path: "papers/academic/wang-2025-scoreflow.pdf"
accessed: "2026-09-04"
review_status: "skimmed"
evidence_confidence: "medium"
---

# wang-2025-scoreflow — ScoreFlow: Mastering LLM Agent Workflows via Score-based Preference Optimization

## Why this source is in the corpus

Directly studies reusable harness components, outer-loop optimization, self-modification, or the statistical controls needed to decide whether an update is a real improvement.

## Research question

Can workflow generation be improved by training on relative quality scores rather than relying only on sparse scalar rewards?

## Harness mechanism studied

A generator proposes executable workflows and Score-DPO learns from ranked candidate pairs whose preference strength reflects score differences.

## Method and experimental setup

ScoreFlow samples workflow code, evaluates multiple candidates on task data, constructs score-weighted preference pairs, fine-tunes the generator, and compares selected workflows under a common GPT-4o-mini executor.

## Main findings

- Table 1 reports averages IO 76.0, CoT 76.7, CoT-SC 77.3, ADAS 76.6, AFlow 80.6, and ScoreFlow 85.3, with ScoreFlow task scores 86.0 HotPotQA, 86.2 DROP, 95.9 HumanEval, 84.7 MBPP, 94.6 GSM8K, and 64.4 MATH.
- The source frames this as about +8.2 points over baselines, but public-task reuse, generator-training/search cost, three-run uncertainty, and workflow-selection exposure make it weaker than a sealed prospective test.

## Mathematical content

Score-DPO applies a preference-logistic objective whose pair weight depends on reward difference, approximating optimization of workflow-ranking quality; it provides no guarantee that pairwise preferences recover true out-of-sample utility.

## Evidence quality and limitations

Preprint; benchmark solutions may enter workflow generation; costs of candidate creation and fine-tuning are not normalized; only three runs; executor and evaluator interactions are not fully isolated.

## Important implementation details

Generate candidate workflow programs, execute and score them, form chosen/rejected pairs with score margins, optimize the workflow generator via DPO, and select a high-scoring program for a fixed executor.

## Claims this source supports

Learning a reusable proposal distribution can make later workflow search more efficient than independent prompting.

## Claims this source weakens or contradicts

A high score after training on task-derived preferences does not demonstrate cross-distribution self-improvement or isolate architecture from data exposure.

## Relevance to a mathematics paper

Connects preference learning to structured program search and raises identifiability questions between reward-scale weighting and adaptive selection.

## Connections to other sources

See the category and claim-level cross-references in [`INDEX.md`](INDEX.md) and the synthesis documents.

## Verification notes

Local PDF objective, training algorithm, Table 1, three-run protocol, ablations, and limitations were checked; values are source-reported. The archived file parsed successfully: 24 pages, 65909 extractable characters, SHA-256 `08a9a584ed58b0871992ce3d3707fc94295f62998f63d7aca0da5f54f880fc2d`.
