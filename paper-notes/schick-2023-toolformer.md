---
title: "Toolformer: Language Models Can Teach Themselves to Use Tools"
authors: ["Timo Schick", "Jane Dwivedi-Yu", "Roberto Dessì", "Roberta Raileanu", "Maria Lomeli", "Luke Zettlemoyer", "Nicola Cancedda", "Thomas Scialom"]
year: 2023
venue: "NeurIPS-2023"
source_type: "peer-reviewed"
paper_url: "https://arxiv.org/abs/2302.04761"
pdf_path: "papers/academic/schick-2023-toolformer.pdf"
accessed: "2026-09-04"
review_status: "fully-reviewed"
evidence_confidence: "high"
---

# schick-2023-toolformer — Toolformer: Language Models Can Teach Themselves to Use Tools

## Why this source is in the corpus

Models the action interface through which a harness turns language outputs into state-changing operations.

## Research question

Can a language model self-supervise when and how to call a small fixed tool set?

## Harness mechanism studied

Candidate API calls are inserted and retained when returned values reduce future-token loss; the fine-tuned model emits calls during generation.

## Method and experimental setup

Self-supervised data construction and fine-tuning over calculator, Q&A, search, translation, and calendar APIs, with tool-enabled and disabled inference comparisons.

## Main findings

- A call is retained only when its result improves weighted future-token loss by at least τ_f.
- At τ_f=0.5 retained calls range from 3,156 for translation to 207,241 for Wikipedia, showing strong tool and data imbalance.

## Mathematical content

L_i(z) is weighted future negative log likelihood; retain a call when L_i^- - L_i^+ ≥ τ_f.

## Evidence quality and limitations

Fine-tuning changes the model, only five fixed APIs are available, a one-call test-time limit prevents realistic recovery loops, and retention optimizes token loss rather than task utility.

## Important implementation details

Represent calls inline with results, filter noisy demonstrations, and evaluate with tools enabled and disabled on the same weights.

## Claims this source supports

Models can learn call timing and argument generation from weak self-supervision.

## Claims this source weakens or contradicts

Toolformer as a pure inference-harness result or evidence for dynamic multi-step agents.

## Relevance to a mathematics paper

Provides a loss-based tool-selection criterion that can be compared with utility-based gating.

## Connections to other sources

See the category and claim-level cross-references in [`INDEX.md`](INDEX.md) and the synthesis documents.

## Verification notes

Filtering equation, retained-call counts, API setup, enabled-disabled results, and limitations checked in the local PDF. The archived file parsed successfully: 17 pages, 71922 extractable characters, SHA-256 `6d7483d94653008e40c2058a1c22441c92e3713dae278b6361e8efc447c99522`.
