---
title: "mini-SWE-agent"
author_or_org: "SWE-agent"
date: "2026-09-04"
source_type: "official-implementation-evidence"
url: "https://github.com/SWE-agent/mini-swe-agent"
version_or_commit: "v2.4.6; main commit 04d809ceab9df28f9adaed044884180159172930"
accessed: "2026-09-04"
review_status: "reviewed"
evidence_confidence: "high-for-mechanism-medium-for-implications"
license_or_access_notes: "MIT"
---

# harness-mini-swe-agent — mini-SWE-agent

## Why this source is in the corpus

This implementation represents the **model-directed-loop** family in the comparative survey. It is included to describe a reproducible mechanism and its treatment variables, not to endorse the project or convert project-authored results into independent evidence.

## System or claim described

A deliberately small coding-agent loop that separates Agent, Model, and Environment protocols.

## Architecture / mechanism

The core separates `Agent`, `Model`, and `Environment` protocols. A default agent holds a message list, queries the model, executes the resulting action through an environment, appends the observation, and repeats until an exit condition or resource-limit exception. The resulting trajectory retains the conversation and execution record. Environment backends include local and isolated options.

## Empirical evidence

The inspected repository, documentation, and release records directly support the implementation description. They do not constitute a controlled, independent estimate of the harness's effect. Any project-authored benchmark or telemetry should be reproduced with a pinned model, prompt, environment, budget, and scorer before comparative use.

## Mathematical or formal content

The common loop is \(a_t\sim\pi_\theta(\cdot\mid C_H(s_t)),\ o_t=E_H(a_t),\ s_{t+1}=U_H(s_t,a_t,o_t)\). Context, executor, update, stopping, and budget are harness parameters; the implementation alone supplies no causal effect estimate.

## What is directly evidenced

**Official sources:** [repository](https://github.com/SWE-agent/mini-swe-agent), [documentation](https://mini-swe-agent.com/latest/), [source tree](https://github.com/SWE-agent/mini-swe-agent/tree/main/src/minisweagent), [license](https://github.com/SWE-agent/mini-swe-agent/blob/main/LICENSE).

The detailed comparison pins the inspected release or commit, license, loop/state design, action representation, context and memory policy, concurrency, containment, and observability surface.

## What is interpretation or advocacy

This is a useful lower-bound architecture: it tests how far a transparent loop, strong model, and well-defined environment can go without a graph engine, retrieval database, durable distributed runtime, or elaborate planner. It is therefore a meaningful control condition for claims that orchestration complexity itself improves performance.

## Limitations, incentives, and likely biases

The default local environment can execute on the host and is not a security boundary. There is no native long-term retrieval memory, central multi-agent protocol, or explicit search planner. **Confidence: high.**

Project documentation optimizes for adoption and correct use, not neutral causal comparison. Fast-moving release streams also make unversioned project names unreliable experimental treatments.

## Transferable engineering lessons

Use a transparent loop as a lower-complexity control before attributing gains to planners, graphs, retrieval stores, or multi-agent coordination.

## Connections to academic work

See the mechanism taxonomy in [`01-definitions-and-taxonomy.md`](../synthesis/01-definitions-and-taxonomy.md), the architecture analysis in [`02-architecture-and-design-patterns.md`](../synthesis/02-architecture-and-design-patterns.md), and the full implementation comparison in [`05-open-source-harnesses.md`](../synthesis/05-open-source-harnesses.md).

## Verification notes

The sources and pinned snapshot were inspected for the 2026-09-04 research cutoff. Version discontinuities and openness caveats are recorded in the full survey. No repository snapshot is redistributed here; the canonical source URL and commit or release identifier are retained.
