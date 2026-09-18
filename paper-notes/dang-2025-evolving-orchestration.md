---
title: "Multi-Agent Collaboration via Evolving Orchestration"
authors: ["Yufan Dang", "Chen Qian", "Xueheng Luo", "Jingru Fan", "Zihao Xie", "Ruijie Shi", "Weize Chen", "Cheng Yang", "Xiaoyin Che", "Ye Tian", "Xuantang Xiong", "Lei Han", "Zhiyuan Liu", "Maosong Sun"]
year: 2025
venue: "NeurIPS-2025"
source_type: "peer-reviewed"
paper_url: "https://arxiv.org/abs/2505.19591"
pdf_path: "papers/academic/dang-2025-evolving-orchestration.pdf"
accessed: "2026-09-04"
review_status: "skimmed"
evidence_confidence: "high"
---

# dang-2025-evolving-orchestration — Multi-Agent Collaboration via Evolving Orchestration

## Why this source is in the corpus

Directly studies reusable harness components, outer-loop optimization, self-modification, or the statistical controls needed to decide whether an update is a real improvement.

## Research question

Can policy-gradient learning adapt multi-agent orchestration while penalizing execution cost?

## Harness mechanism studied

A controller chooses which model/role acts and how messages flow at each step, receiving terminal task reward minus a weighted communication/inference cost.

## Method and experimental setup

The paper trains orchestration policies with REINFORCE on Mimas and Titan configurations, comparing fixed, monolithic, and heterogeneous model pools and reporting task-level and aggregate changes.

## Main findings

- Table 1 reports Mimas heterogeneous 0.6273→0.6324, only +0.0051, while monolithic rises 0.5068→0.6147; Titan heterogeneous rises 0.6893→0.7731 and monolithic 0.6671→0.7453.
- Some task cells regress, including Mimas GSM 0.56→0.54 and SRDD 0.6653→0.6266, so average improvement does not imply safe per-task updates.

## Mathematical content

Actions follow a_t~pi_theta(S_t,tau), with return R-lambda C_T and a likelihood-ratio estimator sum_t grad log pi_theta(a_t|S_t) times return; variance and distribution shift are not theoretically controlled.

## Evidence quality and limitations

Reward scales and lambda determine behavior, REINFORCE is noisy, pools and budgets differ, some cells regress, and the learned policy is tested on a limited benchmark mix rather than long-lived deployment.

## Important implementation details

Encode orchestration state and candidate agents, sample routing/role decisions stepwise, execute the team, measure terminal quality and cumulative cost, and update controller parameters from trajectory returns.

## Claims this source supports

Orchestration itself can be learned and cost regularization can be built into the optimization objective.

## Claims this source weakens or contradicts

Weakens monotonic self-improvement claims because aggregate wins conceal negative task cells and the heterogeneous-pool effect can be tiny.

## Relevance to a mathematics paper

Supplies an explicit constrained-return objective and policy-gradient estimator suitable for variance and safe-improvement analysis.

## Connections to other sources

See the category and claim-level cross-references in [`INDEX.md`](INDEX.md) and the synthesis documents.

## Verification notes

Local PDF objective and estimator equations, Table 1, task-level breakdown, cost ablations, and limitations were checked; no training run was replicated. The archived file parsed successfully: 28 pages, 83746 extractable characters, SHA-256 `244c86ebd95a9fa7ca06539854186ea3dcdbf794ceb6e7827fff6e642e647bf6`.
