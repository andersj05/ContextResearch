---
title: "Cognitive Architectures for Language Agents"
authors: ["Theodore R. Sumers", "Shunyu Yao", "Karthik Narasimhan", "Thomas L. Griffiths"]
year: 2024
venue: "TMLR"
source_type: "peer-reviewed"
paper_url: "https://arxiv.org/abs/2309.02427"
pdf_path: "papers/academic/sumers-2024-coala.pdf"
accessed: "2026-09-04"
review_status: "skimmed"
evidence_confidence: "medium"
---

# sumers-2024-coala — Cognitive Architectures for Language Agents

## Why this source is in the corpus

Supplies vocabulary and comparison axes for formalizing the harness as a composite decision system.

## Research question

How can language agents be decomposed into a reusable cognitive architecture?

## Harness mechanism studied

A modular loop over working memory, long-term memory, grounded actions, decision making, and learning.

## Method and experimental setup

Conceptual synthesis maps cognitive-science constructs onto representative language-agent systems rather than testing one intervention.

## Main findings

- CoALA supplies a useful architecture-level vocabulary and separates internal from external actions.
- Its principal contribution is a framework for comparison, not evidence that one memory or control design improves performance.

## Mathematical content

The architecture can be expressed as a partially observable decision process with state, observation, memory update, and action-selection functions; the paper does not prove a performance theorem.

## Evidence quality and limitations

Taxonomy boundaries are author-chosen, systems evolved after publication, and empirical causal support is limited.

## Important implementation details

Treat memory stores, retrieval, decision procedures, and grounded action spaces as separately versioned harness components.

## Claims this source supports

An agent should be analyzed as model plus memory plus action and update machinery.

## Claims this source weakens or contradicts

A single scalar benchmark score does not identify which cognitive component caused an outcome.

## Relevance to a mathematics paper

Provides state variables and transition structure for a formal harness model.

## Connections to other sources

See the category and claim-level cross-references in [`INDEX.md`](INDEX.md) and the synthesis documents.

## Verification notes

Abstract, architecture sections, taxonomy figures, and conclusion checked in the local PDF. The archived file parsed successfully: 32 pages, 122125 extractable characters, SHA-256 `fd93d2ef1b94f963b652136b8c792b01d7326d861f5ce918926c043934a48dbe`.
