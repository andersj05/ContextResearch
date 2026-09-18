---
title: "SwarmAgentic: Towards Fully Automated Agentic System Generation via Swarm Intelligence"
authors: ["Yao Zhang", "Chenyang Lin", "Shijie Tang", "Haokun Chen", "Shijie Zhou", "Yunpu Ma", "Volker Tresp"]
year: 2025
venue: "EMNLP-2025"
source_type: "peer-reviewed"
paper_url: "https://arxiv.org/abs/2506.15672"
pdf_path: "papers/academic/zhang-2025-swarmagentic.pdf"
accessed: "2026-09-04"
review_status: "skimmed"
evidence_confidence: "high"
---

# zhang-2025-swarmagentic — SwarmAgentic: Towards Fully Automated Agentic System Generation via Swarm Intelligence

## Why this source is in the corpus

Directly studies reusable harness components, outer-loop optimization, self-modification, or the statistical controls needed to decide whether an update is a real improvement.

## Research question

Can particle-swarm-inspired natural-language search optimize agent roles and collaboration structures efficiently?

## Harness mechanism studied

Each particle encodes an agentic design in language; LM-generated velocity/update instructions combine personal-best and global-best designs, followed by benchmark fitness selection.

## Method and experimental setup

SwarmAgentic runs five particles for ten iterations, jointly edits agents and collaboration, and compares against manual agents and ADAS on reasoning and TravelPlanner while reporting training and deployment costs.

## Main findings

- TravelPlanner Table 2 reports final scores 3.3/32.2 for SwarmAgentic versus 1.1/8.9 for ADAS under GPT-3.5/GPT-4o settings; the advertised 261.8% relative gain is inflated by the tiny 8.9 comparator.
- Table 6 reports training cost $8.74 versus ADAS $11.10 and per-task validation/inference $0.567 versus $1.11, but only five-by-ten search and handcrafted language encodings are tested.

## Mathematical content

The update borrows PSO structure x_i^{t+1}=LanguageUpdate(x_i^t,p_i^best,g^best), but positions and velocities are textual and lack metric/vector-space PSO convergence guarantees.

## Evidence quality and limitations

Relative percentages exaggerate low baselines, LLM mutations can hallucinate incompatible designs, representations are hand-authored, comparisons may not equalize calls, and no independent seeds or sealed transfer establish robustness.

## Important implementation details

Maintain a population of textual agent/workflow specs, evaluate fitness, store each particle’s best and the global best, prompt an LM to synthesize the next design from these exemplars, and iterate.

## Claims this source supports

Population diversity and shared discoveries can guide low-cost search over jointly specified agents and collaboration.

## Claims this source weakens or contradicts

The PSO label is metaphorical, and spectacular relative gains need absolute-score and budget context.

## Relevance to a mathematics paper

Useful for studying population search in a nonmetric language space and for demanding appropriate baselines for percent improvement.

## Connections to other sources

See the category and claim-level cross-references in [`INDEX.md`](INDEX.md) and the synthesis documents.

## Verification notes

Local PDF algorithm, TravelPlanner Table 2, cost Table 6, benchmark setup, ablations, and limitations were checked; scores and costs were not reproduced. The archived file parsed successfully: 41 pages, 127442 extractable characters, SHA-256 `36176bc6ba8b7d8780bec5a8be4f3a6f48607e1d28a64e5cf731019379861f7d`.
