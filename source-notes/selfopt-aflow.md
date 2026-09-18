---
title: "AFlow: Automating Agentic Workflow Generation"
author_or_org: "FoundationAgents"
date: "2026-09-04"
source_type: "official-implementation-evidence"
url: "https://github.com/FoundationAgents/AFlow"
version_or_commit: "main commit 3f457218fc716093fe53f6df8a5d5e6379d66346 (2025-12-25); no GitHub releases"
accessed: "2026-09-04"
review_status: "reviewed"
evidence_confidence: "high-for-mechanism-medium-for-implications"
license_or_access_notes: "MIT"
---

# selfopt-aflow — AFlow

## Why this source is in the corpus

AFlow is a representative implementation of score-guided mutation over code-represented agent workflows. It is especially useful because the current source makes it possible to compare the paper/README description of an MCTS variant with the selection rule that is actually executed.

## System or claim described

The project claims to automate workflow construction by searching over Python graphs assembled from reusable LLM operators such as Generate, Format, Review, Revise, Ensemble, Test, and Programmer.

## Architecture / mechanism

Each optimization round selects a previously evaluated workflow from the top completed rounds, supplies its graph, prompt, score, execution logs, operator descriptions, and accumulated success/failure notes to an optimizer LM, and asks for a modification plus replacement graph and prompt. Exact repeated modification descriptions are rejected. The new Python workflow is written to disk, loaded, evaluated for a configured number of validation rounds, and recorded as a success only when its average score exceeds its parent's score. Convergence checking is optional.

## Empirical evidence

The repository supplies evaluator code for HumanEval, MBPP, GSM8K, MATH, HotpotQA, and DROP, plus links to project-generated workflows, prompts, trajectories, and datasets. These materials support reproduction attempts but are not independent evidence that AFlow isolates a harness effect from model, prompt, budget, and benchmark choices.

## Mathematical or formal content

For retained candidates with scores \(s_i\), the implementation samples a parent using

\[
p_i=\frac{\lambda}{n}+(1-\lambda)
\frac{\exp(100\alpha s_i)}{\sum_j\exp(100\alpha s_j)},
\qquad \alpha=0.2,\ \lambda=0.3.
\]

This is an exploration/exploitation mixture over completed rounds. The inspected code does not expose conventional UCT statistics or an explicit tree policy.

## What is directly evidenced

**Official sources:** [repository](https://github.com/FoundationAgents/AFlow), [pinned optimizer](https://github.com/FoundationAgents/AFlow/blob/3f457218fc716093fe53f6df8a5d5e6379d66346/scripts/optimizer.py), [pinned parent-sampling code](https://github.com/FoundationAgents/AFlow/blob/3f457218fc716093fe53f6df8a5d5e6379d66346/scripts/optimizer_utils/data_utils.py), [pinned experience code](https://github.com/FoundationAgents/AFlow/blob/3f457218fc716093fe53f6df8a5d5e6379d66346/scripts/optimizer_utils/experience_utils.py), [README](https://github.com/FoundationAgents/AFlow/blob/3f457218fc716093fe53f6df8a5d5e6379d66346/README.md), and [paper](https://arxiv.org/abs/2410.10762).

The pinned source directly evidences score-biased parent sampling, LLM-generated Python mutations, validation scoring, experience persistence, and the absence of an execution sandbox in this optimization layer.

## What is interpretation or advocacy

Calling the released loop “MCTS” is project framing. A more implementation-faithful description is stochastic local/evolutionary search over an archive of completed workflows, with an LM as mutation operator and benchmark score as fitness.

## Limitations, incentives, and likely biases

Reproduction depends on live model APIs, stochastic generation, external Drive-hosted artifacts, benchmark-specific evaluator code, and execution of generated Python. The README warns that some operators may contain migration bugs. At the inspected pin, the experience formatter prefixes both failed and successful modifications with “Absolutely prohibit,” which can invert useful feedback. The repository is unarchived but had no code push after 2025-12-25 and has no tagged release.

## Transferable engineering lessons

Record the executable parent-selection rule, mutation prompt, validation sampling, and acceptance rule separately. Algorithm labels such as “MCTS” are not adequate treatment descriptions without matching tree state and selection statistics.

## Connections to academic work

AFlow connects LLM program synthesis, evolutionary search, neural-architecture-search-style evaluation, and reflection-based improvement. Its code/paper mismatch is also relevant to research on whether published agent-search abstractions survive repository migration.

## Verification notes

Repository metadata, README, optimizer, sampling, experience, and evaluator surfaces were inspected at commit `3f457218fc716093fe53f6df8a5d5e6379d66346` for the 2026-09-04 cutoff. Implementation statements above refer to that pin, not an unversioned project name.
