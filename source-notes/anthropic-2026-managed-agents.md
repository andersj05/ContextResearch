---
title: "Scaling Managed Agents: Decoupling the Brain from the Hands"
author_or_org: "Anthropic"
date: "2026-04-08"
source_type: "engineering-blog"
url: "https://www.anthropic.com/engineering/managed-agents"
version_or_commit: "web version accessed 2026-09-04"
accessed: "2026-09-04"
review_status: "reviewed"
evidence_confidence: "medium"
---

# anthropic-2026-managed-agents — Decoupling Brain, Hands, and Session

## Why this source is in the corpus

This production architecture cleanly separates three objects that research papers often conflate: durable session history, the replaceable inference harness, and privileged execution environments.

## System or claim described

Managed Agents virtualizes a session as an append-only event log, a harness as the model/tool control loop, and a sandbox or external service as a hand. Each may fail, scale, move, or be replaced without sharing implementation state.

## Architecture / mechanism

Stateless harness workers recover with a session identifier and event replay. Sandboxes are provisioned lazily through a small execution interface. Credentials live with resources or in a vault; an MCP proxy uses a session token to perform authorized calls without exposing underlying credentials to model-generated code or the harness. The full event log remains outside the context window and can be sliced, replayed, or transformed into model context.

## Empirical evidence

Anthropic reports that decoupling eager containers reduced median time to first token by roughly 60% and p95 by more than 90%. This is a production before-after observation with no public workload distribution or confidence interval.

## Mathematical or formal content

The architecture separates durable state `S`, controller `H`, and execution endpoints `E_i`. Crash recovery is possible when every committed transition is in `S`; least privilege requires secrets to be non-reachable from the sandbox state even if model policy is adversarial.

## What is directly evidenced

The post describes interfaces, failure recovery, credential topology, lazy provisioning, external context access, and latency deltas from the deployed system.

## What is interpretation or advocacy

The operating-system analogy and meta-harness framing are architectural judgments. A generic string-returning execution interface may be insufficient for typed, streaming, or transactional tools without further contracts.

## Limitations, incentives, and likely biases

No public code, load distribution, baseline details, failure-rate study, or independent security test is supplied. The article promotes a hosted Anthropic service. Vault separation reduces exposure but does not prove authorization correctness.

## Transferable engineering lessons

Keep secrets unreachable from untrusted execution, externalize durable logs from ephemeral harness workers, make context a recoverable projection, provision expensive environments on demand, and version every interface between controller and executor.

## Connections to academic work

The design connects to event sourcing, deterministic-harness contracts, MemGPT-style external state, indirect prompt injection, AgentDojo, and the host/sandbox boundary in the Stencil playbook.

## Verification notes

The canonical page's virtualization, recovery, security, external-context, latency, and many-brains/many-hands sections were checked on 2026-09-04.
