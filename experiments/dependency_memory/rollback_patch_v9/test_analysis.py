"""Independent factorial arithmetic, missingness and endpoint controls."""
from copy import deepcopy
from itertools import product
import unittest

from experiments.dependency_memory.rollback_patch_v9.analysis import (
    ARMS, CONTRASTS, analyze, contrast,
)


def task_row(task_id, values, family="family-a"):
    return {"task_id": task_id, "family": family, **dict(zip(ARMS, values))}


def outcome(score, *, first_pass=None, attempts=3):
    if first_pass is not None:
        attempts = first_pass
    records = [{"step": step,
                "public": {"status": "public_pass" if step == first_pass else "public_mismatch"},
                "terminal": {"score": score if step == first_pass else 0}}
               for step in range(1, attempts + 1)]
    return {"score": score, "disposition": "unknown_dispatch" if score is None else "fixture",
            "first_pass": first_pass, "attempts": records}


def inputs(scores=(0, 1, 0, 1), *, split="study", lesson_disposition="valid"):
    tasks = [{"task_id": "task-1", "family": "family-a"}]
    jobs = [{"job": {"task_id": "task-1", "arm": "prefix"},
             "result": {"eligible": True, "reason": "natural_substantive_patch_mismatch",
                        "lesson_disposition": lesson_disposition}}]
    for arm, score in zip(ARMS, scores):
        result = outcome(score, first_pass=1 if score == 1 else None,
                         attempts=1 if score is None else 3)
        jobs.append({"job": {"task_id": "task-1", "arm": arm}, "result": result})
    return tasks, {"jobs": jobs}, {"calls": []}, {
        "split": split, "seed": 99, "continuation_attempts": 3,
        "bootstrap_replicates": 100, "minimum_complete_for_interval": 6}


def call(arm, *, stage="action", unknown=False):
    result = {"identity": {"task_id": "task-1", "arm": arm, "stage": stage},
              "state": "unknown" if unknown else "completed"}
    if unknown:
        result["reserve_credits"] = "4.225"
    else:
        result.update(usage={"input_tokens": 20, "cached_input": 5, "output": 10, "reasoning": 7},
                      planning_credits="0.01", elapsed_seconds=1.5)
    return result


