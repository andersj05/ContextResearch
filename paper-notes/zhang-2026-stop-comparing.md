---
title: "Stop Comparing LLM Agents Without Disclosing the Harness"
authors: ["Yunbei Zhang", "Janet Wang", "Yingqiang Ge", "Weijie Xu", "Jihun Hamm", "Chandan K. Reddy"]
year: 2026
venue: "OpenReview-2026"
source_type: "preprint"
paper_url: "https://arxiv.org/abs/2605.23950"
pdf_path: "papers/academic/zhang-2026-stop-comparing.pdf"
accessed: "2026-09-04"
review_status: "fully-reviewed"
evidence_confidence: "medium"
---

# zhang-2026-stop-comparing — Stop Comparing LLM Agents Without Disclosing the Harness

## Why this source is in the corpus

Makes model–harness–environment coupling observable in executable, long-horizon tasks.

## Research question

When do harness differences make cross-model agent comparisons invalid?

## Harness mechanism studied

The position paper models the harness as a closed-loop controller governing context, actions, feedback, stability, and verification, and proposes locked-harness or factorial protocols.

## Method and experimental setup

2026 position paper synthesizing published examples, industry evidence, and a variance decomposition around a Binding Constraint Thesis.

## Main findings

- It argues that among comparable frontier models on long-horizon tasks, harness-induced variance can exceed model-induced variance and reverse rankings.
- The paper's own cited examples include a fixed-model Terminal-Bench change from 69.7% to 77.0%, but the thesis is conditional, not universal.

## Mathematical content

A variance model partitions model, harness, task, and interaction effects; the control framing writes the model as stochastic policy inside a harness-governed state transition.

## Evidence quality and limitations

This is a very recent position paper, selected evidence can favor the thesis, terms such as comparable frontier capability and long horizon require operational definitions, and broad causal evidence remains limited.

## Important implementation details

Disclose context construction, tool mediation, error handling, retries, verification, stopping, budgets, environment, and versions; use a locked harness or crossed model-by-harness design.

## Claims this source supports

The harness is a treatment variable and agent scores are system-level measurements.

## Claims this source weakens or contradicts

Any universal claim that harness always dominates model, or use of the position paper as replicated causal proof.

## Relevance to a mathematics paper

Gives a clean control-system and variance-component formulation for a research hypothesis.

## Connections to other sources

See the category and claim-level cross-references in [`INDEX.md`](INDEX.md) and the synthesis documents.

## Verification notes

Abstract, pages 1-2, formal framing, evidence examples, disclosure proposal, thesis boundary, and limitations checked in the local PDF. The archived file parsed successfully: 17 pages, 63410 extractable characters, SHA-256 `4b7b9b46dc076753ad9cfc51f2741d3828cdb1e2fc8848c4dcaa49836f4072dc`.
