---
title: "TextGrad: Automatic Differentiation via Text"
author_or_org: "Zou Group"
date: "2026-09-04"
source_type: "official-implementation-evidence"
url: "https://github.com/zou-group/textgrad"
version_or_commit: "v0.1.6 (2024-12-15); main commit 75e912e210864b61999781778cdf756d4468120f (2025-07-25)"
accessed: "2026-09-04"
review_status: "reviewed"
evidence_confidence: "high-for-mechanism-medium-for-optimization-analogy"
license_or_access_notes: "MIT"
---

# selfopt-textgrad — TextGrad

## Why this source is in the corpus

TextGrad is the canonical implementation of the textual-gradient metaphor. It can optimize prompts, code, solutions, or other text and therefore clarifies what “backpropagation” means—and does not mean—in LM-based self-improvement systems.

## System or claim described

TextGrad provides a PyTorch-like computation graph of textual `Variable` objects. LM operations install backward functions; a backward engine produces natural-language criticism; Textual Gradient Descent asks an optimizer LM to rewrite trainable variables from that criticism.

## Architecture / mechanism

Variables record values, semantic role descriptions, predecessors, gradient text, gradient context, and reduction metadata. `backward()` topologically traverses the graph in reverse and invokes LM-backed gradient functions for trainable nodes. Multiple feedback strings may be reduced by another LM. `TextualGradientDescent.step()` builds a prompt containing the variable, its role, aggregated feedback/context, optional natural-language constraints, examples, and gradient history; it extracts text between required tags and immediately replaces the variable. A momentum variant supplies past values and feedback.

## Empirical evidence

The repository provides notebooks and task suites for prompt, solution, code, and multimodal optimization and links the published Nature paper. Those results concern particular forward/backward models, tasks, and iteration policies. The implementation itself provides no automatic held-out evaluator around each update.

## Mathematical or formal content

A faithful abstraction is

\[
g_x=\operatorname{LM}_{\mathrm{back}}(x,\tau,L),
\qquad
x'=\operatorname{LM}_{\mathrm{opt}}(x,g_x,\mathcal C),
\]

where \(g_x\) is text and \(\mathcal C\) contains optional constraints/history. This is not a numerical derivative, need not be locally linear, and supplies no descent guarantee. The computation graph controls feedback routing, not differentiability in the analytic sense.

## What is directly evidenced

**Official sources:** [repository](https://github.com/zou-group/textgrad), [documentation](https://textgrad.readthedocs.io/), [v0.1.6 release](https://github.com/zou-group/textgrad/releases/tag/v0.1.6), [pinned Variable/backward traversal](https://github.com/zou-group/textgrad/blob/75e912e210864b61999781778cdf756d4468120f/textgrad/variable.py), [pinned TGD implementation](https://github.com/zou-group/textgrad/blob/75e912e210864b61999781778cdf756d4468120f/textgrad/optimizer/optimizer.py), [pinned backward prompts](https://github.com/zou-group/textgrad/blob/75e912e210864b61999781778cdf756d4468120f/textgrad/autograd/llm_backward_prompts.py), and [paper](https://arxiv.org/abs/2406.07496).

## What is interpretation or advocacy

“Autograd,” “gradient,” “chain rule,” and “descent” are API analogies. They help organize compositional feedback but should not be imported into proofs or convergence claims as if the update were calculus over a normed parameter space.

## Limitations, incentives, and likely biases

`TGD.step()` installs the proposed rewrite without reevaluating the objective, line search, trust region, or rollback; applications must implement that outer loop. Tagged-output parsing can fail. Results depend on both forward and backward LMs, feedback prompt, reduction ordering, and provider behavior. The README marks the LiteLLM engine transition experimental. The last release predates the last commit, and no code push occurred after 2025-07-25.

## Transferable engineering lessons

Textual feedback can be routed through a program graph, but every update should still be evaluated, versioned, and reversible. Papers should distinguish feedback propagation from objective-improving acceptance.

## Connections to academic work

TextGrad builds on ProTeGi-style textual gradients and connects prompt optimization, automatic differentiation interfaces, Reflexion, and LM-based program repair. GEPA differs by adding an explicit population/frontier and validation acceptance loop.

## Verification notes

Release metadata, README, variable graph, backward prompts, and TGD/momentum optimizers were inspected at commit `75e912e210864b61999781778cdf756d4468120f` for the 2026-09-04 cutoff.
