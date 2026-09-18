---
title: "Reflexion: Language Agents with Verbal Reinforcement Learning"
authors: ["Noah Shinn", "Federico Cassano", "Edward Berman", "Ashwin Gopinath", "Karthik Narasimhan", "Shunyu Yao"]
year: 2023
venue: "NeurIPS-2023"
source_type: "peer-reviewed"
paper_url: "https://arxiv.org/abs/2303.11366"
pdf_path: "papers/academic/shinn-2023-reflexion.pdf"
accessed: "2026-09-04"
review_status: "fully-reviewed"
evidence_confidence: "high"
---

# shinn-2023-reflexion — Reflexion: Language Agents with Verbal Reinforcement Learning

## Why this source is in the corpus

Supports analysis of inference-time search, feedback, stopping, and verifier error.

## Research question

Does storing verbal feedback between attempts improve agents without updating model weights?

## Harness mechanism studied

An actor produces a trajectory, an evaluator scores it, and a reflection model writes episodic textual advice for the next attempt.

## Method and experimental setup

Coding, decision, and reasoning tasks compare base attempts, test feedback, blind reflection, and full Reflexion.

## Main findings

- HumanEval is reported at 91% versus GPT-4 at 80.1%.
- On the hardest 50 Rust tasks, base and test-only score 60%, blind reflection 52%, and full external-feedback reflection 68%, showing the feedback channel is load-bearing.

## Mathematical content

An actor-evaluator-reflection loop updates textual episodic memory rather than model weights; no reinforcement-learning convergence theorem applies.

## Evidence quality and limitations

Retries and oracle stopping confound reflection, public tests leak strong signals, and Kapoor et al. find simple warming cheaper and at least as accurate.

## Important implementation details

Store compact diagnoses tied to observable failures, bound attempts, and compare against equal-call retries without reflection.

## Claims this source supports

External feedback plus episodic memory can improve later attempts.

## Claims this source weakens or contradicts

Verbal reinforcement as intrinsic self-knowledge or parameter learning.

## Relevance to a mathematics paper

Provides a nonparametric memory update inside a repeated-decision process.

## Connections to other sources

See the category and claim-level cross-references in [`INDEX.md`](INDEX.md) and the synthesis documents.

## Verification notes

Table 1, Rust ablation, actor-evaluator-reflection loop, memory design, and external rerun checked in local PDFs. The archived file parsed successfully: 19 pages, 59481 extractable characters, SHA-256 `6059b6f89fea9959bd3dab553fbb97756a3dfb1b15e3cbab2fbf3ab6664333bd`.
