---
title: "Archon: Inference-Time Architecture Search"
author_or_org: "Scaling Intelligence"
date: "2026-09-04"
source_type: "official-implementation-evidence"
url: "https://github.com/ScalingIntelligence/Archon"
version_or_commit: "main commit 07114d77af283b6e8185a49ebf22216fdbbf2a55 (2025-03-07); no GitHub releases"
accessed: "2026-09-04"
review_status: "reviewed"
evidence_confidence: "high-for-code-defects-low-for-as-shipped-reproducibility"
license_or_access_notes: "Apache-2.0"
---

# selfopt-archon — Archon ITAS

## Why this source is in the corpus

Archon represents discrete inference-time architecture search over model ensembles and generator/ranker/critic/fuser layers. It is also a high-value negative implementation finding: the pinned ITAS entry point contains multiple defects that prevent accepting the intended algorithm as reproducibly executable without repair.

## System or claim described

Archon expresses inference architectures as JSON layers. ITAS is intended to rank candidate base models, search architectural hyperparameters under an inference-call cap, score candidates on MT-Bench or Arena-Hard, and rescore top configurations on a larger sample.

## Architecture / mechanism

The search first constructs single-model configurations and obtains a power ranking using an LM judge against a baseline. It maps five search choices—number of top models, samples, and up to three fuser-layer widths—to an Archon JSON configuration. The code offers random, grid, and Gaussian-process Bayesian optimization. The objective is a pairwise benchmark score; configurations exceeding `maximum_inference_calls` receive `-1`. Intended finalists are regenerated and judged on a final-ranking sample.

## Empirical evidence

The repository includes many manually named configurations and benchmark integrations. These evidence the design space and runtime component library, but the automated ITAS driver at the inspected pin cannot be treated as a successful reproduction path because of deterministic source defects.

## Mathematical or formal content

ITAS seeks

\[
z^*=\arg\max_{z\in\mathcal Z}\hat f(z)
\quad\text{subject to}\quad C(z)\le C_{\max},
\]

where \(z\) is a discrete architecture, \(C\) sums configured model samples, and \(\hat f\) is an LM-judged benchmark score. The Bayesian path embeds integer choices in continuous bounds and rounds proposals to the nearest allowed value.

## What is directly evidenced

**Official sources:** [repository](https://github.com/ScalingIntelligence/Archon), [pinned ITAS README](https://github.com/ScalingIntelligence/Archon/blob/07114d77af283b6e8185a49ebf22216fdbbf2a55/src/archon/itas_algorithms/README.md), [pinned ITAS implementation](https://github.com/ScalingIntelligence/Archon/blob/07114d77af283b6e8185a49ebf22216fdbbf2a55/src/archon/itas_algorithms/itas_algorithm.py), [pinned power ranker](https://github.com/ScalingIntelligence/Archon/blob/07114d77af283b6e8185a49ebf22216fdbbf2a55/src/archon/itas_algorithms/power_ranker.py), and [pinned search example](https://github.com/ScalingIntelligence/Archon/blob/07114d77af283b6e8185a49ebf22216fdbbf2a55/src/archon/itas_algorithms/search_configs/example_search_config.json).

## What is interpretation or advocacy

Inference-time architecture search is a useful framing for ensemble pipelines. However, the large configuration collection includes manually authored designs; it does not establish that ITAS generated or selected every showcased architecture.

## Limitations, incentives, and likely biases

At the pin, `main()` calls undefined lowercase `itas` instead of class `ITAS`; fuser construction calls `list.append` with two arguments; final “top” candidates are sorted ascending by score; and `sample_top_k` is searched but generator samples remain hard-coded to one. The README additionally requires cloning a FastChat fork into the package. Historical model endpoints, LM judging, tiny configurable search samples, no tagged release, and no push after 2025-03-07 further limit reproduction.

## Transferable engineering lessons

Automated architecture search needs smoke tests that execute every nonzero layer path, verify that every search variable affects the serialized candidate, and assert that final ranking direction is correct. Configuration abundance is not evidence of a working optimizer.

## Connections to academic work

Archon connects mixture-of-agents inference, best-of-N sampling, critique/ranking/fusion pipelines, Bayesian optimization, and neural architecture search. AgentOpt addresses a narrower but more actively implemented model-assignment problem.

## Verification notes

Repository metadata, ITAS driver, power-ranker, and example configuration were inspected at commit `07114d77af283b6e8185a49ebf22216fdbbf2a55` for the 2026-09-04 cutoff. Defects above are direct observations of the pinned code, not inferred from issue reports.
