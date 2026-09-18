---
title: "Symbolic Learning Enables Self-Evolving Agents"
authors: ["Wangchunshu Zhou", "Yixin Ou", "Shengwei Ding", "Long Li", "Jialong Wu", "Tiannan Wang", "Jiamin Chen", "Shuai Wang", "Xiaohua Xu", "Ningyu Zhang", "Huajun Chen", "Yuchen Eleanor Jiang"]
year: 2024
venue: "preprint"
source_type: "preprint"
paper_url: "https://arxiv.org/abs/2406.18532"
pdf_path: "papers/academic/zhou-2024-symbolic-learning.pdf"
accessed: "2026-09-04"
review_status: "skimmed"
evidence_confidence: "medium"
---

# zhou-2024-symbolic-learning — Symbolic Learning Enables Self-Evolving Agents

## Why this source is in the corpus

Directly studies reusable harness components, outer-loop optimization, self-modification, or the statistical controls needed to decide whether an update is a real improvement.

## Research question

Can prompts, tools, and workflow code be optimized together using language-model analogues of loss, gradients, and optimizers?

## Harness mechanism studied

A language loss critic describes execution failures, a language gradient assigns blame to modules, and a language optimizer edits selected symbolic components.

## Method and experimental setup

The framework begins from an existing agent, collects trajectories and evaluator feedback, propagates textual critiques through the computation graph, and applies bounded edits to prompts, tools, or pipeline structure.

## Main findings

- Source-reported Table 2 gives an average of 3.8 on software tasks versus 1.6 for GPTs and 2.4 for Agents; Table 3 reports creative-task averages around 6.9 with GPT-3.5 and 7.4 with GPT-4, above listed baselines.
- The subjective tasks rely on LM graders, initialization from an existing agent is material, and the study does not identify whether loss wording, blame routing, or extra calls caused the gain.

## Mathematical content

The method borrows chain-rule notation by propagating textual gradients through a symbolic graph and applies an update theta_{t+1}=Optimizer(theta_t,g_t); these are metaphors/algorithms, not numerical derivatives or convergence theorems.

## Evidence quality and limitations

LM-generated critiques can be inconsistent, changes may destabilize other modules, evaluator and optimizer can share biases, subjective scores lack strong calibration, and compute is not matched to simpler retry baselines.

## Important implementation details

Log module inputs and outputs, ask a critic for a textual loss, backpropagate module-specific feedback through dependencies, let an optimizer rewrite target artifacts, and reevaluate the revised agent.

## Claims this source supports

Trace-localized feedback can coordinate edits across several harness artifact types rather than optimize a prompt alone.

## Claims this source weakens or contradicts

Calling text a gradient does not import gradient-descent guarantees, and LM-judge gains are vulnerable to shared-model preference and objective hacking.

## Relevance to a mathematics paper

Useful for formalizing a directed computation graph and distinguishing true derivatives from heuristic directional edit proposals.

## Connections to other sources

See the category and claim-level cross-references in [`INDEX.md`](INDEX.md) and the synthesis documents.

## Verification notes

Local PDF framework sections, update notation, Tables 1–3, ablations, and limitations were checked; subjective evaluations were not reproduced. The archived file parsed successfully: 16 pages, 58099 extractable characters, SHA-256 `7bde2483cab9536f5dd93ce789026287bf5f8dd47077d66f1f4fedca9a376f10`.
