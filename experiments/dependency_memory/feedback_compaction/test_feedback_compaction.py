"""Scientific invariants and independent forward checks for feedback diagnostics."""
from copy import deepcopy
from dataclasses import replace
from itertools import combinations
from math import inf
import unittest

from experiments.dependency_memory.artifact_workflow import Action, Receipt
from experiments.dependency_memory.collision_audit.engine import (
    Solver, verify_obstruction,
)
from experiments.dependency_memory.feedback_compaction.feedback import (
    Verifier, certificate_replays, learn, successful_candidate,
)
from experiments.dependency_memory.feedback_compaction.run import feedback_channel_check
from experiments.dependency_memory.feedback_compaction.workflow import Candidate, Contract, KEYS, Workflow


def forward_value(problem, cell):
    """Enumerate all useful legal controllers (zero or one archive call).

    No recurrence or Solver helper is used. Repeating the sole deterministic
    archive read cannot change any observation, and the environment rejects it.
    """
    accepted = problem.tasks[0].accepted
    actions = set().union(*accepted)
    if any(all(a in accepted[i] for i in cell) for a in actions):
        return 0
    if not problem.tools:
        return inf
    tool = problem.tools[0]
    branches = {}
    for i in cell:
        branches.setdefault(tool.observations[i], []).append(i)
    if all(any(all(a in accepted[i] for i in group) for a in actions)
           for group in branches.values()):
        return tool.cost
    return inf


