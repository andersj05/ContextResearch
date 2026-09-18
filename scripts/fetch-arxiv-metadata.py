"""Fetch authoritative arXiv metadata for manifest entries that cite arXiv.

The script updates a compact CSV keyed by ``source_id``. Entries whose primary
landing page is not arXiv are retained with blank arXiv fields so downstream
checks can distinguish "not applicable" from a missing manifest row.
"""

from __future__ import annotations

import argparse
import csv
import re
import time
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path


ARXIV_ID = re.compile(
    r"arxiv\.org/(?:abs|pdf)/((?:\d{4}\.\d{4,5})|(?:[a-z-]+(?:\.[A-Z]{2})?/\d{7}))(?:v\d+)?",
    re.IGNORECASE,
)
ATOM = {"atom": "http://www.w3.org/2005/Atom", "arxiv": "http://arxiv.org/schemas/atom"}
FIELDS = [
    "source_id",
    "arxiv_id",
    "title",
    "authors",
    "published",
    "updated",
    "primary_category",
    "categories",
    "doi",
    "journal_reference",
    "metadata_source",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", default="catalog/paper-downloads.csv")
    parser.add_argument("--output", default="catalog/paper-metadata.csv")
    parser.add_argument("--overrides", default="catalog/paper-metadata-overrides.csv")
    parser.add_argument("--batch-size", type=int, default=40)
    return parser.parse_args()


def normalized(element: ET.Element | None) -> str:
    return " ".join((element.text if element is not None and element.text else "").split())


def fetch_batch(arxiv_ids: list[str]) -> dict[str, dict[str, str]]:
    query = urllib.parse.urlencode({"id_list": ",".join(arxiv_ids), "max_results": len(arxiv_ids)})
    request = urllib.request.Request(
        f"https://export.arxiv.org/api/query?{query}",
        headers={"User-Agent": "HarnessResearch/1.0 (bibliographic metadata)"},
    )
    with urllib.request.urlopen(request, timeout=60) as response:  # noqa: S310 - fixed trusted host
        root = ET.fromstring(response.read())

    records: dict[str, dict[str, str]] = {}
    for entry in root.findall("atom:entry", ATOM):
        canonical_url = normalized(entry.find("atom:id", ATOM))
        match = ARXIV_ID.search(canonical_url)
        if not match:
            continue
        arxiv_id = match.group(1)
        authors = [normalized(author.find("atom:name", ATOM)) for author in entry.findall("atom:author", ATOM)]
        categories = [category.attrib.get("term", "") for category in entry.findall("atom:category", ATOM)]
        primary = entry.find("arxiv:primary_category", ATOM)
        records[arxiv_id] = {
            "arxiv_id": arxiv_id,
            "title": normalized(entry.find("atom:title", ATOM)),
            "authors": "; ".join(author for author in authors if author),
            "published": normalized(entry.find("atom:published", ATOM)),
            "updated": normalized(entry.find("atom:updated", ATOM)),
            "primary_category": primary.attrib.get("term", "") if primary is not None else "",
            "categories": "; ".join(category for category in categories if category),
            "doi": normalized(entry.find("arxiv:doi", ATOM)),
            "journal_reference": normalized(entry.find("arxiv:journal_ref", ATOM)),
            "metadata_source": "arXiv API",
        }
    return records


def main() -> int:
    args = parse_args()
    root = Path(__file__).resolve().parents[1]
    manifest_path = root / args.manifest
    output_path = root / args.output
    overrides_path = root / args.overrides
    with manifest_path.open("r", encoding="utf-8-sig", newline="") as handle:
        manifest = list(csv.DictReader(handle))
    overrides: dict[str, dict[str, str]] = {}
    if overrides_path.exists():
        with overrides_path.open("r", encoding="utf-8-sig", newline="") as handle:
            overrides = {row["source_id"]: row for row in csv.DictReader(handle)}
        unknown = sorted(set(overrides) - {row["source_id"] for row in manifest})
        if unknown:
            raise ValueError(f"metadata overrides reference unknown source IDs: {unknown}")

    ids_by_source: dict[str, str] = {}
    for row in manifest:
        match = ARXIV_ID.search(f"{row['landing_url']} {row['pdf_url']}")
        if match:
            ids_by_source[row["source_id"]] = match.group(1)

    unique_ids = sorted(set(ids_by_source.values()))
    fetched: dict[str, dict[str, str]] = {}
    for start in range(0, len(unique_ids), args.batch_size):
        batch = unique_ids[start : start + args.batch_size]
        print(f"Fetching arXiv metadata {start + 1}-{start + len(batch)} of {len(unique_ids)}")
        fetched.update(fetch_batch(batch))
        if start + args.batch_size < len(unique_ids):
            time.sleep(3)

    output_rows = []
    missing = []
    for row in manifest:
        source_id = row["source_id"]
        arxiv_id = ids_by_source.get(source_id, "")
        record = fetched.get(arxiv_id, {})
        if arxiv_id and not record:
            missing.append(f"{source_id} ({arxiv_id})")
        output_row = {
            "source_id": source_id,
            "arxiv_id": arxiv_id,
            "title": record.get("title", row["title"]),
            "authors": record.get("authors", ""),
            "published": record.get("published", ""),
            "updated": record.get("updated", ""),
            "primary_category": record.get("primary_category", ""),
            "categories": record.get("categories", ""),
            "doi": record.get("doi", ""),
            "journal_reference": record.get("journal_reference", ""),
            "metadata_source": record.get("metadata_source", "manifest-only"),
        }
        for field, value in overrides.get(source_id, {}).items():
            if field != "source_id" and field in output_row and value.strip():
                output_row[field] = value.strip()
        output_rows.append(output_row)

    with output_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(output_rows)

    print(f"Wrote {len(output_rows)} rows to {output_path.relative_to(root)}")
    if missing:
        print("arXiv API omitted: " + ", ".join(missing))
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
