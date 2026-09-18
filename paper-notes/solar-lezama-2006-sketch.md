---
title: "Combinatorial Sketching for Finite Programs"
authors: ["Armando Solar-Lezama", "Liviu Tancau", "Rastislav Bodik", "Sanjit Seshia", "Vijay Saraswat"]
year: 2006
venue: "ASPLOS-2006"
source_type: "peer-reviewed"
paper_url: "https://doi.org/10.1145/1168857.1168907"
pdf_path: "papers/academic/solar-lezama-2006-sketch.pdf"
accessed: "2026-09-04"
review_status: "skimmed"
evidence_confidence: "high"
---

# solar-lezama-2006-sketch — Combinatorial Sketching for Finite Programs

## Why this source is in the corpus

Directly studies reusable harness components, outer-loop optimization, self-modification, or the statistical controls needed to decide whether an update is a real improvement.

## Research question

Can a programmer specify a finite program family with holes and automatically synthesize a completion satisfying assertions?

## Harness mechanism studied

Sketches leave unknown constants or expressions; counterexample-guided inductive synthesis reduces finite candidate search and verification to Boolean constraints.

## Method and experimental setup

Language and solver design with combinatorial synthesis, formal finite-program semantics, and systems experiments on implementation sketches.

## Main findings

- For the encoded finite search space, the solver can return a completion satisfying the formal assertions or establish failure relative to the bounded encoding.
- The practical contribution is a restricted synthesis architecture; it does not prove that assertions capture open-world intent.

## Mathematical content

A sketch denotes candidates p(theta) for finite hole assignment theta; synthesis seeks exists theta forall x: phi(p(theta),x). CEGIS alternates a finite-example synthesis query with a verification query that finds x violating phi; finite exhaustive encodings give relative completeness.

## Evidence quality and limitations

Finite bounds, solver scalability, and specification quality limit the result; undefined behavior, external tools, concurrency, and natural-language requirements can fall outside the semantics; a satisfying program may exploit a specification hole.

## Important implementation details

Define a small harness-edit DSL, state invariants independently of candidate generation, use counterexamples to refine edits, and reject when the solver cannot prove the bounded obligation.

## Claims this source supports

Self-improvement can be made verifiable by restricting the change language and separating synthesis from checking.

## Claims this source weakens or contradicts

The claim that tests or solver success establish unrestricted semantic correctness of an arbitrary generated harness.

## Relevance to a mathematics paper

Provides the quantified synthesis form and proof-gate architecture used in the proposed context-compiler package.

## Connections to other sources

See the category and claim-level cross-references in [`INDEX.md`](INDEX.md) and the synthesis documents.

## Verification notes

Local PDF language/semantics and solver sections, CEGIS architecture, finite Boolean encoding, and evaluation examples checked. The archived file parsed successfully: 12 pages, 74370 extractable characters, SHA-256 `77cb14b219e7e8118d7b12ecb75685ca1225ae6f3246c2db72a874ca8720529f`.
