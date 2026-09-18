---
title: "Effective Harnesses for Long-Running Agents"
author_or_org: "Anthropic"
date: "2025-11-26"
source_type: "engineering-blog"
url: "https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents"
version_or_commit: "web version accessed 2026-09-04"
accessed: "2026-09-04"
review_status: "reviewed"
evidence_confidence: "medium"
---

# anthropic-2025-long-running-agents — Effective Harnesses for Long-Running Agents

## Why this source is in the corpus

This is a concrete design for crossing context-window boundaries while keeping a multi-session software project recoverable and testable.

## System or claim described

The harness uses an initializer session to construct a feature ledger and operating environment, followed by coding sessions that implement one feature, verify the application, commit a clean state, and leave structured handoff notes.

## Architecture / mechanism

The initializer writes `init.sh`, a progress log, an initial Git commit, and a JSON feature list whose items begin failing. Later sessions read the working directory, Git history, progress log, and feature ledger; start and smoke-test the application; choose one high-priority unfinished feature; make incremental progress; verify it end to end; update only its pass status; commit; and leave a summary.

## Empirical evidence

The post reports internal experimentation and a Claude-like application example with more than 200 features. It identifies four observed failures—premature victory, dirty handoffs, premature pass labels, and repeated rediscovery of how to run the app—and maps each to a harness artifact. No task count, control group, effect size, or uncertainty is supplied.

## Mathematical or formal content

The feature ledger is a monotone candidate progress vector only if agents cannot delete or silently weaken requirements. Git supplies recoverable state transitions. Completion is a conjunction over verified features, so weak or agent-editable tests break the logical implication from all flags true to product correctness.

## What is directly evidenced

The page includes prompts, sample artifacts, step sequences, a failure-to-intervention table, and example browser verification. It demonstrates an implementable handoff protocol.

## What is interpretation or advocacy

Claims that one-feature increments or JSON are generally optimal are experience-based. A feature ledger may overconstrain refactors, and a fresh agent is not necessarily statistically independent of its predecessor.

## Limitations, incentives, and likely biases

The example is a generated application under Anthropic tooling. Evaluation is author-judged and selected. Agent-written requirements and tests can collude. Compute and defect costs are absent. The post explicitly leaves single-versus-specialized-agent architecture unresolved.

## Transferable engineering lessons

Separate initialization from continuation, make handoffs executable rather than narrative only, begin each session with recovery and smoke tests, constrain how success criteria may change, and commit small recoverable states.

## Connections to academic work

This pattern connects to external memory, checkpointed workflows, deterministic harness contracts, context handoff, Voyager-style skills, and long-task time-horizon evaluation.

## Verification notes

The canonical page's initializer, feature-list, incremental-progress, testing, session-recovery, failure table, and future-work sections were checked on 2026-09-04.
