"""Build consistent per-paper Markdown notes from the reviewed evidence table."""

from __future__ import annotations

import csv
from pathlib import Path


RELEVANCE = {
    "foundations": "Supplies vocabulary and comparison axes for formalizing the harness as a composite decision system.",
    "harness-engineering": "Directly treats the harness, its optimization, or its runtime semantics as the object of study.",
    "tool-use": "Models the action interface through which a harness turns language outputs into state-changing operations.",
    "search-and-verification": "Supports analysis of inference-time search, feedback, stopping, and verifier error.",
    "mathematics-and-evaluation": "Provides estimators or asymptotic models needed to distinguish coverage, reliability, and deployable utility.",
    "memory-and-context": "Provides mechanisms and failure modes for state, retrieval, summarization, and bounded context.",
    "multi-agent": "Provides communication, aggregation, or coordination mechanisms and their compute-matched counterevidence.",
    "coding-and-evaluation": "Makes model–harness–environment coupling observable in executable, long-horizon tasks.",
    "safety": "Defines adversarial failure modes and control layers for tools, permissions, and execution boundaries.",
    "self-improving-harnesses": "Directly studies reusable harness components, outer-loop optimization, self-modification, or the statistical controls needed to decide whether an update is a real improvement.",
}


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def yaml_string(value: str) -> str:
    return '"' + value.replace("\\", "\\\\").replace('"', '\\"') + '"'


def author_array(value: str) -> str:
    authors = [part.strip() for part in value.replace(", and ", "; ").split(";") if part.strip()]
    return "[" + ", ".join(yaml_string(author) for author in authors) + "]"


def bullets(value: str) -> str:
    items = [item.strip() for item in value.split(" || ") if item.strip()]
    return "\n".join(f"- {item}" for item in items)


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    manifest = read_csv(root / "catalog/paper-downloads.csv")
    metadata = {row["source_id"]: row for row in read_csv(root / "catalog/paper-metadata.csv")}
    inventory = {row["source_id"]: row for row in read_csv(root / "catalog/pdf-inventory.csv")}
    qa = {row["source_id"]: row for row in read_csv(root / "catalog/pdf-qa.csv")}
    distillations = {
        row["source_id"]: row for row in read_csv(root / "catalog/paper-distillations.csv")
    }

    expected = {row["source_id"] for row in manifest}
    supplied = set(distillations)
    if expected != supplied:
        missing = sorted(expected - supplied)
        extra = sorted(supplied - expected)
        raise SystemExit(f"Distillation mismatch. Missing={missing}; extra={extra}")

    output_dir = root / "paper-notes"
    output_dir.mkdir(exist_ok=True)
    index_rows: list[str] = []
    for row in manifest:
        source_id = row["source_id"]
        meta = metadata[source_id]
        inv = inventory[source_id]
        quality = qa[source_id]
        dist = distillations[source_id]
        authors = meta["authors"] or quality["metadata_author"]
        source_type = (
            "preprint"
            if "preprint" in row["publication_status"].lower()
            or "openreview" in row["publication_status"].lower()
            else "peer-reviewed"
        )

        body = f"""---
title: {yaml_string(row['title'])}
authors: {author_array(authors)}
year: {row['year']}
venue: {yaml_string(row['publication_status'])}
source_type: {yaml_string(source_type)}
paper_url: {yaml_string(row['landing_url'])}
pdf_path: {yaml_string(inv['pdf_path'])}
accessed: {yaml_string(inv['accessed'])}
review_status: {yaml_string(dist['review_status'])}
evidence_confidence: {yaml_string(dist['evidence_confidence'])}
---

# {source_id} — {row['title']}

## Why this source is in the corpus

{RELEVANCE[row['category']]}

## Research question

{dist['research_question']}

## Harness mechanism studied

{dist['mechanism']}

## Method and experimental setup

{dist['method']}

## Main findings

{bullets(dist['main_findings'])}

## Mathematical content

{dist['mathematics']}

## Evidence quality and limitations

{dist['limitations']}

## Important implementation details

{dist['implementation_details']}

## Claims this source supports

{dist['supports']}

## Claims this source weakens or contradicts

{dist['weakens']}

## Relevance to a mathematics paper

{dist['math_relevance']}

## Connections to other sources

See the category and claim-level cross-references in [`INDEX.md`](INDEX.md) and the synthesis documents.

## Verification notes

{dist['verification']} The archived file parsed successfully: {quality['pages']} pages, {quality['text_characters']} extractable characters, SHA-256 `{inv['sha256']}`.
"""
        (output_dir / f"{source_id}.md").write_text(body, encoding="utf-8", newline="\n")
        index_rows.append(
            f"| [`{source_id}`]({source_id}.md) | {row['category']} | {row['year']} | "
            f"{row['publication_status']} | {dist['review_status']} | {dist['evidence_confidence']} |"
        )

    index = """# Paper-note index

Each archived PDF has one consistently structured note. `fully-reviewed` means the
paper's central result, method, and cited tables/equations were checked in the local PDF;
`skimmed` means an abstract/method/conclusion-level review suitable for corpus mapping,
not independent reproduction. Confidence concerns the bounded claim in the note, not the
paper or authors as a whole.

| Note | Category | Year | Status | Review | Confidence |
|---|---|---:|---|---|---|
""" + "\n".join(index_rows) + "\n"
    (output_dir / "INDEX.md").write_text(index, encoding="utf-8", newline="\n")
    print(f"Built {len(manifest)} paper notes and paper-notes/INDEX.md")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
