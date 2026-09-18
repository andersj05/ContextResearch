---
title: "Measuring AI Ability to Complete Long Software Tasks"
authors: ["Thomas Kwa", "Ben West", "Joel Becker", "Amy Deng", "Katharyn Garcia", "Max Hasin", "Sami Jawhar", "Megan Kinniment", "Nate Rush", "Sydney Von Arx", "Ryan Bloom", "Thomas Broadley", "Haoxing Du", "Brian Goodrich", "Nikola Jurkovic", "Luke Harold Miles", "Seraphina Nix", "Tao Lin", "Chris Painter", "Neev Parikh", "David Rein", "Lucas Jun Koba Sato", "Hjalmar Wijk", "Daniel M. Ziegler", "Elizabeth Barnes", "Lawrence Chan"]
year: 2025
venue: "NeurIPS-2025"
source_type: "peer-reviewed"
paper_url: "https://papers.nips.cc/paper_files/paper/2025/hash/85069585133c4c168c865e65d72e9775-Abstract-Conference.html"
pdf_path: "papers/academic/kwa-2025-long-software-tasks.pdf"
accessed: "2026-09-04"
review_status: "fully-reviewed"
evidence_confidence: "high"
---

# kwa-2025-long-software-tasks — Measuring AI Ability to Complete Long Software Tasks

## Why this source is in the corpus

Makes model–harness–environment coupling observable in executable, long-horizon tasks.

## Research question

How does agent success vary with the human time required for software and research-engineering tasks?

## Harness mechanism studied

The study times skilled humans, runs agents on the same task families, fits success probability against log human duration, and defines the 50-percent completion horizon.

## Method and experimental setup

NeurIPS 2025 analysis of 170 tasks, more than 800 human baselines totaling 2,529 hours, and agents based on 12 frontier models from 2019-2025 with hierarchical bootstrap.

## Main findings

- The o3-based agent has an estimated 50-percent horizon around 110 minutes.
- The fitted frontier horizon doubles every 207 days with a 95% bootstrap interval of 166-240 days, but this is conditional on the task suite and scaffold and should not be read as a law of nature.

## Mathematical content

A logistic model relates log-odds of success to log human task time; the 50-percent horizon is the duration at fitted probability one half; uncertainty uses a hierarchy over families, tasks, and attempts.

## Evidence quality and limitations

Tasks are selected software/research work, human times are noisy, scaffold and model co-evolve, extrapolation is strong, and external validity to ordinary jobs is unknown.

## Important implementation details

Record human protocol and task family, model and scaffold versions, retries and assistance, fit diagnostics, clustered bootstrap, and out-of-sample calibration.

## Claims this source supports

Task duration provides a cross-benchmark difficulty coordinate when interpreted cautiously.

## Claims this source weakens or contradicts

Extrapolating the seven-month doubling rate as an unconditional forecast of automation.

## Relevance to a mathematics paper

Provides a logistic horizon model and hierarchical-bootstrap template.

## Connections to other sources

See the category and claim-level cross-references in [`INDEX.md`](INDEX.md) and the synthesis documents.

## Verification notes

Abstract and Sections 2-4 checked for 170 tasks, 12 models, over 800 baselines, 2,529 hours, 110 minutes, 207-day estimate, 166-240 interval, model, and caveats. The archived file parsed successfully: 54 pages, 153621 extractable characters, SHA-256 `460e6d25522be8a6d83a13bbedf8f691cc4cfadc12a3e57adb783647515d1c60`.
