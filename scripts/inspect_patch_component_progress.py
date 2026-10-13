"""Posthoc component preservation on saved v11 patches; no model calls.

Candidate source executes only through the unchanged v11 PatchRuntime in fresh
containers: six public cases, then a separate terminal batch containing all six
public plus eighteen reserved cases. Original input order remains intact.
This diagnostic does not change frozen outcomes or identify a causal
mechanism; components recur across authored projects.
"""

from argparse import ArgumentParser
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import json
import sys
import threading

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from experiments.dependency_memory.rollback_patch_v11.common import ARMS, read, save_new, sha, now
from experiments.dependency_memory.rollback_patch_v11.runtime import PatchRuntime
from experiments.dependency_memory.rollback_patch_v11.tasks import verify_tasks, canonical
from experiments.dependency_memory.rollback_patch_v10.runtime import FORMAT
from experiments.dependency_memory.rollback_checkpoint_v7.audit import _inventory
from experiments.dependency_memory.rollback_pilot.records import strict_loads


ROLES = ("first_repair", "terminal_submitted_repair", "public_accepted_repair")


class Capture:
    """Observe Docker's returned data without changing execution or its inputs."""

    def __init__(self, runner):
        self.runner, self.local = runner, threading.local()

    def __getattr__(self, name):
        return getattr(self.runner, name)

    def execute(self, *args, **kwargs):
        self.local.result = self.runner.execute(*args, **kwargs)
        return self.local.result


def outputs_from(result, count):
    if result is None or result.status != "completed":
        return None
    try:
        value = strict_loads(result.stdout)
        if (set(value) != {"format", "status", "outputs", "detail"}
                or value["format"] != FORMAT or value["status"] != "completed"
                or type(value["outputs"]) is not list or len(value["outputs"]) != count):
            return None
        return value["outputs"]
    except (ValueError, TypeError, KeyError):
        return None


def component_scores(task, terminal_outputs):
    """Score exactly the original 24-case terminal batch; never splice batches."""
    result = []
    for contract in task["contract"]["component_contracts"]:
        key, cases = contract["component_id"], []
        offset = 0
        for suite, tests in (("public", task["public_tests"]),
                             ("reserved", task["evaluator"]["reserved_tests"])):
            for index, test in enumerate(tests):
                observed = None if terminal_outputs is None else terminal_outputs[offset + index]
                if terminal_outputs is None:
                    status = "unobserved_whole_project_execution_failure"
                elif type(observed) is not dict or key not in observed:
                    status = "fail_missing_component_value"
                else:
                    status = ("pass" if canonical(observed[key]) == canonical(test["expected"][key])
                              else "fail_value_mismatch")
                cases.append({"suite": suite, "id": test["id"], "status": status})
            offset += len(tests)
        counts = Counter("pass" if row["status"] == "pass" else
                         "fail" if row["status"].startswith("fail_") else "unobserved" for row in cases)
        all_correct = False if counts["fail"] else None if counts["unobserved"] else True
        result.append({"component_id": key, "family": contract["family"],
                       "all_24_cases_correct": all_correct, "passed_cases": counts["pass"],
                       "failed_cases": counts["fail"], "unobserved_cases": counts["unobserved"],
                       "cases": cases})
    return result


def selected_records(result):
    attempts = result.get("attempts", [])
    accepted = next((row for row in attempts if row.get("public", {}).get("status") == "public_pass"), None)
    return {
        "first_repair": attempts[0] if attempts else None,
        # An unknown final call is never replaced by the last known submission.
        "terminal_submitted_repair": (attempts[-1] if attempts and
                                      (accepted is not None or result.get("disposition") == "repair_budget_exhausted") else None),
        "public_accepted_repair": accepted,
    }


