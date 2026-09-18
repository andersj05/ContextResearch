---
title: "PocketFlow"
author_or_org: "The-Pocket"
date: "2026-09-04"
source_type: "official-implementation-evidence"
url: "https://github.com/The-Pocket/PocketFlow"
version_or_commit: "main commit f74d023f93607b8c3268133339a5e532a949898c"
accessed: "2026-09-04"
review_status: "reviewed"
evidence_confidence: "high-for-mechanism-medium-for-implications"
license_or_access_notes: "MIT"
---

# harness-pocketflow — PocketFlow

## Why this source is in the corpus

This implementation represents the **explicit-graph-runtime** family in the comparative survey. It is included to describe a reproducible mechanism and its treatment variables, not to endorse the project or convert project-authored results into independent evidence.

## System or claim described

A minimal graph scheduler built around node prep–execute–post phases, action-labelled transitions, shared state, and batch or async variants.

## Architecture / mechanism

PocketFlow’s core is a very small scheduler. A node runs `prep→exec→post`; `post` returns an action label; a flow follows the corresponding transition in a plain loop. A shared dictionary holds state. Retry/fallback, nested flows, batch variants, async nodes, and `asyncio.gather` variants are provided. It has no required LLM client, tool schema, agent memory, planner, sandbox, tracer, or evaluator.

## Empirical evidence

The inspected repository, documentation, and release records directly support the implementation description. They do not constitute a controlled, independent estimate of the harness's effect. Any project-authored benchmark or telemetry should be reproduced with a pinned model, prompt, environment, budget, and scorer before comparative use.

## Mathematical or formal content

A useful abstraction is a labelled transition system \(s_{t+1}=U_{\ell_t}(s_t,o_t)\), where graph topology, reducer rules, and scheduling determine the admissible transition relation. The implementation does not by itself establish a performance theorem.

## What is directly evidenced

**Official sources:** [repository](https://github.com/The-Pocket/PocketFlow), [core source](https://github.com/The-Pocket/PocketFlow/blob/main/pocketflow/__init__.py), [documentation](https://the-pocket.github.io/PocketFlow/), [license](https://github.com/The-Pocket/PocketFlow/blob/main/LICENSE).

The detailed comparison pins the inspected release or commit, license, loop/state design, action representation, context and memory policy, concurrency, containment, and observability surface.

## What is interpretation or advocacy

PocketFlow is a counterexample to ontological inflation: many “agent” architectures are cyclic labeled transition systems plus user-defined functions. Its small size makes topology easy to audit and places all intelligence and safety responsibility in application code.

## Limitations, incentives, and likely biases

Cycles can be unbounded, parallel code can race on shared state, and durability/security/observability must be built separately. It should not be credited with features supplied only by examples or user code. **Confidence: high.**

Project documentation optimizes for adoption and correct use, not neutral causal comparison. Fast-moving release streams also make unversioned project names unreliable experimental treatments.

## Transferable engineering lessons

Use minimal schedulers as controls: graph execution alone supplies neither model policy, memory semantics, containment, nor evaluation.

## Connections to academic work

See the mechanism taxonomy in [`01-definitions-and-taxonomy.md`](../synthesis/01-definitions-and-taxonomy.md), the architecture analysis in [`02-architecture-and-design-patterns.md`](../synthesis/02-architecture-and-design-patterns.md), and the full implementation comparison in [`05-open-source-harnesses.md`](../synthesis/05-open-source-harnesses.md).

## Verification notes

The sources and pinned snapshot were inspected for the 2026-09-04 research cutoff. Version discontinuities and openness caveats are recorded in the full survey. No repository snapshot is redistributed here; the canonical source URL and commit or release identifier are retained.
