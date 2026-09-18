---
title: "GPTSwarm"
author_or_org: "metauto-ai"
date: "2026-09-04"
source_type: "official-implementation-evidence"
url: "https://github.com/metauto-ai/GPTSwarm"
version_or_commit: "main commit c23a827f561c934ce21dd950408f7606aa4a8821 (2026-02-05); no GitHub releases"
accessed: "2026-09-04"
review_status: "reviewed"
evidence_confidence: "high-for-edge-optimizer-low-for-node-optimizer-completeness"
license_or_access_notes: "MIT"
---

# selfopt-gptswarm — GPTSwarm

## Why this source is in the corpus

GPTSwarm supplies a mathematically explicit counterpoint to LM-written workflow search: it parameterizes inter-agent connectivity probabilistically and trains graph structure with a score-function estimator.

## System or claim described

The project represents a multi-agent system as a graph of nodes and seeks to improve it through edge-connectivity optimization and, separately, node prompt/meta-instruction optimization.

## Architecture / mechanism

Each potential edge has a trainable logit. The edge distribution samples a graph while rejecting cycle-forming edges, or samples a learned topological order before admitting forward edges. A batch of realized graphs is evaluated concurrently. Adam updates the logits from utilities and a moving-average baseline. The separate `MetaPromptOptimizer` asks an LM for revised constraints, executes an answer against Python tests, and returns the first passing revision within a retry budget; otherwise it retains the initial constraint.

## Empirical evidence

The repository includes task environments and experiment scripts, but its strongest evidence for this corpus is the inspectable stochastic graph optimizer. The node optimizer is not implementation-complete enough to support strong claims about retrieval-augmented prompt evolution.

## Mathematical or formal content

With sampled graph \(G_b\sim p_\theta\), utility \(U_b\), and baseline \(m_b\), the code minimizes

\[
L(\theta)=-\frac{1}{B}\sum_{b=1}^{B}
\log p_\theta(G_b)(U_b-m_b),
\]

the REINFORCE/score-function estimator. Cycle filtering makes the realized graph distribution order-dependent; the raw edge Bernoulli probabilities alone do not fully specify it.

## What is directly evidenced

**Official sources:** [repository](https://github.com/metauto-ai/GPTSwarm), [project site](https://gptswarm.org), [pinned edge optimizer](https://github.com/metauto-ai/GPTSwarm/blob/c23a827f561c934ce21dd950408f7606aa4a8821/swarm/optimizer/edge_optimizer/optimization.py), [pinned graph parameterization](https://github.com/metauto-ai/GPTSwarm/blob/c23a827f561c934ce21dd950408f7606aa4a8821/swarm/optimizer/edge_optimizer/parameterization.py), and [pinned node prompt optimizer](https://github.com/metauto-ai/GPTSwarm/blob/c23a827f561c934ce21dd950408f7606aa4a8821/swarm/optimizer/node_optimizer/prompt_optimizer.py).

The code directly evidences sampled DAGs, optional learned ordering, concurrent rollouts, policy-gradient updates, test-gated prompt replacement, and experiment artifact persistence.

## What is interpretation or advocacy

“Self-improving agents” is broader than the verified implementation. The edge optimizer learns connectivity for a fixed node set and evaluator; it does not invent arbitrary nodes, tools, memory policies, or containment mechanisms.

## Limitations, incentives, and likely biases

The estimator can have high variance and is sensitive to utility scaling, batch size, evaluator noise, and graph sampling order. In the node optimizer, `process_records` is literally `pass`, while the intended memory-retrieval logic is commented out; the generation path therefore does not implement the advertised sample retrieval. Historical APIs, local Python execution, no tagged release, and no push after 2026-02-05 further limit reproduction.

## Transferable engineering lessons

Topology is a separable optimization variable. Report the realized constrained graph distribution, utility baseline, optimizer seed, and variance across runs; do not attribute improvements to “the swarm” when only edges changed.

## Connections to academic work

GPTSwarm connects policy-gradient structure learning, stochastic neural architecture search, DAG scheduling, and multi-agent orchestration. Its incomplete prompt path contrasts with TextGrad/GEPA-style textual optimization.

## Verification notes

Repository metadata and the edge distribution, optimization loop, and node prompt optimizer were inspected at commit `c23a827f561c934ce21dd950408f7606aa4a8821` for the 2026-09-04 cutoff.
