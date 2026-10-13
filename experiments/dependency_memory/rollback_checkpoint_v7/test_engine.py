"""Independent channel and boundary checks; scripted outputs are not model evidence."""
from copy import deepcopy
import json
from types import SimpleNamespace
import unittest
from unittest.mock import patch

from experiments.dependency_memory.rollback_checkpoint_v7.common import STUDY, wire
from experiments.dependency_memory.rollback_checkpoint_v7.contexts import actor_state, render, fits
from experiments.dependency_memory.rollback_checkpoint_v7.engine import (initial_state, continuation_state, pair_contract, run_prefix,
                     run_continuation, PairContractError)
from experiments.dependency_memory.rollback_challenge_v6.tasks import generate, candidate
from experiments.dependency_memory.rollback_development_v5.accounting import Identity, Stopped
from experiments.dependency_memory.rollback_development_v5_continuation.accounting import CallUnknown
from experiments.dependency_memory.rollback_pilot.subscription import profile


def make_task(actions=4, stages=3):
    task = generate(split="fixture", seed=202610120713, cells=[("revision_ledger", 2)],
                    replicates=1, stages=stages, actions=actions, require_candidates=True,
                    ledger_profile="intermediate")[0]
    task["task_id"] = "v7-channel-fixture"
    return task


def visible(request):
    return json.loads(request.data()["messages"][1]["content"])


def independent_balances(task, stage):
    """Group then sort records, independently of v6's streaming maximum map."""
    records = [r for p in task["stages"][:stage] for r in p["requirements"]]
    balances = list(task["contract"]["opening_balances"])
    for tx in sorted({r["tx"] for r in records}):
        row = sorted((r for r in records if r["tx"] == tx),
                     key=lambda r: (r["revision"], r["sequence"]))[-1]
        if not row["void"]:
            balances[row["source"]] -= row["amount"]
            balances[row["destination"]] += row["amount"]
    return candidate(balances)


class Scripted:
    """Offline deterministic responses; wrong only at explicitly selected steps."""
    def __init__(self, task, failure_step=2, continuation_failures=()):
        self.task = task
        self.failure_step = failure_step
        self.continuation_failures = set(continuation_failures)
        self.calls = []

    def __call__(self, identity, request):
        self.calls.append((identity, request))
        data = visible(request)
        if identity.stage == "lesson":
            value = {"established": ["The candidate violates the named public balance check."],
                     "retained_observations": [], "uncertainties": ["Other account balances were not certified."]}
        else:
            wrong = ((identity.arm == "prefix" and identity.step == self.failure_step)
                     or (identity.arm != "prefix" and identity.step in self.continuation_failures))
            values = independent_balances(self.task, data["current_stage"])
            if wrong:
                values["values"][0] += 1
            value = {"status": "candidate", "candidate": values, "note": "Offline scripted candidate."}
        return SimpleNamespace(text=wire(value), capped=False)