def plan_candidates(tasks, execution):
    rows = {(row["job"]["task_id"], row["job"]["arm"]): row["result"] for row in execution["jobs"]}
    candidates, projects = {}, []

    def reference(task, record):
        if record is None:
            return {"availability": "missing", "candidate_sha256": None}
        candidate = record.get("candidate")
        if candidate is None:
            return {"availability": "invalid_submission_without_candidate", "candidate_sha256": None,
                    "step": record["step"]}
        key = sha(candidate)
        candidates[(task["task_id"], key)] = candidate
        return {"availability": "saved_candidate", "candidate_sha256": key, "step": record["step"],
                "saved_public_sha256": sha(record["public"]), "saved_terminal_sha256": sha(record["terminal"])}

    for task in tasks:
        prefix = rows[(task["task_id"], "prefix")]
        if not prefix["eligible"]:
            continue
        failed = prefix["failed_record"]
        if failed["public"]["status"] != "public_mismatch":
            raise ValueError("eligible prefix lacks a naturally failed executable patch")
        project = {"task_id": task["task_id"], "family": task["family"],
                   "initial_failed_patch": reference(task, failed),
                   "initial_patch_bytes": len(failed["visible_work"]["patch"].encode("utf-8")),
                   "initial_changed_nonempty_lines": failed["changed_nonempty_lines"], "arms": {}}
        for arm in ARMS:
            result = rows[(task["task_id"], arm)]
            project["arms"][arm] = {"disposition": result["disposition"],
                                    "frozen_score": result.get("score"),
                                    "final_outcome_missing": result.get("score") is None,
                                    **{role: reference(task, record)
                                       for role, record in selected_records(result).items()}}
        projects.append(project)
    return projects, candidates


def compare_components(initial, following):
    later = {row["component_id"]: row for row in following} if following is not None else {}
    result = {key: [] for key in ("initially_correct", "preserved", "regressed", "unassessed",
                                 "initially_failed", "repaired_initial_failure")}
    for row in initial:
        key, before = row["component_id"], row["all_24_cases_correct"]
        after = later.get(key, {}).get("all_24_cases_correct")
        if before is True:
            result["initially_correct"].append(key)
            result["preserved" if after is True else "regressed" if after is False else "unassessed"].append(key)
        elif before is False:
            result["initially_failed"].append(key)
            if after is True:
                result["repaired_initial_failure"].append(key)
    return result


