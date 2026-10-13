"""Concurrency, missingness and durable-replay invariants; no live generations."""
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from contextlib import redirect_stdout
from copy import deepcopy
from dataclasses import asdict
from pathlib import Path
import io
import tempfile
import threading
import unittest
from unittest.mock import patch

from experiments.dependency_memory.rollback_checkpoint_v7.accounting import Ledger, Identity, Stopped, CallUnknown, check_workers
from experiments.dependency_memory.rollback_checkpoint_v7.common import ROOT, STUDY, read, save_new, sha, wire
from experiments.dependency_memory.rollback_checkpoint_v7.prepare import prepare, check_bundle, generate, identities
from experiments.dependency_memory.rollback_checkpoint_v7.engine import initial_state, run_prefix, run_continuation
from experiments.dependency_memory.rollback_checkpoint_v7.contexts import render
from experiments.dependency_memory.rollback_checkpoint_v7.runner import run, ScriptedTransport, read_request, client_preflight
from experiments.dependency_memory.rollback_checkpoint_v7.audit import audit, ReplayMismatch, ledger_rows, independent_action_regrading
from experiments.dependency_memory.rollback_development_v5_continuation.dispatch import Dispatcher, safe_diagnostic, systemic
from experiments.dependency_memory.rollback_math_followup_v4.observe import DiagnosedProtocolError
from experiments.dependency_memory.rollback_pilot.subscription.process import ProtocolError
from experiments.dependency_memory.rollback_pilot.subscription.accounting import Usage, RESERVATION


