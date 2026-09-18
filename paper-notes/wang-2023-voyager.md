---
title: "Voyager: An Open-Ended Embodied Agent with Large Language Models"
authors: ["Guanzhi Wang", "Yuqi Xie", "Yunfan Jiang", "Ajay Mandlekar", "Chaowei Xiao", "Yuke Zhu", "Linxi Fan", "Anima Anandkumar"]
year: 2023
venue: "TMLR-2023"
source_type: "peer-reviewed"
paper_url: "https://arxiv.org/abs/2305.16291"
pdf_path: "papers/academic/wang-2023-voyager.pdf"
accessed: "2026-09-04"
review_status: "skimmed"
evidence_confidence: "medium"
---

# wang-2023-voyager — Voyager: An Open-Ended Embodied Agent with Large Language Models

## Why this source is in the corpus

Provides mechanisms and failure modes for state, retrieval, summarization, and bounded context.

## Research question

Can a lifelong embodied agent autonomously acquire and reuse executable skills?

## Harness mechanism studied

An automatic curriculum selects exploration goals, a vector-indexed skill library stores code, and iterative prompting uses execution errors and self-verification.

## Method and experimental setup

Minecraft evaluation compares Voyager with ReAct, Reflexion, and AutoGPT-style baselines on exploration, technology-tree progress, and zero-shot transfer.

## Main findings

- Voyager reports 3.3 times more unique items, 2.3 times longer exploration distance, and up to 15.3 times faster technology-tree milestones than baselines.
- Skill reuse and curriculum are coupled with GPT-4 and executable environmental feedback.

## Mathematical content

The curriculum and skill retrieval define a nonstationary policy over goals and reusable programs; no lifelong-learning regret or convergence bound is proved.

## Evidence quality and limitations

One game, proprietary GPT-4, substantial hand-engineered environment interface, multiple coupled modules, and no matched-token ablation for every baseline.

## Important implementation details

Store skills as executable code with descriptions, test them in the environment, and retrieve only relevant validated skills.

## Claims this source supports

A persistent skill library can compound capability without weight updates.

## Claims this source weakens or contradicts

Minecraft exploration as direct evidence of general lifelong agency.

## Relevance to a mathematics paper

Invites option-learning and curriculum-optimization formulations over a program library.

## Connections to other sources

See the category and claim-level cross-references in [`INDEX.md`](INDEX.md) and the synthesis documents.

## Verification notes

Abstract, three components, main exploration table, technology-tree timing, transfer, ablations, and limitations checked in the local PDF. The archived file parsed successfully: 42 pages, 128250 extractable characters, SHA-256 `769a4e33ddeeb73870849232eece49afe882c2d146362e33917ccb432ba0efb8`.
