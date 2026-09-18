---
title: "CORE-Bench: Fostering the Credibility of Published Research Through a Computational Reproducibility Agent Benchmark"
authors: ["Zachary S. Siegel", "Sayash Kapoor", "Nitya Nadgir", "Benedikt Stroebl", "Arvind Narayanan"]
year: 2025
venue: "TMLR-2025"
source_type: "peer-reviewed"
paper_url: "https://arxiv.org/abs/2409.11363"
pdf_path: "papers/academic/siegel-2025-core-bench.pdf"
accessed: "2026-09-04"
review_status: "fully-reviewed"
evidence_confidence: "high"
---

# siegel-2025-core-bench — CORE-Bench: Fostering the Credibility of Published Research Through a Computational Reproducibility Agent Benchmark

## Why this source is in the corpus

Makes model–harness–environment coupling observable in executable, long-horizon tasks.

## Research question

Can agents reproduce computational research results from code and data?

## Harness mechanism studied

CORE-Bench gives an agent a research repository and environment, requires installation and execution, and grades answers about reproduced outputs at three difficulty levels.

## Method and experimental setup

Peer-reviewed benchmark with 270 tasks from 90 papers across computer science, social science, and medicine, including text and vision-language conditions.

## Main findings

- The best reported agent achieves 21% on the hardest tasks.
- Failures involve environment setup, dependency resolution, execution, output discovery, and interpretation, so the benchmark measures a full research harness rather than pure scientific reasoning.

## Mathematical content

Success is conjunctive across questions for a repository; three tasks per paper create within-paper dependence that must be reflected in uncertainty.

## Evidence quality and limitations

Only 90 published projects and three disciplines; reference environments can age; conjunctive grading can be brittle; baseline agents and models are dated.

## Important implementation details

Archive containers and dependencies, cluster splits and intervals by paper, preserve commands and outputs, and separately label environment versus interpretation failures.

## Claims this source supports

Research-agent evaluation needs executable, provenance-rich tasks.

## Claims this source weakens or contradicts

Equating paper-question accuracy with autonomous scientific discovery or independent theorem generation.

## Relevance to a mathematics paper

Supports clustered reliability and conjunctive-stage models relevant to reproducibility research.

## Connections to other sources

See the category and claim-level cross-references in [`INDEX.md`](INDEX.md) and the synthesis documents.

## Verification notes

Abstract and pages 1-2 checked for 270 tasks, 90 papers, fields, three levels, conjunctive scoring, 21% hard result, and limitations. The archived file parsed successfully: 30 pages, 103961 extractable characters, SHA-256 `1d1fbe8a3cf472fc468495e6a3bcd6b90224ba1eae3dac8d8174f98d666c3d76`.
