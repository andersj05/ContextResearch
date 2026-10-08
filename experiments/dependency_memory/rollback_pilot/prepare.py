"""Freeze an offline E1/E2 review bundle while leaving live launch gates explicit."""
from __future__ import annotations

import argparse
from pathlib import Path
import platform

from .coding_tasks import select_coding
from .contexts import Renderer
from .controller import write_new
from .fixtures import code_example, math_example
from .math_tasks import generate_math
from .records import ActorTask, EvaluatorTask, digest, strict_loads, wire
from .schedule import ordered_tasks, task_slots


ROOT = Path(__file__).resolve().parents[3]
PACKAGE = Path(__file__).resolve().parent
PROTOCOLS = ("DRAFT_PROTOCOL.md", "EXECUTION_CONTRACT.md", "TASKS_AND_GRADING.md", "ANALYSIS_PLAN.md",
             "EXPERIMENT_SUITE.md", "PROMPTS.md", "POLICY_PROMPTS.md", "design_manifest.json", "review_example.json")


def source_bindings():
    paths = sorted(list(PACKAGE.glob("*.py")) + [PACKAGE / name for name in PROTOCOLS])
    return [{"path": path.relative_to(ROOT).as_posix(), "sha256": digest(path.read_bytes())} for path in paths]


def calibration_requests(renderer):
    math, code = math_example(), code_example()
    mt, _, mc, mb, mf, ml, ms = math
    ct, _, cc, cb, cf, cl, cs = code
    requests = [renderer.render("checkpoint", mt), renderer.render("checkpoint", ct),
                renderer.render("branch", mt, mc), renderer.render("branch", ct, cc),
                renderer.render("lesson", mt, mc, [mb], mf), renderer.render("summary", ct, cc, [cb], cf),
                renderer.continuation("K", mt, mc, [mb], mf, ml, ms),
                renderer.continuation("R", ct, cc, [cb], cf, cl, cs)]
    return [{"calibration_call": index + 1, "task_id": mt.task_id if index in (0, 2, 4, 6) else ct.task_id,
             "stage": request.stage, "request": request.data(), "request_sha256": request.hash,
             "complete_input_units": request.input_units, "counter_id": request.counter_id,
             "excluded_from_all_model_study_cohorts": True} for index, request in enumerate(requests)]


def prepare_bundle(folder, coding_inventory=None, code_checker=None, runtime_audit=None, e0_accepted=False):
    folder = Path(folder)
    folder.mkdir(parents=True, exist_ok=False)
    renderer = Renderer()
    cohort = generate_math()
    coding_report = {"shortfalls": {"easy": 4, "medium": 4, "hard": 4}, "ordering": [], "exclusions": [],
                     "reason": "No pinned, license-reviewed LiveCodeBench inventory/reference package supplied."}
    if coding_inventory is not None:
        if code_checker is None or runtime_audit is None:
            raise ValueError("coding preparation requires the audited isolated runner")
        coding, coding_report = select_coding(coding_inventory, code_checker)
        cohort.extend(coding)
    actors = ordered_tasks([task for task, _ in cohort])
    evaluators = {task.task_id: evaluator for task, evaluator in cohort}
    write_new(folder / "tasks_public.jsonl", "".join(wire({"task_id": task.task_id, "domain": task.domain, "stratum": task.stratum,
                    "public": task.data(), "actor_sha256": task.hash}) + "\n" for task in actors))
    write_new(folder / "tasks_evaluator.jsonl", "".join(wire({"task_id": task.task_id, "actor_sha256": task.hash,
                    "material": evaluators[task.task_id].data()}) + "\n" for task in actors))
    fixtures = [math_example(), code_example()]
    write_new(folder / "calibration_fixtures.json", wire([{"task_id": t.task_id, "actor": t.data(), "evaluator": e.data(),
               "checkpoint": c.data(), "branch": b.data(), "feedback": f.data(), "lesson": l.data(), "summary": s.data(),
               "excluded_from_all_model_study_cohorts": True} for t, e, c, b, f, l, s in fixtures]) + "\n")
    calibration = calibration_requests(renderer)
    write_new(folder / "calibration_requests.jsonl", "".join(wire(x) + "\n" for x in calibration))
    domain_indices, schedule = {"math": 0, "coding": 0}, []
    for task in actors:
        schedule.extend(vars(x) for x in task_slots("UNALLOCATED_E2_REVIEW", task, domain_indices[task.domain]))
        domain_indices[task.domain] += 1
    write_new(folder / "schedule.jsonl", "".join(wire(x) + "\n" for x in schedule))
    write_new(folder / "coding_selection.json", wire(coding_report) + "\n")
    if runtime_audit is not None:
        write_new(folder / "runtime_audit.json", wire(runtime_audit) + "\n")
    gates = {"E0_engineering_acceptance": bool(e0_accepted), "coding_cohort_12_with_reviewed_provenance": False,
             "runtime_reference_and_isolation_checks": runtime_audit is not None and bool(e0_accepted),
             "provider_endpoint_adapter_and_retry_audit": False, "provider_tokenizer_and_overhead_audit": False,
             "model_revision_and_account_access": False, "fresh_pricing_and_metering_calibration": False,
             "separate_E1_E2_launch_allocation": False}
    artifacts = [{"path": p.name, "bytes": p.stat().st_size, "sha256": digest(p.read_bytes())} for p in sorted(folder.iterdir())]
    manifest = {"schema_version": "rollback-offline-preparation-1", "as_of": "2026-10-08",
                "status": "frozen_offline_review_bundle_with_open_live_gates", "launch_authorized": False,
                "model_calls": 0, "selected_transport": None, "immutable_model_revision": None,
                "provider_sampling_seed": None, "python_generator_version": platform.python_version(),
                "prepared_math_tasks": domain_indices["math"], "prepared_coding_tasks": domain_indices["coding"],
                "required_math_tasks": 12, "required_coding_tasks": 12, "calibration_request_count": len(calibration),
                "task_ids": [t.task_id for t in actors], "schedule_scope": "prepared tasks only; missing coding identities are not fabricated",
                "local_schedule_seed": 20261007, "math_base_seed": 20261008,
                "limits": {"maximum_calls_with_calibration": 320, "maximum_task_calls": 312, "proposed_ceiling_usd": "5.00",
                           "per_call_reserve_usd": "0.012288", "maximum_reserve_usd": "3.93216", "automatic_retries": False,
                           "input_token_cap": 32768, "generated_token_cap_including_reasoning": 16384,
                           "writer_visible_token_cap": 1024},
                "counter": {"id": renderer.counter.counter_id, "provider_audited": False,
                            "units": "UTF-8 bytes plus 256 synthetic overhead units, not measured provider tokens"},
                "dataset": {"name": "livecodebench/code_generation_lite", "release": "release_v6",
                            "commit": coding_inventory["dataset_commit"] if coding_inventory else None,
                            "license_review": "unresolved" if coding_inventory is None else "supplied attestations; actual source verification pending"},
                "gates": gates, "open_gates": [name for name, passed in gates.items() if not passed],
                "source_bindings": source_bindings(), "artifacts": artifacts}
    write_new(folder / "manifest.json", wire(manifest) + "\n")
    return manifest


