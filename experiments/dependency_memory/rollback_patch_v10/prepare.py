"""Freeze tasks, software, allocation and feasibility gates before model calls."""
from concurrent.futures import ThreadPoolExecutor
from dataclasses import asdict
from pathlib import Path
import zipfile
from .common import (ROOT, PACKAGE, STUDY, MODEL, EFFORT, SEED, ARMS, ATTEMPTS,
                     WORKERS, RUNTIME_WORKERS, MAX_BODY_BYTES, MAX_INPUT_TEXT_BYTES, IMAGE, sha, read, save_new, now)
from .tasks import generate, public_check, terminal_check, verify_tasks
from .engine import identity
from ..rollback_patch_v9.prepare import bindings as old_bindings


def selected_arms(split):
    return ("K0",) if split == "calibration" else ARMS


def identities(tasks, split):
    return [item for task in tasks for item in (
        identity(task, "prefix", 1), identity(task, "prefix", 1, "lesson"),
        *(identity(task, arm, step) for arm in selected_arms(split) for step in range(1, ATTEMPTS + 1)))]


def jobs(tasks, seed, split):
    result = []
    for task in sorted(tasks, key=lambda t: sha([seed, "task-order", t["task_id"]])):
        prefix_id = sha([STUDY, task["task_id"], "prefix"])
        result.append({"task_id": task["task_id"], "arm": "prefix", "job_id": prefix_id})
        for arm in sorted(selected_arms(split), key=lambda a: sha([seed, task["task_id"], a])):
            result.append({"task_id": task["task_id"], "arm": arm,
                           "job_id": sha([STUDY, task["task_id"], arm]), "depends_on": prefix_id})
    return result


def bindings():
    paths = {row["path"] for row in old_bindings()}
    paths.update(p.relative_to(ROOT).as_posix() for pattern in ("*.py", "*.md") for p in PACKAGE.glob(pattern))
    return [{"path": path, "sha256": sha((ROOT / path).read_bytes())} for path in sorted(paths)]


def verify(tasks, runtime):
    structure = verify_tasks(tasks)
    def check(task):
        candidate = {"files": task["evaluator"]["reference_files"]}
        public = public_check(task, candidate, runtime)
        private = terminal_check(task, candidate, runtime)
        if public["status"] != "public_pass" or private["score"] != 1:
            raise ValueError("reference_disagrees_with_independent_checker:" + task["task_id"])
        return {"task_id": task["task_id"], "public": public, "private": private}
    with ThreadPoolExecutor(max_workers=RUNTIME_WORKERS) as pool:
        rows = list(pool.map(check, tasks))
    return {"evidence_kind": "offline_reference_execution", "passed": True, "independent_oracles": structure,
            "tasks_checked": len(rows), "results": rows, "image": IMAGE}


def calibration_gate(folder):
    folder = Path(folder)
    manifest, execution = read(folder / "manifest.json"), read(folder / "execution.json")
    audit_path = folder.with_name(folder.name + "_replay_audit.json")
    audit = read(audit_path)
    evidence = read(folder / "evidence_manifest.json")
    if manifest["split"] != "calibration" or manifest["per_family"] != 4:
        raise ValueError("fixed_sixteen_task_calibration_required")
    prefixes = [row["result"] for row in execution["jobs"] if row["job"]["arm"] == "prefix"]
    controls = [row["result"] for row in execution["jobs"] if row["job"]["arm"] == "K0"]
    eligible = sum(row["eligible"] for row in prefixes)
    valid_lessons = sum(row["lesson_disposition"] == "valid" for row in prefixes if row["eligible"])
    repaired = sum(row.get("first_pass") is not None for row in controls)
    correct = sum(row.get("score") == 1 for row in controls)
    known_prefixes = sum(row["reason"] not in {"unknown_dispatch", "infrastructure_stop", "controller_error"} for row in prefixes)
    checks = {"all_sixteen_prefixes_known": known_prefixes == 16,
              "natural_failure_headroom": eligible >= 4,
              "one_correct_ordinary_repair": correct >= 1,
              "all_lessons_valid": valid_lessons == eligible,
              "no_global_stop": not execution["stopped"],
              "no_capacity_stop": not any(row["result"].get("reason") == "context_capacity" or row["result"].get("disposition") == "context_capacity" for row in execution["jobs"]),
              "live_calibration": read(folder / "run_settings.json")["live"] is True,
              "independent_replay_passed": audit["passed"] is True,
              "replay_bound_to_manifest": audit["manifest_sha256"] == sha(manifest),
              "replay_bound_to_evidence": audit["evidence_manifest_sha256"] == sha(evidence),
              "exact_job_inventory": [r["job"] for r in execution["jobs"]] == manifest["jobs"]}
    checks["sealed_evidence_intact"] = all(sha((folder / row["path"]).read_bytes()) == row["sha256"]
                                            for row in evidence["files"])
    return {"passed": all(checks.values()), "checks": checks, "eligible": eligible,
            "control_public_repaired": repaired, "control_correct": correct, "valid_lessons": valid_lessons,
            "calibration_result": folder.relative_to(ROOT).as_posix(),
            "calibration_execution_sha256": sha(execution),
            "calibration_audit_path": audit_path.relative_to(ROOT).as_posix(),
            "calibration_audit_sha256": sha(audit),
            "scope": "small control-only feasibility check, not a power guarantee or a treatment-effect selection"}


