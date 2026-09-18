---
title: "Breaking the Martingale Curse: Multi-Agent Debate via Asymmetric Cognitive Potential Energy"
authors: ["Yuhan Liu", "Juntian Zhang", "Yichen Wu", "Martin Takac", "Salem Lahlou", "Xiuying Chen", "Nils Lukas"]
year: 2026
venue: "preprint"
source_type: "preprint"
paper_url: "https://arxiv.org/abs/2603.06801"
pdf_path: "papers/academic/liu-2026-acemad.pdf"
accessed: "2026-09-04"
review_status: "fully-reviewed"
evidence_confidence: "medium"
---

# liu-2026-acemad — Breaking the Martingale Curse: Multi-Agent Debate via Asymmetric Cognitive Potential Energy

## Why this source is in the corpus

Provides communication, aggregation, or coordination mechanisms and their compute-matched counterevidence.

## Research question

Can peer prediction introduce positive drift that escapes debate's martingale behavior?

## Harness mechanism studied

Agents predict peers' belief distributions; Brier-style scores update credibility weights multiplicatively before aggregation.

## Method and experimental setup

Main experiments emphasize challenging subsets where single-agent success is below 40%, with GPT-4o-mini and open-model ablations.

## Main findings

- On selected hard subsets, GPT-4o-mini majority averages 14.0, standard debate about 22.1, and AceMAD with three rounds 49.92.
- Some cells and open-model settings regress, so the effect is not universal.

## Mathematical content

Peer score S_i=1-||qhat_i-Qbar_-i||^2 and weights update as w_i^(t+1)=w_i^t exp(eta S_i^t); theorems give signal dominance, score separation, and positive submartingale drift under truth-holder assumptions.

## Evidence quality and limitations

Recent v1, selected failure subsets, strong truth-holder and uniform-gap assumptions, and no independent full-distribution replication.

## Important implementation details

Elicit predictions separately from answers, calibrate the learning rate, and test whether truth-holder assumptions hold before aggregation.

## Claims this source supports

Asymmetric information can create debate improvement where symmetric exchange cannot.

## Claims this source weakens or contradicts

Selected-subset gains as general debate performance.

## Relevance to a mathematics paper

Offers a mechanism-design and submartingale extension to the debate-vote theory.

## Connections to other sources

See the category and claim-level cross-references in [`INDEX.md`](INDEX.md) and the synthesis documents.

## Verification notes

Main table, Brier score, multiplicative update, Theorems 4.2/4.4/4.6, assumptions, regressions, and limitations checked in the local PDF. The archived file parsed successfully: 25 pages, 74572 extractable characters, SHA-256 `fb6eab55458e03c9d53bd671e27979a1ef22853adc0a4f560756b721f6a29f09`.
