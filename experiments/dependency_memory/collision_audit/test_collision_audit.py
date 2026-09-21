"""Scientific checks, including explicit policy enumeration independent of DP."""
from copy import deepcopy
from itertools import combinations, product
from math import inf
import unittest

from .engine import (Problem, Solver, audit, minimum_repair_partition,
                     replay_policy, verify_impossibility_atom, verify_obstruction)
from .fixtures import binary_receipts, compatibility, diagnostic_specs, rollback, shards


def explicit_depth_two_behaviors():
    """All <=2-query binary decision trees for two specified probes and 3 answers.

    Store only (answer in each world, path cost in each world). This enumerates
    controllers forward, independent of accepted-action sets and the optimizer.
    """
    observations = [(0, 1, 1), (1, 0, 1)]
    leaves = {((answer,) * 3, (0,) * 3) for answer in "ABC"}
    behaviors = leaves
    for _ in range(2):
        expanded = set(leaves)
        for observation in observations:
            for left, right in product(behaviors, repeat=2):
                results = [([left, right][observation[w]][0][w],
                            1 + [left, right][observation[w]][1][w]) for w in range(3)]
                expanded.add((tuple(x[0] for x in results), tuple(x[1] for x in results)))
        behaviors = expanded
    return behaviors


def partitions(items):
    if not items:
        yield ()
        return
    first, rest = items[0], items[1:]
    for partition in partitions(rest):
        yield ((first,),) + partition
        for j in range(len(partition)):
            yield partition[:j] + ((first,) + partition[j],) + partition[j + 1:]


