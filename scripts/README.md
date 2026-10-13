# Repository tools

Run from the repository root. Most research work needs only these entry points:

| Command | Purpose | Writes |
|---|---|---|
| `python scripts/build_experiment_index.py --check` | Fast catalog paths, coverage and freshness check | Nothing |
| `python scripts/build_experiment_index.py` | Rebuild views from the editable registry | Experiment index and categorized summaries |
| `python scripts/validate_context_repo.py --navigation-only` | Fast Markdown links, citations, claims and catalog checks | Nothing |
| `python scripts/validate_context_repo.py` | Full offline evidence validation and deterministic regeneration in memory | Nothing |
| `python scripts/build_paper.py` | Assemble the manuscript and check citations | Ignored `build/paper/` previews |
| `python scripts/run_offline_tests_parallel.py --workers 8 --output tmp/offline-tests` | Run every discovered unittest once across isolated module processes; verify exact test-ID coverage | New per-module logs, manifest and summary; choose an unused output directory |
| `python scripts/inspect_rollback_information.py` | Reinspect saved v6/v7 request boundaries and descriptive recovery endpoints, without model calls | Nothing unless an unused `--output` path is supplied |

The full scientific test command is
`python -m unittest discover -s experiments/dependency_memory -v`.
The parallel runner is an alternative for the same discovered suite, with
separate temporary directories and explicit outcomes for every allocated test.
Its successful exit requires both complete coverage and passing results;
environment-dependent skips remain visible.
Use a selected [study summary](../experiments/INDEX.md) and its implementation
README for scoped scientific commands. Result generators can overwrite their
named outputs; choose them deliberately.

Other scripts here analyze saved Luna/transfer evidence, prepare particular
historical launches, or maintain the inherited source corpus. They are not an
instruction to run every script. In particular, `fetch-papers.ps1`,
`fetch-arxiv-metadata.py` and historical collection/recovery utilities can require
network services or original inputs. The inherited `validate-repository.py`
writes a historical broad-corpus report and is not the default validator.
