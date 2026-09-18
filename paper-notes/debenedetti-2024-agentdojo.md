---
title: "AgentDojo: A Dynamic Environment to Evaluate Prompt Injection Attacks and Defenses for LLM Agents"
authors: ["Edoardo Debenedetti", "Jie Zhang", "Mislav Balunović", "Luca Beurer-Kellner", "Marc Fischer", "Florian Tramèr"]
year: 2024
venue: "NeurIPS-2024"
source_type: "peer-reviewed"
paper_url: "https://arxiv.org/abs/2406.13352"
pdf_path: "papers/academic/debenedetti-2024-agentdojo.pdf"
accessed: "2026-09-04"
review_status: "fully-reviewed"
evidence_confidence: "high"
---

# debenedetti-2024-agentdojo — AgentDojo: A Dynamic Environment to Evaluate Prompt Injection Attacks and Defenses for LLM Agents

## Why this source is in the corpus

Defines adversarial failure modes and control layers for tools, permissions, and execution boundaries.

## Research question

Can prompt-injection defenses be evaluated jointly for normal-task utility and adversarial security in stateful tools?

## Harness mechanism studied

AgentDojo defines deterministic tool environments, user goals, attacker goals, injection endpoints, adaptive attacks, defenses, and programmatic final-state checks.

## Method and experimental setup

NeurIPS 2024 datasets paper with 97 realistic tasks and 629 security cases across email, banking, travel, and related domains.

## Main findings

- Paper-era agents solve fewer than 66% of tasks even without attack; attacks against the best agents succeed in fewer than 25% of cases, and a detector defense reduces attack success to 8%.
- Defenses must be plotted against utility because blocking tools can appear secure by making the agent useless.

## Mathematical content

Security evaluation is bi-objective: maximize benign utility U while minimizing attack success A; dominated defenses should be excluded, and confidence is paired by scenario.

## Evidence quality and limitations

The initial environment covers a few domains, fixed attacks can be overfit, state checks can miss semantic harm, percentages depend on specific models and defenses, and adaptive threats evolve.

## Important implementation details

Maintain an extensible held-out attack set, use real state machines rather than LLM simulation where possible, publish both utility and security with traces, and independently authorize sensitive actions.

## Claims this source supports

Agent security is an end-to-end harness property with an explicit utility-security frontier.

## Claims this source weakens or contradicts

Reporting attack success without benign utility, or interpreting a detector as complete isolation.

## Relevance to a mathematics paper

Supports Pareto-frontier and adversarial-game formulations.

## Connections to other sources

See the category and claim-level cross-references in [`INDEX.md`](INDEX.md) and the synthesis documents.

## Verification notes

Abstract and pages 1-2 checked for 97 tasks, 629 cases, state checks, under-66% utility, under-25% attack success, 8% defense result, and limitations. The archived file parsed successfully: 26 pages, 77489 extractable characters, SHA-256 `349884fffbf43282591c5accffd57bb651632f38e412fe303114941bdd111b05`.
