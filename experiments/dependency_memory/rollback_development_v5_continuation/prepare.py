"""Freeze an amendment against the original allocation and sealed prior receipts."""
from copy import deepcopy
from pathlib import Path
import zipfile

from ..rollback_development_v5.common import ROOT, read, save_new, sha, now
from ..rollback_development_v5.prepare import check_bundle
from ..rollback_development_v5.audit import ledger_rows

PACKAGE = Path(__file__).resolve().parent


def amendment_bindings():
    return [{"path": p.relative_to(ROOT).as_posix(), "sha256": sha(p.read_bytes())}
            for p in sorted(PACKAGE.iterdir()) if p.suffix in {".py", ".md"}]


def sealed_prior(folder, base):
    folder = Path(folder).resolve()
    if not folder.is_relative_to(ROOT):
        raise ValueError("workspace evidence required")
    inventory = read(folder / "evidence_manifest.json")
    actual = {p.relative_to(folder).as_posix() for p in folder.rglob("*.json")
              if p != folder / "evidence_manifest.json"}
    if len(inventory["files"]) != len(actual) or {r["path"] for r in inventory["files"]} != actual:
        raise ValueError("prior sealed inventory is incomplete")
    for row in inventory["files"]:
        path = (folder / row["path"]).resolve()
        if not path.is_relative_to(folder) or sha(path.read_bytes()) != row["sha256"]:
            raise ValueError("prior sealed evidence changed")
    if sha((folder / "ledger.sqlite").read_bytes()) != inventory["ledger_sha256"]:
        raise ValueError("prior ledger changed")
    manifest = read(folder / "manifest.json")
    inherited_base = manifest.get("continuation", {}).get("base_manifest_sha256", sha(manifest))
    if inherited_base != sha(base):
        raise ValueError("prior phase uses a different allocation")
    calls, events, stop = ledger_rows(folder / "ledger.sqlite")
    if any(c["state"] not in {"completed", "unknown"} for c in calls):
        raise ValueError("prior admissions have not drained")
    settings = read(folder / "run_settings.json")
    calibration = read(folder / "calibration.json")
    if settings["live"]:
        expected = {sha(c["identity"]) for c in base["calibration"]}
        rows = calibration["rows"]
        if len(rows) != len(expected) or {r["call_id"] for r in rows} != expected or any(r["disposition"] != "passed" for r in rows):
            raise ValueError("all eight excluded calibration calls must already have passed")
    execution = read(folder / "execution.json")
    if [r["job"] for r in execution["jobs"]] != base["jobs"]:
        raise ValueError("prior job denominator changed")
    return {"inventory_sha256": sha(inventory), "ledger_sha256": inventory["ledger_sha256"],
            "execution_sha256": sha(execution), "calibration_sha256": sha(calibration),
            "admissions": len(calls), "completed": sum(c["state"] == "completed" for c in calls),
            "unknown": sum(c["state"] == "unknown" for c in calls), "live": settings["live"],
            "previous_stop": stop}, calls, events


def prepare(bundle, prior, output):
    base, tasks = check_bundle(bundle)
    inherited, _, _ = sealed_prior(prior, base)
    output = Path(output).resolve()
    if not output.is_relative_to(ROOT) or output.exists():
        raise ValueError("new workspace preparation directory required")
    output.mkdir(parents=True)
    manifest = deepcopy(base)
    manifest["source_bindings"] += amendment_bindings()
    manifest["continuation"] = {
        "amendment": "trajectory-local unknown responses, immutable cumulative receipts",
        "prepared_utc": now(), "base_manifest_sha256": sha(base),
        "original_bundle": Path(bundle).resolve().relative_to(ROOT).as_posix(),
        "prior_phase": Path(prior).resolve().relative_to(ROOT).as_posix(), "prior": inherited,
        "generation_ceiling": base["state_machine_generation_ceiling_including_calibration"],
        "calibration_policy": "reuse eight passed identities; no repeat generations",
        "user_authorization": "explicit full live study approval and explicit amendment/continuation request",
        "timing_amended_after_observation": True, "experimental_payloads_unchanged": True,
        "original_results_modified": False,
    }
    with zipfile.ZipFile(output / "source_snapshot.zip", "x", compression=zipfile.ZIP_DEFLATED) as archive:
        for row in manifest["source_bindings"]:
            archive.writestr(row["path"], (ROOT / row["path"]).read_bytes())
    manifest["continuation"]["source_snapshot_sha256"] = sha((output / "source_snapshot.zip").read_bytes())
    save_new(output / "manifest.json", manifest)
    save_new(output / "bundle.json", {"manifest_sha256": sha(manifest), "model_calls": 0})
    return manifest


def check_prepared(folder):
    folder = Path(folder)
    manifest = read(folder / "manifest.json")
    if sha(manifest) != read(folder / "bundle.json")["manifest_sha256"]:
        raise ValueError("amendment manifest changed")
    amendment = manifest["continuation"]
    base, tasks = check_bundle(ROOT / amendment["original_bundle"])
    if sha(base) != amendment["base_manifest_sha256"]:
        raise ValueError("original allocation changed")
    if manifest["source_bindings"] != base["source_bindings"] + amendment_bindings():
        raise ValueError("amendment source changed")
    candidate = deepcopy(base)
    candidate["source_bindings"] = manifest["source_bindings"]
    candidate["continuation"] = amendment
    if candidate != manifest:
        raise ValueError("original task/protocol fields changed")
    inherited, calls, events = sealed_prior(ROOT / amendment["prior_phase"], base)
    if inherited != amendment["prior"]:
        raise ValueError("prior phase changed since freezing")
    path = folder / "source_snapshot.zip"
    if sha(path.read_bytes()) != amendment["source_snapshot_sha256"]:
        raise ValueError("amendment snapshot changed")
    with zipfile.ZipFile(path) as archive:
        if set(archive.namelist()) != {r["path"] for r in manifest["source_bindings"]}:
            raise ValueError("amendment snapshot inventory changed")
        if any(sha(archive.read(r["path"])) != r["sha256"] for r in manifest["source_bindings"]):
            raise ValueError("amendment snapshot bytes changed")
    return manifest, tasks, calls, events
