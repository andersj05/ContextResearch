---
title: "Identifying the Risks of LM Agents with an LM-Emulated Sandbox"
authors: ["Yangjun Ruan", "Honghua Dong", "Andrew Wang", "Silviu Pitis", "Yongchao Zhou", "Jimmy Ba", "Yann Dubois", "Chris J. Maddison", "Tatsunori Hashimoto"]
year: 2023
venue: "ICLR-2024"
source_type: "peer-reviewed"
paper_url: "https://arxiv.org/abs/2309.15817"
pdf_path: "papers/academic/ruan-2023-toolemu.pdf"
accessed: "2026-09-04"
review_status: "fully-reviewed"
evidence_confidence: "high"
---

# ruan-2023-toolemu — Identifying the Risks of LM Agents with an LM-Emulated Sandbox

## Why this source is in the corpus

Defines adversarial failure modes and control layers for tools, permissions, and execution boundaries.

## Research question

Can agent risks be discovered at scale without executing dangerous real tools?

## Harness mechanism studied

ToolEmu uses an LLM to emulate tool state transitions, an adversarial emulator to generate risky situations, and an LLM evaluator to label trajectory risk.

## Method and experimental setup

ICLR 2024 framework with 36 high-stakes toolkits, 144 cases, agent comparisons, and human validation of the emulator and safety evaluator.

## Main findings

- Human review judges 68.8% of ToolEmu-identified failures as valid potential real-world failures; even the safest tested agent is flagged in 23.9% of cases.
- Emulation expands coverage but introduces a second model whose errors can create or hide risk.

## Mathematical content

Observed risk is a noisy measurement of latent real-world failure; estimates require emulator sensitivity and specificity and should propagate evaluator uncertainty.

## Evidence quality and limitations

The emulator is not an actual sandbox or proof of exploitability; cases are curated; evaluator and agent can share model biases; tail-risk frequencies are not deployment prevalence.

## Important implementation details

Use emulation for triage, then replay high-severity cases in deterministic isolated tools with human adjudication; version emulator, evaluator, prompts, and scenario generator.

## Claims this source supports

Simulation can cheaply search a large safety space when followed by real validation.

## Claims this source weakens or contradicts

Calling an LLM-emulated tool environment a security containment boundary or interpreting flagged rate as real-world incidence.

## Relevance to a mathematics paper

Directly motivates two-stage noisy-oracle and rare-event evaluation models.

## Connections to other sources

See the category and claim-level cross-references in [`INDEX.md`](INDEX.md) and the synthesis documents.

## Verification notes

Abstract and pages 1-2 checked for architecture, 36 toolkits, 144 cases, 68.8%, 23.9%, human validation, and limitations. The archived file parsed successfully: 70 pages, 301439 extractable characters, SHA-256 `2d746c512086bd47084e616a0848c6dd25052dfe8b6da64e42e4c5e2f0050722`.
