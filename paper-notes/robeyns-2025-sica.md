---
title: "A Self-Improving Coding Agent"
authors: ["Maxime Robeyns", "Martin Szummer", "Laurence Aitchison"]
year: 2025
venue: "preprint"
source_type: "preprint"
paper_url: "https://arxiv.org/abs/2504.15228"
pdf_path: "papers/academic/robeyns-2025-sica.pdf"
accessed: "2026-09-04"
review_status: "skimmed"
evidence_confidence: "medium"
---

# robeyns-2025-sica — A Self-Improving Coding Agent

## Why this source is in the corpus

Directly studies reusable harness components, outer-loop optimization, self-modification, or the statistical controls needed to decide whether an update is a real improvement.

## Research question

Can a coding agent improve its own source code through an open-ended archive-based search?

## Harness mechanism studied

A fixed LM proposes mutations to an executable coding-agent scaffold, an evaluator measures SWE-bench performance and efficiency, and an archive preserves diverse high performers.

## Method and experimental setup

SICA repeatedly edits its own agent implementation, runs candidates in sandboxed SWE-bench environments under time limits, selects by measured utility, and separately probes reasoning-task transfer.

## Main findings

- The reported SWE-bench random subset score rises from 17% to 53% over fifteen iterations at about $7,000 search cost.
- Reasoning transfer is weak: the evolved agent averages about 76 on AIME/GPQA-style probes while an o3-mini baseline reaches roughly 87/79 in reported cells, and path dependence plus five-minute timeouts make the initial 17% an unstable denominator.

## Mathematical content

Candidate source programs are optimized against an empirical utility combining task success and efficiency; the archive is a stochastic search heuristic, not a proof of monotone self-improvement.

## Evidence quality and limitations

A small random SWE subset is reused during search, the search is expensive, the base is depressed by strict timeouts, different trajectories yield different agents, and gains largely reflect faster file navigation/editing rather than general reasoning.

## Important implementation details

Expose the agent’s Python scaffold to a mutation model, sandbox each revision, run a fixed SWE task sample, archive viable candidates with scores and lineage, and iterate from selected parents.

## Claims this source supports

Executable harness source can accumulate useful engineering adaptations under an external task evaluator.

## Claims this source weakens or contradicts

The study contradicts broad capability-growth narratives: improvement is domain-specific, costly, path-dependent, and does not transfer cleanly to reasoning.

## Relevance to a mathematics paper

Supports modeling self-editing as noisy expensive black-box optimization with lineage, resource constraints, and a domain-transfer matrix.

## Connections to other sources

See the category and claim-level cross-references in [`INDEX.md`](INDEX.md) and the synthesis documents.

## Verification notes

Local PDF methods, search lineage, SWE result plots, cost discussion, reasoning-transfer study, timeout details, and limitations were checked; scores were not reproduced. The archived file parsed successfully: 18 pages, 63292 extractable characters, SHA-256 `97781b82ed43a330f491a35f772360bc3a9e7b47c5817e8889a0e1fec1115a15`.
