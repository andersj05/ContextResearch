#!/usr/bin/env python3
"""Build consistently structured implementation notes from the reviewed harness survey.

The survey remains the canonical, detailed comparison.  These notes make each
implementation independently discoverable and give it a stable catalog identifier.
"""

from __future__ import annotations

import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SURVEY = ROOT / "synthesis" / "05-open-source-harnesses.md"
OUT = ROOT / "source-notes"


SYSTEMS = [
    {
        "number": 1,
        "slug": "harness-swe-agent",
        "title": "SWE-agent",
        "org": "SWE-agent",
        "url": "https://github.com/SWE-agent/SWE-agent",
        "version": "v1.1.0; main commit 3ea751c087f32b16e039a2233dd6eefecef325d5",
        "license": "MIT",
        "role": "A coding-agent observe–act–execute loop with configurable action grammar, history processing, environment, hooks, and trajectory persistence.",
        "family": "model-directed-loop",
        "lesson": "Treat action grammar, environment image, history processor, prompt, model, budget, and any attempt discriminator as separate experimental factors.",
    },
    {
        "number": 2,
        "slug": "harness-mini-swe-agent",
        "title": "mini-SWE-agent",
        "org": "SWE-agent",
        "url": "https://github.com/SWE-agent/mini-swe-agent",
        "version": "v2.4.6; main commit 04d809ceab9df28f9adaed044884180159172930",
        "license": "MIT",
        "role": "A deliberately small coding-agent loop that separates Agent, Model, and Environment protocols.",
        "family": "model-directed-loop",
        "lesson": "Use a transparent loop as a lower-complexity control before attributing gains to planners, graphs, retrieval stores, or multi-agent coordination.",
    },
    {
        "number": 3,
        "slug": "harness-openhands",
        "title": "OpenHands Software Agent SDK",
        "org": "OpenHands",
        "url": "https://github.com/OpenHands/software-agent-sdk",
        "version": "SDK v1.44.1; commit f47083cc370a85160f0348f32e531ee3514399e5",
        "license": "MIT",
        "role": "An event-oriented coding-agent SDK in which a stateless policy step is separated from conversation lifecycle, execution, and persistence.",
        "family": "event-sourced-loop",
        "lesson": "Separate policy transitions from durable orchestration so state reconstruction, replay, context experiments, and audit are explicit.",
    },
    {
        "number": 4,
        "slug": "harness-aider",
        "title": "Aider",
        "org": "Aider-AI",
        "url": "https://github.com/Aider-AI/aider",
        "version": "v0.86.0; main commit 5dc9490bb35f9729ef2c95d00a19ccd30c26339c",
        "license": "Apache-2.0",
        "role": "A human-led coding harness centered on repository mapping, constrained edit formats, validation, and Git-backed rollback.",
        "family": "human-led-edit-loop",
        "lesson": "Include human authority, patch representation, repository retrieval, and rollback in the harness treatment; autonomy is not a monotone design objective.",
    },
    {
        "number": 5,
        "slug": "harness-codex-cli",
        "title": "Codex CLI",
        "org": "OpenAI",
        "url": "https://github.com/openai/codex",
        "version": "rust-v0.153.2; commit de7874067fe8cb8f4846dd4d8b848965ce79070f",
        "license": "Apache-2.0 for repository code; hosted models and services are proprietary",
        "role": "An open client and event protocol for coding work with persisted threads, compaction, tools, MCP, collaboration, sandboxes, approvals, and telemetry.",
        "family": "event-sourced-loop",
        "lesson": "Version the open client/protocol separately from the proprietary model and service, and report sandbox and approval modes as independent factors.",
    },
    {
        "number": 6,
        "slug": "harness-claude-code",
        "title": "Claude Code",
        "org": "Anthropic",
        "url": "https://github.com/anthropics/claude-code",
        "version": "v2.1.260; commit b3f0e501b79fe5cfc8c10d18cf3b0b6715c5c2fb",
        "license": "Proprietary; public repository is all rights reserved",
        "role": "A publicly distributed but proprietary coding harness with session persistence, compaction, instructions, skills, tools, hooks, subagents, permissions, and telemetry.",
        "family": "model-directed-loop",
        "lesson": "Do not equate a public repository with open source or infer undocumented internals; separate documented interface behavior from implementation claims.",
    },
    {
        "number": 7,
        "slug": "harness-goose",
        "title": "goose",
        "org": "Agentic AI Foundation",
        "url": "https://github.com/aaif-goose/goose",
        "version": "v1.49.0; commit dce69009546ce5f20522d010fa3f1d57abbe2c3f",
        "license": "Apache-2.0",
        "role": "An MCP-first coding and general agent with recipes, session state, context revision, extension discovery, and delegation.",
        "family": "model-directed-loop",
        "lesson": "Model extension discovery, summarization, execution location, and delegation as explicit policies rather than treating MCP support as one binary feature.",
    },
    {
        "number": 8,
        "slug": "harness-langgraph",
        "title": "LangGraph",
        "org": "LangChain",
        "url": "https://github.com/langchain-ai/langgraph",
        "version": "monorepo sdk==0.4.4; commit 81bf17b23123e4ef8b9d5f49fa09a0122fc2edd1",
        "license": "MIT core",
        "role": "A stateful graph runtime with typed state, reducers, checkpoints, replay, stores, branches, and fan-out.",
        "family": "explicit-graph-runtime",
        "lesson": "Declare graph topology, reducer algebra, checkpoint backend, replay semantics, and any adjacent tracing service independently.",
    },
    {
        "number": 9,
        "slug": "harness-autogen",
        "title": "AutoGen",
        "org": "Microsoft",
        "url": "https://github.com/microsoft/autogen",
        "version": "python-v0.7.5; commit 027ecf0a379bcc1d09956d46d12d44a3ad9cee14",
        "license": "MIT code; CC-BY-4.0 documentation",
        "role": "An actor and multi-agent framework with message runtimes, stateful team loops, tools, code executors, memory protocols, and telemetry.",
        "family": "actor-message-runtime",
        "lesson": "Pin the major architecture generation and successor status; team topology and message protocol are treatment variables, not project-name constants.",
    },
    {
        "number": 10,
        "slug": "harness-ag2",
        "title": "AG2 v1",
        "org": "AG2AI",
        "url": "https://github.com/ag2ai/ag2",
        "version": "v1.0.3; commit d4df5694e53d0533d583a7865023fa2e4e53b674",
        "license": "Apache-2.0",
        "role": "A multi-agent network runtime with run handles, tools, middleware, context policies, compaction, memory streams, code execution, and evaluation surfaces.",
        "family": "actor-message-runtime",
        "lesson": "Report v1 separately from AG2 classic and measure message topology, context policy, executor, and concurrency rather than the framework label alone.",
    },
    {
        "number": 11,
        "slug": "harness-crewai",
        "title": "CrewAI",
        "org": "CrewAI",
        "url": "https://github.com/crewAIInc/crewAI",
        "version": "1.15.20; commit c00e3228fc0036e6d262592b5943979659fcfdac",
        "license": "MIT core",
        "role": "A role-agent and event-flow framework spanning sequential or hierarchical crews, typed flow state, planning, delegation, memory, and tool execution.",
        "family": "explicit-graph-runtime",
        "lesson": "Do not conflate role prompts with independent agents; report process topology, manager policy, code-execution mode, and evaluator dependence.",
    },
    {
        "number": 12,
        "slug": "harness-semantic-kernel",
        "title": "Semantic Kernel",
        "org": "Microsoft",
        "url": "https://github.com/microsoft/semantic-kernel",
        "version": "dotnet-1.80.1; commit f8c5ba7aec210c986086a997fc4eef65190666eb",
        "license": "MIT",
        "role": "An SDK and orchestration framework with kernel functions, agent threads, tool calling, multiple orchestration patterns, and OpenTelemetry.",
        "family": "explicit-graph-runtime",
        "lesson": "Treat experimental APIs and successor transitions as reproducibility risks, and distinguish orchestration from containment and independent evaluation.",
    },
    {
        "number": 13,
        "slug": "harness-llamaagents",
        "title": "LlamaAgents / Workflows",
        "org": "LlamaIndex",
        "url": "https://github.com/run-llama/llama-agents",
        "version": "llama-agents-server@v0.7.1; commit 9bfd8f8ea5d66652d5b6ce933df9cba118f6f863",
        "license": "MIT",
        "role": "A typed asynchronous workflow runtime with events, tasks, commands, reducer-like state, durable execution, and replay.",
        "family": "explicit-graph-runtime",
        "lesson": "Separate workflow semantics from model policy, record durable runtime and storage choices, and pin naming/package transitions.",
    },
    {
        "number": 14,
        "slug": "harness-smolagents",
        "title": "smolagents",
        "org": "Hugging Face",
        "url": "https://github.com/huggingface/smolagents",
        "version": "v1.26.0; commit 30bb1161095dbae2271e6bc3cc4c219cc3897a57",
        "license": "Apache-2.0",
        "role": "A compact ReAct and code-agent library with prompted planning, agent memory, tool calling, managed agents, multiple executors, and callbacks.",
        "family": "model-directed-loop",
        "lesson": "Compare code actions with structured tool calls under the same model and budget, and report the actual executor because local restriction is not equivalent to OS isolation.",
    },
    {
        "number": 15,
        "slug": "harness-pydantic-ai",
        "title": "Pydantic AI and Pydantic AI Harness",
        "org": "Pydantic",
        "url": "https://github.com/pydantic/pydantic-ai",
        "version": "core v2.39.0 / 7d85a07ec8e90f0741e8bd488ce1c4d0898f4618; Harness v0.29.0 / ec4b8615ac820bd5b93f19c00c52db29682a6e96",
        "license": "MIT for both repositories",
        "role": "A typed agent graph and validation loop plus a separate capability-oriented coding harness with planning, repository context, compaction, allowlists, and explorer subagents.",
        "family": "typed-loop-and-capability-harness",
        "lesson": "Pin core and Harness separately; schema validation, retries, context compilation, sandbox subset, and subagent isolation are distinct mechanisms.",
    },
    {
        "number": 16,
        "slug": "harness-haystack",
        "title": "Haystack",
        "org": "deepset",
        "url": "https://github.com/deepset-ai/haystack",
        "version": "v3.1.1; commit 82da3adc2fac4675b80ff5573b790ec07113697b",
        "license": "Apache-2.0",
        "role": "A component-pipeline and agent framework with toolsets, agent-as-tool composition, schema state, asynchronous pipelines, breakpoints, and evaluators.",
        "family": "pipeline-and-model-loop",
        "lesson": "Separate pipeline dataflow, integrated agent loop, evaluator components, and arbitrary host-code execution when specifying the treatment.",
    },
    {
        "number": 17,
        "slug": "harness-letta-code",
        "title": "Letta Code",
        "org": "Letta",
        "url": "https://github.com/letta-ai/letta-code",
        "version": "v0.31.12; commit 047fa6a99d9e83529b3c3e91cd8e3a7835a0f9c2",
        "license": "Apache-2.0",
        "role": "A memory-first coding agent with Git-backed memory files, compaction and dreaming, plans, approvals, isolated subagents, and trajectory export.",
        "family": "model-directed-loop",
        "lesson": "Treat persistent memory, context compaction, background memory work, approval mode, and optional execution isolation as separate interventions.",
    },
    {
        "number": 18,
        "slug": "harness-pocketflow",
        "title": "PocketFlow",
        "org": "The-Pocket",
        "url": "https://github.com/The-Pocket/PocketFlow",
        "version": "main commit f74d023f93607b8c3268133339a5e532a949898c",
        "license": "MIT",
        "role": "A minimal graph scheduler built around node prep–execute–post phases, action-labelled transitions, shared state, and batch or async variants.",
        "family": "explicit-graph-runtime",
        "lesson": "Use minimal schedulers as controls: graph execution alone supplies neither model policy, memory semantics, containment, nor evaluation.",
    },
]


