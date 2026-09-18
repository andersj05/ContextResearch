---
title: "Self-Harness: Harnesses That Improve Themselves"
authors: ["Hangfan Zhang", "Shao Zhang", "Kangcong Li", "Chen Zhang", "Yang Chen", "Yiqun Zhang", "Lei Bai", "Shuyue Hu"]
year: 2026
venue: "preprint"
source_type: "preprint"
paper_url: "https://arxiv.org/abs/2606.09498"
pdf_path: "papers/academic/zhang-2026-self-harness.pdf"
accessed: "2026-09-04"
review_status: "skimmed"
evidence_confidence: "high"
---

# zhang-2026-self-harness — Self-Harness: Harnesses That Improve Themselves

## Why this source is in the corpus

Directly studies reusable harness components, outer-loop optimization, self-modification, or the statistical controls needed to decide whether an update is a real improvement.

## Research question

Can a fixed model improve a persistent harness through verifier-grounded edits while requiring both in-sample and held-out non-degradation?

## Harness mechanism studied

The same model proposes bounded harness edits from failure traces; a promotion gate accepts a candidate only when in-sample and nominal held-out deltas are nonnegative and at least one is positive.

## Method and experimental setup

Self-Harness allows two candidate attempts per round, executes them on task splits, applies the conjunctive gate, persists accepted instructions/tools/policies, and evaluates Terminal-Bench 2, SWE, and AppWorld across three models.

## Main findings

- Table 1 reports Terminal-Bench 2 MiniMax 40.5→61.9, Qwen 23.8→38.1, GLM 42.9→57.1; SWE 34.8→40.9, 18.2→39.4, 48.5→50.0; AppWorld 45.6→55.0, 20.0→44.4, 41.1→77.8.
- The nominal held-out split is consulted at every promotion gate, so it is repeatedly used validation rather than a sealed final test; large gains therefore do not quantify unbiased prospective deployment benefit.

## Mathematical content

Acceptance requires Delta_in>=0, Delta_ho>=0, and max(Delta_in,Delta_ho)>0; repeated adaptive testing makes the observed maximum and acceptance event selection-biased despite the two-split rule.

## Evidence quality and limitations

2026 preprint; only two proposals per round, repeated held-out reuse, no confidence intervals or adaptive-testing correction, model-specific tasks, external verifier dependence, and bounded human-designed edit language.

## Important implementation details

Collect verifier failures, ask the frozen executor model to propose a bounded artifact edit, run both splits, apply the conjunctive gate, persist only accepted versions, and repeat.

## Claims this source supports

A single fixed model can propose and reuse harness changes that correlate with large benchmark gains under a conservative-looking gate.

## Claims this source weakens or contradicts

Weakens the interpretation of held-out validation: a split loses test status once queried for every adaptive promotion, so the headline is not sealed-test self-improvement.

## Relevance to a mathematics paper

An unusually clear example of sequential selection on two empirical means and the need for reusable-holdout, confidence-sequence, or final-lockbox methods.

## Connections to other sources

See the category and claim-level cross-references in [`INDEX.md`](INDEX.md) and the synthesis documents.

## Verification notes

Local PDF update loop, exact promotion rule, Table 1, per-round protocol, and limitations were checked; the evidence is provisional and not independently rerun. The archived file parsed successfully: 31 pages, 70957 extractable characters, SHA-256 `eb38452b5d357499ff3a2f7aa8bd7b8c1c1409dbafadaff3624071b2f7b1b302`.
