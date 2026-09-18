---
title: "Not what you've signed up for: Compromising Real-World LLM-Integrated Applications with Indirect Prompt Injection"
authors: ["Kai Greshake", "Sahar Abdelnabi", "Shailesh Mishra", "Christoph Endres", "Thorsten Holz", "Mario Fritz"]
year: 2023
venue: "AISec-2023"
source_type: "peer-reviewed"
paper_url: "https://arxiv.org/abs/2302.12173"
pdf_path: "papers/academic/greshake-2023-indirect-injection.pdf"
accessed: "2026-09-04"
review_status: "fully-reviewed"
evidence_confidence: "high"
---

# greshake-2023-indirect-injection — Not what you've signed up for: Compromising Real-World LLM-Integrated Applications with Indirect Prompt Injection

## Why this source is in the corpus

Defines adversarial failure modes and control layers for tools, permissions, and execution boundaries.

## Research question

How can adversarial instructions in retrieved data compromise tool-using LLM applications?

## Harness mechanism studied

Indirect prompt injection places instructions in third-party content that the harness retrieves and concatenates into the model context, allowing the data source to influence tool calls and outputs.

## Method and experimental setup

AISec 2023 threat-model paper with a security taxonomy and proof-of-concept attacks against real and synthetic LLM-integrated applications.

## Main findings

- The work demonstrates remote manipulation, data theft, API abuse, worm-like propagation, and information contamination when untrusted text is treated as executable instruction.
- The central architectural flaw is collapse of the data-instruction boundary, not simply malicious users at the chat interface.

## Mathematical content

The attack surface can be modeled as information flow from untrusted source D through context compiler C to privileged action A; a security invariant requires noninterference except through explicitly authorized data dependencies.

## Evidence quality and limitations

Demonstrations are qualitative and tied to 2023 systems; attack feasibility is not prevalence; some targets changed; the paper does not establish a universal defense.

## Important implementation details

Track provenance and trust labels through context, enforce least-privilege tools and argument checks outside the model, isolate execution, require confirmation for consequential actions, and test indirect channels.

## Claims this source supports

Security boundaries must be implemented by the harness around an instruction-following model.

## Claims this source weakens or contradicts

Prompt filtering or a stronger system prompt as a complete containment boundary.

## Relevance to a mathematics paper

Supports noninterference, information-flow, and attack-graph formalizations.

## Connections to other sources

See the category and claim-level cross-references in [`INDEX.md`](INDEX.md) and the synthesis documents.

## Verification notes

Abstract, threat model, taxonomy, attack demonstrations, data-instruction argument, and mitigation discussion checked in the local PDF. The archived file parsed successfully: 33 pages, 116690 extractable characters, SHA-256 `428e23e8c7e4f89310e113e38d082b3f65548a8b887188ebc536099061800e81`.
