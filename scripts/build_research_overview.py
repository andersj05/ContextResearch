#!/usr/bin/env python3
"""Build the self-contained research overview from the existing study registry.

Offline documentation only: does not import scientific code or run experiments.
The narrative is an explicitly dated editorial snapshot in the HTML template.
"""
from __future__ import annotations

import argparse
from collections import Counter
import csv
import hashlib
import re
from html import escape
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import quote, unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "experiments/registry.csv"
TEMPLATE = ROOT / "scripts/templates/research_overview.html"
OUTPUT = ROOT / "docs/research-overview.html"
LABELS = {"math": "Mathematical result", "model": "Model study",
          "offline": "Offline diagnostic", "planned": "Prepared study",
          "support": "Infrastructure"}
STATUSES = {"completed": "Completed", "closed-with-gaps": "Closed · gaps retained",
            "offline-complete": "Offline complete", "prepared": "Prepared · not a result",
            "checkpoint": "Saved checkpoint"}


def path_links(value: str) -> str:
    links = []
    for source in filter(None, value.split(";")):
        path = ROOT / source
        if not path.exists() or not path.resolve().is_relative_to(ROOT):
            raise ValueError(f"Missing or unsafe evidence path: {source}")
        label = source.replace("experiments/dependency_memory/", "…/")
        links.append(f'<li><a href="../{quote(source, safe="/#")}">{escape(label)}</a></li>')
    return "<ul>" + "".join(links) + "</ul>"


def study_html(row: dict[str, str]) -> str:
    title, sid = escape(row["title"]), escape(row["study_id"])
    evidence = []
    for field, label in [("entry_points", "Findings & reading"), ("protocol_paths", "Frozen protocol"),
                         ("result_paths", "Saved evidence"), ("code_paths", "Implementation")]:
        if row[field]:
            evidence.append(f'<div><h4>{label}</h4>{path_links(row[field])}</div>')
    claims = ""
    if row["claim_ids"]:
        claims = '<p class="claim-ref">Claim register: <a href="../paper/claims.csv">' + escape(row["claim_ids"].replace(";", ", ")) + '</a></p>'
    badge = "plan" if row["status"] == "prepared" else "gap" if row["status"] == "closed-with-gaps" else ""
    return f'''<article class="study" id="study-{sid}" data-category="{row['category']}" data-status="{row['status']}" data-date="{row['as_of']}">
      <div class="study-meta"><span class="type-label {row['category']}">{LABELS[row['category']]}</span><time datetime="{row['as_of']}">{row['as_of']}</time><span class="status-badge {badge}">{STATUSES[row['status']]}</span></div>
      <h3>{title}</h3><p>{escape(row['summary'])}</p>
      <details><summary>Limits & source evidence <span aria-hidden="true">↗</span></summary><div class="study-detail"><div class="limits"><strong>How to interpret this</strong><p>{escape(row['limitations'])}</p></div>{claims}<div class="evidence-grid">{''.join(evidence)}</div></div></details>
    </article>'''


class LinkAudit(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.ids: set[str] = set()
        self.links: list[str] = []
        self.errors: list[str] = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if "id" in attrs:
            if attrs["id"] in self.ids:
                self.errors.append(f"Duplicate HTML id: {attrs['id']}")
            self.ids.add(attrs["id"])
        if tag == "a" and "href" in attrs:
            self.links.append(attrs["href"])
        if tag in {"img", "script", "link"} and ("src" in attrs or "href" in attrs):
            self.errors.append("The overview must remain self-contained (no external assets)")

    def validate(self):
        for link in self.links:
            parts = urlsplit(link)
            if parts.scheme:
                continue
            if not parts.path:
                if parts.fragment and parts.fragment not in self.ids:
                    self.errors.append(f"Missing anchor: {link}")
            else:
                target = (OUTPUT.parent / unquote(parts.path)).resolve()
                if not target.is_relative_to(ROOT) or not target.exists():
                    self.errors.append(f"Missing or unsafe local link: {link}")
        if self.errors:
            raise ValueError("\n".join(self.errors))


def build() -> str:
    with REGISTRY.open(encoding="utf-8-sig", newline="") as file:
        rows = list(csv.DictReader(file))
    if len({r["study_id"] for r in rows}) != len(rows):
        raise ValueError("Duplicate study IDs in registry")
    counts = Counter(r["category"] for r in rows)
    rows.sort(key=lambda r: (r["as_of"], r["study_id"]), reverse=True)
    template = TEMPLATE.read_text(encoding="utf-8")
    snapshot = re.search(r'<meta name="research-snapshot" content="([0-9-]+)">', template)
    if not snapshot or any(row["as_of"] > snapshot.group(1) for row in rows):
        raise ValueError("Review the dated overview narrative and advance its snapshot before including newer evidence")
    replacements = {"{{STUDIES}}": "\n".join(map(study_html, rows)),
                    "{{TOTAL}}": str(len(rows)),
                    "{{PREPARED}}": str(sum(r["status"] == "prepared" for r in rows)),
                    "{{REGISTRY_HASH}}": hashlib.sha256(REGISTRY.read_bytes()).hexdigest()[:12],
                    **{f"{{{{COUNT_{k.upper()}}}}}": str(v) for k, v in counts.items()}}
    for token, value in replacements.items():
        template = template.replace(token, value)
    if "{{" in template:
        raise ValueError("Unresolved template placeholder")
    audit = LinkAudit()
    audit.feed(template)
    audit.validate()
    return template


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Check generated HTML and evidence links without writing")
    args = parser.parse_args()
    content = build()
    if args.check:
        if not OUTPUT.exists() or OUTPUT.read_text(encoding="utf-8") != content:
            print("Stale overview. Run python scripts/build_research_overview.py")
            return 1
        print("PASS: overview matches registry/template; all local evidence links exist; no external assets")
    else:
        OUTPUT.write_text(content, encoding="utf-8", newline="\n")
        print(f"Built {OUTPUT.relative_to(ROOT)} ({len(content.encode('utf-8')):,} bytes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
