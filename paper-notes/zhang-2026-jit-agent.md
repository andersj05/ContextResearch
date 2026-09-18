---
title: "JIT-Agent: Scaling Harness Intelligence via Just-in-Time Harness Evolution"
authors: ["Guibin Zhang", "Leo Lu", "Fangzhou Xie", "Kang Zhu", "Junhao Wang", "Zhifei Xie", "Zhaochen Yu", "Zihang Liu", "Zhongxiang Sun", "Qiankun Li", "Yue Liao", "Heng Chang", "Xiaobin Hu", "Qibing Ren", "Wangchunshu Zhou", "Chuanrui Hu", "Yafeng Deng", "Shuicheng Yan"]
year: 2026
venue: "preprint"
source_type: "preprint"
paper_url: "https://arxiv.org/abs/2608.25593"
pdf_path: "papers/academic/zhang-2026-jit-agent.pdf"
accessed: "2026-09-04"
review_status: "skimmed"
evidence_confidence: "low"
---

# zhang-2026-jit-agent — JIT-Agent: Scaling Harness Intelligence via Just-in-Time Harness Evolution

## Why this source is in the corpus

Directly treats the harness, its optimization, or its runtime semantics as the object of study.

## Research question

Can a trained helper synthesize task-specific harnesses just in time for other models?

## Harness mechanism studied

A learned harness-intelligence model emits a fixed four-module protocol and can customize, repair, and distill prior configurations.

## Method and experimental setup

Cross-model evaluations on deep-search and agent benchmarks compare generated harnesses with mature runtimes.

## Main findings

- The paper reports DeepSeek-V4-Flash above GPT-5.6 by 9.1 points on DeepSearchQA and 4.3 on OdysseyBench under its configurations.
- GLM-5.2 gains up to 20.2 points, suggesting large task-model interactions.

## Mathematical content

Represents harness generation as conditional program or policy synthesis; headline deltas are empirical and provide no universal dominance theorem.

## Evidence quality and limitations

One-week-old preprint, many moving model and benchmark versions, author-trained helper, unclear independence, and no external replication.

## Important implementation details

Use a constrained module protocol and evaluate generated harnesses for validity, execution stability, transfer, and cost before deployment.

## Claims this source supports

Task-adaptive harness generation can be a learned capability separate from base-model scaling.

## Claims this source weakens or contradicts

Cross-benchmark deltas as proof that a helper generally dominates mature human harnesses.

## Relevance to a mathematics paper

Provides a conditional meta-policy formulation with model-harness interaction terms.

## Connections to other sources

See the category and claim-level cross-references in [`INDEX.md`](INDEX.md) and the synthesis documents.

## Verification notes

Abstract, four-module protocol, headline comparisons, cross-model sections, and stated limitations checked in the local PDF. The archived file parsed successfully: 24 pages, 72211 extractable characters, SHA-256 `5654012b4723f128c26908e0cce6a8c7afd58fe4a69c6688a9a88094bcfe9ebc`.
