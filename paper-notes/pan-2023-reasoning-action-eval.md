---
title: "On Evaluating the Integration of Reasoning and Action in LLM Agents"
authors: ["Linyong Nan", "Ellen Zhang", "Weijin Zou", "Yilun Zhao", "Wenfei Zhou", "Arman Cohan"]
year: 2023
venue: "preprint"
source_type: "preprint"
paper_url: "https://arxiv.org/abs/2311.09721"
pdf_path: "papers/academic/pan-2023-reasoning-action-eval.pdf"
accessed: "2026-09-04"
review_status: "skimmed"
evidence_confidence: "medium"
---

# pan-2023-reasoning-action-eval — On Evaluating the Integration of Reasoning and Action in LLM Agents

## Why this source is in the corpus

Makes model–harness–environment coupling observable in executable, long-horizon tasks.

## Research question

Where do tool-augmented agents fail when database retrieval and long-form reasoning must be integrated?

## Harness mechanism studied

Agents iteratively formulate SQL, observe results, decide whether to continue, and synthesize an analytical narrative; an evaluator ensemble imitates peer review.

## Method and experimental setup

EMNLP 2023 dataset and experiments comparing two SQL interaction strategies with stage-level retrieval, planning, and answer-quality analysis.

## Main findings

- Even GPT-4 struggles; planning what evidence is needed and producing multiple useful SQL queries are the main bottlenecks.
- Stage-wise evaluation shows that final answer quality cannot diagnose whether retrieval, reasoning, or synthesis failed.

## Mathematical content

The loop is a partially observed sequential decision process; end quality is a composition of query validity, evidence coverage, inference, and evaluator reliability.

## Evidence quality and limitations

Dataset is specialized and modest; LLM-based judges may share biases; SQL makes evidence observable but not necessarily sufficient; multiple components change between strategies.

## Important implementation details

Log every query and result, score evidence coverage separately from narrative quality, blind judges, and report inter-rater agreement and token cost.

## Claims this source supports

Fine-grained pipeline evaluation is needed to localize harness failures.

## Claims this source weakens or contradicts

Using a final answer score as evidence that retrieval or planning itself works.

## Relevance to a mathematics paper

Supports staged reliability models and latent-variable decomposition of judge scores.

## Connections to other sources

See the category and claim-level cross-references in [`INDEX.md`](INDEX.md) and the synthesis documents.

## Verification notes

Abstract, task definition, two strategies, stage analysis, evaluator design, and stated bottlenecks checked in the local PDF. The archived file parsed successfully: 16 pages, 59627 extractable characters, SHA-256 `465fd5d7fa6594115aa7764008711b7d9f4fee22eb050098e10feae7055a194b`.
