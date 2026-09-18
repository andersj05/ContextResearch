---
title: "AutoGen: Enabling Next-Gen LLM Applications via Multi-Agent Conversation"
authors: ["Qingyun Wu", "Gagan Bansal", "Jieyu Zhang", "Yiran Wu", "Beibin Li", "Erkang Zhu", "Li Jiang", "Xiaoyun Zhang", "Shaokun Zhang", "Jiale Liu", "Ahmed Hassan Awadallah", "Ryen W White", "Doug Burger", "Chi Wang"]
year: 2023
venue: "preprint"
source_type: "preprint"
paper_url: "https://arxiv.org/abs/2308.08155"
pdf_path: "papers/academic/wu-2023-autogen.pdf"
accessed: "2026-09-04"
review_status: "skimmed"
evidence_confidence: "medium"
---

# wu-2023-autogen — AutoGen: Enabling Next-Gen LLM Applications via Multi-Agent Conversation

## Why this source is in the corpus

Provides communication, aggregation, or coordination mechanisms and their compute-matched counterevidence.

## Research question

Can a generic conversation runtime express diverse single- and multi-agent LLM applications?

## Harness mechanism studied

Customizable conversable agents combine LLM calls, humans, and code or tools under programmable reply and termination policies.

## Method and experimental setup

Open-source framework plus case studies across math, coding, question answering, operations research, and games.

## Main findings

- AutoGen demonstrates that many workflows can be represented as agent conversations and nested interaction patterns.
- Application gains mix models, prompts, tools, human intervention, and orchestration, so the framework paper does not isolate a harness effect.

## Mathematical content

A conversation is a message-passing state machine with reply functions and termination predicates; no general performance theorem.

## Evidence quality and limitations

Case-study evidence, rapid API evolution, application-specific budgets, and current AutoGen architecture differs from the paper's version.

## Important implementation details

Cite the repository commit and package version; specify agent roles, reply order, executors, human-input mode, and stop conditions.

## Claims this source supports

Message-driven orchestration is a flexible implementation substrate.

## Claims this source weakens or contradicts

AutoGen-branded results as comparable across versions or as model-only evidence.

## Relevance to a mathematics paper

Connects harnesses to actor systems and asynchronous message-passing models.

## Connections to other sources

See the category and claim-level cross-references in [`INDEX.md`](INDEX.md) and the synthesis documents.

## Verification notes

Abstract, framework abstractions, application cases, execution modes, and limitations checked in the local PDF; version discontinuity recorded separately. The archived file parsed successfully: 43 pages, 157051 extractable characters, SHA-256 `fcf8b1acae6b1bd6f14c92463caa9726828bf998234ba9f10c2411087897c96b`.
