---
title: "Offline Training of Language Model Agents with Functions as Learnable Weights"
authors: ["Shaokun Zhang", "Jieyu Zhang", "Jiale Liu", "Linxin Song", "Chi Wang", "Ranjay Krishna", "Qingyun Wu"]
year: 2024
venue: "ICML-2024"
source_type: "peer-reviewed"
paper_url: "https://arxiv.org/abs/2402.11359"
pdf_path: "papers/academic/zhang-2024-agentoptimizer.pdf"
accessed: "2026-09-04"
review_status: "skimmed"
evidence_confidence: "high"
---

# zhang-2024-agentoptimizer — Offline Training of Language Model Agents with Functions as Learnable Weights

## Why this source is in the corpus

Directly studies reusable harness components, outer-loop optimization, self-modification, or the statistical controls needed to decide whether an update is a real improvement.

## Research question

Can an LM improve an agent by editing the functions that define its actions and control logic?

## Harness mechanism studied

An optimizer agent proposes add, revise, remove, and rollback operations over Python functions, using execution results on a small development set as feedback.

## Method and experimental setup

AgentOptimizer alternates candidate function-library edits with evaluation, accepts useful versions, rolls back failures, and stops early when development performance ceases to improve; GPT-4 and ReAct-style agents are tested on MATH, GAIA, and TabMWP.

## Main findings

- Table 1 reports improvement in 11 of 14 MATH model/type cells, including GPT-4+ number 56.3→67.5 and ReAct pre-calculus 53.8→62.5, but also regressions such as GPT-4+ algebra 66.3→65.0 and ReAct algebra 83.8→82.5.
- GAIA uses only 10 optimization examples and 100 test examples, rising 16→23 for GPT-4+ and 12→18 for ReAct; TabMWP rises 51→56 and 59→70, so results are promising but noisy and adaptively selected.

## Mathematical content

The procedure performs greedy black-box maximization of an empirical score J(F;D_dev) over a variable function set F, with rollback and early stopping but no multiple-testing correction or convergence bound.

## Evidence quality and limitations

Development sets are extremely small, model and agent styles vary by cell, regressions occur, search cost and variance are not fully quantified, and generated functions introduce execution and security risks.

## Important implementation details

Represent actions and control behaviors as editable Python functions, propose one structured edit at a time, run task evaluations, keep or roll back the version, and terminate after a fixed patience window.

## Claims this source supports

A harness function library can be treated as mutable program state and improved through execution-grounded edits.

## Claims this source weakens or contradicts

Not every domain improves, and tiny repeated development sets undermine claims that accepted edits generalize reliably.

## Relevance to a mathematics paper

A useful case study in adaptive model selection over program versions; selection optimism and sequential stopping can be analyzed directly.

## Connections to other sources

See the category and claim-level cross-references in [`INDEX.md`](INDEX.md) and the synthesis documents.

## Verification notes

Local PDF algorithm, experimental setup, Table 1, ablations, and discussion were checked; quoted changes are source-reported and not rerun. The archived file parsed successfully: 22 pages, 87554 extractable characters, SHA-256 `3201906f4a3de7ea2b10cf3972210cb6a3c7038defce13e74580609cd7a63d2c`.