class CollisionAuditTests(unittest.TestCase):
    def test_every_pair_can_pass_while_full_group_fails(self):
        p = Problem(compatibility())
        s = Solver(p, p.tasks[0])
        self.assertEqual([s.optimum(pair)[0] for pair in combinations(range(3), 2)], [0, 0, 0])
        self.assertEqual(s.optimum((0, 1, 2))[0], 1)
        self.assertEqual(s.smallest_obstruction((0, 1, 2), 0), (0, 1, 2))
        out = audit(p)
        self.assertEqual(out["repair"]["extra_fixed_bits"], 1)
        self.assertTrue(out["tasks"][0]["cells"][0]["all_pairs_within_budget"])

    def test_forward_enumeration_all_343_accepted_action_tables(self):
        behaviors = explicit_depth_two_behaviors()
        answer_sets = [set(c) for size in range(1, 4) for c in combinations("ABC", size)]
        spec = compatibility()
        spec["tools"] = [
            {"name": "q0", "cost": 1, "observations": {"w0": 0, "w1": 1, "w2": 1}},
            {"name": "q1", "cost": 1, "observations": {"w0": 1, "w1": 0, "w2": 1}}]
        for accepted in product(answer_sets, repeat=3):
            spec["tasks"][0]["accepted"] = {f"w{i}": sorted(a) for i, a in enumerate(accepted)}
            p = Problem(spec)
            s = Solver(p, p.tasks[0])
            for size in range(1, 4):
                for cell in combinations(range(3), size):
                    exact = min(max(costs[i] for i in cell) for answers, costs in behaviors
                                if all(answers[i] in accepted[i] for i in cell))
                    cost, policy = s.optimum(cell)
                    self.assertEqual(cost, exact)
                    replay_policy(p, p.tasks[0], cell, policy)
                    if cost:
                        verify_obstruction(p, p.tasks[0], cell, cost - 1, s.obstruction(cell, cost - 1))
            for budget in (0, 1, 2):
                brute_partitions = [parts for parts in partitions((0, 1, 2))
                                    if all(any(all(answers[i] in accepted[i] and costs[i] <= budget
                                                   for i in cell) for answers, costs in behaviors)
                                           for cell in parts)]
                self.assertEqual(len(minimum_repair_partition((0, 1, 2), [s], budget)),
                                 min(map(len, brute_partitions)))

    def test_adaptive_recovery_is_strictly_cheaper_than_fixed_batch(self):
        p = Problem(shards())
        s = Solver(p, p.tasks[0])
        cell = tuple(range(8))
        self.assertEqual(s.optimum(cell)[0], 2)
        self.assertEqual(s.nonadaptive_cost(cell), 4)
        policy = s.optimum(cell)[1]
        self.assertEqual(policy["tool"], "read_directory")
        self.assertEqual({r["cost"] for r in replay_policy(p, p.tasks[0], cell, policy)}, {2})
        self.assertEqual(audit(p)["repair"]["extra_messages"], 2)

    def test_binary_calibration_matches_independent_leaf_count(self):
        # A b-query binary tree has <=2**b leaves; each retained state covers
        # <=2**b of the eight distinct required answers. Sending the remaining
        # 3-b bits attains the lower bound. No optimizer is used in this formula.
        for budget in range(4):
            p = Problem(binary_receipts(budget))
            result = audit(p)
            self.assertEqual(result["repair"]["extra_messages"], 2 ** (3 - budget))
            self.assertEqual(result["repair"]["extra_fixed_bits"], 3 - budget)

    def test_current_recovery_is_not_original_version_recovery(self):
        p = Problem(rollback(False))
        self.assertEqual(Solver(p, p.tasks[0]).optimum((0, 1))[0], 0)
        self.assertEqual(Solver(p, p.tasks[1]).optimum((0, 1))[0], inf)
        self.assertEqual(audit(p)["shortest_failing_declared_trace"]["task"], "original_release")
        with_archive = Problem(rollback(True))
        self.assertEqual(Solver(with_archive, with_archive.tasks[1]).optimum((0, 1))[0], 3)

    def test_infinite_cost_has_a_budget_independent_certificate(self):
        p = Problem(rollback(False))
        s = Solver(p, p.tasks[1])
        atom = s.impossibility_atom((0, 1))
        self.assertTrue(verify_impossibility_atom(p, p.tasks[1], (0, 1), atom))
        archive = Problem(rollback(True))
        with self.assertRaises(ValueError):
            verify_impossibility_atom(archive, archive.tasks[1], (0, 1), atom)

    def test_repair_cannot_know_which_future_task_is_coming(self):
        spec = binary_receipts(0)
        spec["tasks"] = [{"name": f"ask-bit-{bit}", "trace": [f"Reveal query for bit {bit}."],
                          "accepted": {f"w{i}": [str((i >> bit) & 1)] for i in range(8)}}
                         for bit in range(3)]
        p = Problem(spec)
        solvers = [Solver(p, task) for task in p.tasks]
        for solver in solvers:
            self.assertEqual(len(minimum_repair_partition(tuple(range(8)), [solver], 0)), 2)
        self.assertEqual(len(minimum_repair_partition(tuple(range(8)), solvers, 0)), 8)

    def test_negative_controls_do_not_demand_extra_memory(self):
        controls = {s["name"]: s for s in diagnostic_specs()}
        for name in ("harmless_lost_detail", "public_evidence_control",
                     "affordable_archive_control", "adaptive_recovery_budget_two"):
            result = audit(Problem(controls[name]))
            self.assertEqual(result["repair"]["extra_fixed_bits"], 0)
            self.assertIsNone(result["shortest_failing_declared_trace"])

    def test_all_repairs_are_jointly_valid_before_task_reveal(self):
        for spec in diagnostic_specs():
            p = Problem(spec)
            result = audit(p)
            for original, groups in zip(p.cells, result["repair"]["partitions"]):
                self.assertEqual(sorted(i for group in groups for i in group), list(original))
                for task in p.tasks:
                    s = Solver(p, task)
                    for group in groups:
                        cost, policy = s.optimum(tuple(group))
                        self.assertLessEqual(cost, p.budget)
                        replay_policy(p, task, group, policy)

    def test_lower_proof_rejects_tampering_and_omitted_tools(self):
        p = Problem(shards())
        s = Solver(p, p.tasks[0])
        proof = s.obstruction(tuple(range(8)), 1)
        self.assertGreater(verify_obstruction(p, p.tasks[0], tuple(range(8)), 1, proof), 1)
        variants = []
        bad = deepcopy(proof)
        del bad["nodes"][bad["root"]]["tools"]["read_directory"]
        variants.append(bad)
        bad = deepcopy(proof)
        bad["nodes"][bad["root"]]["answers"]["receipt-0"] = 0
        variants.append(bad)
        bad = deepcopy(proof)
        bad["nodes"][bad["root"]]["tools"]["read_directory"]["observation"] = "invented"
        variants.append(bad)
        bad = deepcopy(proof)
        bad["nodes"][bad["root"]]["budget"] = 0
        variants.append(bad)
        for bad in variants:
            with self.assertRaises(ValueError):
                verify_obstruction(p, p.tasks[0], tuple(range(8)), 1, bad)

    def test_nonrefining_tools_cannot_manufacture_information(self):
        p = Problem(rollback(False))
        s = Solver(p, p.tasks[1])
        for budget in (0, 1, 5):
            proof = s.obstruction((0, 1), budget)
            verify_obstruction(p, p.tasks[1], (0, 1), budget, proof)
        self.assertEqual(s.optimum((0, 1))[0], inf)

    def test_proof_size_does_not_grow_with_a_useless_query_budget(self):
        p = Problem(rollback(False, budget=1000000))
        result = audit(p)
        cell = result["tasks"][1]["cells"][0]
        self.assertEqual(len(cell["lower_bound_proof"]["nodes"]), 1)
        self.assertIsNone(cell["minimum_worst_case_recovery_cost"])

    def test_exact_channels_control_collision_membership(self):
        spec = compatibility()
        spec["worlds"][0]["retained"]["note"] = "AB"
        result = audit(Problem(spec))
        self.assertEqual(result["repair"]["extra_fixed_bits"], 0)
        self.assertEqual(len(result["tasks"][0]["cells"]), 2)

    def test_tool_and_observation_renaming_preserves_cost(self):
        spec = shards()
        for i, tool in enumerate(spec["tools"]):
            tool["name"] = f"renamed-{i}"
            tool["observations"] = {w: {"opaque": value} for w, value in tool["observations"].items()}
        spec["tools"].reverse()
        result = audit(Problem(spec))
        self.assertEqual(result["tasks"][0]["cells"][0]["minimum_worst_case_recovery_cost"], 2)

    def test_rejects_undeclared_encoder_access_and_nonpositive_costs(self):
        spec = compatibility()
        spec["worlds"][1]["history"] = spec["worlds"][0]["history"]
        with self.assertRaises(ValueError):
            Problem(spec)
        for cost in (0, -1, True, 0.5):
            spec = compatibility()
            spec["tools"][0]["cost"] = cost
            with self.assertRaises(ValueError):
                Problem(spec)


if __name__ == "__main__":
    unittest.main()
