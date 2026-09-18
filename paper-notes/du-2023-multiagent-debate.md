---
title: "Improving Factuality and Reasoning in Language Models through Multiagent Debate"
authors: ["Yilun Du", "Shuang Li", "Antonio Torralba", "Joshua B. Tenenbaum", "Igor Mordatch"]
year: 2023
venue: "preprint"
source_type: "preprint"
paper_url: "https://arxiv.org/abs/2305.14325"
pdf_path: "papers/academic/du-2023-multiagent-debate.pdf"
accessed: "2026-09-04"
review_status: "fully-reviewed"
evidence_confidence: "medium"
---

# du-2023-multiagent-debate — Improving Factuality and Reasoning in Language Models through Multiagent Debate

## Why this source is in the corpus

Provides communication, aggregation, or coordination mechanisms and their compute-matched counterevidence.

## Research question

Does iterative exchange among sampled agents improve reasoning and factuality beyond a vote?

## Harness mechanism studied

Several model instances answer, see peers' reasoning, debate over multiple rounds, and converge to a final response.

## Method and experimental setup

Three agents and two rounds on 100 arithmetic, 100 GSM8K, and 300 chess cases plus factuality examples.

## Main findings

- Arithmetic reaches 81.8% versus 69.0% for pre-debate majority; GSM8K 85.0% versus 81.0%; chess score 122.9 versus 102.2.
- Debate uses more generations than the vote, and later compute-matched studies often find voting stronger.

## Mathematical content

Round-wise transcript conditioning defines a coupled stochastic process; the paper proves no improvement theorem.

## Evidence quality and limitations

ArXiv-only early study, very small samples, old ChatGPT, unequal response count, and convergence can amplify a common error.

## Important implementation details

Match total calls and tokens, include voting and independent refinement, and measure belief changes rather than final score alone.

## Claims this source supports

Peer information can sometimes alter and improve answers.

## Claims this source weakens or contradicts

The headline as proof that communication rather than extra compute caused gains.

## Relevance to a mathematics paper

Motivates belief-update, correlation, and consensus-process analysis.

## Connections to other sources

See the category and claim-level cross-references in [`INDEX.md`](INDEX.md) and the synthesis documents.

## Verification notes

Sample sizes, arithmetic/GSM8K/chess tables, round protocol, majority baseline, and limitations checked in the local PDF. The archived file parsed successfully: 27 pages, 95853 extractable characters, SHA-256 `b302ff15202dc3cda03f40ea1ac92b29e1519978540b345af92991f6d3e619b4`.
