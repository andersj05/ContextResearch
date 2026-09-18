---
title: "EvoAgent: Towards Automatic Multi-Agent Generation via Evolutionary Algorithms"
author_or_org: "Siyu Yuan et al."
date: "2026-09-04"
source_type: "official-implementation-evidence"
url: "https://github.com/siyuyuan/evoagent"
version_or_commit: "main commit fc6d087b119df69466c2372cfcaf588c040aaba8 (2024-10-19); no GitHub releases"
accessed: "2026-09-04"
review_status: "reviewed"
evidence_confidence: "high-for-released-loop-medium-for-paper-alignment"
license_or_access_notes: "No root license detected; a nested TravelPlanner license does not license the repository as a whole"
---

# selfopt-evoagent — EvoAgent

## Why this source is in the corpus

EvoAgent is included both as a role-generation mechanism and as a terminology counterexample. Its released primary paths implement per-instance agent proliferation and answer refinement, which is narrower than persistent population-level harness optimization.

## System or claim described

The project describes a generic method for extending a predefined expert agent into a multi-agent system by repeatedly generating additional expert roles and integrating their outputs.

## Architecture / mechanism

For each task instance, a base model first produces an answer. A meta-agent proposes a new expert description conditioned on the question, current answer, and prior descriptions. A checker LM rejects duplicate or unsuitable descriptions for a bounded number of retries. The accepted expert produces a sub-answer, and a refiner LM combines the prior answer, expert description, and sub-answer into a new answer. This repeats for `ind` rounds. A separate group ablation creates several experts per round and uses random choice, LM selection, or all-expert aggregation.

## Empirical evidence

The repository contains experiment paths and archived result bundles for SPP tasks, MMMU, ScienceWorld, and TravelPlanner. These are project-authored artifacts. The code supports reproduction of the inference procedure but does not expose a reusable dataset-level architecture optimizer shared across the domains.

## Mathematical or formal content

A faithful abstraction of the primary path is sequential refinement:

\[
d_t\sim G(x,a_t,d_{<t}),\qquad
u_t\sim E(x,d_t),\qquad
a_{t+1}=R(x,a_t,d_t,u_t).
\]

There is no persistent population fitness \(f(d)\), cross-instance selection, or retained architecture archive in the inspected SPP/MMMU loops.

## What is directly evidenced

**Official sources:** [repository](https://github.com/siyuyuan/evoagent), [project page](https://evo-agent.github.io/), [pinned SPP loop](https://github.com/siyuyuan/evoagent/blob/fc6d087b119df69466c2372cfcaf588c040aaba8/spp/util_func.py), [pinned MMMU loop](https://github.com/siyuyuan/evoagent/blob/fc6d087b119df69466c2372cfcaf588c040aaba8/mmmu/run_evoagent.py), [pinned TravelPlanner loop](https://github.com/siyuyuan/evoagent/blob/fc6d087b119df69466c2372cfcaf588c040aaba8/travelplanner/tools/planner/sole_planning.py), and [paper](https://arxiv.org/abs/2406.14228).

The source directly evidences task-local description generation, checker filtering, expert response generation, refinement, and group-selection ablations.

## What is interpretation or advocacy

The biological/evolutionary framing is advocacy. The released primary implementation is better described as iterative runtime role diversification and synthesis. That does not make it ineffective, but it changes the experimental object from an optimized reusable harness to additional inference-time computation.

## Limitations, incentives, and likely biases

There is no root license. Code is duplicated across task forks, model identifiers and SDK calls are historical, TravelPlanner needs an external database, and one API retry loop can continue an extremely large number of times. Evaluation bundles are not independent replications. The repository has no tagged release and no code push after 2024-10-19.

## Transferable engineering lessons

Separate persistent self-improvement from per-instance deliberation. A growing cast of temporary roles changes inference budget and aggregation behavior but does not necessarily learn or retain a better harness.

## Connections to academic work

EvoAgent connects persona prompting, self-refinement, ensemble deliberation, and evolutionary metaphors. It is a useful contrast with AgentSquare's persistent module archive and ADAS's executable program archive.

## Verification notes

Repository metadata, root licensing state, and representative SPP, MMMU, and TravelPlanner implementations were inspected at commit `fc6d087b119df69466c2372cfcaf588c040aaba8` for the 2026-09-04 cutoff.
