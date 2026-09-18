---
title: "smolagents"
author_or_org: "Hugging Face"
date: "2026-09-04"
source_type: "official-implementation-evidence"
url: "https://github.com/huggingface/smolagents"
version_or_commit: "v1.26.0; commit 30bb1161095dbae2271e6bc3cc4c219cc3897a57"
accessed: "2026-09-04"
review_status: "reviewed"
evidence_confidence: "high-for-mechanism-medium-for-implications"
license_or_access_notes: "Apache-2.0"
---

# harness-smolagents — smolagents

## Why this source is in the corpus

This implementation represents the **model-directed-loop** family in the comparative survey. It is included to describe a reproducible mechanism and its treatment variables, not to endorse the project or convert project-authored results into independent evidence.

## System or claim described

A compact ReAct and code-agent library with prompted planning, agent memory, tool calling, managed agents, multiple executors, and callbacks.

## Architecture / mechanism

`MultiStepAgent` implements a ReAct-style step loop with `AgentMemory`. `ToolCallingAgent` emits structured tool calls, while `CodeAgent` emits Python actions. `planning_interval` periodically inserts an explicit planning step. Agents can be exposed as managed tools to other agents. Independent tool calls can use multiple threads. Local code execution uses a restricted interpreter/AST policy; remote Docker or hosted executors are available. Step callbacks and OpenTelemetry-compatible instrumentation expose runs.

## Empirical evidence

The inspected repository, documentation, and release records directly support the implementation description. They do not constitute a controlled, independent estimate of the harness's effect. Any project-authored benchmark or telemetry should be reproduced with a pinned model, prompt, environment, budget, and scorer before comparative use.

## Mathematical or formal content

The common loop is \(a_t\sim\pi_\theta(\cdot\mid C_H(s_t)),\ o_t=E_H(a_t),\ s_{t+1}=U_H(s_t,a_t,o_t)\). Context, executor, update, stopping, and budget are harness parameters; the implementation alone supplies no causal effect estimate.

## What is directly evidenced

**Official sources:** [repository](https://github.com/huggingface/smolagents), [documentation](https://huggingface.co/docs/smolagents/index), [agents guide](https://huggingface.co/docs/smolagents/guided_tour), [secure code execution](https://huggingface.co/docs/smolagents/tutorials/secure_code_execution), [license](https://github.com/huggingface/smolagents/blob/main/LICENSE).

The detailed comparison pins the inspected release or commit, license, loop/state design, action representation, context and memory policy, concurrency, containment, and observability surface.

## What is interpretation or advocacy

The code-versus-tool-call choice is an action-language experiment. Code can compact multiple operations and local transformations into one model output, while structured calls constrain syntax and simplify authorization. Either advantage is empirical and task-dependent.

## Limitations, incentives, and likely biases

The documentation explicitly warns that the local restricted interpreter is not a complete security boundary and can be bypassed; stronger isolation requires a remote/container executor. APIs have experimental surfaces, durable checkpointing and long-term retrieval are not central, and published evaluations are project-authored. **Confidence: high.**

Project documentation optimizes for adoption and correct use, not neutral causal comparison. Fast-moving release streams also make unversioned project names unreliable experimental treatments.

## Transferable engineering lessons

Compare code actions with structured tool calls under the same model and budget, and report the actual executor because local restriction is not equivalent to OS isolation.

## Connections to academic work

See the mechanism taxonomy in [`01-definitions-and-taxonomy.md`](../synthesis/01-definitions-and-taxonomy.md), the architecture analysis in [`02-architecture-and-design-patterns.md`](../synthesis/02-architecture-and-design-patterns.md), and the full implementation comparison in [`05-open-source-harnesses.md`](../synthesis/05-open-source-harnesses.md).

## Verification notes

The sources and pinned snapshot were inspected for the 2026-09-04 research cutoff. Version discontinuities and openness caveats are recorded in the full survey. No repository snapshot is redistributed here; the canonical source URL and commit or release identifier are retained.
