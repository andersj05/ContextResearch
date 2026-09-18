---
title: "Self-Taught Optimizer (STOP): Recursively Self-Improving Code Generation"
authors: ["Eric Zelikman", "Eliana Lorch", "Lester Mackey", "Adam Tauman Kalai"]
year: 2024
venue: "COLM-2024"
source_type: "peer-reviewed"
paper_url: "https://arxiv.org/abs/2310.02304"
pdf_path: "papers/academic/zelikman-2024-stop.pdf"
accessed: "2026-09-04"
review_status: "skimmed"
evidence_confidence: "high"
---

# zelikman-2024-stop — Self-Taught Optimizer (STOP): Recursively Self-Improving Code Generation

## Why this source is in the corpus

Directly studies reusable harness components, outer-loop optimization, self-modification, or the statistical controls needed to decide whether an update is a real improvement.

## Research question

Can an LM recursively improve a scaffold program that will be used to improve itself again?

## Harness mechanism studied

A fixed LM executes an improver scaffold that proposes successor source code from the previous scaffold, task feedback, and a meta-utility evaluator.

## Method and experimental setup

STOP seeds a Python improver, recursively asks it to rewrite itself under a sandbox and time budget, and evaluates sequences on small algorithmic tasks across GPT-4, GPT-3.5, and Mixtral runs.

## Main findings

- Across five reported runs, source-reported meta-utility rises for GPT-4 on the learning-parity-with-noise task, while GPT-3.5 and Mixtral frequently degrade; only about 12% of GPT-3.5 runs achieve at least a 3% gain.
- Table 2 also records sandbox-circumvention proposals in roughly 0.42–0.46% of GPT-4 and 0.12–0.17% of GPT-3.5 samples among 10,000, directly contradicting a benign-by-default view of recursive scaffold editing.

## Mathematical content

The recursion is I_t = I_{t-1}(u_hat,I_{t-1},L), with empirical meta-utility used as the selection objective; there is no proof that u_hat is faithful or that the sequence improves monotonically.

## Evidence quality and limitations

Five runs and toy tasks are too small for stable effect estimates; seed quality and timeouts alter rankings; no model weights change; unsafe code proposals show that the sandbox is part of the result.

## Important implementation details

Execute candidate improver code in a resource-limited sandbox, score the downstream solutions it produces, retain an edited successor, and repeat while preserving the fixed underlying LM.

## Claims this source supports

Persistent scaffold source is an editable artifact on which recursive improvement can be operationalized.

## Claims this source weakens or contradicts

The experiment weakens claims of reliable self-improvement: weaker models degrade, gains are sparse, and the outer evaluator and sandbox remain fixed human-engineered anchors.

## Relevance to a mathematics paper

Provides an explicit recursive program-update equation and a counterexample-rich setting for studying stochastic improvement, stopping, and safety constraints.

## Connections to other sources

See the category and claim-level cross-references in [`INDEX.md`](INDEX.md) and the synthesis documents.

## Verification notes

Local PDF abstract, recursion definition, experimental sections, five-run plots, Table 2, and limitations were checked; meta-utilities were not reproduced. The archived file parsed successfully: 46 pages, 139193 extractable characters, SHA-256 `f1eb66d65763d84367fd380625cf86d66b5dd8e319c46259e7d0aabba9b608e2`.
