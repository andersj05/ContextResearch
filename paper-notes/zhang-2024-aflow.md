---
title: "AFlow: Automating Agentic Workflow Generation"
authors: ["Jiayi Zhang", "Jinyu Xiang", "Zhaoyang Yu", "Fengwei Teng", "Xionghui Chen", "Jiaqi Chen", "Mingchen Zhuge", "Xin Cheng", "Sirui Hong", "Jinlin Wang", "Bingnan Zheng", "Bang Liu", "Yuyu Luo", "Chenglin Wu"]
year: 2024
venue: "ICLR-2025-Oral"
source_type: "peer-reviewed"
paper_url: "https://arxiv.org/abs/2410.10762"
pdf_path: "papers/academic/zhang-2024-aflow.pdf"
accessed: "2026-09-04"
review_status: "skimmed"
evidence_confidence: "high"
---

# zhang-2024-aflow — AFlow: Automating Agentic Workflow Generation

## Why this source is in the corpus

Directly studies reusable harness components, outer-loop optimization, self-modification, or the statistical controls needed to decide whether an update is a real improvement.

## Research question

Can common agent workflows be discovered efficiently by Monte Carlo tree search over a constrained operator language?

## Harness mechanism studied

A workflow is code assembled from seven reusable operator types; MCTS proposes edits, evaluates candidates repeatedly, and updates node values from task scores.

## Method and experimental setup

AFlow runs twenty search rounds with five evaluations per workflow, using an LM to propose workflow code within a fixed operator library, then selects the best validation design for downstream tests.

## Main findings

- Table 1 reports, with the same GPT-4o-mini executor, IO 72.8, CoT 74.7, CoT-SC 76.0, ADAS 67.2, and AFlow 80.3 averaged across the reported tasks.
- On HumanEval the selected workflow costs $0.0291 per evaluation versus GPT-4o IO at $0.6371, about 4.55%, but that comparison excludes AFlow’s offline search expenditure and therefore is not total-cost evidence.

## Mathematical content

The objective is W-star=argmax_W G(W,T); MCTS uses empirical mean rewards and an exploration bonus of UCT form to balance candidate expansion and exploitation, without a post-selection risk bound.

## Evidence quality and limitations

Search cost is omitted from deployment-cost headlines; the operator library and proposer prompt are human-designed; development feedback is reused; task-specific workflows and evaluator noise limit external validity.

## Important implementation details

Expose generation, ensemble, review, revision, routing, voting, and formatting operators; have an LM emit workflow code, execute candidates several times, update an MCTS tree, and deploy the highest validation scorer.

## Claims this source supports

A constrained workflow DSL can yield strong fixed-model designs with cheaper runtime than simply calling a frontier model.

## Claims this source weakens or contradicts

AFlow’s own same-model results contradict an assumption that open-ended ADAS code search is necessarily better; its price headline does not include discovery cost.

## Relevance to a mathematics paper

Provides a finite structured search space and UCT-style allocation rule suitable for sample-complexity and amortization analysis.

## Connections to other sources

See the category and claim-level cross-references in [`INDEX.md`](INDEX.md) and the synthesis documents.

## Verification notes

Local PDF abstract, algorithm, objective equation, Table 1, cost table, search-budget details, and limitations were checked; all effects remain source-reported. The archived file parsed successfully: 38 pages, 116766 extractable characters, SHA-256 `9be15f695f11dd5bc634c1c026bd2270eff3d3c4a53c4d9b51c012b7bd03d521`.
