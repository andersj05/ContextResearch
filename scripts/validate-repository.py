#!/usr/bin/env python3
"""Validate the research corpus, structured notes, catalogs, and local links."""

from __future__ import annotations

import csv
import hashlib
import re
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import unquote


ROOT = Path(__file__).resolve().parents[1]
CATALOG = ROOT / "catalog"
REPORT = ROOT / "research" / "VALIDATION.md"

PAPER_SECTIONS = [
    "Why this source is in the corpus",
    "Research question",
    "Harness mechanism studied",
    "Method and experimental setup",
    "Main findings",
    "Mathematical content",
    "Evidence quality and limitations",
    "Important implementation details",
    "Claims this source supports",
    "Claims this source weakens or contradicts",
    "Relevance to a mathematics paper",
    "Connections to other sources",
    "Verification notes",
]

SOURCE_SECTIONS = [
    "Why this source is in the corpus",
    "System or claim described",
    "Architecture / mechanism",
    "Empirical evidence",
    "Mathematical or formal content",
    "What is directly evidenced",
    "What is interpretation or advocacy",
    "Limitations, incentives, and likely biases",
    "Transferable engineering lessons",
    "Connections to academic work",
    "Verification notes",
]

SYNTHESIS_FILES = [
    "00-executive-map.md",
    "01-definitions-and-taxonomy.md",
    "02-architecture-and-design-patterns.md",
    "03-empirical-evidence-and-benchmark-validity.md",
    "04-mathematical-foundations.md",
    "05-open-source-harnesses.md",
    "06-practitioner-evidence.md",
    "07-research-agenda.md",
    "08-paper-thesis-options.md",
    "09-self-building-and-self-improving-harnesses.md",
    "10-mathematics-of-harness-improvement.md",
    "11-self-improving-experimental-blueprint.md",
    "report-source.md",
]


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def ids(rows: list[dict[str, str]]) -> set[str]:
    return {row["source_id"] for row in rows}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def local_markdown_links(path: Path) -> list[str]:
    text = path.read_text(encoding="utf-8")
    # The corpus uses simple inline Markdown links for local artifacts. Remote URLs,
    # email links, and same-document fragments do not require filesystem checks.
    targets = re.findall(r"(?<!!)\[[^\]]*\]\(([^)]+)\)", text)
    local: list[str] = []
    for raw in targets:
        target = raw.strip().strip("<>")
        if target.startswith(("http://", "https://", "mailto:", "#", "codex:")):
            continue
        target = unquote(target.split("#", 1)[0])
        if target:
            local.append(target)
    return local


