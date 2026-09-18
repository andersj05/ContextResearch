---
title: "Natural-Language Agent Harnesses"
authors: ["Linyue Pan", "Lexiao Zou", "Shuo Guo", "Jingchen Ni", "Hai-Tao Zheng"]
year: 2026
venue: "preprint"
source_type: "preprint"
paper_url: "https://arxiv.org/abs/2603.25723"
pdf_path: "papers/academic/pan-2026-natural-language-harnesses.pdf"
accessed: "2026-09-04"
review_status: "skimmed"
evidence_confidence: "medium"
---

# pan-2026-natural-language-harnesses — Natural-Language Agent Harnesses

## Why this source is in the corpus

Directly treats the harness, its optimization, or its runtime semantics as the object of study.

## Research question

Can high-level harness control logic be externalized as a portable executable natural-language artifact?

## Harness mechanism studied

Natural-Language Agent Harness documents interpreted by a shared runtime into calls, handoffs, state updates, validation gates, and artifact contracts.

## Method and experimental setup

Coding, terminal, and computer-use evaluations compare natural-language, code, and prompted realizations and include module ablations and migration experiments.

## Main findings

- Natural-language harnesses achieve comparable reported task outcomes while exposing shorter static policies.
- Explicit modules make orchestration easier to inspect, transfer, and ablate.

## Mathematical content

Treats a policy document as an executable controller interpreted by a runtime; semantic equivalence to code is empirical, not formally proven.

## Evidence quality and limitations

Recent preprint; interpreter behavior remains code; natural-language ambiguity and evaluator coupling can hide non-equivalence.

## Important implementation details

Separate portable run policy from trusted runtime semantics and require explicit contracts for state and artifacts.

## Claims this source supports

Harness policy can be a versioned research artifact independent of one controller implementation.

## Claims this source weakens or contradicts

Natural-language portability as proof of deterministic or secure execution.

## Relevance to a mathematics paper

Raises questions about program semantics, refinement, and equivalence of textual controllers.

## Connections to other sources

See the category and claim-level cross-references in [`INDEX.md`](INDEX.md) and the synthesis documents.

## Verification notes

Abstract, representation, runtime contracts, comparison experiments, module ablations, and limitations checked in the local PDF. The archived file parsed successfully: 22 pages, 77147 extractable characters, SHA-256 `8de9eb2456a52487f3db5839e2cab6ae044017260d700183c99de9c14dcbf8dc`.
