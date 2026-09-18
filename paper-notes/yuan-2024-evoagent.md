---
title: "EvoAgent: Towards Automatic Multi-Agent Generation via Evolutionary Algorithms"
authors: ["Siyu Yuan", "Kaitao Song", "Jiangjie Chen", "Xu Tan", "Dongsheng Li", "Deqing Yang"]
year: 2024
venue: "NAACL-2025-Long"
source_type: "peer-reviewed"
paper_url: "https://arxiv.org/abs/2406.14228"
pdf_path: "papers/academic/yuan-2024-evoagent.pdf"
accessed: "2026-09-04"
review_status: "skimmed"
evidence_confidence: "high"
---

# yuan-2024-evoagent — EvoAgent: Towards Automatic Multi-Agent Generation via Evolutionary Algorithms

## Why this source is in the corpus

Directly studies reusable harness components, outer-loop optimization, self-modification, or the statistical controls needed to decide whether an update is a real improvement.

## Research question

Can a single-agent seed be expanded into a stronger multi-agent team by evolutionary role and skill diversification?

## Harness mechanism studied

An LM applies mutation and crossover to agent roles, skills, prompts, and interaction descriptions while a task evaluator selects teams around a seed agent.

## Method and experimental setup

EvoAgent generates candidate collaborators from a seed system, evolves role and capability descriptions over generations, and evaluates resulting teams on reasoning, writing, games, tool use, and ScienceWorld.

## Main findings

- Table 1 reports GPT-4 SPP 64.5/79.2/78.35 and AutoAgents 69.0/82.0/83.56 versus EvoAgent 77.0/84.4/84.53 on logic, writing, and Codenames with n=200/100/50; ScienceWorld rises 17.12→19.02 for GPT-3.5 and 27.97→30.42 for GPT-4.
- The paper lacks an equal-call ensemble or randomly diversified-team control, so added agents and inference compute remain plausible explanations.

## Mathematical content

Candidate teams are selected by empirical fitness under mutation/crossover operators; the evolutionary loop has no convergence result and does not estimate a compute-adjusted treatment effect.

## Evidence quality and limitations

Small and heterogeneous samples, LM judging for open-ended outputs, more agents and calls than single-agent baselines, prompt-dependent mutations, and limited variance reporting prevent clean mechanism attribution.

## Important implementation details

Start from a working agent, prompt an evolver to create complementary role/skill variants, crossover useful traits, instantiate a multi-agent collaboration, score it, and retain high-fitness team descriptions.

## Claims this source supports

Persistent role and interaction specifications can be evolved and yield positive results in several domains.

## Claims this source weakens or contradicts

The evidence does not separate evolutionary search from ordinary ensembling, extra sampling, or expert-designed seed quality.

## Relevance to a mathematics paper

Motivates cost-normalized fitness and ablations comparing evolutionary selection with exchangeable random-team baselines.

## Connections to other sources

See the category and claim-level cross-references in [`INDEX.md`](INDEX.md) and the synthesis documents.

## Verification notes

Local PDF method, Table 1, ScienceWorld results, sample sizes, ablations, and limitations were checked; scores are source-reported. The archived file parsed successfully: 26 pages, 91208 extractable characters, SHA-256 `2f7d490bf5d56f47e923302c78b07acf61c294c04c4bd0b8eb8f6e71127ca6f4`.
