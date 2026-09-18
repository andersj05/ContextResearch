---
title: "InjecAgent: Benchmarking Indirect Prompt Injections in Tool-Integrated Large Language Model Agents"
authors: ["Qiusi Zhan", "Zhixiang Liang", "Zifan Ying", "Daniel Kang"]
year: 2024
venue: "ACL-2024"
source_type: "peer-reviewed"
paper_url: "https://arxiv.org/abs/2403.02691"
pdf_path: "papers/academic/zhan-2024-injecagent.pdf"
accessed: "2026-09-04"
review_status: "fully-reviewed"
evidence_confidence: "high"
---

# zhan-2024-injecagent — InjecAgent: Benchmarking Indirect Prompt Injections in Tool-Integrated Large Language Model Agents

## Why this source is in the corpus

Defines adversarial failure modes and control layers for tools, permissions, and execution boundaries.

## Research question

How vulnerable are tool-integrated agents to indirect prompt injection across diverse user and attacker tools?

## Harness mechanism studied

InjecAgent inserts malicious instructions into tool-returned content, then measures whether the agent invokes an attacker-selected harmful or exfiltration tool.

## Method and experimental setup

ACL Findings 2024 benchmark of 1,054 cases spanning 17 user tools, 62 attacker tools, two attack-intent families, and 30 agent configurations.

## Main findings

- ReAct-prompted GPT-4 follows the injected attack in 24% of base cases; adding a hacking-style reinforcement prompt nearly doubles its attack success.
- Vulnerability depends on prompt, model, tool graph, and attack construction rather than one model-wide constant.

## Mathematical content

Attack success is a Bernoulli conditional on task, attacker goal, placement, model, and harness; uncertainty should be clustered by tool and template.

## Evidence quality and limitations

Cases are templated, success conditions can overapproximate harm, models are dated, defenses and adaptive attackers evolve, and the benchmark does not measure real-world frequency.

## Important implementation details

Report utility and attack success together, cluster splits by template and tool, apply capability scoping and external authorization, and test adaptive attacks on held-out scenarios.

## Claims this source supports

Indirect injection is a reproducible tool-harness failure mode at nontrivial rates.

## Claims this source weakens or contradicts

A universal vulnerability percentage or the belief that ReAct reasoning alone provides a defense.

## Relevance to a mathematics paper

Supports adversarial risk surfaces and hierarchical attack-success models.

## Connections to other sources

See the category and claim-level cross-references in [`INDEX.md`](INDEX.md) and the synthesis documents.

## Verification notes

Abstract and pages 1-2 checked for 1,054 cases, 17 and 62 tools, 30 agents, 24% result, reinforced attack, task construction, and limitations. The archived file parsed successfully: 36 pages, 113110 extractable characters, SHA-256 `49e6e6a4a00c797a772ef905a154c0839426655027d5fa0ce6b632e6c1db2bfb`.
