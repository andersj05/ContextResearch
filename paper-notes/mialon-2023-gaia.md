---
title: "GAIA: a benchmark for General AI Assistants"
authors: ["Grégoire Mialon", "Clémentine Fourrier", "Craig Swift", "Thomas Wolf", "Yann LeCun", "Thomas Scialom"]
year: 2023
venue: "ICLR-2024"
source_type: "peer-reviewed"
paper_url: "https://arxiv.org/abs/2311.12983"
pdf_path: "papers/academic/mialon-2023-gaia.pdf"
accessed: "2026-09-04"
review_status: "skimmed"
evidence_confidence: "high"
---

# mialon-2023-gaia — GAIA: a benchmark for General AI Assistants

## Why this source is in the corpus

Makes model–harness–environment coupling observable in executable, long-horizon tasks.

## Research question

Can assistants robustly solve conceptually simple real-world questions requiring tools, browsing, files, and multimodality?

## Harness mechanism studied

GAIA specifies unambiguous answer questions whose solution requires composing research, code, web, and file operations; most answers are hidden for leaderboard use.

## Method and experimental setup

ICLR 2024 benchmark of 466 questions in three difficulty levels, with human and GPT-4-with-plugins baselines.

## Main findings

- Humans obtain 92% while the paper-era GPT-4 plugin system obtains 15%.
- The gap demonstrates that strong static exam performance does not imply robust tool-mediated assistance.

## Mathematical content

Accuracy is a binomial proportion stratified by difficulty; a harness study should use paired task outcomes and level-weighted uncertainty.

## Evidence quality and limitations

Only 466 author-designed questions; tools and web content drift; exact-match answers can miss semantically valid variants; the 2023 plugin harness is obsolete.

## Important implementation details

Preserve task versions and attachments, log tools and sources, freeze web evidence where lawful, report level-stratified accuracy, and distinguish model from harness.

## Claims this source supports

Realistic compositional tasks expose failures hidden by conventional knowledge benchmarks.

## Claims this source weakens or contradicts

Using a dated 15% baseline as a current capability estimate or as a pure model comparison.

## Relevance to a mathematics paper

Supports item-response and difficulty-stratified harness evaluation.

## Connections to other sources

See the category and claim-level cross-references in [`INDEX.md`](INDEX.md) and the synthesis documents.

## Verification notes

Abstract and pages 1-2 checked for 466 questions, hidden answers, human 92%, GPT-4 plugins 15%, task philosophy, and limitations. The archived file parsed successfully: 24 pages, 82222 extractable characters, SHA-256 `5bf6f968d4f5cd20acdfca6e81e3c9f5277bb66061fad7a02e35442dff812ba0`.
