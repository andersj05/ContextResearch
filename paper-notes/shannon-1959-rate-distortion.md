---
title: "Coding Theorems for a Discrete Source With a Fidelity Criterion"
authors: ["Claude E. Shannon"]
year: 1959
venue: "IRE-1959"
source_type: "peer-reviewed"
paper_url: "https://ieeexplore.ieee.org/document/1057299"
pdf_path: "papers/academic/shannon-1959-rate-distortion.pdf"
accessed: "2026-09-04"
review_status: "skimmed"
evidence_confidence: "high"
---

# shannon-1959-rate-distortion — Coding Theorems for a Discrete Source With a Fidelity Criterion

## Why this source is in the corpus

Directly studies reusable harness components, outer-loop optimization, self-modification, or the statistical controls needed to decide whether an update is a real improvement.

## Research question

What minimum communication rate permits reproduction of a memoryless source within a specified expected distortion?

## Harness mechanism studied

Long block codes trade code rate against an additive single-letter fidelity criterion; an optimizing test channel determines the frontier.

## Method and experimental setup

Information-theoretic converse and achievability analysis for discrete memoryless sources in the asymptotic block-length limit.

## Main findings

- The rate-distortion function is the sharp asymptotic boundary between achievable and impossible rate-distortion pairs under the stated source and distortion model.
- Applying it to context requires a declared task distortion and code model; it does not equate tokens with bits.

## Mathematical content

With natural logarithms, R(D)=min_{P_{X_tilde|X}: E d(X,X_tilde)<=D} I(X;X_tilde) nats per source symbol; rates above R(D) are asymptotically achievable and rates below are not. Assumptions include stationarity/memorylessness in the basic theorem, nonnegative additive distortion, long blocks, and an agreed source law.

## Evidence quality and limitations

Finite context windows are not the asymptotic regime; interactive state is nonstationary and correlated; an LLM has shared side information; task loss may not be single-letter; an unknown or moving source distribution breaks direct operational use.

## Important implementation details

Use the theorem to define a lower-bound research question after specifying X, reproduction C, side information, and decision distortion; report token length separately from estimated mutual information.

## Claims this source supports

There is an unavoidable context-budget versus task-loss frontier once the source and distortion are operationalized.

## Claims this source weakens or contradicts

The claim that R(D) directly predicts a production prompt's token count or that generic summarization has a task-independent optimal rate.

## Relevance to a mathematics paper

Provides the foundational converse/achievability distinction and the correct minimization over stochastic context channels.

## Connections to other sources

See the category and claim-level cross-references in [`INDEX.md`](INDEX.md) and the synthesis documents.

## Verification notes

Local PDF Sections 3-5 and the fidelity coding theorems checked; bibliographic record and open scan metadata reconciled in the catalog. The archived file parsed successfully: 26 pages, 61976 extractable characters, SHA-256 `bae66c898e04c7088fcadd6232a53b9d3fe66f344f947dab0a34381c1a0a5955`.
