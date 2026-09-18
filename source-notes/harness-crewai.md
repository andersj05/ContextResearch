---
title: "CrewAI"
author_or_org: "CrewAI"
date: "2026-09-04"
source_type: "official-implementation-evidence"
url: "https://github.com/crewAIInc/crewAI"
version_or_commit: "1.15.20; commit c00e3228fc0036e6d262592b5943979659fcfdac"
accessed: "2026-09-04"
review_status: "reviewed"
evidence_confidence: "high-for-mechanism-medium-for-implications"
license_or_access_notes: "MIT core"
---

# harness-crewai — CrewAI

## Why this source is in the corpus

This implementation represents the **explicit-graph-runtime** family in the comparative survey. It is included to describe a reproducible mechanism and its treatment variables, not to endorse the project or convert project-authored results into independent evidence.

## System or claim described

A role-agent and event-flow framework spanning sequential or hierarchical crews, typed flow state, planning, delegation, memory, and tool execution.

## Architecture / mechanism

CrewAI contains two control abstractions: Crews execute role/task configurations sequentially or through a hierarchical manager; Flows use event listeners, routers, branches, loops, and explicit state. Optional planning performs an additional planning-model pass. The memory layer extracts facts and scores recall using semantic similarity, recency, and importance. Flow persistence supports checkpoint, resume, and fork behavior. Code execution is opt-in and distinguishes Docker-oriented “safe” mode from direct local “unsafe” mode. Hooks and external tracing integrations expose runs; test tooling can repeat executions and use LLM-based scoring.

## Empirical evidence

The inspected repository, documentation, and release records directly support the implementation description. They do not constitute a controlled, independent estimate of the harness's effect. Any project-authored benchmark or telemetry should be reproduced with a pinned model, prompt, environment, budget, and scorer before comparative use.

## Mathematical or formal content

A useful abstraction is a labelled transition system \(s_{t+1}=U_{\ell_t}(s_t,o_t)\), where graph topology, reducer rules, and scheduling determine the admissible transition relation. The implementation does not by itself establish a performance theorem.

## What is directly evidenced

**Official sources:** [repository](https://github.com/crewAIInc/crewAI), [documentation](https://docs.crewai.com/), [Crews](https://docs.crewai.com/en/concepts/crews), [Flows](https://docs.crewai.com/en/concepts/flows), [planning](https://docs.crewai.com/en/concepts/planning), [memory](https://docs.crewai.com/en/concepts/memory), [license](https://github.com/crewAIInc/crewAI/blob/main/LICENSE).

The detailed comparison pins the inspected release or commit, license, loop/state design, action representation, context and memory policy, concurrency, containment, and observability surface.

## What is interpretation or advocacy

Crews and Flows should be separate experimental categories: role-based delegation and explicit event graphs have different causal mechanisms. Composite memory can be represented schematically as

\[
R(m,q)=\alpha\,\mathrm{sim}(m,q)+\beta\,\mathrm{recency}(m)+\gamma\,\mathrm{importance}(m),
\]

but actual normalization, extraction errors, and weights must be pinned before the formula is scientifically meaningful.

## Limitations, incentives, and likely biases

Planner output is another model-generated prompt artifact, not a proven search plan. Crews, Flow state, and memory create overlapping state surfaces. LLM-as-judge tests introduce provider, prompt, calibration, and self-preference confounds. “Safe” mode means the configured container path, not a universal proof of containment. **Confidence: high** for interfaces; **medium** for memory/scoring effects.

Project documentation optimizes for adoption and correct use, not neutral causal comparison. Fast-moving release streams also make unversioned project names unreliable experimental treatments.

## Transferable engineering lessons

Do not conflate role prompts with independent agents; report process topology, manager policy, code-execution mode, and evaluator dependence.

## Connections to academic work

See the mechanism taxonomy in [`01-definitions-and-taxonomy.md`](../synthesis/01-definitions-and-taxonomy.md), the architecture analysis in [`02-architecture-and-design-patterns.md`](../synthesis/02-architecture-and-design-patterns.md), and the full implementation comparison in [`05-open-source-harnesses.md`](../synthesis/05-open-source-harnesses.md).

## Verification notes

The sources and pinned snapshot were inspected for the 2026-09-04 research cutoff. Version discontinuities and openness caveats are recorded in the full survey. No repository snapshot is redistributed here; the canonical source URL and commit or release identifier are retained.
