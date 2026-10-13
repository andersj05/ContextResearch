"""Independent contract probes, using public packets rather than task witnesses.

These are deliberately manufactured engineering fixtures, never model evidence.
They target symmetric information loss that a simple K/R equality test can miss.
"""
from copy import deepcopy
import json
import unittest
from unittest.mock import patch

from experiments.dependency_memory.rollback_checkpoint_v7 import contexts, engine
from experiments.dependency_memory.rollback_checkpoint_v7.analysis import analyze
from experiments.dependency_memory.rollback_checkpoint_v7.common import wire
from experiments.dependency_memory.rollback_checkpoint_v7.prepare import generate
from experiments.dependency_memory.rollback_development_v5_continuation.accounting import CallUnknown
from experiments.dependency_memory.rollback_pilot.subscription.accounting import Usage
from experiments.dependency_memory.rollback_pilot.subscription.transport import Response


def public_balances(visible):
    """Independent sorted formulation using only the actual public request."""
    records = [record for packet in visible["public_dossier"]
               for record in packet["requirements"]]
    picked = {}
    for record in sorted(records, key=lambda row: (row["revision"], row["sequence"]),
                         reverse=True):
        picked.setdefault(record["tx"], record)
    accounts = visible["task"]["contract"]["account_count"]
    return [sum(record["amount"] * ((record["destination"] == account)
                                   - (record["source"] == account))
                for record in picked.values() if not record["void"])
            for account in range(accounts)]


class PublicFixture:
    def __init__(self, failure_stage, *, copy_failed_candidate=False, unknown_arm=None,
                 unknown_lesson=False):
        self.failure_stage = failure_stage
        self.copy_failed_candidate = copy_failed_candidate
        self.unknown_arm = unknown_arm
        self.unknown_lesson = unknown_lesson
        self.requests, self.answers = [], []

    def __call__(self, identity, request):
        visible = json.loads(request.data()["messages"][1]["content"])
        self.requests.append((identity, deepcopy(visible)))
        if identity.arm == self.unknown_arm or (identity.stage == "lesson" and self.unknown_lesson):
            raise CallUnknown("deliberately unavailable fixture response")
        if identity.stage == "lesson":
            retained = [wire(visible["trial"][0]["action"]["candidate"])] if self.copy_failed_candidate else []
            answer = {"established": [wire(visible["feedback"])],
                      "retained_observations": retained, "uncertainties": []}
        else:
            values = public_balances(visible)
            if identity.arm == "prefix" and visible["current_stage"] == self.failure_stage:
                # A wrong, balanced answer exercises the checker beyond sum-zero.
                values[0] += 1
                values[1] -= 1
            answer = {"status": "candidate", "candidate": {"values": values, "order": [], "files": []},
                      "note": "Explicit offline public-packet fixture."}
        self.answers.append((identity, deepcopy(answer)))
        return Response(wire(answer), Usage(1, 0, 1, 0),
                        {"thread_id": "contract-review-" + identity.key}, False)


