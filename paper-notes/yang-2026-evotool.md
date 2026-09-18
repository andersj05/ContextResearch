---
title: "EVOTOOL: Self-Evolving Tool-Use Policy Optimization in LLM Agents via Blame-Aware Mutation and Diversity-Aware Selection"
authors: ["Shuo Yang", "Caren Han", "Xueqi Ma", "Yan Li", "Mohammad Reza Ghasemi Madani", "Eduard Hovy"]
year: 2026
venue: "ACL-2026-Long"
source_type: "peer-reviewed"
paper_url: "https://aclanthology.org/2026.acl-long.2016/"
pdf_path: "papers/academic/yang-2026-evotool.pdf"
accessed: "2026-09-04"
review_status: "skimmed"
evidence_confidence: "high"
---

# yang-2026-evotool — EVOTOOL: Self-Evolving Tool-Use Policy Optimization in LLM Agents via Blame-Aware Mutation and Diversity-Aware Selection

## Why this source is in the corpus

Directly studies reusable harness components, outer-loop optimization, self-modification, or the statistical controls needed to decide whether an update is a real improvement.

## Research question

Can execution feedback localize which part of a tool-use agent should mutate and preserve diverse task-specific winners?

## Harness mechanism studied

Four fixed modules are evolved through blame-aware mutation; an instance-win archive retains candidates that solve complementary validation examples instead of only the highest mean scorer.

## Method and experimental setup

EVOTOOL logs trajectories, asks a critic to assign module blame, mutates the selected prompt/policy, scores candidates, and uses diversity-aware selection across tool-use benchmarks and executor backbones.

## Main findings

- Table 1 reports GPT-4.1 70.6 versus DRAFT 64.9, +5.7 points, and Qwen-8B 57.0 versus 51.8, +5.2; Table 2 reports Qwen static 48.6, random mutation 39.5, monolithic mutation 49.1, and full EVOTOOL 57.0.
- These ablations support localized/diverse search, but there are no confidence intervals and LM-assigned blame is not validated against causal module interventions.

## Mathematical content

The agent is a composition Pi of four modules; optimization maximizes empirical reward while archive coverage counts per-instance wins, a discrete multiobjective heuristic without convergence or safe-improvement guarantees.

## Evidence quality and limitations

ACL 2026 but recent; fixed four-module scaffold limits generality, evaluator and blame model can share bias, exact search costs and seeds are incomplete, and instance-level selection can overfit validation items.

## Important implementation details

Store module prompts separately, trace inputs/outputs, generate a blamed component and mutation, run each candidate, retain designs with novel per-instance wins, and deploy an archive-selected composite policy.

## Claims this source supports

Localized trace feedback and diversity preservation can outperform random or monolithic edits in a controlled modular scaffold.

## Claims this source weakens or contradicts

The study does not prove that textual blame is causally correct or that the full method improves every backbone/task under sealed evaluation.

## Relevance to a mathematics paper

Provides a set-coverage/Pareto interpretation of instance-win diversity and invites causal blame calibration and adaptive-selection correction.

## Connections to other sources

See the category and claim-level cross-references in [`INDEX.md`](INDEX.md) and the synthesis documents.

## Verification notes

Local PDF formal composition/objective, Tables 1–2, mutation/archive ablations, protocol, and limitations were checked; no independent rerun was conducted. The archived file parsed successfully: 20 pages, 69102 extractable characters, SHA-256 `d978bbe7dff41d9e39daa9118b1495c21057273abaa0b686099c8ad1e04aa724`.
