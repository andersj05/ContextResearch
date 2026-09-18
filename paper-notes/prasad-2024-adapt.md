---
title: "ADaPT: As-Needed Decomposition and Planning with Language Models"
authors: ["Archiki Prasad", "Alexander Koller", "Mareike Hartmann", "Peter Clark", "Ashish Sabharwal", "Mohit Bansal", "Tushar Khot"]
year: 2024
venue: "NAACL-2024"
source_type: "peer-reviewed"
paper_url: "https://arxiv.org/abs/2311.05772"
pdf_path: "papers/academic/prasad-2024-adapt.pdf"
accessed: "2026-09-04"
review_status: "skimmed"
evidence_confidence: "medium"
---

# prasad-2024-adapt — ADaPT: As-Needed Decomposition and Planning with Language Models

## Why this source is in the corpus

Supports analysis of inference-time search, feedback, stopping, and verifier error.

## Research question

Can an agent defer decomposition until a simple attempt fails?

## Harness mechanism studied

A model first tries the task, a verifier detects failure, and only then recursively decomposes into smaller subtasks.

## Method and experimental setup

A suite of reasoning and embodied or interactive tasks compares as-needed decomposition with always-decompose and direct baselines.

## Main findings

- Conditional decomposition can save calls on easy tasks while allocating more structure to failures.
- Its benefit depends on a reliable success signal and on decomposed subtasks being easier and composable.

## Mathematical content

The controller is a recursive policy with a failure gate and depth or budget bound; no universal termination or correctness theorem is proved.

## Evidence quality and limitations

Verifier errors propagate, recursion cost varies by task, decomposition prompts carry domain knowledge, and evaluation mixes environments.

## Important implementation details

Set explicit depth, token, and retry limits and log why each decomposition was triggered.

## Claims this source supports

Adaptive allocation can dominate uniformly elaborate planning when task difficulty varies.

## Claims this source weakens or contradicts

Always-on decomposition or fixed workflow complexity as universally efficient.

## Relevance to a mathematics paper

Supports optimal-stopping and value-of-computation models for conditional branching.

## Connections to other sources

See the category and claim-level cross-references in [`INDEX.md`](INDEX.md) and the synthesis documents.

## Verification notes

Abstract, controller algorithm, triggering and stopping rules, ablations, cost discussion, and limitations checked in the local PDF. The archived file parsed successfully: 27 pages, 109882 extractable characters, SHA-256 `9de7a8f3fa07efc9b35c5dac4f5d7a8b55720e3eeaa9f65788aa06a54aa05a0f`.
