# Setup validation

Completed September 18, 2026 on Windows with Python 3.14.2. The active tools require Python 3.10+ and only its standard library. No model experiment, API inference, or training was run during setup.

## Migration integrity

- Imported 658 source files, totaling 574,612,536 bytes; each copy was checked against its prepared SHA-256.
- Preserved the existing ContextResearch Git history and remote configuration.
- Preserved the original HarnessResearch folder as a migration backup.
- Imported the previously uncommitted proposal, survey, mathematical addendum, and dependency-memory prototype.
- Repaired machine-specific links in one inspection document, recording both source and destination hashes.
- Final recheck: 657 imported files still match their migrated hashes exactly. The only deliberately changed imported file is the root `.gitignore`.
- Added the three pinned upstream license files separately, with URLs, dates, and hashes in `provenance/upstream-licenses.json`.

## Commands and results

| Command/check | Result |
|---|---|
| `python -B -m unittest discover -s experiments/dependency_memory -v` | PASS: 17 tests |
| `python -B experiments/dependency_memory/experiment.py` | Regenerated 14 finite-frontier rows and 810 constructed record configurations; no result drift |
| `python -B experiments/dependency_memory/compatibility.py` | Regenerated the 256-assignment certificate and three-bit witness; no result drift |
| `python -B scripts/validate_context_repo.py` | PASS: zero errors |
| `python -B scripts/build_paper.py` | Built standalone Markdown and offline HTML preview with 9 cited references |
| HTML structure check | 19 internal anchor targets resolved; zero external preview dependencies |
| `git diff --check` | PASS |

The repository validator checked 276 Markdown documents, 872 local links, 14 bibliography entries, 10 paper claims, all 171 PDF hashes, 195 immutable imported source/release hashes, and all three added licenses. It also recomputed the compatibility certificate and checked the workflow count against its summary. Code examples are excluded from document-link and citation detection.

## Reviewable setup commits

- `8297068`: import the corpus, compaction studies, and reproducible diagnostics.
- `a4b7086`: establish current scope, agent handoff, and evaluation protocol.
- `d73edd2`: add the manuscript starter, references, claim register, licenses, and offline tools.
- The following verification commit records this report and reconciles the preview documentation.

Work is committed locally on `codex/context-research-setup`. No push or remote publication was performed. Generated previews live under ignored `build/paper/`; editable drafts live under `paper/`.

## Scope of this validation

These checks establish migration integrity, usable navigation, consistent citations, and reproduction of the existing finite diagnostics. They do not certify theorem novelty, independently review all 171 papers, reproduce the supplied historical collection pipeline, or establish improvements over a deployed harness. The manuscript keeps proposed experiments and unresolved results explicit.
