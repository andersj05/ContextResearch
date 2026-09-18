#!/usr/bin/env python3
"""Build the unified source inventory and non-academic source-note index."""

from __future__ import annotations

import csv
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CATALOG = ROOT / "catalog"

FIELDS = [
    "source_id",
    "title",
    "authors_or_org",
    "year",
    "source_class",
    "publication_status",
    "canonical_url",
    "pdf_path",
    "note_path",
    "accessed",
    "sha256",
    "review_status",
    "license_or_access_notes",
]


def read_csv(name: str) -> list[dict[str, str]]:
    with (CATALOG / name).open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def keyed(rows: list[dict[str, str]]) -> dict[str, dict[str, str]]:
    return {row["source_id"]: row for row in rows}


def parse_frontmatter(path: Path) -> dict[str, str]:
    text = path.read_text(encoding="utf-8")
    match = re.match(r"\A---\s*\n(.*?)\n---\s*\n", text, re.DOTALL)
    if not match:
        raise ValueError(f"missing frontmatter: {path}")
    values: dict[str, str] = {}
    for line in match.group(1).splitlines():
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        value = value.strip()
        if len(value) >= 2 and value[0] == value[-1] == '"':
            value = value[1:-1].replace('\\"', '"')
        values[key.strip()] = value
    return values


def academic_rows() -> list[dict[str, str]]:
    downloads = keyed(read_csv("paper-downloads.csv"))
    metadata = keyed(read_csv("paper-metadata.csv"))
    inventory = keyed(read_csv("pdf-inventory.csv"))
    distillations = keyed(read_csv("paper-distillations.csv"))
    ids = set(downloads)
    for label, data in [
        ("metadata", metadata),
        ("inventory", inventory),
        ("distillations", distillations),
    ]:
        if set(data) != ids:
            raise ValueError(
                f"academic ID mismatch for {label}: "
                f"missing={sorted(ids-set(data))}, extra={sorted(set(data)-ids)}"
            )

    rows: list[dict[str, str]] = []
    for source_id in sorted(ids):
        download = downloads[source_id]
        meta = metadata[source_id]
        inv = inventory[source_id]
        dist = distillations[source_id]
        status = download["publication_status"]
        source_class = "academic-preprint" if status.lower() == "preprint" else "academic-publication"
        rows.append(
            {
                "source_id": source_id,
                "title": download["title"],
                "authors_or_org": meta["authors"],
                "year": download["year"],
                "source_class": source_class,
                "publication_status": status,
                "canonical_url": download["landing_url"],
                "pdf_path": inv["pdf_path"],
                "note_path": f"paper-notes/{source_id}.md",
                "accessed": inv["accessed"],
                "sha256": inv["sha256"],
                "review_status": dist["review_status"],
                "license_or_access_notes": (
                    "Openly accessible research copy archived from the recorded canonical PDF URL; "
                    "copyright remains with the authors or publisher."
                ),
            }
        )
    return rows


def engineering_rows() -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for path in sorted((ROOT / "source-notes").glob("*.md")):
        if path.name in {"INDEX.md", "TEMPLATE.md"}:
            continue
        meta = parse_frontmatter(path)
        required = {
            "title",
            "author_or_org",
            "date",
            "source_type",
            "url",
            "accessed",
            "review_status",
        }
        missing = required - set(meta)
        if missing:
            raise ValueError(f"{path}: missing {sorted(missing)}")
        source_type = meta["source_type"]
        if source_type == "official-implementation-evidence":
            status = "versioned official implementation documentation"
            default_notes = "Canonical repository/docs reviewed; no repository snapshot redistributed."
        else:
            status = "non-peer-reviewed practitioner source"
            default_notes = "Canonical web page reviewed; no redistributed snapshot archived."
        version = meta.get("version_or_commit", "")
        access_notes = meta.get("license_or_access_notes", default_notes)
        if version:
            access_notes = f"{access_notes}; snapshot: {version}"
        rows.append(
            {
                "source_id": path.stem,
                "title": meta["title"],
                "authors_or_org": meta["author_or_org"],
                "year": meta["date"][:4],
                "source_class": source_type,
                "publication_status": status,
                "canonical_url": meta["url"],
                "pdf_path": "",
                "note_path": path.relative_to(ROOT).as_posix(),
                "accessed": meta["accessed"],
                "sha256": "",
                "review_status": meta["review_status"],
                "license_or_access_notes": access_notes,
            }
        )
    return rows


def write_catalog(rows: list[dict[str, str]]) -> None:
    path = CATALOG / "sources.csv"
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def md_escape(value: str) -> str:
    return value.replace("|", "\\|").replace("\n", " ")


def write_source_index(rows: list[dict[str, str]]) -> None:
    implementations = [r for r in rows if r["source_class"] == "official-implementation-evidence"]
    practitioner = [r for r in rows if r["source_class"] != "official-implementation-evidence"]
    lines = [
        "# Non-academic and implementation source notes",
        "",
        "This index covers official implementation evidence and practitioner engineering reports. "
        "Mechanism descriptions are kept distinct from controlled evidence of effects.",
        "",
        f"- Official implementation notes: **{len(implementations)}**",
        f"- Practitioner source notes: **{len(practitioner)}**",
        "- Research cutoff: **2026-09-04**",
        "",
        "## Official implementations",
        "",
        "| Source ID | Project / organization | Snapshot note |",
        "|---|---|---|",
    ]
    for row in implementations:
        note = Path(row["note_path"]).name
        lines.append(
            f"| [`{md_escape(row['source_id'])}`]({note}) | "
            f"{md_escape(row['title'])} / {md_escape(row['authors_or_org'])} | "
            f"{md_escape(row['license_or_access_notes'])} |"
        )
    lines += [
        "",
        "## Practitioner and engineering reports",
        "",
        "| Source ID | Source | Evidence class |",
        "|---|---|---|",
    ]
    for row in practitioner:
        note = Path(row["note_path"]).name
        lines.append(
            f"| [`{md_escape(row['source_id'])}`]({note}) | "
            f"{md_escape(row['title'])} / {md_escape(row['authors_or_org'])} | "
            f"{md_escape(row['source_class'])} |"
        )
    lines += [
        "",
        "The machine-readable inventory for these sources and the academic PDF corpus is "
        "[`catalog/sources.csv`](../catalog/sources.csv).",
        "",
    ]
    (ROOT / "source-notes" / "INDEX.md").write_text("\n".join(lines), encoding="utf-8", newline="\n")


def main() -> None:
    academic = academic_rows()
    engineering = engineering_rows()
    rows = sorted(academic + engineering, key=lambda row: row["source_id"])
    if len(rows) != len({r["source_id"] for r in rows}):
        raise ValueError("duplicate source IDs")
    write_catalog(rows)
    write_source_index(engineering)
    print(
        f"wrote {len(rows)} sources: {len(academic)} academic, "
        f"{len(engineering)} engineering/practitioner"
    )


if __name__ == "__main__":
    main()
