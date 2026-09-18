---
title: "Semantic Kernel"
author_or_org: "Microsoft"
date: "2026-09-04"
source_type: "official-implementation-evidence"
url: "https://github.com/microsoft/semantic-kernel"
version_or_commit: "dotnet-1.80.1; commit f8c5ba7aec210c986086a997fc4eef65190666eb"
accessed: "2026-09-04"
review_status: "reviewed"
evidence_confidence: "high-for-mechanism-medium-for-implications"
license_or_access_notes: "MIT"
---

# harness-semantic-kernel — Semantic Kernel

## Why this source is in the corpus

This implementation represents the **explicit-graph-runtime** family in the comparative survey. It is included to describe a reproducible mechanism and its treatment variables, not to endorse the project or convert project-authored results into independent evidence.

## System or claim described

An SDK and orchestration framework with kernel functions, agent threads, tool calling, multiple orchestration patterns, and OpenTelemetry.

## Architecture / mechanism

A Kernel registers functions/plugins and participates in a model function-calling loop. `AgentThread` abstracts local or service-hosted conversation state. Orchestration packages implement concurrent, sequential, handoff, group-chat, and Magentic patterns. Older planner APIs were removed in favor of function calling as the planning mechanism. Contextual function selection can use embeddings to reduce the visible function set. The Process Framework and several memory capabilities provide explicit stateful workflows but are marked experimental. Telemetry follows OpenTelemetry conventions.

## Empirical evidence

The inspected repository, documentation, and release records directly support the implementation description. They do not constitute a controlled, independent estimate of the harness's effect. Any project-authored benchmark or telemetry should be reproduced with a pinned model, prompt, environment, budget, and scorer before comparative use.

## Mathematical or formal content

A useful abstraction is a labelled transition system \(s_{t+1}=U_{\ell_t}(s_t,o_t)\), where graph topology, reducer rules, and scheduling determine the admissible transition relation. The implementation does not by itself establish a performance theorem.

## What is directly evidenced

**Official sources:** [repository](https://github.com/microsoft/semantic-kernel), [overview](https://learn.microsoft.com/en-us/semantic-kernel/overview/), [agents](https://learn.microsoft.com/en-us/semantic-kernel/frameworks/agent/), [orchestration](https://learn.microsoft.com/en-us/semantic-kernel/frameworks/agent/agent-orchestration/), [process framework](https://learn.microsoft.com/en-us/semantic-kernel/frameworks/process/process-framework), [license](https://github.com/microsoft/semantic-kernel/blob/main/LICENSE).

The detailed comparison pins the inspected release or commit, license, loop/state design, action representation, context and memory policy, concurrency, containment, and observability surface.

## What is interpretation or advocacy

Semantic Kernel illustrates a broad industry shift from symbolic “planner” objects to model-mediated function selection. That renaming should not be interpreted as the disappearance of planning; it changes where the routing policy resides and how observable it is.

## Limitations, incentives, and likely biases

Core functions are arbitrary application code and have no universal OS sandbox. Multiple experimental/transitional APIs and the Microsoft Agent Framework successor warning limit longitudinal comparability. No intrinsic neutral task evaluator was found in the core. **Confidence: high** for documented APIs; **medium** for successor-era stability.

Project documentation optimizes for adoption and correct use, not neutral causal comparison. Fast-moving release streams also make unversioned project names unreliable experimental treatments.

## Transferable engineering lessons

Treat experimental APIs and successor transitions as reproducibility risks, and distinguish orchestration from containment and independent evaluation.

## Connections to academic work

See the mechanism taxonomy in [`01-definitions-and-taxonomy.md`](../synthesis/01-definitions-and-taxonomy.md), the architecture analysis in [`02-architecture-and-design-patterns.md`](../synthesis/02-architecture-and-design-patterns.md), and the full implementation comparison in [`05-open-source-harnesses.md`](../synthesis/05-open-source-harnesses.md).

## Verification notes

The sources and pinned snapshot were inspected for the 2026-09-04 research cutoff. Version discontinuities and openness caveats are recorded in the full survey. No repository snapshot is redistributed here; the canonical source URL and commit or release identifier are retained.
