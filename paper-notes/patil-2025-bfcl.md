---
title: "The Berkeley Function Calling Leaderboard BFCL: From Tool Use to Agentic Evaluation of Large Language Models"
authors: ["Shishir G. Patil", "Huanzhi Mao", "Fanjia Yan", "Charlie Cheng-Jie Ji", "Vishnu Suresh", "Ion Stoica", "Joseph E. Gonzalez"]
year: 2025
venue: "ICML-2025"
source_type: "peer-reviewed"
paper_url: "https://proceedings.mlr.press/v267/patil25a.html"
pdf_path: "papers/academic/patil-2025-bfcl.pdf"
accessed: "2026-09-04"
review_status: "skimmed"
evidence_confidence: "high"
---

# patil-2025-bfcl — The Berkeley Function Calling Leaderboard BFCL: From Tool Use to Agentic Evaluation of Large Language Models

## Why this source is in the corpus

Models the action interface through which a harness turns language outputs into state-changing operations.

## Research question

How should function calling be evaluated across serial, parallel, stateful, and irrelevant-tool settings?

## Harness mechanism studied

AST-based call matching, executable multi-turn environments, tool-selection tests, and contamination-resistant updates.

## Method and experimental setup

A large benchmark suite spans multiple languages and call patterns and evolves from single calls toward agentic multi-turn evaluation.

## Main findings

- AST evaluation is more scalable and semantically appropriate than raw string equality for structured calls.
- Multi-turn and stateful categories reveal failures hidden by simple one-call tests.

## Mathematical content

Function-call evaluation is structured equivalence over names, arguments, order, and state transitions; aggregate scores remain weighted benchmark choices.

## Evidence quality and limitations

Project-maintained leaderboard, test-set exposure risk, changing versions, and AST equivalence can miss semantic side effects.

## Important implementation details

Version the benchmark, publish category scores, execute stateful calls in isolated environments, and include irrelevant-tool abstention.

## Claims this source supports

Tool-use capability is multidimensional and harness-sensitive.

## Claims this source weakens or contradicts

A single BFCL total as a timeless or model-only property.

## Relevance to a mathematics paper

Provides a compositional scoring problem for call sequences and state changes.

## Connections to other sources

See the category and claim-level cross-references in [`INDEX.md`](INDEX.md) and the synthesis documents.

## Verification notes

Abstract, benchmark evolution, AST grader, serial and parallel categories, multi-turn setup, and limitations checked in the local PDF. The archived file parsed successfully: 22 pages, 86534 extractable characters, SHA-256 `5248f4770823b2a73fd52e3b12339d94121ff1b359c45163c5a47168edab7a2f`.
