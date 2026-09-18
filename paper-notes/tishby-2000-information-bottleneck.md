---
title: "The Information Bottleneck Method"
authors: ["Naftali Tishby", "Fernando C. Pereira", "William Bialek"]
year: 2000
venue: "Allerton-1999"
source_type: "peer-reviewed"
paper_url: "https://arxiv.org/abs/physics/0004057"
pdf_path: "papers/academic/tishby-2000-information-bottleneck.pdf"
accessed: "2026-09-04"
review_status: "skimmed"
evidence_confidence: "high"
---

# tishby-2000-information-bottleneck — The Information Bottleneck Method

## Why this source is in the corpus

Directly studies reusable harness components, outer-loop optimization, self-modification, or the statistical controls needed to decide whether an update is a real improvement.

## Research question

How can a representation discard information about X while retaining information relevant to prediction of Y?

## Harness mechanism studied

A stochastic encoder minimizes information about X subject to preserving predictive information about Y; self-consistent Blahut-Arimoto-like updates solve the stationary equations.

## Method and experimental setup

Variational information theory for finite alphabets, derivation of self-consistent equations, and convergence of alternating minimization to the stated stationary/minimum structure.

## Main findings

- The bottleneck supplies a task-relative compression objective rather than a universal notion of summary quality.
- Alternating updates decrease a common functional, but joint nonconvexity means the convergence proof does not imply a unique global solution.

## Mathematical content

Under C-X-Y, L_beta=I(X;C)-beta I(C;Y). Theorem 4 gives Q(c|x)=P(c)exp[-beta D_KL(P(Y|x)||P(Y|c))]/Z_beta(x); Theorem 5 gives self-consistent alternating updates. Predictive sufficiency is I(X;Y|C)=0, equivalently I(C;Y)=I(X;Y) under the Markov condition.

## Evidence quality and limitations

Requires a fixed joint P(X,Y), finite or suitably regular alphabets, and a meaningful relevance variable Y; learned neural objectives only approximate mutual information; local minima and representation cardinality matter.

## Important implementation details

Choose Y as a preregistered future action, verifier result, or outcome; estimate the tradeoff on held-out data; do not use the same evaluator to learn the encoder and certify sufficiency.

## Claims this source supports

Context quality can be formalized as compression of task state that preserves declared decision-relevant information.

## Claims this source weakens or contradicts

The claim that the bottleneck discovers relevance without specifying Y, or that its stationary equations certify a globally optimal neural context compiler.

## Relevance to a mathematics paper

Gives the central Lagrangian, effective KL distortion, and an exact criterion for task-relative sufficient context.

## Connections to other sources

See the category and claim-level cross-references in [`INDEX.md`](INDEX.md) and the synthesis documents.

## Verification notes

Local PDF Equation 15, Theorem 4 and Equation 28 on pp. 9-11, and Theorem 5 plus non-uniqueness qualification on pp. 12-13 checked. The archived file parsed successfully: 16 pages, 25831 extractable characters, SHA-256 `afdbc45366b590086e34faef76ad0570885884489ed32233c8571912ef92ef47`.
