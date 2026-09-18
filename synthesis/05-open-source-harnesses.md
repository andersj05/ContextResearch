# Open-source LLM harnesses: an implementation-grounded survey

- **Research snapshot:** 2026-09-04
- **Scope:** 32 implementation profiles—18 runtime harnesses plus 14 optimizer/self-evolution implementations—selected for mechanism coverage rather than popularity
- **Evidence standard:** official repositories, source code, release records, and first-party documentation
- **Comparison unit:** the named release or commit below—not an unversioned product name

## Executive finding

“LLM harness” does not denote one mechanism. The 18 runtime harnesses fall into four control-loop families:

1. **Model-directed while loops** repeatedly ask a model for an action, execute it, append the observation, and stop on a terminal condition. SWE-agent, mini-SWE-agent, OpenHands, Codex CLI, Claude Code, goose, smolagents, Haystack Agent, Letta Code, and much of Pydantic AI Harness fit here.
2. **Explicit graph or dataflow runtimes** make routing and state transitions first-class. LangGraph, LlamaAgents Workflows, CrewAI Flows, Semantic Kernel orchestrations, and PocketFlow fit here.
3. **Actor or multi-agent runtimes** organize independent stateful agents around messages. AutoGen Core, AG2’s network runtime, and several delegation layers fit here.
4. **Human-led edit loops** keep the operator in the control path and optimize repository retrieval, patch representation, validation, and rollback. Aider is the clearest counterexample to the assumption that more autonomy defines a better harness.

The 14 optimizer/self-evolution profiles add an outer loop around such runtimes. Their first-order distinction is the editable artifact: executable program or workflow structure (AFlow, AgentSquare, ADAS, AutoFlow, and EvoAgentX); graph topology or model assignment (GPTSwarm, Archon, and AgentOpt); persistent text, demonstrations, or context (ACE, GEPA, DSPy, and TextGrad); or model weights and transient runtime roles at the boundary of harness optimization (Agent Lightning and EvoAgent). A generic outer loop is

\[
x_{k+1}\sim Q_\phi(\cdot\mid x_k,\tau_k,A_k),\qquad
(r_{k+1},\tau_{k+1})=\mathcal E(x_{k+1};D_k),\qquad
A_{k+1}=\mathcal U(A_k,x_{k+1},r_{k+1}),
\]

where \(x\) is the editable artifact, \(Q_\phi\) the proposal or learning rule, \(\mathcal E\) the evaluator producing a score and trace, and \(A\) the archive/incumbent state. Research claims are not identifiable unless all four are specified along with the search budget and data-reuse policy.

The common model-driven core can be written as

\[
a_t \sim \pi_\theta(\cdot \mid C(s_t)),\qquad
o_t = E(a_t),\qquad
s_{t+1}=U(s_t,a_t,o_t),
\]

where the scientifically interesting object is usually not just the model policy \(\pi_\theta\), but the harness-specific context compiler \(C\), executor \(E\), update rule \(U\), stopping rule, and budget. Most product documentation describes the whole compound system; it rarely identifies which component caused an observed benchmark result.

Two conclusions follow for research design:

- Study **mechanisms under controlled configurations**, not brand names. “LangGraph,” “OpenHands,” or “Claude Code” can denote many materially different graphs, tools, permissions, prompts, models, and budgets.
- Treat project-authored benchmarks, demos, and telemetry as implementation evidence or hypothesis generators—not as independent causal evidence of harness superiority.

## Scope, labels, and evidence discipline

This survey stops at 32 profiles: 18 runtime harnesses and 14 optimizer/self-evolution implementations. The runtime sample saturated the recurring loop, graph, actor, memory, execution, and observability mechanisms; the optimizer sample saturated the recurring program/workflow mutation, topology/allocation search, textual/context adaptation, archive/acceptance, and policy-learning boundary cases. Selection deliberately includes minimal counterexamples, incomplete implementations, and negative findings as well as feature-rich systems.

Each profile separates:

- **Implementation evidence** — behavior directly supported by the pinned repository, source, or official documentation.
- **Research interpretation (inference)** — a mechanism-level implication drawn from that implementation. These statements are not claims made or experimentally established by the project.
- **Limitations** — missing guarantees, evaluation confounds, unstable APIs, or scope boundaries.

Release dates are GitHub release publication dates when available. A commit is reported when release streams are absent, ambiguous, or split across packages. “Open source” is applied to code under an OSI-style license; a public repository alone is not classified as open source.

## Runtime-harness version and license ledger

