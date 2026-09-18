---
title: "LlamaAgents / Workflows"
author_or_org: "LlamaIndex"
date: "2026-09-04"
source_type: "official-implementation-evidence"
url: "https://github.com/run-llama/llama-agents"
version_or_commit: "llama-agents-server@v0.7.1; commit 9bfd8f8ea5d66652d5b6ce933df9cba118f6f863"
accessed: "2026-09-04"
review_status: "reviewed"
evidence_confidence: "high-for-mechanism-medium-for-implications"
license_or_access_notes: "MIT"
---

# harness-llamaagents — LlamaAgents / Workflows

## Why this source is in the corpus

This implementation represents the **explicit-graph-runtime** family in the comparative survey. It is included to describe a reproducible mechanism and its treatment variables, not to endorse the project or convert project-authored results into independent evidence.

## System or claim described

A typed asynchronous workflow runtime with events, tasks, commands, reducer-like state, durable execution, and replay.

## Architecture / mechanism

Workflows are asynchronous, typed, event-driven programs with a `Context` for state and event exchange. The basic runtime schedules work in memory with `asyncio`. A durable DBOS-backed runtime models control-plane evolution as a reducer from state and tick/input to new state plus commands, then persists enough information for rehydration, retry, and replicas. REST/event streaming and human-in-the-loop interactions are supported. The core runtime is model/tool agnostic.

## Empirical evidence

The inspected repository, documentation, and release records directly support the implementation description. They do not constitute a controlled, independent estimate of the harness's effect. Any project-authored benchmark or telemetry should be reproduced with a pinned model, prompt, environment, budget, and scorer before comparative use.

## Mathematical or formal content

A useful abstraction is a labelled transition system \(s_{t+1}=U_{\ell_t}(s_t,o_t)\), where graph topology, reducer rules, and scheduling determine the admissible transition relation. The implementation does not by itself establish a performance theorem.

## What is directly evidenced

**Official sources:** [repository](https://github.com/run-llama/llama-agents), [LlamaIndex Workflows documentation](https://developers.llamaindex.ai/python/framework/module_guides/workflow/), [runtime source](https://github.com/run-llama/llama-agents/tree/main/src), [packages](https://github.com/run-llama/llama-agents/tree/main/packages), [license](https://github.com/run-llama/llama-agents/blob/main/LICENSE).

The detailed comparison pins the inspected release or commit, license, loop/state design, action representation, context and memory policy, concurrency, containment, and observability surface.

## What is interpretation or advocacy

Durable workflow replay can make scheduler state deterministic while external model calls and tools remain stochastic or non-idempotent. A precise claim should therefore distinguish **control-plane replay** from **end-to-end deterministic replay**.

## Limitations, incentives, and likely biases

Durability depends on the selected runtime/backend. User handlers can invoke arbitrary code, so there is no core sandbox. Evaluation and richer observability largely live in adjacent LlamaIndex components. Naming and package boundaries are in transition. **Confidence: high** for workflow/runtime design; **medium** for deployment guarantees.

Project documentation optimizes for adoption and correct use, not neutral causal comparison. Fast-moving release streams also make unversioned project names unreliable experimental treatments.

## Transferable engineering lessons

Separate workflow semantics from model policy, record durable runtime and storage choices, and pin naming/package transitions.

## Connections to academic work

See the mechanism taxonomy in [`01-definitions-and-taxonomy.md`](../synthesis/01-definitions-and-taxonomy.md), the architecture analysis in [`02-architecture-and-design-patterns.md`](../synthesis/02-architecture-and-design-patterns.md), and the full implementation comparison in [`05-open-source-harnesses.md`](../synthesis/05-open-source-harnesses.md).

## Verification notes

The sources and pinned snapshot were inspected for the 2026-09-04 research cutoff. Version discontinuities and openness caveats are recorded in the full survey. No repository snapshot is redistributed here; the canonical source URL and commit or release identifier are retained.
