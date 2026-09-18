---
title: "How We Built Our Multi-Agent Research System"
author_or_org: "Anthropic"
date: "2025-06-13"
source_type: "engineering-blog"
url: "https://www.anthropic.com/engineering/multi-agent-research-system"
version_or_commit: "web version accessed 2026-09-04"
accessed: "2026-09-04"
review_status: "reviewed"
evidence_confidence: "medium"
---

# anthropic-2025-multi-agent-research — Multi-Agent Research System

## Why this source is in the corpus

This is a rare production post that gives an architecture, a quantitative internal comparison, resource-use measurements, and negative boundary conditions for multi-agent research.

## System or claim described

A lead agent plans a research strategy, spawns parallel search agents with separate contexts, and synthesizes their compressed reports. The claimed benefit is breadth-first exploration when lines of inquiry are independent and information exceeds one context window.

## Architecture / mechanism

The system uses an orchestrator-worker topology. Subagents receive disjoint or specialized prompts, search independently, and return high-signal summaries. Separate contexts increase total inference capacity and reduce path dependence; the lead agent integrates results and can redirect work.

## Empirical evidence

Anthropic reports that an Opus 4 lead with Sonnet 4 subagents outperformed a single Opus 4 agent by 90.2% on an internal research evaluation. In a BrowseComp analysis, token usage alone explained 80% of observed variance and token use, tool calls, and model choice jointly explained 95%. Agents used about four times the tokens of chat, and multi-agent systems about 15 times. These are internal observational or partially controlled analyses; the evaluation set and full regression are not public.

## Mathematical or formal content

The architecture is a directed task graph. If branch outputs are conditionally independent given the query, wall time approaches the critical-path maximum while token cost is additive. Performance attribution requires separating agent count from total tokens and tool calls; the reported variance explanation does not by itself identify causal mediation.

## What is directly evidenced

The page documents the deployed topology, prompts/tools lessons, internal score ratio, token multiples, and task types where the team observed benefit or poor fit.

## What is interpretation or advocacy

The broader claim that multi-agent systems become vital above an intelligence threshold is an analogy and product judgment. The post itself says much of the gain comes from spending more tokens.

## Limitations, incentives, and likely biases

Internal tasks, traces, scoring details, and uncertainty are unavailable. Model, token budget, tool calls, concurrency, and orchestration differ together. Anthropic benefits commercially from demonstrating Claude-based research systems.

## Transferable engineering lessons

Use multi-agent orchestration for separable, breadth-heavy tasks; supply an equal-token independent-sampling or single-agent baseline; record task graph, token cost, critical path, merge errors, and coverage; avoid it when state and dependencies are tightly shared.

## Connections to academic work

The system connects to orchestrator-worker patterns, multi-agent debate and vote counterevidence, More Agents Is All You Need, AgentFlow, and MACE exploration. The cost warning aligns with AI Agents That Matter.

## Verification notes

The canonical page's benefits, architecture, quantitative claims, token costs, and poor-fit conditions were checked on 2026-09-04. Percentages are reported as company measurements, not independent facts.
