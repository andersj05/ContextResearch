# Repository structure and placement rules

Organization reviewed October 7, 2026. The central problem was navigation:
the README and status repeated milestones, results were scattered across dated
notes and output folders, and the implementation README covered only early work.
The new catalog provides one maintained route through those materials.

## Where files belong

| Content | Canonical home | Rule |
|---|---|---|
| Project introduction | [Root README](../README.md) | Short orientation; do not prepend each new result |
| Current checkpoint and next gates | [STATUS.md](STATUS.md) | Replace obsolete current prose; retain detailed history separately |
| Task-based retrieval and authority | [RESEARCH_MAP.md](RESEARCH_MAP.md) | Routes to evidence types, not another milestone log |
| Study summaries | [experiments/registry.csv](../experiments/registry.csv) | Edit once; generate categorized summaries and index |
| Code and study-specific tests | [experiments/dependency_memory/](../experiments/dependency_memory/) | One named package per new study; retain existing imports |
| Frozen protocol and discovery records | The study's implementation package | Version follow-ups separately; never overwrite a frozen launch |
| Raw/saved outputs and generated result reports | [results/](../experiments/dependency_memory/results/) | Stable file/run identity, explicit provenance, catalog link |
| Actual workflow task intake | [workflow_intake/](../experiments/dependency_memory/workflow_intake/README.md) | Preserve development/prospective/evaluator/actor separation |
| Derivations, findings and audits | [research/](../research/README.md) | Dated note linked from a study or topic index |
| Substantive claims and publishable writing | [paper/](../paper/README.md) | Claims CSV is authoritative; manuscript is the writing entry point |
| Shared protocols and process | [docs/](README.md) | Index new process documents here |
| Important choices | [DECISIONS.md](DECISIONS.md) | Append dated decisions; do not rewrite historical permissions |
| Old navigation and handoffs | [docs/history/](history/README.md) | Optional historical context, excluded from the startup reading path |
| Focused sources | [sources/](../sources/READING_GUIDE.md) | Keep review scope, original IDs and pinned commits |
| Inherited library and third-party evidence | Existing `papers/`, `paper-notes/`, `source-notes/`, `catalog/`, `synthesis/`, `compaction_frontier_v1/` | Preserve upstream/source provenance; use indexes to retrieve selectively |
| Build previews and temporary work | Ignored `build/` and `tmp/` | Do not promote logs or scratch outputs to evidence automatically |

## Retrieval budget for research agents

Read root README, status and research map, then the relevant catalog section.
Open one study's finding/protocol/result before its code. Use targeted `rg` searches
over `experiments/registry.csv`, `paper/claims.csv` or a chosen package. Avoid
loading all result ledgers, the decision history or the inherited PDF archive.

Keep status focused on the latest checkpoint and unresolved questions. Keep detailed
outcomes in study summaries, and derivations in their primary notes. The CSV is
the single editable source for generated summaries; do not manually duplicate
those summaries into every entry point.

## Why existing evidence paths remain stable

Frozen manifests bind source bytes, some Python modules use repository-relative
imports, claim rows cite exact paths, and inherited imports have provenance hashes.
A wholesale move would create scientific revalidation work with little retrieval
benefit. The October 7 change relocates the accumulated **navigation history** and
adds explicit category/placement rules while keeping scientific evidence intact.

Future physical moves require a scoped migration: inventory imports, commands,
claim/evidence paths and hash bindings first; preserve frozen originals or recorded
mappings; update links and verify the affected scientific artifacts. Do not change
historical hashes merely to make a new path pass validation.

## Checks

```powershell
# Fast, read-only organization and documentation checks
python scripts/build_experiment_index.py --check
python scripts/validate_context_repo.py --navigation-only

# Scientific checks after changes to code, evidence, claims or generators
python -m unittest discover -s experiments/dependency_memory -v
python scripts/validate_context_repo.py
python scripts/build_paper.py
```

The navigation-only check does not grade scientific results or verify imported
bytes. The default validator retains its full offline behavior. An organization
task is not a new workflow-evaluation episode or a model-launch authorization.
