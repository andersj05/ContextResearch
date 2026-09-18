---
title: "Agentic Context Engineering: Evolving Contexts for Self-Improving Language Models"
authors: ["Qizheng Zhang", "Changran Hu", "Shubhangi Upasani", "Boyuan Ma", "Fenglu Hong", "Vamsidhar Kamanuru", "Jay Rainton", "Chen Wu", "Mengmeng Ji", "Hanchen Li", "Urmish Thakker", "James Zou", "Kunle Olukotun"]
year: 2025
venue: "preprint"
source_type: "preprint"
paper_url: "https://arxiv.org/abs/2510.04618"
pdf_path: "papers/academic/zhang-2025-ace.pdf"
accessed: "2026-09-04"
review_status: "skimmed"
evidence_confidence: "high"
---

# zhang-2025-ace — Agentic Context Engineering: Evolving Contexts for Self-Improving Language Models

## Why this source is in the corpus

Directly studies reusable harness components, outer-loop optimization, self-modification, or the statistical controls needed to decide whether an update is a real improvement.

## Research question

Can an agent improve persistent system prompts or memory without iterative context collapse?

## Harness mechanism studied

Generation extracts candidate lessons, reflection evaluates evidence, and curation applies incremental structured updates to a growing playbook rather than rewriting the whole context.

## Method and experimental setup

ACE optimizes context offline as a system prompt and online as agent memory, using labeled scores or natural execution feedback; it compares base, in-context learning, GEPA, dynamic-cheatsheet-style methods, and ACE on agents and domain tasks.

## Main findings

- The abstract reports average gains of +10.6% on agents and +8.6% on finance; Figure 1 shows AppWorld 42.4 base, 46.0 ICL, 46.4 GEPA, 51.9 DC, 59.5 ACE, FiNER 70.7→78.3, and Formula 67.5→76.5.
- A context-collapse case compresses 18,282 tokens to 122 and falls to 57.1 versus 63.7 without context, but this is an illustrative case and not a theorem that all monolithic rewriting collapses.

## Mathematical content

Context is updated by structured set-like add/refine operations under an empirical objective rather than full replacement; no regret, stability, or memory-capacity bound is proved.

## Evidence quality and limitations

ICLR 2026 results combine datasets, metrics, models, and offline/online regimes; AppWorld comparisons include different production systems; growing playbooks consume context; natural feedback can encode evaluator bias.

## Important implementation details

Maintain typed playbook entries with provenance and status, generate lessons from trajectories, reflect against evidence, incrementally add/refine rather than overwrite, retrieve the relevant playbook at execution, and persist approved updates.

## Claims this source supports

Persistent context engineering can outperform concise prompt rewriting and can learn from environment feedback without weight updates.

## Claims this source weakens or contradicts

The evidence weakens brevity-as-default: shorter optimized prompts may omit useful detail; it does not prove unbounded context accumulation or universal superiority over GEPA.

## Relevance to a mathematics paper

Creates a natural information-retention versus token-cost problem and motivates stability metrics for incremental versus replacement updates.

## Connections to other sources

See the category and claim-level cross-references in [`INDEX.md`](INDEX.md) and the synthesis documents.

## Verification notes

Local PDF abstract, Figure 1, context-collapse Figure 2, algorithm, main tables, cost/latency analyses, and limitations were checked; reported effects were not replicated. The archived file parsed successfully: 32 pages, 111355 extractable characters, SHA-256 `51050ced82df75c143b151262d5af8763916968ca50374bd8ff778f40552b0ad`.