def extract_profiles(text: str) -> dict[int, dict[str, str]]:
    pattern = re.compile(
        r"^### (?P<number>\d+)\. (?P<heading>.+?)\n\n"
        r"\*\*Official sources:\*\* (?P<sources>.+?)\n\n"
        r"\*\*Implementation evidence\.\*\* (?P<implementation>.+?)\n\n"
        r"\*\*Research interpretation \(inference\)\.\*\* (?P<inference>.+?)\n\n"
        r"\*\*Limitations\.\*\* (?P<limitations>.+?)"
        r"(?=\n\n### |\n\n## Cross-cutting)",
        re.MULTILINE | re.DOTALL,
    )
    return {int(m.group("number")): m.groupdict() for m in pattern.finditer(text)}


def math_description(family: str) -> str:
    if "graph" in family or "pipeline" in family:
        return (
            "A useful abstraction is a labelled transition system "
            r"\(s_{t+1}=U_{\ell_t}(s_t,o_t)\), where graph topology, reducer rules, "
            "and scheduling determine the admissible transition relation. The implementation "
            "does not by itself establish a performance theorem."
        )
    if "actor" in family:
        return (
            "The runtime can be represented as communicating state machines with local states "
            r"\(s_t^{(i)}\) and messages \(m_{i\to j,t}\). Correctness depends on delivery, "
            "ordering, shared-resource, and termination assumptions that project documentation "
            "does not generally prove."
        )
    if "human-led" in family:
        return (
            "The intervention is a mixed human–machine policy: proposed edits are sampled from "
            r"\(\pi_\theta(\cdot\mid C(s_t))\), while acceptance, repair, and stopping include "
            "operator decisions. Human time and authority therefore belong in the estimand."
        )
    return (
        "The common loop is "
        r"\(a_t\sim\pi_\theta(\cdot\mid C_H(s_t)),\ o_t=E_H(a_t),\ "
        r"s_{t+1}=U_H(s_t,a_t,o_t)\). Context, executor, update, stopping, and budget "
        "are harness parameters; the implementation alone supplies no causal effect estimate."
    )


