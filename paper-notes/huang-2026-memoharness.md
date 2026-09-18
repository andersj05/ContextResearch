---
title: "MemoHarness: Agent Harnesses That Learn from Experience"
authors: ["Yue Huang", "Wenjie Wang", "Han Bao", "Yuchen Ma", "Xiaonan Luo", "Yi Nian", "Haomin Zhuang", "Zheyuan Liu", "Yue Zhao", "Xiangliang Zhang"]
year: 2026
venue: "preprint"
source_type: "preprint"
paper_url: "https://arxiv.org/abs/2607.14159"
pdf_path: "papers/academic/huang-2026-memoharness.pdf"
accessed: "2026-09-04"
review_status: "fully-reviewed"
evidence_confidence: "medium"
---

# huang-2026-memoharness — MemoHarness: Agent Harnesses That Learn from Experience

## Why this source is in the corpus

Directly treats the harness, its optimization, or its runtime semantics as the object of study.

## Research question

Can a harness learn reusable control policies from prior execution diagnoses?

## Harness mechanism studied

Six editable control dimensions, per-case diagnoses, a global pattern bank, and retrieval-conditioned adaptation without test labels or extra search.

## Method and experimental setup

Shell-agent, code-generation, and analytical-reasoning benchmarks with validation selection, cross-dataset and cross-model tests, and cost accounting.

## Main findings

- Reported mean success improves from 0.722 to 0.806 over the strongest fixed baseline, with selective rather than uniform transfer.
- Average success across held-out base models rises by 0.098; some training peaks regress before final selection.

## Mathematical content

Experience retrieval induces a conditional harness policy; empirical success is averaged over repeats, but no regret or generalization bound is given.

## Evidence quality and limitations

Recent author-built preprint, small held-out splits, correlated experience, multiple simultaneous control edits, and selective transfer.

## Important implementation details

Store case-level failure diagnoses separately from distilled global patterns and select final policy using validation rather than test feedback.

## Claims this source supports

Execution experience can adapt a harness without changing model weights.

## Claims this source weakens or contradicts

A single learned harness as universally transferable across tasks and models.

## Relevance to a mathematics paper

Invites contextual-bandit or meta-learning models with retrieval cost and transfer error.

## Connections to other sources

See the category and claim-level cross-references in [`INDEX.md`](INDEX.md) and the synthesis documents.

## Verification notes

Abstract, six-dimension Table 1, Figures 2-4, transfer Tables 2-4, cost analysis, and limitations checked in the local PDF. The archived file parsed successfully: 20 pages, 58792 extractable characters, SHA-256 `491dc8117001be021051c876e6dfef8617a5b6dd34a6030f765811c642ca7e9d`.
