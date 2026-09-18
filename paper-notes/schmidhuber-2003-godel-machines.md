---
title: "Goedel Machines: Self-Referential Universal Problem Solvers Making Provably Optimal Self-Improvements"
authors: ["Juergen Schmidhuber"]
year: 2003
venue: "AGI-2007"
source_type: "peer-reviewed"
paper_url: "https://arxiv.org/abs/cs/0309048"
pdf_path: "papers/academic/schmidhuber-2003-godel-machines.pdf"
accessed: "2026-09-04"
review_status: "skimmed"
evidence_confidence: "medium"
---

# schmidhuber-2003-godel-machines — Goedel Machines: Self-Referential Universal Problem Solvers Making Provably Optimal Self-Improvements

## Why this source is in the corpus

Directly studies reusable harness components, outer-loop optimization, self-modification, or the statistical controls needed to decide whether an update is a real improvement.

## Research question

Can a self-referential problem solver make a self-rewrite whose utility is provably better than continuing its current computation?

## Harness mechanism studied

An embedded proof searcher tests proof techniques for a target theorem comparing immediate execution of switchprog with continued proof search; switchprog may rewrite any part of the machine, including the proof searcher.

## Method and experimental setup

Formal construction and relative-optimality proof in a self-referential axiomatic system; no empirical agent evaluation.

## Main findings

- Theorem 4.1 makes each executed rewrite globally optimal relative to the encoded utility, axioms, hardware model, and current proof-search alternative.
- The theorem is conditional: it neither promises that a useful proof exists nor that proof search finds one within a practical budget.

## Mathematical content

The gate proves E[u | execute switchprog now] > E[u | continue search], where both branches include their downstream self-modifications. Theorem 4.1 assumes a formalizable u and consistency of axiom system A; the proof argues that waiting for another proof is already represented in the rejected branch.

## Evidence quality and limitations

Soundness about the external world is only as good as A; incompleteness and proof-search cost can prevent useful changes; constants and formalization burden are severe; globally optimal is frequently overquoted without its relative qualifier.

## Important implementation details

Use a small decidable rewrite language, an immutable proof checker, explicit cost and utility axioms, and reject on unknown; combine the proof gate with empirical validation for properties not formalized in A.

## Claims this source supports

A proof-carrying harness update can have a conditional non-regression guarantee inside a restricted formal model.

## Claims this source weakens or contradicts

The memed claim that a Goedel machine guarantees practical, open-world, or continually discovered optimal self-improvement.

## Relevance to a mathematics paper

Provides the formal comparison between executing an edit and preserving the incumbent, plus a precise example of theorem status depending on an encoded world model.

## Connections to other sources

See the category and claim-level cross-references in [`INDEX.md`](INDEX.md) and the synthesis documents.

## Verification notes

Local PDF pp. 11-12, Section 4.1 and Theorem 4.1 checked; limitations and proof-search qualifications checked in Sections 2, 5, and 6.7. The archived file parsed successfully: 30 pages, 87013 extractable characters, SHA-256 `1b9e2aa5504e3c6709bbde5c37c0f56561f62ec40684e4d4388116ee8b780ffd`.
