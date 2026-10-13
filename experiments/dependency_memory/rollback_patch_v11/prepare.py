"""Freeze tasks, software, allocation and feasibility gates before model calls."""
from concurrent.futures import ThreadPoolExecutor
from dataclasses import asdict
from pathlib import Path
import zipfile
from .common import (ROOT, PACKAGE, STUDY, MODEL, EFFORT, SEED, ARMS, ATTEMPTS,
                     WORKERS, RUNTIME_WORKERS, MAX_BODY_BYTES, MAX_INPUT_TEXT_BYTES, IMAGE, sha, read, save_new, now)
from .tasks import generate, public_check, terminal_check, verify_tasks
from .engine import identity
from ..rollback_patch_v10.prepare import bindings as old_bindings
from ..rollback_patch_v10.prepare import calibration_gate as original_calibration_gate
from ..rollback_patch_v10.tasks import generate as calibration_tasks


def selected_arms(split):
    return ARMS


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
    paths.add("experiments/dependency_memory/__init__.py")
    paths.update(p.relative_to(ROOT).as_posix() for pattern in ("*.py", "*.md") for p in PACKAGE.glob(pattern))
    return [{"path": path, "sha256": sha((ROOT / path).read_bytes())} for path in sorted(paths)]


def verify(tasks, runtime):
    from .contexts import render, fits, LESSON
    from .engine import patch
    from .common import wire
    structure = verify_tasks(tasks)
    largest_text = largest_body = 0
    for task in tasks:
        example = max(task["public_tests"], key=lambda row: len(wire(row)))
        receipt = {"status": "public_mismatch", "check_id": example["id"],
                   "input": example["input"], "expected": example["expected"], "observed": None,
                   "detail": "Disclosed reference-history serialization fixture; not a model failure."}
        delta = patch(task["base_files"], task["evaluator"]["reference_files"])
        work = {"patch": delta["diff"], "note": "Reference-sized serialization fixture."}
        prefix = {"eligible": True, "failed_record": {"public": receipt, "visible_work": work},
                  "lesson": {key: item["enum"][-1] for key, item in LESSON["properties"].items()}}
        records = [{"step": step, "public": receipt, "work": work} for step in (1, 2)]
        for request in (render(task), render(task, prefix=prefix, kind="lesson"),
                        *(render(task, arm=arm, prefix=prefix, records=records) for arm in ARMS)):
            if not fits(request):
                raise ValueError("reference_history_capacity:" + task["task_id"])
            largest_text = max(largest_text, len(request.json_text.encode("utf-8")))
            largest_body = max(largest_body, request.input_units)
    structure["reference_history_capacity"] = {"passed": True, "tasks": len(tasks),
        "largest_request_text_utf8_bytes": largest_text, "largest_complete_body_bound_bytes": largest_body,
        "scope": "complete task facts, reference-sized failed work and two later reference-sized patches; pathological histories are not guaranteed to fit and trigger the declared interpretation gate"}
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
    """Bind the exact observed departure; never relabel the original failed gate."""
    original = original_calibration_gate(folder)
    failed = sorted(key for key, passed in original["checks"].items() if not passed)
    manifest = read(Path(folder) / "manifest.json")
    checks = {
        "original_gate_remains_failed": original["passed"] is False,
        "only_original_failure_is_headroom": failed == ["natural_failure_headroom"],
        "exact_three_natural_failures": original["eligible"] == 3,
        "exact_three_valid_lessons": original["valid_lessons"] == 3,
        "all_three_controls_correct": original["control_correct"] == 3,
        "v10_control_source": manifest["study"] == "rollback-patch-composite-v10-2026-10-13",
    }
    return {"passed": all(checks.values()), "checks": checks, "original_failed_gate": original,
            "design_departure": "Unplanned exploratory follow-up after 3/16 naturally failed prefixes were all repaired. The frozen v10 minimum was four; its main allocation remains closed. This new fixed cohort was chosen before any deletion/lesson treatment outcomes. It is not a passing v10 gate or confirmation.",
            "calibration_result": original["calibration_result"],
            "calibration_execution_sha256": original["calibration_execution_sha256"],
            "calibration_audit_sha256": original["calibration_audit_sha256"]}


def prepare(folder, *, runtime, split="study", seed=SEED, per_family=64,
            workers=WORKERS, gate_folder=None):
    folder = Path(folder).resolve()
    if not folder.is_relative_to(ROOT) or folder.exists():
        raise ValueError("new_workspace_bundle_required")
    if split not in {"study", "fixture"} or type(workers) is not int or not 1 <= workers <= WORKERS:
        raise ValueError("invalid_allocation")
    if split == "study" and per_family != 64:
        raise ValueError("study_frozen_at_256_tasks")
    if split == "study" and seed != SEED:
        raise ValueError("study_seed_frozen")
    gate = calibration_gate(gate_folder) if split == "study" else None
    if gate is not None and not gate["passed"]:
        raise ValueError("calibration_gate_not_passed")
    tasks = generate(split=split, seed=seed, per_family=per_family)
    if gate is not None:
        old_manifest = read(Path(gate_folder) / "manifest.json")
        old_tasks = calibration_tasks(split=old_manifest["split"], seed=old_manifest["seed"],
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
        "evidence_kind": "unperformed_frozen_exploratory_allocation",
        "design_status": "explicitly unplanned follow-up; v10 four-failure gate remains failed", "model": MODEL, "effort": EFFORT,
        "immutable_model_revision": None, "provider_sampling_seed": None, "seed": seed,
        "per_family": per_family, "arms": list(selected_arms(split)), "continuation_attempts": ATTEMPTS,
        "workers": workers, "runtime_workers": RUNTIME_WORKERS, "image": IMAGE,
        "request_body_byte_limit": MAX_BODY_BYTES, "request_text_utf8_byte_limit": MAX_INPUT_TEXT_BYTES,
        "isolated_content_interpretation_gate": "no capacity dispositions in any planned task; all outcomes retained if gate fails",
        "tasks_sha256": sha(tasks), "jobs": jobs(tasks, seed, split), "schedule": [asdict(i) for i in schedule],
        "generation_ceiling": len(schedule), "source_bindings": sources,
        "verification_sha256": sha(verification), "snapshot_sha256": sha((folder / "source_snapshot.zip").read_bytes()),
        "calibration_gate": gate, "bootstrap_seed": 2026101329,
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
        "limitations": ["Explicitly unplanned development after a failed control-only gate; not confirmation.",
                        "Four authored composite families with eight components per task; finite seeded component pools are reused within each allocation, not independent real repositories.",
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
