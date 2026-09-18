# Migration and provenance

On September 18, 2026, the working research material was imported from `HarnessResearch` into the existing `ContextResearch` repository. The source checkout was at `b74402bf0d0949c845c933f5c64282f438b15764`; the destination began at `092a27ebf11349bbdcc93cb6181057148c1f188f`.

The import includes **658 files / 574,612,536 bytes**, including tracked source material, the previously uncommitted September 16 research/prototype, and 121 files from the pinned harness inspection cache. [Migration metadata](migration.json) and [per-file SHA-256 manifest](import-manifest.csv) record the baseline. File hashes were checked after copying.

## What was retained

- The complete committed literature library, catalogs, notes, synthesis, research documents, historical release, and supporting scripts.
- All active dependency-memory code, tests, and generated results, excluding Python bytecode.
- The September 16 survey, mathematics addendum, and detailed proposal.
- Codex, Pi, and OMP source slices, tree records, and the original fetch script from the investigation cache.
- The destination's initial Git commit and remote configuration. The source repository's `.git` directory and history were not merged into this repository.

The original `README.md` became `HARNESS_CORPUS_README.md`. Machine-specific links in the qualified compaction-release inspection were converted to repository-relative links. The manifest records original and migrated hashes and identifies that transformation; the source files were not changed.

## What was excluded

Temporary extracted paper text, rendered QA previews, installed dependencies, bytecode, and unrelated scratch files. These are disposable or reproducible and are not required for reading or running the active mathematical diagnostics.

## Preservation and subsequent edits

The source folder was retained as a migration backup; no source files were deleted. Continue the paper in `ContextResearch`. The import manifest is a historical baseline, not a demand that authored research files can never change. The setup subsequently updates the root `.gitignore`, adds navigation, and adds the paper workspace.

Git attributes preserve bytes rather than applying platform line-ending conversions, so evidence files and checksums survive future checkouts. Third-party copyright and licenses remain with their owners; see [source provenance](../sources/README.md).

[Setup validation](SETUP_VALIDATION.md) records the commands and outcomes from the completed migration.
