---
title: "Harness Design for Long-Running Application Development"
author_or_org: "Prithvi Rajasekaran / Anthropic"
date: "2026-03-24"
source_type: "engineering-blog"
url: "https://www.anthropic.com/engineering/harness-design-long-running-apps"
version_or_commit: "web version accessed 2026-09-04"
accessed: "2026-09-04"
review_status: "reviewed"
evidence_confidence: "low"
---

# anthropic-2026-harness-design — Harness Design for Long-Running Applications

## Why this source is in the corpus

This post shows how a practitioner evolved from handoff-heavy scaffolding to planner-generator-evaluator loops, then removed components as the underlying model improved.

## System or claim described

A planner expands a short request into a product specification, a generator builds the application, and an evaluator uses browser tools and explicit criteria to test and critique it. The central lesson is that a component is load-bearing only relative to a model, task boundary, and evaluation.

## Architecture / mechanism

The frontend loop runs five to fifteen generator-evaluator iterations. The full-stack version uses structured artifacts, task decomposition, browser-based QA, and feedback cycles. Later versions remove sprint decomposition and context resets for a more capable model while retaining the planner and using the evaluator where the task remains beyond reliable solo capability.

## Empirical evidence

Evidence is a small sequence of author-selected builds. One Digital Audio Workstation run took 3 hours 50 minutes and cost 124.70 dollars: 4.7 minutes for planning, more than three hours of building, and several QA passes. The evaluator caught display-only features, but no blinded score, baseline distribution, or task-level denominator is reported.

## Mathematical or formal content

The rational component rule is conditional: include evaluator `e` when its expected reduction in failure loss exceeds evaluation cost and added error. Sequential feedback can be treated as an optimal-stopping problem, but the post supplies no calibrated estimates.

## What is directly evidenced

The page gives prompts, role definitions, timings, costs, feedback examples, and a narrative ablation path.

## What is interpretation or advocacy

Claims of aesthetic improvement are calibrated to the author's preferences. The GAN analogy is structural, not adversarial training in the mathematical sense. A polished example does not estimate expected quality.

## Limitations, incentives, and likely biases

Very small selected sample, proprietary models, author judge, subjective design outcome, changing models during iteration, and high cost. It should generate hypotheses, not serve as causal proof.

## Transferable engineering lessons

Define evaluator criteria before looping, remove one component at a time, re-test assumptions after model upgrades, and route expensive verification to tasks near the reliability frontier.

## Connections to academic work

The loop relates to Self-Refine, CRITIC, LATS, verifier-aware inference, and the negative results showing that extra iterations can be dominated by simple sampling.

## Verification notes

The canonical page's design criteria, generator-evaluator protocol, architecture revision, component-removal discussion, DAW timing/cost table, and caveats were checked on 2026-09-04.