def verify_bundle(folder, *, check_sources=True):
    folder = Path(folder).resolve()
    manifest = strict_loads((folder / "manifest.json").read_text(encoding="utf-8"))
    if manifest["launch_authorized"] or manifest["model_calls"] != 0 or manifest["selected_transport"] is not None:
        raise ValueError("this bundle cannot authorize or claim a live launch")
    for binding in manifest["artifacts"]:
        path = (folder / binding["path"]).resolve()
        if not path.is_relative_to(folder) or path.is_symlink() or not path.is_file() or digest(path.read_bytes()) != binding["sha256"] or path.stat().st_size != binding["bytes"]:
            raise ValueError(f"artifact binding failed: {binding['path']}")
    if check_sources:
        for binding in manifest["source_bindings"]:
            path = (ROOT / binding["path"]).resolve()
            if not path.is_relative_to(ROOT) or not path.is_file() or digest(path.read_bytes()) != binding["sha256"]:
                raise ValueError(f"source binding failed: {binding['path']}")
    actors = []
    for line in (folder / "tasks_public.jsonl").read_text(encoding="utf-8").splitlines():
        row = strict_loads(line)
        task = ActorTask.from_dict(row["task_id"], row["stratum"], row["public"])
        if task.domain != row["domain"] or task.hash != row["actor_sha256"]:
            raise ValueError("actor binding")
        actors.append(task)
    if manifest["task_ids"] != [t.task_id for t in actors] or len({t.task_id for t in actors}) != len(actors):
        raise ValueError("manifest task order/identity")
    for line, task in zip((folder / "tasks_evaluator.jsonl").read_text(encoding="utf-8").splitlines(), actors, strict=True):
        row = strict_loads(line)
        EvaluatorTask(row["task_id"], row["actor_sha256"], wire(row["material"])).check_binding(task)
    calibration = [strict_loads(line) for line in (folder / "calibration_requests.jsonl").read_text(encoding="utf-8").splitlines()]
    if calibration != calibration_requests(Renderer()):
        raise ValueError("calibration schedule/request bytes changed")
    indices, expected_schedule = {"math": 0, "coding": 0}, []
    for task in actors:
        expected_schedule.extend(vars(x) for x in task_slots("UNALLOCATED_E2_REVIEW", task, indices[task.domain]))
        indices[task.domain] += 1
    saved_schedule = [strict_loads(line) for line in (folder / "schedule.jsonl").read_text(encoding="utf-8").splitlines()]
    if saved_schedule != expected_schedule or indices["math"] != manifest["prepared_math_tasks"] or indices["coding"] != manifest["prepared_coding_tasks"]:
        raise ValueError("schedule/count binding")
    if manifest["open_gates"] != [name for name, passed in manifest["gates"].items() if not passed] or not manifest["open_gates"]:
        raise ValueError("unresolved live gates must remain explicit")
    return {"verified_tasks": len(actors), "verified_calibration_requests": len(calibration), "verified_schedule_slots": len(saved_schedule),
            "source_bindings": len(manifest["source_bindings"]), "artifacts": len(manifest["artifacts"]), "live_ready": False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--verify", action="store_true")
    args = parser.parse_args()
    if args.verify:
        print(wire(verify_bundle(args.output)))
    else:
        prepare_bundle(args.output)
        print(wire(verify_bundle(args.output)))


if __name__ == "__main__":
    main()
