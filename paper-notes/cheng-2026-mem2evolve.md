---
title: "Mem2Evolve: Towards Self-Evolving Agents via Co-Evolutionary Capability Expansion and Experience Distillation"
authors: ["Zihao Cheng", "Zeming Liu", "Yingyu Shan", "Xinyi Wang", "Xiangrong Zhu", "Yunpu Ma", "Hongru Wang", "Yuhang Guo", "Wei Lin", "Yunhong Wang"]
year: 2026
venue: "ACL-2026-Long"
source_type: "peer-reviewed"
paper_url: "https://aclanthology.org/2026.acl-long.952/"
pdf_path: "papers/academic/cheng-2026-mem2evolve.pdf"
accessed: "2026-09-04"
review_status: "skimmed"
evidence_confidence: "high"
---

# cheng-2026-mem2evolve — Mem2Evolve: Towards Self-Evolving Agents via Co-Evolutionary Capability Expansion and Experience Distillation

## Why this source is in the corpus

Directly studies reusable harness components, outer-loop optimization, self-modification, or the statistical controls needed to decide whether an update is a real improvement.

## Research question

Can accumulated experience and reusable tools/experts jointly drive continual agent improvement?

## Harness mechanism studied

Two persistent stores—experience memory and asset memory—receive trace-derived lessons, generated tools, and generated expert agents; tests and repair loops validate executable assets before reuse.

## Method and experimental setup

Mem2Evolve uses an LM judge over trajectories, creates or retrieves tools and experts, generates tests, repairs invalid assets, updates both memories, and evaluates a heterogeneous collection of agent benchmarks.

## Main findings

- Table 2 reports GPT-5-chat average 70.24 versus Alita 63.78, AFlow 58.44, and direct 49.49; Table 3 removal effects are -10.28 without tool creation, -1.72 without expert creation, -3.13 without tool memory, and -4.73 without agent memory.
- Table 4 shows first-pass validity 53.1→72.4 and repair iterations 1.01→0.48, but averages mix unlike metrics and the paper’s percentage wording should be read as absolute-point differences.

## Mathematical content

Memory update seeks empirical expected utility over stored experiences and assets; component removals estimate marginal differences but interactions prevent additive attribution, and no memory-stability or test-soundness theorem is proved.

## Evidence quality and limitations

ACL 2026 and very recent; LM-judge feedback, heterogeneous averaging, generated-test overfitting, code security, executor dependence, and no long-horizon nonstationary deployment constrain the claim of continual evolution.

## Important implementation details

Maintain provenance-aware experience and asset stores, retrieve relevant items, generate tools or specialized agents, create and execute tests, repair failures, insert accepted assets, and reuse them on later tasks.

## Claims this source supports

Persistent executable assets plus memory can outperform transient workflow search, and tool creation appears the largest ablated contributor in this study.

## Claims this source weakens or contradicts

Weakens a simple memory-only story: asset generation, validation, and repair are essential, while percentage headlines can obscure absolute-point arithmetic.

## Relevance to a mathematics paper

Supports a coupled-state model for experience and asset memory and a factorial analysis of validity, retrieval, and component interactions.

## Connections to other sources

See the category and claim-level cross-references in [`INDEX.md`](INDEX.md) and the synthesis documents.

## Verification notes

Local PDF architecture, Tables 2–4, test/repair pipeline, ablations, averaging details, and limitations were checked; results were not replicated. The archived file parsed successfully: 48 pages, 144291 extractable characters, SHA-256 `172228f7c0495ec445ab881d22b35711e64bb2737ec59fa4ff87b450c200076a`.
