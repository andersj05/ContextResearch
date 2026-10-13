"""Immutable preparation bundles and source bindings; no provider calls."""
from dataclasses import asdict
from pathlib import Path
import zipfile

from .common import ROOT, PACKAGE, STUDY, SEED, MODEL, EFFORT, IMAGE, HORIZONS, MAX_WORKERS, DEFAULT_WORKERS, read, save_new, sha, now
from .tasks import generate
from .schedule import jobs, identities, generation_bound, TRACKS
from .calibration import cases


def bindings():
    roots = [PACKAGE, PACKAGE.parent / "rollback_pilot", PACKAGE.parent / "rollback_math_followup_v4", PACKAGE.parent / "rollback_recovery_v3"]
    paths = {p for root in roots for p in root.rglob("*.py")}
    paths |= {p for p in PACKAGE.glob("*.md")}
    paths.add(PACKAGE.parent / "rollback_pilot" / "PROMPTS.md")
    return [{"path": p.relative_to(ROOT).as_posix(), "sha256": sha(p.read_bytes())} for p in sorted(paths)]


def prepare(folder, tracks=TRACKS):
    folder = Path(folder).resolve()
    if not folder.is_relative_to(ROOT) or folder.exists():
        raise ValueError("new workspace bundle directory required")
    if not tracks or len(set(tracks)) != len(tracks) or any(t not in TRACKS for t in tracks):
        raise ValueError("distinct known tracks required")
    tasks = generate(); schedule = identities(tasks, tracks)
    calibration = cases()
    sources = bindings()
    folder.mkdir(parents=True)
    lines = ["# Frozen development task catalog", "", "48 constructed tasks; no Luna outcomes. Difficulty labels are uncalibrated generator settings.", "",
             "| Task | Domain | Difficulty | Action cap | Stages | Public requirements | Reserved cases |", "|---|---|---|---:|---:|---:|---:|"]
    for t in sorted(tasks, key=lambda t: t["task_id"]):
        lines.append(f"| {t['task_id']} | {t['domain']} | {t['difficulty']} | {t['action_allowance']} | {len(t['stages'])} | {sum(len(p['requirements']) for p in t['stages'])} | {len(t['evaluator']['reserved_tests'])} |")
    catalog = ("\n".join(lines) + "\n").encode("utf-8")
    (folder / "TASK_CATALOG.md").write_bytes(catalog)
    with zipfile.ZipFile(folder / "source_snapshot.zip", "x", compression=zipfile.ZIP_DEFLATED) as archive:
        for row in sources:
            info = zipfile.ZipInfo(row["path"], date_time=(2026, 10, 8, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            archive.writestr(info, (ROOT / row["path"]).read_bytes())
    manifest = {"study": STUDY, "prepared_utc": now(), "evidence_kind": "unperformed_development_allocation",
                "model": MODEL, "effort_every_stage": EFFORT, "immutable_model_revision": None, "provider_sampling_seed": None,
                "seed": SEED, "tracks": list(tracks), "tasks": [{"task_id": t["task_id"], "sha256": t["sha256"]} for t in tasks],
                "task_file_sha256": sha(tasks), "source_bindings": sources, "jobs": jobs(tasks, tracks),
                "source_snapshot_sha256": sha((folder / "source_snapshot.zip").read_bytes()),
                "task_catalog_sha256": sha(catalog),
                "schedule": [asdict(i) for i in schedule], "possible_task_call_identities": len(schedule),
                "calibration": [{"identity": asdict(c["identity"]), "request": c["request"].data(), "request_sha256": sha(c["request"].json_text)} for c in calibration],
                "possible_total_call_identities": len(schedule) + len(calibration),
                "state_machine_generation_ceiling_including_calibration": generation_bound(tasks, tracks) + len(calibration),
                "runtime_image": IMAGE, "default_workers": DEFAULT_WORKERS, "maximum_workers": MAX_WORKERS,
                "horizons": HORIZONS, "subscription_only": True, "purchase_or_api_fallback": False,
                "planning_credit_ceiling": None, "budget_kind": "fixed task/action/call allocation; account allowance enforced before each call",
                "launch_requires": ["source/task integrity", "independent reference checks", "installed-client preflight", "excluded live calibration", "explicit launch command"],
                "real_model_calls_at_preparation": 0}
    save_new(folder / "tasks.json", tasks)
    save_new(folder / "manifest.json", manifest)
    save_new(folder / "bundle.json", {"manifest_sha256": sha(manifest), "tasks_sha256": sha(tasks), "model_calls": 0})
    return manifest


def check_bundle(folder):
    folder = Path(folder)
    manifest, tasks, bundle = (read(folder / n) for n in ("manifest.json", "tasks.json", "bundle.json"))
    if sha(manifest) != bundle["manifest_sha256"] or sha(tasks) != bundle["tasks_sha256"] or sha(tasks) != manifest["task_file_sha256"]:
        raise ValueError("bundle bytes changed")
    if [{"task_id": t["task_id"], "sha256": sha({k: v for k, v in t.items() if k != "sha256"})} for t in tasks] != manifest["tasks"]:
        raise ValueError("task binding changed")
    for row in manifest["source_bindings"]:
        if sha((ROOT / row["path"]).read_bytes()) != row["sha256"]:
            raise ValueError("frozen source changed: " + row["path"])
    if manifest["schedule"] != [asdict(i) for i in identities(tasks, manifest["tracks"])]:
        raise ValueError("schedule changed")
    if manifest["jobs"] != jobs(tasks, manifest["tracks"]):
        raise ValueError("job graph changed")
    if manifest["state_machine_generation_ceiling_including_calibration"] != generation_bound(tasks, manifest["tracks"]) + len(cases()):
        raise ValueError("generation bound changed")
    if sha((folder / "source_snapshot.zip").read_bytes()) != manifest["source_snapshot_sha256"]:
        raise ValueError("immutable source snapshot changed")
    if sha((folder / "TASK_CATALOG.md").read_bytes()) != manifest["task_catalog_sha256"]:
        raise ValueError("task catalog changed")
    with zipfile.ZipFile(folder / "source_snapshot.zip") as archive:
        if set(archive.namelist()) != {r["path"] for r in manifest["source_bindings"]}:
            raise ValueError("source snapshot inventory changed")
        if any(sha(archive.read(r["path"])) != r["sha256"] for r in manifest["source_bindings"]):
            raise ValueError("source snapshot bytes changed")
    if manifest["calibration"] != [{"identity": asdict(c["identity"]), "request": c["request"].data(), "request_sha256": sha(c["request"].json_text)} for c in cases()]:
        raise ValueError("calibration changed")
    return manifest, tasks
