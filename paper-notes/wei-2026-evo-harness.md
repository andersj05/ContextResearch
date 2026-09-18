---
title: "Evo-Harness: Context-to-Harness Skill Compilation for Self-Evolving Agents"
authors: ["Tianxin Wei", "Zhan Shi", "Minhua Lin", "Bing He", "Zewen Liu", "Yisi Sang", "Yuanchen Bei", "Xuying Ning", "Jiaru Zou", "Ting-Wei Li", "Xiao Lin", "Yanjun Zhao", "Chi Wang", "Benoit Dumoulin", "Dakuo Wang", "Jingrui He", "Hanqing Lu"]
year: 2026
venue: "preprint"
source_type: "preprint"
paper_url: "https://arxiv.org/abs/2608.15071"
pdf_path: "papers/academic/wei-2026-evo-harness.pdf"
accessed: "2026-09-04"
review_status: "skimmed"
evidence_confidence: "high"
---

# wei-2026-evo-harness — Evo-Harness: Context-to-Harness Skill Compilation for Self-Evolving Agents

## Why this source is in the corpus

Directly studies reusable harness components, outer-loop optimization, self-modification, or the statistical controls needed to decide whether an update is a real improvement.

## Research question

Can grounded failure experience be compiled into reusable natural-language harness skills that transfer across tasks and models?

## Harness mechanism studied

A selector retrieves stored skills, an injector adds them to context, and an evolver chooses Add/Merge/Revise/Skip operations from verifier-grounded feedback; accepted skills persist across later runs.

## Method and experimental setup

Evo-Harness trains/evolves harness skills on several agent benchmarks, compares no-evolve and XSkill, tests strong executors, ablates feedback source and granularity, and evaluates same- versus cross-model transfer.

## Main findings

- Table 1 reports Opus no-evolve 29.54/62.92/63.67/72.73/72.50 versus Evo-Harness 34.02/73.03/67.00/76.97/76.25 on CL/TB2/SWE/tau/WebArena; Table 2 gives strong-model average gains +3.7, +4.5, +3.8 but only +1.1 for Kimi and +0.8 for GPT-OSS.
- Regressions include Opus EDS -2.5, Kimi RSA -0.7, GPT-OSS EDS -1.0; Table 4 self-generated feedback is below no-evolve on CL 27.96 versus 29.54 and SWE 61.67 versus 63.67, and Sonnet transfer falls 58.0→55.3/55.7.

## Mathematical content

Skill state H_t is updated by a discrete edit operator selected from Add/Merge/Revise/Skip based on traces and feedback; the paper estimates score differences but supplies no safe-improvement, transfer, or retrieval-consistency theorem.

## Evidence quality and limitations

2026 preprint; verifier/ground-truth feedback is load-bearing, effects shrink for some strong models, negative task and transfer cells occur, retrieval/selection adds context cost, and repeated benchmark evolution can overfit.

## Important implementation details

Retrieve task-relevant skill entries, inject them into the executor context, collect standardized external failure feedback, ask an evolver to add/merge/revise/skip, persist accepted skills with provenance, and reevaluate across executor models.

## Claims this source supports

Grounded feedback can compile experience into reusable harness text and produce positive average gains across several strong executors.

## Claims this source weakens or contradicts

Decisively weakens self-feedback and universal-transfer memes: ungrounded feedback and some cross-model deployments perform worse than no evolution.

## Relevance to a mathematics paper

Supports a discrete-state update model with model-by-skill interactions, negative-transfer probability, and feedback-quality as a causal moderator.

## Connections to other sources

See the category and claim-level cross-references in [`INDEX.md`](INDEX.md) and the synthesis documents.

## Verification notes

Local PDF Tables 1, 2, and 4, update operators, feedback and transfer ablations, negative cells, and limitations were checked; 2026 preprint findings were not independently replicated. The archived file parsed successfully: 16 pages, 59840 extractable characters, SHA-256 `41476396f4eab1517395672cc204db8915ae4f41ed363bfa0915b5f81b4824e5`.
