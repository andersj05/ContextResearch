---
title: "Revisiting Multi-Agent Debate as Test-Time Scaling: A Systematic Study of Conditional Effectiveness"
authors: ["Yongjin Yang", "Euiin Yi", "Jongwoo Ko", "Kimin Lee", "Zhijing Jin", "Se-Young Yun"]
year: 2025
venue: "preprint"
source_type: "preprint"
paper_url: "https://arxiv.org/abs/2505.22960"
pdf_path: "papers/academic/yang-2025-revisiting-mad.pdf"
accessed: "2026-09-04"
review_status: "fully-reviewed"
evidence_confidence: "high"
---

# yang-2025-revisiting-mad — Revisiting Multi-Agent Debate as Test-Time Scaling: A Systematic Study of Conditional Effectiveness

## Why this source is in the corpus

Provides communication, aggregation, or coordination mechanisms and their compute-matched counterevidence.

## Research question

When does debate beat self-consistency under a fixed generation budget?

## Harness mechanism studied

Sequential and parallel debate configurations are mapped to the same M times T generation budget as voting and self-refinement.

## Method and experimental setup

Maximum 16 generations across MATH500, AIME, and safety tasks over several Qwen sizes plus selected closed models.

## Main findings

- On MATH500 self-consistency wins at each reported Qwen scale: 60.5 versus 59.1 at 1.5B, 72.1 versus 72.0 at 3B, and 84.0 versus 83.6 at 32B.
- Debate helps some smaller models on AIME, while heterogeneous groups can converge near the harmonic mean and degrade.

## Mathematical content

Defines explicit mappings between agent count M, rounds T, and a fixed MT call budget.

## Evidence quality and limitations

ArXiv-only, early stopping changes realized compute, tasks are math and safety, and some closed-model conditions run once.

## Important implementation details

Match realized tokens as well as maximum calls and report model-size and task interactions.

## Claims this source supports

Debate effectiveness is conditional rather than universal.

## Claims this source weakens or contradicts

Multi-agent communication as generally superior to independent voting.

## Relevance to a mathematics paper

Supplies a clean budget normalization for factorial comparisons.

## Connections to other sources

See the category and claim-level cross-references in [`INDEX.md`](INDEX.md) and the synthesis documents.

## Verification notes

Budget mappings, MATH500 and AIME tables, heterogeneous groups, early-stopping rules, and limitations checked in the local PDF. The archived file parsed successfully: 30 pages, 89540 extractable characters, SHA-256 `e2c9b426b9527e86494282488a49cef0f1b9ff11a656fab769dfebda587d749d`.
