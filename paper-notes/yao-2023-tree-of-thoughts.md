---
title: "Tree of Thoughts: Deliberate Problem Solving with Large Language Models"
authors: ["Shunyu Yao", "Dian Yu", "Jeffrey Zhao", "Izhak Shafran", "Thomas L. Griffiths", "Yuan Cao", "Karthik Narasimhan"]
year: 2023
venue: "NeurIPS-2023"
source_type: "peer-reviewed"
paper_url: "https://arxiv.org/abs/2305.10601"
pdf_path: "papers/academic/yao-2023-tree-of-thoughts.pdf"
accessed: "2026-09-04"
review_status: "fully-reviewed"
evidence_confidence: "high"
---

# yao-2023-tree-of-thoughts — Tree of Thoughts: Deliberate Problem Solving with Large Language Models

## Why this source is in the corpus

Supports analysis of inference-time search, feedback, stopping, and verifier error.

## Research question

Can explicit search over intermediate language states solve problems that greedy or sampled chains miss?

## Harness mechanism studied

A generator proposes thoughts, an evaluator scores partial states, and breadth-first or depth-first search selects expansions.

## Method and experimental setup

Game of 24, creative writing, and mini-crossword tasks use hand-designed thought units, proposal prompts, evaluators, and search widths.

## Main findings

- On Game of 24, GPT-4 CoT scores 4%, CoT self-consistency with 100 paths 9%, best-of-100 CoT 49%, and ToT with breadth five 74%.
- ToT costs about $0.74 per case versus $0.47 for best-of-100 CoT and may use 5-100 times CoT tokens.

## Mathematical content

State s=[x,z_1,...,z_i]; generator G(p_theta,s,k), evaluator V(s), and BFS or DFS selection define a heuristic search.

## Evidence quality and limitations

Only three hand-structured tasks, privileged decomposition and evaluator design, large call budgets, and no completeness guarantee.

## Important implementation details

Version thought granularity, branching factor, evaluator prompt, rollback semantics, stopping, and total tokens.

## Claims this source supports

Explicit search can outperform naive sampling when partial states are informative and evaluable.

## Claims this source weakens or contradicts

ToT as cost-free general deliberation or proof that tree search itself caused the full gain.

## Relevance to a mathematics paper

Connects LLM harnesses to heuristic search and budgeted branching-process analysis.

## Connections to other sources

See the category and claim-level cross-references in [`INDEX.md`](INDEX.md) and the synthesis documents.

## Verification notes

Table 2, Table 7, search algorithm, cost table, task decompositions, and limitations checked in the local PDF. The archived file parsed successfully: 14 pages, 59373 extractable characters, SHA-256 `79c5237e3f63953a73f2b0d6894327702ee1f7e981450c251bb1b5cb4f8d7b8f`.
