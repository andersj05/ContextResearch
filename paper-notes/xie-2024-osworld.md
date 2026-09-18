---
title: "OSWorld: Benchmarking Multimodal Agents for Open-Ended Tasks in Real Computer Environments"
authors: ["Tianbao Xie", "Danyang Zhang", "Jixuan Chen", "Xiaochuan Li", "Siheng Zhao", "Ruisheng Cao", "Toh Jing Hua", "Zhoujun Cheng", "Dongchan Shin", "Fangyu Lei", "Yitao Liu", "Yiheng Xu", "Shuyan Zhou", "Silvio Savarese", "Caiming Xiong", "Victor Zhong", "Tao Yu"]
year: 2024
venue: "NeurIPS-2024"
source_type: "peer-reviewed"
paper_url: "https://arxiv.org/abs/2404.07972"
pdf_path: "papers/academic/xie-2024-osworld.pdf"
accessed: "2026-09-04"
review_status: "skimmed"
evidence_confidence: "high"
---

# xie-2024-osworld — OSWorld: Benchmarking Multimodal Agents for Open-Ended Tasks in Real Computer Environments

## Why this source is in the corpus

Makes model–harness–environment coupling observable in executable, long-horizon tasks.

## Research question

How can multimodal agents be tested on open-ended tasks in real computer operating systems?

## Harness mechanism studied

OSWorld provisions task states in Ubuntu, Windows, and macOS, exposes screenshot and accessibility observations plus mouse and keyboard actions, and runs custom state-based graders.

## Method and experimental setup

2024 preprint constructing 369 tasks across real desktop and web applications with execution-based baselines and detailed error analysis.

## Main findings

- Humans complete 72.36% of tasks while the best paper-era model completes 12.24%.
- GUI grounding and operational knowledge are prominent failure sources.

## Mathematical content

Task success is an execution-verified Bernoulli; cross-OS comparisons need hierarchical effects because applications and graders are not exchangeable.

## Evidence quality and limitations

Only hundreds of tasks; OS/app updates cause drift; custom graders may be incomplete; latency and nondeterministic GUI state affect repeatability; paper was a preprint in the archived version.

## Important implementation details

Freeze VM images and application versions, log screen/action trajectories and timing, rerun seeds, audit graders, and report results per OS and application.

## Claims this source supports

Environment engineering and perception/action interfaces dominate computer-agent validity.

## Claims this source weakens or contradicts

Using a benchmark result without the exact VM, observation, action, and retry configuration.

## Relevance to a mathematics paper

Motivates hierarchical reliability and nondeterministic-environment measurement.

## Connections to other sources

See the category and claim-level cross-references in [`INDEX.md`](INDEX.md) and the synthesis documents.

## Verification notes

Abstract and pages 1-2 checked for 369 tasks, supported operating systems, state setup and graders, human 72.36%, model 12.24%, and limitations. The archived file parsed successfully: 51 pages, 155793 extractable characters, SHA-256 `d4c6e20dd59467f005561b1e97199f9842fd3b0e9fdd93e66e06ba0ec09edfdb`.
