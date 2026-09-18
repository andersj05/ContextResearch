#!/usr/bin/env python3
"""Merge reviewed paper-distillation CSV fragments into the canonical catalog.

Rows are written in paper-download manifest order. The command is intentionally
strict: fragment headers must match, duplicate IDs are rejected unless --replace
is passed, every field must be populated, and the final ID set must equal the
manifest when --require-complete is used.
"""

from __future__ import annotations

import argparse
import csv
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_TARGET = ROOT / "catalog" / "paper-distillations.csv"
DEFAULT_MANIFEST = ROOT / "catalog" / "paper-downloads.csv"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("fragments", nargs="+", type=Path)
    parser.add_argument("--target", type=Path, default=DEFAULT_TARGET)
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--replace", action="store_true")
    parser.add_argument("--require-complete", action="store_true")
    return parser.parse_args()


def resolve(path: Path) -> Path:
    return path if path.is_absolute() else ROOT / path


def read_csv(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        if not reader.fieldnames:
            raise ValueError(f"missing CSV header: {path}")
        return reader.fieldnames, list(reader)


def main() -> int:
    args = parse_args()
    target = resolve(args.target)
    manifest = resolve(args.manifest)
    fieldnames, existing = read_csv(target)
    manifest_fields, manifest_rows = read_csv(manifest)
    if "source_id" not in manifest_fields:
        raise ValueError("manifest lacks source_id")

    rows_by_id: dict[str, dict[str, str]] = {}
    for row in existing:
        source_id = row["source_id"].strip()
        if not source_id or source_id in rows_by_id:
            raise ValueError(f"blank or duplicate existing source_id: {source_id!r}")
        rows_by_id[source_id] = row

    additions = 0
    replacements = 0
    for raw_fragment in args.fragments:
        fragment = resolve(raw_fragment)
        fragment_fields, rows = read_csv(fragment)
        if fragment_fields != fieldnames:
            raise ValueError(
                f"header mismatch in {fragment}: "
                f"expected {fieldnames!r}, got {fragment_fields!r}"
            )
        seen_fragment: set[str] = set()
        for row in rows:
            source_id = row["source_id"].strip()
            if not source_id or source_id in seen_fragment:
                raise ValueError(f"blank or duplicate fragment source_id: {source_id!r}")
            seen_fragment.add(source_id)
            missing = [field for field in fieldnames if not row[field].strip()]
            if missing:
                raise ValueError(f"{source_id} has blank fields: {missing}")
            if source_id in rows_by_id and not args.replace:
                raise ValueError(f"source_id already exists: {source_id}")
            if source_id in rows_by_id:
                replacements += 1
            else:
                additions += 1
            rows_by_id[source_id] = row

    order = [row["source_id"] for row in manifest_rows]
    if len(order) != len(set(order)):
        raise ValueError("manifest contains duplicate source IDs")
    manifest_ids = set(order)
    extra = sorted(set(rows_by_id) - manifest_ids)
    missing = sorted(manifest_ids - set(rows_by_id))
    if extra:
        raise ValueError(f"distillations contain IDs outside manifest: {extra}")
    if args.require_complete and missing:
        raise ValueError(f"distillations are missing manifest IDs: {missing}")

    ordered_rows = [rows_by_id[source_id] for source_id in order if source_id in rows_by_id]
    with target.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(ordered_rows)

    print(
        f"wrote {len(ordered_rows)} distillations "
        f"({additions} added, {replacements} replaced, {len(missing)} still missing)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
