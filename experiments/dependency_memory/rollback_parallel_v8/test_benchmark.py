"""Independent small-schedule checks and sealed-timing import controls."""
from datetime import datetime, timedelta, timezone
from contextlib import closing
from hashlib import sha256
import json
from pathlib import Path
import sqlite3
import tempfile
import unittest

from experiments.dependency_memory.rollback_parallel_v8.benchmark import (
    compare_recorded, load_recorded_workload, simulate, sleep_workload,
)


def small_jobs():
    # With two workers the barrier schedule finishes at 16; priority pipeline
    # finishes at 12. A single worker necessarily performs all 23 service units.
    return [
        {"job_id": "a", "task_id": "a", "arm": "prefix", "duration_seconds": 1.0},
        {"job_id": "aK", "task_id": "a", "arm": "K", "depends_on": "a", "duration_seconds": 5.0},
        {"job_id": "aR", "task_id": "a", "arm": "R", "depends_on": "a", "duration_seconds": 5.0},
        {"job_id": "b", "task_id": "b", "arm": "prefix", "duration_seconds": 10.0},
        {"job_id": "bK", "task_id": "b", "arm": "K", "depends_on": "b", "duration_seconds": 1.0},
        {"job_id": "bR", "task_id": "b", "arm": "R", "depends_on": "b", "duration_seconds": 1.0},
    ]


def temporary_directory():
    # The desktop Windows sandbox's redirected system TEMP may deny SQLite
    # writes; an isolated workspace temporary directory has the intended ACL.
    root = Path(__file__).resolve().parents[3] / "tmp"
    root.mkdir(exist_ok=True)
    return tempfile.TemporaryDirectory(prefix="rollback-v8-timing-", dir=root)


def sealed_fixture(folder):
    folder = Path(folder)
    nodes = small_jobs()
    jobs = [{key: value for key, value in node.items() if key != "duration_seconds"} for node in nodes]
    origin = datetime(2026, 10, 13, tzinfo=timezone.utc)
    intervals = {"a": (0, 1), "b": (0, 10), "aK": (10, 15), "aR": (10, 15),
                 "bK": (15, 16), "bR": (15, 16)}
    calls = []
    events = []
    for node in nodes:
        start, end = intervals[node["job_id"]]
        stamp = lambda seconds: (origin + timedelta(seconds=seconds)).isoformat()
        call_id = "call-" + node["job_id"]
        complete = {"completed_utc": stamp(end)}
        calls.append(dict(complete, call_id=call_id, state="completed", elapsed_seconds=end - start,
                          identity={"task_id": node["task_id"], "arm": node["arm"]}))
        events.extend([(start, call_id, "dispatched", {"admitted_utc": stamp(start)}),
                       (end, call_id, "completed", complete)])
    with closing(sqlite3.connect(folder / "ledger.sqlite")) as connection:
        connection.execute("CREATE TABLE events(seq INTEGER PRIMARY KEY,call_id TEXT,state TEXT,payload TEXT)")
        for seq, (_, call_id, state, payload) in enumerate(sorted(events), 1):
            connection.execute("INSERT INTO events VALUES(?,?,?,?)", (seq, call_id, state, json.dumps(payload)))
        connection.commit()
    contents = {"accounting.json": {"stop": None, "calls": calls},
                "manifest.json": {"jobs": jobs}, "execution.json": {"wall_seconds": 16.2},
                "run_settings.json": {"workers": 2}}
    for name, data in contents.items():
        (folder / name).write_text(json.dumps(data), encoding="utf-8")
    evidence = {"files": [{"path": name, "sha256": sha256((folder / name).read_bytes()).hexdigest()}
                           for name in contents],
                "ledger_sha256": sha256((folder / "ledger.sqlite").read_bytes()).hexdigest()}
    (folder / "evidence_manifest.json").write_text(json.dumps(evidence), encoding="utf-8")


