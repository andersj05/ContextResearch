---
title: "SWE-agent"
author_or_org: "SWE-agent"
date: "2026-09-04"
source_type: "official-implementation-evidence"
url: "https://github.com/SWE-agent/SWE-agent"
version_or_commit: "v1.1.0; main commit 3ea751c087f32b16e039a2233dd6eefecef325d5"
accessed: "2026-09-04"
review_status: "reviewed"
evidence_confidence: "high-for-mechanism-medium-for-implications"
license_or_access_notes: "MIT"
---

# harness-swe-agent — SWE-agent

## Why this source is in the corpus

This implementation represents the **model-directed-loop** family in the comparative survey. It is included to describe a reproducible mechanism and its treatment variables, not to endorse the project or convert project-authored results into independent evidence.

## System or claim described

A coding-agent observe–act–execute loop with configurable action grammar, history processing, environment, hooks, and trajectory persistence.

## Architecture / mechanism

The agent repeatedly renders model input from a trajectory, obtains a structured or parsed action, sends it to an execution environment, appends the observation, and terminates on a configured exit or limit. History processors can alter what portion or summary of the trajectory is returned to the model. Hooks expose lifecycle events, and trajectories preserve actions and observations. Execution is normally mediated by SWE-ReX and can use Docker-backed environments. The repository also supports running independent tasks in batches and competitive/multiple attempts with a discriminator.

## Empirical evidence

The inspected repository, documentation, and release records directly support the implementation description. They do not constitute a controlled, independent estimate of the harness's effect. Any project-authored benchmark or telemetry should be reproduced with a pinned model, prompt, environment, budget, and scorer before comparative use.

## Mathematical or formal content

The common loop is \(a_t\sim\pi_\theta(\cdot\mid C_H(s_t)),\ o_t=E_H(a_t),\ s_{t+1}=U_H(s_t,a_t,o_t)\). Context, executor, update, stopping, and budget are harness parameters; the implementation alone supplies no causal effect estimate.

## What is directly evidenced

**Official sources:** [repository](https://github.com/SWE-agent/SWE-agent), [documentation](https://swe-agent.com/latest/), [configuration reference](https://swe-agent.com/latest/config/), [license](https://github.com/SWE-agent/SWE-agent/blob/main/LICENSE).

The detailed comparison pins the inspected release or commit, license, loop/state design, action representation, context and memory policy, concurrency, containment, and observability surface.

## What is interpretation or advocacy

SWE-agent is best modeled as an error-feedback controller around a repository environment. Its important treatment variables are action grammar, environment image, history processor, prompt, model, step/cost limits, and discriminator. “Planning” is primarily model-internal or prompt-elicited rather than a separately verified search algorithm.

## Limitations, incentives, and likely biases

The maintainers position mini-SWE-agent as the simpler actively recommended path. SWE-bench integration is valuable but project-authored configurations do not isolate harness effects from model, prompt, tool, budget, and environment changes. **Confidence: high** for loop/environment/trajectory mechanics; **medium** for comparative research implications.

Project documentation optimizes for adoption and correct use, not neutral causal comparison. Fast-moving release streams also make unversioned project names unreliable experimental treatments.

## Transferable engineering lessons

Treat action grammar, environment image, history processor, prompt, model, budget, and any attempt discriminator as separate experimental factors.

## Connections to academic work

See the mechanism taxonomy in [`01-definitions-and-taxonomy.md`](../synthesis/01-definitions-and-taxonomy.md), the architecture analysis in [`02-architecture-and-design-patterns.md`](../synthesis/02-architecture-and-design-patterns.md), and the full implementation comparison in [`05-open-source-harnesses.md`](../synthesis/05-open-source-harnesses.md).

## Verification notes

The sources and pinned snapshot were inspected for the 2026-09-04 research cutoff. Version discontinuities and openness caveats are recorded in the full survey. No repository snapshot is redistributed here; the canonical source URL and commit or release identifier are retained.
