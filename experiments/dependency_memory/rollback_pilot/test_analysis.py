"""Hand-calculated paired/missingness tables and non-pooled cost projections."""
from copy import deepcopy
from fractions import Fraction
import unittest

from .analysis import analyze, paired, resources, validate_rows
from .controller import Controller
from .fixtures import math_example


def outcome(task_id, K, R, Z=(0, 0), G=(0, 0), domain="math"):
    row = Controller.empty_row(math_example()[0])
    row.update(task_id=task_id, domain=domain, public_failure=True, lesson_usable=True, summary_usable=True,
               primary_scheduled=True, scheduled_arms=["K", "R", "Z", "G"], flow=["public_mismatch"])
    row["grades"] = {"K": list(K), "R": list(R), "Z": list(Z), "G": list(G)}
    return row


class AnalysisTests(unittest.TestCase):
    def test_known_task_differences_not_independent_draw_samples(self):
        rows = [outcome("t1", [1, 0], [1, 1]), outcome("t2", [1, 1], [0, 0]), outcome("t3", [0, 0], [1, 0])]
        result = analyze(rows)["domains"]["math"]["primary_R_minus_K"]
        self.assertEqual(result["scheduled_tasks"], 3)
        self.assertEqual([r["difference"]["fraction"] for r in result["pairs"]], ["1/2", "-1", "1/2"])
        self.assertEqual(result["complete_pair_mean"]["fraction"], "0")
        self.assertEqual(result["all_scheduled_missingness_bounds"][0]["fraction"], "0")
        self.assertIsNone(result["bootstrap"])
        self.assertIsNone(result["confirmatory_p_value"])

    def test_missingness_bounds_keep_scheduled_denominator_and_known_answers(self):
        rows = [outcome("t1", [1, 0], [1, 1]), outcome("t2", [None, 1], [0, None])]
        result = analyze(rows)["domains"]["math"]["primary_R_minus_K"]
        self.assertEqual(result["complete_tasks"], 1)
        self.assertEqual(result["complete_pair_mean"]["fraction"], "1/2")
        self.assertEqual([x["fraction"] for x in result["all_scheduled_missingness_bounds"]], ["-1/4", "1/4"])
        self.assertEqual(result["pairs"][1]["K"], [None, 1])

    def test_every_unknown_slot_spans_full_interval_and_known_failures_stay_zero(self):
        result = paired([outcome("unknown", [None, None], [None, None])], "R", "K")
        self.assertEqual([x["fraction"] for x in result["all_scheduled_missingness_bounds"]], ["-1", "1"])
        result = paired([outcome("known", [0, 0], [0, 0])], "R", "K")
        self.assertEqual([x["fraction"] for x in result["all_scheduled_missingness_bounds"]], ["0", "0"])

    def test_domain_reports_do_not_pool_draws_or_replace_uneligible_tasks(self):
        math = outcome("math1", [0, 0], [1, 1])
        coding = outcome("code1", [1, 1], [0, 0], domain="coding")
        initial_success = Controller.empty_row(math_example()[0], "public_pass")
        initial_success["task_id"] = "success"
        result = analyze([math, coding, initial_success])["domains"]
        self.assertEqual(result["math"]["selected_tasks"], 2)
        self.assertEqual(result["math"]["primary_R_minus_K"]["complete_pair_mean"]["percentage_points"], 100)
        self.assertEqual(result["coding"]["primary_R_minus_K"]["complete_pair_mean"]["percentage_points"], -100)
        self.assertEqual(result["math"]["conditions"]["R"]["scheduled_draws"], 2)

    def test_summary_failure_keeps_primary_and_uses_secondary_intersection(self):
        row = outcome("t1", [0, 1], [1, 1])
        row.update(summary_usable=False, scheduled_arms=["K", "R", "Z"])
        row["grades"]["G"] = [None, None]
        result = analyze([row])["domains"]["math"]
        self.assertEqual(result["primary_R_minus_K"]["scheduled_tasks"], 1)
        self.assertEqual(result["secondary_R_minus_Z"]["scheduled_tasks"], 1)
        self.assertEqual(result["secondary_R_minus_G"]["scheduled_tasks"], 0)
        self.assertEqual(result["conditions"]["G"]["unknown_draws"], 0)

    def test_bootstrap_uses_six_complete_tasks_and_is_seeded_and_descriptive(self):
        rows = [outcome(f"t{i}", [0, 0], [1, 1]) for i in range(6)]
        a, b = paired(rows, "R", "K"), paired(rows, "R", "K")
        self.assertEqual(a["bootstrap"], b["bootstrap"])
        self.assertEqual(a["bootstrap"]["lower"]["fraction"], "1")
        self.assertEqual(a["bootstrap"]["upper"]["fraction"], "1")
        self.assertEqual(a["bootstrap"]["resamples"], 10000)
        self.assertIsNone(paired(rows[:5], "R", "K")["bootstrap"])

    def test_first_example_is_selected_by_frozen_order_not_largest_effect(self):
        result = analyze([outcome("first", [0, 1], [1, 1]), outcome("dramatic", [0, 0], [1, 1])])
        self.assertEqual(result["domains"]["math"]["example_selection"]["R_better"], "first")

    def test_cost_ledger_charges_shared_prep_once_and_projects_only_needed_writer(self):
        stages = [("checkpoint", None, "0.001"), ("branch", None, "0.002"), ("lesson", None, "0.003"),
                  ("summary", None, "0.004"), ("terminal", "K", "0.005"), ("terminal", "R", "0.006"),
                  ("terminal", "Z", "0.007"), ("terminal", "G", "0.008")]
        events = [{"call_id": str(i), "state": "completed", "identity": {"stage": stage, "arm": arm}, "cost_usd": cost,
                   "usage": {key: 1 for key in ("input_tokens", "uncached_input", "cached_input", "cache_write", "output", "reasoning")}}
                  for i, (stage, arm, cost) in enumerate(stages)]
        result = resources(events, [])
        self.assertEqual(result["shared_experiment_cost_usd"], "0.036")
        projections = result["standalone_policy_projections"]
        self.assertEqual(projections["K"]["known_projected_usd"], "0.011")
        self.assertEqual(projections["R"]["known_projected_usd"], "0.012")
        self.assertEqual(projections["Z"]["known_projected_usd"], "0.010")
        self.assertEqual(projections["G"]["known_projected_usd"], "0.015")
        self.assertFalse(result["sum_projections_is_actual_spend"])

    def test_analysis_rejects_duplicate_tasks_wrong_types_and_primary_slot_mismatch(self):
        row = outcome("t1", [0, 0], [1, 1])
        with self.assertRaises(ValueError):
            analyze([row, deepcopy(row)])
        for invalid in (True, 0.5, -1):
            changed = deepcopy(row)
            changed["grades"]["R"][0] = invalid
            with self.assertRaises(ValueError):
                analyze([changed])
        row["scheduled_arms"] = ["R"]
        with self.assertRaises(ValueError):
            validate_rows([row])
