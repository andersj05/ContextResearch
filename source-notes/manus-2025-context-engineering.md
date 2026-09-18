---
title: "Context Engineering for AI Agents: Lessons from Building Manus"
author_or_org: "Yichao Ji / Manus"
date: "2025-07-18"
source_type: "engineering-blog"
url: "https://manus.im/blog/Context-Engineering-for-AI-Agents-Lessons-from-Building-Manus"
version_or_commit: "web version accessed 2026-09-04"
accessed: "2026-09-04"
review_status: "reviewed"
evidence_confidence: "medium"
---

# manus-2025-context-engineering — Context Engineering for AI Agents

## Why this source is in the corpus

This production post provides unusually concrete hypotheses about prompt-prefix caching, action-space stability, external memory, goal recitation, and error preservation.

## System or claim described

Manus reports four framework rewrites and argues that the evolving context—not only the system prompt—determines cost, latency, recovery, and long-horizon behavior. Its six rules are design around the KV cache; mask tools rather than remove them; use the filesystem as restorable context; recite goals; retain failed actions; and avoid homogeneous histories that induce repetitive behavior.

## Architecture / mechanism

- Stable, deterministic, append-only prefixes improve prompt-cache reuse.
- A state machine constrains action choice through response prefills or logit masks without changing the serialized tool roster.
- Large observations spill to files while context retains paths or URLs so compression remains reversible.
- A repeatedly updated todo file places the global objective near the context tail.
- Failed actions and stack traces remain visible as evidence for recovery.
- Small structured serialization variation is introduced to disrupt imitation of a repetitive trajectory.

## Empirical evidence

The post reports an average input-to-output token ratio near 100:1 and roughly 50 tool calls for a typical Manus task. It gives a contemporary ten-to-one cached-versus-uncached Sonnet input price example. It does not provide controlled success-rate ablations for the six rules.

## Mathematical or formal content

Prefix caching makes cost depend on the longest identical prefix, not only total tokens. Restorable compression can be modeled as retaining an address `r(o)` such that an evicted observation `o` can be fetched when needed. Goal recitation changes positional distance, connecting to the U-shaped relevance curves in Lost in the Middle.

## What is directly evidenced

The page documents Manus's implemented choices and operational ratios. It explicitly calls the rules local optima rather than universal truths.

## What is interpretation or advocacy

Claims that retained errors update model beliefs, controlled formatting noise prevents ruts, or KV hit rate is the single most important metric are hypotheses based on experience. Dynamic tool discovery may still win when grammar cost dominates cache invalidation.

## Limitations, incentives, and likely biases

No public dataset, paired trial, uncertainty, or trace sample is supplied. Price ratios change. Some techniques require provider capabilities unavailable through every API. Manus promotes its own product architecture.

## Transferable engineering lessons

Measure cache-hit rate and time-to-first-token; serialize deterministically; separate reversible storage from selected context; test tool masking against discovery; keep failure evidence until it becomes distracting; and treat repeated-action patterns as a detectable state variable.

## Connections to academic work

Filesystem memory connects to MemGPT and RAG; goal recitation to Lost in the Middle and HiAgent; error preservation to ReAct, Reflexion, and CRITIC; tool masking to constrained decoding; homogeneous-trajectory failure to context-induced policy bias.

## Verification notes

All six principle sections and conclusion were inspected in the canonical page on 2026-09-04. Reported ratios are author statements and should not be generalized without replication.
