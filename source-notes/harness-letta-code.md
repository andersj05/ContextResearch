---
title: "Letta Code"
author_or_org: "Letta"
date: "2026-09-04"
source_type: "official-implementation-evidence"
url: "https://github.com/letta-ai/letta-code"
version_or_commit: "v0.31.12; commit 047fa6a99d9e83529b3c3e91cd8e3a7835a0f9c2"
accessed: "2026-09-04"
review_status: "reviewed"
evidence_confidence: "high-for-mechanism-medium-for-implications"
license_or_access_notes: "Apache-2.0"
---

# harness-letta-code — Letta Code

## Why this source is in the corpus

This implementation represents the **model-directed-loop** family in the comparative survey. It is included to describe a reproducible mechanism and its treatment variables, not to endorse the project or convert project-authored results into independent evidence.

## System or claim described

A memory-first coding agent with Git-backed memory files, compaction and dreaming, plans, approvals, isolated subagents, and trajectory export.

## Architecture / mechanism

Letta Code’s headless outer loop sends a turn, streams model events, classifies requested operations as allow/deny/ask, executes approved tools, returns results, and repeats. Its local provider executor estimates context use before a request, reserves a margin, and compacts when necessary. MemFS stores Markdown in a Git-backed tree: `system/` material is injected into context while other files are discovered through a tree/read interface. Memory and agent skills share commit/sync semantics; semantic indexing is optional rather than the only retrieval path. Dreaming performs background reflection. Memory workers use Git worktrees, while foreground/background subagents have their own process, context, model, and tool state. Plan/task tools are model-managed. Permission modes include unrestricted, standard, accept-edits, and strict; the CLI default at inspection was unrestricted. Local execution and optional isolated cloud computers are separate backends.

## Empirical evidence

The inspected repository, documentation, and release records directly support the implementation description. They do not constitute a controlled, independent estimate of the harness's effect. Any project-authored benchmark or telemetry should be reproduced with a pinned model, prompt, environment, budget, and scorer before comparative use.

## Mathematical or formal content

The common loop is \(a_t\sim\pi_\theta(\cdot\mid C_H(s_t)),\ o_t=E_H(a_t),\ s_{t+1}=U_H(s_t,a_t,o_t)\). Context, executor, update, stopping, and budget are harness parameters; the implementation alone supplies no causal effect estimate.

## What is directly evidenced

**Official sources:** [repository](https://github.com/letta-ai/letta-code), [current README](https://github.com/letta-ai/letta-code/blob/main/README.md), [source tree](https://github.com/letta-ai/letta-code/tree/main/src), [platform documentation](https://docs.letta.com/), [legacy repository notice](https://github.com/letta-ai/letta), [license](https://github.com/letta-ai/letta-code/blob/main/LICENSE).

The detailed comparison pins the inspected release or commit, license, loop/state design, action representation, context and memory policy, concurrency, containment, and observability surface.

## What is interpretation or advocacy

Letta treats durable identity/instruction memory as a filesystem and version-control problem rather than only vector retrieval. Git provides provenance and conflict mechanics, not factual correctness. Dreaming resembles an offline consolidation operator

\[
M_{t+1}=G(M_t,H_{1:t}),
\]

whose value must be tested against added cost, drift, and self-reinforcement—not assumed from analogy to human sleep.

## Limitations, incentives, and likely biases

The default unrestricted local mode is a major experimental and security variable. Background agents and memory workers introduce asynchronous state races. Product/session analytics are not equivalent to scientific evaluation. Letta’s wider platform now documents a separate Evals system, but Letta Code trajectory export by itself is not a neutral scorer, and a first-party evaluator remains non-independent. Older Letta/MemGPT papers do not describe the current TypeScript-oriented repository directly. **Confidence: high** for current source mechanics; **medium** for memory benefit claims.

Project documentation optimizes for adoption and correct use, not neutral causal comparison. Fast-moving release streams also make unversioned project names unreliable experimental treatments.

## Transferable engineering lessons

Treat persistent memory, context compaction, background memory work, approval mode, and optional execution isolation as separate interventions.

## Connections to academic work

See the mechanism taxonomy in [`01-definitions-and-taxonomy.md`](../synthesis/01-definitions-and-taxonomy.md), the architecture analysis in [`02-architecture-and-design-patterns.md`](../synthesis/02-architecture-and-design-patterns.md), and the full implementation comparison in [`05-open-source-harnesses.md`](../synthesis/05-open-source-harnesses.md).

## Verification notes

The sources and pinned snapshot were inspected for the 2026-09-04 research cutoff. Version discontinuities and openness caveats are recorded in the full survey. No repository snapshot is redistributed here; the canonical source URL and commit or release identifier are retained.
