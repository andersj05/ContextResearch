---
title: "ART: Automatic multi-step reasoning and tool-use for large language models"
authors: ["Bhargavi Paranjape", "Scott Lundberg", "Sameer Singh", "Hannaneh Hajishirzi", "Luke Zettlemoyer", "Marco Tulio Ribeiro"]
year: 2023
venue: "preprint"
source_type: "preprint"
paper_url: "https://arxiv.org/abs/2303.09014"
pdf_path: "papers/academic/paranjape-2023-art.pdf"
accessed: "2026-09-04"
review_status: "skimmed"
evidence_confidence: "medium"
---

# paranjape-2023-art — ART: Automatic multi-step reasoning and tool-use for large language models

## Why this source is in the corpus

Models the action interface through which a harness turns language outputs into state-changing operations.

## Research question

Can a frozen model reuse a library of reasoning-and-tool programs on unseen tasks?

## Harness mechanism studied

ART retrieves demonstrations, generates an explicit program, pauses on tool calls, inserts results, and resumes execution.

## Method and experimental setup

BigBench and related reasoning tasks compare automatic program generation with hand-crafted chain-of-thought and tool-use baselines.

## Main findings

- A task library can induce multi-step tool programs without writing a new prompt for every task.
- Human correction of a small number of generated steps can further improve reported performance.

## Mathematical content

The generated program is a sequential policy with typed tool calls; no correctness or search-optimality theorem is established.

## Evidence quality and limitations

Task similarity retrieval, demonstrations, tools, and optional human edits are coupled; benchmark tasks and models are early-generation.

## Important implementation details

Store reusable demonstrations as executable traces and treat pauses, tool results, and repair as explicit runtime events.

## Claims this source supports

Program libraries are a practical form of harness memory and skill reuse.

## Claims this source weakens or contradicts

Automatic retrieval as evidence that the induced program is semantically correct.

## Relevance to a mathematics paper

Supports program-synthesis and case-based-reasoning formulations.

## Connections to other sources

See the category and claim-level cross-references in [`INDEX.md`](INDEX.md) and the synthesis documents.

## Verification notes

Abstract, library retrieval, execution mechanism, benchmark comparisons, human-feedback experiment, and conclusion checked in the local PDF. The archived file parsed successfully: 26 pages, 96684 extractable characters, SHA-256 `b93afc2d95a82fbf1204f5cae3a0322aec2ca6ff258ab45115d7f047bcd5593f`.
