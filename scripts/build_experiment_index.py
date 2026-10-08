#!/usr/bin/env python3
"""Build or check the offline experiment catalog; never import or run experiments."""
from __future__ import annotations

import argparse
import csv
from datetime import date
import os
from pathlib import Path
import re
import subprocess

ROOT = Path(__file__).resolve().parents[1]
CATALOG = ROOT / "experiments/registry.csv"
BASE = "experiments/dependency_memory/"
GROUPS = {
    "model": ("model-studies", "Model studies"),
    "math": ("mathematical-checks", "Mathematical checks and coding constructions"),
    "offline": ("offline-diagnostics", "Offline diagnostics and evidence replays"),
    "planned": ("planned-studies", "Prepared studies and unperformed evaluations"),
    "support": ("infrastructure", "Shared infrastructure and verification records"),
}
FIELDS = ["study_id", "title", "category", "status", "as_of", "claim_ids",
          "summary", "limitations", "entry_points", "code_paths", "protocol_paths", "result_paths"]
STATUSES = {"completed", "closed-with-gaps", "offline-complete", "prepared", "checkpoint"}
PATH_FIELDS = ("entry_points", "code_paths", "protocol_paths", "result_paths")


def parts(value: str) -> list[str]:
    return [p for p in value.split(";") if p]


def read_catalog() -> list[dict[str, str]]:
    with CATALOG.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames != FIELDS:
            raise ValueError(f"registry.csv columns must be {FIELDS}")
        return list(reader)


def link(path: str, origin: Path, label: str | None = None) -> str:
    relative = Path(os.path.relpath(ROOT / path, origin.parent)).as_posix()
    return f"[{label or path}]({relative})"


def render(rows: list[dict[str, str]]) -> dict[Path, str]:
    index = ROOT / "experiments/INDEX.md"
    header = ["# Experiment catalog", "",
              "Generated from [registry.csv](registry.csv). Edit the registry, then run",
              "`python scripts/build_experiment_index.py`. Dates describe the evidence checkpoint,",
              "not when this index was built. Read [current status](../docs/STATUS.md) first.", "",
              "A row is a study or diagnostic family, **not** an independent trial. Continuations",
              "are grouped with their original study; dispatches, valid answers and host attempts",
              "must not be added across overlapping reports. Plans and retrospective replays are",
              "separate from observed model outcomes. Imported third-party releases are outside",
              "this catalog; see [scope and maintenance](README.md).", ""]
    outputs = {}
    for category, (slug, title) in GROUPS.items():
        selected = sorted((r for r in rows if r["category"] == category),
                          key=lambda r: (r["as_of"], max(parts(r["claim_ids"]), default=""),
                                         r["study_id"]), reverse=True)
        page = ROOT / "experiments/summaries" / f"{slug}.md"
        header += [f"## {title}", "", f"[Read all {len(selected)} summaries](summaries/{slug}.md).", "",
                   "| Study | Evidence date | Status |", "|---|---|---|"]
        body = [f"# {title}", "", "[Catalog](../INDEX.md) · [Maintenance](../README.md)", "",
                "Generated from [registry.csv](../registry.csv); original reports and frozen",
                "contracts remain authoritative. Summaries describe the dated study scope.", ""]
        if category == "math":
            body += ["These are local derivations and finite computational checks, not model trials.",
                     "External proof and priority review remain open. Later constructions can improve",
                     "earlier bounds without changing the earlier certificates.", ""]
        if category == "model":
            body += ["Reported costs and counts are study-specific. These studies do not establish",
                     "production or native-compaction gains. Missing answers remain missing.", ""]
        for row in selected:
            header.append(f"| [{row['title']}](summaries/{slug}.md#{row['study_id']}) | {row['as_of']} | {row['status']} |")
            body += [f"## {row['study_id']}", "", f"**{row['title']}** — {row['as_of']} · {row['status']}", "",
                     row["summary"], "", f"**Limits:** {row['limitations']}", ""]
            if row["claim_ids"]:
                body += [f"Claims: {link('paper/claims.csv', page, ', '.join(parts(row['claim_ids'])))}.", ""]
            for field, label in zip(PATH_FIELDS, ("Read first", "Implementation", "Protocol", "Saved results")):
                paths = parts(row[field])
                if paths:
                    body += [f"{label}: " + "; ".join(link(p, page) for p in paths) + ".", ""]
        header.append("")
        outputs[page] = "\n".join(body)
    outputs[index] = "\n".join(header)
    return outputs


