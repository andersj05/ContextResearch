"""Scientific design checks for the unfunded, offline pilot schedule."""

from collections import defaultdict
from fractions import Fraction
import unittest
from unittest.mock import patch

from artifact_workflow import run_episode
from pilot_plan import ARMS, build_plan, calibration
from recovery_frontier import executable_policy
from run_recovery_frontier import route_fixtures, scenarios


class PilotPlanTests(unittest.TestCase):
    def test_calibration_costs_are_attained_through_complete_environment(self):
        for cell in calibration():
            config = scenarios()[cell["scenario"]]
            fixtures = tuple(route_fixtures(config))
            self.assertEqual(len(fixtures), 30)
            for inspect, key in ((False, "no_inspection_extra_cost"), (True, "inspection_extra_cost")):
                policy = executable_policy(config, inspect=inspect, recover=True)
                results = [run_episode(config, f, policy) for f in fixtures]
                self.assertTrue(all(r.success for r in results))
                observed = Fraction(sum(r.cost_units - 7 - config.delay for r in results), len(results))
                self.assertEqual(observed, Fraction(cell[key]))

    def test_positive_null_and_adverse_controls_survive(self):
        cells = {row["scenario"]: row for row in calibration()}
        self.assertEqual(cells["costly_recovery"]["optimal_decisions"], ["inspect"])
        self.assertEqual(cells["revision_costly_recovery"]["optimal_decisions"], ["inspect"])
        for name in ("cheap_recovery", "revision_cheap_recovery", "ample_parent", "small_child"):
            self.assertEqual(cells[name]["optimal_decisions"], ["skip"])
        adverse = cells["small_child"]
        self.assertGreater(Fraction(adverse["p1"]), Fraction(adverse["p0"]))
        self.assertGreater(Fraction(adverse["inspection_minus_skip_cost"]), 0)
        self.assertEqual(cells["ample_parent"]["p0"], cells["ample_parent"]["p1"])

    def test_heldout_routes_are_disjoint_and_arms_are_paired(self):
        plan = build_plan()
        assignments = plan["fixture_assignments"]
        self.assertEqual(len({a["route_index"] for a in assignments}), 5)
        self.assertTrue(all(0 <= a["route_index"] < 30 for a in assignments))
        groups = defaultdict(list)
        for episode in plan["stage_b_episodes"]:
            groups[episode["pair_id"]].append(episode)
        self.assertEqual(len(groups), 60)
        for paired in groups.values():
            self.assertEqual({e["arm"] for e in paired}, set(ARMS))
            self.assertEqual(len({(e["split"], e["family"], e["route_index"], e["scenario"], e["render_mode"]) for e in paired}), 1)
        # Every same-route comparison across regimes/renderings has identical pairing.
        for assignment in assignments:
            family_episodes = [e for e in plan["stage_b_episodes"] if e["family"] == assignment["family"]]
            self.assertEqual(len(family_episodes), 36)
            self.assertEqual({e["route_index"] for e in family_episodes}, {assignment["route_index"]})

    def test_request_ceiling_and_development_precedence(self):
        plan = build_plan()
        episodes = {e["episode_id"]: e for e in plan["stage_b_episodes"]}
        self.assertEqual(len(episodes), 180)
        order = plan["stage_b_execution_order"]
        self.assertEqual(len(order), len(set(order)))
        self.assertEqual(set(order), set(episodes))
        self.assertTrue(all(episodes[e]["split"] == "development" for e in order[:36]))
        self.assertTrue(all(episodes[e]["split"] == "heldout" for e in order[36:]))
        # 12 decisions + 180*2 boundary calls + 60 selective decisions.
        self.assertEqual(plan["counts"]["total_maximum_model_requests"], 432)
        self.assertEqual(sum(e["maximum_model_requests"] for e in episodes.values()), 420)

    def test_sample_composition_does_not_inherit_population_preferences(self):
        plan = build_plan()
        rows = {r["scenario"]: r for r in plan["sampled_scripted_reference"] if r["split"] == "heldout"}
        population = {r["scenario"]: r for r in plan["calibration"]}
        for name in ("costly_recovery", "revision_cheap_recovery"):
            self.assertEqual(rows[name]["fixture_count"], 4)
            self.assertEqual(rows[name]["skip_mean_extra_cost"], "1")
            self.assertEqual(rows[name]["inspect_mean_extra_cost"], "1")
            self.assertNotEqual(population[name]["inspection_minus_skip_cost"], "0")

    def test_reliable_recovery_masks_forgetting_in_all_pilot_regimes(self):
        # Empty selection is a valid but maximally forgetful compactor. Use the
        # actual tool state machine at unchanged capacities and costs.
        for cell in calibration():
            config = scenarios()[cell["scenario"]]
            policy = executable_policy(config, inspect=False, recover=True)
            with patch("artifact_workflow.compact", return_value=()):
                results = [run_episode(config, f, policy) for f in route_fixtures(config)]
            self.assertEqual(len(results), 30)
            for result in results:
                self.assertTrue(result.success)
                self.assertTrue(result.recovery_attempted)
                self.assertTrue(all(c["retained_records"] == 0 for c in result.compactions))
                self.assertEqual(result.cost_units, 7 + config.delay + config.recovery_cost)


if __name__ == "__main__":
    unittest.main()