class RunnerTests(unittest.TestCase):
    def setUp(self):
        parent = ROOT / "tmp" / "rollback-v7-runner-tests"
        parent.mkdir(parents=True, exist_ok=True)
        self.temporary = tempfile.TemporaryDirectory(dir=parent)
        self.addCleanup(self.temporary.cleanup)
        self.folder = Path(self.temporary.name).resolve()
        self.assertTrue(self.folder.is_relative_to(parent.resolve()))

    def fixture(self, name="bundle", count=8, workers=8):
        bundle = self.folder / name
        manifest = prepare(bundle, split="fixture", replicates=count, stages=3,
                           actions=4, workers=workers, seed=2026101267)
        return bundle, manifest, read(bundle / "tasks.json")

    def run_fixture(self, bundle, name="run"):
        output = self.folder / name
        with redirect_stdout(io.StringIO()):
            result = run(bundle, output)
        return output, result

    def test_midstage_fixture_archives_and_replays_exact_pairs(self):
        bundle, manifest, tasks = self.fixture(count=2, workers=2)
        output, result = self.run_fixture(bundle)
        self.assertEqual(result["model_calls"], 0)
        self.assertEqual(result["eligible_prefixes"], 2)
        self.assertEqual(result["completed"], 14)
        self.assertIsNone(result["stop"])
        checked = audit(bundle, output)
        self.assertTrue(checked["all_passed"])
        self.assertEqual(checked["matched_context_contracts"], 2)
        self.assertEqual(checked["independent_action_grades"], 12)
        execution = read(output / "execution.json")
        self.assertEqual([row["job"] for row in execution["jobs"]], manifest["jobs"])
        by_id = {task["task_id"]: task for task in tasks}
        for row in execution["jobs"]:
            if row["job"]["arm"] != "prefix":
                self.assertEqual(row["result"]["score"], 1)
                continue
            prefix = row["result"]
            self.assertEqual(prefix["pair_contract"]["failure_stage"], 2)
            self.assertEqual(len(prefix["checkpoint"]["checkpoint_records"]), 1)
            task = by_id[row["job"]["task_id"]]
            payloads = {}
            for arm in ("K", "R"):
                key = Identity(STUDY, task["task_id"], "mechanism", arm, 3, "action").key
                payloads[arm] = read(output / "requests" / (key + ".json"))
            import json
            visible = {arm: json.loads(payload["messages"][1]["content"])
                       for arm, payload in payloads.items()}
            self.assertEqual(len(visible["R"]["public_dossier"]), 2)
            self.assertEqual(visible["R"]["public_dossier"], visible["K"]["public_dossier"])
            self.assertEqual(visible["K"]["trial"], prefix["trial"])
            self.assertEqual(visible["R"]["trial"], [])
            visible["K"]["trial"] = []
            self.assertEqual(visible["K"], visible["R"])

    def test_eight_simultaneous_admissions_one_unknown_then_independent_completion(self):
        bundle, manifest, tasks = self.fixture()
        first_job = next(job for job in manifest["jobs"] if job["arm"] == "prefix")
        failed_task = first_job["task_id"]
        barrier, lock, sent = threading.Barrier(8), threading.Lock(), Counter()
        base = ScriptedTransport

        class BarrierFixture(base):
            def generate(inner, identity, request):
                with lock:
                    sent[identity.key] += 1
                if identity.arm == "prefix" and identity.step == 1:
                    barrier.wait(timeout=20)
                    if identity.task_id == failed_task:
                        raise DiagnosedProtocolError(ProtocolError("generation_timeout"), "collect", {})
                return super().generate(identity, request)

        with patch("experiments.dependency_memory.rollback_checkpoint_v7.runner.ScriptedTransport", BarrierFixture):
            output, result = self.run_fixture(bundle)
        self.assertIsNone(result["stop"])
        self.assertEqual(result["unknown"], 1)
        self.assertEqual(result["eligible_prefixes"], 7)
        checked = audit(bundle, output)
        self.assertEqual(checked["peak_admitted_calls"], 8)
        self.assertEqual(checked["unknowns_preserved"], 1)
        self.assertTrue(all(count == 1 for count in sent.values()))
        accounting = read(output / "accounting.json")
        self.assertEqual(accounting["locked_planning_credits"], str(RESERVATION))
        self.assertEqual(len(accounting["calls"]), len(sent))
        self.assertLessEqual(len(sent), manifest["generation_ceiling"])
        rows = read(output / "execution.json")["jobs"]
        self.assertEqual(len(rows), 24)
        for row in rows:
            job, outcome = row["job"], row["result"]
            if job["task_id"] == failed_task:
                if job["arm"] == "prefix":
                    self.assertEqual(outcome["reason"], "unknown_dispatch")
                else:
                    self.assertEqual(outcome["disposition"], "not_eligible:unknown_dispatch")
                    self.assertIsNone(outcome["score"])
                    self.assertEqual(outcome["call_ids"], [])
            elif job["arm"] in {"K", "R"}:
                self.assertEqual(outcome["score"], 1)
        calls, events, _ = ledger_rows(output / "ledger.sqlite")
        unknown_event = next(i for i, event in enumerate(events) if event["state"] == "unknown")
        self.assertTrue(any(event["state"] == "dispatched" for event in events[unknown_event + 1:]))
        self.assertFalse(any(call["identity"]["task_id"] == failed_task
                             and call["identity"]["arm"] != "prefix" for call in calls))

    def test_unknown_arm_preserves_its_mate_and_no_replacement(self):
        bundle, _, tasks = self.fixture(count=2, workers=2)
        failed = Identity(STUDY, tasks[0]["task_id"], "mechanism", "R", 3, "action")
        base = ScriptedTransport

        class MissingArm(base):
            def generate(inner, identity, request):
                if identity == failed:
                    raise DiagnosedProtocolError(ProtocolError("generation_timeout"), "collect", {})
                return super().generate(identity, request)

        with patch("experiments.dependency_memory.rollback_checkpoint_v7.runner.ScriptedTransport", MissingArm):
            output, result = self.run_fixture(bundle)
        self.assertEqual(result["unknown"], 1)
        self.assertIsNone(result["stop"])
        self.assertTrue(audit(bundle, output)["all_passed"])
        rows = read(output / "execution.json")["jobs"]
        by_arm = {row["job"]["arm"]: row["result"] for row in rows
                  if row["job"]["task_id"] == tasks[0]["task_id"]}
        self.assertEqual(by_arm["R"]["disposition"], "unknown_dispatch")
        self.assertEqual(by_arm["K"]["score"], 1)
        self.assertFalse(any(call["identity"]["arm"] == "R" and call["identity"]["step"] > 3
                             and call["identity"]["task_id"] == failed.task_id
                             for call in read(output / "accounting.json")["calls"]))

    def test_unknown_shared_lesson_skips_only_dependent_pair(self):
        bundle, _, tasks = self.fixture(count=2, workers=2)
        failed = Identity(STUDY, tasks[0]["task_id"], "mechanism", "prefix", 2, "lesson")
        base = ScriptedTransport

        class MissingLesson(base):
            def generate(inner, identity, request):
                if identity == failed:
                    raise DiagnosedProtocolError(ProtocolError("generation_timeout"), "collect", {})
                return super().generate(identity, request)

        with patch("experiments.dependency_memory.rollback_checkpoint_v7.runner.ScriptedTransport", MissingLesson):
            output, result = self.run_fixture(bundle)
        self.assertEqual(result["unknown"], 1)
        self.assertEqual(result["eligible_prefixes"], 1)
        self.assertIsNone(result["stop"])
        self.assertTrue(audit(bundle, output)["all_passed"])
        calls = read(output / "accounting.json")["calls"]
        self.assertEqual([call["state"] for call in calls if call["call_id"] == failed.key], ["unknown"])
        self.assertFalse(any(call["identity"]["task_id"] == failed.task_id
                             and call["identity"]["arm"] != "prefix" for call in calls))

    def test_no_failed_prefix_keeps_explicit_fixed_denominator_skips(self):
        bundle, manifest, _ = self.fixture(count=2, workers=2)
        base = ScriptedTransport

        class AlwaysCorrect(base):
            def __init__(inner, tasks):
                super().__init__(tasks, failure_step=999)

        with patch("experiments.dependency_memory.rollback_checkpoint_v7.runner.ScriptedTransport", AlwaysCorrect):
            output, result = self.run_fixture(bundle)
        self.assertEqual(result["eligible_prefixes"], 0)
        self.assertEqual(result["completed"], 6)
        self.assertTrue(audit(bundle, output)["all_passed"])
        self.assertEqual(len(read(output / "execution.json")["jobs"]), len(manifest["jobs"]))
        calls = read(output / "accounting.json")["calls"]
        self.assertTrue(all(call["identity"]["arm"] == "prefix"
                            and call["identity"]["stage"] == "action" for call in calls))

    def test_no_second_launch_and_frozen_workers(self):
        bundle, _, _ = self.fixture(count=1, workers=1)
        with self.assertRaisesRegex(ValueError, "worker count differs"):
            run(bundle, self.folder / "wrong-workers", workers=2)
        self.run_fixture(bundle)
        with self.assertRaisesRegex(ValueError, "already started"):
            run(bundle, self.folder / "replacement")
        with self.assertRaisesRegex(ValueError, "fixture allocations"):
            run(bundle, self.folder / "accidental-live", live=True)

    def test_archive_detects_grader_request_and_inventory_tampering(self):
        bundle, _, _ = self.fixture(count=1, workers=1)
        output, _ = self.run_fixture(bundle)
        self.assertTrue(audit(bundle, output)["all_passed"])
        request = next((output / "requests").glob("*.json"))
        request.write_text("{}", encoding="utf-8")
        with self.assertRaisesRegex(ReplayMismatch, "evidence changed"):
            audit(bundle, output)

    def test_independent_regrading_rejects_a_consistently_replayed_checker_defect(self):
        # A checker that accepts a wrong final balance can produce an internally
        # consistent sealed archive, and replaying that same checker agrees.
        # The independent sorted-revision formulation must still reject it.
        bundle, _, tasks = self.fixture(count=1, workers=1)
        base = ScriptedTransport
        from experiments.dependency_memory.rollback_challenge_v6.tasks import public_check as correct_check

        class WrongFinalCandidate(base):
            def __init__(inner, cohort):
                super().__init__(cohort, failure_step=999)

            def generate(inner, identity, request):
                response = super().generate(identity, request)
                if identity.stage == "action" and read_request(request)["current_stage"] == 3:
                    import json
                    value = json.loads(response.text)
                    value["candidate"]["values"][0] += 1
                    return type(response)(wire(value), response.usage, response.metadata, response.capped)
                return response

        def defective_check(task, stage, candidate):
            if stage == 2:
                return {"status": "public_pass", "checks": sum(len(p["requirements"]) for p in task["stages"])}
            return correct_check(task, stage, candidate)

        with patch("experiments.dependency_memory.rollback_checkpoint_v7.runner.ScriptedTransport", WrongFinalCandidate), \
                patch("experiments.dependency_memory.rollback_checkpoint_v7.engine.public_check", side_effect=defective_check):
            output, _ = self.run_fixture(bundle)
            # Same buggy checker remains active while replay runs. Only the
            # separate formulation can identify the incorrect pass receipt.
            with self.assertRaisesRegex(ReplayMismatch, "independent action grader disagreement"):
                audit(bundle, output)

    def test_independent_regrading_preserves_capped_malformed_and_invalid_candidates(self):
        bundle, _, tasks = self.fixture(count=3, workers=3)
        kinds = {task["task_id"]: kind for task, kind in zip(tasks, ("capped", "malformed", "invalid"))}
        base = ScriptedTransport

        class NonMathematicalFailures(base):
            def generate(inner, identity, request):
                response = super().generate(identity, request)
                if identity.stage != "action" or identity.step != 1:
                    return response
                kind = kinds[identity.task_id]
                if kind == "capped":
                    return type(response)(response.text, response.usage, response.metadata, True)
                if kind == "malformed":
                    return type(response)("not valid JSON", response.usage, response.metadata, False)
                import json
                value = json.loads(response.text)
                value["candidate"]["order"] = [1]
                return type(response)(wire(value), response.usage, response.metadata, False)

        with patch("experiments.dependency_memory.rollback_checkpoint_v7.runner.ScriptedTransport", NonMathematicalFailures):
            output, result = self.run_fixture(bundle)
        checked = audit(bundle, output)
        self.assertEqual(result["completed"], 3)
        self.assertEqual(result["eligible_prefixes"], 0)
        self.assertEqual(checked["independent_action_regrading"], {
            "checked": 1, "public_pass": 0, "public_mismatch": 0, "invalid_candidate": 1,
            "capped_records_preserved": 1, "malformed_or_disallowed_records_preserved": 1,
            "unknown_actions_preserved": 0})

    def test_concurrency_bound_supports_sixteen_and_never_overadmits(self):
        candidates = [Identity(STUDY, "fixture", "mechanism", "prefix", step, "action")
                      for step in range(1, 18)]
        ledger = Ledger(self.folder / "ledger.sqlite", candidates, 16, generation_ceiling=17)
        with ThreadPoolExecutor(max_workers=16) as pool:
            list(pool.map(lambda identity: ledger.admit(identity, "fixture-request"), candidates[:16]))
        self.assertEqual(ledger.snapshot()["unknown_or_inflight_calls"], 16)
        with self.assertRaisesRegex(ValueError, "concurrency"):
            ledger.admit(candidates[16], "fixture-request")
        ledger.complete(candidates[0], Usage(10, 0, 10, 0), {"thread_id": "fixture-first"}, 0)
        ledger.admit(candidates[16], "fixture-request")
        self.assertEqual(len(ledger.snapshot()["calls"]), 17)
        for value in (0, 17, -1, 1.0, True):
            with self.assertRaises(ValueError):
                check_workers(value)

    def test_generation_ceiling_counts_unknowns_and_prevents_repeated_identity(self):
        candidates = [Identity(STUDY, "fixture", "mechanism", "prefix", step, "action")
                      for step in (1, 2, 3)]
        ledger = Ledger(self.folder / "ledger.sqlite", candidates, 8, generation_ceiling=2)
        ledger.admit(candidates[0], "request-one")
        ledger.unknown(candidates[0], "fixture_unknown", diagnostic={}, fatal=False)
        with self.assertRaisesRegex(ValueError, "never replay"):
            ledger.admit(candidates[0], "request-one")
        ledger.admit(candidates[1], "request-two")
        ledger.complete(candidates[1], Usage(1, 0, 1, 0), {"thread_id": "new-thread"}, 0)
        with self.assertRaisesRegex(Stopped, "ceiling"):
            ledger.admit(candidates[2], "request-three")
        self.assertEqual(ledger.snapshot()["locked_planning_credits"], str(RESERVATION))
        self.assertEqual(len(ledger.snapshot()["calls"]), 2)

    def test_quota_isolation_and_source_faults_stop_global_admission(self):
        for phase, reason in (("quota", "included_limit_reached_or_unknown"),
                              ("collect", "tool_or_external_information_attempt"),
                              ("thread", "unexpected_workspace_or_prior_state"),
                              ("account", "ChatGPT_subscription_signin_required")):
            self.assertTrue(systemic(safe_diagnostic(DiagnosedProtocolError(ProtocolError(reason), phase, {}))))
        task = generate(split="fixture", replicates=1)[0]
        ledger = Ledger(self.folder / "ledger.sqlite", identities([task]), 8, generation_ceiling=8)
        path = self.folder / "pinned.py"
        path.write_text("frozen", encoding="utf-8")
        bindings = [{"path": path.relative_to(ROOT).as_posix(), "sha256": sha(path.read_bytes())}]
        dispatcher = Dispatcher(self.folder, {"source_bindings": bindings}, ledger,
                                lambda: self.fail("source drift created a transport"))
        path.write_text("changed", encoding="utf-8")
        with self.assertRaisesRegex(Stopped, "source_drift"):
            dispatcher(identities([task])[0], render(task, initial_state(task)))
        self.assertEqual(ledger.snapshot()["stop"], "source_drift")
        self.assertEqual(ledger.snapshot()["calls"], [])

    def test_real_client_preflight_schedules_frozen_concurrency_and_both_schemas(self):
        # This mocks only external processes, not the runner, actor contexts,
        # checkpoint reconstruction, output schemas, or parallel barrier.
        tasks = generate(split="fixture", replicates=2)
        instructions = self.folder / "AGENTS.md"
        instructions.write_text("Fixture global instructions.", encoding="utf-8")
        observed, lock = [], threading.Lock()

        def loopback(executable, global_text, request, case, scratch_root):
            with lock:
                observed.append((request.stage, sha(request.json_text)))
            return {"case": case, "http_attempts": 1, "authorization_present": False,
                    "accepted_transport": True, "real_model_generations": 0}

        with patch("experiments.dependency_memory.rollback_checkpoint_v7.runner.preflight",
                   return_value={"serialization_and_retry_audit_passed": True}), \
                patch("experiments.dependency_memory.rollback_checkpoint_v7.runner.run_case", side_effect=loopback):
            checked = client_preflight("fixture-codex", instructions, self.folder / "scratch", tasks, 8)
        self.assertEqual(checked["v7_verified_workers"], 8)
        self.assertEqual(len(checked["v7_parallel_payload_checks"]), 8)
        self.assertEqual({stage for stage, _ in observed}, {"action", "lesson"})
        self.assertTrue(checked["v7_fixture_prefix_eligible"])
        self.assertEqual(checked["real_model_generations"], 0)


if __name__ == "__main__":
    unittest.main()
