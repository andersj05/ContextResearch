---
title: "DSPy: Compiling Declarative Language Model Calls into Self-Improving Pipelines"
authors: ["Omar Khattab", "Arnav Singhvi", "Paridhi Maheshwari", "Zhiyuan Zhang", "Keshav Santhanam", "Sri Vardhamanan", "Saiful Haq", "Ashutosh Sharma", "Thomas T. Joshi", "Hanna Moazam", "Heather Miller", "Matei Zaharia", "Christopher Potts"]
year: 2023
venue: "ICLR-2024"
source_type: "peer-reviewed"
paper_url: "https://arxiv.org/abs/2310.03714"
pdf_path: "papers/academic/khattab-2023-dspy.pdf"
accessed: "2026-09-04"
review_status: "skimmed"
evidence_confidence: "high"
---

# khattab-2023-dspy — DSPy: Compiling Declarative Language Model Calls into Self-Improving Pipelines

## Why this source is in the corpus

Directly studies reusable harness components, outer-loop optimization, self-modification, or the statistical controls needed to decide whether an update is a real improvement.

## Research question

Can declarative LM programs be compiled into effective prompts and demonstrations without hand-tuning every call?

## Harness mechanism studied

A compiler treats signatures, modules, demonstrations, and instructions as editable program parameters and searches them against a development metric.

## Method and experimental setup

The paper implements typed signatures and composable modules, then uses teleprompters that bootstrap successful traces and perform random search over prompt and demonstration candidates on held-out development examples.

## Main findings

- Source-reported Tables 1–2 show compilation can move GSM8K configurations from roughly 4–20% to 49–88%, depending on the LM and program, and also improves HotPotQA retrieval-and-reasoning programs.
- These are joint effects of program structure, demonstrations, instructions, and search; the paper does not isolate a universal compiler effect or independently reproduce the gains here.

## Mathematical content

The operative problem is finite black-box optimization, theta-star in argmax over candidate program parameters of an empirical development metric; no convergence or generalization theorem is proved.

## Evidence quality and limitations

Many cells change the program, compiler, demonstrations, and model together; selection uses 10–20 trials on roughly 150–300 validation items; dated LM versions and task-specific metrics limit transportability.

## Important implementation details

Declare an LM pipeline as signatures and modules, compile bootstrapped execution traces into few-shot demonstrations, optionally generate instructions, score candidates on a development set, and deploy the selected program unchanged on test.

## Claims this source supports

Prompts and demonstrations are legitimate persistent harness state, and modular compilation can substantially change fixed-model behavior.

## Claims this source weakens or contradicts

A headline gain from compilation cannot be attributed to any single harness component, and repeated development-set search is not sealed-test evidence.

## Relevance to a mathematics paper

Provides a clean empirical-risk-minimization abstraction for prompt-program compilation and a natural place to study selection bias versus candidate count.

## Connections to other sources

See the category and claim-level cross-references in [`INDEX.md`](INDEX.md) and the synthesis documents.

## Verification notes

Local PDF abstract, Sections 2–4, Tables 1–2, optimization descriptions, and limitations were checked; values are source-reported and were not rerun. The archived file parsed successfully: 32 pages, 107643 extractable characters, SHA-256 `5309836325c3a580b6c176242f49f21ca40e413b0acd514e74b67e16bb1b56bc`.
