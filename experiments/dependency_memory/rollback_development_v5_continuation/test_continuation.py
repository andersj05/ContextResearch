"""Scientific invariants for amended failure scope and receipt reconstruction."""
from copy import deepcopy
from dataclasses import asdict
from pathlib import Path
import shutil
import tempfile
import unittest

from .accounting import Ledger, CallUnknown
from .dispatch import Dispatcher, safe_diagnostic, systemic
from .engine import run_prefix, run_episode
from .schedule import execute, child_dispositions
from .prepare import prepare, check_prepared
from .run import run
from .audit import audit
from ..rollback_development_v5.common import ROOT, STUDY, save_new, sha, read
from ..rollback_development_v5.accounting import Ledger as OldLedger, Identity, Stopped
from ..rollback_development_v5.dispatch import Dispatcher as OldDispatcher
from ..rollback_development_v5.engine import initial_state, run_episode as old_episode
from ..rollback_development_v5.contexts import render
from ..rollback_development_v5.tasks import generate
from ..rollback_development_v5.schedule import identities, jobs, execute as old_execute
from ..rollback_development_v5.prepare import prepare as old_prepare
from ..rollback_development_v5.analysis import analyze as old_analyze
from ..rollback_development_v5.audit import ReplayMismatch, ledger_rows
from ..rollback_development_v5.calibration import cases
from ..rollback_development_v5.simulation import ScriptedTransport, OracleRunner
from ..rollback_math_followup_v4.observe import DiagnosedProtocolError
from ..rollback_pilot.subscription.process import ProtocolError


class LocalFailure(ScriptedTransport):
    def generate(self, identity, request):
        if identity.key == self.fail_key:
            raise DiagnosedProtocolError(ProtocolError("generation_timeout"), "collect", {})
        return super().generate(identity, request)


class ContinuationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tasks = generate()

    def setUp(self):
        (ROOT / "tmp").mkdir(exist_ok=True)
        self.temp = tempfile.TemporaryDirectory(dir=ROOT / "tmp", prefix="v5-continuation-test-")
        self.addCleanup(self.temp.cleanup)
        self.folder = Path(self.temp.name)
        self.task = next(t for t in self.tasks if t["family"] == "scheduling" and t["horizon"] == "medium")
        self.runner = OracleRunner(self.tasks)

    def identity(self, arm="K", step=1, stage="action", track="policy"):
        return Identity(STUDY, self.task["task_id"], track, arm, step, stage)

    def dispatcher(self, *, fail=None, old=False, folder=None):
        folder = folder or self.folder
        allocation = identities([self.task], ("policy", "mechanism", "memory"))
        ledger = (OldLedger if old else Ledger)(folder / "ledger.sqlite", allocation, 4)
        factory = lambda: (ScriptedTransport if old else LocalFailure)([self.task], fail_key=fail)
        return (OldDispatcher if old else Dispatcher)(folder, {"source_bindings": []}, ledger, factory)

    def test_unknown_call_leaves_independent_work_admissible(self):
        first, second = self.identity(), self.identity("R")
        dispatcher = self.dispatcher(fail=first.key)
        request = render(self.task, initial_state(self.task))
        with self.assertRaises(CallUnknown):
            dispatcher(first, request)
        dispatcher(second, request)
        self.assertFalse(dispatcher.ledger.stopped())
        self.assertEqual(dispatcher.ledger.snapshot()["unknown_or_inflight_calls"], 1)
        self.assertEqual(dispatcher.ledger.snapshot()["completed_calls"], 1)

    def test_subscription_or_information_contract_failures_stop_globally(self):
        for phase, reason in (("quota", "included_limit_reached_or_unknown"),
                              ("collect", "tool_or_external_information_attempt"),
                              ("thread", "unexpected_workspace_or_prior_state")):
            with self.subTest(phase=phase):
                diagnostic = safe_diagnostic(DiagnosedProtocolError(ProtocolError(reason), phase, {}))
                self.assertTrue(systemic(diagnostic))

    def test_diagnostics_exclude_untrusted_strings(self):
        error = DiagnosedProtocolError(ProtocolError("generation_timeout"), "collect", {
            "method_counts": {"item/completed": 2, "secret-value": 3}, "server_error_codes": ["internalServerError", "secret"],
            "raw": "credential", "turn_statuses": ["failed", "private"]})
        diagnostic = safe_diagnostic(error)
        self.assertNotIn("secret", str(diagnostic))
        self.assertNotIn("credential", str(diagnostic))
        self.assertFalse(systemic(diagnostic))

    def make_historical_action(self):
        prior = self.folder / "prior"
        dispatcher = self.dispatcher(old=True, folder=prior)
        identity = self.identity()
        request = render(self.task, initial_state(self.task))
        response = dispatcher(identity, request)
        calls, _, _ = ledger_rows(prior / "ledger.sqlite")
        current = self.folder / "current"
        current.mkdir()
        shutil.copytree(prior / "requests", current / "requests")
        shutil.copytree(prior / "responses", current / "responses")
        ledger = Ledger(current / "ledger.sqlite", identities([self.task], ("policy", "mechanism", "memory")), 4,
                        prior=prior / "ledger.sqlite")
        return prior, current, ledger, identity, request, response, calls

    def test_historical_response_reconstructs_without_transport_or_admission(self):
        prior, current, ledger, identity, request, response, calls = self.make_historical_action()
        before = sha((prior / "ledger.sqlite").read_bytes())
        def forbidden():
            self.fail("historical reconstruction created a transport")
        dispatcher = Dispatcher(current, {"source_bindings": []}, ledger, forbidden, historical=calls)
        self.assertEqual(dispatcher(identity, request).text, response.text)
        self.assertEqual(len(ledger.snapshot()["calls"]), 1)
        self.assertEqual(sha((prior / "ledger.sqlite").read_bytes()), before)
        with self.assertRaises(ReplayMismatch):
            dispatcher(identity, request)

    def test_historical_request_tampering_is_rejected(self):
        _, current, ledger, identity, _, _, calls = self.make_historical_action()
        state = initial_state(self.task)
        state["memory"] = [{"invented": "extra facts"}]
        dispatcher = Dispatcher(current, {"source_bindings": []}, ledger, lambda: None, historical=calls)
        with self.assertRaises(ReplayMismatch):
            dispatcher(identity, render(self.task, state))
        self.assertTrue(ledger.stopped())

    def test_cumulative_ceiling_includes_completed_and_unknown_admissions(self):
        prior = self.folder / "prior"
        a, b, c = self.identity(), self.identity("R"), self.identity("Z")
        old = self.dispatcher(old=True, folder=prior)
        request = render(self.task, initial_state(self.task))
        old(a, request)
        old.ledger.admit(b, sha(request.json_text))
        old.ledger.unknown(b, "preserved_failure")
        ledger = Ledger(self.folder / "new.sqlite", identities([self.task], ("policy", "mechanism", "memory")), 4,
                        prior=prior / "ledger.sqlite", generation_ceiling=2)
        self.assertFalse(ledger.stopped())
        with self.assertRaises(Stopped):
            ledger.admit(c, sha(request.json_text))
        self.assertEqual(ledger.snapshot()["stop"], "generation_ceiling_reached")
        self.assertEqual(len(ledger.snapshot()["calls"]), 2)

    def test_partial_episode_restoration_sends_only_next_unsent_identity(self):
        stop_identity = self.identity(step=2)
        old = self.dispatcher(old=True)
        original_factory = old.transport_factory
        class StopBeforeNext:
            def __call__(_, identity, request):
                if identity == stop_identity:
                    old.ledger.stop("other_job_failed")
                    raise Stopped("other_job_failed")
                return old(identity, request)
        partial = old_episode(self.task, "policy", "K", StopBeforeNext(), self.runner)
        self.assertIsNone(partial["score"])
        historical, _, _ = ledger_rows(self.folder / "ledger.sqlite")
        current = self.folder / "current"
        current.mkdir()
        for name in ("requests", "responses"):
            shutil.copytree(self.folder / name, current / name)
        ledger = Ledger(current / "ledger.sqlite", identities([self.task], ("policy", "mechanism", "memory")), 4,
                        prior=self.folder / "ledger.sqlite")
        sent = []
        class Counting(ScriptedTransport):
            def generate(inner, identity, request):
                sent.append(identity.key)
                return super().generate(identity, request)
        dispatcher = Dispatcher(current, {"source_bindings": []}, ledger, lambda: Counting([self.task]), historical=historical)
        result = run_episode(self.task, "policy", "K", dispatcher, self.runner)
        self.assertEqual(result["score"], 1)
        self.assertEqual(sent[0], stop_identity.key)
        self.assertFalse({c["call_id"] for c in historical} & set(sent))
        self.assertEqual(result["actions_used"], len(self.task["stages"]) + 1)

    def test_unknown_common_lesson_blocks_only_dependent_arms(self):
        identity = self.identity("shared", 0, "lesson", "mechanism")
        dispatcher = self.dispatcher(fail=identity.key)
        prefix = run_prefix(self.task, dispatcher, self.runner)
        self.assertTrue(prefix["eligible"])
        self.assertIsNone(prefix["shared"]["lesson"])
        self.assertIsNotNone(prefix["shared"]["summary"])
        children = [j for j in jobs([self.task], ("mechanism",)) if j["dependency"]]
        reasons = {j["arm"]: reason for j, reason in child_dispositions(self.task, prefix, children, dispatcher.ledger)}
        self.assertEqual({arm for arm, reason in reasons.items() if reason}, {"K", "R"})
        self.assertFalse(dispatcher.ledger.stopped())

    def test_scheduler_finishes_all_tracks_after_local_shared_writer_failure(self):
        failed = self.identity("shared", 0, "lesson", "mechanism")
        dispatcher = self.dispatcher(fail=failed.key)
        planned = jobs([self.task], ("mechanism", "policy", "memory"))
        prior = {"jobs": [{"job": job, "result": {"score": None, "disposition": "unstarted_global_stop", "call_ids": []}}
                          for job in planned], "wall_seconds": 0, "peak_active_jobs": 0}
        result = execute([self.task], {"jobs": planned}, dispatcher, self.runner, self.folder, 4, prior, [])
        self.assertFalse(result["stopped"])
        self.assertEqual(len(result["jobs"]), 16)
        blocked = [r for r in result["jobs"] if r["result"].get("disposition") == "unusable_common_lesson"]
        self.assertEqual({r["job"]["arm"] for r in blocked}, {"K", "R"})
        self.assertEqual({r["job"]["track"] for r in blocked}, {"mechanism"})
        self.assertTrue(all(r["result"].get("score") == 1 for r in result["jobs"]
                            if r["job"]["track"] in {"policy", "memory"}))
        self.assertEqual(dispatcher.ledger.snapshot()["unknown_or_inflight_calls"], 1)


