---
title: "From Language Models to Practical Self-Improving Computer Agents"
authors: ["Alex Sheng"]
year: 2024
venue: "preprint"
source_type: "preprint"
paper_url: "https://arxiv.org/abs/2404.11964"
pdf_path: "papers/academic/sheng-2024-self-improving-computer-agent.pdf"
accessed: "2026-09-04"
review_status: "skimmed"
evidence_confidence: "low"
---

# sheng-2024-self-improving-computer-agent — From Language Models to Practical Self-Improving Computer Agents

## Why this source is in the corpus

Directly studies reusable harness components, outer-loop optimization, self-modification, or the statistical controls needed to decide whether an update is a real improvement.

## Research question

Can a computer-use agent improve from natural-language instruction and its own interaction history?

## Harness mechanism studied

A human instructor and an LM agent iteratively revise task guidance and procedures after observing failures in desktop-computer demonstrations.

## Method and experimental setup

The work presents a tutorial-style system and three qualitative case studies in which instructions, interaction traces, and manually guided revisions are carried forward to later attempts.

## Main findings

- The source shows three worked examples in which revised guidance changes later behavior.
- It reports no benchmark, denominator, matched baseline, uncertainty, or sealed held-out evaluation, so it is evidence of feasibility only and not of measurable self-improvement.

## Mathematical content

No formal objective, estimator, statistical test, or theorem is provided; the implied update is a deterministic or LM-mediated map from trace and human feedback to revised instructions.

## Evidence quality and limitations

Cherry-picked case studies, direct human intervention, no quantitative outcome definition, no cost accounting, and unaddressed computer-control security make generalization impossible to assess.

## Important implementation details

Record a failed computer trajectory, solicit instructor feedback, encode the correction into the agent’s procedural context, and retry a related task while preserving the revised instructions.

## Claims this source supports

Persistent procedural text can mediate cross-attempt learning in a computer-use loop.

## Claims this source weakens or contradicts

The paper weakens any claim that a demonstration of revision alone establishes autonomous, scalable, or statistically reliable self-improvement.

## Relevance to a mathematics paper

Mainly useful as a null-evidence example: without a sample frame and comparator, no effect size or error bound can be inferred.

## Connections to other sources

See the category and claim-level cross-references in [`INDEX.md`](INDEX.md) and the synthesis documents.

## Verification notes

Local PDF abstract, system description, all three case studies, and conclusion were checked; there are no quantitative results to verify. The archived file parsed successfully: 25 pages, 75516 extractable characters, SHA-256 `54b99fcf52c64c4d94b58205977004229b0c3223cb9077c32974799a1dbdd4b3`.
