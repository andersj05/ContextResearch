---
title: "CAMEL: Communicative Agents for Mind Exploration of Large Language Model Society"
authors: ["Guohao Li", "Hasan Abed Al Kader Hammoud", "Hani Itani", "Dmitrii Khizbullin", "Bernard Ghanem"]
year: 2023
venue: "NeurIPS-2023"
source_type: "peer-reviewed"
paper_url: "https://arxiv.org/abs/2303.17760"
pdf_path: "papers/academic/li-2023-camel.pdf"
accessed: "2026-09-04"
review_status: "skimmed"
evidence_confidence: "medium"
---

# li-2023-camel — CAMEL: Communicative Agents for Mind Exploration of Large Language Model Society

## Why this source is in the corpus

Provides communication, aggregation, or coordination mechanisms and their compute-matched counterevidence.

## Research question

Can role-playing prompts sustain autonomous cooperation between conversational agents?

## Harness mechanism studied

Inception prompts assign complementary roles and a task; two agents iteratively exchange instructions and solutions.

## Method and experimental setup

Framework demonstrations and generated conversational datasets explore role consistency and task completion across many prompts.

## Main findings

- CAMEL shows that role prompts can generate long, structured agent-agent interactions with limited human turns.
- Its central evidence is feasibility and behavior generation, not a compute-matched proof that two agents outperform one.

## Mathematical content

The interaction is an alternating message process conditioned on fixed role prompts; no consensus or convergence theorem is established.

## Evidence quality and limitations

Self-instructed tasks, qualitative assessment, old ChatGPT models, prompt leakage and role drift, and no neutral success oracle.

## Important implementation details

Pin roles, message protocol, maximum turns, termination, and evaluator; preserve full transcripts.

## Claims this source supports

Communication topology and role specification are harness mechanisms.

## Claims this source weakens or contradicts

Agent-society rhetoric as evidence of collective intelligence.

## Relevance to a mathematics paper

Provides an alternating-game model with role-conditioned policies.

## Connections to other sources

See the category and claim-level cross-references in [`INDEX.md`](INDEX.md) and the synthesis documents.

## Verification notes

Abstract, inception prompting, interaction loop, dataset generation, examples, and limitations checked in the local PDF. The archived file parsed successfully: 77 pages, 209032 extractable characters, SHA-256 `926c73c2ae9f9abc7612ab58373e428476f4de55db78646ed59de09810db7777`.