def validate() -> tuple[list[str], list[str], dict[str, int]]:
    errors: list[str] = []
    warnings: list[str] = []

    downloads = read_csv(CATALOG / "paper-downloads.csv")
    metadata = read_csv(CATALOG / "paper-metadata.csv")
    inventory = read_csv(CATALOG / "pdf-inventory.csv")
    distillations = read_csv(CATALOG / "paper-distillations.csv")
    sources = read_csv(CATALOG / "sources.csv")
    visual_qa = read_csv(CATALOG / "pdf-visual-qa.csv")

    expected_ids = ids(downloads)
    if len(downloads) != len(expected_ids):
        errors.append("paper-downloads.csv contains duplicate source IDs")
    for name, rows in [
        ("paper-metadata.csv", metadata),
        ("pdf-inventory.csv", inventory),
        ("paper-distillations.csv", distillations),
    ]:
        if ids(rows) != expected_ids:
            errors.append(
                f"{name} ID mismatch: missing={sorted(expected_ids-ids(rows))}, "
                f"extra={sorted(ids(rows)-expected_ids)}"
            )

    source_ids = ids(sources)
    if len(sources) != len(source_ids):
        errors.append("sources.csv contains duplicate source IDs")
    if not expected_ids.issubset(source_ids):
        errors.append(f"sources.csv is missing academic IDs: {sorted(expected_ids-source_ids)}")

    inventory_by_id = {row["source_id"]: row for row in inventory}
    total_pages = 0
    total_bytes = 0
    for source_id in sorted(expected_ids):
        row = inventory_by_id[source_id]
        pdf = ROOT / row["pdf_path"]
        if not pdf.is_file():
            errors.append(f"missing PDF: {row['pdf_path']}")
            continue
        size = pdf.stat().st_size
        total_bytes += size
        try:
            total_pages += int(row["pages"])
        except ValueError:
            errors.append(f"invalid page count for {source_id}: {row['pages']!r}")
        with pdf.open("rb") as handle:
            if handle.read(5) != b"%PDF-":
                errors.append(f"invalid PDF magic: {row['pdf_path']}")
        if str(size) != row["bytes"]:
            errors.append(f"size mismatch for {source_id}: file={size}, catalog={row['bytes']}")
        actual_hash = sha256(pdf)
        if actual_hash.lower() != row["sha256"].lower():
            errors.append(f"SHA-256 mismatch for {source_id}")

    pdf_files = set((ROOT / "papers" / "academic").glob("*.pdf"))
    inventory_files = {ROOT / row["pdf_path"] for row in inventory}
    if pdf_files != inventory_files:
        errors.append(
            "PDF directory/inventory mismatch: "
            f"unlisted={sorted(str(p.relative_to(ROOT)) for p in pdf_files-inventory_files)}, "
            f"missing={sorted(str(p.relative_to(ROOT)) for p in inventory_files-pdf_files)}"
        )

    paper_notes = {
        path.stem: path
        for path in (ROOT / "paper-notes").glob("*.md")
        if path.name not in {"INDEX.md", "TEMPLATE.md"}
    }
    if set(paper_notes) != expected_ids:
        errors.append(
            "paper-note ID mismatch: "
            f"missing={sorted(expected_ids-set(paper_notes))}, "
            f"extra={sorted(set(paper_notes)-expected_ids)}"
        )
    for source_id, path in paper_notes.items():
        text = path.read_text(encoding="utf-8")
        for section in PAPER_SECTIONS:
            if f"## {section}" not in text:
                errors.append(f"{path.relative_to(ROOT)} missing section: {section}")

    required_distillation = [
        "research_question",
        "mechanism",
        "method",
        "main_findings",
        "mathematics",
        "limitations",
        "implementation_details",
        "supports",
        "weakens",
        "math_relevance",
        "verification",
        "review_status",
        "evidence_confidence",
    ]
    for row in distillations:
        for field in required_distillation:
            if not row.get(field, "").strip():
                errors.append(f"paper-distillations.csv: {row['source_id']} blank {field}")

    source_notes = [
        path
        for path in (ROOT / "source-notes").glob("*.md")
        if path.name not in {"INDEX.md", "TEMPLATE.md"}
    ]
    for path in source_notes:
        text = path.read_text(encoding="utf-8")
        if not text.startswith("---\n") and not text.startswith("---\r\n"):
            errors.append(f"{path.relative_to(ROOT)} missing frontmatter")
        for section in SOURCE_SECTIONS:
            if f"## {section}" not in text:
                errors.append(f"{path.relative_to(ROOT)} missing section: {section}")

    catalog_note_paths = {row["note_path"] for row in sources}
    expected_note_paths = {
        path.relative_to(ROOT).as_posix() for path in paper_notes.values()
    } | {path.relative_to(ROOT).as_posix() for path in source_notes}
    if catalog_note_paths != expected_note_paths:
        errors.append(
            "source catalog/note mismatch: "
            f"unlisted={sorted(expected_note_paths-catalog_note_paths)}, "
            f"missing={sorted(catalog_note_paths-expected_note_paths)}"
        )

    required_source_fields = [
        "source_id",
        "title",
        "authors_or_org",
        "year",
        "source_class",
        "publication_status",
        "canonical_url",
        "note_path",
        "accessed",
        "review_status",
        "license_or_access_notes",
    ]
    for row in sources:
        for field in required_source_fields:
            if not row.get(field, "").strip():
                errors.append(f"sources.csv: {row['source_id']} blank {field}")
        if not row["canonical_url"].startswith("https://"):
            warnings.append(f"non-HTTPS canonical URL for {row['source_id']}: {row['canonical_url']}")

    for name in SYNTHESIS_FILES:
        path = ROOT / "synthesis" / name
        if not path.is_file() or path.stat().st_size < 1000:
            errors.append(f"missing or unexpectedly small synthesis: synthesis/{name}")
            continue
        text = path.read_text(encoding="utf-8")
        for opening, closing, label in [
            (r"\[", r"\]", "display-math"),
            (r"\(", r"\)", "inline-math"),
        ]:
            if text.count(opening) != text.count(closing):
                errors.append(
                    f"unbalanced {label} delimiters in synthesis/{name}: "
                    f"{text.count(opening)} opening, {text.count(closing)} closing"
                )

    for row in visual_qa:
        if row.get("source_id", "") not in expected_ids:
            errors.append(f"visual QA references unknown PDF: {row.get('source_id', '')}")
        if row.get("result", "").lower() != "pass":
            errors.append(f"visual QA did not pass for {row.get('source_id', '')}")
        if not row.get("inspection", "").strip():
            errors.append(f"visual QA lacks inspection notes for {row.get('source_id', '')}")

    # Check local Markdown targets across authored research artifacts. Templates are
    # included because a broken relative example can propagate into generated notes.
    markdown_roots = [ROOT / "README.md"]
    for directory in ["catalog", "paper-notes", "papers", "research", "source-notes", "synthesis"]:
        markdown_roots.extend((ROOT / directory).rglob("*.md"))
    for path in markdown_roots:
        for target in local_markdown_links(path):
            resolved = (path.parent / target).resolve()
            try:
                resolved.relative_to(ROOT.resolve())
            except ValueError:
                errors.append(f"{path.relative_to(ROOT)} link escapes repository: {target}")
                continue
            if not resolved.exists():
                errors.append(f"{path.relative_to(ROOT)} broken local link: {target}")

    # Validate source identifiers named in the claim ledger.
    ledger = (CATALOG / "claim-source-ledger.md").read_text(encoding="utf-8")
    claim_rows = [line for line in ledger.splitlines() if re.match(r"^\| C\d+ \|", line)]
    claim_ids: list[str] = []
    for line in claim_rows:
        cells = line.split("|")
        if len(cells) < 5:
            errors.append(f"malformed claim ledger row: {line[:80]}")
            continue
        for source_id in cells[3].split(";"):
            source_id = source_id.strip()
            if source_id:
                claim_ids.append(source_id)
                if source_id not in source_ids:
                    errors.append(f"claim ledger references unknown source ID: {source_id}")

    # Placeholders are prohibited, but the ordinary noun "todo" is legitimate in
    # context-engineering notes and is therefore not part of this scan.
    placeholder = re.compile(r"\b(?:TBD|PLACEHOLDER|FIXME|CITATION NEEDED)\b", re.IGNORECASE)
    for path in markdown_roots:
        # The generated validation report names this check and may contain a prior
        # failure message, so it must not recursively validate itself.
        if path.resolve() == REPORT.resolve():
            continue
        match = placeholder.search(path.read_text(encoding="utf-8"))
        if match:
            errors.append(f"placeholder {match.group(0)!r} in {path.relative_to(ROOT)}")

    class_counts = Counter(row["source_class"] for row in sources)
    stats = {
        "academic_pdfs": len(inventory),
        "academic_pages": total_pages,
        "academic_bytes": total_bytes,
        "paper_notes": len(paper_notes),
        "source_notes": len(source_notes),
        "unified_sources": len(sources),
        "claims": len(claim_rows),
        "claim_source_references": len(claim_ids),
        "syntheses": len(SYNTHESIS_FILES),
        "visually_spot_checked_pdfs": len(visual_qa),
        "academic_publications": class_counts["academic-publication"],
        "academic_preprints": class_counts["academic-preprint"],
        "implementation_notes": class_counts["official-implementation-evidence"],
        "practitioner_notes": (
            class_counts["engineering-blog"] + class_counts["practitioner-report"]
        ),
    }
    return errors, warnings, stats


