---
title: "AutoFlow: Automated Workflow Generation for Large Language Model Agents"
authors: ["Zelong Li", "Shuyuan Xu", "Kai Mei", "Wenyue Hua", "Balaji Rama", "Om Raheja", "Hao Wang", "He Zhu", "Yongfeng Zhang"]
year: 2024
venue: "preprint"
source_type: "preprint"
paper_url: "https://arxiv.org/abs/2407.12821"
pdf_path: "papers/academic/li-2024-autoflow.pdf"
accessed: "2026-09-04"
review_status: "skimmed"
evidence_confidence: "medium"
---

# li-2024-autoflow — AutoFlow: Automated Workflow Generation for Large Language Model Agents

## Why this source is in the corpus

Directly studies reusable harness components, outer-loop optimization, self-modification, or the statistical controls needed to decide whether an update is a real improvement.

## Research question

Can an LM learn to generate a task-solving workflow in natural language while a frozen interpreter executes it?

## Harness mechanism studied

A workflow generator is trained with reinforcement learning to output procedural instructions, and a separate frozen interpreter instantiates the described control sequence.

## Method and experimental setup

AutoFlow samples candidate natural-language workflows, runs them through an interpreter on OpenAGI tasks, assigns task reward, and updates the generator; transfer is examined across executor models.

## Main findings

- Source-reported Table 1 gives Mixtral average scores of 0.1206 zero-shot and 0.1736 few-shot versus 0.3597 and 0.3442 for AutoFlow variants; Table 2 reports GPT-4 averages around 0.6415–0.6501 versus a strongest listed baseline around 0.6104.
- The claimed greater-than-40% relative Mixtral and greater-than-5% GPT-4 improvements are benchmark- and denominator-sensitive, with no sealed workflow-search test or full search-cost accounting verified here.

## Mathematical content

The generator maximizes expected reward E_{w~pi_theta}[R(Interpreter(w),D)] using policy-gradient-style optimization; no guarantee addresses interpreter mismatch or validation selection.

## Evidence quality and limitations

Preprint evidence on one benchmark family, limited model/task breadth, natural-language workflows with ambiguous execution semantics, adaptive reward use, and unreported total optimization cost constrain causal conclusions.

## Important implementation details

Train a workflow-producing LM against task rewards while keeping an interpreter fixed; serialize the learned procedure as text and have the interpreter call tools or models according to it.

## Claims this source supports

Workflow policy and execution engine can be decoupled, allowing persistent procedures to transfer across executor backbones.

## Claims this source weakens or contradicts

Reported gains do not establish that natural-language generation beats simpler hand-written or searched DSL workflows at matched total compute.

## Relevance to a mathematics paper

Exposes a two-level stochastic policy in which generator error and interpreter error can be separated in expected utility.

## Connections to other sources

See the category and claim-level cross-references in [`INDEX.md`](INDEX.md) and the synthesis documents.

## Verification notes

Local PDF abstract, model formulation, OpenAGI protocol, Tables 1–2, transfer discussion, and stated limitations were checked; experiments were not rerun. The archived file parsed successfully: 11 pages, 41379 extractable characters, SHA-256 `dee9185ced28099dcf689698051090a309bcaf584bf41dd95e7ec679c8bc2132`.
