---
title: "AgentSquare: Automatic LLM Agent Search in Modular Design Space"
author_or_org: "Tsinghua FIB Lab"
date: "2026-09-04"
source_type: "official-implementation-evidence"
url: "https://github.com/tsinghua-fib-lab/AgentSquare"
version_or_commit: "main commit 8f5b3fe5d8a32f9b59d20370823bef2a2c86928c (2025-11-04); no GitHub releases"
accessed: "2026-09-04"
review_status: "reviewed"
evidence_confidence: "high-for-code-low-for-runnability"
license_or_access_notes: "No root license detected; public source is not legally open-source by default"
---

# selfopt-agentsquare — AgentSquare

## Why this source is in the corpus

AgentSquare represents modular agent search: it generates implementations inside named planning, reasoning, tool-use, and memory categories, then searches over compositions. It also provides a useful case where implementation defects materially qualify the paper-level mechanism.

## System or claim described

The released ALFWorld search combines module evolution, benchmark evaluation, module recombination, and an LM-based performance predictor intended to reduce the number of expensive candidate evaluations.

## Architecture / mechanism

The search starts from a hard-coded `(None, IO, None, None)` agent and score `0.56`. For ten iterations, an LM proposes new module Python code; generated modules and composed agents are benchmarked; the incumbent is greedily replaced when measured performance improves. An LM then recombines known module names into new tuples. A separate LM predicts their scores, and only the highest predicted recombination is benchmarked. Some evaluations run in a `ProcessPoolExecutor`, while generated classes are appended to task source modules and later removed.

## Empirical evidence

The repository includes task forks and evaluator plumbing for ALFWorld and other domains. The inspected implementation directly demonstrates a runnable search design in outline, but the code defects below prevent treating repository outputs as clean replication evidence without repair and result auditing.

## Mathematical or formal content

For module sets \(P,R,T,M\), the nominal discrete composition space has size

\[
|\mathcal A|=|P|\,|R|\,|T|\,|M|.
\]

The predictor acts as a surrogate \(\hat f(a)\) used to choose one candidate for true evaluation \(f(a)\); the incumbent update is \(a_{t+1}=a'\) only if \(f(a')>f(a_t)\). No calibrated error bound for \(\hat f\) is implemented.

## What is directly evidenced

**Official sources:** [repository](https://github.com/tsinghua-fib-lab/AgentSquare), [pinned search loop](https://github.com/tsinghua-fib-lab/AgentSquare/blob/8f5b3fe5d8a32f9b59d20370823bef2a2c86928c/search/agent_search.py), [pinned module evolution](https://github.com/tsinghua-fib-lab/AgentSquare/blob/8f5b3fe5d8a32f9b59d20370823bef2a2c86928c/module_evolution/module_evolution.py), [pinned recombination](https://github.com/tsinghua-fib-lab/AgentSquare/blob/8f5b3fe5d8a32f9b59d20370823bef2a2c86928c/module_recombination/module_recombination.py), and [pinned performance predictor](https://github.com/tsinghua-fib-lab/AgentSquare/blob/8f5b3fe5d8a32f9b59d20370823bef2a2c86928c/module_predictor/module_predictor.py).

The source directly evidences fixed-iteration greedy search, generated code insertion, predictor-gated evaluation, hard-coded model/baseline choices, and explicit exclusion of tool-use agents in the ALFWorld path.

## What is interpretation or advocacy

“Automatic agent search” is accurate at the orchestration level, but claims about all four modular dimensions require qualification: the inspected ALFWorld loop generates tool-use modules yet filters every agent using them before evaluation.

## Limitations, incentives, and likely biases

There is no root license. The recombination code uses `eval(response)`, generated Python is executed without an evident sandbox, and paths/models are task-specific. More seriously, futures are created in planning/reasoning/memory order but their results are zipped back against a reasoning/planning/memory dictionary order, so planning and reasoning module scores can be misassigned. The repository is unarchived but has no code push after 2025-11-04 and no tagged release.

## Transferable engineering lessons

Search systems need typed candidate records and invariant-preserving result attribution. A surrogate evaluator saves calls only when its ranking quality is measured, and a conceptual search dimension should not be reported as explored when implementation filters it out.

## Connections to academic work

AgentSquare combines modular neural architecture search, evolutionary program generation, greedy best-so-far selection, and learned/synthetic surrogate scoring. It is a concrete comparison point for ADAS-style open-ended code search and AgentOpt-style fixed model-assignment search.

## Verification notes

Repository metadata and the search, evolution, recombination, and predictor modules were inspected at commit `8f5b3fe5d8a32f9b59d20370823bef2a2c86928c` for the 2026-09-04 cutoff. Absence of a root license was checked through repository metadata and tree inspection.
