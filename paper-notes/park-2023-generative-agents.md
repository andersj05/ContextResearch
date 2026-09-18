---
title: "Generative Agents: Interactive Simulacra of Human Behavior"
authors: ["Joon Sung Park", "Joseph C. O'Brien", "Carrie J. Cai", "Meredith Ringel Morris", "Percy Liang", "Michael S. Bernstein"]
year: 2023
venue: "UIST-2023"
source_type: "peer-reviewed"
paper_url: "https://arxiv.org/abs/2304.03442"
pdf_path: "papers/academic/park-2023-generative-agents.pdf"
accessed: "2026-09-04"
review_status: "fully-reviewed"
evidence_confidence: "high"
---

# park-2023-generative-agents — Generative Agents: Interactive Simulacra of Human Behavior

## Why this source is in the corpus

Provides mechanisms and failure modes for state, retrieval, summarization, and bounded context.

## Research question

Do memory, reflection, and planning improve human judgments of believable agent behavior over time?

## Harness mechanism studied

A memory stream is retrieved by recency, importance, and relevance; accumulated importance triggers reflections; plans condition later actions.

## Method and experimental setup

A 25-agent sandbox, qualitative emergence examples, and a 100-person within-subject evaluation compare full and ablated architectures using TrueSkill.

## Main findings

- Full architecture has TrueSkill mean 29.89 versus 26.88 without reflection, 25.64 without reflection and planning, and 21.21 without memory, planning, or reflection.
- The Friedman statistic H(4)=150.29 with p<0.001 supports the bundle on believability, not objective task competence.

## Mathematical content

Retrieval sums normalized recency, importance, and relevance with equal weights; recency decays by 0.995; reflection triggers above accumulated importance 150; evaluation uses a Gaussian TrueSkill model.

## Evidence quality and limitations

Memories from the full simulation were reused in ablations, outcomes are human-rated believability, and famous social anecdotes are not controlled capability tests.

## Important implementation details

Record memory write rules, retrieval weights, reflection trigger, and plan horizon; rerun ablations with fresh trajectories.

## Claims this source supports

Memory, reflection, and planning materially affect perceived behavioral coherence.

## Claims this source weakens or contradicts

Emergent-society anecdotes as evidence of general autonomous capability.

## Relevance to a mathematics paper

Provides scoring, threshold, and latent-skill models for a stateful harness.

## Connections to other sources

See the category and claim-level cross-references in [`INDEX.md`](INDEX.md) and the synthesis documents.

## Verification notes

Architecture equations, trigger thresholds, ablation table, TrueSkill analysis, and evaluation protocol checked in the local PDF. The archived file parsed successfully: 22 pages, 130391 extractable characters, SHA-256 `1b31e77fb24d25d7598f2c49e955d12a28b95a6dabad34acdac40f44bfb7a139`.
