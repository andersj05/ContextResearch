---
title: "Automated Design of Agentic Systems (ADAS): Meta Agent Search"
author_or_org: "Shengran Hu, Cong Lu, and Jeff Clune"
date: "2026-09-04"
source_type: "official-implementation-evidence"
url: "https://github.com/ShengranHu/ADAS"
version_or_commit: "main commit 2702bee8fefda42255efc5be9f60e3bd3db96ae4 (2025-01-28); no GitHub releases"
accessed: "2026-09-04"
review_status: "reviewed"
evidence_confidence: "high-for-mechanism-medium-for-implications"
license_or_access_notes: "Apache-2.0"
---

# selfopt-adas — ADAS / Meta Agent Search

## Why this source is in the corpus

ADAS is the clearest early open implementation of unrestricted agent-program search: the optimized object is an executable agent method rather than a prompt, fixed graph mask, or tuple of predefined modules.

## System or claim described

Meta Agent Search asks a meta-level LM to invent agent systems as Python code using an archive of prior designs and fitness values, then evaluates each invented program on a task domain.

## Architecture / mechanism

Each benchmark folder is substantially self-contained. The search evaluates a seed archive, prompts a meta-LM with prior discoveries, requests a new `forward` implementation, and performs two LM reflection/revision passes. The code is installed dynamically with `exec`, run on validation examples through a thread pool, and repaired by feeding exceptions or near-zero accuracy back to the LM for up to three debugging attempts. An executable candidate receives bootstrap confidence-interval fitness metadata and is appended to the archive whether or not it beats the incumbent. A separate evaluation mode scores archived designs on the test split.

## Empirical evidence

The repository contains domain-specific search and evaluation code for MGSM, ARC, DROP, MMLU, and related tasks. It supports inspection and partial reproduction of the published algorithm, but benchmark-specific duplication, historical APIs, and unsafe execution make results sensitive to environment reconstruction.

## Mathematical or formal content

Let \(c_t\) be candidate source code, \(H_t\) the archive, and \(D_v\) validation data. The implemented abstraction is

\[
c_{t+1}\sim q_\phi(\cdot\mid H_t),\qquad
\hat f(c)=\frac{1}{|D_v|}\sum_{x\in D_v} r(c,x),
\]

with a bootstrap interval reported around the empirical score. The archive update retains valid candidates rather than only improvements; no convergence or generalization theorem is supplied.

## What is directly evidenced

**Official sources:** [repository](https://github.com/ShengranHu/ADAS), [project page](https://www.shengranhu.com/ADAS/), [pinned MGSM search](https://github.com/ShengranHu/ADAS/blob/2702bee8fefda42255efc5be9f60e3bd3db96ae4/_mgsm/search.py), [pinned ARC search](https://github.com/ShengranHu/ADAS/blob/2702bee8fefda42255efc5be9f60e3bd3db96ae4/_arc/search.py), [README and safety warning](https://github.com/ShengranHu/ADAS/blob/2702bee8fefda42255efc5be9f60e3bd3db96ae4/README.md), and [paper](https://arxiv.org/abs/2408.08435).

The source directly evidences archive-conditioned program proposal, double reflection, exception-driven repair, threaded evaluation, bootstrap reporting, and dynamic code execution.

## What is interpretation or advocacy

The implementation demonstrates that an LM can participate in open-ended program search; it does not by itself establish that discovered designs are novel, robust, or causally superior to equal-budget human or algorithmic baselines.

## Limitations, incentives, and likely biases

The README explicitly warns that model-generated code may act destructively. There is no sandbox in the search scripts. Reproduction depends on old named models, live APIs, stochastic generations, benchmark-specific prompts, and duplicated code. The small research snapshot has no tagged release and no code push after 2025-01-28.

## Transferable engineering lessons

Separate proposal, repair, containment, fitness estimation, archive policy, and held-out evaluation. Arbitrary program search expands expressivity but also expands the attack surface and the number of uncontrolled experimental factors.

## Connections to academic work

ADAS connects program synthesis, quality-diversity/open-ended search, reflective repair, evolutionary computation, and automated machine-learning ideas. It is a direct precursor/comparator for later meta-harness and harness-evolution systems.

## Verification notes

The README and representative benchmark search implementations were inspected at commit `2702bee8fefda42255efc5be9f60e3bd3db96ae4` for the 2026-09-04 cutoff. Safety and algorithm statements are tied to the pinned repository rather than inferred from the paper alone.
