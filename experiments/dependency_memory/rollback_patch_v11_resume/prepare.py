"""Freeze an unsent-work amendment without changing the scientific allocation."""
from copy import deepcopy
from contextlib import closing
from pathlib import Path
import shutil
import sqlite3
import zipfile

from .common import ROOT, PACKAGE, AMENDMENT, sha, read, save_new, now
from ..rollback_patch_v11.prepare import check_bundle as check_original, identities
from ..rollback_checkpoint_v7.audit import _inventory
from ..rollback_development_v5.audit import ledger_rows


def workspace_path(value):
    path = Path(value)
    path = path.resolve() if path.is_absolute() else (ROOT / path).resolve()
    if not path.is_relative_to(ROOT):
        raise ValueError("workspace_path_required")
    return path


def relative(value):
    return workspace_path(value).relative_to(ROOT).as_posix()


def prior_binding(original_bundle, prior_output, prior_audit):
    original_bundle, prior_output, prior_audit = map(
        workspace_path, (original_bundle, prior_output, prior_audit))
    original, tasks = check_original(original_bundle)
    if read(prior_output / "manifest.json") != original:
        raise ValueError("prior_is_not_original_sealed_phase")
    _inventory(prior_output)
    audit = read(prior_audit)
    evidence_sha = sha(read(prior_output / "evidence_manifest.json"))
    calls, _, stop = ledger_rows(prior_output / "ledger.sqlite")
    if not stop or any(call["state"] not in {"completed", "unknown"} for call in calls):
        raise ValueError("sealed_drained_global_stop_required")
    if (audit.get("passed") is not True or audit.get("model_calls") != 0
            or audit.get("manifest_sha256") != sha(original)
            or audit.get("evidence_manifest_sha256") != evidence_sha
            or audit.get("all_admissions_reconstructed") != len(calls)):
        raise ValueError("prior_independent_replay_required")
    if len(calls) >= original["generation_ceiling"]:
        raise ValueError("no_original_call_capacity_remaining")
    with closing(sqlite3.connect((prior_output / "ledger.sqlite").as_uri() + "?mode=ro", uri=True)) as db:
        if db.execute("SELECT 1 FROM inherited_stops").fetchone():
            raise ValueError("this_amendment_binds_original_phase_only")
    execution = read(prior_output / "execution.json")
    if execution["stopped"] is not True:
        raise ValueError("prior_execution_stop_mismatch")
    settings = read(prior_output / "run_settings.json")
    if settings["workers"] != original["workers"] or settings["retries"] != 0:
        raise ValueError("prior_run_contract_changed")
    if settings["live"] and (len(tasks) != 256 or original["generation_ceiling"] != 3584):
        raise ValueError("original_live_cohort_required")
    if settings["live"]:
        fatal = [call for call in calls if call.get("failure_scope") == "global"]
        if (len(calls) != 289 or sum(call["state"] == "completed" for call in calls) != 284
                or len(fatal) != 1 or stop != "systemic_transport_failure"):
            raise ValueError("original_diagnosed_interruption_required")
        diagnostic = fatal[0].get("diagnostic", {})
        if any(diagnostic.get(key) != value for key, value in {
                "phase": "quota", "reason_code": "rpc_error",
                "rpc_method": "account/rateLimits/read", "rpc_numeric_code": -32603}.items()):
            raise ValueError("original_quota_rpc_error_required")
    from .recovery import select_jobs
    selection = select_jobs(original, execution, calls)
    recovery = {
        "amendment": AMENDMENT,
        "original_bundle": relative(original_bundle),
        "prior_output": relative(prior_output),
        "prior_audit": relative(prior_audit),
        "prior_manifest_sha256": sha(original),
        "prior_evidence_manifest_sha256": evidence_sha,
        "prior_ledger_sha256": sha((prior_output / "ledger.sqlite").read_bytes()),
        "prior_audit_sha256": sha(audit),
        "prior_admissions": len(calls),
        "prior_completed": sum(call["state"] == "completed" for call in calls),
        "prior_unknown": sum(call["state"] == "unknown" for call in calls),
        "prior_live": settings["live"],
        "inherited_stop": stop,
        "inherited_stops": [stop],
        "isolated_content_interpretation_gate_permanently_failed": True,
        "selection": "terminal and unknown-containing jobs retained; only healthy globally interrupted jobs resumed; dependent children recomputed when prefix resumes",
        "automatic_retries": 0,
        "selection_sha256": sha(selection),
    }
    return original, tasks, recovery


