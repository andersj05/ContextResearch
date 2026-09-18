---
title: "Syntax-Guided Synthesis"
authors: ["Rajeev Alur", "Rastislav Bodik", "Garvit Juniwal", "Milo M. K. Martin", "Mukund Raghothaman", "Sanjit A. Seshia", "Rishabh Singh", "Armando Solar-Lezama", "Emina Torlak", "Abhishek Udupa"]
year: 2013
venue: "FMCAD-2013"
source_type: "peer-reviewed"
paper_url: "https://doi.org/10.1109/FMCAD.2013.6679385"
pdf_path: "papers/academic/alur-2013-sygus.pdf"
accessed: "2026-09-04"
review_status: "skimmed"
evidence_confidence: "high"
---

# alur-2013-sygus — Syntax-Guided Synthesis

## Why this source is in the corpus

Directly studies reusable harness components, outer-loop optimization, self-modification, or the statistical controls needed to decide whether an update is a real improvement.

## Research question

How should program synthesis be formalized when the implementation must come from a user-specified syntactic language?

## Harness mechanism studied

Syntax-Guided Synthesis combines a semantic specification in theory T with a grammar G that restricts admissible implementations and supports solver competition formats.

## Method and experimental setup

Formal problem definition, decidability and complexity analysis for selected grammar-theory fragments, and prototype solver comparisons.

## Main findings

- SyGuS cleanly separates what a candidate must satisfy from the language in which it may be expressed.
- Soundness is relative to the theory, grammar, and verifier; general SyGuS is not uniformly decidable or efficiently solvable.

## Mathematical content

Given specification phi(f,x) and grammar language L(G), solve exists e in L(G) forall x: T models phi[e/f]. CEGIS is one realization; completeness and complexity depend on T and G rather than following from the syntax-guided label alone.

## Evidence quality and limitations

The grammar can omit useful updates or encode dangerous ones; decidable fragments may be too weak; a formally valid specification can be behaviorally wrong; solver termination is fragment-dependent.

## Important implementation details

Version the grammar and theory as part of the harness, make the verifier independent of the proposal model, and record whether rejection means false, unsatisfiable, or unknown.

## Claims this source supports

A fixed-capacity, proof-gated context compiler can be defined as a SyGuS problem over a bounded rule language.

## Claims this source weakens or contradicts

The claim that constrained generation alone proves safety or that a language-model-generated proof substitutes for a sound checker.

## Relevance to a mathematics paper

Gives the exact restricted-program-search quantifiers needed to state a defensible synthesis guarantee.

## Connections to other sources

See the category and claim-level cross-references in [`INDEX.md`](INDEX.md) and the synthesis documents.

## Verification notes

Local PDF pp. 1-3 problem definition and examples, decidability/complexity sections, and solver architecture checked. The archived file parsed successfully: 8 pages, 48450 extractable characters, SHA-256 `ed46aeb2ac50ff93169331b92b11ecd03ffa3bcc43acddd29b468e9913dabaf7`.
