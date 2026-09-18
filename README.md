# ContextResearch

Research on memory, compaction, and context management for long-running language-model agents. This is the working repository for the paper and its evidence, experiments, and drafts.

**Current question:** When future task dependencies become known gradually, which compressed representations can survive successive memory limits without additional decision error, and how much extra memory is needed when they cannot?

The repository contains a checked finite example, a locally audited scaling derivation with a uniform error gap, and a deterministic artifact/manifest environment with an exact restricted recovery reference. Start with the [living findings draft](paper/findings-draft.md) for a short account of the results and next research step. External proof review and novelty assessment remain open. The project does **not** yet establish an LLM performance improvement or savings over native Codex or Claude compaction.

## Start here

1. [Current status and next work](docs/STATUS.md) — the shortest reliable handoff.
2. [Research map](docs/RESEARCH_MAP.md) — active work, background, and evidence limitations.
3. [Paper workspace](paper/README.md) — outline, manuscript starter, bibliography, and claim register.
4. [Detailed research proposal](research/LIVE_DEPENDENCY_RESEARCH_PROPOSAL_2026-09-16.md) — model, proof, and experiment design.
5. [Experiment protocol](docs/EXPERIMENT_PROTOCOL.md) — information access, native reasoning state, cache costs, and controls.
6. [Proof audit](research/PROOF_AUDIT_2026-09-18.md) and [deterministic environment results](experiments/dependency_memory/results/artifact_workflow_report.md) — the latest completed work.
7. [Recovery comparison](experiments/dependency_memory/results/recovery_frontier_report.md) and [literature positioning](research/LITERATURE_POSITIONING_2026-09-18.md) — when early inspection is worth its cost, and what remains unresolved.

Agents should first read [AGENTS.md](AGENTS.md). Historical notes are evidence and background; they do not override the current direction in `docs/STATUS.md`.

## Repository map

| Directory | Contents |
|---|---|
| `paper/` | Editable paper documents, references, and claim tracking |
| `docs/` | Current status, decisions, protocols, and contribution workflow |
| `experiments/dependency_memory/` | Standard-library Python diagnostics, tested workflow environment, and reproducible results |
| `research/` | Compaction survey, mathematics, proposal, and earlier research notes |
| `sources/` | Focused reading guide and pinned Codex, Pi, and OMP source snapshots |
| `papers/`, `paper-notes/` | Inherited library of 171 academic PDFs and associated notes |
| `source-notes/`, `synthesis/`, `catalog/` | Broader harness research, source metadata, and earlier claim ledger |
| `compaction_frontier_v1/` | Historical third-party release; read the evidence limitations before using it |
| `scripts/` | Offline validation, paper assembly, and earlier corpus utilities |
| `provenance/` | Migration manifest, source hashes, and setup validation |

## Reproduce the completed work

Python 3.10 or newer is sufficient for the active prototype. No packages, model API, network, credentials, or GPU are needed.

```powershell
python -m unittest discover -s experiments/dependency_memory -v
python experiments/dependency_memory/experiment.py
python experiments/dependency_memory/compatibility.py
python experiments/dependency_memory/compatibility_scaling.py
python experiments/dependency_memory/audit_scaling.py
python experiments/dependency_memory/run_artifact_workflow.py
python experiments/dependency_memory/run_recovery_frontier.py
python scripts/validate_context_repo.py
python scripts/build_paper.py
```

The experiment scripts regenerate their committed diagnostic results. The paper builder writes an assembled Markdown draft and a self-contained HTML preview under ignored `build/paper/`. The validator is read-only. See [the workflow](docs/RESEARCH_WORKFLOW.md) for details.

## Evidence and provenance

The active compaction investigation is dated September 16–18, 2026. The broader inherited literature snapshot is dated September 4, 2026; its review labels have not been upgraded by moving the files. Read the [migration record](provenance/README.md) and [historical corpus overview](HARNESS_CORPUS_README.md) for provenance and scope.

This repository preserves the existing `ContextResearch` Git history. The imported `HarnessResearch` folder remains available as a migration backup. Continue this paper here to avoid divergent working copies. Historical setup commits are on `codex/context-research-setup`; current work uses `task/` branches per the user's preference. The audit and initial environment are on `task/proof-audit-environment`; the recovery comparison and living draft continue on `task/recovery-frontier-draft`. No remote publication was requested.
