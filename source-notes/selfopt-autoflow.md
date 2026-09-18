---
title: "AutoFlow: Automated Workflow Generation for Large Language Model Agents"
author_or_org: "AGI Research / Zelong Li et al."
date: "2026-09-04"
source_type: "official-implementation-evidence"
url: "https://github.com/agiresearch/AutoFlow"
version_or_commit: "main commit 47203078a17e6612c79fe190d437ea58ae8c4d51 (2024-09-11); no GitHub releases"
accessed: "2026-09-04"
review_status: "reviewed"
evidence_confidence: "high-for-mechanism-medium-low-for-reproducibility"
license_or_access_notes: "Apache-2.0"
---

# selfopt-autoflow — AutoFlow

## Why this source is in the corpus

AutoFlow represents natural-language workflow-program generation rather than Python program synthesis. It also exposes two distinct optimizer choices: in-context black-box revision with a closed model and PPO training of an open workflow generator.

## System or claim described

The system generates workflows in a CoRE-style text DSL intended to be easier for an LLM interpreter to execute than arbitrary source code. A workflow line encodes a step name, process/decision/terminal type, natural-language instruction, and keyed outgoing branches.

## Architecture / mechanism

The in-context path starts from a manual workflow, evaluates it, and puts the workflow plus scalar performance into a meta-LM conversation. Each epoch asks for a new complete workflow, overwrites the candidate file, executes it on training tasks, and supplies the resulting score or exception for the next proposal. When training performance beats the incumbent, the code evaluates a validation/test split. The open-model path samples workflows from a LoRA-equipped generator, uses a separate GPT grammar checker/repairer, scores the result through the executor, and applies PPO to the generator.

## Empirical evidence

The repository provides manual and generated workflows for OpenAGI and TravelPlanner, task-specific evaluators, and exact dependency guidance. External datasets/databases are required. These artifacts evidence the implementation path but do not independently establish that natural-language programs are more reliable under contemporary models.

## Mathematical or formal content

The in-context optimizer is a history-conditioned black-box process,

\[
w_{t+1}\sim q_\phi(\cdot\mid w_{\le t},f(w_{\le t}),e_{\le t}),
\qquad b_{t+1}=\max\{b_t,f(w_{t+1})\},
\]

although the next proposal is conditioned on the latest candidate even when it regresses. The alternative path applies a standard PPO update to the workflow-generating policy; the repository supplies no workflow-specific convergence theorem.

## What is directly evidenced

**Official sources:** [repository](https://github.com/agiresearch/AutoFlow), [pinned README blob](https://github.com/agiresearch/AutoFlow/blob/47203078a17e6612c79fe190d437ea58ae8c4d51/README.md), [pinned optimization entry point](https://github.com/agiresearch/AutoFlow/blob/47203078a17e6612c79fe190d437ea58ae8c4d51/src/auto_main.py), [pinned flow parser](https://github.com/agiresearch/AutoFlow/blob/47203078a17e6612c79fe190d437ea58ae8c4d51/src/flow/flow.py), [pinned block grammar](https://github.com/agiresearch/AutoFlow/blob/47203078a17e6612c79fe190d437ea58ae8c4d51/src/flow/block.py), and [paper](https://arxiv.org/abs/2407.12821).

The source directly evidences the DSL, scalar/error feedback loop, full-file replacement, optional grammar repair, benchmark execution, and PPO generator path.

## What is interpretation or advocacy

The assertion that natural-language programs have a higher executable rate is a project claim tied to its parser, tasks, and historical models. The DSL reduces syntax but leaves semantic branch correctness, termination, and instruction ambiguity to the interpreter.

## Limitations, incentives, and likely biases

Reproduction needs separately downloaded OpenAGI and TravelPlanner data, historical API models, specific CUDA/TRL versions, and local workflow execution. The README documents a PPOTrainer incompatibility. The OpenAGI path observes test results each time training improves rather than reserving a single untouched final test. There is no release and no code push after 2024-09-11.

## Transferable engineering lessons

Workflow representation is an experimental factor. A constrained text grammar can improve parseability while still requiring static graph checks, execution containment, held-out evaluation, and explicit incumbent/rollback semantics.

## Connections to academic work

AutoFlow connects program induction, natural-language programming, black-box prompt optimization, and reinforcement learning. It provides a lower-syntax alternative to ADAS's Python search and AFlow's operator-based code search.

## Verification notes

The README blob, optimizer, DSL parser, and metadata were inspected at commit `47203078a17e6612c79fe190d437ea58ae8c4d51` for the 2026-09-04 cutoff. The README contents endpoint was inconsistent, so the canonical Git blob and pinned browser URL were cross-checked.
