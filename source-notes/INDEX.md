# Non-academic and implementation source notes

This index covers official implementation evidence and practitioner engineering reports. Mechanism descriptions are kept distinct from controlled evidence of effects.

- Official implementation notes: **32**
- Practitioner source notes: **16**
- Research cutoff: **2026-09-04**

## Official implementations

| Source ID | Project / organization | Snapshot note |
|---|---|---|
| [`harness-ag2`](harness-ag2.md) | AG2 v1 / AG2AI | Apache-2.0; snapshot: v1.0.3; commit d4df5694e53d0533d583a7865023fa2e4e53b674 |
| [`harness-aider`](harness-aider.md) | Aider / Aider-AI | Apache-2.0; snapshot: v0.86.0; main commit 5dc9490bb35f9729ef2c95d00a19ccd30c26339c |
| [`harness-autogen`](harness-autogen.md) | AutoGen / Microsoft | MIT code; CC-BY-4.0 documentation; snapshot: python-v0.7.5; commit 027ecf0a379bcc1d09956d46d12d44a3ad9cee14 |
| [`harness-claude-code`](harness-claude-code.md) | Claude Code / Anthropic | Proprietary; public repository is all rights reserved; snapshot: v2.1.260; commit b3f0e501b79fe5cfc8c10d18cf3b0b6715c5c2fb |
| [`harness-codex-cli`](harness-codex-cli.md) | Codex CLI / OpenAI | Apache-2.0 for repository code; hosted models and services are proprietary; snapshot: rust-v0.153.2; commit de7874067fe8cb8f4846dd4d8b848965ce79070f |
| [`harness-crewai`](harness-crewai.md) | CrewAI / CrewAI | MIT core; snapshot: 1.15.20; commit c00e3228fc0036e6d262592b5943979659fcfdac |
| [`harness-goose`](harness-goose.md) | goose / Agentic AI Foundation | Apache-2.0; snapshot: v1.49.0; commit dce69009546ce5f20522d010fa3f1d57abbe2c3f |
| [`harness-haystack`](harness-haystack.md) | Haystack / deepset | Apache-2.0; snapshot: v3.1.1; commit 82da3adc2fac4675b80ff5573b790ec07113697b |
| [`harness-langgraph`](harness-langgraph.md) | LangGraph / LangChain | MIT core; snapshot: monorepo sdk==0.4.4; commit 81bf17b23123e4ef8b9d5f49fa09a0122fc2edd1 |
| [`harness-letta-code`](harness-letta-code.md) | Letta Code / Letta | Apache-2.0; snapshot: v0.31.12; commit 047fa6a99d9e83529b3c3e91cd8e3a7835a0f9c2 |
| [`harness-llamaagents`](harness-llamaagents.md) | LlamaAgents / Workflows / LlamaIndex | MIT; snapshot: llama-agents-server@v0.7.1; commit 9bfd8f8ea5d66652d5b6ce933df9cba118f6f863 |
| [`harness-mini-swe-agent`](harness-mini-swe-agent.md) | mini-SWE-agent / SWE-agent | MIT; snapshot: v2.4.6; main commit 04d809ceab9df28f9adaed044884180159172930 |
| [`harness-openhands`](harness-openhands.md) | OpenHands Software Agent SDK / OpenHands | MIT; snapshot: SDK v1.44.1; commit f47083cc370a85160f0348f32e531ee3514399e5 |
| [`harness-pocketflow`](harness-pocketflow.md) | PocketFlow / The-Pocket | MIT; snapshot: main commit f74d023f93607b8c3268133339a5e532a949898c |
| [`harness-pydantic-ai`](harness-pydantic-ai.md) | Pydantic AI and Pydantic AI Harness / Pydantic | MIT for both repositories; snapshot: core v2.39.0 / 7d85a07ec8e90f0741e8bd488ce1c4d0898f4618; Harness v0.29.0 / ec4b8615ac820bd5b93f19c00c52db29682a6e96 |
| [`harness-semantic-kernel`](harness-semantic-kernel.md) | Semantic Kernel / Microsoft | MIT; snapshot: dotnet-1.80.1; commit f8c5ba7aec210c986086a997fc4eef65190666eb |
| [`harness-smolagents`](harness-smolagents.md) | smolagents / Hugging Face | Apache-2.0; snapshot: v1.26.0; commit 30bb1161095dbae2271e6bc3cc4c219cc3897a57 |
| [`harness-swe-agent`](harness-swe-agent.md) | SWE-agent / SWE-agent | MIT; snapshot: v1.1.0; main commit 3ea751c087f32b16e039a2233dd6eefecef325d5 |
| [`selfopt-ace`](selfopt-ace.md) | Agentic Context Engineering (ACE) / ace-agent | Apache-2.0; snapshot: main commit 82709de050e1db6e6ef2f07bcb0393560b94992a (2026-08-24); no GitHub releases |
| [`selfopt-adas`](selfopt-adas.md) | Automated Design of Agentic Systems (ADAS): Meta Agent Search / Shengran Hu, Cong Lu, and Jeff Clune | Apache-2.0; snapshot: main commit 2702bee8fefda42255efc5be9f60e3bd3db96ae4 (2025-01-28); no GitHub releases |
| [`selfopt-aflow`](selfopt-aflow.md) | AFlow: Automating Agentic Workflow Generation / FoundationAgents | MIT; snapshot: main commit 3f457218fc716093fe53f6df8a5d5e6379d66346 (2025-12-25); no GitHub releases |
| [`selfopt-agent-lightning`](selfopt-agent-lightning.md) | Agent Lightning v1.0 / Microsoft | MIT; v1.0 is a complete redesign and pre-v1 behavior lives on the v0.x branch; snapshot: v1.0.1 (2026-08-24); main commit 218f1f7c0bac0800de4d5a4e5e6f61cf7b5038b4 (2026-09-02) |
| [`selfopt-agentopt`](selfopt-agentopt.md) | AgentOpt / AgentOptimizer | Apache-2.0; snapshot: v0.1.0 (2026-03-23); main commit 08b2d2c7fe370c884d956afbe540a09abc163c27 (2026-07-18) |
| [`selfopt-agentsquare`](selfopt-agentsquare.md) | AgentSquare: Automatic LLM Agent Search in Modular Design Space / Tsinghua FIB Lab | No root license detected; public source is not legally open-source by default; snapshot: main commit 8f5b3fe5d8a32f9b59d20370823bef2a2c86928c (2025-11-04); no GitHub releases |
| [`selfopt-archon`](selfopt-archon.md) | Archon: Inference-Time Architecture Search / Scaling Intelligence | Apache-2.0; snapshot: main commit 07114d77af283b6e8185a49ebf22216fdbbf2a55 (2025-03-07); no GitHub releases |
| [`selfopt-autoflow`](selfopt-autoflow.md) | AutoFlow: Automated Workflow Generation for Large Language Model Agents / AGI Research / Zelong Li et al. | Apache-2.0; snapshot: main commit 47203078a17e6612c79fe190d437ea58ae8c4d51 (2024-09-11); no GitHub releases |
| [`selfopt-dspy`](selfopt-dspy.md) | DSPy Optimizers: MIPROv2 and GEPA/Flex / Stanford NLP | MIT; dspy.GEPA delegates its core search engine to the separately MIT-licensed gepa package; snapshot: 3.3.1 (2026-08-21); main commit 35ef21f1689576c4fbe06c27e22eabb5db1b24b6 (2026-09-04) |
| [`selfopt-evoagent`](selfopt-evoagent.md) | EvoAgent: Towards Automatic Multi-Agent Generation via Evolutionary Algorithms / Siyu Yuan et al. | No root license detected; a nested TravelPlanner license does not license the repository as a whole; snapshot: main commit fc6d087b119df69466c2372cfcaf588c040aaba8 (2024-10-19); no GitHub releases |
| [`selfopt-evoagentx`](selfopt-evoagentx.md) | EvoAgentX / ANative Lab | Root LICENSE begins MIT; GitHub metadata reports NOASSERTION because the file also contains third-party notices; snapshot: v0.1.4 (2026-06-28); main commit d77fd6b9a3e76c8dd83bebe3374c53a3f5d16f54 (2026-08-27) |
| [`selfopt-gepa`](selfopt-gepa.md) | GEPA: Genetic-Pareto Reflective Optimization / gepa-ai | MIT; optional meta-harness depends on proprietary Claude Code as proposer; snapshot: v0.1.4 (2026-07-15); main commit 0632cdb5dcc052e690eab439e1b4a7e3e9cfe407 (2026-09-01) |
| [`selfopt-gptswarm`](selfopt-gptswarm.md) | GPTSwarm / metauto-ai | MIT; snapshot: main commit c23a827f561c934ce21dd950408f7606aa4a8821 (2026-02-05); no GitHub releases |
| [`selfopt-textgrad`](selfopt-textgrad.md) | TextGrad: Automatic Differentiation via Text / Zou Group | MIT; snapshot: v0.1.6 (2024-12-15); main commit 75e912e210864b61999781778cdf756d4468120f (2025-07-25) |

