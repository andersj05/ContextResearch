---
title: "OpenHands Software Agent SDK"
author_or_org: "OpenHands"
date: "2026-09-04"
source_type: "official-implementation-evidence"
url: "https://github.com/OpenHands/software-agent-sdk"
version_or_commit: "SDK v1.44.1; commit f47083cc370a85160f0348f32e531ee3514399e5"
accessed: "2026-09-04"
review_status: "reviewed"
evidence_confidence: "high-for-mechanism-medium-for-implications"
license_or_access_notes: "MIT"
---

# harness-openhands — OpenHands Software Agent SDK

## Why this source is in the corpus

This implementation represents the **event-sourced-loop** family in the comparative survey. It is included to describe a reproducible mechanism and its treatment variables, not to endorse the project or convert project-authored results into independent evidence.

## System or claim described

An event-oriented coding-agent SDK in which a stateless policy step is separated from conversation lifecycle, execution, and persistence.

## Architecture / mechanism

In the V1 SDK, `Agent.step()` is intentionally stateless: it receives a view of conversation events and emits typed events. `Conversation` owns state, persistence, execution, lifecycle, and agent coordination. Tools use typed action/observation/executor interfaces and can be extended through MCP. Event files and base state support persistence; context condensers reduce history; an opt-in Markdown memory design distinguishes always-visible durable instructions from discoverable files. Parallel tool calls are configurable, and a task tool can delegate to subagents. A `LocalWorkspace` executes locally, whereas Docker/remote Agent Server modes provide stronger isolation. Security confirmations, event hooks, and OpenTelemetry-compatible tracing are exposed.

## Empirical evidence

The inspected repository, documentation, and release records directly support the implementation description. They do not constitute a controlled, independent estimate of the harness's effect. Any project-authored benchmark or telemetry should be reproduced with a pinned model, prompt, environment, budget, and scorer before comparative use.

## Mathematical or formal content

The common loop is \(a_t\sim\pi_\theta(\cdot\mid C_H(s_t)),\ o_t=E_H(a_t),\ s_{t+1}=U_H(s_t,a_t,o_t)\). Context, executor, update, stopping, and budget are harness parameters; the implementation alone supplies no causal effect estimate.

## What is directly evidenced

**Official sources:** [SDK repository](https://github.com/OpenHands/software-agent-sdk), [product repository](https://github.com/OpenHands/OpenHands), [SDK documentation](https://docs.openhands.dev/sdk/), [benchmarks repository](https://github.com/OpenHands/benchmarks), [license](https://github.com/OpenHands/software-agent-sdk/blob/main/LICENSE).

The detailed comparison pins the inspected release or commit, license, loop/state design, action representation, context and memory policy, concurrency, containment, and observability surface.

## What is interpretation or advocacy

Event sourcing separates the policy transition from orchestration and makes replay, auditing, and counterfactual context experiments cleaner than a mutable monolithic loop. This does not make model calls deterministic: replayability of control-plane events is distinct from repeatability of external side effects or sampled model output.

## Limitations, incentives, and likely biases

V0 papers and source analyses can misdescribe V1. Optional memory and parallelism are configuration choices, not universal properties. The official benchmark package is not an independent evaluator. **Confidence: high** for V1 architecture; **medium** for deployment-specific behavior.

Project documentation optimizes for adoption and correct use, not neutral causal comparison. Fast-moving release streams also make unversioned project names unreliable experimental treatments.

## Transferable engineering lessons

Separate policy transitions from durable orchestration so state reconstruction, replay, context experiments, and audit are explicit.

## Connections to academic work

See the mechanism taxonomy in [`01-definitions-and-taxonomy.md`](../synthesis/01-definitions-and-taxonomy.md), the architecture analysis in [`02-architecture-and-design-patterns.md`](../synthesis/02-architecture-and-design-patterns.md), and the full implementation comparison in [`05-open-source-harnesses.md`](../synthesis/05-open-source-harnesses.md).

## Verification notes

The sources and pinned snapshot were inspected for the 2026-09-04 research cutoff. Version discontinuities and openness caveats are recorded in the full survey. No repository snapshot is redistributed here; the canonical source URL and commit or release identifier are retained.
