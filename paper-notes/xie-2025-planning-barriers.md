---
title: "Revealing the Barriers of Language Agents in Planning"
authors: ["Jian Xie", "Kexun Zhang", "Jiangjie Chen", "Siyu Yuan", "Kai Zhang", "Yikai Zhang", "Lei Li", "Yanghua Xiao"]
year: 2025
venue: "NAACL-2025"
source_type: "peer-reviewed"
paper_url: "https://aclanthology.org/2025.naacl-long.93/"
pdf_path: "papers/academic/xie-2025-planning-barriers.pdf"
accessed: "2026-09-04"
review_status: "skimmed"
evidence_confidence: "high"
---

# xie-2025-planning-barriers — Revealing the Barriers of Language Agents in Planning

## Why this source is in the corpus

Makes model–harness–environment coupling observable in executable, long-horizon tasks.

## Research question

What limits language-agent planning even when stronger reasoning models and memory updates are used?

## Harness mechanism studied

The study applies feature attribution to task and generated-plan tokens and tests parametric and episodic memory updates intended to improve constraint use.

## Method and experimental setup

NAACL 2025 experiments on plan-generation benchmarks with direct prompting, memory-updating strategies, and model comparisons.

## Main findings

- OpenAI o1 obtains only 15.6% on one complex real-world planning benchmark.
- Limited influence of constraints and diminishing influence of the question are identified as barriers; proposed memory strategies mitigate but do not remove them.

## Mathematical content

Feature-attribution scores are diagnostic statistics, not causal effects; planning accuracy is a task proportion under exact or structured graders.

## Evidence quality and limitations

Attribution methods are model-dependent, benchmarks may privilege one plan representation, accuracy does not measure execution, and the model/harness landscape changes rapidly.

## Important implementation details

Evaluate plan validity through execution, perturb constraints directly, report attribution stability, and cross models and context policies under fixed budgets.

## Claims this source supports

Long-horizon planning failure can originate in context use rather than absence of a planning prompt.

## Claims this source weakens or contradicts

Planning labels and chain-of-thought length as proof of valid constraint-sensitive plans.

## Relevance to a mathematics paper

Motivates causal perturbation and position-sensitive context models.

## Connections to other sources

See the category and claim-level cross-references in [`INDEX.md`](INDEX.md) and the synthesis documents.

## Verification notes

Abstract and main experiments checked for 15.6% result, two attributed barriers, memory strategies, benchmark setup, and limitations. The archived file parsed successfully: 17 pages, 62490 extractable characters, SHA-256 `4320d496ebf3a01f41e61561d8e47f6b100773415e0c0ec3a4298ba9f4603c20`.