def quote_yaml(value: str) -> str:
    return '"' + value.replace('"', '\\"') + '"'


def main() -> None:
    profiles = extract_profiles(SURVEY.read_text(encoding="utf-8"))
    expected = {s["number"] for s in SYSTEMS}
    if set(profiles) != expected:
        missing = sorted(expected - set(profiles))
        extra = sorted(set(profiles) - expected)
        raise SystemExit(f"profile parse mismatch; missing={missing}, extra={extra}")

    OUT.mkdir(parents=True, exist_ok=True)
    for system in SYSTEMS:
        profile = profiles[system["number"]]
        path = OUT / f"{system['slug']}.md"
        body = f'''---
title: {quote_yaml(system['title'])}
author_or_org: {quote_yaml(system['org'])}
date: "2026-09-04"
source_type: "official-implementation-evidence"
url: {quote_yaml(system['url'])}
version_or_commit: {quote_yaml(system['version'])}
accessed: "2026-09-04"
review_status: "reviewed"
evidence_confidence: "high-for-mechanism-medium-for-implications"
license_or_access_notes: {quote_yaml(system['license'])}
---

# {system['slug']} — {system['title']}

## Why this source is in the corpus

This implementation represents the **{system['family']}** family in the comparative survey. It is included to describe a reproducible mechanism and its treatment variables, not to endorse the project or convert project-authored results into independent evidence.

## System or claim described

{system['role']}

## Architecture / mechanism

{profile['implementation']}

## Empirical evidence

The inspected repository, documentation, and release records directly support the implementation description. They do not constitute a controlled, independent estimate of the harness's effect. Any project-authored benchmark or telemetry should be reproduced with a pinned model, prompt, environment, budget, and scorer before comparative use.

## Mathematical or formal content

{math_description(system['family'])}

## What is directly evidenced

**Official sources:** {profile['sources']}

The detailed comparison pins the inspected release or commit, license, loop/state design, action representation, context and memory policy, concurrency, containment, and observability surface.

## What is interpretation or advocacy

{profile['inference']}

## Limitations, incentives, and likely biases

{profile['limitations']}

Project documentation optimizes for adoption and correct use, not neutral causal comparison. Fast-moving release streams also make unversioned project names unreliable experimental treatments.

## Transferable engineering lessons

{system['lesson']}

## Connections to academic work

See the mechanism taxonomy in [`01-definitions-and-taxonomy.md`](../synthesis/01-definitions-and-taxonomy.md), the architecture analysis in [`02-architecture-and-design-patterns.md`](../synthesis/02-architecture-and-design-patterns.md), and the full implementation comparison in [`05-open-source-harnesses.md`](../synthesis/05-open-source-harnesses.md).

## Verification notes

The sources and pinned snapshot were inspected for the 2026-09-04 research cutoff. Version discontinuities and openness caveats are recorded in the full survey. No repository snapshot is redistributed here; the canonical source URL and commit or release identifier are retained.
'''
        path.write_text(body, encoding="utf-8", newline="\n")

    print(f"wrote {len(SYSTEMS)} harness notes to {OUT}")


if __name__ == "__main__":
    main()
