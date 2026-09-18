---
title: "More Agents Is All You Need"
authors: ["Junyou Li", "Qin Zhang", "Yangbin Yu", "Qiang Fu", "Deheng Ye"]
year: 2024
venue: "TMLR-2024"
source_type: "peer-reviewed"
paper_url: "https://arxiv.org/abs/2402.05120"
pdf_path: "papers/academic/li-2024-more-agents.pdf"
accessed: "2026-09-04"
review_status: "fully-reviewed"
evidence_confidence: "high"
---

# li-2024-more-agents — More Agents Is All You Need

## Why this source is in the corpus

Provides communication, aggregation, or coordination mechanisms and their compute-matched counterevidence.

## Research question

Does independent sampling and voting improve as more nominal agents are instantiated?

## Harness mechanism studied

Agent Forest samples independent responses and selects by exact vote or pairwise output similarity.

## Method and experimental setup

Multiple benchmarks, models, ensemble sizes up to 40, and combinations with other methods test scaling and task difficulty.

## Main findings

- At 40 samples, Llama-2-13B rises from 0.35 to 0.59 on GSM8K and 0.14 to 0.18 on HumanEval; 15 samples makes 13B comparable to 70B on GSM8K.
- Token use grows linearly and adding debate can harm code.

## Mathematical content

For open output choose the response maximizing summed pairwise similarity; relative gain is normalized by single-sample performance.

## Evidence quality and limitations

The agents do not communicate, so this is ensembling rather than orchestration; correlated errors and similarity can select common wrong code.

## Important implementation details

Call it repeated sampling, report ensemble size and token cost, and compare with calibrated verification.

## Claims this source supports

Simple sampling-and-aggregation is a strong multi-agent baseline.

## Claims this source weakens or contradicts

More agents terminology as evidence of social or coordinated reasoning.

## Relevance to a mathematics paper

Provides an ensemble-scaling baseline and correlation questions.

## Connections to other sources

See the category and claim-level cross-references in [`INDEX.md`](INDEX.md) and the synthesis documents.

## Verification notes

Ensemble-size tables, similarity rule, token scaling, debate combination, and limitations checked in the local PDF. The archived file parsed successfully: 18 pages, 55512 extractable characters, SHA-256 `d948be6a6068835cffe9b6f8b799861e188eea3a0204a90eec70e5faae0cfe57`.
