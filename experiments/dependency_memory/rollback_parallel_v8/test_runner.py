"""Full controller invariants for higher concurrency and dependency pipelining.

All transports below are disclosed scripted fixtures. They make no model call.
The actual prepared allocation, request contexts, durable ledger, controller,
analysis and receipt replay are exercised without bypassing source checks.
"""

from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from contextlib import redirect_stdout
from pathlib import Path
import io
import json
import tempfile
import threading
import unittest
from unittest.mock import patch

from experiments.dependency_memory.rollback_parallel_v8.accounting import Ledger, Identity
from experiments.dependency_memory.rollback_parallel_v8.common import ROOT, STUDY, read
from experiments.dependency_memory.rollback_parallel_v8.prepare import prepare
from experiments.dependency_memory.rollback_parallel_v8.runner import (
    ScriptedTransport, client_preflight, run,
)
from experiments.dependency_memory.rollback_parallel_v8.audit import audit, ledger_rows
from experiments.dependency_memory.rollback_checkpoint_v7 import engine as historical_engine
from experiments.dependency_memory.rollback_math_followup_v4.observe import DiagnosedProtocolError
from experiments.dependency_memory.rollback_pilot.subscription.process import ProtocolError
from experiments.dependency_memory.rollback_pilot.subscription.accounting import Usage, RESERVATION


