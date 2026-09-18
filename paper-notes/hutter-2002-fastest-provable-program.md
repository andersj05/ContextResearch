---
title: "The Fastest and Shortest Algorithm for All Well-Defined Problems"
authors: ["Marcus Hutter"]
year: 2002
venue: "IJFCS-2002"
source_type: "peer-reviewed"
paper_url: "https://arxiv.org/abs/cs/0206022"
pdf_path: "papers/academic/hutter-2002-fastest-provable-program.pdf"
accessed: "2026-09-04"
review_status: "skimmed"
evidence_confidence: "high"
---

# hutter-2002-fastest-provable-program — The Fastest and Shortest Algorithm for All Well-Defined Problems

## Why this source is in the corpus

Directly studies reusable harness components, outer-loop optimization, self-modification, or the statistical controls needed to decide whether an update is a real improvement.

## Research question

Can one construct a universal solver whose runtime is near that of every program provably equivalent to a formal specification?

## Harness mechanism studied

Enumerate proofs of program equivalence and time bounds, allocate search and execution resources, and run the best currently proved competitor.

## Method and experimental setup

Formal algorithm and runtime/description-length theorems inside a fixed proof system.

## Main findings

- For every provably equivalent program p with provable time bound t_p, the constructed solver is at most a factor five slower asymptotically, plus program-dependent proof-bound overhead.
- This is a comparator theorem over provable programs, not a practical guarantee of finding the fastest semantic implementation.

## Mathematical content

Theorem 2 states time_{M_p*}(x) <= 5 t_p(x)+d_p time_{t_p}(x)+c_p, with c_p,d_p depending on p and its proofs but not x. Competitors require a proof of equivalence to p* and a proof that their runtime is bounded by t_p in the chosen formal system.

## Evidence quality and limitations

Constants can be enormous; proof search and evaluating t_p may dominate; true but unprovable equivalences are excluded; a wrong or weak specification is still optimized; real tool latency may not be formalizable.

## Important implementation details

Apply only to a restricted pure component with formal semantics, cache proof artifacts, and treat the factor-five asymptotic statement as a conceptual comparator rather than a service-level estimate.

## Claims this source supports

Proof-restricted synthesis can evade an unrestricted fastest-program demand while retaining a conditional performance theorem.

## Claims this source weakens or contradicts

The claim that a universal harness can efficiently identify the actually fastest correct agent implementation in open-world tasks.

## Relevance to a mathematics paper

Provides a constructive counterpoint to Blum speedup by changing the comparator class to provably equivalent, provably bounded programs.

## Connections to other sources

See the category and claim-level cross-references in [`INDEX.md`](INDEX.md) and the synthesis documents.

## Verification notes

Local PDF pp. 1-2 summary and pp. 7-10 proof and Theorem 2 checked, including constants and provability restrictions. The archived file parsed successfully: 13 pages, 34648 extractable characters, SHA-256 `b08f86b49b4fb8607b87ec73bb46cfdb379e80ead363082e14cd36057f3279bd`.
