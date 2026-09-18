---
title: "AutoGen"
author_or_org: "Microsoft"
date: "2026-09-04"
source_type: "official-implementation-evidence"
url: "https://github.com/microsoft/autogen"
version_or_commit: "python-v0.7.5; commit 027ecf0a379bcc1d09956d46d12d44a3ad9cee14"
accessed: "2026-09-04"
review_status: "reviewed"
evidence_confidence: "high-for-mechanism-medium-for-implications"
license_or_access_notes: "MIT code; CC-BY-4.0 documentation"
---

# harness-autogen — AutoGen

## Why this source is in the corpus

This implementation represents the **actor-message-runtime** family in the comparative survey. It is included to describe a reproducible mechanism and its treatment variables, not to endorse the project or convert project-authored results into independent evidence.

## System or claim described

An actor and multi-agent framework with message runtimes, stateful team loops, tools, code executors, memory protocols, and telemetry.

## Architecture / mechanism

AutoGen Core is an event-driven actor/message runtime. AgentChat supplies higher-level stateful agents and team patterns, including round-robin, selector, swarm, and Magentic-style coordination. `AssistantAgent` can execute tools, iterate tool calls, and use a memory protocol. Agents and teams expose save/load state. Code execution can be local or Docker-backed. Tracing integrates with OpenTelemetry.

## Empirical evidence

The inspected repository, documentation, and release records directly support the implementation description. They do not constitute a controlled, independent estimate of the harness's effect. Any project-authored benchmark or telemetry should be reproduced with a pinned model, prompt, environment, budget, and scorer before comparative use.

## Mathematical or formal content

The runtime can be represented as communicating state machines with local states \(s_t^{(i)}\) and messages \(m_{i\to j,t}\). Correctness depends on delivery, ordering, shared-resource, and termination assumptions that project documentation does not generally prove.

## What is directly evidenced

**Official sources:** [repository](https://github.com/microsoft/autogen), [stable documentation](https://microsoft.github.io/autogen/stable/), [Core concepts](https://microsoft.github.io/autogen/stable/user-guide/core-user-guide/core-concepts/architecture.html), [AgentChat](https://microsoft.github.io/autogen/stable/user-guide/agentchat-user-guide/index.html), [MIT code license](https://github.com/microsoft/autogen/blob/main/LICENSE-CODE), [CC-BY-4.0 repository-content license](https://github.com/microsoft/autogen/blob/main/LICENSE).

The detailed comparison pins the inspected release or commit, license, loop/state design, action representation, context and memory policy, concurrency, containment, and observability surface.

## What is interpretation or advocacy

The two-layer design distinguishes transport/scheduling from conversational policy, which is useful for experiments on topology. Named team patterns should be treated as routing algorithms plus prompts and termination rules—not as evidence that dialogue among agents improves task accuracy.

## Limitations, incentives, and likely biases

The repository is community-maintained and Microsoft directs new work to Microsoft Agent Framework. Older AGBench and AutoGen 0.2 results do not directly validate current 0.7.x APIs. Local execution is not isolated. **Confidence: high** for current documented mechanics; **medium** for continuity with prior evaluations.

Project documentation optimizes for adoption and correct use, not neutral causal comparison. Fast-moving release streams also make unversioned project names unreliable experimental treatments.

## Transferable engineering lessons

Pin the major architecture generation and successor status; team topology and message protocol are treatment variables, not project-name constants.

## Connections to academic work

See the mechanism taxonomy in [`01-definitions-and-taxonomy.md`](../synthesis/01-definitions-and-taxonomy.md), the architecture analysis in [`02-architecture-and-design-patterns.md`](../synthesis/02-architecture-and-design-patterns.md), and the full implementation comparison in [`05-open-source-harnesses.md`](../synthesis/05-open-source-harnesses.md).

## Verification notes

The sources and pinned snapshot were inspected for the 2026-09-04 research cutoff. Version discontinuities and openness caveats are recorded in the full survey. No repository snapshot is redistributed here; the canonical source URL and commit or release identifier are retained.