## Practitioner and engineering reports

| Source ID | Source | Evidence class |
|---|---|---|
| [`anthropic-2024-building-effective-agents`](anthropic-2024-building-effective-agents.md) | Building Effective Agents / Anthropic | engineering-blog |
| [`anthropic-2025-context-engineering`](anthropic-2025-context-engineering.md) | Effective Context Engineering for AI Agents / Anthropic | engineering-blog |
| [`anthropic-2025-long-running-agents`](anthropic-2025-long-running-agents.md) | Effective Harnesses for Long-Running Agents / Anthropic | engineering-blog |
| [`anthropic-2025-multi-agent-research`](anthropic-2025-multi-agent-research.md) | How We Built Our Multi-Agent Research System / Anthropic | engineering-blog |
| [`anthropic-2026-agent-evals`](anthropic-2026-agent-evals.md) | Demystifying Evals for AI Agents / Anthropic | engineering-blog |
| [`anthropic-2026-harness-design`](anthropic-2026-harness-design.md) | Harness Design for Long-Running Application Development / Prithvi Rajasekaran / Anthropic | engineering-blog |
| [`anthropic-2026-infrastructure-noise`](anthropic-2026-infrastructure-noise.md) | Quantifying Infrastructure Noise in Agentic Coding Evals / Anthropic | engineering-blog |
| [`anthropic-2026-managed-agents`](anthropic-2026-managed-agents.md) | Scaling Managed Agents: Decoupling the Brain from the Hands / Anthropic | engineering-blog |
| [`cursor-2026-improving-harness`](cursor-2026-improving-harness.md) | Continually Improving Our Agent Harness / Stefan Heule and Jediah Katz / Cursor | engineering-blog |
| [`langchain-2026-better-harness`](langchain-2026-better-harness.md) | Better Harness: A Recipe for Harness Hill-Climbing with Evals / Vivek Trivedy / LangChain | engineering-blog |
| [`manus-2025-context-engineering`](manus-2025-context-engineering.md) | Context Engineering for AI Agents: Lessons from Building Manus / Yichao Ji / Manus | engineering-blog |
| [`openai-2024-swebench-verified`](openai-2024-swebench-verified.md) | Introducing SWE-bench Verified / OpenAI and SWE-bench contributors | practitioner-report |
| [`openai-2026-harness-engineering`](openai-2026-harness-engineering.md) | Harness Engineering: Leveraging Codex in an Agent-First World / Ryan Lopopolo / OpenAI | engineering-blog |
| [`openai-2026-swebench-pro-audit`](openai-2026-swebench-pro-audit.md) | Separating Signal from Noise in Coding Evaluations / OpenAI | practitioner-report |
| [`openai-2026-swebench-retirement`](openai-2026-swebench-retirement.md) | Why SWE-bench Verified No Longer Measures Frontier Coding Capabilities / OpenAI | practitioner-report |
| [`stencil-2026-harness-playbook`](stencil-2026-harness-playbook.md) | The Harness Playbook / Can Bölük / Stencil | engineering-blog |

The machine-readable inventory for these sources and the academic PDF corpus is [`catalog/sources.csv`](../catalog/sources.csv).
