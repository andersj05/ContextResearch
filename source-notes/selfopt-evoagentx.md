---
title: "EvoAgentX"
author_or_org: "ANative Lab"
date: "2026-09-04"
source_type: "official-implementation-evidence"
url: "https://github.com/ANative-Lab/EvoAgentX"
version_or_commit: "v0.1.4 (2026-06-28); main commit d77fd6b9a3e76c8dd83bebe3374c53a3f5d16f54 (2026-08-27)"
accessed: "2026-09-04"
review_status: "reviewed"
evidence_confidence: "high-for-inspected-components-medium-for-framework-wide-claims"
license_or_access_notes: "Root LICENSE begins MIT; GitHub metadata reports NOASSERTION because the file also contains third-party notices"
---

# selfopt-evoagentx — EvoAgentX

## Why this source is in the corpus

EvoAgentX is a current integration framework that exposes multiple optimization mechanisms behind a shared agent/workflow surface. Its MAP-Elites implementation adds a quality-diversity mechanism not represented by purely best-score search.

## System or claim described

The project supports automatic workflow generation and a collection of optimizers including AFlow, TextGrad, EvoPrompt, MIPRO, SEW, and MAP-Elites. It should be treated as a separately maintained, similarly named project; no official succession relationship to `siyuyuan/evoagent` was verified.

## Architecture / mechanism

The workflow generator asks a task planner to decompose a goal into typed subtasks, constructs edges when one subtask's named outputs match another's inputs, and asks an agent generator to assign or create agents for each node. Optimizers act on different artifacts. The generic MAP-Elites optimizer samples a registered parameter configuration or mutates one parameter from a randomly selected archive member, runs the configured program/evaluator, maps evaluator-supplied behavioral features to a discretized cell, and retains the highest-fitness configuration in each cell.

## Empirical evidence

The repository provides tutorials, examples, tests, and implementations for its optimizer set. These directly evidence API breadth and individual mechanisms; they do not make results from heterogeneous optimizers comparable without holding program, evaluator, data, model, and budget fixed.

## Mathematical or formal content

For behavior descriptor \(z(c)\) discretized to cell \(k\), MAP-Elites maintains

\[
A[k]=\arg\max_{c:\,\operatorname{bin}(z(c))=k} f(c).
\]

This optimizes archive coverage and within-cell quality rather than only a single global incumbent. The implemented mutation changes one registered configuration key at a time.

## What is directly evidenced

**Official sources:** [repository](https://github.com/ANative-Lab/EvoAgentX), [documentation](https://evoagentx.github.io/EvoAgentX/), [v0.1.4 release](https://github.com/ANative-Lab/EvoAgentX/releases/tag/v0.1.4), [pinned optimizer directory](https://github.com/ANative-Lab/EvoAgentX/tree/d77fd6b9a3e76c8dd83bebe3374c53a3f5d16f54/evoagentx/optimizers), [pinned MAP-Elites optimizer](https://github.com/ANative-Lab/EvoAgentX/blob/d77fd6b9a3e76c8dd83bebe3374c53a3f5d16f54/evoagentx/optimizers/map_elites_optimizer.py), [pinned AFlow port](https://github.com/ANative-Lab/EvoAgentX/blob/d77fd6b9a3e76c8dd83bebe3374c53a3f5d16f54/evoagentx/optimizers/aflow_optimizer.py), and [pinned workflow generator](https://github.com/ANative-Lab/EvoAgentX/blob/d77fd6b9a3e76c8dd83bebe3374c53a3f5d16f54/evoagentx/workflow/workflow_generator.py).

## What is interpretation or advocacy

“Self-evolving ecosystem” is umbrella framing. Some components generate a workflow once; others tune prompts, code, or registered parameters. These are distinct treatments and should not be collapsed into one self-improvement claim.

## Limitations, incentives, and likely biases

Rapid development makes release-versus-main behavior important. The workflow generator declares a reviewer/refinement component, but its automatic initialization is TODO/commented out at the inspected pin. Edge inference by matching parameter names is a heuristic, not semantic dependency validation. Integrated optimizer names can inherit limitations from their upstream algorithms and provider APIs.

## Transferable engineering lessons

A common optimizer interface is valuable only when it records the actual optimized artifact, proposal distribution, evaluator, archive/acceptance policy, and budget. Quality-diversity archives preserve complementary designs that a single-score incumbent would discard.

## Connections to academic work

EvoAgentX bridges MAP-Elites/quality diversity, prompt optimization, workflow search, and agent generation. Its AFlow and MIPRO integrations make provenance and upstream-version recording especially important.

## Verification notes

The release, root license text, optimizer registry, MAP-Elites implementation, AFlow port, and workflow generator were inspected through commit `d77fd6b9a3e76c8dd83bebe3374c53a3f5d16f54` for the 2026-09-04 cutoff.
