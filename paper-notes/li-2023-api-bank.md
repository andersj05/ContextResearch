---
title: "API-Bank: A Comprehensive Benchmark for Tool-Augmented LLMs"
authors: ["Minghao Li", "Yingxiu Zhao", "Bowen Yu", "Feifan Song", "Hangyu Li", "Haiyang Yu", "Zhoujun Li", "Fei Huang", "Yongbin Li"]
year: 2023
venue: "EMNLP-2023"
source_type: "peer-reviewed"
paper_url: "https://arxiv.org/abs/2304.08244"
pdf_path: "papers/academic/li-2023-api-bank.pdf"
accessed: "2026-09-04"
review_status: "skimmed"
evidence_confidence: "high"
---

# li-2023-api-bank — API-Bank: A Comprehensive Benchmark for Tool-Augmented LLMs

## Why this source is in the corpus

Models the action interface through which a harness turns language outputs into state-changing operations.

## Research question

How well do models plan, retrieve, and invoke APIs, and what training data improves those skills?

## Harness mechanism studied

A runnable evaluation system with API retrieval, call generation, execution, and multi-turn dialogue state.

## Method and experimental setup

73 executable tools, 314 annotated dialogues with 753 calls for evaluation, plus 1,888 training dialogues spanning 2,138 APIs and 1,000 domains.

## Main findings

- API-Bank exposes separate failures in planning, API retrieval, and argument-level calls.
- Its training corpus improves selected models, but combines data generation and model adaptation with the harness.

## Mathematical content

Evaluation decomposes success by dialogue and call stages; no general theorem, and grader validity depends on executable API outcomes and annotations.

## Evidence quality and limitations

Small evaluation dialogue count, synthetic or annotated data, early models, and changing multiple components at once.

## Important implementation details

Evaluate tool agents at planning, selection, syntax, execution, and final-answer levels rather than one aggregate score.

## Claims this source supports

Tool use is a multi-stage reliability chain.

## Claims this source weakens or contradicts

One end-to-end success rate as an adequate diagnosis of tool failure.

## Relevance to a mathematics paper

Supports product-of-stage-success and error-propagation models.

## Connections to other sources

See the category and claim-level cross-references in [`INDEX.md`](INDEX.md) and the synthesis documents.

## Verification notes

Abstract, dataset counts, evaluation decomposition, training protocol, main results, and limitations checked in the local PDF. The archived file parsed successfully: 15 pages, 56821 extractable characters, SHA-256 `619006a4cfcdd1d2427e4d7cb0fd45d54803c16f238bdabde899d8e141958b92`.
