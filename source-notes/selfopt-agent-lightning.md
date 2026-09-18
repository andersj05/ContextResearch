---
title: "Agent Lightning v1.0"
author_or_org: "Microsoft"
date: "2026-09-04"
source_type: "official-implementation-evidence"
url: "https://github.com/microsoft/agent-lightning"
version_or_commit: "v1.0.1 (2026-08-24); main commit 218f1f7c0bac0800de4d5a4e5e6f61cf7b5038b4 (2026-09-02)"
accessed: "2026-09-04"
review_status: "reviewed"
evidence_confidence: "high-for-v1-architecture-medium-for-reported-training-effects"
license_or_access_notes: "MIT; v1.0 is a complete redesign and pre-v1 behavior lives on the v0.x branch"
---

# selfopt-agent-lightning — Agent Lightning v1.0

## Why this source is in the corpus

Agent Lightning is a boundary case for “self-improving harnesses.” Its current architecture trains model policy weights from trajectories produced by real agent harnesses while intentionally leaving tools, context construction, control flow, and environment in the loop and externally owned.

## System or claim described

Version 1.0 connects arbitrary agents to rollout RL through an OpenAI-compatible gateway. A Trainer creates rollout work, a Controller launches agents locally or as Kubernetes Jobs, and the Gateway captures exact model interactions as training data.

## Architecture / mechanism

The Trainer runs `verl` and vLLM and updates the policy. Each rollout carries a dataset input and is launched by a Controller using a local Python agent class or rendered Kubernetes Job template. Agents call the model through the Gateway, which records prompt/response token sequences and rewards. In trajectory aggregation mode, consecutive calls are merged only when the next prompt has the exact prior prompt+response token prefix; intervening tool observations are retained as context but masked from policy loss. Transition mode instead trains on each call separately. Async collection, pause/drain behavior, timeouts, and rollout failure states are configurable.

## Empirical evidence

The repository includes end-to-end examples for GSM8K, ScienceWorld, search, LLM-in-sandbox, multimodal QA, and coding agents, plus a project-authored SWE-bench result. Those materials support reproducibility work but do not isolate RL, data cleaning, reward design, base model, gateway, and harness effects without ablation.

## Mathematical or formal content

When rollout \(R\) yields \(n_R\) aggregated training rows with row losses \(\ell_{Rj}\), per-rollout mean normalization corresponds to

\[
L_R=\frac{1}{n_R}\sum_{j=1}^{n_R}\ell_{Rj},
\qquad
L=\frac{1}{|\mathcal R|}\sum_{R\in\mathcal R}L_R.
\]

The same rollout-level advantage is used across rows from one rollout, preventing long multi-call trajectories from receiving more weight merely because aggregation emitted more rows. The policy update is implemented through the upstream `verl` PPO stack rather than a novel harness-search objective.

## What is directly evidenced

**Official sources:** [repository](https://github.com/microsoft/agent-lightning), [documentation](https://microsoft.github.io/agent-lightning/), [v1.0.1 release](https://github.com/microsoft/agent-lightning/releases/tag/v1.0.1), [pinned v1 README/architecture](https://github.com/microsoft/agent-lightning/blob/218f1f7c0bac0800de4d5a4e5e6f61cf7b5038b4/README.md), [pinned trainer configuration and aggregation semantics](https://github.com/microsoft/agent-lightning/blob/218f1f7c0bac0800de4d5a4e5e6f61cf7b5038b4/docs/20-trainer-configuration.md), [pinned trainer source](https://github.com/microsoft/agent-lightning/blob/218f1f7c0bac0800de4d5a4e5e6f61cf7b5038b4/agentlightning/verl/trainer.py), and [v1 technical report](https://arxiv.org/abs/2608.17528).

## What is interpretation or advocacy

“Training agents with real harnesses” means the harness supplies the rollout environment and observations. The optimized artifact in v1 is primarily the model policy checkpoint, not automatically rewritten harness source, prompts, tools, or topology. It is therefore a comparator/boundary, not evidence of harness design automation.

## Limitations, incentives, and likely biases

Reproduction requires a compatible CUDA/`verl`/vLLM stack, model checkpoints, distributed resources, exact reward functions, datasets, controller templates, and gateway settings. Kubernetes Jobs provide orchestration and isolation boundaries but are not automatically a hardened sandbox. Reward hacking and credit assignment remain task-specific. Version 1.0 was completely redesigned; mechanisms from the older Agent Lightning paper/code must be cited against the `v0.x` branch rather than inferred for v1.

## Transferable engineering lessons

Keep policy learning and harness evolution distinct in experimental design. Preserve exact token sequences across gateway boundaries, normalize variable-length rollouts, mask environment observations appropriately, and version the controller/harness alongside the learned checkpoint.

## Connections to academic work

Agent Lightning connects agentic RL, PPO, off-policy rollout infrastructure, trajectory aggregation, and credit assignment. It complements HarnessDev-style source evolution and GEPA-style artifact mutation by optimizing weights while the external harness remains fixed.

## Verification notes

Release metadata, v1 architecture, trainer configuration, rollout/aggregation description, and representative trainer source were inspected through commit `218f1f7c0bac0800de4d5a4e5e6f61cf7b5038b4` for the 2026-09-04 cutoff. No v0.x mechanisms were silently carried into this note.
