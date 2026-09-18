---
title: "AG2 v1"
author_or_org: "AG2AI"
date: "2026-09-04"
source_type: "official-implementation-evidence"
url: "https://github.com/ag2ai/ag2"
version_or_commit: "v1.0.3; commit d4df5694e53d0533d583a7865023fa2e4e53b674"
accessed: "2026-09-04"
review_status: "reviewed"
evidence_confidence: "high-for-mechanism-medium-for-implications"
license_or_access_notes: "Apache-2.0"
---

# harness-ag2 — AG2 v1

## Why this source is in the corpus

This implementation represents the **actor-message-runtime** family in the comparative survey. It is included to describe a reproducible mechanism and its treatment variables, not to endorse the project or convert project-authored results into independent evidence.

## System or claim described

A multi-agent network runtime with run handles, tools, middleware, context policies, compaction, memory streams, code execution, and evaluation surfaces.

## Architecture / mechanism

AG2 v1 exposes agents and asynchronous run handles, a bare Agent Harness, context policies, compaction, knowledge/memory integrations, middleware, and fresh-context subtasks. Subtasks can fan out with `asyncio.gather`. Its network design adds agents connected through a hub, channels, per-channel write-ahead logs, and governance controls. Execution backends include local, Docker, and hosted environments. Evaluation APIs cover datasets, scorers, repeats, and concurrency; OpenTelemetry instrumentation is available.

## Empirical evidence

The inspected repository, documentation, and release records directly support the implementation description. They do not constitute a controlled, independent estimate of the harness's effect. Any project-authored benchmark or telemetry should be reproduced with a pinned model, prompt, environment, budget, and scorer before comparative use.

## Mathematical or formal content

The runtime can be represented as communicating state machines with local states \(s_t^{(i)}\) and messages \(m_{i\to j,t}\). Correctness depends on delivery, ordering, shared-resource, and termination assumptions that project documentation does not generally prove.

## What is directly evidenced

**Official sources:** [repository](https://github.com/ag2ai/ag2), [documentation](https://docs.ag2.ai/), [classic repository](https://github.com/ag2ai/ag2-classic), [license](https://github.com/ag2ai/ag2/blob/main/LICENSE).

The detailed comparison pins the inspected release or commit, license, loop/state design, action representation, context and memory policy, concurrency, containment, and observability surface.

## What is interpretation or advocacy

Fresh-context subtasks implement an information-boundary experiment: delegation can reduce context interference at the cost of communication loss. A hub/WAL architecture improves auditability and recovery but creates a coordination bottleneck and does not validate message truthfulness.

## Limitations, incentives, and likely biases

v1 was new at the snapshot date; its operational maturity and independent evaluation record were limited. The Classic-to-v1 discontinuity makes unversioned comparisons invalid. Executor safety depends on backend selection. **Confidence: high** for source-described interfaces; **medium** for production properties.

Project documentation optimizes for adoption and correct use, not neutral causal comparison. Fast-moving release streams also make unversioned project names unreliable experimental treatments.

## Transferable engineering lessons

Report v1 separately from AG2 classic and measure message topology, context policy, executor, and concurrency rather than the framework label alone.

## Connections to academic work

See the mechanism taxonomy in [`01-definitions-and-taxonomy.md`](../synthesis/01-definitions-and-taxonomy.md), the architecture analysis in [`02-architecture-and-design-patterns.md`](../synthesis/02-architecture-and-design-patterns.md), and the full implementation comparison in [`05-open-source-harnesses.md`](../synthesis/05-open-source-harnesses.md).

## Verification notes

The sources and pinned snapshot were inspected for the 2026-09-04 research cutoff. Version discontinuities and openness caveats are recorded in the full survey. No repository snapshot is redistributed here; the canonical source URL and commit or release identifier are retained.
