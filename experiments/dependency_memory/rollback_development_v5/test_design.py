"""Scientific invariants and concurrency failures, not scored model trials."""
import copy
import json
from pathlib import Path
import tempfile
import threading
from concurrent.futures import ThreadPoolExecutor
import unittest
from contextlib import contextmanager

from .common import ROOT, STUDY, sha, wire
from .tasks import generate, requirements, public_check
from .contexts import render, actor_state, parse_action, parse_writer, fits
from .engine import initial_state, apply_intervention, run_episode, run_prefix
from .simulation import ScriptedTransport, OracleRunner, bad_candidate
from .accounting import Identity, Ledger, Stopped
from .dispatch import Dispatcher
from .schedule import jobs, identities, generation_bound, execute
from .analysis import comparison, analyze
from .verification import independent_math, check_math
from .coding_tasks import batch_program, run_tests
from ..rollback_pilot.subscription.accounting import Usage


@contextmanager
def temporary_workspace():
    parent = (ROOT / "tmp" / "rollback-v5-tests").resolve()
    parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(dir=parent) as folder:
        if Path(folder).resolve().parent != parent:
            raise ValueError("test scratch escaped workspace")
        yield folder


class DesignTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tasks = generate()
        cls.runner = OracleRunner(cls.tasks)

    def selected(self, family="scheduling", horizon="long"):
        return next(t for t in self.tasks if t["family"] == family and t["horizon"] == horizon)

    def test_factorial_balance_and_unique_seeded_instances(self):
        from collections import Counter
        self.assertEqual(len(self.tasks), 48)
        self.assertEqual(set(Counter((t["family"], t["horizon"], t["difficulty"]) for t in self.tasks).values()), {2})
        self.assertEqual(len({t["sha256"] for t in self.tasks}), 48)
        self.assertEqual(len({t["evaluator"]["seed"] for t in self.tasks}), 48)

    def test_generator_reproducible_and_hashes_bind_every_field(self):
        self.assertEqual(self.tasks, generate())
        for t in self.tasks:
            self.assertEqual(t["sha256"], sha({k: v for k, v in t.items() if k != "sha256"}))

    def test_horizon_and_difficulty_have_explicit_distinct_controls(self):
        for t in self.tasks:
            expected = {"short": (2, 1), "medium": (10, 4), "long": (30, 8)}[t["horizon"]]
            self.assertEqual((t["action_allowance"], len(t["stages"])), expected)
            self.assertTrue(all(p["requirements"] for p in t["stages"]))

    def test_private_and_future_mutations_cannot_change_current_request(self):
        for t in self.tasks:
            state = initial_state(t); before = render(t, state).json_text
            modified = copy.deepcopy(t); modified["evaluator"] = {"secret": "PRIVATE_SENTINEL"}
            if len(t["stages"]) > 1:
                modified["stages"][-1] = {"requirements": [{"secret": "FUTURE_SENTINEL"}]}
            self.assertEqual(before, render(modified, state).json_text)
            self.assertNotIn("reserved_tests", before)

    def test_K_R_initial_inputs_differ_only_in_raw_history(self):
        t = self.selected(); s = initial_state(t)
        s["history"] = [{"public": "old observation"}]; s["feedback"] = {"status": "public_mismatch"}
        lesson = {"established": ["one candidate failed"], "retained_observations": [], "uncertainties": ["unverified alternative"]}
        k, r = copy.deepcopy(s), copy.deepcopy(s)
        apply_intervention(k, "K", lesson); apply_intervention(r, "R", lesson)
        a, b = actor_state(t, k), actor_state(t, r)
        self.assertEqual([key for key in a if a[key] != b[key]], ["history"])
        self.assertEqual(k["artifact"], r["artifact"])
        self.assertEqual(render(t, k).data()["messages"][0], render(t, r).data()["messages"][0])

    def test_evidence_lesson_factor_keeps_K_R_contrast_identical(self):
        t = self.selected(); s = initial_state(t)
        s["history"] = [{"speculation": "unverified"}]; s["feedback"] = {"status": "public_mismatch", "check": "window-0"}
        a, b = copy.deepcopy(s), copy.deepcopy(s)
        apply_intervention(a, "KE"); apply_intervention(b, "RE")
        aa, bb = actor_state(t, a), actor_state(t, b)
        self.assertEqual([k for k in aa if aa[k] != bb[k]], ["history"])
        self.assertEqual(a["memory"][0]["content"]["uncertainties"], [])

    def test_fresh_restart_has_all_released_requirements_and_no_trials(self):
        t = self.selected(); s = initial_state(t); s["stage"] = 2
        s["history"] = [{"sentinel": "FAILED_TRIAL"}]; s["memory"] = ["UNVERIFIED_LESSON"]
        a = actor_state(t, s, "F")
        self.assertEqual(len(a["public_dossier"]), 3)
        self.assertEqual(a["history"], []); self.assertEqual(a["memory"], [])
        self.assertIsNone(a["feedback"])
        self.assertNotIn("FAILED_TRIAL", wire(a))

    def test_all_math_references_pass_independent_formulation_at_all_stages(self):
        for t in self.tasks:
            if t["domain"] != "math": continue
            for stage in range(len(t["stages"])):
                self.assertTrue(independent_math(t, t["evaluator"]["reference"], requirements(t, stage)))
                self.assertEqual(public_check(t, stage, t["evaluator"]["reference"])["status"], "public_pass")

    def test_exhaustive_small_routes_agree_with_production(self):
        t = next(t for t in self.tasks if t["family"] == "routing" and t["difficulty"] == "moderate")
        result = check_math(t)
        self.assertTrue(result["exhaustive_routes"])
        self.assertGreater(result["final_route_solutions"], 0)

    def test_source_paths_and_boolean_integer_candidates_are_rejected(self):
        t = self.selected("ledger"); c = copy.deepcopy(t["evaluator"]["reference"])
        c["files"][0]["path"] = "../secret.py"
        with self.assertRaises(ValueError): batch_program(c)
        with self.assertRaises(ValueError): parse_action({"status": "candidate", "candidate": {"values": [True], "order": [], "files": []}, "note": ""})

    def test_writer_overflow_and_continue_with_candidate_fail(self):
        with self.assertRaises(ValueError): parse_writer(wire({"summary": "x" * 5000}), "summary")
        with self.assertRaises(ValueError): parse_action({"status": "continue", "candidate": {"values": [1], "order": [], "files": []}, "note": ""})

    def test_ambiguous_duplicate_json_fields_are_not_silently_accepted(self):
        with self.assertRaises(ValueError): parse_writer('{"summary":"first","summary":"second"}', "summary")

    def test_frozen_bundle_binds_readable_catalog_and_retained_source(self):
        from .prepare import prepare, check_bundle
        with temporary_workspace() as folder:
            bundle = Path(folder) / "prepared"
            prepare(bundle, tracks=("policy",))
            self.assertEqual(len(check_bundle(bundle)[1]), 48)
            catalog = bundle / "TASK_CATALOG.md"; original = catalog.read_bytes()
            catalog.write_bytes(original + b"altered")
            with self.assertRaisesRegex(ValueError, "catalog changed"): check_bundle(bundle)
            catalog.write_bytes(original)
            with (bundle / "source_snapshot.zip").open("ab") as stream: stream.write(b"altered")
            with self.assertRaisesRegex(ValueError, "snapshot changed"): check_bundle(bundle)

    def test_every_stage_uses_medium_and_initial_requests_fit(self):
        for t in self.tasks:
            for kind in ("action", "lesson", "summary", "compress"):
                req = render(t, initial_state(t), kind)
                self.assertEqual(req.data()["settings"]["reasoning_effort"], "medium")
                self.assertTrue(fits(req))

    def test_perfect_actor_can_finish_early_without_padding(self):
        t = self.selected()
        actor = ScriptedTransport([t], inject_failures=False)
        result = run_episode(t, "policy", "K", actor.generate, self.runner)
        self.assertEqual(result["score"], 1)
        self.assertEqual(result["actions_used"], 8)
        self.assertLess(result["actions_used"], t["action_allowance"])

    def test_short_control_has_room_for_real_recovery(self):
        t = self.selected(horizon="short"); actor = ScriptedTransport([t])
        prefix = run_prefix(t, actor.generate, self.runner)
        self.assertTrue(prefix["eligible"])
        for arm in ("K", "R", "Z", "G", "F", "KE", "RE"):
            result = run_episode(t, "mechanism", arm, actor.generate, self.runner, prefix["state"], prefix["shared"])
            self.assertEqual(result["score"], 1)
        self.assertEqual(prefix["state"]["used"], 1)
        self.assertTrue(prefix["state"]["history"])

    def test_repeated_compression_is_separate_and_counted(self):
        t = self.selected(); actor = ScriptedTransport([t], inject_failures=False)
        plain = run_episode(t, "policy", "K", actor.generate, self.runner)
        compressed = run_episode(t, "memory", "K", actor.generate, self.runner)
        self.assertEqual(plain["compression_count"], 0)
        self.assertEqual(compressed["compression_count"], 2)
        self.assertEqual(len(compressed["call_ids"]) - len(plain["call_ids"]), 2)

    def test_frozen_schedule_has_no_duplicate_or_shared_call_identity(self):
        ids = identities(self.tasks)
        self.assertEqual(len({i.key for i in ids}), len(ids))
        self.assertEqual(len(jobs(self.tasks)), 48 * 16)
        self.assertEqual(generation_bound(self.tasks), 13632)

    def test_unknowns_preserve_fixed_denominator_bounds(self):
        rows = [{"task_id": "a", "arm": "R", "score": 1}, {"task_id": "a", "arm": "K", "score": None}]
        result = comparison(rows, "R", "K")
        self.assertEqual(result["complete_pairs"], 0)
        self.assertEqual(result["fixed_denominator_missingness_bounds"], [0, 1])


