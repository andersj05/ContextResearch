---
title: "Claude Code"
author_or_org: "Anthropic"
date: "2026-09-04"
source_type: "official-implementation-evidence"
url: "https://github.com/anthropics/claude-code"
version_or_commit: "v2.1.260; commit b3f0e501b79fe5cfc8c10d18cf3b0b6715c5c2fb"
accessed: "2026-09-04"
review_status: "reviewed"
evidence_confidence: "high-for-mechanism-medium-for-implications"
license_or_access_notes: "Proprietary; public repository is all rights reserved"
---

# harness-claude-code — Claude Code

## Why this source is in the corpus

This implementation represents the **model-directed-loop** family in the comparative survey. It is included to describe a reproducible mechanism and its treatment variables, not to endorse the project or convert project-authored results into independent evidence.

## System or claim described

A publicly distributed but proprietary coding harness with session persistence, compaction, instructions, skills, tools, hooks, subagents, permissions, and telemetry.

## Architecture / mechanism

First-party documentation describes a gather→act→verify interaction cycle; persistent JSONL sessions and checkpoints; automatic context compaction; project/user instruction files (`CLAUDE.md`); auto-memory and skills; built-in tools and MCP; hooks; foreground/background subagents; optional Git worktrees; permission rules; OS-level sandbox settings; and OpenTelemetry monitoring.

## Empirical evidence

The inspected repository, documentation, and release records directly support the implementation description. They do not constitute a controlled, independent estimate of the harness's effect. Any project-authored benchmark or telemetry should be reproduced with a pinned model, prompt, environment, budget, and scorer before comparative use.

## Mathematical or formal content

The common loop is \(a_t\sim\pi_\theta(\cdot\mid C_H(s_t)),\ o_t=E_H(a_t),\ s_{t+1}=U_H(s_t,a_t,o_t)\). Context, executor, update, stopping, and budget are harness parameters; the implementation alone supplies no causal effect estimate.

## What is directly evidenced

**Official sources:** [public distribution/issues repository](https://github.com/anthropics/claude-code), [overview](https://code.claude.com/docs/en/overview), [memory](https://code.claude.com/docs/en/memory), [subagents](https://code.claude.com/docs/en/sub-agents), [sandboxing](https://code.claude.com/docs/en/sandboxing), [monitoring](https://code.claude.com/docs/en/monitoring-usage), [proprietary license](https://github.com/anthropics/claude-code/blob/main/LICENSE.md).

The detailed comparison pins the inspected release or commit, license, loop/state design, action representation, context and memory policy, concurrency, containment, and observability surface.

## What is interpretation or advocacy

Public documentation reveals the product-level control surfaces but not enough implementation detail to validate scheduler, context-selection, or policy behavior independently. It should be analyzed as a black- or gray-box proprietary harness, not grouped with source-available runtimes.

## Limitations, incentives, and likely biases

The public repository is not the full implementation and its license is proprietary; **Claude Code is not open source**. Documentation supports feature existence but cannot establish hidden defaults, ordering, or causal efficacy. **Confidence: high** for documented interfaces; **low** for internals.

Project documentation optimizes for adoption and correct use, not neutral causal comparison. Fast-moving release streams also make unversioned project names unreliable experimental treatments.

## Transferable engineering lessons

Do not equate a public repository with open source or infer undocumented internals; separate documented interface behavior from implementation claims.

## Connections to academic work

See the mechanism taxonomy in [`01-definitions-and-taxonomy.md`](../synthesis/01-definitions-and-taxonomy.md), the architecture analysis in [`02-architecture-and-design-patterns.md`](../synthesis/02-architecture-and-design-patterns.md), and the full implementation comparison in [`05-open-source-harnesses.md`](../synthesis/05-open-source-harnesses.md).

## Verification notes

The sources and pinned snapshot were inspected for the 2026-09-04 research cutoff. Version discontinuities and openness caveats are recorded in the full survey. No repository snapshot is redistributed here; the canonical source URL and commit or release identifier are retained.