class PipelineControllerTests(unittest.TestCase):
    def setUp(self):
        parent = ROOT / "tmp" / "rollback-v8-runner-tests"
        parent.mkdir(parents=True, exist_ok=True)
        temporary = tempfile.TemporaryDirectory(dir=parent)
        self.addCleanup(temporary.cleanup)
        self.folder = Path(temporary.name).resolve()
        self.assertTrue(self.folder.is_relative_to(parent.resolve()))

    def fixture(self, count=2, workers=2):
        bundle = self.folder / "bundle"
        manifest = prepare(bundle, split="fixture", replicates=count, workers=workers,
                           stages=3, actions=4, max_calls=8 * count, seed=2026101381)
        return bundle, manifest, read(bundle / "tasks.json")

    def run_fixture(self, bundle):
        output = self.folder / "run"
        with redirect_stdout(io.StringIO()):
            result = run(bundle, output)
        return output, result

    def test_sixteen_calls_pipeline_around_slow_prefix_and_preserve_one_unknown(self):
        bundle, manifest, tasks = self.fixture(count=16, workers=16)
        prefix_jobs = [job for job in manifest["jobs"] if job["arm"] == "prefix"]
        slow_task, unknown_task = [job["task_id"] for job in prefix_jobs[:2]]
        gate = threading.Barrier(16)
        continuation = threading.Event()
        lock, attempted = threading.Lock(), Counter()

        class ConcurrentFixture(ScriptedTransport):
            def generate(inner, identity, request):
                with lock:
                    attempted[identity.key] += 1
                if identity.arm == "prefix" and identity.step == 1:
                    gate.wait(timeout=30)
                    if identity.task_id == unknown_task:
                        raise DiagnosedProtocolError(ProtocolError("generation_timeout"), "collect", {})
                    if identity.task_id == slow_task and not continuation.wait(timeout=30):
                        raise AssertionError("a continuation must start before unrelated prefix finishes")
                elif identity.arm in {"K", "R"}:
                    continuation.set()
                return super().generate(identity, request)

        with patch("experiments.dependency_memory.rollback_parallel_v8.runner.ScriptedTransport", ConcurrentFixture):
            output, result = self.run_fixture(bundle)
        self.assertEqual(result["model_calls"], 0)
        self.assertEqual(result["jobs"], 48)
        self.assertEqual(result["completed"], 105)
        self.assertEqual(result["unknown"], 1)
        self.assertEqual(result["eligible_prefixes"], 15)
        self.assertIsNone(result["stop"])
        self.assertEqual(set(attempted.values()), {1})
        checked = audit(bundle, output)
        self.assertTrue(checked["all_passed"])
        self.assertEqual(checked["peak_admitted_calls"], 16)
        self.assertEqual(checked["matched_context_contracts"], 15)
        self.assertEqual(checked["unknowns_preserved"], 1)
        self.assertEqual(checked["independent_action_grades"], 90)
        execution = read(output / "execution.json")
        self.assertEqual([row["job"] for row in execution["jobs"]], manifest["jobs"])
        for row in execution["jobs"]:
            job, outcome = row["job"], row["result"]
            if job["task_id"] == unknown_task and job["arm"] != "prefix":
                self.assertEqual(outcome["disposition"], "not_eligible:unknown_dispatch")
                self.assertIsNone(outcome["score"])
                self.assertEqual(outcome["call_ids"], [])
            elif job["task_id"] != unknown_task and job["arm"] != "prefix":
                self.assertEqual(outcome["score"], 1)
        accounting = read(output / "accounting.json")
        self.assertEqual(accounting["locked_planning_credits"], str(RESERVATION))
        self.assertEqual(len(accounting["calls"]), 106)
        self.assertEqual(len({c["metadata"]["thread_id"] for c in accounting["calls"]
                              if c["state"] == "completed"}), 105)
        for key in ("input_tokens", "cached_input", "output", "reasoning"):
            self.assertEqual(accounting["usage"][key], sum(c["usage"][key] for c in accounting["calls"]
                                                         if c["state"] == "completed"))
        calls, events, _ = ledger_rows(output / "ledger.sqlite")
        unknown_index = next(i for i, event in enumerate(events) if event["state"] == "unknown")
        self.assertTrue(any(event["state"] == "dispatched" for event in events[unknown_index + 1:]))
        self.assertFalse(any(call["identity"]["task_id"] == unknown_task
                             and call["identity"]["arm"] != "prefix" for call in calls))
        trace = read(output / "scheduler_trace.json")
        self.assertEqual(trace["peak_active_workers"], 16)
        self.assertGreater(trace["continuation_started_before_all_prefixes_persisted"], 0)
        rows = {row["job_id"]: row for row in trace["jobs"]}
        slow_id = next(job["job_id"] for job in prefix_jobs if job["task_id"] == slow_task)
        self.assertTrue(any(row["arm"] in {"K", "R"} and
                            row["started_seconds"] < rows[slow_id]["finished_seconds"]
                            for row in rows.values()))
        for row in rows.values():
            if row["depends_on"]:
                self.assertLessEqual(rows[row["depends_on"]]["completed_seconds"], row["started_seconds"])

    def test_serial_and_pipelined_engines_render_identical_full_contexts_and_usage(self):
        bundle, manifest, tasks = self.fixture(count=2, workers=2)
        output, result = self.run_fixture(bundle)
        self.assertEqual(result["completed"], 14)
        self.assertTrue(audit(bundle, output)["all_passed"])
        reference_requests, reference_usage = {}, {}
        fixture = ScriptedTransport(tasks)

        def historical(identity, request):
            # v7 IDs differ by study name; task, stage, step and arm identify the
            # same logical call without editing any frozen v7 implementation.
            key = (identity.task_id, identity.arm, identity.step, identity.stage)
            reference_requests[key] = request.data()
            response = fixture.generate(identity, request)
            reference_usage[key] = vars(response.usage)
            return response

        for task in tasks:
            prefix = historical_engine.run_prefix(task, historical)
            for arm in ("K", "R"):
                historical_engine.run_continuation(task, arm, prefix, historical)
        accounting = read(output / "accounting.json")
        self.assertEqual(len(reference_requests), len(accounting["calls"]))
        for call in accounting["calls"]:
            identity = call["identity"]
            key = tuple(identity[field] for field in ("task_id", "arm", "step", "stage"))
            self.assertEqual(read(output / "requests" / (call["call_id"] + ".json")), reference_requests[key])
            self.assertEqual(call["usage"], reference_usage[key])
        for task in tasks:
            payloads = {}
            for arm in ("K", "R"):
                key = Identity(STUDY, task["task_id"], "mechanism", arm, 3, "action").key
                request = read(output / "requests" / (key + ".json"))
                payloads[arm] = json.loads(request["messages"][1]["content"])
            self.assertEqual(len(payloads["K"]["public_dossier"]), 2)
            self.assertEqual(len(payloads["K"]["checkpoint"]["records"]), 1)
            self.assertEqual(len(payloads["K"]["trial"]), 1)
            self.assertEqual(payloads["R"]["trial"], [])
            payloads["K"]["trial"] = []
            self.assertEqual(payloads["K"], payloads["R"])

    def test_unknown_continuation_preserves_mate_and_unrelated_task(self):
        bundle, _, tasks = self.fixture(count=2, workers=2)
        missing = Identity(STUDY, tasks[0]["task_id"], "mechanism", "R", 3, "action")

        class MissingArm(ScriptedTransport):
            def generate(inner, identity, request):
                if identity == missing:
                    raise DiagnosedProtocolError(ProtocolError("generation_timeout"), "collect", {})
                return super().generate(identity, request)

        with patch("experiments.dependency_memory.rollback_parallel_v8.runner.ScriptedTransport", MissingArm):
            output, result = self.run_fixture(bundle)
        self.assertEqual(result["unknown"], 1)
        self.assertIsNone(result["stop"])
        self.assertTrue(audit(bundle, output)["all_passed"])
        rows = read(output / "execution.json")["jobs"]
        by_arm = {row["job"]["arm"]: row["result"] for row in rows
                  if row["job"]["task_id"] == tasks[0]["task_id"]}
        self.assertEqual(by_arm["R"]["disposition"], "unknown_dispatch")
        self.assertEqual(by_arm["K"]["score"], 1)
        self.assertTrue(all(row["result"]["score"] == 1 for row in rows
                            if row["job"]["task_id"] == tasks[1]["task_id"]
                            and row["job"]["arm"] != "prefix"))
        calls = read(output / "accounting.json")["calls"]
        self.assertFalse(any(call["identity"]["task_id"] == missing.task_id
                             and call["identity"]["arm"] == "R" and call["identity"]["step"] > 3
                             for call in calls))

    def test_thirty_two_admissions_are_bounded_and_unknown_keeps_its_reservation(self):
        candidates = [Identity(STUDY, "fixture", "mechanism", "prefix", i, "action") for i in range(1, 34)]
        ledger = Ledger(self.folder / "ledger.sqlite", candidates, 32, generation_ceiling=33)
        with ThreadPoolExecutor(max_workers=32) as pool:
            list(pool.map(lambda identity: ledger.admit(identity, "fixture-request"), candidates[:32]))
        self.assertEqual(ledger.snapshot()["unknown_or_inflight_calls"], 32)
        with self.assertRaisesRegex(ValueError, "concurrency"):
            ledger.admit(candidates[32], "fixture-request")
        ledger.unknown(candidates[0], "fixture_unknown", diagnostic={}, fatal=False)
        with self.assertRaisesRegex(ValueError, "never replay"):
            ledger.admit(candidates[0], "fixture-request")
        ledger.admit(candidates[32], "fixture-request")
        for identity in candidates[1:]:
            ledger.complete(identity, Usage(1, 0, 1, 0), {"thread_id": "fixture-" + identity.key}, 0)
        self.assertEqual(len(ledger.snapshot()["calls"]), 33)
        self.assertEqual(ledger.snapshot()["completed_calls"], 32)
        self.assertEqual(ledger.snapshot()["locked_planning_credits"], str(RESERVATION))
        self.assertIsNone(ledger.snapshot()["stop"])

    def test_preflight_exercises_sixteen_sessions_and_both_request_schemas(self):
        _, _, tasks = self.fixture(count=2, workers=16)
        instructions = self.folder / "global-instructions.md"
        instructions.write_text("Only a fixture instruction.", encoding="utf-8")
        seen, lock = [], threading.Lock()

        def loopback(executable, text, request, case, scratch_root):
            with lock:
                seen.append(request.stage)
            return {"case": case, "http_attempts": 1, "authorization_present": False,
                    "accepted_transport": True, "real_model_generations": 0}

        with patch("experiments.dependency_memory.rollback_parallel_v8.runner.preflight",
                   return_value={"serialization_and_retry_audit_passed": True}), \
                patch("experiments.dependency_memory.rollback_parallel_v8.runner.run_case", side_effect=loopback):
            checked = client_preflight("fixture-codex", instructions, self.folder / "scratch", tasks, 16)
        self.assertEqual(checked["v8_verified_workers"], 16)
        self.assertEqual(len(checked["v8_parallel_payload_checks"]), 16)
        self.assertEqual(set(seen), {"action", "lesson"})
        self.assertEqual(checked["real_model_generations"], 0)


if __name__ == "__main__":
    unittest.main()
