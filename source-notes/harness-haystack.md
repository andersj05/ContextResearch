---
title: "Haystack"
author_or_org: "deepset"
date: "2026-09-04"
source_type: "official-implementation-evidence"
url: "https://github.com/deepset-ai/haystack"
version_or_commit: "v3.1.1; commit 82da3adc2fac4675b80ff5573b790ec07113697b"
accessed: "2026-09-04"
review_status: "reviewed"
evidence_confidence: "high-for-mechanism-medium-for-implications"
license_or_access_notes: "Apache-2.0"
---

# harness-haystack — Haystack

## Why this source is in the corpus

This implementation represents the **pipeline-and-model-loop** family in the comparative survey. It is included to describe a reproducible mechanism and its treatment variables, not to endorse the project or convert project-authored results into independent evidence.

## System or claim described

A component-pipeline and agent framework with toolsets, agent-as-tool composition, schema state, asynchronous pipelines, breakpoints, and evaluators.

## Architecture / mechanism

The current v3 Agent owns the model/tool loop: it calls a chat generator, executes selected tools/toolsets, returns tool errors as observations, invokes hooks, and stops on text, configured exit conditions, or a maximum step count. Agent `State` uses a schema and merge handlers. Tool calls can run concurrently with a configurable default. `AgentTool` exposes another agent as a tool and can isolate delegated context. `AsyncPipeline` schedules independent graph components concurrently. Breakpoints, hooks, tracing integrations, OpenTelemetry, and evaluator components are available.

## Empirical evidence

The inspected repository, documentation, and release records directly support the implementation description. They do not constitute a controlled, independent estimate of the harness's effect. Any project-authored benchmark or telemetry should be reproduced with a pinned model, prompt, environment, budget, and scorer before comparative use.

## Mathematical or formal content

A useful abstraction is a labelled transition system \(s_{t+1}=U_{\ell_t}(s_t,o_t)\), where graph topology, reducer rules, and scheduling determine the admissible transition relation. The implementation does not by itself establish a performance theorem.

## What is directly evidenced

**Official sources:** [repository](https://github.com/deepset-ai/haystack), [documentation](https://docs.haystack.deepset.ai/), [Agent component](https://docs.haystack.deepset.ai/docs/agent), [AsyncPipeline](https://docs.haystack.deepset.ai/docs/asyncpipeline), [evaluation](https://docs.haystack.deepset.ai/docs/evaluation), [tracing](https://docs.haystack.deepset.ai/docs/tracing), [license](https://github.com/deepset-ai/haystack/blob/main/LICENSE.txt).

The detailed comparison pins the inspected release or commit, license, loop/state design, action representation, context and memory policy, concurrency, containment, and observability surface.

## What is interpretation or advocacy

Returning tool exceptions to the model turns runtime failure into corrective feedback. Whether this is beneficial depends on error specificity and budget; it can also create retry loops that look like deliberation while merely consuming tokens.

## Limitations, incentives, and likely biases

Agent State is primarily per run, not automatically long-term memory. Components and tools may execute arbitrary Python with no core OS sandbox. Older documentation in which a separate `ToolInvoker` performed execution can be stale for v3.1.1. **Confidence: high** for current source; **medium** for version-crossing comparisons.

Project documentation optimizes for adoption and correct use, not neutral causal comparison. Fast-moving release streams also make unversioned project names unreliable experimental treatments.

## Transferable engineering lessons

Separate pipeline dataflow, integrated agent loop, evaluator components, and arbitrary host-code execution when specifying the treatment.

## Connections to academic work

See the mechanism taxonomy in [`01-definitions-and-taxonomy.md`](../synthesis/01-definitions-and-taxonomy.md), the architecture analysis in [`02-architecture-and-design-patterns.md`](../synthesis/02-architecture-and-design-patterns.md), and the full implementation comparison in [`05-open-source-harnesses.md`](../synthesis/05-open-source-harnesses.md).

## Verification notes

The sources and pinned snapshot were inspected for the 2026-09-04 research cutoff. Version discontinuities and openness caveats are recorded in the full survey. No repository snapshot is redistributed here; the canonical source URL and commit or release identifier are retained.