def inspect(bundle, run, destination, *, workers=4, plan_only=False):
    bundle, run, destination = map(lambda value: Path(value).resolve(), (bundle, run, destination))
    if (not destination.is_relative_to(ROOT) or destination.exists()
            or destination.is_relative_to(bundle) or destination.is_relative_to(run)):
        raise ValueError("unused output outside sealed inputs required")
    manifest, tasks, execution = read(bundle / "manifest.json"), read(bundle / "tasks.json"), read(run / "execution.json")
    if read(run / "manifest.json") != manifest or sha(tasks) != manifest["tasks_sha256"]:
        raise ValueError("sealed run/task binding mismatch")
    _inventory(run)
    for binding in manifest["source_bindings"]:
        if sha((ROOT / binding["path"]).read_bytes()) != binding["sha256"]:
            raise ValueError("frozen source changed: " + binding["path"])
    verification = verify_tasks(tasks)
    projects, planned = plan_candidates(tasks, execution)
    report = {
        "schema": "posthoc-v11-component-progress-v2", "created_utc": now(), "posthoc": True,
        "model_calls": 0, "host_candidate_execution": False, "plan_only": plan_only,
        "evidence_kind": "posthoc_live_patch_diagnostic" if read(run / "run_settings.json")["live"] else "scripted_fixture_diagnostic",
        "bindings": {"script_sha256": sha(Path(__file__).read_bytes()),
                     "manifest_sha256": sha(manifest), "tasks_sha256": sha(tasks),
                     "evidence_manifest_sha256": sha(read(run / "evidence_manifest.json")),
                     "execution_sha256": sha(execution),
                     "bundle": bundle.relative_to(ROOT).as_posix(), "run": run.relative_to(ROOT).as_posix()},
        "verification": verification, "projects": projects,
        "planned_unique_task_candidates": len(planned), "planned_docker_batches": 2 * len(planned),
        "method": "Run the unchanged candidate on the six frozen public cases, then in a separate fresh container on the exact original terminal batch: those same six public cases followed by eighteen reserved cases. Score component correctness from all 24 outputs of that terminal batch alone; do not splice outputs across executions. Public and terminal receipts are compared with their saved counterparts. Cache identical candidate bytes only within a task and this diagnostic. No new cases or model calls.",
        "plan_correction": "Version 1 was an unused plan-only draft with an eighteen-case reserved batch. Version 2 corrects that draft before any diagnostic Docker execution: the frozen terminal checker uses public plus reserved inputs in one 24-case batch. The superseded plan is retained unchanged.",
        "limitations": [
            "Exploratory posthoc diagnosis, not a preregistered endpoint or proof that deleting code caused a regression.",
            "Twenty-four tested cases do not establish global program correctness. Component instances recur across authored projects and are not independent trials or real repositories.",
            "A whole-project execution failure can hide otherwise correct components; unobserved outputs remain unassessed. Missing component keys are observed contract failures.",
            "Unknown final calls remain missing. A saved first repair may still be described when its later outcome is missing; it does not replace that missing outcome.",
            "Component value correctness does not excuse extra top-level output keys; whole-project receipts retain that distinction.",
        ],
    }
    if plan_only:
        save_new(destination, report)
        return {"output": str(destination), "plan_only": True, "eligible_projects": len(projects),
                "planned_candidates": len(planned), "planned_docker_batches": 2 * len(planned)}
    runtime = PatchRuntime(max_containers=workers)
    capture = Capture(runtime.runner)
    runtime.runner = capture
    report["runtime_audit"] = runtime.audit()
    by_task = {task["task_id"]: task for task in tasks}

    def evaluate(item):
        (task_id, key), candidate = item
        task, batches, receipts = by_task[task_id], {}, {}
        for suite, tests in (("public", task["public_tests"]),
                             ("terminal", task["public_tests"] + task["evaluator"]["reserved_tests"])):
            capture.local.result = None
            receipts[suite] = runtime.check(candidate, tests, public=suite == "public")
            batches[suite] = outputs_from(capture.local.result, len(tests))
        return (task_id, key), {"task_id": task_id, "candidate_sha256": key,
                               "source_bytes": sum(len(row["text"].encode("utf-8")) for row in candidate["files"]),
                               "receipts": receipts, "components": component_scores(task, batches["terminal"])}

    scored = {}
    with ThreadPoolExecutor(max_workers=workers) as executor:
        for key, result in executor.map(evaluate, planned.items()):
            scored[key] = result
            print(json.dumps({"posthoc_candidates_done": len(scored), "total": len(planned)}), flush=True)
    initial_summary, role_summary = Counter(), {arm: {role: Counter() for role in ROLES} for arm in ARMS}
    initial_by_family, replay_agreement = {}, Counter()
    def check_saved(reference, candidate_result):
        if candidate_result is None:
            return
        receipts = candidate_result["receipts"]
        terminal = {key: receipts["terminal"][key] for key in ("score", "disposition")}
        agreement = {"public": sha(receipts["public"]) == reference["saved_public_sha256"],
                     "terminal": sha(terminal) == reference["saved_terminal_sha256"]}
        reference["saved_receipt_agreement"] = agreement
        replay_agreement["compared_candidate_references"] += 1
        replay_agreement["references_with_any_mismatch"] += int(not all(agreement.values()))
    for project in projects:
        task_id = project["task_id"]
        initial_result = scored[(task_id, project["initial_failed_patch"]["candidate_sha256"])]
        check_saved(project["initial_failed_patch"], initial_result)
        initial = initial_result["components"]
        for component in initial:
            label = "correct_all_24" if component["all_24_cases_correct"] is True else "failed_observed_case" if component["all_24_cases_correct"] is False else "unassessed"
            initial_summary[label] += 1
            initial_by_family.setdefault(component["family"], Counter())[label] += 1
        for arm in ARMS:
            for role in ROLES:
                reference = project["arms"][arm][role]
                candidate_result = scored.get((task_id, reference["candidate_sha256"]))
                check_saved(reference, candidate_result)
                following = candidate_result["components"] if candidate_result else None
                comparison = compare_components(initial, following)
                reference["component_comparison"] = comparison
                role_summary[arm][role].update({key: len(value) for key, value in comparison.items()})
                role_summary[arm][role]["projects_with_saved_candidate"] += int(following is not None)
    report.update(candidate_results=[scored[key] for key in sorted(scored)],
                  runtime_statistics=runtime.statistics(),
                  summary={"eligible_projects": len(projects), "initial_component_instances": dict(initial_summary),
                           "initial_by_component_family": initial_by_family,
                           "saved_receipt_replay_agreement": replay_agreement,
                           "preservation_by_arm_and_role": role_summary})
    save_new(destination, report)
    return {"output": str(destination), "model_calls": 0, "eligible_projects": len(projects),
            "unique_task_candidates": len(scored), "docker_batches": runtime.statistics()["executions"],
            "summary": report["summary"]}


def main():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("bundle")
    parser.add_argument("run")
    parser.add_argument("output")
    parser.add_argument("--workers", type=int, choices=range(1, 5), default=4)
    parser.add_argument("--plan-only", action="store_true", help="validate and plan without any candidate execution")
    args = parser.parse_args()
    print(json.dumps(inspect(args.bundle, args.run, args.output, workers=args.workers, plan_only=args.plan_only), sort_keys=True))


if __name__ == "__main__":
    main()
