---
title: "DSPy Optimizers: MIPROv2 and GEPA/Flex"
author_or_org: "Stanford NLP"
date: "2026-09-04"
source_type: "official-implementation-evidence"
url: "https://github.com/stanfordnlp/dspy"
version_or_commit: "3.3.1 (2026-08-21); main commit 35ef21f1689576c4fbe06c27e22eabb5db1b24b6 (2026-09-04)"
accessed: "2026-09-04"
review_status: "reviewed"
evidence_confidence: "high-for-optimizer-contracts-medium-for-task-transfer"
license_or_access_notes: "MIT; dspy.GEPA delegates its core search engine to the separately MIT-licensed gepa package"
---

# selfopt-dspy — DSPy optimizers

## Why this source is in the corpus

DSPy is the most mature implementation surface in this set for compiling LM programs by optimizing instructions and demonstrations. Its current GEPA/Flex integration also crosses the boundary from prompt optimization into source-code/control-flow optimization.

## System or claim described

DSPy programs define predictors/modules and task metrics. Optimizers compile a student program into a variant with selected instructions, few-shot demonstrations, or—through Flex—module source, while preserving the surrounding application interface.

## Architecture / mechanism

MIPROv2 first bootstraps sets of demonstrations by retaining training examples on which a program produces metric-approved outputs. An instruction proposer summarizes the dataset and program/predictor code, includes candidate demonstrations and a sampled stylistic tip, and creates instruction alternatives. Bayesian optimization then searches the joint assignment of instruction and demonstration candidates across predictors, using minibatch trials and periodic full-validation evaluations.

DSPy's GEPA adapter captures full program and per-predictor traces, calls a metric for numeric score and optional text feedback, and delegates population, Pareto selection, reflection, and merge to `gepa`. Normally each component is a predictor's signature instruction. At the inspected pin, a `dspy.Flex` submodule instead exposes its entire `module_src`, allowing the optimizer to rewrite code as a component.

## Empirical evidence

Official documentation includes executable notebooks and task examples. These establish API behavior and expected workflows, not independent evidence that one optimizer dominates across models, metrics, or datasets. Optimized artifacts should be evaluated on a held-out split not seen by compilation.

## Mathematical or formal content

MIPROv2 searches a finite joint configuration \(z=(i_1,d_1,\ldots,i_k,d_k)\) to maximize validation objective \(f(z)\), using a Bayesian surrogate/acquisition process rather than enumerating every assignment. GEPA treats instruction or source components as a candidate vector and performs reflection-guided evolutionary search over validation score vectors.

## What is directly evidenced

**Official sources:** [repository](https://github.com/stanfordnlp/dspy), [documentation](https://dspy.ai/), [3.3.1 release](https://github.com/stanfordnlp/dspy/releases/tag/3.3.1), [official MIPROv2 mechanism page](https://github.com/stanfordnlp/dspy/blob/35ef21f1689576c4fbe06c27e22eabb5db1b24b6/docs/docs/api/optimizers/MIPROv2.md), [official GEPA overview](https://github.com/stanfordnlp/dspy/blob/35ef21f1689576c4fbe06c27e22eabb5db1b24b6/docs/docs/api/optimizers/GEPA/overview.md), [GEPA implementation/adaptation](https://github.com/stanfordnlp/dspy/blob/35ef21f1689576c4fbe06c27e22eabb5db1b24b6/dspy/teleprompt/gepa/gepa.py), and [GEPA in-depth mechanics](https://github.com/stanfordnlp/dspy/blob/35ef21f1689576c4fbe06c27e22eabb5db1b24b6/docs/docs/diving-deeper/gepa-in-depth.md).

## What is interpretation or advocacy

“Programming—not prompting” is project positioning. At the optimizer boundary, many compiled parameters remain prompts and demonstrations. Flex source mutation is materially broader, but it inherits the safety and evaluation problems of generated program search.

## Limitations, incentives, and likely biases

Optimization depends on a user metric, model/provider behavior, bootstrap success, proposal budget, and dataset composition. In `dspy.GEPA`, `valset` defaults to `trainset` when omitted, making accidental adaptive reuse easy. Reflection and evaluation can dominate cost; generated demonstrations can encode model-specific artifacts. The inspected main commit postdates 3.3.1 and should be pinned separately.

## Transferable engineering lessons

Treat instruction text, demonstrations, module source, metric, training examples, validation examples, and search budget as distinct experimental variables. A compilation API should retain the full candidate lineage and the exact artifact written into the final program.

## Connections to academic work

DSPy links declarative LM programs, Bayesian optimization, few-shot bootstrapping, prompt evolution, and automated program repair. It provides production-quality adapters for mechanisms associated with MIPRO and GEPA rather than a single optimizer theory.

## Verification notes

Release metadata, MIPROv2 and GEPA documentation, and the pinned GEPA/Flex adapter source were inspected at commit `35ef21f1689576c4fbe06c27e22eabb5db1b24b6` for the 2026-09-04 cutoff.
