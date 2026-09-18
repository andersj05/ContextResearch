---
title: "Harness Updating Is Not Harness Benefit: Disentangling Evolution Capabilities in Self-Evolving LLM Agents"
authors: ["Minhua Lin", "Juncheng Wu", "Zijun Wang", "Zhan Shi", "Yisi Sang", "Bing He", "Zewen Liu", "Tianxin Wei", "Zongyu Wu", "Zhiwei Zhang", "Dakuo Wang", "Xiang Zhang", "Benoit Dumoulin", "Cihang Xie", "Yuyin Zhou", "Suhang Wang", "Hanqing Lu"]
year: 2026
venue: "preprint"
source_type: "preprint"
paper_url: "https://arxiv.org/abs/2605.30621"
pdf_path: "papers/academic/lin-2026-harness-updating.pdf"
accessed: "2026-09-04"
review_status: "skimmed"
evidence_confidence: "high"
---

# lin-2026-harness-updating — Harness Updating Is Not Harness Benefit: Disentangling Evolution Capabilities in Self-Evolving LLM Agents

## Why this source is in the corpus

Directly studies reusable harness components, outer-loop optimization, self-modification, or the statistical controls needed to decide whether an update is a real improvement.

## Research question

How much measured improvement comes from the evolver that edits a harness versus the base agent that must activate and follow it?

## Harness mechanism studied

A factorial design holds tasks and harness-update protocol fixed while varying evolver and executor backbones; separate metrics quantify update quality and realized harness benefit.

## Method and experimental setup

The study evaluates several evolvers and seven base agents on three benchmarks, records whether skills are activated and adhered to, and decomposes score changes into delta_update and delta_benefit.

## Main findings

- The maximum performance spread among evolvers is only 3.1 points, with Qwen-3.5-9B versus Opus SkillsBench examples 3.8 versus 2.3; base-agent gaps are 18.6–35.2 points.
- SWE harness benefit ranges Qwen-32B +4.4, Qwen-235B +19.3, GPT-OSS +15.8, Haiku +2.4, Sonnet +2.8, Opus +2.6; weak agents activate skills about 25% versus roughly 96% for strong agents, and adherence decays about fourfold over a trajectory.

## Mathematical content

The paper defines separate difference estimands for the artifact update and executor-realized benefit in a two-factor model; the empirical interaction is large, but no universal ordering or causal identification beyond the tested factorial cells is claimed.

## Evidence quality and limitations

2026 preprint; only three benchmarks and seven models, proprietary models can change, activation/adherence classifiers may err, and the tested update protocol may not cover richer code- or graph-editing evolvers.

## Important implementation details

Cross every evolver with multiple frozen base agents, save the same learned harness artifact, measure task score with/without it, classify retrieval/activation/adherence events, and report interaction rather than only aggregate gain.

## Claims this source supports

Harness effectiveness is a model-by-artifact interaction and executor competence is often more important than optimizer prestige.

## Claims this source weakens or contradicts

Decisively weakens the meme that a stronger evolver automatically yields a better agent or that an improved artifact guarantees realized benefit.

## Relevance to a mathematics paper

Provides the corpus’s clearest factorial estimands for updater effect, harness benefit, activation probability, adherence decay, and interaction.

## Connections to other sources

See the category and claim-level cross-references in [`INDEX.md`](INDEX.md) and the synthesis documents.

## Verification notes

Local PDF definitions, factorial protocol, primary and SWE tables, activation/adherence analyses, and limitations were checked; 2026 claims remain provisional and were not replicated. The archived file parsed successfully: 24 pages, 82726 extractable characters, SHA-256 `a3a09f90dc278f1c6ceee5a3f7bf807b5a92b642cbcb0123d20b824a0e880d6b`.
