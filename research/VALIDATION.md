# Repository validation

- **Status:** PASS
- **Validated:** 2026-09-04T21:48:51Z
- **Validator:** `scripts/validate-repository.py`

## Corpus counts

| Check | Value |
|---|---:|
| academic PDFs | 171 |
| academic pages | 5,390 |
| PDF bytes | 525,061,332 (500.7 MiB) |
| academic publications / preprints | 100 / 71 |
| structured academic notes | 171 |
| implementation notes | 32 |
| practitioner notes | 16 |
| unified source records | 219 |
| bounded claim rows | 44 |
| claim-to-source references | 152 |
| required synthesis documents | 13 |
| visually spot-checked PDFs | 8 |

## Checks performed

- catalog ID equality and uniqueness;
- PDF presence, magic bytes, recorded size, and SHA-256;
- academic and engineering note structure;
- required distillation and source-catalog fields;
- source-note/catalog equality;
- required synthesis artifacts;
- synthesis math-delimiter balance;
- recorded PDF visual spot checks;
- local Markdown link resolution and repository containment;
- claim-ledger source-ID resolution;
- unresolved placeholder scan.

## Errors

- None.

## Warnings

- None.
