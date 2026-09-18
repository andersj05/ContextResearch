---
title: "OpenHands: An Open Platform for AI Software Developers as Generalist Agents"
authors: ["Xingyao Wang", "Boxuan Li", "Yufan Song", "Frank F. Xu", "Xiangru Tang", "Mingchen Zhuge", "Jiayi Pan", "Yueqi Song", "Bowen Li", "Jaskirat Singh", "Hoang H. Tran", "Fuqiang Li", "Ren Ma", "Mingzhang Zheng", "Bill Qian", "Yanjun Shao", "Niklas Muennighoff", "Yizhe Zhang", "Binyuan Hui", "Junyang Lin", "Robert Brennan", "Hao Peng", "Heng Ji", "Graham Neubig"]
year: 2024
venue: "ICLR-2025"
source_type: "peer-reviewed"
paper_url: "https://arxiv.org/abs/2407.16741"
pdf_path: "papers/academic/wang-2024-openhands.pdf"
accessed: "2026-09-04"
review_status: "skimmed"
evidence_confidence: "medium"
---

# wang-2024-openhands — OpenHands: An Open Platform for AI Software Developers as Generalist Agents

## Why this source is in the corpus

Makes model–harness–environment coupling observable in executable, long-horizon tasks.

## Research question

What platform abstractions are needed to support generalist software-development agents?

## Harness mechanism studied

OpenHands defines an event stream connecting an agent controller to sandboxed code, shell, browser, and file operations, with delegation and evaluation infrastructure.

## Method and experimental setup

System paper describing the original OpenHands platform and agents, benchmark integrations, runtime abstractions, and qualitative design lessons.

## Main findings

- A shared event-based platform can run coding, browsing, and general assistance agents across multiple benchmarks.
- The paper is mainly infrastructure evidence; it does not isolate which platform component causes a score gain.

## Mathematical content

The event history is a state trajectory; reproducibility requires treating controller, action space, runtime, and stopping rule as a joint intervention.

## Evidence quality and limitations

Many experiments combine model, prompt, tools, and agent changes; benchmark-specific adapters differ; the current OpenHands SDK V1 is a substantial rewrite of the V0 architecture described here.

## Important implementation details

Identify paper-era V0 separately from current V1, pin repository commits and runtime images, export event trajectories, and separate platform support from agent-policy claims.

## Claims this source supports

Event sourcing and isolated execution are reusable harness primitives.

## Claims this source weakens or contradicts

Treating a platform paper or a modern repository name as evidence for a particular current implementation or causal gain.

## Relevance to a mathematics paper

Supports state-machine and event-log formalizations but contains no performance theorem.

## Connections to other sources

See the category and claim-level cross-references in [`INDEX.md`](INDEX.md) and the synthesis documents.

## Verification notes

Architecture figures, benchmark table, event/action abstractions, evaluation setup, and version scope checked in the local PDF. The archived file parsed successfully: 38 pages, 104815 extractable characters, SHA-256 `5d802255c4a58104a06147ba736fee09569faf3c26f251e5e9b7eff5d7662c14`.