class EvidenceReplayTest(unittest.TestCase):
    def test_complete_continuation_and_independent_replay_preserve_unknown(self):
        (ROOT / "tmp").mkdir(exist_ok=True)
        with tempfile.TemporaryDirectory(dir=ROOT / "tmp", prefix="v5-amendment-evidence-") as name:
            root = Path(name)
            bundle, prior, prepared, output = (root / p for p in ("bundle", "prior", "prepared", "output"))
            manifest = old_prepare(bundle, ("policy",))
            tasks = read(bundle / "tasks.json")
            prior.mkdir()
            allocation = identities(tasks, manifest["tracks"]) + [c["identity"] for c in cases()]
            ledger = OldLedger(prior / "ledger.sqlite", allocation, 4)
            first = next(j for j in manifest["jobs"] if j["arm"] == "K")
            failed = Identity(STUDY, first["task_id"], "policy", "K", 1, "action")
            dispatcher = OldDispatcher(prior, manifest, ledger, lambda: ScriptedTransport(tasks, fail_key=failed.key))
            execution = old_execute(tasks, manifest, dispatcher, OracleRunner(tasks), prior, 4)
            save_new(prior / "manifest.json", manifest)
            save_new(prior / "run_settings.json", {"live": False, "workers": 4})
            save_new(prior / "calibration.json", {"live": False, "rows": [], "excluded_from_study": True})
            save_new(prior / "execution.json", execution)
            save_new(prior / "analysis.json", old_analyze(tasks, execution, ledger.snapshot(), simulated=True))
            save_new(prior / "evidence_manifest.json", {"files": [
                {"path": p.relative_to(prior).as_posix(), "sha256": sha(p.read_bytes())} for p in sorted(prior.rglob("*.json"))],
                "ledger_sha256": sha((prior / "ledger.sqlite").read_bytes())})
            old_hash = sha((prior / "ledger.sqlite").read_bytes())
            prepare(bundle, prior, prepared)
            result = run(prepared, output, workers=4)
            self.assertFalse(result["stopped"])
            self.assertEqual(sha((prior / "ledger.sqlite").read_bytes()), old_hash)
            audited = audit(prepared, output)
            self.assertTrue(audited["all_passed"])
            self.assertEqual(audited["unknown_generations_reconciled"], 1)
            rows = read(output / "execution.json")["jobs"]
            missing = [r for r in rows if r["result"].get("score") is None]
            self.assertEqual(len(missing), 1)
            self.assertEqual(missing[0]["job"]["task_id"], failed.task_id)
            # Mutation must fail before it can be treated as a verified replay.
            response_path = next((output / "responses").glob("*.json"))
            response_path.write_text("{}", encoding="utf-8")
            with self.assertRaises(ValueError):
                audit(prepared, output)


if __name__ == "__main__":
    unittest.main()