def prepare(folder, *, runtime, split="calibration", seed=SEED, per_family=4,
            workers=WORKERS, gate_folder=None):
    folder = Path(folder).resolve()
    if not folder.is_relative_to(ROOT) or folder.exists():
        raise ValueError("new_workspace_bundle_required")
    if split not in {"calibration", "study", "fixture"} or type(workers) is not int or not 1 <= workers <= WORKERS:
        raise ValueError("invalid_allocation")
    if split == "calibration" and per_family != 4:
        raise ValueError("calibration_frozen_at_sixteen_tasks")
    if split == "study" and per_family != 64:
        raise ValueError("study_frozen_at_256_tasks")
    if split == "study" and seed != SEED + 1:
        raise ValueError("study_seed_frozen")
    if split == "calibration" and seed != SEED:
        raise ValueError("calibration_seed_frozen")
    gate = calibration_gate(gate_folder) if split == "study" else None
    if gate is not None and not gate["passed"]:
        raise ValueError("calibration_gate_not_passed")
    tasks = generate(split=split, seed=seed, per_family=per_family)
    if gate is not None:
        old_manifest = read(Path(gate_folder) / "manifest.json")
        old_tasks = generate(split=old_manifest["split"], seed=old_manifest["seed"],
                             per_family=old_manifest["per_family"])
        def semantic_hash(task):
            return sha({key: task[key] for key in ("family", "contract", "base_files", "public_tests")})
        if {semantic_hash(t) for t in tasks} & {semantic_hash(t) for t in old_tasks}:
            raise ValueError("calibration_study_task_overlap")
    verification = verify(tasks, runtime)
    sources = bindings()
    folder.mkdir(parents=True)
    save_new(folder / "tasks.json", tasks)
    save_new(folder / "verification.json", verification)
    with zipfile.ZipFile(folder / "source_snapshot.zip", "x", compression=zipfile.ZIP_DEFLATED) as archive:
        for row in sources:
            info = zipfile.ZipInfo(row["path"], date_time=(2026, 10, 13, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            archive.writestr(info, (ROOT / row["path"]).read_bytes())
    schedule = identities(tasks, split)
    manifest = {"study": STUDY, "prepared_utc": now(), "split": split,
        "evidence_kind": "unperformed_frozen_development_allocation", "model": MODEL, "effort": EFFORT,
        "immutable_model_revision": None, "provider_sampling_seed": None, "seed": seed,
        "per_family": per_family, "arms": list(selected_arms(split)), "continuation_attempts": ATTEMPTS,
        "workers": workers, "runtime_workers": RUNTIME_WORKERS, "image": IMAGE,
        "request_body_byte_limit": MAX_BODY_BYTES, "request_text_utf8_byte_limit": MAX_INPUT_TEXT_BYTES,
        "isolated_content_interpretation_gate": "no capacity dispositions in any planned task; all outcomes retained if gate fails",
        "tasks_sha256": sha(tasks), "jobs": jobs(tasks, seed, split), "schedule": [asdict(i) for i in schedule],
        "generation_ceiling": len(schedule), "source_bindings": sources,
        "verification_sha256": sha(verification), "snapshot_sha256": sha((folder / "source_snapshot.zip").read_bytes()),
        "calibration_gate": gate, "bootstrap_seed": 2026101319,
        "primary": "held-out correctness of the first publicly accepted repair within three continuation attempts",
        "factorial": "failed unified diff retained/deleted independently of shared closed-category diagnostic lesson absent/present",
        "eligibility": "first natural submitted patch executes with valid outputs but fails public examples, with at least four changed nonempty lines and an AST change excluding standalone strings",
        "stopping": "fixed cohort irrespective of treatment outcomes or eligible count; public pass stops individual arm; no retries or replacement tasks",
        "information": "all full specifications, base files and public examples preserved; same checkpoint and initial feedback; only failed_work and lesson differ",
        "runtime_access": "fresh pinned Docker container per suite, no network or host mounts; candidate sees all inputs in its suite batch; expected answers remain outside container",
        "model_access": "fresh isolated Luna subscription thread per call; no archives, evaluator, private feedback, prior provider sessions or opaque reasoning replay; pinned client has disclosed inert-tool observation limitations",
        "unknowns": "transport unknown ends affected trajectory; missing lesson makes KL/RL missing while K0/R0 remain runnable; infrastructure/isolation/source faults stop global admission",
        "resources": "actual shared prefix and writer once; standalone lesson arms include writer cost, no-lesson arms do not; equal actor-attempt allowance, not equal tokens or total compute",
        "authorization": "Explicit human authorization for thousands of Luna subscription calls and parallel workers; no purchases, API key, fallback or automatic retries",
        "limitations": ["Four authored composite families with eight components per task; finite seeded component pools are reused within each allocation, not independent real repositories.",
                        "Visible patch deletion; workspace restoration held constant and private reasoning not manipulated.",
                        "Categorical diagnostic hints, not unrestricted natural-language reflection.",
                        "Task bootstrap is descriptive; related generated tasks and unpinned provider weights limit population inference."]}
    save_new(folder / "manifest.json", manifest)
    save_new(folder / "bundle.json", {"manifest_sha256": sha(manifest), "model_calls": 0})
    return manifest


def check_bundle(folder, *, check_sources=True):
    folder = Path(folder)
    manifest, tasks = read(folder / "manifest.json"), read(folder / "tasks.json")
    if sha(manifest) != read(folder / "bundle.json")["manifest_sha256"] or sha(tasks) != manifest["tasks_sha256"]:
        raise ValueError("bundle_changed")
    if manifest["study"] != STUDY or manifest["arms"] != list(selected_arms(manifest["split"])):
        raise ValueError("study_contract_changed")
    if tasks != generate(split=manifest["split"], seed=manifest["seed"], per_family=manifest["per_family"]):
        raise ValueError("cohort_not_reproducible")
    schedule = identities(tasks, manifest["split"])
    if manifest["schedule"] != [asdict(i) for i in schedule] or manifest["generation_ceiling"] != len(schedule):
        raise ValueError("allocation_changed")
    if manifest["jobs"] != jobs(tasks, manifest["seed"], manifest["split"]):
        raise ValueError("jobs_changed")
    if sha(read(folder / "verification.json")) != manifest["verification_sha256"]:
        raise ValueError("verification_changed")
    if sha((folder / "source_snapshot.zip").read_bytes()) != manifest["snapshot_sha256"]:
        raise ValueError("snapshot_changed")
    with zipfile.ZipFile(folder / "source_snapshot.zip") as archive:
        if set(archive.namelist()) != {row["path"] for row in manifest["source_bindings"]}:
            raise ValueError("snapshot_inventory_changed")
        for row in manifest["source_bindings"]:
            if sha(archive.read(row["path"])) != row["sha256"]:
                raise ValueError("snapshot_source_changed")
            if check_sources and sha((ROOT / row["path"]).read_bytes()) != row["sha256"]:
                raise ValueError("source_drift:" + row["path"])
    return manifest, tasks
