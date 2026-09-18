---
title: "Large Language Models as Tool Makers"
authors: ["Tianle Cai", "Xuezhi Wang", "Tengyu Ma", "Xinyun Chen", "Denny Zhou"]
year: 2023
venue: "ICLR-2024"
source_type: "peer-reviewed"
paper_url: "https://arxiv.org/abs/2305.17126"
pdf_path: "papers/academic/cai-2023-latm.pdf"
accessed: "2026-09-04"
review_status: "skimmed"
evidence_confidence: "high"
---

# cai-2023-latm — Large Language Models as Tool Makers

## Why this source is in the corpus

Directly studies reusable harness components, outer-loop optimization, self-modification, or the statistical controls needed to decide whether an update is a real improvement.

## Research question

Can a strong LM create reusable tools that let a weaker LM solve structured tasks more accurately and cheaply?

## Harness mechanism studied

An offline tool maker turns demonstrations into executable Python utilities, validates and wraps them, while a separate tool user retrieves and calls the cached utilities.

## Method and experimental setup

The authors pair GPT-4 as tool maker with GPT-3.5 as tool user on six algorithmic tasks, compare chain-of-thought and tool-use baselines, test tool generation success, and analyze amortized cost.

## Main findings

- Source-reported Table 2 shows GPT-3.5 chain-of-thought scores of 66.4/61.6/20.4/59.2/0/18.9 versus LATM 79.7/99.6/92.2/98.3/100/100 across the six tasks; GPT-4 chain-of-thought is 88.8/100/63.6/90.9/0/55.6 versus LATM 86.6/100/87.5/99.1/100/100.
- GPT-4 successfully generated tools on only 3/5 and 4/5 harder tool-making cases where GPT-3.5 produced 0/5, so the result supports asymmetric model roles rather than autonomous universal tool creation.

## Mathematical content

The paper derives an amortization condition comparing one-time maker cost C with per-query savings c, so reuse is favorable after more than roughly C/c queries; the search itself has no correctness guarantee.

## Evidence quality and limitations

Only six structured, code-solvable tasks are studied; validation uses a few demonstrations; executable generated code creates safety risk; the stronger maker model, caching, and tool affordance are major confounds.

## Important implementation details

Generate Python functions from demonstrations, run validation examples, repair and package successful code, expose it through a dispatcher, and let the weaker user call cached tools on later inputs.

## Claims this source supports

Persistent executable tools can shift capability across model tiers and amortize an expensive optimizer over repeated deployment.

## Claims this source weakens or contradicts

The evidence does not show that the task agent can safely or reliably invent its own tools without a stronger external maker and validators.

## Relevance to a mathematics paper

Offers an explicit break-even inequality for optimization cost versus repeated-use savings and separates tool-construction from tool-invocation error probabilities.

## Connections to other sources

See the category and claim-level cross-references in [`INDEX.md`](INDEX.md) and the synthesis documents.

## Verification notes

Local PDF method, cost analysis, Tables 2 and tool-generation results, dispatcher study, and limitations were checked; no code or benchmark rerun was performed. The archived file parsed successfully: 23 pages, 59314 extractable characters, SHA-256 `b943eec75e8a02e2c1003e87cb8508717820950a422508ce1d067195fb0edd10`.
