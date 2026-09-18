#!/usr/bin/env python3
"""Read-only, offline checks for the research workspace and committed evidence."""
from __future__ import annotations

import csv
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import sys
from urllib.parse import unquote

# Validation must not write bytecode into the repository.
sys.dont_write_bytecode = True
from build_paper import citation_keys, read_bibliography

ROOT = Path(__file__).resolve().parents[1]


def rows(path: str) -> list[dict[str, str]]:
    with (ROOT / path).open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def inside(path: Path) -> bool:
    return path.resolve().is_relative_to(ROOT)


def main() -> int:
    errors = []
    counts = {}
    bibliography = read_bibliography(ROOT / "paper/references.bib")
    counts["bibliography_entries"] = len(bibliography)
    required = ["README.md", "AGENTS.md", "docs/STATUS.md", "docs/EXPERIMENT_PROTOCOL.md",
                "paper/manuscript.md", "paper/outline.md", "paper/claims.csv",
                "provenance/import-manifest.csv", "provenance/SETUP_VALIDATION.md"]
    for name in required:
        if not (ROOT / name).is_file():
            errors.append(f"Missing required document: {name}")

    documents = [ROOT / "README.md", ROOT / "AGENTS.md", ROOT / "HARNESS_CORPUS_README.md"]
    for directory in ["docs", "paper", "research", "provenance", "catalog", "paper-notes", "source-notes", "synthesis", "papers", "experiments"]:
        documents.extend((ROOT / directory).rglob("*.md"))
    documents.extend((ROOT / "sources").glob("*.md"))
    documents.append(ROOT / "sources/harness-snapshots/2026-09-16/README.md")
    link_count = 0
    for path in documents:
        if not path.is_file():
            continue
        text = path.read_text(encoding="utf-8-sig")
        # Code examples can contain citation syntax or bracketed function calls;
        # those are not document links or citations.
        text = re.sub(r"(?ms)^```[^\n]*\n.*?^```[^\n]*(?:\n|$)", "", text)
        text = re.sub(r"`[^`\n]+`", "", text)
        # External source snapshots contain their own upstream-relative links and
        # are deliberately excluded from local-document link validation.
        for target in re.findall(r"(?<!!)\[[^\]]*\]\(([^)]+)\)", text):
            target = target.strip().strip("<>")
            if target.startswith(("http://", "https://", "mailto:", "#", "codex:")):
                continue
            clean = unquote(target.split("#", 1)[0])
            resolved = path.parent / clean
            link_count += 1
            if not inside(resolved) or not resolved.exists():
                errors.append(f"{path.relative_to(ROOT)}: invalid local link {target}")
        if path.is_relative_to(ROOT / "paper"):
            for key in citation_keys(text) - bibliography.keys():
                errors.append(f"{path.relative_to(ROOT)}: unknown citation {key}")
    counts["markdown_documents"] = len(documents)
    counts["local_links"] = link_count

    claims = rows("paper/claims.csv")
    if len({row["claim_id"] for row in claims}) != len(claims):
        errors.append("Duplicate paper claim IDs")
    for row in claims:
        for field in ["claim_id", "claim", "status", "evidence_paths", "limitation"]:
            if not row[field]:
                errors.append(f"{row['claim_id']}: empty {field}")
        for evidence in row["evidence_paths"].split(";"):
            path = ROOT / evidence
            if not inside(path) or not path.is_file():
                errors.append(f"{row['claim_id']}: missing evidence {evidence}")
        for key in filter(None, row["source_keys"].split(";")):
            if key not in bibliography:
                errors.append(f"{row['claim_id']}: unknown source {key}")
    counts["paper_claims"] = len(claims)

    inventory = rows("catalog/pdf-inventory.csv")
    for row in inventory:
        path = ROOT / row["pdf_path"]
        if not inside(path) or not path.is_file() or sha256(path) != row["sha256"].lower():
            errors.append(f"PDF missing or modified: {row['pdf_path']}")
    counts["pdf_hashes"] = len(inventory)

    manifest = rows("provenance/import-manifest.csv")
    immutable = [row for row in manifest if row["destination_path"].startswith(("sources/harness-snapshots/", "compaction_frontier_v1/"))]
    for row in immutable:
        path = ROOT / row["destination_path"]
        if not inside(path) or not path.is_file() or sha256(path) != row["destination_sha256"]:
            errors.append(f"Imported evidence missing or modified: {row['destination_path']}")
    counts["immutable_import_hashes"] = len(immutable)
    for row in json.loads((ROOT / "provenance/upstream-licenses.json").read_text(encoding="utf-8-sig")):
        path = ROOT / row["path"]
        if not inside(path) or not path.is_file() or sha256(path) != row["sha256"]:
            errors.append(f"Upstream license missing or modified: {row['path']}")

    spec = importlib.util.spec_from_file_location("compatibility", ROOT / "experiments/dependency_memory/compatibility.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    expected_certificate = json.loads(json.dumps(module.certificate()))
    actual_certificate = json.loads((ROOT / "experiments/dependency_memory/results/compatibility_certificate.json").read_text(encoding="utf-8"))
    if expected_certificate != actual_certificate:
        errors.append("Compatibility certificate is stale; regenerate it")
    sys.path.insert(0, str(ROOT / "experiments/dependency_memory"))
    import compatibility_scaling
    expected_scaling = compatibility_scaling.certificate()
    actual_scaling = json.loads((ROOT / "experiments/dependency_memory/results/compatibility_scaling_certificate.json").read_text(encoding="utf-8"))
    if expected_scaling != actual_scaling:
        errors.append("Compatibility scaling certificate is stale; regenerate it")
    counts["scaling_child_codebooks"] = sum(row["codebooks_checked"] for row in expected_scaling["child_codebook_checks"])
    counts["scaling_entropy_assignments"] = expected_scaling["block_entropy_check"]["optimal_branch_assignments_checked"]
    import audit_scaling
    expected_audit = json.loads(json.dumps(audit_scaling.certificate()))
    actual_audit = json.loads((ROOT / "experiments/dependency_memory/results/scaling_audit_certificate.json").read_text(encoding="utf-8"))
    if expected_audit != actual_audit:
        errors.append("Scaling audit certificate is stale; regenerate it")
    counts["audit_signed_assignments"] = expected_audit["signed_majority_assignments"]
    import run_artifact_workflow
    artifact_rows, artifact_summary, artifact_witness = run_artifact_workflow.diagnostics()
    expected_rows = [{key: str(value) for key, value in row.items()} for row in artifact_rows]
    if expected_rows != rows("experiments/dependency_memory/results/artifact_workflow.csv"):
        errors.append("Artifact workflow CSV is stale; regenerate it")
    for filename, expected in (("artifact_workflow_summary.json", artifact_summary),
                               ("artifact_workflow_witness.json", artifact_witness)):
        actual = json.loads((ROOT / "experiments/dependency_memory/results" / filename).read_text(encoding="utf-8"))
        if actual != json.loads(json.dumps(expected)):
            errors.append(f"{filename} is stale; regenerate it")
    actual_report = (ROOT / "experiments/dependency_memory/results/artifact_workflow_report.md").read_text(encoding="utf-8")
    if actual_report != run_artifact_workflow.report(artifact_summary):
        errors.append("Artifact workflow report is stale; regenerate it")
    counts["artifact_workflow_configurations"] = len(artifact_rows)
    workflow = rows("experiments/dependency_memory/results/workflow_retention.csv")
    summary = json.loads((ROOT / "experiments/dependency_memory/results/summary.json").read_text(encoding="utf-8"))
    if len(workflow) != summary["workflow_runs"]:
        errors.append("Workflow result count disagrees with summary")
    counts["compatibility_assignments"] = expected_certificate["branch_code_assignments_examined"]
    counts["workflow_configurations"] = len(workflow)

    print(json.dumps({"status": "FAIL" if errors else "PASS", "checks": counts, "errors": errors}, indent=2))
    return bool(errors)


if __name__ == "__main__":
    raise SystemExit(main())
