---
title: "Fundamental Limits of Prompt Compression: A Rate-Distortion Framework for Black-Box Language Models"
authors: ["Alliot Nagle", "Adway Girish", "Marco Bondaschi", "Michael Gastpar", "Ashok Vardhan Makkuva", "Hyeji Kim"]
year: 2024
venue: "preprint"
source_type: "preprint"
paper_url: "https://arxiv.org/abs/2407.15504"
pdf_path: "papers/academic/nagle-2024-prompt-compression-rate-distortion.pdf"
accessed: "2026-09-04"
review_status: "skimmed"
evidence_confidence: "medium"
---

# nagle-2024-prompt-compression-rate-distortion — Fundamental Limits of Prompt Compression: A Rate-Distortion Framework for Black-Box Language Models

## Why this source is in the corpus

Directly studies reusable harness components, outer-loop optimization, self-modification, or the statistical controls needed to decide whether an update is a real improvement.

## Research question

What is the best distortion achievable by a black-box prompt compressor at a specified expected token-rate budget?

## Harness mechanism studied

A stochastic compressor selects an allowed compressed message for each prompt; prompt length defines rate and downstream black-box-model loss defines distortion; primal and dual linear programs trace the optimum.

## Method and experimental setup

Finite-alphabet optimization theory plus exact synthetic experiments and approximate studies on small natural-language datasets; query-agnostic and query-aware settings are separated.

## Main findings

- The dual LP gives a computable fundamental limit for the declared finite message sets.
- Existing compressors were far from the exact synthetic frontier; query awareness and variable-rate Adaptive QuerySelect improved the tradeoff, but large natural prompts required approximations.

## Mathematical content

Theorem 1 gives D*(R)=sup_{lambda>=0}{-lambda R + sum_x min_{m in M_x}[D_{x,m}+lambda R_{x,m}]}; Theorem 2 gives analogous query-conditioned and average query-aware duals. The exact result assumes finite X and M_x, a fixed black-box model and source/query law, and the paper's rate and distortion definitions.

## Evidence quality and limitations

Enumerating all token-pruned messages is exponential in prompt length; exact frontiers were feasible mainly on synthetic binary prompts; natural-language curves use beam-search bounds and limited datasets; the result is not Shannon's universal asymptotic rate-distortion theorem.

## Important implementation details

Define an allowed compiler message set, measure normalized token rate and task loss under a fixed target model, solve the dual on small controlled domains, and use the resulting curve as a lower-bound baseline rather than a production guarantee.

## Claims this source supports

Context compilation can be posed as a constrained outcome-versus-rate optimization with a falsifiable optimal frontier.

## Claims this source weakens or contradicts

The claim that a named prompt compressor is near optimal merely because it beats other heuristics, or that token count alone is a Shannon information rate.

## Relevance to a mathematics paper

Gives an operational finite optimization problem that connects harness context budgets to task-specific distortion without pretending the LLM is an ideal decoder.

## Connections to other sources

See the category and claim-level cross-references in [`INDEX.md`](INDEX.md) and the synthesis documents.

## Verification notes

Local PDF Sections 3-4, Proposition 1, Theorems 1-2, Figures 1 and 6, and large-prompt complexity discussion on pp. 18-20 checked. The archived file parsed successfully: 42 pages, 109489 extractable characters, SHA-256 `029bc1b2d30fead23ef4f4a00e08d070d9d92ae271acbe3ce7a6e6df26ea5048`.