class FactorialAnalysisTests(unittest.TestCase):
    def test_opposite_simple_effects_are_visible_despite_zero_main_effect(self):
        # Removing helps without the lesson but hurts with it.
        rows = [task_row("one", (0, 1, 1, 0))]
        actual = {name: contrast(rows, weights, seed=1)["complete_case_mean"]
                  for name, weights in CONTRASTS.items()}
        self.assertEqual(actual["deletion_main"], 0)
        self.assertEqual(actual["lesson_main"], 0)
        self.assertEqual(actual["deletion_without_lesson"], 1)
        self.assertEqual(actual["deletion_with_lesson"], -1)
        self.assertEqual(actual["interaction"], -2)

    def test_missingness_bounds_equal_exhaustive_binary_completions(self):
        rows = [task_row("one", (0, None, 1, None)), task_row("two", (None, 1, None, 0))]
        missing = [(index, arm) for index, row in enumerate(rows) for arm in ARMS if row[arm] is None]
        for name, weights in CONTRASTS.items():
            with self.subTest(contrast=name):
                values = []
                for assignments in product((0, 1), repeat=len(missing)):
                    filled = deepcopy(rows)
                    for (index, arm), value in zip(missing, assignments):
                        filled[index][arm] = value
                    values.append(sum(sum(weights[arm] * row[arm] for arm in weights)
                                      for row in filled) / len(filled))
                result = contrast(rows, weights, seed=1)
                self.assertEqual(result["finite_cohort_missingness_bounds"], [min(values), max(values)])

    def test_missing_lesson_does_not_drop_known_no_lesson_pair(self):
        args = inputs((0, 1, None, None), lesson_disposition="unknown_dispatch")
        report = analyze(*args, simulated=True)
        no_lesson = report["factorial_contrasts"]["deletion_without_lesson"]
        main = report["factorial_contrasts"]["deletion_main"]
        self.assertEqual(no_lesson["complete_case_mean"], 1)
        self.assertEqual(no_lesson["finite_cohort_missingness_bounds"], [1, 1])
        self.assertIsNone(main["complete_case_mean"])
        self.assertEqual(main["finite_cohort_missingness_bounds"], [0, 1])
        self.assertEqual(report["eligible_natural_failures"], 1)
        self.assertEqual(report["complete_quartets"], 0)
        self.assertEqual(report["arms"]["KL"]["terminal_success"]["missing"], 1)

    def test_stratified_bootstrap_preserves_pairing_and_reproduces(self):
        rows = [task_row(str(index), (0, 1, 0, 1), family="a" if index < 3 else "b")
                for index in range(6)]
        first = contrast(rows, CONTRASTS["deletion_main"], seed=7, bootstrap_replicates=100)
        second = contrast(rows, CONTRASTS["deletion_main"], seed=7, bootstrap_replicates=100)
        self.assertEqual(first, second)
        self.assertEqual(first["complete_case_family_counts"], {"a": 3, "b": 3})
        self.assertEqual(first["descriptive_bootstrap_95"]["lower"], 1)
        self.assertEqual(first["descriptive_bootstrap_95"]["upper"], 1)
        self.assertIsNone(first["confirmatory_p_value"])
        self.assertIn("Complete cases only", first["descriptive_bootstrap_95"]["scope"])

    def test_public_acceptance_does_not_imply_heldout_success(self):
        args = inputs()
        args[1]["jobs"][1]["result"] = outcome(0, first_pass=1)
        report = analyze(*args, simulated=True)
        arm = report["arms"]["K0"]
        self.assertEqual(arm["public_repair_by_attempt"]["1"]["passed"], 1)
        self.assertEqual(arm["public_repair_by_attempt"]["3"]["passed"], 1)
        self.assertEqual(arm["terminal_success"]["passed"], 0)

    def test_three_attempts_allow_delayed_repair(self):
        args = inputs((1, 1, 1, 1))
        args[1]["jobs"][1]["result"] = outcome(1, first_pass=3)
        report = analyze(*args, simulated=True)
        curve = report["arms"]["K0"]["public_repair_by_attempt"]
        self.assertEqual([curve[str(n)]["passed"] for n in (1, 2, 3)], [0, 0, 1])
        self.assertEqual(report["arms"]["K0"]["terminal_success"]["passed"], 1)

    def test_later_unknown_keeps_observed_early_failure_and_missing_later_curve(self):
        args = inputs((None, 1, 1, 1))
        report = analyze(*args, simulated=True)
        curve = report["arms"]["K0"]["public_repair_by_attempt"]
        self.assertEqual(curve["1"]["known"], 1)
        self.assertEqual(curve["1"]["passed"], 0)
        self.assertEqual(curve["2"]["missing"], 1)
        self.assertEqual(curve["3"]["missing"], 1)
        self.assertEqual(report["arms"]["K0"]["terminal_success"]["missing"], 1)

    def test_heldout_pass_without_public_pass_is_only_diagnostic(self):
        args = inputs()
        args[1]["jobs"][1]["result"]["attempts"][0]["terminal"]["score"] = 1
        report = analyze(*args, simulated=True)
        arm = report["arms"]["K0"]
        self.assertEqual(arm["terminal_success"]["passed"], 0)
        self.assertEqual(arm["public_repair_by_attempt"]["1"]["passed"], 0)
        self.assertEqual(arm["diagnostic_any_heldout_pass_by_attempt"]["1"]["passed"], 1)

    def test_calibration_reports_no_factorial_effects(self):
        report = analyze(*inputs(split="calibration"), simulated=True)
        self.assertFalse(report["factorial_effects_evaluated"])
        self.assertEqual(report["factorial_contrasts"], {})
        self.assertEqual(set(report["arms"]), {"K0"})
        self.assertEqual(report["complete_quartet_standalone_resource_projections"], {})

    def test_shared_costs_count_once_and_lesson_absent_from_no_lesson_projection(self):
        args = inputs()
        args[2]["calls"] = [call("prefix"), call("prefix", stage="lesson"), *(call(arm) for arm in ARMS)]
        report = analyze(*args, simulated=True)
        self.assertEqual(report["actual_study_resources"]["admitted_calls"], 6)
        self.assertEqual(report["actual_study_resources"]["known_planning_credits"], "0.06")
        projections = report["complete_quartet_standalone_resource_projections"]
        self.assertEqual(projections["K0"]["admitted_calls"], 2)
        self.assertEqual(projections["R0"]["admitted_calls"], 2)
        self.assertEqual(projections["KL"]["admitted_calls"], 3)
        self.assertEqual(projections["RL"]["admitted_calls"], 3)
        self.assertEqual(projections["KL"]["known_planning_credits"], "0.03")
        self.assertEqual(sum(group["admitted_calls"] for group in report["disjoint_resource_categories"].values()), 6)

    def test_unknown_writer_cost_is_retained_without_dropping_no_lesson_results(self):
        args = inputs((0, 1, None, None), lesson_disposition="unknown_dispatch")
        args[2]["calls"] = [call("prefix"), call("prefix", stage="lesson", unknown=True), call("K0"), call("R0")]
        report = analyze(*args, simulated=True)
        self.assertEqual(report["actual_study_resources"]["unknown_locked_planning_credits"], "4.225")
        self.assertEqual(report["disjoint_resource_categories"]["shared_lesson"]["unknown_calls"], 1)
        self.assertEqual(report["actual_study_resources"]["known_calls"], 3)
        self.assertEqual(report["factorial_contrasts"]["deletion_without_lesson"]["complete_tasks"], 1)

    def test_unknown_prefix_is_reported_without_inventing_eligibility(self):
        args = inputs()
        args[1]["jobs"][0]["result"] = {"eligible": False, "reason": "unknown_dispatch"}
        report = analyze(*args, simulated=True)
        self.assertEqual(report["planned_tasks"], 1)
        self.assertEqual(report["eligible_natural_failures"], 0)
        self.assertEqual(report["prefix_dispositions"], {"unknown_dispatch": 1})
        self.assertIsNone(report["factorial_contrasts"]["deletion_main"]["finite_cohort_missingness_bounds"])

    def test_inconsistent_acceptance_or_success_is_rejected(self):
        for mutation in ("no_public_pass", "later_record", "wrong_first_pass", "hidden_failure"):
            with self.subTest(mutation=mutation):
                args = inputs((1, 1, 1, 1))
                result = args[1]["jobs"][1]["result"]
                if mutation == "no_public_pass":
                    result["attempts"][0]["public"]["status"] = "public_mismatch"
                    result["first_pass"] = None
                elif mutation == "later_record":
                    result["attempts"].append(outcome(0)["attempts"][0])
                elif mutation == "wrong_first_pass":
                    result["first_pass"] = 2
                else:
                    result["attempts"][0]["terminal"]["score"] = 0
                with self.assertRaises(ValueError):
                    analyze(*args, simulated=True)


if __name__ == "__main__":
    unittest.main()
