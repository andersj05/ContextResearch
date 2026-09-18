---
title: "Godel Agent: A Self-Referential Agent Framework for Recursive Self-Improvement"
authors: ["Xunjian Yin", "Xinyi Wang", "Liangming Pan", "Li Lin", "Xiaojun Wan", "William Yang Wang"]
year: 2024
venue: "preprint"
source_type: "preprint"
paper_url: "https://arxiv.org/abs/2410.04444"
pdf_path: "papers/academic/yin-2024-godel-agent.pdf"
accessed: "2026-09-04"
review_status: "skimmed"
evidence_confidence: "medium"
---

# yin-2024-godel-agent — Godel Agent: A Self-Referential Agent Framework for Recursive Self-Improvement

## Why this source is in the corpus

Directly studies reusable harness components, outer-loop optimization, self-modification, or the statistical controls needed to decide whether an update is a real improvement.

## Research question

Can an agent edit both its policy and its own improvement routine without a hand-specified edit language?

## Harness mechanism studied

A self-referential optimizer receives the current policy, current improvement procedure, reward feedback, and task, then emits unconstrained code/text revisions to both.

## Method and experimental setup

The paper contrasts a bounded base variant with a freer self-referential variant, runs up to thirty improvement iterations on four reasoning tasks plus Game of 24, and uses GPT-4o as optimizer with GPT-3.5-class execution in key settings.

## Main findings

- Table 1 reports Gödel-base DROP 80.9±0.8, MGSM 64.2±3.4, MMLU 70.9±3.1, GPQA 34.9±3.3 versus Gödel-free 90.5±1.8, 90.6±2.0, 87.9±2.2, 55.7±3.1; Game of 24 reaches 100% in the reported run.
- The free variant has a broader edit space and stronger optimizer/executor asymmetry, validation subsets are small, and the claimed roughly $15 search cost versus ADAS $300 is not a controlled quality-equivalent comparison.

## Mathematical content

The recursive state update is (pi_{t+1},I_{t+1})=I_t(pi_t,I_t,r_t,g); it is inspired by Gödel machines but supplies no proof of utility improvement or self-rewrite optimality.

## Evidence quality and limitations

Preprint; small repeatedly queried validation subsets; unconstrained edits are hard to sandbox; strong external optimizer; no sealed test across improvement rounds; current LMs may imitate rather than invent algorithms.

## Important implementation details

Serialize the executor policy and improvement code, provide reward and traces to the improver, allow edits to both artifacts, run the successor on validation tasks, and repeat under external evaluation.

## Claims this source supports

Self-reference can be implemented as persistent dual state over policy and optimizer, producing large reported gains in some reasoning tasks.

## Claims this source weakens or contradicts

The name does not confer the proof obligations of a Gödel machine, and observed gains remain dependent on fixed external rewards, models, and sandboxing.

## Relevance to a mathematics paper

Offers a concise dynamical-system equation for recursive self-editing and highlights that empirical self-reference is not proof-carrying optimal self-modification.

## Connections to other sources

See the category and claim-level cross-references in [`INDEX.md`](INDEX.md) and the synthesis documents.

## Verification notes

Local PDF update equation, methods, Table 1, Game-of-24 and cost discussions, and limitations were checked; no independent reproduction occurred. The archived file parsed successfully: 24 pages, 79105 extractable characters, SHA-256 `f3e8e090d16bc53048cf9a2f20557c217ea0d52ea1d33e496f7ee1be07241a95`.