class IndependentContractReview(unittest.TestCase):
    def task(self):
        return generate(split="fixture", seed=2026101299, replicates=1)[0]

    def prefix(self, stage=2, **kwargs):
        task = self.task()
        actor = PublicFixture(stage, **kwargs)
        result = engine.run_prefix(task, actor)
        self.assertTrue(result["eligible"])
        return task, actor, result

    def test_stage_two_and_three_restore_every_packet_and_successful_record(self):
        for stage in (2, 3):
            with self.subTest(failure_stage=stage):
                task, actor, prefix = self.prefix(stage)
                expected_packets = [{"stage": index + 1, "stage_count": 3, **deepcopy(packet)}
                                    for index, packet in enumerate(task["stages"][:stage])]
                successful_answers = [answer for identity, answer in actor.answers
                                      if identity.stage == "action" and identity.step < stage]
                payloads = {}
                for arm in ("K", "R"):
                    state = engine.continuation_state(task, arm, prefix)
                    payload = contexts.render(task, state).data()
                    visible = json.loads(payload["messages"][1]["content"])
                    self.assertEqual(visible["public_dossier"], expected_packets)
                    self.assertEqual([record["action"] for record in visible["checkpoint"]["records"]],
                                     successful_answers)
                    self.assertEqual(visible["checkpoint"]["artifact"], successful_answers[-1]["candidate"])
                    self.assertEqual(visible["remaining_actions"], 4 - stage)
                    self.assertEqual(visible["current_stage"], stage)
                    self.assertEqual(len(visible["trial"]), int(arm == "K"))
                    visible["trial"] = []
                    payload["messages"][1]["content"] = wire(visible)
                    payloads[arm] = wire(payload)
                self.assertEqual(payloads["K"], payloads["R"])

    def test_lesson_may_retain_failed_values_and_forks_are_independent(self):
        task, actor, prefix = self.prefix(copy_failed_candidate=True)
        original = deepcopy(prefix)
        states = {arm: engine.continuation_state(task, arm, prefix) for arm in ("K", "R")}
        copied = wire(prefix["trial"][0]["action"]["candidate"])
        self.assertEqual(states["R"]["trial"], [])
        self.assertIn(copied, states["R"]["lesson"]["retained_observations"])
        states["R"]["lesson"]["retained_observations"].clear()
        states["R"]["public_dossier"][0]["requirements"].clear()
        self.assertEqual(prefix, original)
        self.assertIn(copied, states["K"]["lesson"]["retained_observations"])
        for arm in ("R", "K"):
            self.assertEqual(engine.run_continuation(task, arm, prefix, actor)["score"], 1)
        self.assertEqual(prefix, original)
        self.assertEqual(sum(identity.stage == "lesson" for identity, _ in actor.requests), 1)

    def test_symmetric_render_omissions_cannot_pass_pair_gate(self):
        task, _, prefix = self.prefix()
        original_actor_state = contexts.actor_state

        def missing_packet(visible):
            visible["public_dossier"].pop(0)

        def wrong_checkpoint(visible):
            visible["checkpoint"]["artifact"]["values"][0] += 100

        def missing_record(visible):
            visible["checkpoint"]["records"].clear()

        def extra_budget(visible):
            visible["remaining_actions"] += 1

        for mutation in (missing_packet, wrong_checkpoint, missing_record, extra_budget):
            def corrupt(task, state):
                visible = original_actor_state(task, state)
                mutation(visible)
                return visible
            with self.subTest(mutation=mutation.__name__), patch.object(contexts, "actor_state", corrupt):
                # Both arms receive the same corruption: between-arm equality
                # alone is insufficient to establish checkpoint restoration.
                with self.assertRaisesRegex(engine.PairContractError, "pair_contract"):
                    engine.pair_contract(task, prefix)

    def test_pair_gate_failure_escapes_prefix_policy_failure_handling(self):
        task = self.task()
        actor = PublicFixture(2)
        original_actor_state = contexts.actor_state

        def corrupt_only_completed_fork(task, state):
            visible = original_actor_state(task, state)
            if state["lesson"] is not None:
                visible["public_dossier"].pop(0)
            return visible

        with patch.object(contexts, "actor_state", corrupt_only_completed_fork):
            with self.assertRaisesRegex(engine.PairContractError, "pair_contract"):
                engine.run_prefix(task, actor)

    def test_unknown_in_one_arm_does_not_remove_its_paired_observation(self):
        task, _, prefix = self.prefix()
        unknown = PublicFixture(2, unknown_arm="R")
        result = engine.run_continuation(task, "R", prefix, unknown)
        self.assertIsNone(result["score"])
        self.assertEqual(result["disposition"], "unknown_dispatch")
        healthy = PublicFixture(2)
        self.assertEqual(engine.run_continuation(task, "K", prefix, healthy)["score"], 1)
        self.assertEqual(len(unknown.requests), 1)

    def test_shared_writer_unknown_prevents_both_continuations(self):
        task = self.task()
        actor = PublicFixture(2, unknown_lesson=True)
        prefix = engine.run_prefix(task, actor)
        self.assertFalse(prefix["eligible"])
        self.assertEqual(prefix["reason"], "unknown_dispatch")
        calls_before = len(actor.requests)
        for arm in ("K", "R"):
            result = engine.run_continuation(task, arm, prefix, actor)
            self.assertIsNone(result["score"])
            self.assertEqual(result["disposition"], "not_eligible:unknown_dispatch")
        self.assertEqual(len(actor.requests), calls_before)

    def test_conditional_denominator_retains_missing_pairs_and_excludes_initial_success(self):
        tasks = [{"task_id": f"fixture-{index}"} for index in range(4)]
        jobs = []
        scores = [(1, 0), (None, 1), (None, None), (None, None)]  # R, K
        for index, task in enumerate(tasks):
            task_id = task["task_id"]
            eligible = index != 3
            jobs.append({"job": {"task_id": task_id, "arm": "prefix"},
                         "result": {"eligible": eligible, "reason": "first_public_mismatch" if eligible else "all_stages_passed",
                                    "state": {"stage": 1}}})
            for arm, score in zip(("R", "K"), scores[index]):
                jobs.append({"job": {"task_id": task_id, "arm": arm},
                             "result": {"score": score, "disposition": "unknown" if score is None else "observed"}})
        report = analyze(tasks, {"jobs": jobs}, {"calls": []},
                         {"minimum_complete_pairs_for_descriptive_interval": 6, "seed": 99, "split": "fixture"},
                         simulated=True)
        self.assertEqual(report["selected_tasks"], 4)
        self.assertEqual(report["eligible_prefixes"], 3)
        self.assertEqual(report["primary"]["scheduled_pairs"], 3)
        self.assertEqual(report["primary"]["complete_pairs"], 1)
        self.assertEqual(report["primary"]["mean_difference"], 1)
        self.assertEqual(report["primary"]["fixed_denominator_bounds"], [-1 / 3, 2 / 3])
        self.assertEqual(report["arms"]["R"]["missing"], 2)
        self.assertEqual(report["arms"]["K"]["missing"], 1)
        self.assertIsNone(report["primary"]["descriptive_task_bootstrap_95"])
        self.assertIsNone(report["primary"]["confirmatory_p"])


if __name__ == "__main__":
    unittest.main()