def bindings(original):
    result = {row["path"]: row["sha256"] for row in original["source_bindings"]}
    for pattern in ("*.py", "*.md"):
        for path in PACKAGE.glob(pattern):
            result[path.relative_to(ROOT).as_posix()] = sha(path.read_bytes())
    return [{"path": key, "sha256": value} for key, value in sorted(result.items())]


def prepare(folder, *, original_bundle, prior_output, prior_audit):
    folder = workspace_path(folder)
    if folder.exists():
        raise ValueError("new_workspace_bundle_required")
    original, tasks, recovery = prior_binding(original_bundle, prior_output, prior_audit)
    manifest = deepcopy(original)
    manifest.update(recovery=recovery, prepared_utc=now(), source_bindings=bindings(original))
    folder.mkdir(parents=True)
    for name in ("tasks.json", "verification.json"):
        shutil.copyfile(workspace_path(original_bundle) / name, folder / name)
    with zipfile.ZipFile(folder / "source_snapshot.zip", "x", zipfile.ZIP_DEFLATED) as archive:
        for row in manifest["source_bindings"]:
            archive.write(ROOT / row["path"], row["path"])
    manifest["snapshot_sha256"] = sha((folder / "source_snapshot.zip").read_bytes())
    save_new(folder / "manifest.json", manifest)
    save_new(folder / "bundle.json", {"manifest_sha256": sha(manifest), "model_calls": 0})
    check_bundle(folder)
    return manifest


def check_bundle(folder, *, check_sources=True):
    folder = workspace_path(folder)
    manifest, tasks = read(folder / "manifest.json"), read(folder / "tasks.json")
    if sha(manifest) != read(folder / "bundle.json")["manifest_sha256"]:
        raise ValueError("recovery_manifest_changed")
    recovery = manifest["recovery"]
    original, original_tasks, expected = prior_binding(
        recovery["original_bundle"], recovery["prior_output"], recovery["prior_audit"])
    if recovery != expected or tasks != original_tasks:
        raise ValueError("recovery_evidence_binding_changed")
    unchanged = deepcopy(manifest)
    unchanged.pop("recovery")
    for key in ("prepared_utc", "source_bindings", "snapshot_sha256"):
        unchanged[key] = original[key]
    if unchanged != original:
        raise ValueError("scientific_contract_changed")
    if manifest["source_bindings"] != bindings(original):
        raise ValueError("amendment_source_changed")
    if sha(tasks) != original["tasks_sha256"]:
        raise ValueError("tasks_changed")
    if sha(read(folder / "verification.json")) != original["verification_sha256"]:
        raise ValueError("verification_changed")
    if sha((folder / "source_snapshot.zip").read_bytes()) != manifest["snapshot_sha256"]:
        raise ValueError("source_snapshot_changed")
    with zipfile.ZipFile(folder / "source_snapshot.zip") as archive:
        if set(archive.namelist()) != {row["path"] for row in manifest["source_bindings"]}:
            raise ValueError("source_snapshot_inventory_changed")
        for row in manifest["source_bindings"]:
            if sha(archive.read(row["path"])) != row["sha256"]:
                raise ValueError("snapshot_source_changed")
            if check_sources and sha((ROOT / row["path"]).read_bytes()) != row["sha256"]:
                raise ValueError("source_drift:" + row["path"])
    return manifest, tasks
