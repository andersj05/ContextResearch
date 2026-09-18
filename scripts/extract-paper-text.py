"""Validate the paper archive and extract page-addressable text for review.

The extracted text is a disposable working cache under ``tmp/``. The committed
QA table is intentionally small and reproducible from the archived PDFs.
"""

from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path

from pypdf import PdfReader


QA_FIELDS = [
    "source_id",
    "category",
    "pdf_path",
    "pages",
    "text_characters",
    "pages_without_text",
    "metadata_title",
    "metadata_author",
    "parse_status",
    "parse_error",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", default="catalog/paper-downloads.csv")
    parser.add_argument("--pdf-dir", default="papers/academic")
    parser.add_argument("--text-dir", default="tmp/paper-text")
    parser.add_argument("--qa-output", default="catalog/pdf-qa.csv")
    return parser.parse_args()


def clean_metadata(value: object) -> str:
    if value is None:
        return ""
    return " ".join(str(value).replace("\x00", "").split())


def main() -> int:
    args = parse_args()
    root = Path(__file__).resolve().parents[1]
    manifest_path = root / args.manifest
    pdf_dir = root / args.pdf_dir
    text_dir = root / args.text_dir
    qa_output = root / args.qa_output
    text_dir.mkdir(parents=True, exist_ok=True)

    with manifest_path.open("r", encoding="utf-8-sig", newline="") as handle:
        manifest = list(csv.DictReader(handle))

    qa_rows: list[dict[str, str | int]] = []
    failures = 0
    for index, row in enumerate(manifest, start=1):
        source_id = row["source_id"]
        pdf_path = pdf_dir / f"{source_id}.pdf"
        text_path = text_dir / f"{source_id}.txt"
        print(f"[{index}/{len(manifest)}] {source_id}")

        qa: dict[str, str | int] = {
            "source_id": source_id,
            "category": row["category"],
            "pdf_path": pdf_path.relative_to(root).as_posix(),
            "pages": 0,
            "text_characters": 0,
            "pages_without_text": 0,
            "metadata_title": "",
            "metadata_author": "",
            "parse_status": "failed",
            "parse_error": "",
        }

        try:
            if not pdf_path.exists():
                raise FileNotFoundError(f"missing file: {pdf_path}")
            with pdf_path.open("rb") as handle:
                if handle.read(5) != b"%PDF-":
                    raise ValueError("invalid PDF signature")

            reader = PdfReader(str(pdf_path), strict=False)
            if reader.is_encrypted and not reader.decrypt(""):
                raise ValueError("encrypted PDF cannot be opened with an empty password")

            metadata = reader.metadata or {}
            qa["metadata_title"] = clean_metadata(getattr(metadata, "title", ""))
            qa["metadata_author"] = clean_metadata(getattr(metadata, "author", ""))
            qa["pages"] = len(reader.pages)

            extracted_pages: list[str] = []
            empty_pages = 0
            total_characters = 0
            for page_number, page in enumerate(reader.pages, start=1):
                text = page.extract_text() or ""
                normalized = text.replace("\r\n", "\n").replace("\r", "\n").strip()
                if not normalized:
                    empty_pages += 1
                total_characters += len(normalized)
                extracted_pages.append(
                    f"\n\n===== PDF PAGE {page_number} =====\n\n{normalized}\n"
                )

            text_path.write_text("".join(extracted_pages), encoding="utf-8")
            qa["text_characters"] = total_characters
            qa["pages_without_text"] = empty_pages
            qa["parse_status"] = "ok"
        except Exception as exc:  # noqa: BLE001 - record every corrupt-source failure
            failures += 1
            qa["parse_error"] = f"{type(exc).__name__}: {exc}"
            if text_path.exists():
                text_path.unlink()

        qa_rows.append(qa)

    qa_output.parent.mkdir(parents=True, exist_ok=True)
    with qa_output.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=QA_FIELDS)
        writer.writeheader()
        writer.writerows(qa_rows)

    print(
        f"Validated {len(qa_rows) - failures}/{len(qa_rows)} PDFs; "
        f"QA table: {qa_output.relative_to(root)}"
    )
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
