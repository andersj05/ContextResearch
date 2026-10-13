"""Bounded posthoc check of which correct failed-patch components were new fixes.

Only original visible checkpoint candidates are newly executed. Follow-up
component results are read from the completed, separately bound diagnostic.
No model calls and no changes to the frozen scientific allocation.
"""

from argparse import ArgumentParser
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import json
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts import inspect_patch_component_progress as component
from experiments.dependency_memory.rollback_patch_v11.common import ARMS, read, save_new, sha, now
from experiments.dependency_memory.rollback_patch_v11.runtime import PatchRuntime
from experiments.dependency_memory.rollback_checkpoint_v7.audit import _inventory


def classify(base, initial):
    before = {row["component_id"]: row["all_24_cases_correct"] for row in base}
    result = {key: [] for key in ("verified_partial_fixes", "already_correct_checkpoint",
                                 "initially_correct_with_unassessed_base", "checkpoint_regressions_in_initial_patch")}
    for row in initial:
        key, after = row["component_id"], row["all_24_cases_correct"]
        if after is True:
            label = ("verified_partial_fixes" if before[key] is False else "already_correct_checkpoint"
                     if before[key] is True else "initially_correct_with_unassessed_base")
            result[label].append(key)
        elif after is False and before[key] is True:
            result["checkpoint_regressions_in_initial_patch"].append(key)
    return result


def verified_comparison(fixes, comparison):
    fixes = set(fixes)
    return {key: sorted(fixes & set(comparison[key])) for key in ("preserved", "regressed", "unassessed")}


def inspect(bundle, run, progress, destination, *, workers=4):
    bundle, run, progress, destination = map(lambda value: Path(value).resolve(), (bundle, run, progress, destination))
    if (not destination.is_relative_to(ROOT) or destination.exists()
            or destination.is_relative_to(bundle) or destination.is_relative_to(run)):
        raise ValueError("unused result path outside sealed inputs required")
    manifest, tasks, previous = read(bundle / "manifest.json"), read(bundle / "tasks.json"), read(progress)
    if (previous["schema"] != "posthoc-v11-component-progress-v2" or previous["plan_only"]
            or previous["bindings"]["manifest_sha256"] != sha(manifest)
            or previous["bindings"]["tasks_sha256"] != sha(tasks)
            or previous["bindings"]["script_sha256"] != sha(Path(component.__file__).read_bytes())
            or read(run / "manifest.json") != manifest):
        raise ValueError("finished component diagnostic binding mismatch")
    _inventory(run)
    if previous["bindings"]["evidence_manifest_sha256"] != sha(read(run / "evidence_manifest.json")):
        raise ValueError("run evidence changed")
    for binding in manifest["source_bindings"]:
        if sha((ROOT / binding["path"]).read_bytes()) != binding["sha256"]:
            raise ValueError("frozen source changed: " + binding["path"])
    project_ids = {project["task_id"] for project in previous["projects"]}
    selected = [task for task in tasks if task["task_id"] in project_ids]
    if len(selected) != len(project_ids) or len(selected) != 28:
        raise ValueError("this bounded diagnostic is fixed to the 28 saved eligible projects")
    runtime = PatchRuntime(max_containers=workers)
    capture = component.Capture(runtime.runner)
    runtime.runner = capture
    audit = runtime.audit()

    def evaluate(task):
        candidate = {"files": task["base_files"]}
        receipts, terminal_outputs = {}, None
        for suite, tests in (("public", task["public_tests"]),
                             ("terminal", task["public_tests"] + task["evaluator"]["reserved_tests"])):
            capture.local.result = None
            receipts[suite] = runtime.check(candidate, tests, public=suite == "public")
            if suite == "terminal":
                terminal_outputs = component.outputs_from(capture.local.result, len(tests))
        return {"task_id": task["task_id"], "base_candidate_sha256": sha(candidate),
                "receipts": receipts, "components": component.component_scores(task, terminal_outputs)}

    bases = {}
    with ThreadPoolExecutor(max_workers=workers) as executor:
        for value in executor.map(evaluate, selected):
            bases[value["task_id"]] = value
            print(json.dumps({"base_candidates_done": len(bases), "total": len(selected)}), flush=True)
    candidates = {(row["task_id"], row["candidate_sha256"]): row for row in previous["candidate_results"]}
    totals, by_family, base_counts = Counter(), {}, Counter()
    role_totals = {arm: {role: Counter() for role in component.ROLES} for arm in ARMS}
    rows = []
    for project in previous["projects"]:
        task_id = project["task_id"]
        initial = candidates[(task_id, project["initial_failed_patch"]["candidate_sha256"])]
        classification = classify(bases[task_id]["components"], initial["components"])
        totals.update({key: len(value) for key, value in classification.items()})
        for row in bases[task_id]["components"]:
            state = row["all_24_cases_correct"]
            base_counts["correct_all_24" if state is True else "failed_observed_case" if state is False else "unassessed"] += 1
        families = {row["component_id"]: row["family"] for row in initial["components"]}
        for label, ids in classification.items():
            for key in ids:
                by_family.setdefault(families[key], Counter())[label] += 1
        item = {"task_id": task_id, "family": project["family"], **classification, "arms": {}}
        for arm in ARMS:
            item["arms"][arm] = {"frozen_score": project["arms"][arm]["frozen_score"],
                                 "final_outcome_missing": project["arms"][arm]["final_outcome_missing"]}
            for role in component.ROLES:
                comparison = verified_comparison(classification["verified_partial_fixes"],
                                                  project["arms"][arm][role]["component_comparison"])
                item["arms"][arm][role] = comparison
                role_totals[arm][role].update({key: len(value) for key, value in comparison.items()})
        rows.append(item)
    report = {
        "schema": "posthoc-v11-base-progress-v1", "posthoc": True, "created_utc": now(),
        "model_calls": 0, "host_candidate_execution": False,
        "bindings": {"script_sha256": sha(Path(__file__).read_bytes()),
                     "component_helper_sha256": sha(Path(component.__file__).read_bytes()),
                     "component_progress_sha256": sha(progress.read_bytes()),
                     "manifest_sha256": sha(manifest), "tasks_sha256": sha(tasks),
                     "evidence_manifest_sha256": previous["bindings"]["evidence_manifest_sha256"]},
        "method": "The fixed 28 original checkpoints receive one six-case public batch and a separate original 24-case terminal batch, in the original order. A verified partial fix means the base had an observed component failure and the initial failed patch passes that component on all 24 terminal cases. Follow-up preservation is intersected with this verified-fix set; no model outcomes are replaced.",
        "limitations": previous["limitations"] + ["These are finite test-suite partial fixes, not proof of general correctness or identification of a causal mediator."],
        "runtime_audit": audit, "runtime_statistics": runtime.statistics(),
        "base_results": [bases[key] for key in sorted(bases)], "projects": rows,
        "summary": {"projects": len(rows), "base_component_instances": base_counts,
                    "initial_progress": totals, "initial_progress_by_family": by_family,
                    "verified_fix_preservation_by_arm_and_role": role_totals},
    }
    save_new(destination, report)
    return {"output": str(destination), "model_calls": 0, "docker_batches": runtime.statistics()["executions"],
            "summary": report["summary"]}


def main():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("bundle")
    parser.add_argument("run")
    parser.add_argument("component_progress")
    parser.add_argument("output")
    parser.add_argument("--workers", type=int, choices=range(1, 5), default=4)
    args = parser.parse_args()
    print(json.dumps(inspect(args.bundle, args.run, args.component_progress, args.output, workers=args.workers), sort_keys=True))


if __name__ == "__main__":
    main()
