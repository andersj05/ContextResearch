---
title: "Tau-bench: A Benchmark for Tool-Agent-User Interaction in Real-World Domains"
authors: ["Shunyu Yao", "Noah Shinn", "Pedram Razavi", "Karthik Narasimhan"]
year: 2024
venue: "preprint"
source_type: "preprint"
paper_url: "https://arxiv.org/abs/2406.12045"
pdf_path: "papers/academic/yao-2024-tau-bench.pdf"
accessed: "2026-09-04"
review_status: "fully-reviewed"
evidence_confidence: "high"
---

# yao-2024-tau-bench — Tau-bench: A Benchmark for Tool-Agent-User Interaction in Real-World Domains

## Why this source is in the corpus

Makes model–harness–environment coupling observable in executable, long-horizon tasks.

## Research question

How reliably can tool agents interact with users while following domain policies?

## Harness mechanism studied

Tau-bench couples a tool-using agent to a simulated user, policy document, stateful database, and end-state evaluator in retail and airline domains.

## Method and experimental setup

ICLR 2025 benchmark with 115 retail and 50 airline tasks, repeated trials, policy adherence, action and response scoring, and a consistency metric.

## Main findings

- Paper-era state-of-the-art agents succeed on fewer than half the tasks, and retail pass to the eighth power is below 25%.
- A high single-run score can coexist with poor repeated reliability.

## Mathematical content

The paper estimates pass superscript k by the unbiased all-k-successes statistic C(c,k)/C(n,k), contrasted with pass at k, 1-C(n-c,k)/C(n,k), for c successes among n sampled trials.

## Evidence quality and limitations

Users are simulated, only two domains are included, end-state checks can miss policy violations, attempts are exchangeable only conditionally, and current agents differ.

## Important implementation details

Publish policy and database versions, user simulator prompt, seeds, complete traces, action/output graders, and both success and repeated-reliability curves.

## Claims this source supports

Consistency across repeated stochastic trials is a distinct deployment property.

## Claims this source weakens or contradicts

Equating best-of-k success with reliability or reporting only a lucky trajectory.

## Relevance to a mathematics paper

Central source for finite-sample pass-at-k and pass-to-k estimators.

## Connections to other sources

See the category and claim-level cross-references in [`INDEX.md`](INDEX.md) and the synthesis documents.

## Verification notes

Abstract and metric section checked for domain sizes, state evaluator, under-50% and pass^8 claims, formulas, assumptions, and limitations. The archived file parsed successfully: 50 pages, 129807 extractable characters, SHA-256 `0ce66a1763d698c61bb311c3c874bf593d1e9a5bfff11bb35f6f72b981f6da56`.
