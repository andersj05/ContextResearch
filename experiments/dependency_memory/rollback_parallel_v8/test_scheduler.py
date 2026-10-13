"""Real-thread invariants for dependency release, boundedness and dispositions."""

from collections import Counter
from copy import deepcopy
import threading
import unittest

from experiments.dependency_memory.rollback_parallel_v8.scheduler import execute


def jobs_for(count, *, reverse_first_pair=False):
    jobs = []
    for index in range(count):
        task_id = "task-" + str(index)
        prefix_id = task_id + "-prefix"
        jobs.append({"job_id": prefix_id, "task_id": task_id, "arm": "prefix"})
        arms = ("R", "K") if reverse_first_pair and index == 0 else ("K", "R")
        jobs.extend({"job_id": task_id + "-" + arm, "task_id": task_id,
                     "arm": arm, "depends_on": prefix_id} for arm in arms)
    return jobs


class DependencySchedulerTests(unittest.TestCase):
    def assert_trace(self, trace, jobs, workers):
        identities = {job["job_id"] for job in jobs}
        self.assertEqual(trace["jobs_completed"], len(jobs))
        self.assertEqual(trace["jobs_total"], len(jobs))
        self.assertEqual(set(trace["completion_order"]), identities)
        self.assertEqual(len(trace["completion_order"]), len(jobs))
        self.assertLessEqual(trace["peak_active_workers"], workers)
        self.assertLessEqual(trace["max_outstanding"], workers)
        rows = {row["job_id"]: row for row in trace["jobs"]}
        self.assertEqual(set(rows), identities)
        self.assertEqual([row["job_id"] for row in trace["jobs"]], [j["job_id"] for j in jobs])
        for row in rows.values():
            self.assertLessEqual(row["submitted_seconds"], row["started_seconds"])
            self.assertLessEqual(row["started_seconds"], row["finished_seconds"])
            self.assertLessEqual(row["finished_seconds"], row["completed_seconds"])
            self.assertLessEqual(row["completed_seconds"], trace["wall_seconds"])
            if row["depends_on"]:
                self.assertLessEqual(rows[row["depends_on"]]["completed_seconds"], row["submitted_seconds"])
        expected = Counter((job["job_id"], kind) for job in jobs
                           for kind in ("submit", "start", "finish", "persisted"))
        self.assertEqual(Counter((e["job_id"], e["event"]) for e in trace["events"]), expected)
        times = [e["seconds"] for e in trace["events"]]
        self.assertEqual(times, sorted(times))
        active = outstanding = 0
        maximum_active = maximum_outstanding = 0
        for event in trace["events"]:
            if event["event"] == "submit":
                outstanding += 1
                maximum_outstanding = max(maximum_outstanding, outstanding)
            elif event["event"] == "persisted":
                outstanding -= 1
            elif event["event"] == "start":
                active += 1
                maximum_active = max(maximum_active, active)
            elif event["event"] == "finish":
                active -= 1
            self.assertGreaterEqual(active, 0)
            self.assertGreaterEqual(outstanding, 0)
        self.assertEqual((active, outstanding), (0, 0))
        self.assertEqual(maximum_active, trace["peak_active_workers"])
        self.assertEqual(maximum_outstanding, trace["max_outstanding"])

    def test_continuation_runs_while_unrelated_prefix_is_still_blocked(self):
        # A phase barrier cannot complete this dependency-free workload: the
        # intentionally slow prefix waits for the other task's continuation.
        jobs = jobs_for(2)
        continuation_started = threading.Event()
        published = {}
        lock = threading.Lock()

        def work(job):
            if job["arm"] == "prefix" and job["task_id"] == "task-0":
                if not continuation_started.wait(timeout=10):
                    raise AssertionError("continuation blocked behind unrelated prefix")
            if job["arm"] != "prefix":
                with lock:
                    self.assertEqual(published[job["task_id"]], "durable-prefix")
                if job["task_id"] == "task-1":
                    continuation_started.set()
            return "durable-prefix" if job["arm"] == "prefix" else "complete"

        def save(future, job):
            result = future.result()
            if job["arm"] == "prefix":
                with lock:
                    published[job["task_id"]] = result

        trace = execute(jobs, work, save, 2)
        self.assert_trace(trace, jobs, 2)
        self.assertGreaterEqual(trace["continuation_started_before_all_prefixes_persisted"], 1)

    def test_ready_pair_precedes_unstarted_prefix_and_keeps_frozen_arm_order(self):
        jobs = jobs_for(3, reverse_first_pair=True)
        started = []
        trace = execute(jobs, lambda job: started.append(job["job_id"]),
                        lambda future, job: future.result(), 1)
        self.assertEqual(started, [job["job_id"] for job in jobs])
        self.assertEqual(started[1:3], ["task-0-R", "task-0-K"])
        self.assert_trace(trace, jobs, 1)

    def test_sixteen_and_thirty_two_actual_workers_without_duplicate_jobs(self):
        for workers in (16, 32):
            with self.subTest(workers=workers):
                jobs = jobs_for(workers + 3)
                gate = threading.Barrier(workers)
                started, lock = Counter(), threading.Lock()

                def work(job):
                    with lock:
                        started[job["job_id"]] += 1
                    if job["arm"] == "prefix" and int(job["task_id"].split("-")[1]) < workers:
                        gate.wait(timeout=10)
                    return job["job_id"]

                trace = execute(jobs, work, lambda future, job: future.result(), workers)
                self.assertEqual(started, Counter(job["job_id"] for job in jobs))
                self.assertEqual(trace["peak_active_workers"], workers)
                self.assertEqual(trace["max_outstanding"], workers)
                self.assert_trace(trace, jobs, workers)

    def test_unknown_prefix_still_materializes_both_skips_without_retry(self):
        jobs = jobs_for(4)
        published, dispositions, attempts = {}, {}, Counter()
        lock = threading.Lock()

        def work(job):
            with lock:
                attempts[job["job_id"]] += 1
                if job["arm"] == "prefix":
                    return {"eligible": job["task_id"] != "task-0"}
                return "complete" if published[job["task_id"]]["eligible"] else "not_eligible:unknown_dispatch"

        def save(future, job):
            value = future.result()
            with lock:
                if job["arm"] == "prefix":
                    published[job["task_id"]] = value
                dispositions[job["job_id"]] = value

        trace = execute(jobs, work, save, 4)
        self.assertEqual(len(dispositions), len(jobs))
        self.assertEqual(dispositions["task-0-K"], "not_eligible:unknown_dispatch")
        self.assertEqual(dispositions["task-0-R"], "not_eligible:unknown_dispatch")
        self.assertEqual(dispositions["task-3-K"], "complete")
        self.assertEqual(set(attempts.values()), {1})
        self.assert_trace(trace, jobs, 4)

    def test_one_arm_error_is_callback_owned_and_does_not_drop_other_dispositions(self):
        jobs = jobs_for(2)
        saved, attempted = {}, Counter()

        def work(job):
            attempted[job["job_id"]] += 1
            if job["job_id"] == "task-0-R":
                raise RuntimeError("synthetic unknown outcome")
            return "complete"

        def save(future, job):
            try:
                saved[job["job_id"]] = future.result()
            except RuntimeError:
                saved[job["job_id"]] = "unknown_dispatch"

        trace = execute(jobs, work, save, 2)
        self.assertEqual(saved["task-0-R"], "unknown_dispatch")
        self.assertEqual(saved["task-0-K"], "complete")
        self.assertEqual(saved["task-1-R"], "complete")
        self.assertEqual(len(saved), len(jobs))
        self.assertEqual(set(attempted.values()), {1})
        self.assert_trace(trace, jobs, 2)

    def test_failed_persistence_never_releases_children(self):
        jobs = jobs_for(1)
        attempted = []

        def fail_save(future, job):
            future.result()
            raise OSError("synthetic evidence failure")

        with self.assertRaisesRegex(OSError, "evidence failure"):
            execute(jobs, lambda job: attempted.append(job["job_id"]), fail_save, 1)
        self.assertEqual(attempted, ["task-0-prefix"])

    def test_global_admission_stop_keeps_fixed_job_dispositions(self):
        # A scheduler must not silently omit jobs when the authoritative ledger
        # stops. This fixture models that ledger's admission guard independently.
        jobs = jobs_for(3)
        stopped = threading.Event()
        admitted, saved = [], {}

        def work(job):
            if stopped.is_set():
                return "infrastructure_stop"
            admitted.append(job["job_id"])
            stopped.set()
            return "systemic_fault"

        def save(future, job):
            saved[job["job_id"]] = future.result()

        trace = execute(jobs, work, save, 1)
        self.assertEqual(admitted, ["task-0-prefix"])
        self.assertEqual(len(saved), len(jobs))
        self.assertEqual(sum(value == "infrastructure_stop" for value in saved.values()), len(jobs) - 1)
        self.assert_trace(trace, jobs, 1)

    def test_invalid_schedule_rejected_before_any_submission(self):
        valid = jobs_for(2)
        bad = []
        duplicate = deepcopy(valid)
        duplicate[1]["job_id"] = duplicate[0]["job_id"]
        bad.append(duplicate)
        cross_task = deepcopy(valid)
        cross_task[1]["depends_on"] = cross_task[3]["job_id"]
        bad.append(cross_task)
        cyclic = deepcopy(valid)
        cyclic[0]["depends_on"] = cyclic[1]["job_id"]
        bad.append(cyclic)
        bad.append(valid[:-1])
        wrong_arm = deepcopy(valid)
        wrong_arm[1]["arm"] = "other"
        bad.append(wrong_arm)
        for jobs in bad:
            with self.subTest(jobs=jobs), self.assertRaises(ValueError):
                execute(jobs, lambda job: self.fail("invalid job dispatched"), lambda future, job: None, 2)
        for workers in (0, 33, -1, 1.0, True):
            with self.subTest(workers=workers), self.assertRaises(ValueError):
                execute(valid, lambda job: self.fail("invalid pool created"), lambda future, job: None, workers)

    def test_empty_schedule_and_submission_notifications(self):
        empty = execute([], lambda job: None, lambda future, job: None, 16)
        self.assertEqual(empty["events"], [])
        self.assertEqual(empty["jobs_completed"], 0)
        self.assertEqual(empty["peak_active_workers"], 0)
        jobs = jobs_for(1)
        notified = []
        trace = execute(jobs, lambda job: None, lambda future, job: future.result(), 2,
                        on_submitted=lambda job: notified.append(job["job_id"]))
        self.assertEqual(Counter(notified), Counter(job["job_id"] for job in jobs))
        self.assert_trace(trace, jobs, 2)


if __name__ == "__main__":
    unittest.main()
