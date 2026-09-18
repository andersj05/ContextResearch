---
title: "SWE-smith: Scaling Data for Software Engineering Agents"
authors: ["John Yang", "Kilian Lieret", "Carlos E. Jimenez", "Alexander Wettig", "Kabir Khandpur", "Yanzhe Zhang", "Binyuan Hui", "Ofir Press", "Ludwig Schmidt", "Diyi Yang"]
year: 2025
venue: "preprint"
source_type: "preprint"
paper_url: "https://arxiv.org/abs/2504.21798"
pdf_path: "papers/academic/yang-2025-swe-smith.pdf"
accessed: "2026-09-04"
review_status: "skimmed"
evidence_confidence: "medium"
---

# yang-2025-swe-smith — SWE-smith: Scaling Data for Software Engineering Agents

## Why this source is in the corpus

Makes model–harness–environment coupling observable in executable, long-horizon tasks.

## Research question

Can executable software-engineering training data be synthesized at scale?

## Harness mechanism studied

SWE-smith creates environments and breaks real codebases through model rewrites, AST mutations, pull-request mirroring, and bug composition, then trains agents on verified trajectories.

## Method and experimental setup

2025 preprint constructing 50,000-plus task instances from 128 repositories and training SWE-agent-LM-32B with data-scaling experiments.

## Main findings

- The dataset has about 50,000 instances from 128 repositories, an order of magnitude above earlier executable sets; the trained 32B model reports 40.2% pass at one on SWE-bench Verified.
- Scaling curves mix data quantity, filtering, training, and harness choices.

## Mathematical content

Pass at one is a task mean; the data-scaling curve is empirical and does not establish a universal power law.

## Evidence quality and limitations

Synthetic bugs may not match real maintenance work; generator and verifier biases can couple; the benchmark is public; the reported model result is not a harness-only effect.

## Important implementation details

Retain mutation provenance, environment Dockerfiles, failing and passing tests, generated issue text, trajectory filters, and contamination checks for every task.

## Claims this source supports

Executable synthetic tasks can lower the data bottleneck for training interactive agents.

## Claims this source weakens or contradicts

Interpreting synthetic-data scaling as direct evidence about real-world harness architecture.

## Relevance to a mathematics paper

Useful for learning-curve design and distribution-shift analysis, not a theorem.

## Connections to other sources

See the category and claim-level cross-references in [`INDEX.md`](INDEX.md) and the synthesis documents.

## Verification notes

Abstract and pages 1-2 checked for repository and instance counts, generation strategies, 40.2% result, and stated scope. The archived file parsed successfully: 46 pages, 157604 extractable characters, SHA-256 `6752df853569104ae2e55cc1bee09dc3f6b335f7eeae300b6e9fee911f3f2897`.
