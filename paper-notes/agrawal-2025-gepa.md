---
title: "GEPA: Reflective Prompt Evolution Can Outperform Reinforcement Learning"
authors: ["Lakshya A Agrawal", "Shangyin Tan", "Dilara Soylu", "Noah Ziems", "Rishi Khare", "Krista Opsahl-Ong", "Arnav Singhvi", "Herumb Shandilya", "Michael J Ryan", "Meng Jiang", "Christopher Potts", "Koushik Sen", "Alexandros G. Dimakis", "Ion Stoica", "Dan Klein", "Matei Zaharia", "Omar Khattab"]
year: 2025
venue: "ICLR-2026"
source_type: "peer-reviewed"
paper_url: "https://arxiv.org/abs/2507.19457"
pdf_path: "papers/academic/agrawal-2025-gepa.pdf"
accessed: "2026-09-04"
review_status: "skimmed"
evidence_confidence: "high"
---

# agrawal-2025-gepa — GEPA: Reflective Prompt Evolution Can Outperform Reinforcement Learning

## Why this source is in the corpus

Directly studies reusable harness components, outer-loop optimization, self-modification, or the statistical controls needed to decide whether an update is a real improvement.

## Research question

Can execution traces and natural-language reflection evolve high-performing system prompts more sample-efficiently than reinforcement learning?

## Harness mechanism studied

A reflection model proposes prompt mutations from trajectories; a Pareto archive retains candidates that excel on different development examples and recombines useful text.

## Method and experimental setup

GEPA alternates trajectory collection, reflective diagnosis, prompt proposal, per-example scoring, Pareto selection, and optional merge; it compares against prompt optimizers and GRPO across reasoning and agent tasks.

## Main findings

- Table 1 reports Qwen3-8B baseline 45.23, GRPO 48.91 with 24,000 rollouts, MIPRO 47.84, and GEPA 54.85 using about 3,936 rollouts on average; GPT-4.1-mini rises from 53.03 to 65.22, or 66.36 with merge.
- GEPA loses AIME to GRPO 32 versus 38, merge hurts IFBench to 28.23, and cross-model transfer of a Qwen-optimized prompt reaches 62.03 rather than the same-model 65.22/66.36, so benefit is neither uniform nor model-invariant.

## Mathematical content

The archive keeps nondominated prompts under a vector of per-example scores; reflective proposal plus Pareto selection is a heuristic multiobjective search, not a gradient estimator or convergence proof.

## Evidence quality and limitations

No confidence intervals or multiple random seeds for many searches, adaptive validation reuse, prompt-only scope, evaluator/model dependence, and selected benchmark/task mixtures limit claims of general sample efficiency.

## Important implementation details

Collect full traces, have an LM write a diagnosis and revised prompt, score the child per development example, insert it if Pareto-nondominated, and optionally merge complementary archive members.

## Claims this source supports

Persistent prompts can improve sharply from grounded trajectories with far fewer rollouts than the compared RL configuration.

## Claims this source weakens or contradicts

The paper contradicts a universal GEPA win: AIME favors GRPO, merge can regress, and cross-model transfer loses performance.

## Relevance to a mathematics paper

The per-example Pareto archive is mathematically useful for diversity-preserving selection and exposes validation-vector overfitting.

## Connections to other sources

See the category and claim-level cross-references in [`INDEX.md`](INDEX.md) and the synthesis documents.

## Verification notes

Local PDF algorithms, Table 1, rollout accounting, cross-model and merge results, Table 3 archive ablations, and limitations were checked; no rerun was done. The archived file parsed successfully: 96 pages, 274216 extractable characters, SHA-256 `ab3a5139bac83f192ad67529368d77b84b0d807e95a8e4fd0daa8d45fd046bec`.
