---
title: "AutoHarness: Improving LLM Agents by Automatically Synthesizing a Code Harness"
authors: ["Xinghua Lou", "Miguel Lázaro-Gredilla", "Antoine Dedieu", "Carter Wendelken", "Wolfgang Lehrach", "Kevin P. Murphy"]
year: 2026
venue: "preprint"
source_type: "preprint"
paper_url: "https://arxiv.org/abs/2603.03329"
pdf_path: "papers/academic/lou-2026-autoharness.pdf"
accessed: "2026-09-04"
review_status: "skimmed"
evidence_confidence: "medium"
---

# lou-2026-autoharness — AutoHarness: Improving LLM Agents by Automatically Synthesizing a Code Harness

## Why this source is in the corpus

Directly studies reusable harness components, outer-loop optimization, self-modification, or the statistical controls needed to decide whether an update is a real improvement.

## Research question

Can an LM synthesize an environment-specific action harness that guarantees legal interaction and improves a cheaper model’s gameplay?

## Harness mechanism studied

A Thompson-sampling tree search generates executable harness code from environment feedback; a rejection filter discards candidates producing invalid actions before persistent deployment.

## Method and experimental setup

AutoHarness builds one text-game harness per environment, tests generated programs across long rollouts and seeds, and compares Flash plus harness with stronger models on 32 two-player and additional single-player TextArena games.

## Main findings

- The paper reports 100% legal actions on novel 1,000-step rollouts over ten seeds after an average 14.5 search iterations; on 32 two-player games Flash+harness wins 9/16 against Pro and scores 56.3 versus 38.2 overall, while one-player reward is 0.745 versus Pro 0.707 and Flash 0.673.
- In the harness-as-policy comparison it reports 0.870 versus GPT-5.2-High 0.844, yet head-to-head outcomes are only 3 wins/8 ties versus GPT’s 5 wins, with unequal repetitions and one harness per game.

## Mathematical content

Search maintains a posterior or empirical success estimate for tree nodes and uses Thompson sampling to allocate expansions; validity is a hard acceptance predicate, but no posterior-correctness or generalization guarantee follows from the generated tests.

## Evidence quality and limitations

2026 preprint; narrow text-game setting, per-environment harnesses, unequal replication and inference budgets, code-generation safety, no cross-game persistent transfer, and ambiguous aggregate versus head-to-head conclusions.

## Important implementation details

Generate environment wrapper/policy code, execute candidate tests, reject any invalid-action program, update tree-node statistics from scores, sample expansions with Thompson sampling, and freeze a successful harness for later model calls.

## Claims this source supports

Automated environment adapters can enforce syntax/legality and let a cheaper fixed model compete with a stronger one.

## Claims this source weakens or contradicts

Weakens model-substitution headlines because pairwise wins do not match the aggregate reward ordering and each harness is specialized to one game.

## Relevance to a mathematics paper

Combines Bayesian search allocation with a hard safety/validity constraint; multiple-comparison and hierarchical game-level uncertainty remain open.

## Connections to other sources

See the category and claim-level cross-references in [`INDEX.md`](INDEX.md) and the synthesis documents.

## Verification notes

Local PDF algorithm, legality experiment, two-player and single-player tables, harness-as-policy comparison, search-iteration statistics, and limitations were checked; games were not rerun. The archived file parsed successfully: 21 pages, 44939 extractable characters, SHA-256 `8399c0a6a76a38c1a96804c88d0bac69286fe52ba3f255cba9175e3882fecf19`.
