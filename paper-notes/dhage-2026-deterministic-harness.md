---
title: "Harness Engineering for Predictable Agentic Systems: An Empirical Study of Deterministic Execution Constraints"
authors: ["Saransh Dhage"]
year: 2026
venue: "preprint"
source_type: "preprint"
paper_url: "https://arxiv.org/abs/2608.26197"
pdf_path: "papers/academic/dhage-2026-deterministic-harness.pdf"
accessed: "2026-09-04"
review_status: "fully-reviewed"
evidence_confidence: "medium"
---

# dhage-2026-deterministic-harness — Harness Engineering for Predictable Agentic Systems: An Empirical Study of Deterministic Execution Constraints

## Why this source is in the corpus

Directly treats the harness, its optimization, or its runtime semantics as the object of study.

## Research question

Do deterministic control constraints reduce run-to-run agent variance without destroying task success?

## Harness mechanism studied

Finite-state execution, forced one-tool selection, validation, bounded retry, and an added structured-planning stage.

## Method and experimental setup

Two synthetic regulated-domain tasks, two open models, 100 runs per model-task-condition cell, bootstrap intervals and significance tests.

## Main findings

- The first-pass harness helped reproducibility in one of four cells, harmed two, and had no significant effect in one.
- Adding structured planning yielded reproducibility and determinism indices of 1.000 in all four cells and 100% task success in three, while latency effects reversed by model.

## Mathematical content

Defines reproducibility rate and a determinism index over action structure; uses bootstrap confidence intervals and cell-level hypothesis tests.

## Evidence quality and limitations

Only two synthetic tasks and two models; exact-match reproducibility may reward rigid but wrong behavior; authors iterated after seeing first-stage failures.

## Important implementation details

Validate a structured plan before any tool call, constrain transitions, and separately measure token cost, latency, reproducibility, and correctness.

## Claims this source supports

Harness constraints can remove execution variance, but only after diagnosing model-specific failure modes.

## Claims this source weakens or contradicts

Determinism as automatically beneficial or cost-free.

## Relevance to a mathematics paper

Offers measurable stochastic-process outputs and a caution against pooling heterogeneous cells.

## Connections to other sources

See the category and claim-level cross-references in [`INDEX.md`](INDEX.md) and the synthesis documents.

## Verification notes

Abstract, Tables 1-3, sample sizes, bootstrap protocol, latency analysis, and conclusion checked in the local PDF. The archived file parsed successfully: 9 pages, 28314 extractable characters, SHA-256 `3bafe1cbdb0469a02a736405adf2664825a807edec6fbf13056596d9cd70a595`.
