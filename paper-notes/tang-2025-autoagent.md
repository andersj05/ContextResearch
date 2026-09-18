---
title: "AutoAgent: A Fully-Automated and Zero-Code Framework for LLM Agents"
authors: ["Jiabin Tang", "Tianyu Fan", "Chao Huang"]
year: 2025
venue: "Findings-ACL-2026"
source_type: "peer-reviewed"
paper_url: "https://arxiv.org/abs/2502.05957"
pdf_path: "papers/academic/tang-2025-autoagent.pdf"
accessed: "2026-09-04"
review_status: "skimmed"
evidence_confidence: "medium"
---

# tang-2025-autoagent — AutoAgent: A Fully-Automated and Zero-Code Framework for LLM Agents

## Why this source is in the corpus

Directly studies reusable harness components, outer-loop optimization, self-modification, or the statistical controls needed to decide whether an update is a real improvement.

## Research question

Can agents, tools, and workflows be generated and modified directly in natural language without users writing orchestration code?

## Harness mechanism studied

A central natural-language programming agent invokes meta-tools to create XML-specified tools, agents, and workflows, then uses self-play, execution feedback, editing, and debugging.

## Method and experimental setup

AutoAgent builds components from user requests and environment descriptions, tests generated artifacts, and evaluates GAIA, retrieval-augmented generation, and a majority-vote workflow against agent frameworks and proprietary systems.

## Main findings

- GAIA Table 1 reports 55.15 for AutoAgent versus proprietary h2oGPTe 63.64, supporting the narrower claim of top open-source performance rather than overall state of the art; RAG reports 73.51 versus LangChain 62.83.
- A generated majority workflow reaches 75.6 versus its best component 74.2, only +1.4 points with extra calls, and the paper states it does not systematically evaluate the central natural-language programming mechanism.

## Mathematical content

Artifact creation is a constrained program-synthesis map from natural language to XML/runtime objects; majority voting estimates a modal answer but no equal-cost statistical test or synthesis correctness theorem is supplied.

## Evidence quality and limitations

Findings ACL 2026 paper with changing external comparisons, no comprehensive evaluation of the core editor, unequal calls in workflows, generated-code/tool security risks, and possible benchmark-specific manual intervention.

## Important implementation details

Expose create/edit/debug commands for tools, agents, and XML workflows; generate definitions in natural language, run smoke tests and self-play, repair failures, register artifacts, and compose them at runtime.

## Claims this source supports

Natural-language meta-tools can lower the barrier to creating and persisting harness components.

## Claims this source weakens or contradicts

Weakens claims of fully automatic design: the overall GAIA system trails a proprietary comparator and the isolated orchestration gain is small and compute-confounded.

## Relevance to a mathematics paper

Raises formal program-validity and voting-cost questions but contributes no theorem; useful as an implementation architecture rather than an estimator.

## Connections to other sources

See the category and claim-level cross-references in [`INDEX.md`](INDEX.md) and the synthesis documents.

## Verification notes

Local PDF system design, Tables 1 and RAG/majority results, stated evaluation scope, case studies, and limitations were checked; no generated agent was rerun. The archived file parsed successfully: 58 pages, 139516 extractable characters, SHA-256 `d3d72179c14c4a66214e53d0d5ed760bb37f9664141c952c3cefa8154addcc41`.
