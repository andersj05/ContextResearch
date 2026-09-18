---
title: "Quine: Realizing LLM Agents as Native POSIX Processes"
authors: ["Hao Ke"]
year: 2026
venue: "preprint"
source_type: "preprint"
paper_url: "https://arxiv.org/abs/2603.18030"
pdf_path: "papers/academic/ke-2026-quine.pdf"
accessed: "2026-09-04"
review_status: "fully-reviewed"
evidence_confidence: "medium"
---

# ke-2026-quine — Quine: Realizing LLM Agents as Native POSIX Processes

## Why this source is in the corpus

Directly treats the harness, its optimization, or its runtime semantics as the object of study.

## Research question

Can operating-system process semantics replace part of an application-level agent orchestrator?

## Harness mechanism studied

Agents map to POSIX processes: PID identity, streams and exit status as interface, process memory and filesystem as state, and fork-exec-exit as lifecycle.

## Method and experimental setup

Architecture paper plus reference implementation analyzes recursive delegation, renewal, shell composition, isolation, and the limits of process semantics.

## Main findings

- The design inherits mature isolation, scheduling, composition, and resource-control primitives from the kernel.
- It also shows that processes do not supply a complete cognitive runtime, especially task-relative worlds and revisable time.

## Mathematical content

The mapping is a labeled transition and process-algebra perspective; the paper proves no end-task performance advantage.

## Evidence quality and limitations

Single POSIX design, limited empirical benchmarking, operating-system isolation is configurable rather than absolute, and non-POSIX platforms differ.

## Important implementation details

Use OS processes as a trusted lifecycle substrate while specifying cognition, context, and rollback above that boundary.

## Claims this source supports

Some harness responsibilities can be delegated to mature systems primitives.

## Claims this source weakens or contradicts

Claims that a process abstraction alone solves memory, evaluation, or semantic rollback.

## Relevance to a mathematics paper

Provides unusually crisp operational semantics for identity, communication, and lifecycle.

## Connections to other sources

See the category and claim-level cross-references in [`INDEX.md`](INDEX.md) and the synthesis documents.

## Verification notes

Abstract, POSIX mapping, reference architecture, delegation examples, boundary analysis, and conclusion checked in the local PDF. The archived file parsed successfully: 10 pages, 51030 extractable characters, SHA-256 `ab9e29ad5aaf7ed9d805d72336bb8e53154c15c68dba2aec07dd146dfaa634e2`.
