---
title: "TextGrad: Automatic Differentiation via Text"
authors: ["Mert Yuksekgonul", "Federico Bianchi", "Joseph Boen", "Sheng Liu", "Zhi Huang", "Carlos Guestrin", "James Zou"]
year: 2024
venue: "Nature-2025"
source_type: "peer-reviewed"
paper_url: "https://arxiv.org/abs/2406.07496"
pdf_path: "papers/academic/yuksekgonul-2024-textgrad.pdf"
accessed: "2026-09-04"
review_status: "skimmed"
evidence_confidence: "high"
---

# yuksekgonul-2024-textgrad — TextGrad: Automatic Differentiation via Text

## Why this source is in the corpus

Directly studies reusable harness components, outer-loop optimization, self-modification, or the statistical controls needed to decide whether an update is a real improvement.

## Research question

Can natural-language critiques serve as gradients for optimizing prompts and other variables in compound LM systems?

## Harness mechanism studied

A textual autograd engine records a computation graph, invokes backward critics to produce variable-specific feedback, and applies textual optimizer updates.

## Method and experimental setup

TextGrad defines differentiable-by-analogy text variables and operations, propagates critiques from an evaluation loss, and tests iterative updates on reasoning, coding, molecule, and prompt-optimization tasks.

## Main findings

- The paper reports 55% on GPQA and an MMLU machine-learning increase from 85.7 to 88.4 under textual optimization, alongside results on a 39-problem LeetCodeHard subset and other domains.
- The gains are source-reported, task and optimizer prompts vary, and no numerical-gradient identity or independent replication shows that backpropagated text is better than matched iterative critique.

## Mathematical content

For a computation graph, a backward engine maps downstream textual feedback into messages for predecessor variables and an optimizer proposes theta_{t+1}; despite gradient notation, there is no vector derivative, smoothness assumption, descent lemma, or convergence guarantee.

## Evidence quality and limitations

Critiques are subjective and model-dependent, computation is high, LeetCodeHard is tiny, evaluator leakage is possible, and the method can regress or oscillate without a principled step size.

## Important implementation details

Mark prompts or generated artifacts as variables, record forward-call dependencies, define a textual loss, recursively request local critiques, combine feedback, and ask an optimizer LM to rewrite each selected variable.

## Claims this source supports

A common interface can optimize prompts and intermediate artifacts using execution feedback without weight updates.

## Claims this source weakens or contradicts

The gradient metaphor is weaker than the publicity suggests and does not establish causal advantage over simpler reflection/revision loops.

## Relevance to a mathematics paper

Important negative mathematical lesson: chain-rule syntax alone supplies no differentiability or convergence; the update is stochastic black-box search.

## Connections to other sources

See the category and claim-level cross-references in [`INDEX.md`](INDEX.md) and the synthesis documents.

## Verification notes

Local PDF abstract, framework equations, algorithms, benchmark tables including GPQA/MMLU and LeetCode subset, and limitations were checked; no rerun was done. The archived file parsed successfully: 41 pages, 132647 extractable characters, SHA-256 `9cbfd5c78ad69e2a8363e76d6774f3e6b5e68f46b409d8b560e98276a985b428`.