def validate(rows: list[dict[str, str]], *, check_generated: bool = True) -> tuple[dict, list[str]]:
    errors = []
    ids = set()
    with (ROOT / "paper/claims.csv").open(encoding="utf-8-sig", newline="") as handle:
        claims = {r["claim_id"] for r in csv.DictReader(handle)}
    referenced = set()
    for row in rows:
        sid = row.get("study_id", "")
        if set(row) != set(FIELDS) or any(v is None for v in row.values()):
            errors.append(f"{sid}: malformed CSV row")
            continue
        if not re.fullmatch(r"[a-z][a-z0-9-]*", sid) or sid in ids:
            errors.append(f"Invalid or duplicate study ID: {sid}")
        ids.add(sid)
        for field in ("title", "summary", "limitations", "entry_points"):
            if not row[field].strip():
                errors.append(f"{sid}: missing {field}")
        if row["category"] not in GROUPS or row["status"] not in STATUSES:
            errors.append(f"{sid}: invalid category/status")
        try:
            date.fromisoformat(row["as_of"])
        except ValueError:
            errors.append(f"{sid}: invalid evidence date")
        for claim in parts(row["claim_ids"]):
            if claim not in claims:
                errors.append(f"{sid}: unknown claim {claim}")
        for field in PATH_FIELDS:
            for name in parts(row[field]):
                path = ROOT / name
                if Path(name).is_absolute() or "\\" in name or not path.resolve().is_relative_to(ROOT) or not path.exists():
                    errors.append(f"{sid}: missing/unsafe {field}: {name}")
                referenced.add(name.rstrip("/"))
        if row["category"] in {"model", "math", "offline"} and not row["result_paths"]:
            errors.append(f"{sid}: evidence entry needs saved results")
    # Enumerate tracked paths, so ignored captures, local caches and temporary work
    # cannot silently become experimental evidence. New untracked results must be
    # registered before they are committed; explicit registry links are checked now.
    tracked = subprocess.run(["git", "ls-files", "--", BASE], cwd=ROOT,
                             check=True, capture_output=True, text=True).stdout.splitlines()
    packages = {BASE + p[len(BASE):].split("/", 1)[0] for p in tracked
                if "/" in p[len(BASE):] and not p.startswith(BASE + "results/")}
    results = {p for p in tracked if p.startswith(BASE + "results/")}
    def covered(path: str) -> bool:
        return any(path == ref or path.startswith(ref + "/") for ref in referenced)
    # Linking the whole implementation/results root defeats catalog coverage.
    if BASE.rstrip("/") in referenced or BASE + "results" in referenced:
        errors.append("Register individual packages/results, not their common root")
    for path in sorted(packages | results):
        if not covered(path):
            errors.append(f"Uncataloged package/result: {path}")
    if check_generated and not errors:
        for path, expected in render(rows).items():
            if not path.is_file() or path.read_text(encoding="utf-8") != expected:
                errors.append(f"Stale index: {path.relative_to(ROOT)}; run python scripts/build_experiment_index.py")
    return {"catalog_entries": len(rows), "implementation_packages": len(packages),
            "tracked_result_files": len(results)}, errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Check coverage, paths and generated summaries without writing")
    args = parser.parse_args()
    rows = read_catalog()
    counts, errors = validate(rows, check_generated=args.check)
    if errors:
        print("\n".join(errors))
        return 1
    if not args.check:
        for path, content in render(rows).items():
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8", newline="\n")
    print(("PASS" if args.check else "Built") + ": " + ", ".join(f"{k}={v}" for k, v in counts.items()))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
