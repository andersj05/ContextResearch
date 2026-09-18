---
title: "On the Self-Verification Limitations of Large Language Models on Reasoning and Planning Tasks"
authors: ["Kaya Stechly", "Karthik Valmeekam", "Subbarao Kambhampati"]
year: 2024
venue: "preprint"
source_type: "preprint"
paper_url: "https://arxiv.org/abs/2402.08115"
pdf_path: "papers/academic/stechly-2024-self-verification-limits.pdf"
accessed: "2026-09-04"
review_status: "skimmed"
evidence_confidence: "high"
---

# stechly-2024-self-verification-limits — On the Self-Verification Limitations of Large Language Models on Reasoning and Planning Tasks

## Why this source is in the corpus

Supports analysis of inference-time search, feedback, stopping, and verifier error.

## Research question

Can a model reliably verify its own candidate solutions on reasoning and planning tasks?

## Harness mechanism studied

Candidate generation is followed by prompted self-verification or selection among alternatives.

## Method and experimental setup

Controlled reasoning and planning tasks compare generation accuracy, verification discrimination, and selection performance.

## Main findings

- Models can generate correct candidates that they cannot reliably identify as correct.
- Verification performance is task- and presentation-sensitive, so best-of-N coverage need not translate into selected accuracy.

## Mathematical content

The key distinction is generator success probability versus verifier true- and false-positive rates; selection utility depends on both.

## Evidence quality and limitations

Limited task families and model generations; prompting may not exhaust all verifier designs; self-verification shares correlated errors with generation.

## Important implementation details

Measure verifier confusion matrices separately and include independently grounded or executable checks.

## Claims this source supports

Selection quality is a separate harness capability from candidate coverage.

## Claims this source weakens or contradicts

Oracle pass@k as deployable accuracy and self-confidence as a sufficient selector.

## Relevance to a mathematics paper

Directly motivates imperfect-verifier probability models.

## Connections to other sources

See the category and claim-level cross-references in [`INDEX.md`](INDEX.md) and the synthesis documents.

## Verification notes

Abstract, verification tasks, generator-versus-verifier tables, error analysis, and conclusion checked in the local PDF. The archived file parsed successfully: 53 pages, 136657 extractable characters, SHA-256 `90544a98c961a4c94414d58f8cd39be6f166974e14332abadbdf6a0b41b8e9c4`.
