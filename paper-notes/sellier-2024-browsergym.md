---
title: "The BrowserGym Ecosystem for Web Agent Research"
authors: ["Thibault Le Sellier De Chezelles", "Maxime Gasse", "Alexandre Drouin", "Massimo Caccia", "Léo Boisvert", "Megh Thakkar", "Tom Marty", "Rim Assouel", "Sahar Omidi Shayegan", "Lawrence Keunho Jang", "Xing Han Lù", "Ori Yoran", "Dehan Kong", "Frank F. Xu", "Siva Reddy", "Quentin Cappart", "Graham Neubig", "Ruslan Salakhutdinov", "Nicolas Chapados", "Alexandre Lacoste"]
year: 2024
venue: "preprint"
source_type: "preprint"
paper_url: "https://arxiv.org/abs/2412.05467"
pdf_path: "papers/academic/sellier-2024-browsergym.pdf"
accessed: "2026-09-04"
review_status: "skimmed"
evidence_confidence: "high"
---

# sellier-2024-browsergym — The BrowserGym Ecosystem for Web Agent Research

## Why this source is in the corpus

Makes model–harness–environment coupling observable in executable, long-horizon tasks.

## Research question

Can web-agent experiments be made comparable across previously fragmented benchmarks?

## Harness mechanism studied

BrowserGym standardizes browser observations and actions; AgentLab adds agent construction, parallel experiment management, trace analysis, and benchmark adapters.

## Method and experimental setup

2025 preprint running six models across six web benchmarks inside one ecosystem and documenting conversion and reproducibility choices.

## Main findings

- A unified environment makes model and agent comparisons operationally easier and exposes cross-benchmark differences.
- Claude 3.5 Sonnet leads most reported text-oriented conditions while GPT-4o leads selected vision conditions, but these rankings are tied to the exact agent and date.

## Mathematical content

A multi-benchmark score is a vector rather than inherently a scalar; aggregation weights and missing conditions determine ranks.

## Evidence quality and limitations

Benchmark conversions can alter observations and graders; websites and model APIs drift; the study changes both model and modality; project-authored results are not neutral certification.

## Important implementation details

Pin BrowserGym, benchmark, browser, website, and model versions; publish action/observation configs, seeds, traces, cost, and per-benchmark scores.

## Claims this source supports

Shared evaluation infrastructure reduces accidental implementation variance.

## Claims this source weakens or contradicts

Assuming that using one framework eliminates construct differences between web benchmarks.

## Relevance to a mathematics paper

Supports multivariate comparison, missing-data analysis, and rank robustness.

## Connections to other sources

See the category and claim-level cross-references in [`INDEX.md`](INDEX.md) and the synthesis documents.

## Verification notes

Abstract, ecosystem components, six-by-six experiment, observation/action standardization, and limitations checked in the local PDF. The archived file parsed successfully: 33 pages, 108927 extractable characters, SHA-256 `98d4d9b8088ca6bc5e0efd613389622b53ffedcb36cb285f093f7e6045499491`.