class TimingReplayTests(unittest.TestCase):
    def test_hand_calculated_phase_barrier_and_pipeline(self):
        barrier = simulate(small_jobs(), 2, policy="two_phase")
        pipeline = simulate(small_jobs(), 2, policy="pipeline")
        self.assertEqual(barrier["makespan_seconds"], 16)
        self.assertEqual(pipeline["makespan_seconds"], 12)
        self.assertEqual(pipeline["busy_worker_seconds"], 23)
        self.assertEqual(pipeline["idle_worker_seconds"], 1)
        traced = {row["job_id"]: row for row in pipeline["trace"]}
        self.assertEqual(traced["aK"]["start_seconds"], 1)
        self.assertEqual(traced["aR"]["start_seconds"], 6)
        self.assertEqual(traced["bK"]["start_seconds"], 10)

    def test_one_worker_has_no_parallel_speedup(self):
        for policy in ("pipeline", "two_phase"):
            result = simulate(small_jobs(), 1, policy=policy)
            self.assertEqual(result["makespan_seconds"], 23)
            self.assertEqual(result["utilization"], 1)
            self.assertEqual(result["peak_active_jobs"], 1)

    def test_unlimited_workers_still_preserve_dependency_critical_path(self):
        result = simulate(small_jobs(), 32)
        # Long prefix B takes ten; its dependent one-unit arms finish at eleven.
        self.assertEqual(result["makespan_seconds"], 11)
        trace = {row["job_id"]: row for row in result["trace"]}
        for node in small_jobs():
            if node.get("depends_on"):
                self.assertGreaterEqual(trace[node["job_id"]]["start_seconds"],
                                        trace[node["depends_on"]]["finish_seconds"])

    def test_zero_call_dispositions_are_included_without_service(self):
        nodes = small_jobs()
        for node in nodes:
            node["duration_seconds"] = 0
        result = simulate(nodes, 2)
        self.assertEqual(result["makespan_seconds"], 0)
        self.assertEqual(len(result["trace"]), 6)
        self.assertEqual(result["peak_active_jobs"], 0)

    def test_tie_priority_prefers_ready_continuation(self):
        nodes = small_jobs()
        nodes.extend([
            {"job_id": "c", "task_id": "c", "arm": "prefix", "duration_seconds": 1.0},
            {"job_id": "cK", "task_id": "c", "arm": "K", "depends_on": "c", "duration_seconds": 0.0},
            {"job_id": "cR", "task_id": "c", "arm": "R", "depends_on": "c", "duration_seconds": 0.0},
        ])
        trace = {row["job_id"]: row for row in simulate(nodes, 2)["trace"]}
        self.assertEqual(trace["aK"]["start_seconds"], 1)
        self.assertGreater(trace["c"]["start_seconds"], trace["aK"]["start_seconds"])

    def test_invalid_dependency_and_durations_rejected(self):
        for value in (-1, float("nan"), float("inf")):
            nodes = small_jobs()
            nodes[0]["duration_seconds"] = value
            with self.assertRaises(ValueError):
                simulate(nodes, 2)
        nodes = small_jobs()
        nodes[1]["depends_on"] = "b"
        with self.assertRaises(ValueError):
            simulate(nodes, 2)

    def test_sealed_fixture_import_recovers_observed_timing(self):
        with temporary_directory() as tmp:
            sealed_fixture(tmp)
            workload = load_recorded_workload(tmp)
            observed = workload["observed"]
            self.assertEqual(observed["admission_to_completion_envelope_seconds"], 16)
            self.assertEqual(observed["summed_job_span_seconds"], 23)
            self.assertEqual(observed["peak_admitted_calls"], 2)
            self.assertEqual(observed["phase_details"]["prefix"]["idle_worker_seconds"], 9)
            self.assertEqual(observed["intra_job_outside_admitted_interval_worker_seconds"], 0)
            comparison = compare_recorded(workload, (2,))
            self.assertAlmostEqual(comparison["baseline_replay_vs_observed_controller_seconds"]["observed_minus_replay"], 0.2)
            self.assertEqual(comparison["model_calls"], 0)
            self.assertEqual(comparison["comparisons"][1]["speedup_vs_replayed_original_policy"], 16 / 12)

    def test_timing_json_tamper_is_rejected(self):
        with temporary_directory() as tmp:
            sealed_fixture(tmp)
            (Path(tmp) / "execution.json").write_text('{"wall_seconds": 1}', encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "evidence seal"):
                load_recorded_workload(tmp)

    def test_timing_ledger_tamper_is_rejected(self):
        with temporary_directory() as tmp:
            sealed_fixture(tmp)
            with closing(sqlite3.connect(Path(tmp) / "ledger.sqlite")) as connection:
                connection.execute("DELETE FROM events WHERE seq=1")
                connection.commit()
            with self.assertRaisesRegex(ValueError, "evidence seal"):
                load_recorded_workload(tmp)

    def test_executable_sleep_workload_respects_dependencies_and_capacity(self):
        for policy in ("two_phase", "pipeline"):
            result = sleep_workload(small_jobs(), 2, policy=policy, time_scale=0.002)
            self.assertEqual(result["jobs_completed"], 6)
            self.assertLessEqual(result["peak_active_workers"], 2)
            self.assertTrue(result["dependency_persistence_checked"])
            self.assertTrue(result["at_most_once_checked"])
            self.assertEqual(result["model_calls"], 0)
            self.assertEqual(result["evidence_kind"], "executed_local_scaled_sleep_workload")
            for node in small_jobs():
                if node.get("depends_on"):
                    self.assertGreaterEqual(result["intervals"][node["job_id"]]["start_seconds"],
                                            result["intervals"][node["depends_on"]]["end_seconds"])


if __name__ == "__main__":
    unittest.main()
