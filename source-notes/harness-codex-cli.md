---
title: "Codex CLI"
author_or_org: "OpenAI"
date: "2026-09-04"
source_type: "official-implementation-evidence"
url: "https://github.com/openai/codex"
version_or_commit: "rust-v0.153.2; commit de7874067fe8cb8f4846dd4d8b848965ce79070f"
accessed: "2026-09-04"
review_status: "reviewed"
evidence_confidence: "high-for-mechanism-medium-for-implications"
license_or_access_notes: "Apache-2.0 for repository code; hosted models and services are proprietary"
---

# harness-codex-cli — Codex CLI

## Why this source is in the corpus

This implementation represents the **event-sourced-loop** family in the comparative survey. It is included to describe a reproducible mechanism and its treatment variables, not to endorse the project or convert project-authored results into independent evidence.

## System or claim described

An open client and event protocol for coding work with persisted threads, compaction, tools, MCP, collaboration, sandboxes, approvals, and telemetry.

## Architecture / mechanism

The Rust client exposes a structured thread→turn→item protocol. Items/events cover model reasoning, plans, command execution, file changes, MCP calls, web operations, compaction, and collaboration/subagent activity. Conversation history and workspace/Git state provide working context. The client supports MCP server configuration, tool controls, approvals, subagents, and multiple sandbox policies, including read-only, workspace-write, and full access. It also exposes structured event output and OpenTelemetry configuration.

## Empirical evidence

The inspected repository, documentation, and release records directly support the implementation description. They do not constitute a controlled, independent estimate of the harness's effect. Any project-authored benchmark or telemetry should be reproduced with a pinned model, prompt, environment, budget, and scorer before comparative use.

## Mathematical or formal content

The common loop is \(a_t\sim\pi_\theta(\cdot\mid C_H(s_t)),\ o_t=E_H(a_t),\ s_{t+1}=U_H(s_t,a_t,o_t)\). Context, executor, update, stopping, and budget are harness parameters; the implementation alone supplies no causal effect estimate.

## What is directly evidenced

**Official sources:** [repository](https://github.com/openai/codex), [CLI documentation](https://learn.chatgpt.com/docs/codex/cli), [agent approvals and security](https://learn.chatgpt.com/docs/agent-approvals-security), [repository documentation](https://github.com/openai/codex/tree/main/docs), [protocol source](https://github.com/openai/codex/tree/main/codex-rs/protocol), [license](https://github.com/openai/codex/blob/main/LICENSE).

The detailed comparison pins the inspected release or commit, license, loop/state design, action representation, context and memory policy, concurrency, containment, and observability surface.

## What is interpretation or advocacy

Codex demonstrates **layered openness**: the client, protocol, and sandbox implementation can be inspected under Apache-2.0, while hosted model weights and service-side behavior remain proprietary. Reproducible studies must therefore identify which layer is under test and capture model/service identifiers as external dependencies.

## Limitations, incentives, and likely biases

An open client is not an open end-to-end agent. Plans are model-produced mutable artifacts rather than guaranteed optimal policies. The CLI does not provide a neutral intrinsic task evaluator. **Confidence: high** for client-side mechanisms; **low to medium** for unobservable service internals.

Project documentation optimizes for adoption and correct use, not neutral causal comparison. Fast-moving release streams also make unversioned project names unreliable experimental treatments.

## Transferable engineering lessons

Version the open client/protocol separately from the proprietary model and service, and report sandbox and approval modes as independent factors.

## Connections to academic work

See the mechanism taxonomy in [`01-definitions-and-taxonomy.md`](../synthesis/01-definitions-and-taxonomy.md), the architecture analysis in [`02-architecture-and-design-patterns.md`](../synthesis/02-architecture-and-design-patterns.md), and the full implementation comparison in [`05-open-source-harnesses.md`](../synthesis/05-open-source-harnesses.md).

## Verification notes

The sources and pinned snapshot were inspected for the 2026-09-04 research cutoff. Version discontinuities and openness caveats are recorded in the full survey. No repository snapshot is redistributed here; the canonical source URL and commit or release identifier are retained.
