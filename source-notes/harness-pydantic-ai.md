---
title: "Pydantic AI and Pydantic AI Harness"
author_or_org: "Pydantic"
date: "2026-09-04"
source_type: "official-implementation-evidence"
url: "https://github.com/pydantic/pydantic-ai"
version_or_commit: "core v2.39.0 / 7d85a07ec8e90f0741e8bd488ce1c4d0898f4618; Harness v0.29.0 / ec4b8615ac820bd5b93f19c00c52db29682a6e96"
accessed: "2026-09-04"
review_status: "reviewed"
evidence_confidence: "high-for-mechanism-medium-for-implications"
license_or_access_notes: "MIT for both repositories"
---

# harness-pydantic-ai — Pydantic AI and Pydantic AI Harness

## Why this source is in the corpus

This implementation represents the **typed-loop-and-capability-harness** family in the comparative survey. It is included to describe a reproducible mechanism and its treatment variables, not to endorse the project or convert project-authored results into independent evidence.

## System or claim described

A typed agent graph and validation loop plus a separate capability-oriented coding harness with planning, repository context, compaction, allowlists, and explorer subagents.

## Architecture / mechanism

The core agent is a typed state graph with schema-validated dependencies, tools, outputs, retry paths, and serializable message history. Durable integrations include Temporal, DBOS, and Prefect. `pydantic-evals` supplies dataset/case abstractions, evaluators, assertions, repeated execution, and reporting; OpenTelemetry/Logfire capture traces. The separate Harness repository bundles repository/filesystem context, allowlisted shell capabilities, structured plan state, tool-result clearing, compaction, tool search, memory, and a read-only explorer subagent. Explorer tasks receive fresh contexts and can run in parallel. Code mode uses Monty, a restricted Python subset, with explicit mounted capabilities.

## Empirical evidence

The inspected repository, documentation, and release records directly support the implementation description. They do not constitute a controlled, independent estimate of the harness's effect. Any project-authored benchmark or telemetry should be reproduced with a pinned model, prompt, environment, budget, and scorer before comparative use.

## Mathematical or formal content

The common loop is \(a_t\sim\pi_\theta(\cdot\mid C_H(s_t)),\ o_t=E_H(a_t),\ s_{t+1}=U_H(s_t,a_t,o_t)\). Context, executor, update, stopping, and budget are harness parameters; the implementation alone supplies no causal effect estimate.

## What is directly evidenced

**Official sources:** [Pydantic AI repository](https://github.com/pydantic/pydantic-ai), [Pydantic AI documentation](https://ai.pydantic.dev/), [agents](https://ai.pydantic.dev/agents/), [durable execution](https://ai.pydantic.dev/durable_execution/), [evaluation](https://ai.pydantic.dev/evals/), [Pydantic AI Harness repository](https://github.com/pydantic/pydantic-ai-harness), [Coder composition](https://github.com/pydantic/pydantic-ai-harness/blob/main/docs/coder.md), [code-mode sandbox](https://github.com/pydantic/pydantic-ai-harness/blob/main/docs/code-mode.md), [core license](https://github.com/pydantic/pydantic-ai/blob/main/LICENSE), [Harness license](https://github.com/pydantic/pydantic-ai-harness/blob/main/LICENSE).

The detailed comparison pins the inspected release or commit, license, loop/state design, action representation, context and memory policy, concurrency, containment, and observability surface.

## What is interpretation or advocacy

Typed validation changes the error channel: malformed model output becomes a structured retry observation instead of an uncontrolled parse failure. This may improve recoverability but can also increase calls and produce evaluator-visible selection effects when only successful retries are retained.

## Limitations, incentives, and likely biases

Core tools normally execute as host application code; schemas and allowlists are not OS isolation. Harness is a comparatively young 0.x capability layer, so findings should pin exact versions. Fresh-context explorer agents trade reduced contamination for lossy summaries. **Confidence: high** for core and documented Harness interfaces; **medium** for young Harness operational behavior.

Project documentation optimizes for adoption and correct use, not neutral causal comparison. Fast-moving release streams also make unversioned project names unreliable experimental treatments.

## Transferable engineering lessons

Pin core and Harness separately; schema validation, retries, context compilation, sandbox subset, and subagent isolation are distinct mechanisms.

## Connections to academic work

See the mechanism taxonomy in [`01-definitions-and-taxonomy.md`](../synthesis/01-definitions-and-taxonomy.md), the architecture analysis in [`02-architecture-and-design-patterns.md`](../synthesis/02-architecture-and-design-patterns.md), and the full implementation comparison in [`05-open-source-harnesses.md`](../synthesis/05-open-source-harnesses.md).

## Verification notes

The sources and pinned snapshot were inspected for the 2026-09-04 research cutoff. Version discontinuities and openness caveats are recorded in the full survey. No repository snapshot is redistributed here; the canonical source URL and commit or release identifier are retained.
