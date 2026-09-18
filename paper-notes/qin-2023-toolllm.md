---
title: "ToolLLM: Facilitating Large Language Models to Master 16000+ Real-world APIs"
authors: ["Yujia Qin", "Shihao Liang", "Yining Ye", "Kunlun Zhu", "Lan Yan", "Yaxi Lu", "Yankai Lin", "Xin Cong", "Xiangru Tang", "Bill Qian", "Sihan Zhao", "Lauren Hong", "Runchu Tian", "Ruobing Xie", "Jie Zhou", "Mark Gerstein", "Dahai Li", "Zhiyuan Liu", "Maosong Sun"]
year: 2023
venue: "ICLR-2024"
source_type: "peer-reviewed"
paper_url: "https://arxiv.org/abs/2307.16789"
pdf_path: "papers/academic/qin-2023-toolllm.pdf"
accessed: "2026-09-04"
review_status: "fully-reviewed"
evidence_confidence: "high"
---

# qin-2023-toolllm — ToolLLM: Facilitating Large Language Models to Master 16000+ Real-world APIs

## Why this source is in the corpus

Models the action interface through which a harness turns language outputs into state-changing operations.

## Research question

Can data generation, retrieval, and tree search teach open models to use a very large API catalog?

## Harness mechanism studied

ToolBench training, an API retriever, and depth-first search over alternative call trajectories with proceed or give-up decisions.

## Method and experimental setup

16,464 APIs, 126,486 instances, 469,585 real calls, in- and out-of-distribution evaluation, and oracle-API comparisons.

## Main findings

- ToolLLM improves tool-use benchmarks, but oracle API provision sharply improves out-of-distribution results, identifying retrieval as a major bottleneck.
- Training, retrieval, search, and evaluation all change together.

## Mathematical content

DFSDT is a language-model-controlled decision tree explored depth first; no theorem guarantees useful coverage or stopping.

## Evidence quality and limitations

ChatGPT creates much of the data, GPT-style models judge answers, live APIs drift, and component attribution is weak.

## Important implementation details

Log retrieval candidates and tree branches, bound search, retain failed calls, and evaluate retrieval independently from planning.

## Claims this source supports

Large-catalog performance depends on harness retrieval and search as well as the base model.

## Claims this source weakens or contradicts

End-to-end ToolLLM gains as evidence solely of model fine-tuning.

## Relevance to a mathematics paper

Supports a decomposition into retriever recall, branch policy, executor success, and judge error.

## Connections to other sources

See the category and claim-level cross-references in [`INDEX.md`](INDEX.md) and the synthesis documents.

## Verification notes

Dataset counts, DFSDT algorithm, oracle-retrieval results, OOD tables, and limitations checked in the local PDF. The archived file parsed successfully: 24 pages, 83572 extractable characters, SHA-256 `295299721d67b250661fb6598bee86a2e9fe766241fdc08dd7cf389e984b4d1a`.