class AccountingTests(unittest.TestCase):
    def make_id(self, step):
        return Identity(STUDY, "fixture", "policy", "K", step, "action")

    def test_concurrent_admission_is_bounded_and_duplicate_safe(self):
        with temporary_workspace() as folder:
            ids = [self.make_id(i) for i in range(9)]
            ledger = Ledger(Path(folder) / "ledger.sqlite", ids, 8)
            with ThreadPoolExecutor(max_workers=8) as pool:
                list(pool.map(lambda i: ledger.admit(i, "bound"), ids[:8]))
            with self.assertRaises(ValueError): ledger.admit(ids[8], "bound")
            with self.assertRaises(ValueError): ledger.admit(ids[0], "bound")
            for i in ids[:8]: ledger.complete(i, Usage(10, 0, 3, 1), {"thread_id": i.key}, 0)
            self.assertEqual(ledger.snapshot()["completed_calls"], 8)

    def test_unknown_stops_new_work_and_drain_keeps_other_usage(self):
        with temporary_workspace() as folder:
            ids = [self.make_id(i) for i in range(3)]
            ledger = Ledger(Path(folder) / "ledger.sqlite", ids, 2)
            for i in ids[:2]: ledger.admit(i, "bound")
            ledger.unknown(ids[0], "timeout")
            with self.assertRaises(Stopped): ledger.admit(ids[2], "bound")
            ledger.complete(ids[1], Usage(10, 0, 3, 1), {"thread_id": ids[1].key}, 0)
            snapshot = ledger.snapshot()
            self.assertEqual(snapshot["unknown_or_inflight_calls"], 1)
            self.assertEqual(snapshot["completed_calls"], 1)
            self.assertNotEqual(snapshot["locked_planning_credits"], "0")

    def test_existing_dispatch_cannot_be_reopened_or_retried(self):
        with temporary_workspace() as folder:
            path = Path(folder) / "ledger.sqlite"; ids = [self.make_id(1)]
            ledger = Ledger(path, ids, 1); ledger.admit(ids[0], "bound")
            with self.assertRaises(ValueError): Ledger(path, ids, 1)

    def test_missing_usage_and_reused_provider_thread_are_not_completed(self):
        with temporary_workspace() as folder:
            ids = [self.make_id(i) for i in range(2)]
            ledger = Ledger(Path(folder) / "ledger.sqlite", ids, 2)
            for i in ids: ledger.admit(i, "bound")
            with self.assertRaises(ValueError): ledger.complete(ids[0], None, {}, 0)
            with self.assertRaises(ValueError): ledger.complete(ids[0], Usage(1, 0, 1, 0), {}, 0)
            ledger.complete(ids[0], Usage(1, 0, 1, 0), {"thread_id": "same"}, 0)
            with self.assertRaises(ValueError): ledger.complete(ids[1], Usage(1, 0, 1, 0), {"thread_id": "same"}, 0)

    def test_report_charges_received_work_even_when_episode_state_is_missing(self):
        from .audit import reconcile_report, ReplayMismatch
        task = generate()[0]
        identity = Identity(STUDY, task["task_id"], "policy", "K", 1, "action")
        with temporary_workspace() as folder:
            ledger = Ledger(Path(folder) / "ledger.sqlite", [identity], 1)
            ledger.admit(identity, "request")
            ledger.complete(identity, Usage(10, 0, 3, 1), {"thread_id": "fixture"}, 0)
            ledger.stop("grader_unavailable")
            execution = {"jobs": [{"job": {"task_id": task["task_id"], "track": "policy", "arm": "K"},
                                   "result": {"score": None, "disposition": "infrastructure_error"}}],
                         "worker_count": 1, "peak_active_jobs": 1, "wall_seconds": 0, "stopped": True}
            accounting = ledger.snapshot()
            report = analyze([task], execution, accounting, simulated=True)
            arm = report["tracks"]["policy"]["conditions"]["K"]
            self.assertEqual((arm["recorded_calls"], arm["input_tokens"], arm["known"]), (1, 10, 0))
            reconcile_report([task], execution, report, accounting["calls"], accounting["stop"], True)
            arm["correct"] = 1
            with self.assertRaisesRegex(ReplayMismatch, "analysis differs"):
                reconcile_report([task], execution, report, accounting["calls"], accounting["stop"], True)


