---
title: "Effective Context Engineering for AI Agents"
author_or_org: "Anthropic"
date: "2025-09-29"
source_type: "engineering-blog"
url: "https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents"
version_or_commit: "web version accessed 2026-09-04"
accessed: "2026-09-04"
review_status: "reviewed"
evidence_confidence: "medium"
---

# anthropic-2025-context-engineering — Effective Context Engineering

## Why this source is in the corpus

This post gives a production-oriented definition of context engineering and a compact taxonomy of retrieval, compaction, durable notes, and subagent isolation.

## System or claim described

Context engineering is defined as curating and maintaining the token set passed at every inference step, including prompts, tools, external data, and history. The design target is the smallest high-signal context that preserves behaviorally necessary information.

## Architecture / mechanism

The post recommends minimal but sufficient system instructions, unambiguous low-overlap tools, canonical examples, just-in-time exploration, compaction, file-based notes, and separate subagent contexts. Compaction first favors recall, then removes redundant material; old tool results are an early candidate. Claude Code's reported implementation retains a model-written summary and the five most recently accessed files.

## Empirical evidence

The post synthesizes Anthropic and customer experience but gives no public controlled comparison for most recommendations. It reports that specialized subagents may consume tens of thousands of tokens and return summaries of roughly 1,000-2,000 tokens, which is an operational pattern rather than a performance estimate.

## Mathematical or formal content

The implied optimization is constrained selection: choose context subset `S` to maximize expected task utility subject to a token budget. This is not proved to be submodular or optimally solved by any proposed heuristic. Compaction introduces asymmetric loss because future relevance is unknown.

## What is directly evidenced

The page documents specific Anthropic implementations and gives explicit failure modes: bloated tools, vague or overfit prompts, context pollution, and irreversible loss from aggressive summaries.

## What is interpretation or advocacy

The attention-budget analogy and recommendation that compact context remains central as windows grow are reasoned positions. Claims about universal context degradation should be anchored to controlled studies such as Lost in the Middle rather than this post alone.

## Limitations, incentives, and likely biases

No denominators, held-out tasks, costs, or uncertainty are reported for most techniques. Provider-specific compaction and memory features are commercial products. The recommendations may differ for local models or tasks requiring exhaustive records.

## Transferable engineering lessons

Measure what each token class contributes, make compression reversible where possible, distinguish working context from durable memory, tune summaries on long traces, and select among compaction, notes, and subagents based on task topology rather than fashion.

## Connections to academic work

The guidance connects to RAG, MemGPT, Lost in the Middle, LongMemEval, MemoHarness, HiAgent, and multi-agent compression. It also supplies practitioner hypotheses for the formal context compiler in the synthesis.

## Verification notes

The canonical page's definition, token-selection guidance, retrieval, compaction, note-taking, subagent, and conclusion sections were checked on 2026-09-04.
