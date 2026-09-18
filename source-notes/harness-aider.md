---
title: "Aider"
author_or_org: "Aider-AI"
date: "2026-09-04"
source_type: "official-implementation-evidence"
url: "https://github.com/Aider-AI/aider"
version_or_commit: "v0.86.0; main commit 5dc9490bb35f9729ef2c95d00a19ccd30c26339c"
accessed: "2026-09-04"
review_status: "reviewed"
evidence_confidence: "high-for-mechanism-medium-for-implications"
license_or_access_notes: "Apache-2.0"
---

# harness-aider — Aider

## Why this source is in the corpus

This implementation represents the **human-led-edit-loop** family in the comparative survey. It is included to describe a reproducible mechanism and its treatment variables, not to endorse the project or convert project-authored results into independent evidence.

## System or claim described

A human-led coding harness centered on repository mapping, constrained edit formats, validation, and Git-backed rollback.

## Architecture / mechanism

Aider is organized around an operator conversation rather than unattended task completion. It constructs a token-budgeted repository map using parsed symbols and a ranked dependency/reference graph, asks a model for edits in constrained formats, applies them, and can feed lint or test failures back into the next turn. Architect mode separates a reasoning/planning model from an editor model. Git integration creates checkpoints and supports undo.

## Empirical evidence

The inspected repository, documentation, and release records directly support the implementation description. They do not constitute a controlled, independent estimate of the harness's effect. Any project-authored benchmark or telemetry should be reproduced with a pinned model, prompt, environment, budget, and scorer before comparative use.

## Mathematical or formal content

The intervention is a mixed human–machine policy: proposed edits are sampled from \(\pi_\theta(\cdot\mid C(s_t))\), while acceptance, repair, and stopping include operator decisions. Human time and authority therefore belong in the estimand.

## What is directly evidenced

**Official sources:** [repository](https://github.com/Aider-AI/aider), [documentation](https://aider.chat/docs/), [repository map documentation](https://aider.chat/docs/repomap.html), [edit formats](https://aider.chat/docs/more/edit-formats.html), [benchmarks](https://aider.chat/docs/leaderboards/), [license](https://github.com/Aider-AI/aider/blob/main/LICENSE.txt).

The detailed comparison pins the inspected release or commit, license, loop/state design, action representation, context and memory policy, concurrency, containment, and observability surface.

## What is interpretation or advocacy

Aider suggests an alternative harness hypothesis: repository selection, change representation, validation feedback, and recoverability may matter more than autonomous step count. Architect/editor mode is a role decomposition, but not evidence of independent agents or a search procedure.

## Limitations, incentives, and likely biases

Host-repository execution is not a robust sandbox. There is no central durable multi-agent scheduler or general branch-concurrency semantics. Its leaderboard is project-authored and entangles model, edit format, prompting, and retry policy. **Confidence: high.**

Project documentation optimizes for adoption and correct use, not neutral causal comparison. Fast-moving release streams also make unversioned project names unreliable experimental treatments.

## Transferable engineering lessons

Include human authority, patch representation, repository retrieval, and rollback in the harness treatment; autonomy is not a monotone design objective.

## Connections to academic work

See the mechanism taxonomy in [`01-definitions-and-taxonomy.md`](../synthesis/01-definitions-and-taxonomy.md), the architecture analysis in [`02-architecture-and-design-patterns.md`](../synthesis/02-architecture-and-design-patterns.md), and the full implementation comparison in [`05-open-source-harnesses.md`](../synthesis/05-open-source-harnesses.md).

## Verification notes

The sources and pinned snapshot were inspected for the 2026-09-04 research cutoff. Version discontinuities and openness caveats are recorded in the full survey. No repository snapshot is redistributed here; the canonical source URL and commit or release identifier are retained.
