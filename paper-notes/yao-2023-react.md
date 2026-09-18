---
title: "ReAct: Synergizing Reasoning and Acting in Language Models"
authors: ["Shunyu Yao", "Jeffrey Zhao", "Dian Yu", "Nan Du", "Izhak Shafran", "Karthik Narasimhan", "Yuan Cao"]
year: 2023
venue: "ICLR-2023"
source_type: "peer-reviewed"
paper_url: "https://arxiv.org/abs/2210.03629"
pdf_path: "papers/academic/yao-2023-react.pdf"
accessed: "2026-09-04"
review_status: "fully-reviewed"
evidence_confidence: "high"
---

# yao-2023-react — ReAct: Synergizing Reasoning and Acting in Language Models

## Why this source is in the corpus

Models the action interface through which a harness turns language outputs into state-changing operations.

## Research question

Does interleaving language reasoning with environment actions improve knowledge and interactive tasks?

## Harness mechanism studied

A policy chooses both thought actions, which alter context only, and grounded actions, which change or observe the environment.

## Method and experimental setup

Prompted PaLM and GPT-family models on HotpotQA, FEVER, ALFWorld, and WebShop, with baselines, hybrids, and 200 manually labeled trajectories.

## Main findings

- ReAct scores 27.4 HotpotQA EM and 60.9 FEVER accuracy, while CoT scores 29.4 and 56.3; hybrids reach 34.2-35.1 and 62.0-64.6.
- ReAct is therefore not uniformly superior; 47% of labeled failures are reasoning errors and 23% failed searches.

## Mathematical content

The policy is π(a_t|c_t) over an augmented action space containing environment actions and language thoughts.

## Evidence quality and limitations

Prompt and tool affordances are hand-designed, models are dated, tasks are small, and hybrids receive different information paths.

## Important implementation details

Serialize thoughts, actions, and observations distinctly and make action parsing, error handling, and stopping explicit.

## Claims this source supports

Interleaved tool feedback can reduce hallucination and support adaptive plans.

## Claims this source weakens or contradicts

The meme that ReAct universally beats chain-of-thought.

## Relevance to a mathematics paper

Supplies the canonical controlled-process equation for an agent loop.

## Connections to other sources

See the category and claim-level cross-references in [`INDEX.md`](INDEX.md) and the synthesis documents.

## Verification notes

Table 1, Table 2, augmented action-space definition, trajectory analysis, and conclusions checked in the local PDF. The archived file parsed successfully: 33 pages, 110055 extractable characters, SHA-256 `f285b0971ae4a790e402fb93966bed3adde2cf0a04977d08b2b40d6ab0cace69`.
