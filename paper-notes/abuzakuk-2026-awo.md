---
title: "Optimizing Agentic Workflows using Meta-tools"
authors: ["Sami Abuzakuk", "Anne-Marie Kermarrec", "Rishi Sharma", "Rasmus Moorits Veski", "Martijn de Vos"]
year: 2026
venue: "preprint"
source_type: "preprint"
paper_url: "https://arxiv.org/abs/2601.22037"
pdf_path: "papers/academic/abuzakuk-2026-awo.pdf"
accessed: "2026-09-04"
review_status: "skimmed"
evidence_confidence: "medium"
---

# abuzakuk-2026-awo — Optimizing Agentic Workflows using Meta-tools

## Why this source is in the corpus

Directly studies reusable harness components, outer-loop optimization, self-modification, or the statistical controls needed to decide whether an update is a real improvement.

## Research question

Can repeated tool-call subsequences be compiled into deterministic meta-tools that reduce agent cost without reducing success?

## Harness mechanism studied

Trace mining finds common tool-call paths and compresses qualifying subsequences into composite deterministic tools exposed to later agent runs.

## Method and experimental setup

AWO builds a prefix/tree representation from prior trajectories, applies coverage-based merging rules, creates meta-tools, and reruns GPT-5.1 and Claude-4.5 agents on VisualWebArena and AppWorld.

## Main findings

- The abstract reports up to 11.9% fewer LLM calls and up to +4.2 percentage points task success; Table 1 reports VisualWebArena cost $44.5→$42.0 for GPT and $272.3→$244.5 for Claude, and AppWorld $31.59→$26.85 and $29.63→$28.39.
- Some model/benchmark cells show increased calls or latency, and the mined trajectories come from the same application families, so the result is workload-specific optimization rather than open-ended invention.

## Mathematical content

A coverage threshold accepts a path compression when its represented trajectories exceed a rule such as 50%; efficiency is measured by differences/ratios in calls, tokens, latency, and cost, with no generalization bound for future workflow distributions.

## Evidence quality and limitations

2026 preprint; only two benchmarks; meta-tools depend on stable APIs and recurrent paths; offline mining/build cost and security of composite side effects are incomplete; gains vary by model and metric.

## Important implementation details

Log tool trajectories, merge common prefixes/subsequences under coverage constraints, generate deterministic composite functions, register them alongside atomic tools, and allow the agent to choose them on later runs.

## Claims this source supports

Harnesses can improve by compiling regular stochastic action loops into cheaper deterministic procedures.

## Claims this source weakens or contradicts

Optimization is not uniformly beneficial and cannot be assumed to transfer when task mix, model policy, or tool APIs change.

## Relevance to a mathematics paper

Offers a grammar/path-compression view of workflow optimization and explicit cost and success-rate estimands.

## Connections to other sources

See the category and claim-level cross-references in [`INDEX.md`](INDEX.md) and the synthesis documents.

## Verification notes

Local PDF abstract, tree-merging algorithm, Table 1, benchmark-level call/latency/success tables, and limitations were checked; values were not independently reproduced. The archived file parsed successfully: 17 pages, 64136 extractable characters, SHA-256 `97f856b6c45a66870a9323359f260d8df8b8f66785b0ae96837b8672ccd140ff`.
