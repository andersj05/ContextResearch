# ContextResearch

Research on repeated context compression when future task dependencies become
known gradually. We study which representations survive successive memory limits,
what information must be retained, and whether the mechanism helps real agents.

## Start here

For a visual introduction, open the [research overview](docs/research-overview.html):
the question, results, key decisions, searchable study library and next steps.
It is a self-contained HTML snapshot as of October 9, 2026.

1. [Current status](docs/STATUS.md): scientific checkpoint, open questions and next gates.
2. [Research map](docs/RESEARCH_MAP.md): choose the evidence relevant to your task.
3. [Experiment catalog](experiments/INDEX.md): summaries of every registered local
   study and diagnostic family, including negative results, interrupted runs and plans.

For research agents, read [AGENTS.md](AGENTS.md), then the three entry points above.
Load the selected summary and its primary evidence before making a claim. The
171-paper inherited library is available for targeted retrieval, not required context.

## Current evidence

The scientific checkpoint is October 2, 2026: C75, living draft v0.42. The local
theory includes the exact four-bit chain optimum **9/32**, the full asymptotic
rate curve, and finite coding constructions. Model studies contain useful failure
observations and strong direct-retention/recovery controls. **Practical improvement
over deployed or native compaction remains unestablished.** External proof and
priority review remain open. See [status](docs/STATUS.md) for the current scope;
the [historical handoff](docs/history/STATUS_2026-10-02.md) retains earlier milestones.

## Repository map

| Location | Purpose and entry point |
|---|---|
| [docs/](docs/README.md) | Current status, decisions, protocols and research workflow |
| [experiments/](experiments/README.md) | Study registry and categorized summaries |
| [experiments/dependency_memory/](experiments/dependency_memory/README.md) | Executable code, frozen contracts and saved results at stable paths |
| [research/](research/README.md) | Derivations, findings, source comparisons and dated audits |
| [paper/](paper/README.md) | Manuscript, living findings, authoritative claim register and bibliography |
| [sources/](sources/READING_GUIDE.md) | Focused readings and pinned implementation snapshots |
| [papers/](papers/), [paper-notes/](paper-notes/INDEX.md) | Inherited academic library and notes |
| [source-notes/](source-notes/INDEX.md), [synthesis/](synthesis/00-executive-map.md), [catalog/](catalog/sources.csv) | Inherited implementation notes, synthesis and source metadata |
| [provenance/](provenance/README.md) | Import records, source hashes and setup history |
| [compaction_frontier_v1/](compaction_frontier_v1/docs/README.md) | Historical supplied release; read its [evidence limitations](research/COMPACTION_FRONTIER_REVERSE_ENGINEERING.md) |
| [scripts/](scripts/README.md) | Index maintenance, validation and paper assembly |

See [where files belong](docs/REPOSITORY_STRUCTURE.md) before adding or moving files.
Use ignored `build/` for generated previews and `tmp/` for disposable work.

## Reproduce the completed work

Run from the repository root with Python 3.11+. These checks are offline and
require no model credentials, packages or GPU:

```powershell
python scripts/build_experiment_index.py --check
python -m unittest discover -s experiments/dependency_memory -t . -v
python scripts/validate_context_repo.py
python scripts/build_paper.py
```

The full scientific checks can take many minutes. The index check is fast and
does not run experiments. The paper builder writes ignored `build/paper/` previews.
For scoped checks and deliberate result regeneration, follow the selected study's
README and [research workflow](docs/RESEARCH_WORKFLOW.md). Frozen model launches
and historical collection scripts are not repository checks. Byte-identical
executed-workflow reproduction was recorded on Windows; portability is not established.

## Evidence and provenance

[paper/claims.csv](paper/claims.csv) governs substantive claims. The experiment
catalog routes to evidence; it does not replace raw results, protocols or claims.
Imported material retains its original IDs, hashes and review status. See the
[migration record](provenance/README.md) and [inherited corpus overview](HARNESS_CORPUS_README.md).
This remains the sole working repository; use `task/` for new branches.
