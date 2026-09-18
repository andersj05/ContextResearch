# Research and drafting workflow

## Reading and adding evidence

Start from the [research map](RESEARCH_MAP.md) and [focused sources](../sources/READING_GUIDE.md). Record a source's canonical URL, version or commit, access/review date, relevant claim, and limitations. For a new paper, reuse [the note template](../paper-notes/TEMPLATE.md) when a full note is useful; brief focused notes may live in `sources/notes/`.

Do not upgrade an inherited `skimmed` label merely because a file was imported. Living provider docs require a fresh check before claims about present behavior. Keep third-party material and original results distinguishable from our interpretations.

## Writing

Edit [the manuscript](../paper/manuscript.md) and [the outline](../paper/outline.md). Use stable citation keys from [the bibliography](../paper/references.bib), in the form `[@key]`. Track nontrivial claims in [the claim register](../paper/claims.csv). Mark prospective experiments and missing results explicitly; no placeholder number should look like a measurement.

Run `python scripts/build_paper.py` to generate `build/paper/manuscript.md` and `build/paper/preview.html`. The HTML preview renders headings, prose, code blocks, and citations locally with navigation. Mathematics remains in readable text/code form; this is not a venue-formatted submission or a LaTeX renderer. The assembled Markdown embeds the reference list so it can be shared without repository-relative links. Venue-specific PDF/LaTeX or Word production is a later formatting step.

For a new derivation, use [the derivation template](../paper/templates/derivation.md). For an experiment, use [the experiment-plan template](../paper/templates/experiment-plan.md). For source-specific notes, use [the source-note template](../paper/templates/source-note.md).

## Reproduction

```powershell
python -m unittest discover -s experiments/dependency_memory -v
python experiments/dependency_memory/experiment.py
python experiments/dependency_memory/compatibility.py
python experiments/dependency_memory/compatibility_scaling.py
python experiments/dependency_memory/audit_scaling.py
python experiments/dependency_memory/run_artifact_workflow.py
python scripts/validate_context_repo.py
python scripts/build_paper.py
```

The active tools use only Python's standard library. Run commands from the repository root. `scripts/validate_context_repo.py` checks links in the active documents, citation keys, claim evidence paths, imported PDF hashes, and deterministic results without changing source documents. It intentionally does not execute imported collection pipelines.

The inherited `scripts/validate-repository.py` audits the older broad corpus and writes `research/VALIDATION.md`. That is a historical report; prefer the new validator for routine work. Optional Parquet inspection requires the dependencies described by the inspection script and is not part of the core setup.

## Commits and handoffs

Commit coherent increments: evidence import, proof change, protocol change, draft revision, or experiment result. Include the relevant validation in the commit or handoff. Update status when a milestone changes. Use small deterministic fixtures in Git; keep generated document previews and temporary work under ignored `build/` or `tmp/`.

The initial migration recorded hashes in [the import manifest](../provenance/import-manifest.csv). Those hashes describe the import baseline. An intentionally edited research note may later differ; preserve provenance and explain meaningful scientific changes in Git. Third-party snapshots and release data should remain immutable.
