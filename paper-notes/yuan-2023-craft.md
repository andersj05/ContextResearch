---
title: "CRAFT: Customizing LLMs by Creating and Retrieving from Specialized Toolsets"
authors: ["Lifan Yuan", "Yangyi Chen", "Xingyao Wang", "Yi R. Fung", "Hao Peng", "Heng Ji"]
year: 2023
venue: "ICLR-2024"
source_type: "peer-reviewed"
paper_url: "https://arxiv.org/abs/2309.17428"
pdf_path: "papers/academic/yuan-2023-craft.pdf"
accessed: "2026-09-04"
review_status: "skimmed"
evidence_confidence: "high"
---

# yuan-2023-craft — CRAFT: Customizing LLMs by Creating and Retrieving from Specialized Toolsets

## Why this source is in the corpus

Directly studies reusable harness components, outer-loop optimization, self-modification, or the statistical controls needed to decide whether an update is a real improvement.

## Research question

Can reusable code tools be abstracted from solved examples and retrieved to improve visual and mathematical reasoning?

## Harness mechanism studied

An offline pipeline converts LM-generated solutions into generalized functions, validates and deduplicates them, then retrieves a small tool subset through multiple textual views at inference.

## Method and experimental setup

CRAFT uses GPT-4 to solve seed examples, abstracts solution code into tools, filters on execution and redundancy, indexes documentation and demonstrations, and compares tool-augmented inference on VQA plus an algebra subset of MATH.

## Main findings

- The abstract reports a 43.16% average relative F1 gain over the strongest VQA baselines; Table 3 reports GPT-4 CRAFT SAcc/F1 of 55.6/58.8, 39.0/49.1, and 35.3/44.8 versus ViperGPT 51.4/53.7, 36.7/47.2, and 32.8/42.4 on three datasets.
- Tool libraries grow from 261 to 337 to 525 functions as source data expand, but the study does not isolate library size from data coverage or prove transfer beyond code-expressible tasks.

## Mathematical content

Tool retrieval approximates nearest-neighbor selection over multiple representations, while creation applies empirical acceptance and deduplication predicates; no theorem links library growth to expected risk.

## Evidence quality and limitations

Only MATH algebra is used because of budget; the original problem distribution informs tool validation; GPT-4 creates the assets used later; no uncertainty intervals or executable-code security analysis are supplied.

## Important implementation details

Solve seed items with code, abstract successful snippets into parameterized functions, validate and deduplicate them, build multi-view embeddings, retrieve relevant tools, and allow the fixed executor to compose calls.

## Claims this source supports

Offline experience can be compiled into a persistent capability library rather than repeatedly placed verbatim in context.

## Claims this source weakens or contradicts

Relative percentage headlines overstate small absolute changes in some VQA cells, and success depends on a stronger tool creator plus curated code-friendly domains.

## Relevance to a mathematics paper

Suggests coverage, retrieval error, and tool-validity terms for decomposing library utility; the paper itself gives empirical rather than theoretical guarantees.

## Connections to other sources

See the category and claim-level cross-references in [`INDEX.md`](INDEX.md) and the synthesis documents.

## Verification notes

Local PDF abstract, Sections 3–5, Tables 2–3, library-size analysis, MATH sampling note, and limitations were checked; findings are not independently replicated. The archived file parsed successfully: 29 pages, 100129 extractable characters, SHA-256 `59263fffdc51e21530d9dba1aeeeacefb2b5c4048012a7e385b4f555a362f155`.
