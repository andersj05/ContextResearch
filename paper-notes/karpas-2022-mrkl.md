---
title: "MRKL Systems: A modular neuro-symbolic architecture that combines large language models external knowledge sources and discrete reasoning"
authors: ["Ehud Karpas", "Omri Abend", "Yonatan Belinkov", "Barak Lenz", "Opher Lieber", "Nir Ratner", "Yoav Shoham", "Hofit Bata", "Yoav Levine", "Kevin Leyton-Brown", "Dor Muhlgay", "Noam Rozen", "Erez Schwartz", "Gal Shachaf", "Shai Shalev-Shwartz", "Amnon Shashua", "Moshe Tenenholtz"]
year: 2022
venue: "preprint"
source_type: "preprint"
paper_url: "https://arxiv.org/abs/2205.00445"
pdf_path: "papers/academic/karpas-2022-mrkl.pdf"
accessed: "2026-09-04"
review_status: "skimmed"
evidence_confidence: "medium"
---

# karpas-2022-mrkl — MRKL Systems: A modular neuro-symbolic architecture that combines large language models external knowledge sources and discrete reasoning

## Why this source is in the corpus

Models the action interface through which a harness turns language outputs into state-changing operations.

## Research question

Can a language model route requests to symbolic, retrieval, and domain-specific expert modules?

## Harness mechanism studied

A neural router delegates subtasks to discrete calculators, databases, knowledge bases, and specialized models before composing an answer.

## Method and experimental setup

Architecture and Jurassic-X implementation examples illustrate modular neuro-symbolic routing and discuss training and integration challenges.

## Main findings

- MRKL reframes a large language model as one component in a modular system rather than the sole knowledge or reasoning engine.
- It offers strong architectural motivation but limited controlled causal evidence.

## Mathematical content

A router can be modeled as a latent expert-selection variable in a mixture-of-experts system; no new general performance theorem is proved.

## Evidence quality and limitations

Predominantly a position and architecture paper, proprietary implementation details, and few reproducible head-to-head experiments.

## Important implementation details

Give tools narrow contracts, expose routing failures, and separate deterministic expert outputs from language composition.

## Claims this source supports

External modules can supply capabilities and current knowledge absent from model weights.

## Claims this source weakens or contradicts

Modularity alone as evidence of reliability or correct routing.

## Relevance to a mathematics paper

Motivates mixture and routing-error decompositions for harness success probability.

## Connections to other sources

See the category and claim-level cross-references in [`INDEX.md`](INDEX.md) and the synthesis documents.

## Verification notes

Abstract, architecture, routing examples, implementation challenges, and conclusion checked in the local PDF. The archived file parsed successfully: 19 pages, 36151 extractable characters, SHA-256 `50496293f221729999f03d17867bd0b7a84dba7275196684a1aa6fe06cca7257`.
