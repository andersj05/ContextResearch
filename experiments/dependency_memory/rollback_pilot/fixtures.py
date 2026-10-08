"""Disclosed authored engineering tasks, permanently excluded from model cohorts."""
from pathlib import Path

from .grading import MathChecker, PublicReceipt
from .records import ActorTask, EvaluatorTask, Record, strict_loads, wire


def math_example():
    fixture = strict_loads(Path(__file__).with_name("review_example.json").read_text(encoding="utf-8"))
    original = fixture["task"]
    public = {"domain": "math", "statement": "Find x,y satisfying x+y=10 and x+2y=14. Return integer values in that order.",
              "family": "integer", "variables": original["variables"], "bounds": original["bounds"],
              "constraints": original["constraints"], "allowed_colors": None, "edges": []}
    task = ActorTask.from_dict("authored-calibration-math", "calibration_excluded", public)
    evaluator = EvaluatorTask.bind(task, {"witness": fixture["evaluator_only"]["illustrative_valid_artifact"],
                                         "origin": "authored review illustration", "license": "repository-authored",
                                         "excluded_from_all_model_study_cohorts": True})
    checkpoint = Record.parse("checkpoint", wire(fixture["checkpoint"]), task)
    branch = Record.parse("branch", wire(fixture["branch"][0]), task, option_ids=("O1", "O2"))
    receipt = PublicReceipt.create(**{key: value for key, value in fixture["feedback"].items() if key != "truncated"})
    lesson = Record.parse("lesson", wire(fixture["lesson"]), task, supplied=task.source_ids() | {"F1"})
    summary = Record.parse("summary", wire(fixture["summary"]), task)
    return task, evaluator, checkpoint, branch, receipt, lesson, summary


def code_example():
    task = ActorTask.from_dict("authored-calibration-sum", "calibration_excluded", {
        "domain": "coding", "statement": "Read two integers from stdin and print their sum.",
        "input_format": "Two whitespace-separated integers.", "output_format": "One integer followed by a newline.",
        "public_examples": [{"id": "public1", "input": "2 3\n", "output": "5\n"}]})
    reference = "import sys\na,b=map(int,sys.stdin.read().split())\nprint(a+b)\n"
    evaluator = EvaluatorTask.bind(task, {"private_tests": [{"id": "reserved1", "input": "-4 9\n", "output": "5\n"},
                                                             {"id": "reserved2", "input": "0 0\n", "output": "0\n"}],
                                         "reference_code": reference, "reference_provenance": "authored sum fixture",
                                         "origin": "authored interface calibration", "license": "repository-authored",
                                         "excluded_from_all_model_study_cohorts": True})
    checkpoint = Record.parse("checkpoint", wire({"facts": [], "open_requirements": ["Produce a standalone Python program."],
              "tentative_options": [{"id": "O1", "method": "Read the two integers and combine them.", "unverified_assumptions": []}],
              "possible_checks": ["public1"]}), task)
    branch = Record.parse("branch", wire({"status": "candidate", "chosen_option": "O1", "assumptions": [],
              "observations": [{"statement": "Authored wrong-program fixture. CODE_BRANCH_ONLY_CANARY", "source_ids": ["task"]}],
              "artifact": {"code": "import sys\nprint(sys.stdin.read().split()[0])\n"}}), task, option_ids=("O1",))
    receipt = PublicReceipt.create("F1", "B1", "public_mismatch", "public1", "2\n", "5\n", "Authored public output mismatch.")
    lesson = Record.parse("lesson", wire({"failure_kind": "public_output_mismatch", "evidence_ids": ["F1"],
              "refuted_claims": ["Printing only the first integer meets the task."], "retained_observations": [],
              "uncertainties": ["A passing program is still needed."]}), task, supplied=task.source_ids() | {"F1"})
    summary = Record.parse("summary", wire({"summary": "The trial printed only the first integer; public1 expected 5 and observed 2."}), task)
    return task, evaluator, checkpoint, branch, receipt, lesson, summary
