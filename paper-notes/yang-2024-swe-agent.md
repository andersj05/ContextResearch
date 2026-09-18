---
title: "SWE-agent: Agent-Computer Interfaces Enable Automated Software Engineering"
authors: ["John Yang", "Carlos E. Jimenez", "Alexander Wettig", "Kilian Lieret", "Shunyu Yao", "Karthik Narasimhan", "Ofir Press"]
year: 2024
venue: "NeurIPS-2024"
source_type: "peer-reviewed"
paper_url: "https://arxiv.org/abs/2405.15793"
pdf_path: "papers/academic/yang-2024-swe-agent.pdf"
accessed: "2026-09-04"
review_status: "fully-reviewed"
evidence_confidence: "high"
---

# yang-2024-swe-agent — SWE-agent: Agent-Computer Interfaces Enable Automated Software Engineering

## Why this source is in the corpus

Makes model–harness–environment coupling observable in executable, long-horizon tasks.

## Research question

How much can an agent-computer interface change software-repair performance with the model held fixed?

## Harness mechanism studied

SWE-agent provides constrained file viewing, repository search, editing, execution feedback, history handling, and explicit submission through an agent-computer interface.

## Method and experimental setup

NeurIPS 2024 system paper with fixed-model interface ablations on SWE-bench and HumanEvalFix plus trajectory and error analysis.

## Main findings

- On SWE-bench Lite, the tailored interface resolves about 18% versus about 11% for a shell-only interface with the same GPT-4 family.
- Search and file-view commands materially change outcomes, while performance comes at much higher per-task cost than simple baselines.

## Mathematical content

Resolution is a paired binary outcome by task; the relevant harness effect is a within-task risk difference under matched model and budget.

## Evidence quality and limitations

The interface was tuned on a small development set; runs use dated models and a four-dollar task cap; several components change together; public benchmark exposure grows over time.

## Important implementation details

Record the exact ACI command schemas, prompt, context windowing, retry policy, model snapshot, budget, container, and trajectory; use paired seeds for ablations.

## Claims this source supports

Harness interfaces are causal experimental variables rather than neutral wrappers.

## Claims this source weakens or contradicts

Model-only explanations of agent performance and unqualified claims that more autonomy is always better.

## Relevance to a mathematics paper

Motivates paired treatment-effect estimation and component factorial designs.

## Connections to other sources

See the category and claim-level cross-references in [`INDEX.md`](INDEX.md) and the synthesis documents.

## Verification notes

Abstract, fixed-model ACI tables and ablations, cost discussion, prompt/interface details, and limitations checked in the local PDF. The archived file parsed successfully: 118 pages, 291638 extractable characters, SHA-256 `d171e0693060b910ceb2cddd0fd4bc7cae302005d42d0d8059bfdbe056c3adba`.
