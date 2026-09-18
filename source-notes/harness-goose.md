---
title: "goose"
author_or_org: "Agentic AI Foundation"
date: "2026-09-04"
source_type: "official-implementation-evidence"
url: "https://github.com/aaif-goose/goose"
version_or_commit: "v1.49.0; commit dce69009546ce5f20522d010fa3f1d57abbe2c3f"
accessed: "2026-09-04"
review_status: "reviewed"
evidence_confidence: "high-for-mechanism-medium-for-implications"
license_or_access_notes: "Apache-2.0"
---

# harness-goose — goose

## Why this source is in the corpus

This implementation represents the **model-directed-loop** family in the comparative survey. It is included to describe a reproducible mechanism and its treatment variables, not to endorse the project or convert project-authored results into independent evidence.

## System or claim described

An MCP-first coding and general agent with recipes, session state, context revision, extension discovery, and delegation.

## Architecture / mechanism

goose implements a session-oriented model/tool/result loop and makes MCP extensions the principal tool boundary. Recipes package instructions and extension configuration for repeatable tasks. The runtime records sessions and revises context through summarization/deletion policies. It can delegate across ACP-compatible agents and run independent agents concurrently.

## Empirical evidence

The inspected repository, documentation, and release records directly support the implementation description. They do not constitute a controlled, independent estimate of the harness's effect. Any project-authored benchmark or telemetry should be reproduced with a pinned model, prompt, environment, budget, and scorer before comparative use.

## Mathematical or formal content

The common loop is \(a_t\sim\pi_\theta(\cdot\mid C_H(s_t)),\ o_t=E_H(a_t),\ s_{t+1}=U_H(s_t,a_t,o_t)\). Context, executor, update, stopping, and budget are harness parameters; the implementation alone supplies no causal effect estimate.

## What is directly evidenced

**Official sources:** [repository](https://github.com/aaif-goose/goose), [documentation](https://block.github.io/goose/), [extensions documentation](https://block.github.io/goose/docs/getting-started/using-extensions/), [license](https://github.com/aaif-goose/goose/blob/main/LICENSE).

The detailed comparison pins the inspected release or commit, license, loop/state design, action representation, context and memory policy, concurrency, containment, and observability surface.

## What is interpretation or advocacy

MCP-first architecture reduces tool-adapter coupling and makes tool availability an explicit experimental factor. Protocol interoperability does not imply semantic equivalence: two MCP servers with the same nominal capability can differ in schemas, latency, permissions, and error behavior.

## Limitations, incentives, and likely biases

Local tools commonly execute with the user’s host privileges; official security guidance recommends a dedicated VM/container when isolation is required. Evaluation is not a first-class neutral subsystem. **Confidence: high** for protocol and session architecture; **medium** for extension-dependent behavior.

Project documentation optimizes for adoption and correct use, not neutral causal comparison. Fast-moving release streams also make unversioned project names unreliable experimental treatments.

## Transferable engineering lessons

Model extension discovery, summarization, execution location, and delegation as explicit policies rather than treating MCP support as one binary feature.

## Connections to academic work

See the mechanism taxonomy in [`01-definitions-and-taxonomy.md`](../synthesis/01-definitions-and-taxonomy.md), the architecture analysis in [`02-architecture-and-design-patterns.md`](../synthesis/02-architecture-and-design-patterns.md), and the full implementation comparison in [`05-open-source-harnesses.md`](../synthesis/05-open-source-harnesses.md).

## Verification notes

The sources and pinned snapshot were inspected for the 2026-09-04 research cutoff. Version discontinuities and openness caveats are recorded in the full survey. No repository snapshot is redistributed here; the canonical source URL and commit or release identifier are retained.
