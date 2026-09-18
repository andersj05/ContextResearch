---
title: "Why Do Multi-Agent LLM Systems Fail?"
authors: ["Mert Cemri", "Melissa Z. Pan", "Shuyi Yang", "Lakshya A. Agrawal", "Bhavya Chopra", "Rishabh Tiwari", "Kurt Keutzer", "Aditya Parameswaran", "Dan Klein", "Kannan Ramchandran", "Matei Zaharia", "Joseph E. Gonzalez", "Ion Stoica"]
year: 2025
venue: "preprint"
source_type: "preprint"
paper_url: "https://arxiv.org/abs/2503.13657"
pdf_path: "papers/academic/cemri-2025-mas-failures.pdf"
accessed: "2026-09-04"
review_status: "fully-reviewed"
evidence_confidence: "high"
---

# cemri-2025-mas-failures — Why Do Multi-Agent LLM Systems Fail?

## Why this source is in the corpus

Provides communication, aggregation, or coordination mechanisms and their compute-matched counterevidence.

## Research question

What recurring failure modes prevent multi-agent systems from achieving their goals?

## Harness mechanism studied

MAST is a 14-mode taxonomy over specification, inter-agent misalignment, and task-verification failures, applied to execution traces.

## Method and experimental setup

Grounded-theory analysis of 150 traces, iterative human annotation, an LLM annotator, and 1,642 traces across seven frameworks.

## Main findings

- Observed system failure rates span 41% to 86.7%.
- Human taxonomy agreement reaches Cohen's kappa 0.88; the LLM annotator reaches 94% accuracy and kappa 0.77; a case-study intervention adds 9.4% task success.

## Mathematical content

Cohen's kappa quantifies label agreement; prevalence is a trace-sample estimate, not a causal probability for all tasks.

## Evidence quality and limitations

Framework and benchmark sample selection, failures can have multiple causes, LLM annotations, and taxonomy completeness is explicitly not claimed.

## Important implementation details

Log message provenance and responsibility, classify failures before repair, and validate interventions on held-out traces.

## Claims this source supports

Many multi-agent losses arise from coordination and specification rather than base reasoning alone.

## Claims this source weakens or contradicts

Adding agents as monotonically reducing error.

## Relevance to a mathematics paper

Provides categorical failure variables and agreement statistics for a reliability model.

## Connections to other sources

See the category and claim-level cross-references in [`INDEX.md`](INDEX.md) and the synthesis documents.

## Verification notes

Figure 1, dataset counts, 14 modes, kappa studies, seven-system rates, case intervention, and limitations checked in the local PDF. The archived file parsed successfully: 47 pages, 135482 extractable characters, SHA-256 `1b9e317a2a421e60ca2b2eda4a30844557a01e63286a790890c0ecef32d25460`.
