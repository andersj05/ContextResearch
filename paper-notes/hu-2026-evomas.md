---
title: "Evolutionary Generation of Multi-Agent Systems"
authors: ["Yuntong Hu", "Yuting Zhang", "Matthew Trager", "Yi Zhang", "Shuo Yang", "Wei Xia", "Stefano Soatto"]
year: 2026
venue: "preprint"
source_type: "preprint"
paper_url: "https://arxiv.org/abs/2602.06511"
pdf_path: "papers/academic/hu-2026-evomas.pdf"
accessed: "2026-09-04"
review_status: "skimmed"
evidence_confidence: "high"
---

# hu-2026-evomas — Evolutionary Generation of Multi-Agent Systems

## Why this source is in the corpus

Directly studies reusable harness components, outer-loop optimization, self-modification, or the statistical controls needed to decide whether an update is a real improvement.

## Research question

Can evolutionary search over structured multi-agent configurations improve expressiveness without the execution failures of free-form code generation?

## Harness mechanism studied

A declarative DAG configuration specifies agents, prompts, models, tools, input/output roles, and edges; feedback-conditioned mutation, crossover, a candidate pool, and experience memory evolve the system.

## Method and experimental setup

EvoMAS seeds a pool with human-designed topologies, executes configurations through a fixed interpreter, scores traces, mutates/crosses candidates, updates persistent pool and memory, and evaluates BBEH, WorkBench, SWE-bench, and AIME.

## Main findings

- The abstract reports +10.5 points over EvoAgent on BBEH, +7.1 on WorkBench, and 79.1% SWE-bench Verified with Claude-4.5-Sonnet; Table 15 budget-matches SWE and still reports 79.1 at 31M tokens.
- Appendix Table 19 says per-query evolution alone improves a single agent but pool and memory add gains; Table 11 transfer drops from 49.1 to 44.1 in one setting, and success depends strongly on high-quality seed configurations.

## Mathematical content

Definition 2.1 sets C=(G,{A_i},V_in,V_out), G=(V,E), A_i=(b_i,p_i,Gamma_i), and maximizes expected reward minus a cost weight beta; evolution is heuristic, while beta sensitivity is only empirical—1.1 points across 10^-6 to 10^-8.

## Evidence quality and limitations

ICML 2026 paper but extremely recent; human seed pool and interpreter bound the space; meta-model and judge remain external; several benchmarks use judge scores; persistent pool is not tested under long nonstationary deployment.

## Important implementation details

Represent each MAS as schema-validated acyclic configuration, execute it with a shared runtime, retain multiple seeds, feed traces to a mutation/crossover model, store experience, and gate pool updates on task reward and cost.

## Claims this source supports

Structured configuration search can jointly edit topology, prompts, models, and tools while preserving executability better than raw code search.

## Claims this source weakens or contradicts

The results weaken claims that evolution starts from nothing or always transfers: curated seeds are critical and at least one transfer cell declines.

## Relevance to a mathematics paper

Supplies a precise graph/configuration object, a cost-regularized objective, and ablations for persistence components, seed quality, judges, and compute.

## Connections to other sources

See the category and claim-level cross-references in [`INDEX.md`](INDEX.md) and the synthesis documents.

## Verification notes

Local ICML 2026 PDF abstract, Definition 2.1, Tables 1–2 and Appendix Tables 11–25 including budget, transfer, accumulation, and cost studies were checked; no rerun was performed. The archived file parsed successfully: 33 pages, 130835 extractable characters, SHA-256 `eb0825fda1b70a9522298d8b423fffe19d9b1cafbd183873bcfb457f8bc0892d`.
