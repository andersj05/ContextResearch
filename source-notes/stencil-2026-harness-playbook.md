---
title: "The Harness Playbook"
author_or_org: "Can Bölük / Stencil"
date: "2026-09-02"
source_type: "engineering-blog"
url: "https://stencil.so/blog/harness-playbook"
version_or_commit: "web version accessed 2026-09-04"
accessed: "2026-09-04"
review_status: "reviewed"
evidence_confidence: "medium"
---

# stencil-2026-harness-playbook — The Harness Playbook

## Why this source is in the corpus

This is the most detailed practitioner treatment found of a harness as a systems-engineering object rather than a thin model loop. It is a postmortem of `omp` and a design proposal for `omp²`, published two days before this corpus cutoff.

## System or claim described

The central claim is that a production harness owns unavoidable distributed-systems complexity: authoritative state, journaling, untrusted execution, concurrent jobs, control policy, provider compatibility, tool protocols, and multiple user interfaces. Its five design requirements are one authoritative session, a trusted host control plane, bounded work, explicit model/provider compatibility, and views that are projections of shared state.

## Architecture / mechanism

- One journal-derived session tree contains transcript, tool calls, jobs, settings, queues, and subagent state. Rewind, fork, resume, and replication are materializations or diffs of the same authority.
- The trusted host owns inference, policy, approvals, limits, routing, and journaling. A sandbox contains only a small execution stub, with bounded streams crossing the boundary.
- Tool calls, subagents, daemons, and background work share a cancellable process-like job abstraction rather than relying on cooperative cancellation alone.
- A compositional Director stack controls whether a proposed model yield is accepted, continued, or augmented with a temporary requirement such as a forced tool call.
- Provider quirks are compiled from a declarative capability taxonomy with explicit specificity and an unknown state, rather than scattered name checks.
- The permanent tool grammar should be small. A stable shell/code surface provides discovery and composition for the long tail.
- Controller and actor are separate: terminal, web, remote, and inspector clients render the same semantic component tree and patch stream.

## Empirical evidence

The article reports an appendix audit of 78 official extension examples: 60 were stateless and only two of 17 stateful examples were judged correct. It also reports a six-run microbenchmark in which restricting the permanent roster to five tools reduced median wall time to 36.6 seconds, versus 42.2 for Codex and 37.0 for Pi in the stated task. These are author-run diagnostics, not independent or general performance evaluations.

## Mathematical or formal content

The terminal protocol separates semantic block state, width-independent logical history, and physical scrollback. With finalized blocks `F_i`, current append-only block `W_j`, and emitted prefix length `e_j`, it defines

\[
L = F_1 \cdot F_2 \cdots F_c \cdot W_j[1..e_j].
\]

The claimed invariants are exactly-once ordered commitment, exclusion of mutable speculative snapshots from history, and resize independence of logical state. Appendix B embeds a TLA+ model and describes a safety theorem and conditional progress results. This corpus records the specification but has not independently model-checked it.

## What is directly evidenced

The page exposes concrete failure examples, source links, interfaces, state layouts, compatibility rules, benchmark protocol, and the full TLA+ text. It directly evidences how the author diagnosed and redesigned these systems.

## What is interpretation or advocacy

The game-engine analogy, the choice of an XML-like DOM, Python extensions, a Director stack, and a stable CLI/code surface are design judgments. They are plausible implementations of the invariants, not uniquely implied solutions.

## Limitations, incentives, and likely biases

The author is building the proposed replacement and has an incentive to emphasize flaws in predecessor designs. Several `omp²` components were still under construction. The extension audit does not use blinded independent labels, and the latency test has only six runs on one task. The post is too new for replication.

## Transferable engineering lessons

Define authority, replay, cancellation, privilege, compatibility precedence, and output bounds before adding product features. Treat a tool call as one durable lifecycle object. Make every temporary behavior explicit and bounded. Preserve unknown capability states. Keep irreversible state outside views and untrusted runtimes.

## Connections to academic work

The journal/state model connects to event sourcing and workflow semantics; the host/sandbox split to indirect prompt injection and AgentDojo; the small tool surface to Toolformer and tool-retrieval studies; the Director stack to finite-state and pushdown control; the TLA+ appendix to formal verification; and the skepticism about state examples to deterministic-harness work.

## Verification notes

All nine chapters and both appendices were inspected in the canonical page on 2026-09-04. Claims above are tied to the page's design-envelope, state, runtime, control-plane, inference, tool-surface, interface, and Appendix B sections. No PDF snapshot was generated because redistribution and rendering rights were not clear; the canonical URL is preserved instead.
