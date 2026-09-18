---
title: "AutoAgents: A Framework for Automatic Agent Generation"
authors: ["Guangyao Chen", "Siwei Dong", "Yu Shu", "Ge Zhang", "Jaward Sesay", "Börje F. Karlsson", "Jie Fu", "Yemin Shi"]
year: 2023
venue: "IJCAI-2024"
source_type: "peer-reviewed"
paper_url: "https://arxiv.org/abs/2309.17288"
pdf_path: "papers/academic/chen-2023-autoagents.pdf"
accessed: "2026-09-04"
review_status: "skimmed"
evidence_confidence: "medium"
---

# chen-2023-autoagents — AutoAgents: A Framework for Automatic Agent Generation

## Why this source is in the corpus

Directly studies reusable harness components, outer-loop optimization, self-modification, or the statistical controls needed to decide whether an update is a real improvement.

## Research question

Can a fixed meta-pipeline dynamically create specialized agents and an execution plan for each user task?

## Harness mechanism studied

A planner generates roles and plans; Agent, Plan, and Action Observers critique the proposed team and monitor execution inside a hand-designed outer controller.

## Method and experimental setup

AutoAgents uses GPT-4-0613 for dynamic role generation, planning, observation, and execution; it evaluates open-domain QA and creative tasks with LM and human preferences plus a small observer ablation.

## Main findings

- Table 2 reports 76.3% LM-judge and 62.5% human preference over a GPT-4 baseline on open QA; creative versus standard settings are 82.0/85.3 versus 74.6/77.0.
- The observer ablation uses only n=20 and reports full 90 versus 87–89 without individual observers, with no uncertainty, so it does not establish distinct causal value for each role.

## Mathematical content

The pipeline performs sequential conditional generation under a fixed control graph; preference rates are sample proportions, but confidence intervals, inter-rater models, and equal-call cost normalization are absent.

## Evidence quality and limitations

Every component uses the same GPT-4 version, agent count and calls exceed the baseline, subjective judging may share model bias, the outer template is human-written, and the ablation sample is tiny.

## Important implementation details

Generate a role roster and plan from the task, run specialized agents, have three observer roles critique agents/plans/actions, revise when triggered, and aggregate a final answer under a fixed controller.

## Claims this source supports

Task-conditioned team composition and runtime oversight are practical harness mechanisms.

## Claims this source weakens or contradicts

Dynamic role names and positive preferences do not show autonomous architecture discovery or improvement after accounting for extra GPT-4 calls.

## Relevance to a mathematics paper

Preference-rate uncertainty and factorial observer ablations are the natural mathematical analyses missing from the reported study.

## Connections to other sources

See the category and claim-level cross-references in [`INDEX.md`](INDEX.md) and the synthesis documents.

## Verification notes

Local PDF architecture, experimental protocol, Table 2, creative comparison, n=20 observer ablation, and limitations were checked; preference trials were not replicated. The archived file parsed successfully: 30 pages, 82295 extractable characters, SHA-256 `eb28d6d380b88dbdaabaaea10c9e55dac04706f903ccac22830f462f043385f6`.
