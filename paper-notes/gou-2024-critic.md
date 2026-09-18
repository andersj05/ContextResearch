---
title: "CRITIC: Large Language Models Can Self-Correct with Tool-Interactive Critiquing"
authors: ["Zhibin Gou", "Zhihong Shao", "Yeyun Gong", "Yelong Shen", "Yujiu Yang", "Nan Duan", "Weizhu Chen"]
year: 2024
venue: "ICLR-2024"
source_type: "peer-reviewed"
paper_url: "https://arxiv.org/abs/2305.11738"
pdf_path: "papers/academic/gou-2024-critic.pdf"
accessed: "2026-09-04"
review_status: "fully-reviewed"
evidence_confidence: "high"
---

# gou-2024-critic — CRITIC: Large Language Models Can Self-Correct with Tool-Interactive Critiquing

## Why this source is in the corpus

Supports analysis of inference-time search, feedback, stopping, and verifier error.

## Research question

Does grounding critique in external tools improve self-correction?

## Harness mechanism studied

A model drafts, critiques with search, calculator, or code tools, and revises from returned evidence.

## Method and experimental setup

Knowledge, math, and code tasks compare base, tool-free critique, tool use, and iterative CRITIC; hallucination detection is also evaluated.

## Main findings

- For ChatGPT, AmbigNQ rises from 51.8/64.3 EM/F1 to 62.0/74.9 and HotpotQA from 32.7/42.8 to 40.3/52.9.
- Removing tools reduces most gains; hallucination-detection AUROC is reported around 0.810-0.831.

## Mathematical content

Iterated revision is conditioned on external observations; confidence uses normalized correctness-token probabilities.

## Evidence quality and limitations

Only 500 examples per task in parts of the study, cached or truncated search, reproduced prompts, and tool information rather than introspection drives correction.

## Important implementation details

Separate intrinsic critique from evidence retrieval and log tool freshness, truncation, and revision transitions.

## Claims this source supports

Tool-grounded verification can correct errors that self-critique alone cannot.

## Claims this source weakens or contradicts

CRITIC as evidence that models intrinsically know when they are wrong.

## Relevance to a mathematics paper

Supports Bayesian or evidence-conditioned correction models with tool error.

## Connections to other sources

See the category and claim-level cross-references in [`INDEX.md`](INDEX.md) and the synthesis documents.

## Verification notes

Tables 1 and 5, tool ablation, search truncation, iterative protocol, and limitations checked in the local PDF. The archived file parsed successfully: 78 pages, 222891 extractable characters, SHA-256 `ed5cbff53c8ff550b72d6abba0d7e4d83c5d214d61d0fafde10cbe4bbfc31a5b`.
