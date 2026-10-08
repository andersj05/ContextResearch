# Experiments: summaries and evidence

**Start with the [experiment catalog](INDEX.md).** It is the central place to find
what ran, what happened, what failed, and where the supporting evidence lives.
For current priorities, use [status](../docs/STATUS.md).

## Layout

```text
experiments/
  README.md                 scope and maintenance rules
  registry.csv              editable study metadata; one row per study/family
  INDEX.md                  generated compact table of contents
  summaries/                generated summaries by evidence type
    model-studies.md
    mathematical-checks.md
    offline-diagnostics.md
    planned-studies.md
    infrastructure.md
  dependency_memory/        existing code and frozen study packages
    <study>/                implementation, tests, protocols, discovery evidence
    results/                saved certificates, reports and launch ledgers
    workflow_intake/        chronological development/prospective task records
```

The registry covers local study families, finite checks, post-hoc analyses and
prepared evaluations. A row is not a trial or an independent sample. Related
launches and never-attempted suffixes stay in the same study summary, with their
individual evidence directories linked. Replays of earlier answers are separate
offline entries, not additional model observations. The historical third-party
release and inherited literature are indexed through the [research map](../docs/RESEARCH_MAP.md).

## Read a study

1. Find its row in [INDEX.md](INDEX.md), or search the small [registry](registry.csv).
2. Read the summary's outcome and limitations, then its **Read first** note.
3. Inspect the frozen protocol and original report/ledger for exact counts, costs,
   information access, model revision, seeds and missing dispositions.
4. Load only the relevant implementation and tests. Check the associated claims
   in [paper/claims.csv](../paper/claims.csv) before using a result in writing.

Summaries route to primary evidence; they do not supersede it. Earlier scope
statements remain dated history when later results tighten a bound or close a run.

## Add or update a study

Edit [registry.csv](registry.csv), then regenerate the views:

```powershell
python scripts/build_experiment_index.py
python scripts/validate_context_repo.py --navigation-only
```

| Field | Contract |
|---|---|
| `study_id` | Stable lowercase hyphenated ID; also the summary anchor. Keep it when a study gets a continuation |
| `title` | Short descriptive study/family name |
| `category` | `model`, `math`, `offline`, `planned`, or `support` |
| `status` | `completed`, `closed-with-gaps`, `offline-complete`, `prepared`, or `checkpoint` |
| `as_of` | ISO date of the evidence checkpoint, not the index build date |
| `claim_ids` | Semicolon-separated existing claim IDs; empty for infrastructure or an unclaimed plan |
| `summary` | Observed outcome or explicitly unperformed plan; distinguish attempts, answers and paired cases |
| `limitations` | Strong controls, negative results, missingness, scope and unperformed extensions |
| `entry_points` | First narrative/report to read; semicolon-separated repository-relative paths |
| `code_paths` | Individual implementation packages or files, never the common implementation root |
| `protocol_paths` | Frozen protocol/contract paths; preserve each launch's original contract |
| `result_paths` | Specific result files or individual run directories; never the entire results root |

Paths use forward slashes, with no absolute paths or external URLs. CSV quoting
handles commas in prose. Do not hand-edit generated `INDEX.md` or `summaries/`.
`completed` means the declared study work finished; it does not mean the method
won. `closed-with-gaps` retains failures/missing outcomes and does not authorize
retries. `offline-complete` never implies a model evaluation. `prepared` includes
implemented/frozen runtimes whose intended evaluation has not occurred.

For a new dependency-memory study, put code and tests under
`dependency_memory/<study_id>/`, save a bounded protocol before running, and put
outputs under a specifically named results directory or certificate file.
A different research domain may use another top-level experiment package after
extending the catalog's coverage rules. Do not start another domain merely to
reclassify these existing packages.

The read-only `--check` mode rejects duplicate IDs, unknown claims, missing paths,
stale generated summaries, and uncataloged tracked implementation packages or
result files. Coverage currently targets `dependency_memory`; it is a navigation
check, not verification of numerical results. It ignores untracked/ignored local
scratch work; register new evidence before committing it and rerun the check
after staging so Git's tracked inventory includes it.

When a scientific conclusion changes, update the primary finding, claim register,
paper and current status together. Append consequential choices to
[DECISIONS.md](../docs/DECISIONS.md). Keep saved outputs and frozen protocols at
their original paths; source hashes and relative imports depend on them.
