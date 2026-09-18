---
title: "Language Agents as Optimizable Graphs"
authors: ["Mingchen Zhuge", "Wenyi Wang", "Louis Kirsch", "Francesco Faccio", "Dmitrii Khizbullin", "Jürgen Schmidhuber"]
year: 2024
venue: "ICML-2024"
source_type: "peer-reviewed"
paper_url: "https://arxiv.org/abs/2402.16823"
pdf_path: "papers/academic/zhuge-2024-gptswarm.pdf"
accessed: "2026-09-04"
review_status: "skimmed"
evidence_confidence: "high"
---

# zhuge-2024-gptswarm — Language Agents as Optimizable Graphs

## Why this source is in the corpus

Directly studies reusable harness components, outer-loop optimization, self-modification, or the statistical controls needed to decide whether an update is a real improvement.

## Research question

Can a multi-agent workflow be optimized as a computational graph rather than hand-designed?

## Harness mechanism studied

Agents are graph nodes and communication choices are differentiable or stochastic edges; node prompts and edge probabilities are optimized with task reward.

## Method and experimental setup

GPTSwarm defines a graph G=(N,E,F,o), applies REINFORCE-style updates to edge distributions, and evaluates graph variants on Mini Crosswords, HumanEval, and GAIA, with separate node and edge optimization studies.

## Main findings

- Mini Crosswords rises from 0.465±0.0509 to 0.575±0.0275 after ten iterations, but the same 20 puzzles are used for optimization and evaluation; HumanEval rises 0.76→0.88±0.007 while repeatedly optimizing over the full public set.
- The GAIA score 18.45 versus GPT-4-Turbo 9.70 uses no node or edge optimization, but a seven-sample Tree-of-Thought self-consistency system taking about 415 seconds versus 71 seconds; HumanEval optimization costs $28.46 versus $1.61 without optimization.

## Mathematical content

For edge parameters theta, the paper uses a score-function gradient estimator E[R(G) grad_theta log p_theta(G)] and stochastic gradient ascent; high variance and biased reuse of evaluation tasks are not corrected.

## Evidence quality and limitations

Public evaluation items are reused adaptively, sample sizes are tiny, compute is unequal, GAIA does not test the advertised optimizer, and reported gains cannot distinguish search from ensembling or extra inference.

## Important implementation details

Encode candidate agents and message routes as a graph, sample discrete edge configurations, execute full workflows, assign scalar task reward, and update edge logits; optional textual optimization edits node prompts.

## Claims this source supports

Graph topology is a genuine optimizable harness variable and policy-gradient machinery can search it.

## Claims this source weakens or contradicts

The most memed headline results are confounded by train-on-test reuse and unequal compute; they are not clean evidence of general graph-optimization benefit.

## Relevance to a mathematics paper

Contains the clearest likelihood-ratio estimator in this family and exposes the variance, sample reuse, and cost terms a rigorous analysis must include.

## Connections to other sources

See the category and claim-level cross-references in [`INDEX.md`](INDEX.md) and the synthesis documents.

## Verification notes

Local PDF formal graph definition, optimization equations, Tables and plots for all three benchmarks, timing/cost appendix, and protocol text were checked; no replication was attempted. The archived file parsed successfully: 25 pages, 78688 extractable characters, SHA-256 `c7380846511d8beb77faf51467e0c947a93d1de95b8683bae82e3ccc3acec335`.
