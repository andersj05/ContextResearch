---
title: "GEPA: Genetic-Pareto Reflective Optimization"
author_or_org: "gepa-ai"
date: "2026-09-04"
source_type: "official-implementation-evidence"
url: "https://github.com/gepa-ai/gepa"
version_or_commit: "v0.1.4 (2026-07-15); main commit 0632cdb5dcc052e690eab439e1b4a7e3e9cfe407 (2026-09-01)"
accessed: "2026-09-04"
review_status: "reviewed"
evidence_confidence: "high-for-mechanism-medium-for-generalization-claims"
license_or_access_notes: "MIT; optional meta-harness depends on proprietary Claude Code as proposer"
---

# selfopt-gepa — GEPA

## Why this source is in the corpus

GEPA is a current general-purpose implementation of reflection-guided evolutionary optimization. Unlike prompt-only systems, its adapter and `optimize_anything` surfaces can treat code, agent architectures, tool descriptions, configurations, or other text artifacts as the candidate.

## System or claim described

GEPA uses an evaluator's scalar score plus textual/actionable side information from traces to diagnose failures, mutate one or more textual components, and retain complementary candidates through a Pareto-aware archive.

## Architecture / mechanism

The core begins with a dictionary of named text components. It evaluates the seed on validation data, selects a candidate—by Pareto coverage, current best, epsilon-greedy, or top-k Pareto—samples a training minibatch, captures traces, selects components, and asks a reflection LM or custom proposer for replacements. A configurable acceptance criterion admits the proposal after minibatch evaluation; accepted candidates receive validation scores and update the frontier. Optional merge combines components from distinct successful lineages. Budgets can be metric calls, reflection cost, time/signal/file stoppers, or custom callbacks; state can be persisted and resumed.

The pinned main branch also contains a separate meta-harness engine. A Claude Code subprocess reads task, frontier, candidate files, evaluation traces, and short reports; it prototypes and writes up to three structural candidates. An outer evaluation server scores them and updates overall and per-example frontiers.

## Empirical evidence

The repository supplies adapters and examples for prompts, DSPy programs, LangChain, MCP tool descriptions, RAG, TerminalBench, ARC-AGI, and non-LLM optimization examples. These are valuable executable demonstrations, but project-reported gains span different models, metrics, and budgets and should not be treated as one pooled causal estimate.

## Mathematical or formal content

For candidate \(c\) with per-instance score vector \(v(c)\), the default selector samples candidates that are maximal on at least one validation instance. Reflection proposes

\[
c'\sim q_\phi(\cdot\mid c,\tau(c,B),F(c,B)),
\]

where \(\tau\) is an execution trace and \(F\) textual evaluator feedback on minibatch \(B\). Aggregate validation score chooses the returned winner; the frontier primarily controls exploration. This is black-box evolutionary optimization, not gradient descent.

## What is directly evidenced

**Official sources:** [repository](https://github.com/gepa-ai/gepa), [documentation](https://gepa-ai.github.io/gepa/), [v0.1.4 release](https://github.com/gepa-ai/gepa/releases/tag/v0.1.4), [pinned public API](https://github.com/gepa-ai/gepa/blob/0632cdb5dcc052e690eab439e1b4a7e3e9cfe407/src/gepa/api.py), [pinned engine](https://github.com/gepa-ai/gepa/blob/0632cdb5dcc052e690eab439e1b4a7e3e9cfe407/src/gepa/core/engine.py), [pinned reflective proposer](https://github.com/gepa-ai/gepa/tree/0632cdb5dcc052e690eab439e1b4a7e3e9cfe407/src/gepa/proposer/reflective_mutation), [pinned meta-harness](https://github.com/gepa-ai/gepa/blob/0632cdb5dcc052e690eab439e1b4a7e3e9cfe407/src/gepa/oa/engines/meta_harness.py), and [paper](https://arxiv.org/abs/2507.19457).

## What is interpretation or advocacy

“Optimize anything” means any serialized artifact for which the user supplies a meaningful evaluator and execution adapter. It does not remove representation design, safety engineering, measurement error, or the risk that an LM proposer exploits the evaluator.

## Limitations, incentives, and likely biases

Search quality depends on evaluator fidelity, trace informativeness, proposal-model behavior, and budget. Validation reuse creates adaptive overfitting risk. Arbitrary code candidates require a containment layer outside the generic optimizer. The optional meta-harness is only layered openness: its engine/state/evaluation code is MIT, while the default proposer is the proprietary Claude Code CLI. Its bwrap/Seatbelt restrictions are configurable and do not prove evaluator-side code is safe. Main moved after v0.1.4, so release and inspected commit must not be conflated.

## Transferable engineering lessons

Expose candidate components, side information, lineage, acceptance, frontier, cost, and held-out evaluation as first-class records. Textual diagnostics can be more actionable than a scalar, but only if the evaluator remains independent of proposal generation.

## Connections to academic work

GEPA connects evolutionary computation, Pareto/quality-diversity selection, reflective prompting, program synthesis, and automated prompt optimization. Its newer meta-harness is directly relevant to AutoDesign, HarnessOpt, HarnessDev, and observability-driven harness-evolution work already catalogued.

## Verification notes

Release metadata and the API, engine, proposer, adapters, `optimize_anything`, and meta-harness at commit `0632cdb5dcc052e690eab439e1b4a7e3e9cfe407` were inspected for the 2026-09-04 cutoff. Features visible only on pinned main are not automatically attributed to v0.1.4.
