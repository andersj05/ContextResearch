---
title: "From Question Answering to Task Completion: A Survey on Agent System and Harness Design"
authors: ["Jianyuan Guo", "Zhiwei Hao", "Chengcheng Wang", "Cheng Fan", "Tingzhang Luo", "Hongguang Li", "Ying Gao", "Hefei Mei", "Jiankun Peng", "Rongjian Xu", "Minjing Dong", "Han Wu", "Mengyu Zheng", "Kai Han", "Shiqi Wang", "Chang Xu", "Yunhe Wang"]
year: 2026
venue: "preprint"
source_type: "preprint"
paper_url: "https://arxiv.org/abs/2606.20683"
pdf_path: "papers/academic/guo-2026-agent-harness-survey.pdf"
accessed: "2026-09-04"
review_status: "skimmed"
evidence_confidence: "medium"
---

# guo-2026-agent-harness-survey — From Question Answering to Task Completion: A Survey on Agent System and Harness Design

## Why this source is in the corpus

Supplies vocabulary and comparison axes for formalizing the harness as a composite decision system.

## Research question

Where does agent performance reside: model, harness, or their coupling?

## Harness mechanism studied

Six runtime responsibilities: observation, context, control, action, state, and verification.

## Method and experimental setup

Recent model-harness survey maps task pressures, engineering paradigms, benchmark practices, and evidence across domains.

## Main findings

- It explicitly defines an agent as a foundation model coupled to an execution harness.
- Quality emerges from model, runtime, task structure, and evaluation rather than model weights alone.

## Mathematical content

Offers a systems decomposition suitable for a composite function of model, harness, environment, budget, and task; it proves no causal theorem.

## Evidence quality and limitations

Very recent preprint and partly synthesizes the same young harness literature studied here.

## Important implementation details

Use the six responsibilities as an auditable architecture checklist and report their versioned configuration.

## Claims this source supports

The model-harness pair is the minimal meaningful evaluation unit.

## Claims this source weakens or contradicts

Model-only interpretations of long-horizon agent scores.

## Relevance to a mathematics paper

Provides a compact state-and-control decomposition for the paper's formal definition.

## Connections to other sources

See the category and claim-level cross-references in [`INDEX.md`](INDEX.md) and the synthesis documents.

## Verification notes

Abstract, six-part decomposition, evidence synthesis, and stated open challenges checked in the local PDF. The archived file parsed successfully: 29 pages, 186009 extractable characters, SHA-256 `5d21e1f25dd55857e7d17452be1bc74d14026e0bc7843d84f73f55c17856fdda`.
