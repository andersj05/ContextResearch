---
title: "Evaluating Large Language Models Trained on Code"
authors: ["Mark Chen", "Jerry Tworek", "Heewoo Jun", "Qiming Yuan", "Henrique Ponde de Oliveira Pinto", "Jared Kaplan", "Harri Edwards", "Yuri Burda", "Nicholas Joseph", "Greg Brockman", "Alex Ray", "Raul Puri", "Gretchen Krueger", "Michael Petrov", "Heidy Khlaaf", "Girish Sastry", "Pamela Mishkin", "Brooke Chan", "Scott Gray", "Nick Ryder", "Mikhail Pavlov", "Alethea Power", "Lukasz Kaiser", "Mohammad Bavarian", "Clemens Winter", "Philippe Tillet", "Felipe Petroski Such", "Dave Cummings", "Matthias Plappert", "Fotios Chantzis", "Elizabeth Barnes", "Ariel Herbert-Voss", "William Hebgen Guss", "Alex Nichol", "Alex Paino", "Nikolas Tezak", "Jie Tang", "Igor Babuschkin", "Suchir Balaji", "Shantanu Jain", "William Saunders", "Christopher Hesse", "Andrew N. Carr", "Jan Leike", "Josh Achiam", "Vedant Misra", "Evan Morikawa", "Alec Radford", "Matthew Knight", "Miles Brundage", "Mira Murati", "Katie Mayer", "Peter Welinder", "Bob McGrew", "Dario Amodei", "Sam McCandlish", "Ilya Sutskever", "Wojciech Zaremba"]
year: 2021
venue: "preprint"
source_type: "preprint"
paper_url: "https://arxiv.org/abs/2107.03374"
pdf_path: "papers/academic/chen-2021-codex-passk.pdf"
accessed: "2026-09-04"
review_status: "fully-reviewed"
evidence_confidence: "high"
---

# chen-2021-codex-passk — Evaluating Large Language Models Trained on Code

## Why this source is in the corpus

Provides estimators or asymptotic models needed to distinguish coverage, reliability, and deployable utility.

## Research question

How should multiple sampled programs be evaluated when any one correct sample counts?

## Harness mechanism studied

Generate n candidates per task, execute tests, and estimate the probability that a size-k subset contains at least one passing candidate.

## Method and experimental setup

HumanEval and other code datasets evaluate Codex model sizes with many samples per problem and an unbiased combinatorial estimator.

## Main findings

- Codex-12B reports 28.8% pass@1 and 70.2% pass@100.
- The latter is oracle at-least-one coverage among 100 attempts, not a 70.2% probability that a deployed single run is reliable.

## Mathematical content

For n samples and c correct, unbiased pass@k is 1-C(n-c,k)/C(n,k), averaged over tasks.

## Evidence quality and limitations

HumanEval tests are incomplete, samples are not necessarily independent, the oracle knows correctness, and pass@100 hides selection and cost.

## Important implementation details

Store all candidates and test outcomes and report pass@1, pass@k, selected accuracy, total cost, and verifier error separately.

## Claims this source supports

Repeated attempts can expose capability hidden by pass@1.

## Claims this source weakens or contradicts

Pass@k as repeat reliability or deployable success without a selector.

## Relevance to a mathematics paper

The estimator is foundational for deriving coverage, reliability, and selection-aware utility.

## Connections to other sources

See the category and claim-level cross-references in [`INDEX.md`](INDEX.md) and the synthesis documents.

## Verification notes

Estimator derivation, HumanEval protocol, 28.8/70.2 result, test limitations, and sampling conditions checked in the local PDF. The archived file parsed successfully: 35 pages, 154328 extractable characters, SHA-256 `ebae72ea0e8a5eb2ecbccdb985aec6cc1254a7c4d29e6d4de7866db1e66c4855`.