def write_report(errors: list[str], warnings: list[str], stats: dict[str, int]) -> None:
    status = "PASS" if not errors else "FAIL"
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    mib = stats["academic_bytes"] / (1024 * 1024)
    lines = [
        "# Repository validation",
        "",
        f"- **Status:** {status}",
        f"- **Validated:** {now}",
        "- **Validator:** `scripts/validate-repository.py`",
        "",
        "## Corpus counts",
        "",
        "| Check | Value |",
        "|---|---:|",
        f"| academic PDFs | {stats['academic_pdfs']} |",
        f"| academic pages | {stats['academic_pages']:,} |",
        f"| PDF bytes | {stats['academic_bytes']:,} ({mib:.1f} MiB) |",
        f"| academic publications / preprints | {stats['academic_publications']} / {stats['academic_preprints']} |",
        f"| structured academic notes | {stats['paper_notes']} |",
        f"| implementation notes | {stats['implementation_notes']} |",
        f"| practitioner notes | {stats['practitioner_notes']} |",
        f"| unified source records | {stats['unified_sources']} |",
        f"| bounded claim rows | {stats['claims']} |",
        f"| claim-to-source references | {stats['claim_source_references']} |",
        f"| required synthesis documents | {stats['syntheses']} |",
        f"| visually spot-checked PDFs | {stats['visually_spot_checked_pdfs']} |",
        "",
        "## Checks performed",
        "",
        "- catalog ID equality and uniqueness;",
        "- PDF presence, magic bytes, recorded size, and SHA-256;",
        "- academic and engineering note structure;",
        "- required distillation and source-catalog fields;",
        "- source-note/catalog equality;",
        "- required synthesis artifacts;",
        "- synthesis math-delimiter balance;",
        "- recorded PDF visual spot checks;",
        "- local Markdown link resolution and repository containment;",
        "- claim-ledger source-ID resolution;",
        "- unresolved placeholder scan.",
        "",
        "## Errors",
        "",
    ]
    lines.extend([f"- {error}" for error in errors] or ["- None."])
    lines += ["", "## Warnings", ""]
    lines.extend([f"- {warning}" for warning in warnings] or ["- None."])
    lines.append("")
    REPORT.write_text("\n".join(lines), encoding="utf-8", newline="\n")


def main() -> int:
    errors, warnings, stats = validate()
    write_report(errors, warnings, stats)
    print(
        f"{'PASS' if not errors else 'FAIL'}: {stats['academic_pdfs']} PDFs, "
        f"{stats['unified_sources']} sources, {stats['claims']} claims, "
        f"{len(errors)} errors, {len(warnings)} warnings"
    )
    for error in errors:
        print(f"ERROR: {error}")
    for warning in warnings:
        print(f"WARNING: {warning}")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
