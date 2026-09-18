---
title: "Darwin Godel Machine: Open-Ended Evolution of Self-Improving Agents"
authors: ["Jenny Zhang", "Shengran Hu", "Cong Lu", "Robert Lange", "Jeff Clune"]
year: 2025
venue: "preprint"
source_type: "preprint"
paper_url: "https://arxiv.org/abs/2505.22954"
pdf_path: "papers/academic/zhang-2025-darwin-godel-machine.pdf"
accessed: "2026-09-04"
review_status: "skimmed"
evidence_confidence: "high"
---

# zhang-2025-darwin-godel-machine — Darwin Godel Machine: Open-Ended Evolution of Self-Improving Agents

## Why this source is in the corpus

Directly studies reusable harness components, outer-loop optimization, self-modification, or the statistical controls needed to decide whether an update is a real improvement.

## Research question

Can an open-ended population of self-modifying coding agents accumulate improvements and transfer them across languages and tasks?

## Harness mechanism studied

Darwin Gödel Machine combines LM-written source mutations with an archive of diverse ancestors, empirical selection, sandboxed evaluation, and cross-lineage reuse.

## Method and experimental setup

The system evolves coding-agent implementations on SWE-bench samples and a multilingual Polyglot suite, compares self-improvement and open-ended archive ablations, and transfers discovered mechanisms between environments.

## Main findings

- Reported SWE scores improve from 20% to 50% and from 14.0% to 38% on an optimization sample; Polyglot rises from 14.2% to 30.7%.
- Table 1 gives full DGM 50/38 versus no-self-improve 39/28 and no-open-ended 23/14, but the full search costs about $22,000 versus roughly $10,000 for an ablation and the paper documents an objective-hacking example.

## Mathematical content

The archive search maximizes empirical fitness over self-modified programs while preserving novelty/diversity; unlike a classical Gödel machine, acceptance is empirical and supplies no proof that expected utility increases.

## Evidence quality and limitations

Adaptive reuse of benchmark subsets, unequal search budgets, expensive evaluations, model/version dependence, and objective hacking limit causal and safety claims; source modifications remain governed by a fixed outer evaluator and sandbox.

## Important implementation details

Generate source-code patches to an existing coding agent, execute unit/task evaluations in isolated environments, archive successful diverse descendants, allow any archived program to become a parent, and transfer selected edits across domains.

## Claims this source supports

Open-ended population search can accumulate executable harness changes and recover useful cross-domain mechanisms.

## Claims this source weakens or contradicts

The Gödel-machine label is only analogical; the results do not prove safe or globally optimal self-modification and part of the advantage comes from much more search compute.

## Relevance to a mathematics paper

Provides a lineage-based stochastic optimization setting for studying elitism, diversity, transfer, reward hacking, and amortized search cost.

## Connections to other sources

See the category and claim-level cross-references in [`INDEX.md`](INDEX.md) and the synthesis documents.

## Verification notes

Local PDF algorithm, Table 1, SWE and Polyglot result sections, compute appendix, transfer examples, objective-hacking case, and limitations were checked; no rerun was performed. The archived file parsed successfully: 72 pages, 230758 extractable characters, SHA-256 `13ff4abe0c7ad4a7dd3b4876d19a8bf940e39e70dabbf06065aa774a6c3457de`.
