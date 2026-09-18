---
title: "Language Agent Tree Search Unifies Reasoning Acting and Planning in Language Models"
authors: ["Andy Zhou", "Kai Yan", "Michal Shlapentokh-Rothman", "Haohan Wang", "Yu-Xiong Wang"]
year: 2024
venue: "ICML-2024"
source_type: "peer-reviewed"
paper_url: "https://arxiv.org/abs/2310.04406"
pdf_path: "papers/academic/zhou-2024-lats.pdf"
accessed: "2026-09-04"
review_status: "fully-reviewed"
evidence_confidence: "medium"
---

# zhou-2024-lats — Language Agent Tree Search Unifies Reasoning Acting and Planning in Language Models

## Why this source is in the corpus

Supports analysis of inference-time search, feedback, stopping, and verifier error.

## Research question

Can MCTS combine acting, environment feedback, value estimates, and verbal reflection?

## Harness mechanism studied

Tree search selects action trajectories with UCT, expands LM proposals, evaluates states, backpropagates value, and retains reflections.

## Method and experimental setup

HumanEval, WebShop, HotPotQA, and other tasks compare LATS with reasoning and agent baselines; a later independent cost study reruns public code.

## Main findings

- The paper reports GPT-4 HumanEval 92.7% and GPT-3.5 WebShop 75.9%.
- Kapoor et al. rerun LATS at 88.0% and $134.50 versus simple warming at 93.2% and $2.45, undermining cost-uncontrolled architectural attribution.

## Mathematical content

UCT selects V(s)+w sqrt(ln N(parent)/N(s)); backpropagation uses running means and mixed value signals.

## Evidence quality and limitations

Public tests, multiple coupled mechanisms, high sampling cost, environment rollback assumptions, and contradictory independent rerun.

## Important implementation details

Disclose branch factor, depth, value model, reflection memory, rollback, test access, and total cost.

## Claims this source supports

Search can integrate feedback over long trajectories.

## Claims this source weakens or contradicts

LATS accuracy as evidence of cost-effective tree search or model improvement.

## Relevance to a mathematics paper

Offers an MCTS harness with a valuable external falsification and Pareto comparison.

## Connections to other sources

See the category and claim-level cross-references in [`INDEX.md`](INDEX.md) and the synthesis documents.

## Verification notes

Original algorithm and result tables plus Kapoor et al. rerun costs and outcomes checked in local PDFs. The archived file parsed successfully: 23 pages, 95911 extractable characters, SHA-256 `04c1e9cb00f384052739c53bcecb75626bf1f58f66c379cc289ea60ffc988635`.
