---
title: "AutoDesign: Meta-Harness Optimization for Long-Horizon Agentic Design"
authors: ["Yaxin Luo", "Haobin Jiang", "Jialv Zou", "Xu Huang", "Wenhao Yan", "Haodong Li", "Zhengrong Yue", "Jing Li", "Xiaofu Chen", "Xiaohan Zhao", "Jiacheng Liu", "Jiacheng Cui", "Zhiqiang Shen", "Xiaotong Li"]
year: 2026
venue: "preprint"
source_type: "preprint"
paper_url: "https://arxiv.org/abs/2608.13560"
pdf_path: "papers/academic/luo-2026-autodesign.pdf"
accessed: "2026-09-04"
review_status: "fully-reviewed"
evidence_confidence: "medium"
---

# luo-2026-autodesign — AutoDesign: Meta-Harness Optimization for Long-Horizon Agentic Design

## Why this source is in the corpus

Directly treats the harness, its optimization, or its runtime semantics as the object of study.

## Research question

Can a meta-harness improve a reusable paper-to-poster design harness from repeated rollout feedback?

## Harness mechanism studied

An outer code agent modifies designer, critic, tools, feedback, and stopping policy while an inner loop iteratively produces artifacts.

## Method and experimental setup

PosterBench with 100 papers plus a 10-paper controlled subset, seven code-agent-model configurations, automated scoring and system-blind human preferences.

## Main findings

- The learned DesignHarness raises average score from 54.99 to 67.39, a 12.4-point gain across seven configurations.
- Main-track AutoDesign scores 78.32, 7.45 points above Claude Design; the human Bradley-Terry estimate is 64.0% with a 95% interval of 55.2-77.8%.

## Mathematical content

Defines nested designer-critic refinement and accept-on-train-improvement-without-dev-regression; human preferences use Bradley-Terry estimation and crossed bootstrap intervals.

## Evidence quality and limitations

Single artifact domain, author-built grader, expensive seven-day evolution, possible metric gaming, and newest-model comparisons are perishable.

## Important implementation details

Keep inner artifact refinement distinct from outer harness updates and require train, development, and human-validation gates.

## Claims this source supports

Harness optimization can transfer across several executor configurations in one domain.

## Claims this source weakens or contradicts

Automated poster score improvement as evidence of broad agent self-improvement.

## Relevance to a mathematics paper

Offers a concrete bilevel optimization and preference-modeling case study.

## Connections to other sources

See the category and claim-level cross-references in [`INDEX.md`](INDEX.md) and the synthesis documents.

## Verification notes

Abstract, equations for inner loop, acceptance gate, main tables, human study, bootstrap interval, and limitations checked in the local PDF. The archived file parsed successfully: 29 pages, 101250 extractable characters, SHA-256 `9e9b8532f29ab9d12756f4dba5cc8d1577feb9b0057ae1ae6f2bcc9f04ce06d8`.
