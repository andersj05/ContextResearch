---
title: "AgentOpt"
author_or_org: "AgentOptimizer"
date: "2026-09-04"
source_type: "official-implementation-evidence"
url: "https://github.com/AgentOptimizer/agentopt"
version_or_commit: "v0.1.0 (2026-03-23); main commit 08b2d2c7fe370c884d956afbe540a09abc163c27 (2026-07-18)"
accessed: "2026-09-04"
review_status: "reviewed"
evidence_confidence: "high-for-selection-mechanisms-medium-for-young-runtime"
license_or_access_notes: "Apache-2.0"
---

# selfopt-agentopt — AgentOpt

## Why this source is in the corpus

AgentOpt isolates a narrower optimization variable than workflow-search systems: which model should serve each named LLM call site in an otherwise fixed agent. It is useful both as a deployable mechanism and as a control for claims that require changing prompts, tools, memory, or topology.

## System or claim described

The library intercepts LLM HTTP requests, records model/token/latency/cost attribution, evaluates candidate per-node model assignments on a user dataset, and returns the best mapping under accuracy or an optional cost/latency-penalized objective.

## Architecture / mechanism

Candidate models are specified for each agent node. The selector instantiates/runs the user's agent under a mapping, attributes calls using `contextvars`, caches responses by request-body hash, scores outputs with a user `eval_fn`, and aggregates accuracy, latency, and estimated price. Implemented selectors include exhaustive Cartesian search, progressive arm elimination, Matrix-UCB over combination × datapoint cells, a low-rank Matrix-UCB variant, and mixed-input Gaussian-process Bayesian optimization. Evaluation can be sequential or concurrency-limited async.

A separate router interface can swap the model on each HTTP call using prompt/session/history context. At the inspected pin, uniform random routing is the only built-in policy; learned selection-to-routing is roadmap work.

## Empirical evidence

The repository provides framework examples and project-authored benchmark results. These directly support integration and instrumentation claims but not universal superiority of a selected mapping: outcomes depend on the user's dataset, metric, candidate models, prices, sampling parameters, and cache policy.

## Mathematical or formal content

For node candidate sets \(M_1,\ldots,M_k\), exhaustive search contains \(\prod_i|M_i|\) mappings. The optional per-sample objective is

\[
J=\operatorname{score}
-\lambda_c\operatorname{norm}(\operatorname{cost})
-\lambda_\ell\operatorname{norm}(\operatorname{latency}).
\]

Matrix-UCB allocates observations over mapping–datapoint cells, while the Bayesian selector fits a GP surrogate and uses expected improvement. These economize evaluations but do not remove adaptive selection bias.

## What is directly evidenced

**Official sources:** [repository](https://github.com/AgentOptimizer/agentopt), [documentation](https://agentoptimizer.github.io/agentopt/), [v0.1.0 release](https://github.com/AgentOptimizer/agentopt/releases/tag/v0.1.0), [selection algorithm documentation](https://github.com/AgentOptimizer/agentopt/blob/08b2d2c7fe370c884d956afbe540a09abc163c27/docs/concepts/algorithms.md), [pinned selector implementations](https://github.com/AgentOptimizer/agentopt/tree/08b2d2c7fe370c884d956afbe540a09abc163c27/src/agentopt/model_selection), [pinned interception/tracking code](https://github.com/AgentOptimizer/agentopt/tree/08b2d2c7fe370c884d956afbe540a09abc163c27/src/agentopt/proxy), [router documentation](https://github.com/AgentOptimizer/agentopt/blob/08b2d2c7fe370c884d956afbe540a09abc163c27/docs/api/router.md), and [pinned random router](https://github.com/AgentOptimizer/agentopt/blob/08b2d2c7fe370c884d956afbe540a09abc163c27/src/agentopt/routing/random_policy.py).

## What is interpretation or advocacy

AgentOpt optimizes model allocation, not the whole agent. Any gain should be attributed to the mapping/search procedure under a fixed harness. The router abstraction permits classifiers or bandits supplied by users, but those policies are not shipped as learned built-ins at this pin.

## Limitations, incentives, and likely biases

Provider behavior and pricing change over time. HTTP caching improves cost/repeatability but freezes responses that would otherwise be stochastic, changing the evaluated distribution. Subprocess interception uses mitmproxy and a local CA trust boundary. Routing v1 is same-provider only; Gemini's URL-encoded model is not rewritten. Only random routing is wired to the CLI, and the documented selection-to-routing loop is not implemented. The project is active but at an early `v0.1.0` release.

## Transferable engineering lessons

Model choice per call site is a separable treatment. Log exact mappings, provider/model versions, cache hits, token counts, latency sampling, price table, metric, data split, and search budget before comparing it with structural harness changes.

## Connections to academic work

AgentOpt connects best-arm identification, matrix bandits, Bayesian optimization, cost-aware inference, and model routing. Archon searches a broader ensemble topology; AgentOpt supplies a cleaner control when only model assignment should vary.

## Verification notes

Release metadata, algorithm documentation, selector implementations, proxy/tracker, cache, and router code were inspected through commit `08b2d2c7fe370c884d956afbe540a09abc163c27` for the 2026-09-04 cutoff.
