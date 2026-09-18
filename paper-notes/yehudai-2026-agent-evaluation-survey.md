---
title: "A Survey on Evaluation of LLM-based Agents"
authors: ["Asaf Yehudai", "Lilach Eden", "Alan Li", "Guy Uziel", "Yilun Zhao", "Roy Bar-Haim", "Arman Cohan", "Michal Shmueli-Scheuer"]
year: 2026
venue: "Findings-ACL-2026"
source_type: "peer-reviewed"
paper_url: "https://aclanthology.org/2026.findings-acl.1330/"
pdf_path: "papers/academic/yehudai-2026-agent-evaluation-survey.pdf"
accessed: "2026-09-04"
review_status: "skimmed"
evidence_confidence: "medium"
---

# yehudai-2026-agent-evaluation-survey — A Survey on Evaluation of LLM-based Agents

## Why this source is in the corpus

Supplies vocabulary and comparison axes for formalizing the harness as a composite decision system.

## Research question

How are LLM agents evaluated, and where do current protocols fail?

## Harness mechanism studied

Evaluation harnesses spanning environments, trajectories, capability dimensions, and graders.

## Method and experimental setup

Survey classifies benchmarks, metrics, environments, and evaluation challenges across agent domains.

## Main findings

- Evaluation choices are themselves harness components that shape observed capability.
- The literature lacks consistent reporting of budgets, environment versions, reliability, and safety.

## Mathematical content

Summarizes success-rate, efficiency, robustness, and trajectory metrics; no single universal estimator is justified.

## Evidence quality and limitations

Coverage depends on available publications and fast-moving benchmarks; survey categories do not validate graders.

## Important implementation details

Version task environments and scorers, log trajectories, and report uncertainty and repeated-run reliability.

## Claims this source supports

Agent evaluation must include process, cost, and robustness, not only final task reward.

## Claims this source weakens or contradicts

Leaderboard point estimates as context-free model properties.

## Relevance to a mathematics paper

Provides the measurement dimensions needed for a multivariate response model.

## Connections to other sources

See the category and claim-level cross-references in [`INDEX.md`](INDEX.md) and the synthesis documents.

## Verification notes

Abstract, benchmark taxonomy, metric discussion, challenges, and conclusion checked in the local PDF. The archived file parsed successfully: 25 pages, 115507 extractable characters, SHA-256 `2c3c80fff5735925378b99528684559e2d47f82e281957dc4b955397186560b1`.
