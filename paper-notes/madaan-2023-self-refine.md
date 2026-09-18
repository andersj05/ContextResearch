---
title: "Self-Refine: Iterative Refinement with Self-Feedback"
authors: ["Aman Madaan", "Niket Tandon", "Prakhar Gupta", "Skyler Hallinan", "Luyu Gao", "Sarah Wiegreffe", "Uri Alon", "Nouha Dziri", "Shrimai Prabhumoye", "Yiming Yang", "Shashank Gupta", "Bodhisattwa Prasad Majumder", "Katherine Hermann", "Sean Welleck", "Amir Yazdanbakhsh", "Peter Clark"]
year: 2023
venue: "NeurIPS-2023"
source_type: "peer-reviewed"
paper_url: "https://arxiv.org/abs/2303.17651"
pdf_path: "papers/academic/madaan-2023-self-refine.pdf"
accessed: "2026-09-04"
review_status: "fully-reviewed"
evidence_confidence: "high"
---

# madaan-2023-self-refine — Self-Refine: Iterative Refinement with Self-Feedback

## Why this source is in the corpus

Supports analysis of inference-time search, feedback, stopping, and verifier error.

## Research question

Can one model iteratively critique and revise its own answer without external feedback?

## Harness mechanism studied

The same model generates an output, textual feedback, and a revision for up to four rounds.

## Method and experimental setup

Seven generation tasks compare initial and refined outputs using automatic or model-based metrics and ablations.

## Main findings

- Reported average gains are driven by selected subjective or directly checkable tasks; GPT-4 dialogue preference rises 25.4 to 74.6.
- Math changes are effectively null: 64.1 to 64.1, 74.8 to 75.0, and 92.9 to 93.1.

## Mathematical content

Feedback and revision are iterated model calls conditioned on every prior draft and critique, forming a stochastic dynamical system.

## Evidence quality and limitations

Metrics and judges are heterogeneous, no compute-matched stronger-initial-prompt baseline for every task, and intrinsic feedback may share the initial error.

## Important implementation details

Preserve each draft and critique, cap rounds, use independent judges, and compare with spending the same calls on fresh samples.

## Claims this source supports

Iterative feedback can improve some subjective or readily verifiable outputs.

## Claims this source weakens or contradicts

The approximately 20% average meme as evidence of broad reasoning or math self-correction.

## Relevance to a mathematics paper

Supplies an iterated stochastic map whose fixed points and error transitions can be studied.

## Connections to other sources

See the category and claim-level cross-references in [`INDEX.md`](INDEX.md) and the synthesis documents.

## Verification notes

Table 1, iterative equations, four-round cap, task-level results, judge setup, and limitations checked in the local PDF. The archived file parsed successfully: 54 pages, 125027 extractable characters, SHA-256 `81e44592314d80218ad108d3490cd0b84ba5962fefd5c84819987afd77a57087`.
