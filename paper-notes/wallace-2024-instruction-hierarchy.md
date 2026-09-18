---
title: "The Instruction Hierarchy: Training LLMs to Prioritize Privileged Instructions"
authors: ["Eric Wallace", "Kai Xiao", "Reimar Leike", "Lilian Weng", "Johannes Heidecke", "Alex Beutel"]
year: 2024
venue: "preprint"
source_type: "preprint"
paper_url: "https://arxiv.org/abs/2404.13208"
pdf_path: "papers/academic/wallace-2024-instruction-hierarchy.pdf"
accessed: "2026-09-04"
review_status: "fully-reviewed"
evidence_confidence: "high"
---

# wallace-2024-instruction-hierarchy — The Instruction Hierarchy: Training LLMs to Prioritize Privileged Instructions

## Why this source is in the corpus

Defines adversarial failure modes and control layers for tools, permissions, and execution boundaries.

## Research question

Can models be trained to respect privilege levels among system, user, and tool-originated instructions?

## Harness mechanism studied

An instruction hierarchy orders message sources by privilege and trains on aligned and conflicting synthetic examples so lower-priority instructions are ignored when they conflict.

## Method and experimental setup

2024 OpenAI technical report fine-tuning GPT-3.5-class models and testing prompt injection, system-prompt extraction, jailbreak, and ordinary capability benchmarks.

## Main findings

- Hierarchical training greatly improves robustness, including a reported 63-point improvement on system-prompt extraction defense, with small average capability degradation.
- This is a model-training intervention that can reinforce but cannot replace harness-enforced authorization and isolation.

## Mathematical content

Privileges form a partial or total precedence order; a correct policy should satisfy noninterference of lower-priority conflicting instructions on protected actions, subject to explicitly permitted delegation.

## Evidence quality and limitations

Results use proprietary model variants and synthetic data; benchmark attacks are incomplete; unseen adaptive attacks remain; instruction-following robustness is probabilistic rather than a hard security boundary.

## Important implementation details

Preserve message provenance, define a machine-enforced privilege lattice for tools and data, train models to follow it, and still validate actions and contain execution outside the model.

## Claims this source supports

Separating trusted instructions from untrusted content is both a model and harness design principle.

## Claims this source weakens or contradicts

Treating learned instruction priority as proof of security against arbitrary prompt injection.

## Relevance to a mathematics paper

Provides order-theoretic and noninterference language for message privileges.

## Connections to other sources

See the category and claim-level cross-references in [`INDEX.md`](INDEX.md) and the synthesis documents.

## Verification notes

Abstract and pages 1-2 checked for hierarchy definition, training construction, 63-point example, generalization claim, capability tradeoff, and limitations. The archived file parsed successfully: 13 pages, 47024 extractable characters, SHA-256 `fbc2d65e913e75b8f0ae74e83e3443c36a727636d1038a071a2f10d8be63dac4`.