class CheckpointEngineTests(unittest.TestCase):
    def setUp(self):
        self.task = make_task()

    def prefix(self, step=2, task=None):
        task = task or self.task
        scripted = Scripted(task, step)
        result = run_prefix(task, scripted)
        self.assertTrue(result["eligible"])
        return result, scripted

    def test_initial_actor_has_only_first_packet_and_allowlisted_channels(self):
        task = deepcopy(self.task)
        task["evaluator"]["secret_marker"] = "EVALUATOR_ONLY_SENTINEL"
        task["stages"][-1]["secret_marker"] = "FUTURE_PACKET_SENTINEL"
        state = initial_state(task)
        state["internal_secret"] = "BOOKKEEPING_SENTINEL"
        data = actor_state(task, state)
        text = render(task, state).json_text
        self.assertEqual(set(data), {"task", "current_stage", "public_dossier", "checkpoint",
                                    "accepted_artifact", "trial", "continuation_records", "feedback",
                                    "lesson", "remaining_actions"})
        self.assertEqual(data["current_stage"], 1)
        self.assertEqual(data["public_dossier"], [{"stage": 1, "stage_count": 3, **task["stages"][0]}])
        for forbidden in ("EVALUATOR_ONLY_SENTINEL", "FUTURE_PACKET_SENTINEL", "BOOKKEEPING_SENTINEL"):
            self.assertNotIn(forbidden, text)
        self.assertNotIn("evaluator", data["task"])
        self.assertNotIn("seed", data["task"])

    def test_public_packet_bytes_survive_failure_at_every_stage(self):
        for failure_step in (1, 2, 3):
            with self.subTest(stage=failure_step):
                prefix, calls = self.prefix(failure_step)
                checkpoint = prefix["checkpoint"]
                expected = [{"stage": i + 1, "stage_count": 3, **self.task["stages"][i]}
                            for i in range(failure_step)]
                self.assertEqual(wire(checkpoint["public_dossier"]), wire(expected))
                self.assertEqual(visible(calls.calls[-1][1])["public_dossier"], expected)
                for arm in ("K", "R"):
                    state = continuation_state(self.task, arm, prefix)
                    self.assertEqual(wire(visible(render(self.task, state))["public_dossier"]), wire(expected))
                    for packet in expected:
                        self.assertEqual(wire(packet["requirements"]),
                                         wire(self.task["stages"][packet["stage"] - 1]["requirements"]))
                self.assertEqual(prefix["pair_contract"]["failure_stage"], failure_step)

    def test_initial_requests_are_byte_identical_after_removing_only_trial(self):
        prefix, _ = self.prefix(3)
        requests = {arm: render(self.task, continuation_state(self.task, arm, prefix)).data()
                    for arm in ("K", "R")}
        users = {arm: json.loads(requests[arm]["messages"][1]["content"]) for arm in requests}
        self.assertEqual(users["K"]["trial"], prefix["trial"])
        self.assertEqual(users["R"]["trial"], [])
        self.assertEqual(set(users["K"]), set(users["R"]))
        self.assertEqual([key for key in users["K"] if users["K"][key] != users["R"][key]], ["trial"])
        for arm in requests:
            users[arm].pop("trial")
            requests[arm]["messages"][1]["content"] = wire(users[arm])
        self.assertEqual(wire(requests["K"]), wire(requests["R"]))
        self.assertNotIn("arm", users["K"])
        self.assertNotIn("policy", users["K"])
        self.assertTrue(pair_contract(self.task, prefix)["passed"])

    def test_successful_prefix_records_and_exact_pre_failure_context_survive(self):
        prefix, calls = self.prefix(3)
        before_request = visible(calls.calls[2][1])
        before_checkpoint = actor_state(self.task, prefix["checkpoint"])
        self.assertEqual(wire(before_request), wire(before_checkpoint))
        self.assertEqual(len(before_request["checkpoint"]["records"]), 2)
        for i, record in enumerate(before_request["checkpoint"]["records"], start=1):
            self.assertEqual(record["action"]["candidate"], independent_balances(self.task, i))
            self.assertEqual(record["receipt"]["status"], "public_pass")
        for arm in ("K", "R"):
            after = visible(render(self.task, continuation_state(self.task, arm, prefix)))
            self.assertEqual(after["checkpoint"], before_request["checkpoint"])
            self.assertEqual(after["accepted_artifact"], before_request["accepted_artifact"])
            self.assertEqual(after["remaining_actions"], before_request["remaining_actions"] - 1)
            self.assertEqual(after["feedback"], prefix["trial"][0]["receipt"])

    def test_shared_lesson_is_generated_once_with_global_step_and_identity(self):
        prefix, scripted = self.prefix(2)
        self.assertEqual([(i.arm, i.step, i.stage) for i, _ in scripted.calls],
                         [("prefix", 1, "action"), ("prefix", 2, "action"), ("prefix", 2, "lesson")])
        for identity, _ in scripted.calls:
            self.assertEqual(identity.study, STUDY)
            self.assertEqual(identity.track, "mechanism")
        outcomes = [run_continuation(self.task, arm, prefix, scripted) for arm in ("K", "R")]
        self.assertTrue(all(outcome["score"] == 1 for outcome in outcomes))
        self.assertEqual(sum(i.stage == "lesson" for i, _ in scripted.calls), 1)
        self.assertEqual(len({i.key for i, _ in scripted.calls}), len(scripted.calls))
        shared = prefix["outcome"]["call_ids"]
        self.assertEqual(len(shared), 3)
        for outcome in outcomes:
            self.assertEqual(outcome["shared_prefix_call_ids"], shared)
            self.assertFalse(set(shared) & set(outcome["call_ids"]))
            self.assertEqual(outcome["actions_used"], 4)
            self.assertEqual(outcome["continuation_actions_used"], 2)
        self.assertEqual(len(scripted.calls), 7)

    def test_new_packets_append_and_checkpoint_remains_fixed_after_recovery(self):
        prefix, _ = self.prefix(1)
        checkpoint = actor_state(self.task, prefix["state"])["checkpoint"]
        for arm in ("K", "R"):
            scripted = Scripted(self.task)
            result = run_continuation(self.task, arm, prefix, scripted)
            self.assertEqual(result["score"], 1)
            for index, (_, request) in enumerate(scripted.calls):
                data = visible(request)
                self.assertEqual(data["checkpoint"], checkpoint)
                self.assertEqual(len(data["continuation_records"]), index)
                self.assertEqual(data["public_dossier"],
                                 [{"stage": i + 1, "stage_count": 3, **self.task["stages"][i]}
                                  for i in range(index + 1)])
                if index:
                    self.assertEqual(data["accepted_artifact"], independent_balances(self.task, index))

    def test_second_failure_retained_without_another_writer_or_deletion(self):
        task = make_task(actions=5)
        prefix, _ = self.prefix(2, task)
        for arm in ("K", "R"):
            scripted = Scripted(task, continuation_failures=(3,))
            result = run_continuation(task, arm, prefix, scripted)
            self.assertEqual(result["score"], 1)
            self.assertTrue(all(i.stage == "action" for i, _ in scripted.calls))
            next_data = visible(scripted.calls[1][1])
            self.assertEqual(len(next_data["continuation_records"]), 1)
            self.assertEqual(next_data["continuation_records"][0]["receipt"]["status"], "public_mismatch")
            self.assertEqual(next_data["lesson"], prefix["lesson"])
            self.assertEqual(next_data["trial"], prefix["trial"] if arm == "K" else [])

    def test_render_and_both_continuations_do_not_mutate_shared_input(self):
        prefix, _ = self.prefix()
        original_task, original_prefix = deepcopy(self.task), deepcopy(prefix)
        state = continuation_state(self.task, "R", prefix)
        snapshot = deepcopy(state)
        data = actor_state(self.task, state)
        data["public_dossier"][0]["requirements"].clear()
        data["checkpoint"]["records"].clear()
        render(self.task, state)
        self.assertEqual(state, snapshot)
        for arm in ("R", "K"):
            run_continuation(self.task, arm, prefix, Scripted(self.task))
        self.assertEqual(self.task, original_task)
        self.assertEqual(prefix, original_prefix)

    def test_no_failure_prefix_is_ineligible_and_continuations_make_no_calls(self):
        scripted = Scripted(self.task, failure_step=None)
        prefix = run_prefix(self.task, scripted)
        self.assertFalse(prefix["eligible"])
        self.assertEqual(prefix["reason"], "all_stages_passed")
        self.assertEqual(prefix["outcome"]["score"], 1)
        self.assertEqual(len(scripted.calls), 3)
        for arm in ("K", "R"):
            result = run_continuation(self.task, arm, prefix, lambda *_: self.fail("unexpected dispatch"))
            self.assertIsNone(result["score"])
            self.assertEqual(result["call_ids"], [])
            self.assertEqual(result["continuation_actions_used"], 0)

    def test_first_mismatch_at_last_action_has_no_lesson_or_pair(self):
        task = make_task(actions=3)
        scripted = Scripted(task, failure_step=3)
        prefix = run_prefix(task, scripted)
        self.assertFalse(prefix["eligible"])
        self.assertEqual(prefix["reason"], "no_remaining_actions")
        self.assertEqual(prefix["outcome"]["score"], 0)
        self.assertTrue(all(i.stage == "action" for i, _ in scripted.calls))
        self.assertNotIn("pair_contract", prefix)

    def test_malformed_and_capped_actions_are_failures_and_consume_action(self):
        for response, disposition in ((SimpleNamespace(text="not JSON", capped=False), "invalid_record"),
                                      (SimpleNamespace(text="{}", capped=True), "capped_output")):
            prefix = run_prefix(self.task, lambda *_: response)
            self.assertFalse(prefix["eligible"])
            self.assertEqual(prefix["outcome"]["score"], 0)
            self.assertEqual(prefix["outcome"]["disposition"], disposition)
            self.assertEqual(prefix["outcome"]["actions_used"], 1)

    def test_continue_action_cannot_manufacture_a_qualifying_failure(self):
        response = SimpleNamespace(text=wire({"status": "continue", "candidate": candidate([]), "note": "wait"}), capped=False)
        result = run_prefix(self.task, lambda *_: response)
        self.assertFalse(result["eligible"])
        self.assertEqual(result["reason"], "invalid_action")
        self.assertEqual(result["trial"], [])

    def test_unusable_lesson_stops_pair_and_is_never_silently_replaced(self):
        for response, reason in ((SimpleNamespace(text="{}", capped=False), "invalid_lesson"),
                                 (SimpleNamespace(text="{}", capped=True), "lesson_capped_output")):
            scripted = Scripted(self.task, failure_step=1)
            def invoke(identity, request):
                return response if identity.stage == "lesson" else scripted(identity, request)
            result = run_prefix(self.task, invoke)
            self.assertFalse(result["eligible"])
            self.assertEqual(result["reason"], reason)
            self.assertIsNone(result["lesson"])
            self.assertEqual(result["outcome"]["actions_used"], 1)
            self.assertEqual(len(result["outcome"]["call_ids"]), 2)

    def test_context_capacity_is_checked_before_dispatch(self):
        with patch("experiments.dependency_memory.rollback_checkpoint_v7.engine.fits", return_value=False):
            prefix = run_prefix(self.task, lambda *_: self.fail("capacity must block dispatch"))
        self.assertEqual(prefix["disposition"], "context_capacity")
        self.assertEqual(prefix["outcome"]["actions_used"], 0)
        self.assertEqual(prefix["outcome"]["call_ids"], [])

    def test_local_unknown_and_global_stop_are_missing_not_observed_failures(self):
        for error, expected in ((CallUnknown("unknown"), "unknown_dispatch"),
                                (Stopped("global"), "infrastructure_stop")):
            def invoke(*_):
                raise error
            prefix = run_prefix(self.task, invoke)
            self.assertEqual(prefix["disposition"], expected)
            self.assertIsNone(prefix["outcome"]["score"])
            eligible, _ = self.prefix()
            result = run_continuation(self.task, "R", eligible, invoke)
            self.assertEqual(result["disposition"], expected)
            self.assertIsNone(result["score"])

    def test_pair_contract_rejects_packet_checkpoint_feedback_and_lesson_drift(self):
        prefix, _ = self.prefix(3)
        mutations = [
            lambda p: p["state"]["public_dossier"][0]["requirements"].pop(),
            lambda p: p["checkpoint"]["public_dossier"][0]["requirements"].pop(),
            lambda p: p["state"]["checkpoint_records"].pop(),
            lambda p: p["state"]["checkpoint_artifact"]["values"].append(99),
            lambda p: p["state"]["feedback"].update(check="fabricated"),
            lambda p: p["state"].update(lesson=None),
            lambda p: p["state"].update(used=4),
            lambda p: p["state"].update(continuation_records=[{"forged": True}]),
        ]
        for mutate in mutations:
            bad = deepcopy(prefix)
            mutate(bad)
            with self.assertRaises(PairContractError):
                pair_contract(self.task, bad)
            with self.assertRaises(PairContractError):
                run_continuation(self.task, "R", bad, lambda *_: self.fail("broken pair dispatched"))

    def test_pair_contract_also_blocks_larger_k_request_when_only_r_fits(self):
        prefix, _ = self.prefix(3)
        with patch("experiments.dependency_memory.rollback_checkpoint_v7.engine.fits",
                   side_effect=lambda request: not visible(request)["trial"]):
            with self.assertRaises(PairContractError):
                pair_contract(self.task, prefix)

    def test_candidate_only_schema_and_complete_body_bound_are_used(self):
        request = render(self.task, initial_state(self.task))
        self.assertTrue(fits(request))
        self.assertEqual(request.input_units, profile.body_bound(request))
        prompt = request.data()["messages"][0]["content"]
        schema = json.loads(prompt.split("\nOutput schema: ")[1].split("\nSupplied source IDs: ")[0])
        self.assertEqual(schema["properties"]["status"]["enum"], ["candidate"])
        self.assertEqual(request.data()["settings"]["reasoning_effort"], "medium")
        self.assertEqual(request.data()["settings"]["model"], "gpt-6-luna")


if __name__ == "__main__":
    unittest.main()