class ParallelTests(unittest.TestCase):
    def test_scheduler_overlaps_independent_tasks_and_forks_only_after_shared_prefix(self):
        tasks = [t for t in generate() if t["domain"] == "math" and t["horizon"] == "short"][:4]
        tracks = ("mechanism", "policy")
        with temporary_workspace() as folder:
            folder = Path(folder); manifest = {"jobs": jobs(tasks, tracks), "source_bindings": []}
            ledger = Ledger(folder / "ledger.sqlite", identities(tasks, tracks), 4)
            dispatcher = Dispatcher(folder, manifest, ledger, lambda: ScriptedTransport(tasks, delay=.01))
            result = execute(tasks, manifest, dispatcher, OracleRunner(tasks), folder, 4)
            self.assertEqual(result["peak_active_jobs"], 4)
            self.assertFalse(result["stopped"])
            self.assertEqual(len(result["jobs"]), len(manifest["jobs"]))
            self.assertEqual(ledger.snapshot()["unknown_or_inflight_calls"], 0)
            for row in result["jobs"]:
                if row["job"]["dependency"]:
                    self.assertEqual(row["result"]["score"], 1)

    def test_parallel_unknown_does_not_start_another_job_or_erase_inflight(self):
        tasks = [t for t in generate() if t["domain"] == "math" and t["horizon"] == "short"][:4]
        tracks = ("policy",)
        planned = jobs(tasks, tracks); first = planned[0]
        fail = Identity(STUDY, first["task_id"], first["track"], first["arm"], 1, "action").key
        with temporary_workspace() as folder:
            folder = Path(folder); manifest = {"jobs": planned, "source_bindings": []}
            ledger = Ledger(folder / "ledger.sqlite", identities(tasks, tracks), 4)
            dispatcher = Dispatcher(folder, manifest, ledger, lambda: ScriptedTransport(tasks, fail_key=fail, delay=.02))
            result = execute(tasks, manifest, dispatcher, OracleRunner(tasks), folder, 4)
            self.assertTrue(result["stopped"])
            snapshot = ledger.snapshot()
            self.assertEqual(snapshot["unknown_or_inflight_calls"], 1)
            from .audit import ledger_rows
            _, events, _ = ledger_rows(folder / "ledger.sqlite")
            first_unknown = next(i for i, e in enumerate(events) if e["state"] == "unknown")
            self.assertFalse(any(e["state"] == "dispatched" for e in events[first_unknown + 1:]))
            self.assertEqual(len(result["jobs"]), len(planned))
            self.assertTrue(any(r["result"]["disposition"] == "unstarted_global_stop" for r in result["jobs"]))


if __name__ == "__main__":
    unittest.main()
