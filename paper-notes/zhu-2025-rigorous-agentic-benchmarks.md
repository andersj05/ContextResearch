---
title: "Establishing Best Practices for Building Rigorous Agentic Benchmarks"
authors: ["Yuxuan Zhu", "Tengjun Jin", "Yada Pruksachatkun", "Andy Zhang", "Shu Liu", "Sasha Cui", "Sayash Kapoor", "Shayne Longpre", "Kevin Meng", "Rebecca Weiss", "Fazl Barez", "Rahul Gupta", "Jwala Dhamala", "Jacob Merizian", "Mario Giulianelli", "Harry Coppock", "Cozmin Ududec", "Jasjeet Sekhon", "Jacob Steinhardt", "Antony Kellermann", "Sarah Schwettmann", "Matei Zaharia", "Ion Stoica", "Percy Liang", "Daniel Kang"]
year: 2025
venue: "NeurIPS-2025"
source_type: "peer-reviewed"
paper_url: "https://arxiv.org/abs/2507.02825"
pdf_path: "papers/academic/zhu-2025-rigorous-agentic-benchmarks.pdf"
accessed: "2026-09-04"
review_status: "fully-reviewed"
evidence_confidence: "high"
---

# zhu-2025-rigorous-agentic-benchmarks — Establishing Best Practices for Building Rigorous Agentic Benchmarks

## Why this source is in the corpus

Makes model–harness–environment coupling observable in executable, long-horizon tasks.

## Research question

What validity conditions should an agentic benchmark satisfy?

## Harness mechanism studied

The Agentic Benchmark Checklist separates task validity, outcome validity, and reporting validity, then audits existing benchmarks and revises CVE-Bench.

## Method and experimental setup

2025 preprint synthesizing prior failures and builder experience, applying a checklist to ten popular agent benchmarks, and expert-validating a security benchmark case study.

## Main findings

- Seven of ten audited benchmarks have outcome-validity flaws, seven have task-validity flaws, and all have reporting limitations.
- Reported errors reach 100% relative; examples include a trivial 38% tau-bench airline score, 31-point KernelBench inflation, 5.2-point WebArena inflation, and a 33-point reduction of CVE-Bench overestimation after revision.

## Mathematical content

If observed success is an imperfect test of latent task success, q equals sensitivity times prevalence plus one minus specificity times one minus prevalence; inversion requires sensitivity plus specificity greater than one.

## Evidence quality and limitations

Checklist audits include judgment and selected benchmarks; some examples depend on implementation versions; corrected scores need not transfer; the paper was a preprint at cutoff.

## Important implementation details

Pretest tasks for solvability, audit reward false positives and negatives, execute trivial and oracle agents, freeze versions, release logs, and report denominator and exclusions.

## Claims this source supports

Benchmark validity is an engineering and measurement problem, not merely dataset size.

## Claims this source weakens or contradicts

Treating executable reward as automatically objective or leaderboard precision as ground truth.

## Relevance to a mathematics paper

Direct basis for measurement-error and construct-validity mathematics.

## Connections to other sources

See the category and claim-level cross-references in [`INDEX.md`](INDEX.md) and the synthesis documents.

## Verification notes

Abstract and pages 1-2 checked for definitions, ten-benchmark audit, seven-seven-all result, example errors, CVE-Bench correction, and limitations. The archived file parsed successfully: 39 pages, 135450 extractable characters, SHA-256 `6bee07172c55c1146fdc8a14e0a4839854f7b4be36616729fda3ee6d519a698b`.