| # | Project (official organization) | Role / openness | License | Release or inspected commit | Date |
|---:|---|---|---|---|---|
| 1 | [SWE-agent](https://github.com/SWE-agent/SWE-agent) (SWE-agent) | Coding agent; open source | MIT | [v1.1.0](https://github.com/SWE-agent/SWE-agent/releases/tag/v1.1.0); main also inspected at [`3ea751c`](https://github.com/SWE-agent/SWE-agent/commit/3ea751c087f32b16e039a2233dd6eefecef325d5) | 2025-05-22; commit 2026-07-16 |
| 2 | [mini-SWE-agent](https://github.com/SWE-agent/mini-swe-agent) (SWE-agent) | Minimal coding agent; open source | MIT | [v2.4.6](https://github.com/SWE-agent/mini-swe-agent/releases/tag/v2.4.6); main [`04d809c`](https://github.com/SWE-agent/mini-swe-agent/commit/04d809ceab9df28f9adaed044884180159172930) | 2026-07-23; commit 2026-09-03 |
| 3 | [OpenHands Software Agent SDK](https://github.com/OpenHands/software-agent-sdk) / [OpenHands](https://github.com/OpenHands/OpenHands) | Coding-agent SDK and product; open source client/runtime | MIT | SDK [v1.44.1](https://github.com/OpenHands/software-agent-sdk/releases/tag/v1.44.1), [`f47083c`](https://github.com/OpenHands/software-agent-sdk/commit/f47083cc370a85160f0348f32e531ee3514399e5); product [v1.16.0](https://github.com/OpenHands/OpenHands/releases/tag/v1.16.0) | SDK 2026-08-28; product 2026-08-27; commit 2026-09-04 |
| 4 | [Aider](https://github.com/Aider-AI/aider) (Aider-AI) | Human-led coding harness; open source | Apache-2.0 | [v0.86.0](https://github.com/Aider-AI/aider/releases/tag/v0.86.0); main [`5dc9490`](https://github.com/Aider-AI/aider/commit/5dc9490bb35f9729ef2c95d00a19ccd30c26339c) | 2025-08-09; commit 2026-05-22 |
| 5 | [Codex CLI](https://github.com/openai/codex) (OpenAI) | Open-source client/protocol around proprietary hosted models/services | Apache-2.0 (repository code) | [rust-v0.153.2](https://github.com/openai/codex/releases/tag/rust-v0.153.2), [`de78740`](https://github.com/openai/codex/commit/de7874067fe8cb8f4846dd4d8b848965ce79070f) | 2026-09-03; commit 2026-09-04 |
| 6 | [Claude Code](https://github.com/anthropics/claude-code) (Anthropic) | Publicly distributed coding harness; **proprietary, not open source** | [All rights reserved; Anthropic Commercial Terms](https://github.com/anthropics/claude-code/blob/main/LICENSE.md) | [v2.1.260](https://github.com/anthropics/claude-code/releases/tag/v2.1.260), [`b3f0e50`](https://github.com/anthropics/claude-code/commit/b3f0e501b79fe5cfc8c10d18cf3b0b6715c5c2fb) | 2026-09-03 |
| 7 | [goose](https://github.com/aaif-goose/goose) (Agentic AI Foundation) | Coding/general MCP agent; open source | Apache-2.0 | [v1.49.0](https://github.com/aaif-goose/goose/releases/tag/v1.49.0), [`dce6900`](https://github.com/aaif-goose/goose/commit/dce69009546ce5f20522d010fa3f1d57abbe2c3f) | 2026-09-03 |
| 8 | [LangGraph](https://github.com/langchain-ai/langgraph) (LangChain) | Stateful graph runtime; open source core | MIT | monorepo release [`sdk==0.4.4`](https://github.com/langchain-ai/langgraph/releases/tag/sdk%3D%3D0.4.4); main [`81bf17b`](https://github.com/langchain-ai/langgraph/commit/81bf17b23123e4ef8b9d5f49fa09a0122fc2edd1) | 2026-08-27; commit 2026-09-03 |
| 9 | [AutoGen](https://github.com/microsoft/autogen) (Microsoft) | Actor and multi-agent framework; community-maintained | MIT code; CC-BY-4.0 docs | [python-v0.7.5](https://github.com/microsoft/autogen/releases/tag/python-v0.7.5), [`027ecf0`](https://github.com/microsoft/autogen/commit/027ecf0a379bcc1d09956d46d12d44a3ad9cee14) | 2025-09-30 |
| 10 | [AG2](https://github.com/ag2ai/ag2) (AG2AI) | Multi-agent harness/runtime; open source | Apache-2.0 | [v1.0.3](https://github.com/ag2ai/ag2/releases/tag/v1.0.3), [`d4df569`](https://github.com/ag2ai/ag2/commit/d4df5694e53d0533d583a7865023fa2e4e53b674) | 2026-08-28 |
| 11 | [CrewAI](https://github.com/crewAIInc/crewAI) (CrewAI) | Role-agent and event-flow framework; open-source core | MIT | [1.15.20](https://github.com/crewAIInc/crewAI/releases/tag/1.15.20), [`c00e322`](https://github.com/crewAIInc/crewAI/commit/c00e3228fc0036e6d262592b5943979659fcfdac) | 2026-09-04 |
| 12 | [Semantic Kernel](https://github.com/microsoft/semantic-kernel) (Microsoft) | SDK and orchestration framework; open source | MIT | [dotnet-1.80.1](https://github.com/microsoft/semantic-kernel/releases/tag/dotnet-1.80.1), [`f8c5ba7`](https://github.com/microsoft/semantic-kernel/commit/f8c5ba7aec210c986086a997fc4eef65190666eb) | 2026-09-03 |
| 13 | [LlamaAgents](https://github.com/run-llama/llama-agents) (LlamaIndex) | Durable workflow/runtime packages; open source | MIT | [`llama-agents-server@v0.7.1`](https://github.com/run-llama/llama-agents/releases/tag/llama-agents-server%40v0.7.1); main [`9bfd8f8`](https://github.com/run-llama/llama-agents/commit/9bfd8f8ea5d66652d5b6ce933df9cba118f6f863) | 2026-08-22; commit 2026-09-03 |
| 14 | [smolagents](https://github.com/huggingface/smolagents) (Hugging Face) | Small ReAct/code-agent library; open source | Apache-2.0 | [v1.26.0](https://github.com/huggingface/smolagents/releases/tag/v1.26.0), [`30bb116`](https://github.com/huggingface/smolagents/commit/30bb1161095dbae2271e6bc3cc4c219cc3897a57) | 2026-05-29 |
| 15 | [Pydantic AI](https://github.com/pydantic/pydantic-ai) + [Pydantic AI Harness](https://github.com/pydantic/pydantic-ai-harness) (Pydantic) | Typed agent graph plus separate capability/coding-harness library; open source | MIT (both) | core [v2.39.0](https://github.com/pydantic/pydantic-ai/releases/tag/v2.39.0), [`7d85a07`](https://github.com/pydantic/pydantic-ai/commit/7d85a07ec8e90f0741e8bd488ce1c4d0898f4618); Harness [v0.29.0](https://github.com/pydantic/pydantic-ai-harness/releases/tag/v0.29.0), [`ec4b861`](https://github.com/pydantic/pydantic-ai-harness/commit/ec4b8615ac820bd5b93f19c00c52db29682a6e96) | 2026-09-04; Harness commit 2026-09-03 |
| 16 | [Haystack](https://github.com/deepset-ai/haystack) (deepset) | Component pipeline and agent framework; open source | Apache-2.0 | [v3.1.1](https://github.com/deepset-ai/haystack/releases/tag/v3.1.1), [`82da3ad`](https://github.com/deepset-ai/haystack/commit/82da3adc2fac4675b80ff5573b790ec07113697b) | 2026-09-03 |
| 17 | [Letta Code](https://github.com/letta-ai/letta-code) (Letta) | Memory-first coding agent; open source | Apache-2.0 | [v0.31.12](https://github.com/letta-ai/letta-code/releases/tag/v0.31.12), [`047fa6a`](https://github.com/letta-ai/letta-code/commit/047fa6a99d9e83529b3c3e91cd8e3a7835a0f9c2) | 2026-09-03; commit 2026-09-04 |
| 18 | [PocketFlow](https://github.com/The-Pocket/PocketFlow) (The-Pocket) | Minimal graph scheduler; open source | MIT | no GitHub release; main [`f74d023`](https://github.com/The-Pocket/PocketFlow/commit/f74d023f93607b8c3268133339a5e532a949898c) | 2026-07-26 |

### Version discontinuities that must not be averaged together

- **OpenHands V1:** current engine work lives in `OpenHands/software-agent-sdk`; the `OpenHands/OpenHands` repository is the product shell. Papers or reports about the older V0 controller should not be treated as source-level descriptions of V1.
- **Letta:** the former `letta-ai/letta` Python server was reduced to a landing/archival repository in commit [`87fd37a`](https://github.com/letta-ai/letta/commit/87fd37aab68c7bdd0d66fe63751553756f6af3e5) on 2026-08-16. The current implementation inspected here is `letta-ai/letta-code`; older MemGPT/Letta server results remain historically relevant but are not a current code map.
- **AutoGen:** Microsoft describes AutoGen as community-maintained and directs new users toward Microsoft Agent Framework. Results tied to AutoGen 0.2, 0.4, or current 0.7.x should be versioned separately.
- **AG2:** the current v1 architecture is distinct from the older API, which moved to [`ag2ai/ag2-classic`](https://github.com/ag2ai/ag2-classic). “AG2” without a major version is not a reproducible treatment.
- **Semantic Kernel:** its repository points toward Microsoft Agent Framework as its successor; several orchestration, process, and memory APIs remain experimental or transitional.
- **LlamaIndex naming:** the repository is now titled **LlamaAgents**, while the Python workflow package and surrounding documentation still use “Workflows.”
- **Aider:** the GitHub stable release inspected was v0.86.0, while history/tag material referenced later 0.86.1/0.86.2 identifiers. Pin a commit rather than assuming every distribution channel names the same artifact.
- **LangGraph:** the monorepo has independent package release trains. A tag such as `sdk==0.4.4` does not uniquely version every Python, JavaScript, SDK, and server component.
- **Pydantic AI Harness:** Harness is a separate `pydantic/pydantic-ai-harness` repository and 0.x release train layered on Pydantic AI core. Record both versions; a core release alone does not identify the capability bundle.

## Optimizer/self-evolution implementation ledger

These 14 profiles describe what the inspected implementation actually edits and how its outer loop updates candidates. The linked local notes contain the full official-source trail, exact pin, license/access status, mathematical details, and implementation-versus-inference separation. Project-authored results remain implementation evidence, not independent efficacy evidence.

| # | Implementation, license, and inspected version | Editable artifact and implemented outer loop | Key implementation caveat |
|---:|---|---|---|
| 19 | [AFlow](../source-notes/selfopt-aflow.md) ([repo](https://github.com/FoundationAgents/AFlow); MIT; [`3f4572`](https://github.com/FoundationAgents/AFlow/commit/3f457218fc716093fe53f6df8a5d5e6379d66346), 2025-12-25) | Python operator graph and prompt; score-biased parent sampling → LM mutation → benchmark validation → experience/archive update | Released selector is not conventional UCT/MCTS; the inspected experience formatter labels both success and failure “Absolutely prohibit.” |
| 20 | [AgentSquare](../source-notes/selfopt-agentsquare.md) ([repo](https://github.com/tsinghua-fib-lab/AgentSquare); no root license; [`8f5b3f`](https://github.com/tsinghua-fib-lab/AgentSquare/commit/8f5b3fe5d8a32f9b59d20370823bef2a2c86928c), 2025-11-04) | Planning/reasoning/tool/memory module code and their tuples; LM evolution/recombination plus predictor-gated benchmark evaluation | ALFWorld filters tool-use candidates; planning/reasoning futures can be attributed in the wrong order; public code is not automatically open source without a license. |
| 21 | [ADAS / Meta Agent Search](../source-notes/selfopt-adas.md) ([repo](https://github.com/ShengranHu/ADAS); Apache-2.0; [`2702be`](https://github.com/ShengranHu/ADAS/commit/2702bee8fefda42255efc5be9f60e3bd3db96ae4), 2025-01-28) | Executable Python `forward` method; archive-conditioned LM proposal → two reflections → exception repair → validation/archive insertion | Generated code is installed with `exec` without a sandbox; the README explicitly warns that it may act destructively. |
| 22 | [GPTSwarm](../source-notes/selfopt-gptswarm.md) ([repo](https://github.com/metauto-ai/GPTSwarm); MIT; [`c23a82`](https://github.com/metauto-ai/GPTSwarm/commit/c23a827f561c934ce21dd950408f7606aa4a8821), 2026-02-05) | Inter-agent edge logits; constrained DAG sampling → concurrent utility evaluation → REINFORCE/Adam update; separate prompt-revision path | Edge learning is complete enough to inspect, but node `process_records` is `pass` and its intended retrieval path is commented out. |
| 23 | [EvoAgent](../source-notes/selfopt-evoagent.md) ([repo](https://github.com/siyuyuan/evoagent); no root license; [`fc6d08`](https://github.com/siyuyuan/evoagent/commit/fc6d087b119df69466c2372cfcaf588c040aaba8), 2024-10-19) | Per-instance expert descriptions and synthesized answer; generate role → check → answer → refine, repeated at inference time | The released primary loop does not retain a cross-instance population or reusable optimized harness; “evolution” is largely transient role diversification. |
| 24 | [AutoFlow](../source-notes/selfopt-autoflow.md) ([repo](https://github.com/agiresearch/AutoFlow); Apache-2.0; [`472030`](https://github.com/agiresearch/AutoFlow/commit/47203078a17e6612c79fe190d437ea58ae8c4d51), 2024-09-11) | Natural-language workflow DSL; conversational score/error feedback and complete rewrites, or PPO training of a workflow generator | Reproduction needs external assets and historical dependencies; the OpenAGI path repeatedly observes test results when training improves. |
| 25 | [EvoAgentX](../source-notes/selfopt-evoagentx.md) ([repo](https://github.com/ANative-Lab/EvoAgentX); MIT with mixed-notice caveat; [v0.1.4](https://github.com/ANative-Lab/EvoAgentX/releases/tag/v0.1.4), main [`d77fd6`](https://github.com/ANative-Lab/EvoAgentX/commit/d77fd6b9a3e76c8dd83bebe3374c53a3f5d16f54)) | Optimizer-dependent prompt, code, workflow, or registered parameters; includes AFlow-style search and MAP-Elites quality-diversity archives | Umbrella API combines distinct treatments; automatic workflow reviewer initialization is TODO/commented out; no succession relation to `siyuyuan/evoagent` was verified. |
| 26 | [ACE](../source-notes/selfopt-ace.md) ([repo](https://github.com/ace-agent/ace); Apache-2.0; [`82709d`](https://github.com/ace-agent/ace/commit/82709de050e1db6e6ef2f07bcb0393560b94992a), 2026-08-24) | Persistent playbook bullets supplied as context; Generator → evaluator → Reflector → Curator with offline validation-best or online updates | Despite a larger operation vocabulary in documentation, the current application path fully applies only `ADD`; online adaptation is not held-out evaluation. |
| 27 | [GEPA](../source-notes/selfopt-gepa.md) ([repo](https://github.com/gepa-ai/gepa); MIT; [v0.1.4](https://github.com/gepa-ai/gepa/releases/tag/v0.1.4), main [`0632cd`](https://github.com/gepa-ai/gepa/commit/0632cdb5dcc052e690eab439e1b4a7e3e9cfe407)) | Named serialized components including prompts, code, tool text, or architecture; trace-conditioned reflection/mutation → acceptance → Pareto-frontier update and optional merge | Adaptive validation reuse risks overfitting; arbitrary code needs external containment; the optional meta-harness is only layered openness because its default proposer is proprietary Claude Code. |
| 28 | [DSPy optimizers](../source-notes/selfopt-dspy.md) ([repo](https://github.com/stanfordnlp/dspy); MIT; [3.3.1](https://github.com/stanfordnlp/dspy/releases/tag/3.3.1), main [`35ef21`](https://github.com/stanfordnlp/dspy/commit/35ef21f1689576c4fbe06c27e22eabb5db1b24b6)) | Predictor instructions and demonstrations, or Flex module source; MIPROv2 Bayesian search and GEPA reflection/Pareto search | `dspy.GEPA` defaults `valset` to `trainset` when omitted; prompt/demo compilation and source rewriting are materially different experiments. |
| 29 | [TextGrad](../source-notes/selfopt-textgrad.md) ([repo](https://github.com/zou-group/textgrad); MIT; [v0.1.6](https://github.com/zou-group/textgrad/releases/tag/v0.1.6), main [`75e912`](https://github.com/zou-group/textgrad/commit/75e912e210864b61999781778cdf756d4468120f)) | Text variables such as prompts, code, or solutions; computation-graph-routed verbal criticism → LM rewrite | “Gradient,” “backpropagation,” and “descent” are interface analogies; `step()` installs a rewrite without objective re-evaluation, line search, or rollback. |
| 30 | [Archon ITAS](../source-notes/selfopt-archon.md) ([repo](https://github.com/ScalingIntelligence/Archon); Apache-2.0; [`07114d`](https://github.com/ScalingIntelligence/Archon/commit/07114d77af283b6e8185a49ebf22216fdbbf2a55), 2025-03-07) | JSON generator/ranker/critic/fuser architecture; random, grid, or GP/Bayesian search under an inference-call cap | The pinned entry point has deterministic defects, including a wrong class name, invalid `append`, reversed final ranking, and a searched variable that does not affect generation. |
| 31 | [AgentOpt](../source-notes/selfopt-agentopt.md) ([repo](https://github.com/AgentOptimizer/agentopt); Apache-2.0; [v0.1.0](https://github.com/AgentOptimizer/agentopt/releases/tag/v0.1.0), main [`08b2d2`](https://github.com/AgentOptimizer/agentopt/commit/08b2d2c7fe370c884d956afbe540a09abc163c27)) | Per-call-site model assignment; exhaustive, arm-elimination, Matrix-UCB, low-rank, or GP search over a fixed harness | It does not edit prompts, tools, memory, or topology; caching changes the stochastic response distribution, and the only built-in online router is random. |
| 32 | [Agent Lightning v1](../source-notes/selfopt-agent-lightning.md) ([repo](https://github.com/microsoft/agent-lightning); MIT; [v1.0.1](https://github.com/microsoft/agent-lightning/releases/tag/v1.0.1), main [`218f1f`](https://github.com/microsoft/agent-lightning/commit/218f1f7c0bac0800de4d5a4e5e6f61cf7b5038b4)) | Model policy weights/checkpoint; gateway-captured real-harness trajectories → aggregation/masking → `verl` PPO training | The external harness remains fixed, so this is policy learning rather than harness-source optimization; v1 is a complete redesign and must not inherit v0.x mechanisms. |

## Runtime-harness architecture comparison

| System | Loop / state | Tools and action representation | Context, memory, planning | Concurrency | Containment / approval | Tracing and evaluation |
|---|---|---|---|---|---|---|
| SWE-agent | model→action→environment observation; trajectory state | parsed shell/tool actions | history processors; prompt/model planning | batch jobs and competitive attempts | SWE-ReX/Docker environment options | trajectories/hooks; SWE-bench-oriented evaluation |
| mini-SWE-agent | compact message-list while loop | model action executed by environment protocol | raw history plus configured limits; no native planner | task-level external parallelism | local, Docker, or other environment backend | complete trajectory; benchmark runners |
| OpenHands SDK | stateless `Agent.step()` over an event view; `Conversation` owns lifecycle | typed action/observation events, executor tools, MCP | condensers; event persistence; optional Markdown memory | parallel tool calls; subagent task tool | local workspace or container/remote agent server; confirmations | event stream, hooks, OpenTelemetry; separate benchmark repo |
| Aider | human-led request/edit/validate cycle | constrained edit formats and shell/test feedback | ranked repository map; architect/editor split | no central multi-agent scheduler | executes in operator repository; Git checkpoints/undo | edit history, lint/tests, project benchmark |
| Codex CLI | thread→turn→item event protocol | shell, patch/file, MCP, web, collaboration items | persisted history, compaction, plans, filesystem/Git | tool and subagent collaboration modes | read-only/workspace-write/full-access sandboxes plus approvals | structured events and OpenTelemetry; no intrinsic neutral scorer |
| Claude Code | documented gather→act→verify loop | built-in tools, MCP, hooks | JSONL sessions, compaction, `CLAUDE.md`, skills, auto-memory | foreground/background subagents and worktrees | permissions plus OS-level sandbox configuration | hooks and OpenTelemetry; proprietary internals/evaluation |
| goose | model/tool/result loop | MCP-first extensions and recipes | sessions, summarization and context revision | independent agents; ACP delegation | host execution by default; dedicated VM/container advised for isolation | session records; limited intrinsic evaluation |
| LangGraph | graph nodes/edges over typed state; Pregel-style supersteps | arbitrary node functions and `ToolNode` | reducers, checkpoints, per-thread state, cross-thread Store | `Send` fan-out, branch and tool parallelism | arbitrary application code; no core OS sandbox | state history/replay; LangSmith is a separate tracing/eval service |
| AutoGen | actor messages at Core layer; stateful AgentChat loops | tools, code executors, inter-agent messages | agent/team save-load and memory protocol | actor concurrency; team patterns | local or Docker code executors | OpenTelemetry; legacy/project-authored benchmark tooling |
| AG2 v1 | agent run handles plus network/hub message runtime | tools, middleware, subtasks, channel messages | context policies, compaction, knowledge, memory stream | `asyncio` subtask fan-out and network agents | local, Docker, and hosted executors | WAL/event surfaces, OpenTelemetry, dataset/scorer APIs |
| CrewAI | sequential/hierarchical Crews; event-driven Flows | role agents, tasks, tools, routers | optional planner; flow state; composite memory | crew delegation and flow branches | opt-in Docker “safe” code mode or local “unsafe” mode | hooks/third-party tracing; repeated LLM-scored tests |
| Semantic Kernel | function-calling agent loop plus orchestration patterns | kernel functions/plugins and agent messages | `AgentThread`, experimental memory/process APIs | concurrent/sequential/handoff/group/Magentic patterns | no core OS sandbox | OpenTelemetry; no intrinsic neutral evaluator found |
| LlamaAgents | typed async workflow events; runtime reducer | events, tasks, commands and model/tool-agnostic handlers | workflow `Context`; durable state with DBOS runtime | async tasks, replicas and branch commands | application-defined; no core sandbox | event streaming, persistence/replay; adjacent eval tools |
| smolagents | ReAct-style `MultiStepAgent` | Python code actions or structured tool calls | `AgentMemory`; periodic prompted planning | concurrent tool calls; managed agents | local restricted interpreter or remote/container executor | step callbacks and OpenTelemetry; project-authored evals |
| Pydantic AI / Harness | typed graph plus model/tool retry loop | schema-validated tools, outputs and dependencies | serializable history; durable adapters; harness plan/repo context/compaction | async tools and fresh-context explorer subagents | core host tools; Harness allowlists and Monty subset sandbox | OpenTelemetry/Logfire and `pydantic-evals` |
| Haystack | integrated Agent model/tool loop; component pipelines | toolsets, agent-as-tool, model tool calls | per-run schema/merge state; pipeline data | tool concurrency and `AsyncPipeline` | arbitrary Python; no core OS sandbox | hooks, breakpoints, OpenTelemetry and evaluator components |
| Letta Code | outer approval loop around streaming agent turns | filesystem, shell, plan/task and subagent tools | Git-backed MemFS, always-loaded system memory, compaction, dreaming | isolated foreground/background subagents and memory workers | permission modes; local or optional isolated cloud computers | event/trajectory export and product telemetry; no neutral scorer |
| PocketFlow | node `prep→exec→post`; action-labeled transitions | no built-in LLM/tool abstraction | shared dictionary only; user-built planning/memory | batch/async variants including `gather` | none | none beyond user code |

## Runtime-harness implementation profiles

### 1. SWE-agent — SWE-agent

**Official sources:** [repository](https://github.com/SWE-agent/SWE-agent), [documentation](https://swe-agent.com/latest/), [configuration reference](https://swe-agent.com/latest/config/), [license](https://github.com/SWE-agent/SWE-agent/blob/main/LICENSE).

**Implementation evidence.** The agent repeatedly renders model input from a trajectory, obtains a structured or parsed action, sends it to an execution environment, appends the observation, and terminates on a configured exit or limit. History processors can alter what portion or summary of the trajectory is returned to the model. Hooks expose lifecycle events, and trajectories preserve actions and observations. Execution is normally mediated by SWE-ReX and can use Docker-backed environments. The repository also supports running independent tasks in batches and competitive/multiple attempts with a discriminator.

**Research interpretation (inference).** SWE-agent is best modeled as an error-feedback controller around a repository environment. Its important treatment variables are action grammar, environment image, history processor, prompt, model, step/cost limits, and discriminator. “Planning” is primarily model-internal or prompt-elicited rather than a separately verified search algorithm.

**Limitations.** The maintainers position mini-SWE-agent as the simpler actively recommended path. SWE-bench integration is valuable but project-authored configurations do not isolate harness effects from model, prompt, tool, budget, and environment changes. **Confidence: high** for loop/environment/trajectory mechanics; **medium** for comparative research implications.

### 2. mini-SWE-agent — SWE-agent

**Official sources:** [repository](https://github.com/SWE-agent/mini-swe-agent), [documentation](https://mini-swe-agent.com/latest/), [source tree](https://github.com/SWE-agent/mini-swe-agent/tree/main/src/minisweagent), [license](https://github.com/SWE-agent/mini-swe-agent/blob/main/LICENSE).

**Implementation evidence.** The core separates `Agent`, `Model`, and `Environment` protocols. A default agent holds a message list, queries the model, executes the resulting action through an environment, appends the observation, and repeats until an exit condition or resource-limit exception. The resulting trajectory retains the conversation and execution record. Environment backends include local and isolated options.

**Research interpretation (inference).** This is a useful lower-bound architecture: it tests how far a transparent loop, strong model, and well-defined environment can go without a graph engine, retrieval database, durable distributed runtime, or elaborate planner. It is therefore a meaningful control condition for claims that orchestration complexity itself improves performance.

**Limitations.** The default local environment can execute on the host and is not a security boundary. There is no native long-term retrieval memory, central multi-agent protocol, or explicit search planner. **Confidence: high.**

### 3. OpenHands Software Agent SDK — OpenHands

**Official sources:** [SDK repository](https://github.com/OpenHands/software-agent-sdk), [product repository](https://github.com/OpenHands/OpenHands), [SDK documentation](https://docs.openhands.dev/sdk/), [benchmarks repository](https://github.com/OpenHands/benchmarks), [license](https://github.com/OpenHands/software-agent-sdk/blob/main/LICENSE).

**Implementation evidence.** In the V1 SDK, `Agent.step()` is intentionally stateless: it receives a view of conversation events and emits typed events. `Conversation` owns state, persistence, execution, lifecycle, and agent coordination. Tools use typed action/observation/executor interfaces and can be extended through MCP. Event files and base state support persistence; context condensers reduce history; an opt-in Markdown memory design distinguishes always-visible durable instructions from discoverable files. Parallel tool calls are configurable, and a task tool can delegate to subagents. A `LocalWorkspace` executes locally, whereas Docker/remote Agent Server modes provide stronger isolation. Security confirmations, event hooks, and OpenTelemetry-compatible tracing are exposed.

**Research interpretation (inference).** Event sourcing separates the policy transition from orchestration and makes replay, auditing, and counterfactual context experiments cleaner than a mutable monolithic loop. This does not make model calls deterministic: replayability of control-plane events is distinct from repeatability of external side effects or sampled model output.

**Limitations.** V0 papers and source analyses can misdescribe V1. Optional memory and parallelism are configuration choices, not universal properties. The official benchmark package is not an independent evaluator. **Confidence: high** for V1 architecture; **medium** for deployment-specific behavior.

### 4. Aider — Aider-AI

**Official sources:** [repository](https://github.com/Aider-AI/aider), [documentation](https://aider.chat/docs/), [repository map documentation](https://aider.chat/docs/repomap.html), [edit formats](https://aider.chat/docs/more/edit-formats.html), [benchmarks](https://aider.chat/docs/leaderboards/), [license](https://github.com/Aider-AI/aider/blob/main/LICENSE.txt).

**Implementation evidence.** Aider is organized around an operator conversation rather than unattended task completion. It constructs a token-budgeted repository map using parsed symbols and a ranked dependency/reference graph, asks a model for edits in constrained formats, applies them, and can feed lint or test failures back into the next turn. Architect mode separates a reasoning/planning model from an editor model. Git integration creates checkpoints and supports undo.

**Research interpretation (inference).** Aider suggests an alternative harness hypothesis: repository selection, change representation, validation feedback, and recoverability may matter more than autonomous step count. Architect/editor mode is a role decomposition, but not evidence of independent agents or a search procedure.

**Limitations.** Host-repository execution is not a robust sandbox. There is no central durable multi-agent scheduler or general branch-concurrency semantics. Its leaderboard is project-authored and entangles model, edit format, prompting, and retry policy. **Confidence: high.**

### 5. Codex CLI — OpenAI

**Official sources:** [repository](https://github.com/openai/codex), [CLI documentation](https://learn.chatgpt.com/docs/codex/cli), [agent approvals and security](https://learn.chatgpt.com/docs/agent-approvals-security), [repository documentation](https://github.com/openai/codex/tree/main/docs), [protocol source](https://github.com/openai/codex/tree/main/codex-rs/protocol), [license](https://github.com/openai/codex/blob/main/LICENSE).

**Implementation evidence.** The Rust client exposes a structured thread→turn→item protocol. Items/events cover model reasoning, plans, command execution, file changes, MCP calls, web operations, compaction, and collaboration/subagent activity. Conversation history and workspace/Git state provide working context. The client supports MCP server configuration, tool controls, approvals, subagents, and multiple sandbox policies, including read-only, workspace-write, and full access. It also exposes structured event output and OpenTelemetry configuration.

**Research interpretation (inference).** Codex demonstrates **layered openness**: the client, protocol, and sandbox implementation can be inspected under Apache-2.0, while hosted model weights and service-side behavior remain proprietary. Reproducible studies must therefore identify which layer is under test and capture model/service identifiers as external dependencies.

**Limitations.** An open client is not an open end-to-end agent. Plans are model-produced mutable artifacts rather than guaranteed optimal policies. The CLI does not provide a neutral intrinsic task evaluator. **Confidence: high** for client-side mechanisms; **low to medium** for unobservable service internals.

### 6. Claude Code — Anthropic

**Official sources:** [public distribution/issues repository](https://github.com/anthropics/claude-code), [overview](https://code.claude.com/docs/en/overview), [memory](https://code.claude.com/docs/en/memory), [subagents](https://code.claude.com/docs/en/sub-agents), [sandboxing](https://code.claude.com/docs/en/sandboxing), [monitoring](https://code.claude.com/docs/en/monitoring-usage), [proprietary license](https://github.com/anthropics/claude-code/blob/main/LICENSE.md).

**Implementation evidence.** First-party documentation describes a gather→act→verify interaction cycle; persistent JSONL sessions and checkpoints; automatic context compaction; project/user instruction files (`CLAUDE.md`); auto-memory and skills; built-in tools and MCP; hooks; foreground/background subagents; optional Git worktrees; permission rules; OS-level sandbox settings; and OpenTelemetry monitoring.

**Research interpretation (inference).** Public documentation reveals the product-level control surfaces but not enough implementation detail to validate scheduler, context-selection, or policy behavior independently. It should be analyzed as a black- or gray-box proprietary harness, not grouped with source-available runtimes.

**Limitations.** The public repository is not the full implementation and its license is proprietary; **Claude Code is not open source**. Documentation supports feature existence but cannot establish hidden defaults, ordering, or causal efficacy. **Confidence: high** for documented interfaces; **low** for internals.

### 7. goose — Agentic AI Foundation

**Official sources:** [repository](https://github.com/aaif-goose/goose), [documentation](https://block.github.io/goose/), [extensions documentation](https://block.github.io/goose/docs/getting-started/using-extensions/), [license](https://github.com/aaif-goose/goose/blob/main/LICENSE).

**Implementation evidence.** goose implements a session-oriented model/tool/result loop and makes MCP extensions the principal tool boundary. Recipes package instructions and extension configuration for repeatable tasks. The runtime records sessions and revises context through summarization/deletion policies. It can delegate across ACP-compatible agents and run independent agents concurrently.

**Research interpretation (inference).** MCP-first architecture reduces tool-adapter coupling and makes tool availability an explicit experimental factor. Protocol interoperability does not imply semantic equivalence: two MCP servers with the same nominal capability can differ in schemas, latency, permissions, and error behavior.

**Limitations.** Local tools commonly execute with the user’s host privileges; official security guidance recommends a dedicated VM/container when isolation is required. Evaluation is not a first-class neutral subsystem. **Confidence: high** for protocol and session architecture; **medium** for extension-dependent behavior.

### 8. LangGraph — LangChain

**Official sources:** [repository](https://github.com/langchain-ai/langgraph), [overview](https://docs.langchain.com/oss/python/langgraph/overview), [graph API](https://docs.langchain.com/oss/python/langgraph/graph-api), [persistence](https://docs.langchain.com/oss/python/langgraph/persistence), [durable execution](https://docs.langchain.com/oss/python/langgraph/durable-execution), [LangChain agents](https://docs.langchain.com/oss/python/langchain/agents), [license](https://github.com/langchain-ai/langgraph/blob/main/LICENSE).

**Implementation evidence.** LangGraph represents an application as nodes and edges over declared state. Its Pregel-inspired runtime advances active nodes in supersteps; reducers define how updates merge. `Command` combines state updates with routing, while `Send` creates dynamic fan-out. Checkpointers persist per-thread state and pending writes, enabling interrupts, resume, state history, and time-travel-style replay. A separate Store supports cross-thread data. Tool nodes and graph branches can run in parallel. LangChain’s higher-level agents are built on LangGraph, so this survey treats LangChain agents as a configuration/wrapper layer rather than counting them as a second control runtime.

**Research interpretation (inference).** LangGraph moves control policy from a hidden prompt into an inspectable graph, enabling ablations on topology and routing. Parallel correctness still depends on reducer semantics and side-effect discipline. For independent actions \(a,b\), order-insensitive execution would require

\[
U(U(s,a),b)=U(U(s,b),a),
\]

a property the runtime cannot generally prove for arbitrary Python nodes.

**Limitations.** Nodes can execute arbitrary application code; the core is not an OS sandbox. Idempotency, external-side-effect recovery, and conflicting state updates remain application responsibilities. LangSmith observability/evaluation is a separate service and must not be reported as an intrinsic property of the MIT core. **Confidence: high.**

### 9. AutoGen — Microsoft

**Official sources:** [repository](https://github.com/microsoft/autogen), [stable documentation](https://microsoft.github.io/autogen/stable/), [Core concepts](https://microsoft.github.io/autogen/stable/user-guide/core-user-guide/core-concepts/architecture.html), [AgentChat](https://microsoft.github.io/autogen/stable/user-guide/agentchat-user-guide/index.html), [MIT code license](https://github.com/microsoft/autogen/blob/main/LICENSE-CODE), [CC-BY-4.0 repository-content license](https://github.com/microsoft/autogen/blob/main/LICENSE).

**Implementation evidence.** AutoGen Core is an event-driven actor/message runtime. AgentChat supplies higher-level stateful agents and team patterns, including round-robin, selector, swarm, and Magentic-style coordination. `AssistantAgent` can execute tools, iterate tool calls, and use a memory protocol. Agents and teams expose save/load state. Code execution can be local or Docker-backed. Tracing integrates with OpenTelemetry.

**Research interpretation (inference).** The two-layer design distinguishes transport/scheduling from conversational policy, which is useful for experiments on topology. Named team patterns should be treated as routing algorithms plus prompts and termination rules—not as evidence that dialogue among agents improves task accuracy.

**Limitations.** The repository is community-maintained and Microsoft directs new work to Microsoft Agent Framework. Older AGBench and AutoGen 0.2 results do not directly validate current 0.7.x APIs. Local execution is not isolated. **Confidence: high** for current documented mechanics; **medium** for continuity with prior evaluations.

### 10. AG2 v1 — AG2AI

**Official sources:** [repository](https://github.com/ag2ai/ag2), [documentation](https://docs.ag2.ai/), [classic repository](https://github.com/ag2ai/ag2-classic), [license](https://github.com/ag2ai/ag2/blob/main/LICENSE).

**Implementation evidence.** AG2 v1 exposes agents and asynchronous run handles, a bare Agent Harness, context policies, compaction, knowledge/memory integrations, middleware, and fresh-context subtasks. Subtasks can fan out with `asyncio.gather`. Its network design adds agents connected through a hub, channels, per-channel write-ahead logs, and governance controls. Execution backends include local, Docker, and hosted environments. Evaluation APIs cover datasets, scorers, repeats, and concurrency; OpenTelemetry instrumentation is available.

**Research interpretation (inference).** Fresh-context subtasks implement an information-boundary experiment: delegation can reduce context interference at the cost of communication loss. A hub/WAL architecture improves auditability and recovery but creates a coordination bottleneck and does not validate message truthfulness.

**Limitations.** v1 was new at the snapshot date; its operational maturity and independent evaluation record were limited. The Classic-to-v1 discontinuity makes unversioned comparisons invalid. Executor safety depends on backend selection. **Confidence: high** for source-described interfaces; **medium** for production properties.

### 11. CrewAI — CrewAI

**Official sources:** [repository](https://github.com/crewAIInc/crewAI), [documentation](https://docs.crewai.com/), [Crews](https://docs.crewai.com/en/concepts/crews), [Flows](https://docs.crewai.com/en/concepts/flows), [planning](https://docs.crewai.com/en/concepts/planning), [memory](https://docs.crewai.com/en/concepts/memory), [license](https://github.com/crewAIInc/crewAI/blob/main/LICENSE).

**Implementation evidence.** CrewAI contains two control abstractions: Crews execute role/task configurations sequentially or through a hierarchical manager; Flows use event listeners, routers, branches, loops, and explicit state. Optional planning performs an additional planning-model pass. The memory layer extracts facts and scores recall using semantic similarity, recency, and importance. Flow persistence supports checkpoint, resume, and fork behavior. Code execution is opt-in and distinguishes Docker-oriented “safe” mode from direct local “unsafe” mode. Hooks and external tracing integrations expose runs; test tooling can repeat executions and use LLM-based scoring.

**Research interpretation (inference).** Crews and Flows should be separate experimental categories: role-based delegation and explicit event graphs have different causal mechanisms. Composite memory can be represented schematically as

\[
R(m,q)=\alpha\,\mathrm{sim}(m,q)+\beta\,\mathrm{recency}(m)+\gamma\,\mathrm{importance}(m),
\]

but actual normalization, extraction errors, and weights must be pinned before the formula is scientifically meaningful.

**Limitations.** Planner output is another model-generated prompt artifact, not a proven search plan. Crews, Flow state, and memory create overlapping state surfaces. LLM-as-judge tests introduce provider, prompt, calibration, and self-preference confounds. “Safe” mode means the configured container path, not a universal proof of containment. **Confidence: high** for interfaces; **medium** for memory/scoring effects.

### 12. Semantic Kernel — Microsoft

**Official sources:** [repository](https://github.com/microsoft/semantic-kernel), [overview](https://learn.microsoft.com/en-us/semantic-kernel/overview/), [agents](https://learn.microsoft.com/en-us/semantic-kernel/frameworks/agent/), [orchestration](https://learn.microsoft.com/en-us/semantic-kernel/frameworks/agent/agent-orchestration/), [process framework](https://learn.microsoft.com/en-us/semantic-kernel/frameworks/process/process-framework), [license](https://github.com/microsoft/semantic-kernel/blob/main/LICENSE).

**Implementation evidence.** A Kernel registers functions/plugins and participates in a model function-calling loop. `AgentThread` abstracts local or service-hosted conversation state. Orchestration packages implement concurrent, sequential, handoff, group-chat, and Magentic patterns. Older planner APIs were removed in favor of function calling as the planning mechanism. Contextual function selection can use embeddings to reduce the visible function set. The Process Framework and several memory capabilities provide explicit stateful workflows but are marked experimental. Telemetry follows OpenTelemetry conventions.

**Research interpretation (inference).** Semantic Kernel illustrates a broad industry shift from symbolic “planner” objects to model-mediated function selection. That renaming should not be interpreted as the disappearance of planning; it changes where the routing policy resides and how observable it is.

**Limitations.** Core functions are arbitrary application code and have no universal OS sandbox. Multiple experimental/transitional APIs and the Microsoft Agent Framework successor warning limit longitudinal comparability. No intrinsic neutral task evaluator was found in the core. **Confidence: high** for documented APIs; **medium** for successor-era stability.

### 13. LlamaAgents / Workflows — LlamaIndex

**Official sources:** [repository](https://github.com/run-llama/llama-agents), [LlamaIndex Workflows documentation](https://developers.llamaindex.ai/python/framework/module_guides/workflow/), [runtime source](https://github.com/run-llama/llama-agents/tree/main/src), [packages](https://github.com/run-llama/llama-agents/tree/main/packages), [license](https://github.com/run-llama/llama-agents/blob/main/LICENSE).

**Implementation evidence.** Workflows are asynchronous, typed, event-driven programs with a `Context` for state and event exchange. The basic runtime schedules work in memory with `asyncio`. A durable DBOS-backed runtime models control-plane evolution as a reducer from state and tick/input to new state plus commands, then persists enough information for rehydration, retry, and replicas. REST/event streaming and human-in-the-loop interactions are supported. The core runtime is model/tool agnostic.

**Research interpretation (inference).** Durable workflow replay can make scheduler state deterministic while external model calls and tools remain stochastic or non-idempotent. A precise claim should therefore distinguish **control-plane replay** from **end-to-end deterministic replay**.

**Limitations.** Durability depends on the selected runtime/backend. User handlers can invoke arbitrary code, so there is no core sandbox. Evaluation and richer observability largely live in adjacent LlamaIndex components. Naming and package boundaries are in transition. **Confidence: high** for workflow/runtime design; **medium** for deployment guarantees.

### 14. smolagents — Hugging Face

**Official sources:** [repository](https://github.com/huggingface/smolagents), [documentation](https://huggingface.co/docs/smolagents/index), [agents guide](https://huggingface.co/docs/smolagents/guided_tour), [secure code execution](https://huggingface.co/docs/smolagents/tutorials/secure_code_execution), [license](https://github.com/huggingface/smolagents/blob/main/LICENSE).

**Implementation evidence.** `MultiStepAgent` implements a ReAct-style step loop with `AgentMemory`. `ToolCallingAgent` emits structured tool calls, while `CodeAgent` emits Python actions. `planning_interval` periodically inserts an explicit planning step. Agents can be exposed as managed tools to other agents. Independent tool calls can use multiple threads. Local code execution uses a restricted interpreter/AST policy; remote Docker or hosted executors are available. Step callbacks and OpenTelemetry-compatible instrumentation expose runs.

**Research interpretation (inference).** The code-versus-tool-call choice is an action-language experiment. Code can compact multiple operations and local transformations into one model output, while structured calls constrain syntax and simplify authorization. Either advantage is empirical and task-dependent.

**Limitations.** The documentation explicitly warns that the local restricted interpreter is not a complete security boundary and can be bypassed; stronger isolation requires a remote/container executor. APIs have experimental surfaces, durable checkpointing and long-term retrieval are not central, and published evaluations are project-authored. **Confidence: high.**

### 15. Pydantic AI and Pydantic AI Harness — Pydantic

**Official sources:** [Pydantic AI repository](https://github.com/pydantic/pydantic-ai), [Pydantic AI documentation](https://ai.pydantic.dev/), [agents](https://ai.pydantic.dev/agents/), [durable execution](https://ai.pydantic.dev/durable_execution/), [evaluation](https://ai.pydantic.dev/evals/), [Pydantic AI Harness repository](https://github.com/pydantic/pydantic-ai-harness), [Coder composition](https://github.com/pydantic/pydantic-ai-harness/blob/main/docs/coder.md), [code-mode sandbox](https://github.com/pydantic/pydantic-ai-harness/blob/main/docs/code-mode.md), [core license](https://github.com/pydantic/pydantic-ai/blob/main/LICENSE), [Harness license](https://github.com/pydantic/pydantic-ai-harness/blob/main/LICENSE).

**Implementation evidence.** The core agent is a typed state graph with schema-validated dependencies, tools, outputs, retry paths, and serializable message history. Durable integrations include Temporal, DBOS, and Prefect. `pydantic-evals` supplies dataset/case abstractions, evaluators, assertions, repeated execution, and reporting; OpenTelemetry/Logfire capture traces. The separate Harness repository bundles repository/filesystem context, allowlisted shell capabilities, structured plan state, tool-result clearing, compaction, tool search, memory, and a read-only explorer subagent. Explorer tasks receive fresh contexts and can run in parallel. Code mode uses Monty, a restricted Python subset, with explicit mounted capabilities.

**Research interpretation (inference).** Typed validation changes the error channel: malformed model output becomes a structured retry observation instead of an uncontrolled parse failure. This may improve recoverability but can also increase calls and produce evaluator-visible selection effects when only successful retries are retained.

**Limitations.** Core tools normally execute as host application code; schemas and allowlists are not OS isolation. Harness is a comparatively young 0.x capability layer, so findings should pin exact versions. Fresh-context explorer agents trade reduced contamination for lossy summaries. **Confidence: high** for core and documented Harness interfaces; **medium** for young Harness operational behavior.

### 16. Haystack — deepset

**Official sources:** [repository](https://github.com/deepset-ai/haystack), [documentation](https://docs.haystack.deepset.ai/), [Agent component](https://docs.haystack.deepset.ai/docs/agent), [AsyncPipeline](https://docs.haystack.deepset.ai/docs/asyncpipeline), [evaluation](https://docs.haystack.deepset.ai/docs/evaluation), [tracing](https://docs.haystack.deepset.ai/docs/tracing), [license](https://github.com/deepset-ai/haystack/blob/main/LICENSE.txt).

**Implementation evidence.** The current v3 Agent owns the model/tool loop: it calls a chat generator, executes selected tools/toolsets, returns tool errors as observations, invokes hooks, and stops on text, configured exit conditions, or a maximum step count. Agent `State` uses a schema and merge handlers. Tool calls can run concurrently with a configurable default. `AgentTool` exposes another agent as a tool and can isolate delegated context. `AsyncPipeline` schedules independent graph components concurrently. Breakpoints, hooks, tracing integrations, OpenTelemetry, and evaluator components are available.

**Research interpretation (inference).** Returning tool exceptions to the model turns runtime failure into corrective feedback. Whether this is beneficial depends on error specificity and budget; it can also create retry loops that look like deliberation while merely consuming tokens.

**Limitations.** Agent State is primarily per run, not automatically long-term memory. Components and tools may execute arbitrary Python with no core OS sandbox. Older documentation in which a separate `ToolInvoker` performed execution can be stale for v3.1.1. **Confidence: high** for current source; **medium** for version-crossing comparisons.

### 17. Letta Code — Letta

**Official sources:** [repository](https://github.com/letta-ai/letta-code), [current README](https://github.com/letta-ai/letta-code/blob/main/README.md), [source tree](https://github.com/letta-ai/letta-code/tree/main/src), [platform documentation](https://docs.letta.com/), [legacy repository notice](https://github.com/letta-ai/letta), [license](https://github.com/letta-ai/letta-code/blob/main/LICENSE).

**Implementation evidence.** Letta Code’s headless outer loop sends a turn, streams model events, classifies requested operations as allow/deny/ask, executes approved tools, returns results, and repeats. Its local provider executor estimates context use before a request, reserves a margin, and compacts when necessary. MemFS stores Markdown in a Git-backed tree: `system/` material is injected into context while other files are discovered through a tree/read interface. Memory and agent skills share commit/sync semantics; semantic indexing is optional rather than the only retrieval path. Dreaming performs background reflection. Memory workers use Git worktrees, while foreground/background subagents have their own process, context, model, and tool state. Plan/task tools are model-managed. Permission modes include unrestricted, standard, accept-edits, and strict; the CLI default at inspection was unrestricted. Local execution and optional isolated cloud computers are separate backends.

**Research interpretation (inference).** Letta treats durable identity/instruction memory as a filesystem and version-control problem rather than only vector retrieval. Git provides provenance and conflict mechanics, not factual correctness. Dreaming resembles an offline consolidation operator

\[
M_{t+1}=G(M_t,H_{1:t}),
\]

whose value must be tested against added cost, drift, and self-reinforcement—not assumed from analogy to human sleep.

**Limitations.** The default unrestricted local mode is a major experimental and security variable. Background agents and memory workers introduce asynchronous state races. Product/session analytics are not equivalent to scientific evaluation. Letta’s wider platform now documents a separate Evals system, but Letta Code trajectory export by itself is not a neutral scorer, and a first-party evaluator remains non-independent. Older Letta/MemGPT papers do not describe the current TypeScript-oriented repository directly. **Confidence: high** for current source mechanics; **medium** for memory benefit claims.

### 18. PocketFlow — The-Pocket

**Official sources:** [repository](https://github.com/The-Pocket/PocketFlow), [core source](https://github.com/The-Pocket/PocketFlow/blob/main/pocketflow/__init__.py), [documentation](https://the-pocket.github.io/PocketFlow/), [license](https://github.com/The-Pocket/PocketFlow/blob/main/LICENSE).

**Implementation evidence.** PocketFlow’s core is a very small scheduler. A node runs `prep→exec→post`; `post` returns an action label; a flow follows the corresponding transition in a plain loop. A shared dictionary holds state. Retry/fallback, nested flows, batch variants, async nodes, and `asyncio.gather` variants are provided. It has no required LLM client, tool schema, agent memory, planner, sandbox, tracer, or evaluator.

**Research interpretation (inference).** PocketFlow is a counterexample to ontological inflation: many “agent” architectures are cyclic labeled transition systems plus user-defined functions. Its small size makes topology easy to audit and places all intelligence and safety responsibility in application code.

**Limitations.** Cycles can be unbounded, parallel code can race on shared state, and durability/security/observability must be built separately. It should not be credited with features supplied only by examples or user code. **Confidence: high.**

## Cross-cutting mechanism analysis

### 1. Context construction is the central hidden policy

Most harnesses can be described by a context compiler

\[
C_t=P\;\Vert\;I\;\Vert\;R(q_t,M)\;\Vert\;\sigma(H_{\le t-k})\;\Vert\;H_{t-k+1:t},
\qquad \operatorname{tokens}(C_t)\le W,
\]

where \(P\) is the system/policy prompt, \(I\) durable instructions, \(R\) retrieval from memory or repository state, \(\sigma\) a summary/compaction operator, recent history is retained verbatim, and \(W\) is the model window after reserving output/tool margin.

The systems implement different parts:

- **Repository selection:** Aider’s ranked repo map; coding harness filesystem/search tools; Pydantic Harness explorer agents.
- **History transformation:** SWE-agent history processors, OpenHands condensers, goose context revision, Codex/Claude/Letta/Pydantic compaction.
- **Cross-session identity/instructions:** Claude `CLAUDE.md`/auto-memory, OpenHands Markdown memory, Letta MemFS, LangGraph Store.
- **Execution checkpoints rather than semantic memory:** LangGraph checkpoints, LlamaAgents durable state, CrewAI flow persistence, OpenHands event state, AutoGen save/load.

These are not interchangeable. A checkpoint answers “how can execution resume?”; retrieval memory answers “what past information should enter this prompt?”; durable instructions answer “what should remain stable across runs?”; raw history answers “what just happened?” Research should report them separately.

### 2. Planning is usually a mutable prompt artifact

Across the survey, “planning” can mean:

- a model-written task list or plan item (Codex, Letta, Pydantic Harness);
- an extra planning call inserted periodically or before execution (smolagents, CrewAI);
- a manager/selector deciding which agent acts (CrewAI, AutoGen, Semantic Kernel);
- explicit graph routing (LangGraph, LlamaAgents, PocketFlow);
- a separate architect model producing instructions for an editor (Aider).

Only the graph cases necessarily externalize a transition policy; none by default establishes optimal planning in the classical sense. A useful study should measure plan adherence, revision rate, invalid-dependency rate, and cost—not just whether a plan string existed.

### 3. Tool interfaces shape the action space

Three recurring action languages are:

1. **Shell/code:** expressive and token-efficient for composition, but difficult to authorize and contain.
2. **Structured function/tool calls:** schema-validatable and permission-friendly, but verbose and limited to predeclared operations.
3. **Typed events/messages:** well suited to replay and distributed scheduling, but require adapters before side effects occur.

MCP (OpenHands, Codex, Claude Code, goose and others) standardizes discovery and invocation transport; it does not standardize tool trust, semantic quality, latency, or reversibility. Pydantic validation and OpenHands typed events make syntax failures explicit. smolagents provides a particularly direct code-action versus structured-call comparison.

### 4. Concurrency is three different treatments

- **Tool concurrency:** several independent calls from one model turn (OpenHands, smolagents, Haystack).
- **Agent concurrency:** subagents with separate context and possibly separate workspaces (Codex, Claude Code, AG2, Letta, Pydantic Harness).
- **Graph concurrency:** dataflow branches or superstep nodes (LangGraph, LlamaAgents, Haystack pipelines, PocketFlow).

Speedup is bounded by serial work. If fraction \(p\) is parallelizable over \(n\) workers, Amdahl’s idealized bound is

\[
S(n)\le \frac{1}{(1-p)+p/n}.
\]

LLM harnesses add token duplication, coordination calls, rate limits, tool contention, merge conflicts, and correlated errors, so observed speedup can be lower or negative. Multiple independent attempts have ideal best-of-\(N\) success

\[
P(\text{at least one success})=1-(1-p)^N,
\]

but this is optimistic when attempts share prompts/models and their errors are correlated; a fallible discriminator further reduces realized selection accuracy.

### 5. Sandbox, permission, and workspace isolation are orthogonal

The survey exposes at least four independent controls:

- **OS/process containment:** Docker, VM, remote sandbox, restricted process namespace.
- **Filesystem scope:** read-only, workspace-write, mounted paths, worktrees.
- **Capability policy:** allow/deny/ask, tool allowlists, approval prompts.
- **language restriction:** AST or Python-subset interpreters.

An approval prompt does not contain a malicious process; a container does not decide whether a destructive but in-scope action is intended; an allowlist does not neutralize a powerful shell; and an AST filter is not necessarily a security boundary. Codex exposes both sandbox modes and approvals; Claude documents permissions and sandboxing separately; OpenHands separates local from Agent Server/container execution; smolagents explicitly distinguishes restricted interpretation from stronger remote isolation; CrewAI and Letta make backend/mode selection decisive. Papers should record the complete tuple rather than a binary “sandboxed” field.

### 6. Observability converges; evaluation does not

Event logs, trajectories, hooks, structured streams, and OpenTelemetry are now common. They allow reconstruction of costs, latency, tool errors, context transformations, and decision sequences. They do **not** establish task correctness. Evaluation mechanisms vary:

- coding benchmark runners (SWE-agent, mini-SWE-agent, OpenHands, Aider);
- general dataset/scorer frameworks (AG2, Pydantic Evals, Haystack evaluators);
- repeated LLM-scored tests (CrewAI);
- trace/telemetry surfaces with no neutral scorer (Codex, Claude Code, goose, Letta, LangGraph core, Semantic Kernel core).

The outcome of a benchmark run should be treated as

\[
Y=f(M,H,P,T,C,E,B,D),
\]

for model \(M\), harness implementation \(H\), prompt \(P\), tool set \(T\), context policy \(C\), execution environment \(E\), budget/stopping rule \(B\), and dataset/scorer \(D\). A leaderboard row that changes several coordinates does not identify the causal effect of \(H\).

### 7. Meaningful counterexamples

- **mini-SWE-agent** challenges the premise that orchestration layers are necessary for strong coding results.
- **PocketFlow** shows that an agent graph can reduce to a tiny cyclic scheduler with no built-in LLM concepts.
- **Aider** keeps the human in the loop and emphasizes retrieval, constrained edits, Git rollback, and test feedback.
- **LangGraph** externalizes control topology rather than asking the model to choose every transition.
- **Letta Code** makes durable identity/memory the organizing abstraction rather than treating memory as an optional vector store.
- **Claude Code** shows why public availability and a public GitHub repository are not synonyms for open source.
- **Codex CLI** shows why openness must be assessed layer by layer: inspectable Apache-2.0 client, proprietary hosted intelligence.

### 8. Optimizer profiles make the editable artifact the scientific unit

The optimizer sample changes what must be held fixed. AFlow, AgentSquare, ADAS, AutoFlow, and EvoAgentX can alter executable workflow or program structure; GPTSwarm, Archon, and AgentOpt alter a graph or allocation inside a constrained design space; ACE, GEPA, DSPy, and TextGrad alter persistent text-like state; Agent Lightning alters model weights; and EvoAgent's primary released path alters only transient per-instance roles and answers. Calling all of these “self-improvement” hides the treatment.

Every outer-loop experiment should report the tuple

\[
\mathcal O=(\mathcal X,Q_\phi,\mathcal E,\mathcal U,A_0,B,D_{\mathrm{train}},D_{\mathrm{val}},D_{\mathrm{test}}),
\]

where \(\mathcal X\) is the candidate representation, \(Q_\phi\) the proposal/update mechanism, \(\mathcal E\) the executor/evaluator, \(\mathcal U\) the acceptance/archive policy, \(A_0\) the initial state, and \(B\) the budget. Two systems that use the same label but edit different \(\mathcal X\), reuse validation data differently, or execute candidates under different containment are not instances of one controlled algorithm.

The recurring failure modes are correspondingly specific: arbitrary generated code without containment (ADAS, and potentially general GEPA/Flex use); incomplete or disconnected advertised mechanisms (GPTSwarm node retrieval, ACE operations, EvoAgentX reviewer); implementation defects that invalidate the nominal search (AgentSquare attribution and Archon ITAS); adaptive validation/test reuse (GEPA, DSPy defaults, AutoFlow); and metaphors broader than the optimized object (AFlow “MCTS,” TextGrad “gradient,” EvoAgent “evolution,” and Agent Lightning as harness optimization).

## Implications for a mathematics-oriented research program

The most tractable mathematical objects are mechanism-level, not vendor-level:

1. **Context allocation:** optimize selection/summarization under a token budget; study submodularity, redundancy, information loss, and recency bias.
2. **Stopping and budgets:** model the loop as an optimal-stopping or constrained Markov decision problem with cost, risk, and success utility.
3. **Routing:** compare model-chosen routing with explicit graph policies under equal calls/tokens.
4. **Error correction:** estimate when tool-error feedback increases eventual success versus causing costly loops.
5. **Parallel scheduling:** characterize commutativity, conflict probability, merge cost, and correlated failure across tools/agents/branches.
6. **Memory dynamics:** measure retention, retrieval precision, contradiction, drift, and consolidation stability over long horizons.
7. **Containment:** formalize reachable side effects under capability and filesystem policies, independently of task accuracy.
8. **Evaluation identification:** use factorial or matched designs that hold model, prompt, tools, environment, budget, and scorer fixed while ablating one harness mechanism.
9. **Outer-loop search:** quantify proposal quality, archive diversity, acceptance bias, adaptive overfitting, and multiple-comparison effects while holding the editable artifact and evaluation budget explicit.

A defensible paper should avoid treating a proprietary product’s undocumented internals as known, an implementation feature as an efficacy result, or a project-authored benchmark as independent validation.

## Reproducibility checklist

For every reported harness experiment, record:

- [ ] Exact repository URL, commit SHA, package versions, and local patches.
- [ ] Whether the inspected architecture is current, legacy, experimental, or superseded.
- [ ] For optimization studies, the exact editable artifact and serialization/hash of every seed, candidate, and selected incumbent.
- [ ] Proposal/update mechanism, proposer model and prompt, reflection/repair steps, candidate budget, and random seeds.
- [ ] Acceptance rule, archive/frontier policy, evaluator feedback exposed to the proposer, and train/validation/test reuse schedule.
- [ ] Code license and any separate model/service/data terms.
- [ ] Model provider, exact model identifier/snapshot, decoding parameters, and service date/region when relevant.
- [ ] Complete system/developer/task prompts and prompt templates.
- [ ] Tool schemas, MCP server names/versions, tool descriptions, and enabled/disabled tools.
- [ ] Action representation: shell/code, structured calls, patches, messages, or typed events.
- [ ] Context-window size, reserved output margin, truncation, compaction, summarization, and retrieval policy.
- [ ] Memory types separately: raw history, checkpoint state, retrieval store, and durable instructions/identity.
- [ ] Planning mechanism, planner model, invocation schedule, plan visibility, and plan-revision rule.
- [ ] Agent/team/graph topology, concurrency limits, scheduler, timeout, retry, and merge/conflict policy.
- [ ] Execution backend image/OS, dependency state, repository revision, network access, secrets, and working directory.
- [ ] Sandbox, filesystem scope, language restriction, approval mode, and capability allow/deny rules as separate fields.
- [ ] Step, wall-clock, token, API-cost, and tool-call budgets plus every stopping condition.
- [ ] Random seeds where effective, number of repetitions, failed/aborted runs, and rate-limit/backoff behavior.
- [ ] Full trajectories/events, tool stdout/stderr, context-compaction events, approvals, and resource usage.
- [ ] Dataset version, contamination controls, scorer version, tests, LLM-judge prompt/model, and human adjudication procedure.
- [ ] Whether evaluation was independent, project-authored, or performed by the same model family as the agent.
- [ ] Ablation matrix showing which single mechanism changed between conditions.
- [ ] Mean, uncertainty interval, paired effect size, cost-normalized result, and multiplicity correction where applicable.
- [ ] Safety incidents, unintended side effects, merge conflicts, recovery steps, and excluded trials.

## Stopping rule and remaining uncertainty

Runtime-harness saturation was reached when additional candidates mostly recombined the same state-machine, graph, actor, retrieval, compaction, delegation, sandbox, and tracing patterns. Optimizer/self-evolution saturation was reached separately when additional implementations mostly recombined the same editable-artifact classes, LM proposal/reflection loops, stochastic topology/allocation search, evaluator feedback, acceptance/archive policies, and weight-learning boundary cases. The 18-plus-14 split is therefore a **representative two-sample mechanism survey**, not a census. Fast-moving projects may have changed after 2026-09-04. The highest remaining uncertainty concerns proprietary service-side behavior (Claude Code and hosted Codex layers), deployment-specific defaults, young or rewritten architectures (AG2 v1, Pydantic Harness, current Letta Code, Agent Lightning v1, and post-release GEPA/EvoAgentX main), unsafe or incomplete optimizer paths, adaptive evaluator reuse, and whether project-provided results survive matched independent replication.
