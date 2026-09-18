---
title: "AgentOccam: A Simple Yet Strong Baseline for LLM-Based Web Agents"
authors: ["Ke Yang", "Yao Liu", "Sapana Chaudhary", "Rasool Fakoor", "Pratik Chaudhari", "George Karypis", "Huzefa Rangwala"]
year: 2024
venue: "ICLR-2025"
source_type: "peer-reviewed"
paper_url: "https://arxiv.org/abs/2410.13825"
pdf_path: "papers/academic/yang-2024-agentoccam.pdf"
accessed: "2026-09-04"
review_status: "skimmed"
evidence_confidence: "high"
---

# yang-2024-agentoccam — AgentOccam: A Simple Yet Strong Baseline for LLM-Based Web Agents

## Why this source is in the corpus

Directly studies reusable harness components, outer-loop optimization, self-modification, or the statistical controls needed to decide whether an update is a real improvement.

## Research question

How much agent performance can be gained from a simple observation/action-aligned scaffold rather than elaborate planning or multi-agent machinery?

## Harness mechanism studied

A compact policy filters observations, aligns available actions with the environment, and applies domain-specific execution heuristics without demonstrations, role-play, or online workflow search.

## Method and experimental setup

AgentOccam is hand-designed and evaluated on WebArena and WebVoyager against complex agents, with deterministic and comparable plain-agent baselines intended to isolate scaffold simplicity.

## Main findings

- The abstract reports +9.8 absolute WebArena points over the previous state of the art and +26.6 points over comparable plain agents; WebVoyager improves +2.4 under deterministic evaluation.
- These gains come from a domain-specific static scaffold rather than self-building search, providing decisive counterevidence to the presumption that more agents, reflection, or evolutionary machinery are necessary.

## Mathematical content

The study estimates simple score differences under fixed policies; there is no architecture-search objective or theorem, but it supplies a low-complexity control for comparing marginal harness value.

## Evidence quality and limitations

Hand-engineered for web interaction, benchmark-specific observation/action alignment may not transfer, compute equivalence to every automated method is incomplete, and static heuristics do not address continual adaptation.

## Important implementation details

Prune irrelevant page observations, expose a constrained action representation aligned to the environment, use a concise execution loop and error handling, and avoid extra planning/persona modules.

## Claims this source supports

Careful interface and state design can dominate nominally sophisticated orchestration.

## Claims this source weakens or contradicts

Weakens complexity and self-improvement narratives: a simple static scaffold can beat elaborate agents without search or multiple roles.

## Relevance to a mathematics paper

Defines an essential simplicity baseline and motivates regularizing utility by calls, tokens, latency, and description length.

## Connections to other sources

See the category and claim-level cross-references in [`INDEX.md`](INDEX.md) and the synthesis documents.

## Verification notes

Local PDF abstract, design sections, WebArena/WebVoyager tables, comparable-agent discussion, ablations, and limitations were checked; no benchmark rerun was performed. The archived file parsed successfully: 33 pages, 156636 extractable characters, SHA-256 `1917c0df163ea0c8cdd0e50ed8cb5c0b6b8c648f8c4f9943c4a4c6061b5722f4`.