class FeedbackTests(unittest.TestCase):
    def test_every_catalog_answer_is_execution_graded(self):
        w = Workflow()
        for route in range(6):
            p = w.problem(w.initial, route)
            self.assertTrue(all(len(a) == 1 for a in p.tasks[0].accepted))
            for world, bits in enumerate(w.bits):
                env = w.checkpoint(w.initial, bits, w.routes[route])[0]
                self.assertFalse(deepcopy(env).step(Action("submit", None)).success)
                garbage = Receipt(w.routes[route][1], 2, "not-in-the-catalog")
                self.assertFalse(deepcopy(env).step(Action("submit", garbage)).success)

    def test_forward_controllers_match_optimizer_for_all_subcells(self):
        checks = 0
        for recovery in (False, True):
            w = Workflow(Contract(recovery=recovery))
            for candidate in w.candidates:
                for route in range(6):
                    p = w.problem(candidate, route)
                    solver = Solver(p, p.tasks[0])
                    # Every nonempty subset of every actually accessible cell.
                    for cell in p.cells:
                        for size in range(1, len(cell) + 1):
                            for group in combinations(cell, size):
                                self.assertEqual(solver.optimum(group)[0], forward_value(p, group))
                                checks += 1
        # Per route: three schemas retain the higher key (four size-two
        # cells), four omit it (two size-four cells), under two tool settings.
        self.assertEqual(checks, 2 * 6 * (3 * 4 * 3 + 4 * 2 * 15))

    def test_accumulated_feedback_preserves_prior_constraints(self):
        w = Workflow()
        result = learn(w)
        self.assertEqual(result["status"], "certified")
        self.assertEqual(result["audit_calls"], 3)
        candidate = successful_candidate(w, result)
        self.assertEqual(candidate.fields, KEYS[1:])
        self.assertEqual(len({r["candidate"] for r in result["history"]}), 3)
        self.assertEqual(len(certificate_replays(w, candidate)), 48)

    def test_latest_only_repair_cycles(self):
        result = learn(Workflow(), "last_only")
        self.assertEqual(result["status"], "cycle")
        self.assertEqual([row["fields"] for row in result["history"]],
                         [["job-0", "job-1"], ["job-2"], ["job-1"]])

    def test_strong_baseline_matches_with_less_synthesis(self):
        w = Workflow()
        fixed = learn(w, "critical_fields")
        repaired = learn(w)
        self.assertEqual(fixed["candidate"], repaired["candidate"])
        self.assertLess(fixed["audit_calls"], repaired["audit_calls"])
        self.assertEqual(sum(r["success"] for r in w.execution(w.initial)), 32)
        self.assertEqual(sum(r["success"] for r in w.execution(w.critical_fields)), 48)

    def test_complete_failure_feedback_is_sound_for_every_candidate(self):
        w = Workflow()
        v = Verifier(w)
        for current in w.candidates:
            witness = v.first_failure(current)
            if witness is None:
                continue
            self.assertTrue(v.merges(current, witness))
            for candidate in w.candidates:
                if v.merges(candidate, witness):
                    p = v.problem(candidate, witness.route)
                    self.assertGreater(forward_value(p, witness.worlds), p.budget)

    def test_proof_tampering_is_rejected(self):
        w = Workflow()
        v = Verifier(w)
        witness = v.first_failure(w.initial)
        proof = deepcopy(witness.proof)
        node = proof["nodes"][proof["root"]]
        node["answers"].clear()
        with self.assertRaises(ValueError):
            v.merges(w.initial, replace(witness, proof=proof))

    def test_feedback_is_invalid_after_budget_change(self):
        old = Workflow(Contract(recovery=True, recovery_budget=2))
        witness = Verifier(old).first_failure(old.initial)
        new = Workflow(Contract(recovery=True, recovery_budget=3))
        with self.assertRaises(ValueError):
            Verifier(new).merges(new.initial, witness)

    def test_binding_child_cannot_be_fixed_by_parent_only_in_this_family(self):
        w = Workflow(Contract(parent_capacity=3, child_capacity=1))
        self.assertEqual(learn(w)["status"], "exhausted_family")
        # Independent reasoning: on pair (0,1), keeping 1 drops new 0; dropping
        # 1 cannot answer target 1. Neither public target is known at selection.
        for c in w.candidates:
            self.assertLess(sum(r["success"] for r in w.execution(c)), 48)

    def test_early_target_repairs_timing_with_one_child_record(self):
        w = Workflow(Contract(child_capacity=1, early_target=True))
        result = learn(w)
        self.assertEqual(result["status"], "certified")
        c = successful_candidate(w, result)
        self.assertTrue(all(r["success"] and r["child_records"] == 1 for r in w.execution(c)))

    def test_parent_and_child_do_not_see_late_target(self):
        w = Workflow()
        for bits in w.bits:
            for pair in combinations(KEYS, 2):
                first = w.checkpoint(w.initial, bits, (pair, pair[0]))
                second = w.checkpoint(w.initial, bits, (pair, pair[1]))
                self.assertEqual(first[2:4], second[2:4])
        # Parent is selected before even the pair becomes known.
        parents = {w.checkpoint(w.initial, (0, 1, 0), r)[2] for r in w.routes}
        self.assertEqual(len(parents), 1)

    def test_capacity_and_recovery_sweep_has_independent_feasibility_rule(self):
        for parent in range(4):
            for child in range(3):
                for recovery, budget in ((False, 0), (True, 0), (True, 2), (True, 3)):
                    w = Workflow(Contract(parent_capacity=parent, child_capacity=child,
                                          recovery=recovery, recovery_budget=budget))
                    # Workflow algebra: higher key is either 1 or 2. Both must
                    # survive parent; both refreshed and unrefreshed candidate
                    # records must survive child, unless archive cost is allowed.
                    feasible = (recovery and budget >= 3) or (parent >= 2 and child >= 2)
                    result = learn(w)
                    self.assertEqual(result["status"] == "certified", feasible)
                    self.assertLessEqual(result["audit_calls"], len(w.candidates))

    def test_runtime_cost_includes_recovery_and_failed_runs(self):
        for budget in (0, 2, 3):
            w = Workflow(Contract(parent_capacity=0, child_capacity=0,
                                  recovery=True, recovery_budget=budget))
            rows = w.execution(w.initial)
            self.assertEqual(len(rows), 48)
            self.assertTrue(all(r["environment_units"] == 9 + r["recovery_units"] for r in rows))
            self.assertEqual(sum(r["success"] for r in rows), 48 if budget == 3 else 0)
            self.assertEqual(sum(r["recovery_units"] for r in rows), 144 if budget == 3 else 0)

    def test_unprobed_continuation_is_not_certified(self):
        w = Workflow()
        result = learn(w, routes=(0, 1))
        candidate = successful_candidate(w, result)
        self.assertIsNotNone(candidate)
        self.assertIsNone(Verifier(w, routes=(0, 1)).first_failure(candidate))
        self.assertIsNotNone(Verifier(w, routes=(2, 3, 4, 5)).first_failure(candidate))

    def test_identifier_channel_is_two_bits_in_one_tagged_record(self):
        w = Workflow(Contract(child_capacity=1))
        candidate = Candidate(KEYS[1:], "coded")
        self.assertIsNone(Verifier(w).first_failure(candidate))
        for route in range(6):
            self.assertEqual(len(w.problem(candidate, route).cells), 4)
        self.assertEqual(sum(r["success"] for r in w.execution(candidate)), 24)
        self.assertEqual(sum(r["success"] for r in w.execution(candidate, coded_decode=True)), 48)
        self.assertEqual(len(certificate_replays(w, candidate)), 48)

    def test_late_value_feedback_is_an_extra_channel(self):
        result = feedback_channel_check()
        self.assertEqual(result["maximum_correct_without_new_channel"], 4)
        self.assertEqual(result["correct_with_true_missing_value_feedback"], 8)

    def test_schema_replays_on_different_payloads_without_resynthesis(self):
        development = Workflow()
        result = learn(development)
        candidate = successful_candidate(development, result)
        fresh = Workflow(Contract(salt="disjoint-payload-control-v1"))
        self.assertNotEqual(development.fixture((0, 0, 0), KEYS[:2], KEYS[0]).receipts,
                            fresh.fixture((0, 0, 0), KEYS[:2], KEYS[0]).receipts)
        self.assertEqual(sum(r["success"] for r in fresh.execution(candidate)), 48)

    def test_invalid_contracts_and_round_limit(self):
        with self.assertRaises(ValueError):
            Contract(parent_capacity=4)
        with self.assertRaises(ValueError):
            Verifier(Workflow(), routes=())
        self.assertEqual(learn(Workflow(), limit=1)["status"], "round_limit")


if __name__ == "__main__":
    unittest.main()
