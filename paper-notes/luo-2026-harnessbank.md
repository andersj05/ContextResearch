---
title: "HarnessBank: Semantic Gene-Bank Search with Gated Verification for Agent-Harness Self-Evolution"
authors: ["Xiaotian Luo", "Dizhan Xue", "Fengxingyu Wang", "Chuanrui Hu", "Yafeng Deng"]
year: 2026
venue: "preprint"
source_type: "preprint"
paper_url: "https://arxiv.org/abs/2607.13683"
pdf_path: "papers/academic/luo-2026-harnessbank.pdf"
accessed: "2026-09-04"
review_status: "skimmed"
evidence_confidence: "medium"
---

# luo-2026-harnessbank — HarnessBank: Semantic Gene-Bank Search with Gated Verification for Agent-Harness Self-Evolution

## Why this source is in the corpus

Directly studies reusable harness components, outer-loop optimization, self-modification, or the statistical controls needed to decide whether an update is a real improvement.

## Research question

Can a quality-diversity bank of harnesses improve cross-task transfer while enforcing validity, activation, significance, and gain gates?

## Harness mechanism studied

A QD archive indexes harnesses by where and why they work, recombines compatible artifacts, and admits candidates only after staged validity, activation, paired-significance, and gain tests.

## Method and experimental setup

HarnessBank evolves and recombines persistent harness modules, evaluates them on development tasks, applies a paired z-score gate, freezes accepted bank entries, and reports separate sealed-test results across six benchmark families.

## Main findings

- The paper reports sealed-test gains of +9.3 Terminal-Bench 2, +13.7 LiveCode, +11.7 OmniMath, +13.9 BrowseComp, +9.2 GDPval, +15.4 AppWorld, and preliminary +5.1 SWE; with K=3 runs it credits 4/5 sealed improvements versus DGM 1 and GEPA 0 in one comparison.
- DGM is -1.1 on OmniMath, SWE uses only n=26, QD versus gate effects are not isolated, and code is promised after acceptance rather than available for current reproduction.

## Mathematical content

The promotion statistic is a paired z score z=(mean paired gain)/(estimated standard error) with threshold z>=1.96, alongside hard validity and activation gates; K=3 is too small for reliable normal calibration and repeated proposals still require multiplicity control.

## Evidence quality and limitations

2026 preprint; tiny K, small SWE sample, optimizer/gate/QD components confounded, stronger Claude Opus 4.8 evolver with Qwen-3.6-27B executor, incomplete code release, and possible benchmark-specific bank indexing.

## Important implementation details

Store harnesses with task/failure descriptors and provenance, retrieve and recombine related entries, check executability and activation, estimate paired gains over common instances, apply the z and gain gates, then freeze a bank for sealed evaluation.

## Claims this source supports

Explicit artifact banking, activation checks, paired evaluation, and a sealed final split are stronger evidence practices than raw iterative score maximization.

## Claims this source weakens or contradicts

Weakens universal transfer claims: at least one comparator regresses, sample sizes are small, and the evidence does not isolate which safeguard creates the gain.

## Relevance to a mathematics paper

Provides a concrete paired estimator and acceptance threshold, while also illustrating low-n normal-approximation and repeated-testing hazards.

## Connections to other sources

See the category and claim-level cross-references in [`INDEX.md`](INDEX.md) and the synthesis documents.

## Verification notes

Local PDF objective, gate equations including Eq. 14, sealed-test tables, K=3 protocol, SWE sample note, comparator regressions, and limitations were checked; code/results were not reproduced. The archived file parsed successfully: 9 pages, 38846 extractable characters, SHA-256 `360efedc16753f6bfe062cd58b1e2f7e9984bbdd36a8cc79ed363af686aeaeb2`.
