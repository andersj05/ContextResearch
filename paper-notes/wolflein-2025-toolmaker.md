---
title: "LLM Agents Making Agent Tools"
authors: ["Georg Wölflein", "Dyke Ferber", "Daniel Truhn", "Ognjen Arandjelović", "Jakob Nikolas Kather"]
year: 2025
venue: "ACL-2025-Long"
source_type: "peer-reviewed"
paper_url: "https://arxiv.org/abs/2502.11705"
pdf_path: "papers/academic/wolflein-2025-toolmaker.pdf"
accessed: "2026-09-04"
review_status: "skimmed"
evidence_confidence: "medium"
---

# wolflein-2025-toolmaker — LLM Agents Making Agent Tools

## Why this source is in the corpus

Directly studies reusable harness components, outer-loop optimization, self-modification, or the statistical controls needed to decide whether an update is a real improvement.

## Research question

Can an agent autonomously turn scientific papers and GitHub repositories into reusable executable tools?

## Harness mechanism studied

A multi-stage tool-building harness retrieves source artifacts, resolves dependencies, generates wrappers, debugs against unit tests, and registers successful tools for later use.

## Method and experimental setup

ToolMaker is evaluated on fifteen repository-backed tasks with more than one hundred aggregate unit tests, measuring implementation success and downstream task solving against software-engineering agents.

## Main findings

- The paper reports implementing 80% of the fifteen tools and outperforming compared SWE-style agents on the selected tasks.
- The denominator is only fifteen, repositories and tasks are supplied, and passing known tests can reward narrow wrappers or overfit implementations rather than safe general-purpose tools.

## Mathematical content

Acceptance is an empirical predicate over build success and unit-test pass rate; with n=15, a raw 80% is 12/15 and has substantial binomial uncertainty, while no formal synthesis-correctness theorem is proved.

## Evidence quality and limitations

Tiny domain-biased sample, known-test overfitting, external package and repository trust, fixed role pipeline, missing security analysis, and no long-run maintenance or unseen-client validation.

## Important implementation details

Parse papers/readmes and repositories, install or resolve dependencies in a sandbox, synthesize a callable wrapper, generate/run tests, iteratively debug failures, and save the passing tool to a registry.

## Claims this source supports

External technical artifacts can be compiled into persistent executable harness capabilities with automated validation.

## Claims this source weakens or contradicts

Unit-test success on curated repositories is not evidence of secure autonomous tool acquisition or robust transfer to unseen usage.

## Relevance to a mathematics paper

Supports reliability modeling as a product of retrieval, build, wrapper, and test-coverage probabilities; small-n confidence intervals should accompany the headline.

## Connections to other sources

See the category and claim-level cross-references in [`INDEX.md`](INDEX.md) and the synthesis documents.

## Verification notes

Local PDF pipeline, task construction, more-than-100-test description, 80% result, comparisons, examples, and limitations were checked; tools were not rebuilt. The archived file parsed successfully: 31 pages, 131984 extractable characters, SHA-256 `ad5422bf08d0db34ff8a5f39ebb3e466614f2f233c132a2d85d6b88a46a13ee6`.
