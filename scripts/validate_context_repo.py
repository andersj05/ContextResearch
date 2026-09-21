#!/usr/bin/env python3
"""Read-only, offline checks for the research workspace and committed evidence."""
from __future__ import annotations

import argparse
import csv
from decimal import Decimal, InvalidOperation
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import subprocess
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


def _canonical_hash(value) -> str:
    data = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(data).hexdigest()


def _strict_json(text):
    def unique(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise ValueError("duplicate JSON key")
            result[key] = value
        return result
    def invalid_constant(_):
        raise ValueError("nonfinite JSON constant")
    return json.loads(text, object_pairs_hook=unique, parse_constant=invalid_constant)


def validate_luna_runs(results: Path) -> tuple[dict, list[str]]:
    """Check saved live evidence internally, without rerunning any model.

    Historical source hashes identify the code used then. They are deliberately
    not compared with today's files. Request and summary content, accounting,
    and the combined first-tranche ceilings remain independently checkable.
    """
    errors = []
    counts = {"luna_development_runs": 0, "luna_development_request_rows": 0,
              "completed_pilot_model_requests": 0, "completed_pilot_model_responses": 0}
    total_committed = Decimal(0)
    statuses = ("completed", "policy_failure", "transport_failure", "reserved")

    for directory in sorted(results.glob("luna_development_*")):
        if not directory.is_dir():
            continue
        files = [directory / name for name in ("manifest.json", "requests.jsonl", "summary.json")]
        # A live run writes its manifest and reservation ledger incrementally.
        # Only a saved summary marks evidence ready for finished-run checks.
        if not files[2].is_file():
            continue
        counts["luna_development_runs"] += 1
        prefix = directory.name
        def require(condition, message):
            if not condition:
                raise ValueError(message)
        try:
            require(all(path.is_file() for path in files), "missing manifest, request ledger, or summary")
            manifest = _strict_json(files[0].read_text(encoding="utf-8"))
            ledger = [_strict_json(line) for line in files[1].read_text(encoding="utf-8").splitlines() if line.strip()]
            summary = _strict_json(files[2].read_text(encoding="utf-8"))
            counts["luna_development_request_rows"] += len(ledger)
            require(type(manifest) is dict and type(summary) is dict, "manifest and summary must be objects")
            require(summary.get("fake") is False, "Luna evidence must be explicitly live")
            require(summary.get("manifest_sha256") == _canonical_hash(manifest), "manifest hash mismatch")
            require(summary.get("request_audit_sha256") == _canonical_hash(ledger), "request-ledger hash mismatch")
            cap = manifest.get("request_cap")
            require(type(cap) is int and 0 <= cap <= 96, "invalid declared request cap")
            require(summary.get("request_cap") == cap and len(ledger) <= cap, "request cap mismatch or exceeded")
            require(summary.get("request_attempts") == len(ledger), "summary request count mismatch")
            require(manifest.get("split") == "development" and manifest.get("heldout_requests") == 0
                    and summary.get("heldout_requests") == 0, "held-out calls are outside this tranche")
            for episode in manifest.get("stage_b", []) + summary.get("stage_b", []):
                require(episode.get("split") == "development", "non-development episode in live evidence")
            expected_counts = {status: sum(row.get("status") == status for row in ledger) for status in statuses}
            require(sum(expected_counts.values()) == len(ledger), "unknown request status")
            require(summary.get("attempt_status_counts") == expected_counts, "summary status counts mismatch")
            transport = manifest.get("transport")
            require(type(transport) is dict, "missing frozen transport contract")
            require(summary.get("transport_manifest") == transport, "summary transport differs from frozen manifest")
            require(transport.get("model") == "gpt-5.6-luna", "unexpected model")
            # Validate hash format only: later implementation edits do not make
            # a frozen historical run stale.
            for name, value in transport.get("source_sha256", {}).items():
                require(isinstance(name, str) and isinstance(value, str)
                        and re.fullmatch(r"[0-9a-f]{64}", value) is not None, "invalid historical source hash")
            final_budget = summary.get("cost_accounting", {}).get("credit_budget")
            require(type(final_budget) is dict, "missing final credit-equivalent budget")
            require(summary.get("cost_accounting", {}).get("api_dollars") == 0, "unexpected API billing")
            latest_budget = transport.get("budget")
            require(type(latest_budget) is dict, "missing initial credit-equivalent budget")
            dispatches = settled = failed = 0
            settled_credits = uncertain_credits = Decimal(0)
            for number, row in enumerate(ledger, 1):
                require(type(row.get("attempt")) is int and row["attempt"] == number, "nonsequential attempt numbers")
                request = row.get("request_utf8")
                require(isinstance(request, str), "missing exact request bytes")
                raw = request.encode("utf-8")
                require(type(row.get("request_bytes")) is int and row["request_bytes"] == len(raw), "request byte-length mismatch")
                require(row.get("request_sha256") == hashlib.sha256(raw).hexdigest(), "request hash mismatch")
                require(isinstance(row.get("evaluator_id"), str)
                        and row["evaluator_id"].startswith(("calibration/", "development/")), "unexpected evaluator split")
                metadata = row.get("provider_metadata")
                require(type(metadata) is dict and type(metadata.get("dispatched")) is bool, "missing dispatch classification")
                if not metadata["dispatched"]:
                    require(row["status"] == "transport_failure", "nondispatched request cannot be a model result")
                    continue
                dispatches += 1
                require(metadata.get("model") == "gpt-5.6-luna", "request model mismatch")
                accounting = metadata.get("credit_accounting")
                require(type(accounting) is dict, "dispatched request lacks reservation accounting")
                require(accounting.get("ticket") == dispatches, "nonsequential generation tickets")
                latest_budget = accounting.get("budget")
                require(type(latest_budget) is dict, "missing per-attempt budget snapshot")
                if accounting.get("status") == "settled":
                    settled += 1
                    usage = accounting.get("usage")
                    require(type(usage) is dict, "settled request lacks token accounting")
                    fields = ("inputTokens", "cachedInputTokens", "cacheWriteInputTokens",
                              "outputTokens", "reasoningOutputTokens", "totalTokens")
                    require(all(type(usage.get(key)) is int and usage[key] >= 0 for key in fields),
                            "invalid settled token counts")
                    require(0 < usage["inputTokens"] < 272_000 and usage["outputTokens"] <= 128_000,
                            "settled tokens exceed the reviewed envelope")
                    require(usage["cachedInputTokens"] + usage["cacheWriteInputTokens"] <= usage["inputTokens"]
                            and usage["reasoningOutputTokens"] <= usage["outputTokens"]
                            and usage["totalTokens"] == usage["inputTokens"] + usage["outputTokens"],
                            "inconsistent settled token buckets")
                    expected_credit = (Decimal(usage["inputTokens"]) * Decimal("6.25")
                                       + Decimal(usage["outputTokens"]) * 30) / 1_000_000
                    require(Decimal(accounting["conservative_credit_equivalent_exact"]) == expected_credit,
                            "settled credit equivalent disagrees with token accounting")
                    require(Decimal(str(accounting["conservative_credit_equivalent"])) == expected_credit,
                            "numeric settled credit equivalent disagrees with exact value")
                    settled_credits += expected_credit
                    require(metadata.get("harness_termination") == "session_budget_exceeded", "missing controlled generation guard")
                elif accounting.get("status") == "reservation_retained":
                    failed += 1
                    uncertain_credits += Decimal(latest_budget["per_attempt_reservation_exact"])
                    require(row["status"] == "transport_failure", "uncertain reservation reported as a success")
                else:
                    raise ValueError("unknown reservation-accounting status")
            counts["completed_pilot_model_requests"] += dispatches
            counts["completed_pilot_model_responses"] += sum(
                row.get("status") in ("completed", "policy_failure") for row in ledger)
            require(type(summary.get("model_requests")) is int and summary["model_requests"] == dispatches,
                    "summary model-dispatch count mismatch")
            require(final_budget == latest_budget, "final budget differs from the latest request accounting")
            require(final_budget.get("generation_attempts") == dispatches
                    and final_budget.get("settled_attempts") == settled
                    and final_budget.get("failed_attempts") == failed, "budget attempt counters mismatch")
            attempt_ceiling = final_budget.get("generation_attempt_ceiling")
            require(type(attempt_ceiling) is int and dispatches <= attempt_ceiling <= 96,
                    "invalid budget generation ceiling")
            require(final_budget.get("pending_ticket") is None, "unfinished reservation in completed run")
            require(final_budget.get("api_dollar_spend_authorized") == 0
                    and final_budget.get("api_key_fallback") is False
                    and final_budget.get("credit_purchases") == 0
                    and final_budget.get("reset_redemptions") == 0, "unexpected billing or reset authorization")
            credit_cap = Decimal(final_budget["cap_credit_equivalent_exact"])
            committed = Decimal(final_budget["committed_credit_equivalent_exact"])
            require(credit_cap.is_finite() and 0 <= credit_cap <= 20, "invalid credit-equivalent ceiling")
            require(committed.is_finite() and 0 <= committed <= credit_cap, "credit-equivalent ceiling exceeded")
            require(Decimal(final_budget["settled_credit_equivalent_exact"]) == settled_credits
                    and Decimal(final_budget["uncertain_credit_reservations_exact"]) == uncertain_credits
                    and committed == settled_credits + uncertain_credits, "credit-equivalent totals mismatch")
            total_committed += committed
            if "request_metrics" in summary:
                expected_metrics = [{key: row[key] for key in (
                    "evaluator_id", "status", "latency_seconds", "provider_metadata")} for row in ledger]
                require(summary["request_metrics"] == expected_metrics, "summary request metrics differ from ledger")
        except (OSError, ValueError, TypeError, KeyError, AttributeError, InvalidOperation) as error:
            errors.append(f"{prefix}: {error}")
    if counts["completed_pilot_model_requests"] > 96:
        errors.append("Combined Luna development model dispatches exceed the 96-request tranche")
    if total_committed > 20:
        errors.append("Combined Luna development credit equivalents exceed the 20-credit tranche")
    counts["luna_credit_equivalent_committed"] = str(total_committed)
    return counts, errors


def validate_revision_runs(results: Path) -> tuple[dict, list[str]]:
    """Audit every separate revision run and enforce one combined allocation.

    A named run directory is evidence of an attempted run, even if interrupted;
    missing summaries or ledgers are errors rather than silently omitted usage.
    The initial 96-request/20-credit tranche is checked separately above.
    """
    from audit_revision_run import audit

    errors = []
    counts = {"revision_luna_runs": 0, "revision_luna_validated_runs": 0,
              "revision_luna_request_rows": 0, "completed_revision_model_requests": 0}
    committed = Decimal(0)
    for directory in sorted(results.glob("revision_luna_*")):
        if not directory.is_dir():
            continue
        counts["revision_luna_runs"] += 1
        try:
            evidence = audit(directory)
            if evidence.get("passed") is not True or evidence.get("fake") is not False:
                raise ValueError("revision run must be audited live evidence")
            dispatches = evidence["model_requests"]
            if type(dispatches) is not int or not 0 <= dispatches <= 24:
                raise ValueError("invalid audited model dispatch count")
            cost = (Decimal(evidence["settled_credit_equivalent"])
                    + Decimal(evidence["retained_credit_equivalent"]))
            if not cost.is_finite() or not 0 <= cost <= 12:
                raise ValueError("invalid audited committed credit equivalents")
            counts["revision_luna_validated_runs"] += 1
            counts["revision_luna_request_rows"] += evidence["requests_checked"]
            counts["completed_revision_model_requests"] += dispatches
            committed += cost
        except (OSError, ValueError, TypeError, KeyError, AttributeError, InvalidOperation) as error:
            errors.append(f"{directory.name}: {error}")
    if counts["completed_revision_model_requests"] > 24:
        errors.append("Combined revision Luna model dispatches exceed the separate 24-request allocation")
    if committed > 12:
        errors.append("Combined revision Luna credit equivalents exceed the separate 12-credit allocation")
    counts["revision_credit_equivalent_committed"] = str(committed)
    return counts, errors


def validate_transfer_runs(results: Path) -> tuple[dict, list[str]]:
    """Check the separate fixed allocation, including interrupted run evidence."""
    from audit_transfer_run import audit
    errors = []
    counts = {"transfer_luna_runs": 0, "transfer_luna_validated_runs": 0,
              "transfer_luna_request_rows": 0, "completed_transfer_model_requests": 0}
    committed = Decimal(0)
    for directory in sorted(results.glob("transfer_luna_*")):
        if not directory.is_dir():
            continue
        counts["transfer_luna_runs"] += 1
        try:
            manifest = _strict_json((directory / "manifest.json").read_text(encoding="utf-8"))
            if manifest.get("version") == "transfer_continuation_run_v1":
                from audit_transfer_continuation import audit as audit_continuation
                evidence = audit_continuation(directory)
            else:
                evidence = audit(directory)
            if evidence.get("passed") is not True or evidence.get("fake") is not False:
                raise ValueError("transfer run must be audited live evidence")
            dispatches = evidence["model_requests"]
            cost = Decimal(evidence["settled_credit_equivalent"]) + Decimal(evidence["retained_credit_equivalent"])
            if type(dispatches) is not int or not 0 <= dispatches <= 1536:
                raise ValueError("invalid transfer dispatch count")
            if not cost.is_finite() or not 0 <= cost <= 200:
                raise ValueError("invalid transfer committed credit equivalents")
            counts["transfer_luna_validated_runs"] += 1
            counts["transfer_luna_request_rows"] += evidence["requests_checked"]
            counts["completed_transfer_model_requests"] += dispatches
            committed += cost
        except (OSError, ValueError, TypeError, KeyError, AttributeError, InvalidOperation) as error:
            errors.append(f"{directory.name}: {error}")
    if counts["completed_transfer_model_requests"] > 1536 or committed > 200:
        errors.append("Combined transfer runs exceed the separate 1536-request/200-credit allocation")
    counts["transfer_credit_equivalent_committed"] = str(committed)
    return counts, errors


def validate_transfer_artifacts(results: Path) -> tuple[dict, list[str]]:
    import transfer_study
    import run_transfer_study
    errors, counts = [], {}
    try:
        plan = transfer_study.make_plan()
        run_transfer_study.validate_plan(plan)
        actual = _strict_json((results / "transfer_study_plan.json").read_text(encoding="utf-8"))
        if actual != plan or not plan["protocol_and_wire_audit_present"]:
            errors.append("Transfer plan is stale or missing frozen dependencies")
        controls = []
        for mode in ("optimal", "static_low", "first_visible", "invalid"):
            summary = run_transfer_study.execute([transfer_study.FakeClient(mode) for _ in range(4)])
            controls.append({"mode": mode, **{k: v for k, v in summary.items()
                            if k not in ("rows", "worker_summaries")}})
        expected = {"version": transfer_study.VERSION, "model_requests": 0,
                    "plan_sha256": _canonical_hash(plan), "controls": controls}
        if _strict_json((results / "transfer_study_audit.json").read_text(encoding="utf-8")) != expected:
            errors.append("Transfer fake controls are stale; regenerate the offline audit")
        counts["transfer_planned_cases"] = len(plan["cases"])
        counts["transfer_fake_requests"] = sum(c["request_attempts"] for c in controls)
        counts["transfer_offline_model_requests"] = sum(c["model_requests"] for c in controls)
    except (OSError, ValueError, TypeError, KeyError, AssertionError) as error:
        errors.append(f"Offline transfer validation failed: {error}")
    return counts, errors


def validate_revision_artifacts(results: Path) -> tuple[dict, list[str]]:
    """Regenerate the post-hoc analysis and diagnostic's separate offline controls.

    These counts stay separate from the immutable first Luna allocation: reused
    choices, exact route calculations, plans, and fake calls are not new model
    requests. This does not validate or authorize a future live allocation.
    """
    import revision_analysis
    import revision_diagnostic

    counts, errors = {}, []
    try:
        analysis = revision_analysis.analyze(results / "luna_development_2026-09-19")
        actual = _strict_json((results / "revision_analysis.json").read_text(encoding="utf-8"))
        if actual != json.loads(json.dumps(analysis)):
            errors.append("Post-hoc revision analysis is stale; regenerate it from the unchanged Luna run")
        actual_report = (results / "revision_analysis_report.md").read_text(encoding="utf-8")
        if actual_report != revision_analysis.report(analysis):
            errors.append("Post-hoc revision analysis report is stale; regenerate it")
        if analysis.get("new_model_requests") != 0:
            errors.append("Post-hoc revision analysis must not count model requests")
        counts["revision_posthoc_saved_parent_selections"] = analysis["counts"]["saved_parent_selections"]
        counts["revision_posthoc_population_selections"] = analysis["counts"]["full_population_parent_selections"]
        counts["revision_posthoc_manifest_conditioned_selections"] = analysis["counts"]["manifest_conditioned_parent_selections"]
        counts["revision_posthoc_strict_parent_deficits"] = analysis["counts"]["strict_parent_deficits"]
        counts["revision_posthoc_new_model_requests"] = analysis["new_model_requests"]
    except (OSError, ValueError, TypeError, KeyError, AttributeError) as error:
        errors.append(f"Post-hoc revision analysis validation failed: {error}")

    try:
        plan, fake_audit = revision_diagnostic.make_plan(), revision_diagnostic.fake_audit()
        for filename, expected in (("revision_diagnostic_plan.json", plan),
                                   ("revision_diagnostic_audit.json", fake_audit)):
            actual = _strict_json((results / filename).read_text(encoding="utf-8"))
            if actual != json.loads(json.dumps(expected)):
                errors.append(f"{filename} is stale; regenerate the offline revision diagnostic")
        if (plan.get("split") != "development" or plan.get("heldout_requests") != 0
                or plan.get("model_requests_completed_by_plan") != 0
                or plan.get("realized_routes_sampled") != 0 or fake_audit.get("model_requests") != 0):
            errors.append("Revision diagnostic plan/fake controls must remain unrun development evidence")
        if (plan.get("planned_cases") != len(plan["cases"])
                or len(plan["cases"]) > plan["maximum_model_requests"]):
            errors.append("Revision diagnostic plan case count exceeds its separate request ceiling")
        counts["revision_diagnostic_planned_request_ceiling"] = plan["maximum_model_requests"]
        counts["revision_diagnostic_planned_cases"] = plan["planned_cases"]
        counts["revision_diagnostic_fake_requests"] = fake_audit["fake_requests"]
        counts["revision_diagnostic_model_requests_in_offline_artifacts"] = (
            plan["model_requests_completed_by_plan"] + fake_audit["model_requests"])
    except (OSError, ValueError, TypeError, KeyError, AttributeError) as error:
        errors.append(f"Offline revision diagnostic validation failed: {error}")
    return counts, errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--exact-chain-compiler", help="Also rerun the full partition search with this C99 compiler")
    args = parser.parse_args()
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
    from joint_coding import coding as joint_block_coding
    expected_joint = joint_block_coding.certificate()
    joint_path = ROOT / "experiments/dependency_memory/results/joint_block_certificate.json"
    if json.loads(joint_path.read_text(encoding="utf-8")) != expected_joint:
        errors.append("Joint-block certificate is stale; regenerate it")
    joint_report = ROOT / "experiments/dependency_memory/results/joint_block_report.md"
    if joint_report.read_text(encoding="utf-8") != joint_block_coding.report(expected_joint):
        errors.append("Joint-block report is stale; regenerate it")
    counts["joint_block_witness_outcomes_checked"] = expected_joint["finite_witness"]["outcomes"]
    from joint_coding import decoder_frontier
    expected_frontier = decoder_frontier.certificate()
    frontier_path = ROOT / "experiments/dependency_memory/results/decoder_frontier_certificate.json"
    if json.loads(frontier_path.read_text(encoding="utf-8")) != expected_frontier:
        errors.append("Decoder frontier certificate is stale; regenerate it")
    frontier_report = ROOT / "experiments/dependency_memory/results/decoder_frontier_report.md"
    if frontier_report.read_text(encoding="utf-8") != decoder_frontier.report(expected_frontier):
        errors.append("Decoder frontier report is stale; regenerate it")
    counts["frontier_decoder_tables_checked"] = expected_frontier["decoder_tables_covered"]
    counts["frontier_decoder_orbits_checked"] = expected_frontier["decoder_orbits"]
    from collision_audit import run as collision_audit_run
    expected_collisions = collision_audit_run.certificate()
    collision_path = ROOT / "experiments/dependency_memory/results/collision_audit_certificate.json"
    if json.loads(collision_path.read_text(encoding="utf-8")) != expected_collisions:
        errors.append("Collision audit certificate is stale; regenerate it")
    collision_report = ROOT / "experiments/dependency_memory/results/collision_audit_report.md"
    if collision_report.read_text(encoding="utf-8") != collision_audit_run.report(expected_collisions):
        errors.append("Collision audit report is stale; regenerate it")
    collision_example = ROOT / "experiments/dependency_memory/collision_audit/example.json"
    if json.loads(collision_example.read_text(encoding="utf-8")) != expected_collisions["specifications"][0]:
        errors.append("Collision audit input example is stale; regenerate it")
    counts["collision_audit_constructed_specifications"] = len(expected_collisions["audits"])
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
    import run_recovery_frontier
    recovery_rows, recovery_grid, recovery_summary = run_recovery_frontier.diagnostics()
    for filename, expected in (("recovery_episodes.csv", recovery_rows), ("recovery_grid.csv", recovery_grid)):
        actual = rows("experiments/dependency_memory/results/" + filename)
        if actual != [{key: str(value) for key, value in row.items()} for row in expected]:
            errors.append(f"{filename} is stale; regenerate it")
    recovery_path = ROOT / "experiments/dependency_memory/results/recovery_frontier_summary.json"
    if json.loads(recovery_path.read_text(encoding="utf-8")) != json.loads(json.dumps(recovery_summary)):
        errors.append("Recovery frontier summary is stale; regenerate it")
    recovery_report = ROOT / "experiments/dependency_memory/results/recovery_frontier_report.md"
    if recovery_report.read_text(encoding="utf-8") != run_recovery_frontier.report(recovery_summary):
        errors.append("Recovery frontier report is stale; regenerate it")
    counts["recovery_executed_episodes"] = len(recovery_rows)
    counts["recovery_exact_configurations"] = len(recovery_grid)
    import pilot_plan
    expected_plan = pilot_plan.build_plan()
    plan_path = ROOT / "experiments/dependency_memory/results/pilot_plan.json"
    if json.loads(plan_path.read_text(encoding="utf-8")) != expected_plan:
        errors.append("Offline pilot plan is stale; regenerate it")
    plan_report = ROOT / "experiments/dependency_memory/results/pilot_calibration_report.md"
    if plan_report.read_text(encoding="utf-8") != pilot_plan.report(expected_plan):
        errors.append("Pilot calibration report is stale; regenerate it")
    counts["planned_pilot_request_ceiling"] = expected_plan["counts"]["total_maximum_model_requests"]
    import audit_heldout_renderers
    try:
        renderer_audit = audit_heldout_renderers.build_audit()
        renderer_path = ROOT / "experiments/dependency_memory/results/heldout_renderer_audit.json"
        if _strict_json(renderer_path.read_text(encoding="utf-8")) != renderer_audit:
            errors.append("Held-out renderer semantics checkpoint is stale; regenerate it")
        renderer_report = ROOT / "experiments/dependency_memory/results/heldout_renderer_report.md"
        if renderer_report.read_text(encoding="utf-8") != audit_heldout_renderers.report(renderer_audit):
            errors.append("Held-out renderer report is stale; regenerate it")
        if renderer_audit["model_requests"] != 0 or renderer_audit["provider_launch_ready"] is not False:
            errors.append("Held-out renderer checkpoint must remain offline-only evidence")
        counts["heldout_renderer_families"] = renderer_audit["counts"]["families"]
        counts["heldout_renderer_clue_entries"] = renderer_audit["counts"]["family_mode_clue_entries"]
        counts["heldout_renderer_unique_serialized_clues"] = renderer_audit["counts"]["unique_serialized_clues"]
        counts["heldout_renderer_semantic_route_checks"] = renderer_audit["counts"]["target_route_checks"]
    except (OSError, ValueError, TypeError, KeyError, AssertionError) as error:
        errors.append(f"Held-out renderer validation failed: {error}")
    luna_counts, luna_errors = validate_luna_runs(ROOT / "experiments/dependency_memory/results")
    counts.update(luna_counts)
    errors.extend(luna_errors)
    revision_run_counts, revision_run_errors = validate_revision_runs(ROOT / "experiments/dependency_memory/results")
    counts.update(revision_run_counts)
    errors.extend(revision_run_errors)
    transfer_run_counts, transfer_run_errors = validate_transfer_runs(ROOT / "experiments/dependency_memory/results")
    counts.update(transfer_run_counts)
    errors.extend(transfer_run_errors)
    counts["all_development_model_requests"] = (counts["completed_pilot_model_requests"]
                                                + counts["completed_revision_model_requests"]
                                                + counts["completed_transfer_model_requests"])
    import run_development_pilot
    fake_audit = run_development_pilot.offline_audit()
    fake_path = ROOT / "experiments/dependency_memory/results/development_pilot_audit.json"
    if json.loads(fake_path.read_text(encoding="utf-8")) != fake_audit:
        errors.append("Development fake-client audit is stale; regenerate it")
    counts["development_fake_requests"] = sum(r["fake_request_attempts"] for r in fake_audit["controls"])
    revision_counts, revision_errors = validate_revision_artifacts(ROOT / "experiments/dependency_memory/results")
    counts.update(revision_counts)
    errors.extend(revision_errors)
    transfer_counts, transfer_errors = validate_transfer_artifacts(ROOT / "experiments/dependency_memory/results")
    counts.update(transfer_counts)
    errors.extend(transfer_errors)
    import exact_chain
    chain_path = ROOT / "experiments/dependency_memory/results/exact_chain_certificate.json"
    chain = json.loads(chain_path.read_text(encoding="utf-8"))
    if chain.get("native_source_sha256") != hashlib.sha256(exact_chain.NATIVE_SOURCE.encode()).hexdigest():
        errors.append("Exact-chain native source changed; rerun the exhaustive search")
    raw_chain = {"partitions": chain["partitions"], "best_gain": chain["best_gain"],
                 "gain_histogram": {int(k): v for k, v in chain["gain_histogram"].items()},
                 "witness_masks": tuple(chain["witness"]["parent_masks"])}
    checked_chain = json.loads(json.dumps(exact_chain.certificate(raw_chain)))
    if any(chain.get(key) != value for key, value in checked_chain.items()):
        errors.append("Exact-chain certificate disagrees with count/objective/witness checks")
    # The normal offline check grades all witness outcomes and checks the search
    # digest/count. It does NOT rerun 171 million partitions or require a compiler.
    counts["exact_chain_partitions_recorded"] = chain["partitions"]
    counts["exact_chain_witness_outcomes_checked"] = checked_chain["outcomes"]
    counts["exact_chain_full_search_rerun"] = False
    if args.exact_chain_compiler:
        try:
            fresh_chain = json.loads(json.dumps(exact_chain.certificate(
                exact_chain.search_native(args.exact_chain_compiler))))
            # Search time and compiler metadata may vary. Scientific outputs,
            # the complete histogram, and the deterministic witness must match.
            compare_keys = set(checked_chain) | {"native_source_sha256"}
            if any(chain.get(key) != fresh_chain.get(key) for key in compare_keys):
                errors.append("Full exact-chain rerun disagrees with the committed certificate")
            counts["exact_chain_full_search_rerun"] = True
        except (ValueError, OSError, subprocess.CalledProcessError) as exc:
            errors.append(f"Could not complete exact-chain rerun: {exc}")
    import experiment
    frontier, disclosure, workflow, example_events, summary = experiment.diagnostics()
    for filename, expected in (("exact_frontier.csv", frontier), ("disclosure_timing.csv", disclosure),
                               ("workflow_retention.csv", workflow)):
        actual = rows("experiments/dependency_memory/results/" + filename)
        if actual != [{key: str(value) for key, value in row.items()} for row in expected]:
            errors.append(f"{filename} is stale; regenerate it")
    for filename, expected in (("example_events.json", example_events), ("summary.json", summary)):
        actual = json.loads((ROOT / "experiments/dependency_memory/results" / filename).read_text(encoding="utf-8"))
        if actual != expected:
            errors.append(f"{filename} is stale; regenerate it")
    counts["exact_frontier_rows_regenerated"] = len(frontier)
    counts["disclosure_rows_regenerated"] = len(disclosure)
    counts["compatibility_assignments"] = expected_certificate["branch_code_assignments_examined"]
    counts["workflow_configurations"] = len(workflow)

    print(json.dumps({"status": "FAIL" if errors else "PASS", "checks": counts, "errors": errors}, indent=2))
    return bool(errors)


if __name__ == "__main__":
    raise SystemExit(main())
