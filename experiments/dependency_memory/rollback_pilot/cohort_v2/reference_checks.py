"""Actual Docker validation of all authored reference programs and retained tests."""
import argparse
from pathlib import Path
import time

from ..code_runner import DockerRunner
from ..controller import write_new
from ..grading import CodeChecker
from ..records import digest, wire
from .authored import generate


def run(output, image):
    output = Path(output)
    if output.exists():
        raise FileExistsError(output)
    runner = DockerRunner(image)
    runtime = runner.audit()
    checker = CodeChecker(runner)
    rows = []
    for task, evaluator in generate():
        started = time.monotonic()
        grade = checker.grade(task, evaluator, {"code": evaluator.data()["reference_code"]})
        row = {"task_id": task.task_id, "actor_sha256": task.hash,
               "evaluator_sha256": digest(evaluator.material_json), "grade": grade,
               "elapsed_seconds": time.monotonic() - started}
        rows.append(row)
        print(wire({"reference_task": task.task_id, "score": grade["score"],
                    "retained_tests_executed": len(grade["tests"])}), flush=True)
    result = {"scope": "offline isolated execution of repository-authored references",
              "model_calls": 0, "runtime": runtime, "tasks": rows,
              "all_references_passed": all(x["grade"]["score"] == 1 for x in rows),
              "retained_test_executions": sum(len(x["grade"]["tests"]) for x in rows)}
    write_new(output, wire(result) + "\n")
    if not result["all_references_passed"]:
        raise ValueError("authored reference failed retained suite; no launch")
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--image", required=True)
    args = parser.parse_args()
    run(args.output, args.image)


if __name__ == "__main__":
    main()
