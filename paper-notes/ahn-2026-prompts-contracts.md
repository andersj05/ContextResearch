---
title: "From Prompts to Contracts: Harness Engineering for Auditable Enterprise LLM Agents"
authors: ["Joongho Ahn", "Moonsoo Kim"]
year: 2026
venue: "preprint"
source_type: "preprint"
paper_url: "https://arxiv.org/abs/2607.08028"
pdf_path: "papers/academic/ahn-2026-prompts-contracts.pdf"
accessed: "2026-09-04"
review_status: "skimmed"
evidence_confidence: "medium"
---

# ahn-2026-prompts-contracts — From Prompts to Contracts: Harness Engineering for Auditable Enterprise LLM Agents

## Why this source is in the corpus

Directly treats the harness, its optimization, or its runtime semantics as the object of study.

## Research question

Can deterministic contracts around a replaceable LLM make enterprise agents auditable across models?

## Harness mechanism studied

Code-owned manifests, schemas, routing, source boundaries, output hygiene, and validation gates around a model composition boundary.

## Method and experimental setup

Public-data case over five Korean groups and 25 companies; three hosted models, 270 composition-boundary runs, fault injection, prompt-only and bolt-on guardrail ablations.

## Main findings

- Harness contracts held in all 270 composition-boundary runs and injected faults were detected.
- Prompt instructions alone leaked violations; an external guardrail blocked them but reduced utility to 88/120, whereas code-owned enforcement retained 120/120 in the reported ablation.

## Mathematical content

The contract layer is naturally expressed as predicates over inputs, traces, and outputs; the paper reports finite validation counts rather than probabilistic guarantees.

## Evidence quality and limitations

Author-built finance slice, fixed scenarios, hosted-model dependence, and new unreplicated preprint.

## Important implementation details

Move invariant behavior from prose prompts into executable predicates and preserve model substitution behind a narrow boundary.

## Claims this source supports

Deterministic harness checks can preserve selected safety and audit properties across model substitution.

## Claims this source weakens or contradicts

Prompt compliance as a dependable enforcement mechanism.

## Relevance to a mathematics paper

Supports formal specification of safety properties and empirical false-accept or false-reject rates.

## Connections to other sources

See the category and claim-level cross-references in [`INDEX.md`](INDEX.md) and the synthesis documents.

## Verification notes

Abstract, RQ setup, 270-run result, fault injection, guardrail ablation, and limitations checked in the local PDF. The archived file parsed successfully: 32 pages, 102527 extractable characters, SHA-256 `d90ad4ee4e445512e930a291fee7d10ec43c662e7a920eccafd6740cd6f8eb64`.
