"""Dependency and concurrency invariants for both frozen v9 job shapes."""
from copy import deepcopy
import threading
import unittest

from experiments.dependency_memory.rollback_patch_v9.scheduler import execute
from experiments.dependency_memory.rollback_patch_v9.audit import verify_trace, ReplayMismatch


def jobs(count=2, calibration=False):
    result = []
    for index in range(count):
        task = "task-" + str(index)
        parent = task + ":prefix"
        result.append({"job_id": parent, "task_id": task, "arm": "prefix"})
        for arm in (("K0",) if calibration else ("RL", "K0", "KL", "R0")):
            result.append({"job_id": task + ":" + arm, "task_id": task,
                           "arm": arm, "depends_on": parent})
    return result


class FactorialSchedulerTests(unittest.TestCase):
    def run_jobs(self, planned, workers):
        persisted, called = set(), []
        lock = threading.Lock()

        def work(job):
            with lock:
                if job["arm"] != "prefix":
                    self.assertIn(job["depends_on"], persisted)
                called.append(job["job_id"])
            return job["job_id"]

        def completed(future, job):
            self.assertEqual(future.result(), job["job_id"])
            with lock:
                persisted.add(job["job_id"])

        trace = execute(planned, work, completed, workers)
        self.assertEqual(set(called), {job["job_id"] for job in planned})
        self.assertEqual(len(called), len(planned))
        self.assertTrue(verify_trace(trace, planned, workers)["passed"])
        return trace

    def test_all_four_arms_start_only_after_durable_parent(self):
        self.run_jobs(jobs(8), 8)

    def test_control_only_calibration_has_same_dependency_guarantee(self):
        self.run_jobs(jobs(8, calibration=True), 4)

    def test_single_worker_prioritizes_ready_children_in_frozen_order(self):
        planned = jobs(2)
        trace = self.run_jobs(planned, 1)
        self.assertEqual([row["job_id"] for row in trace["events"] if row["event"] == "submit"],
                         [job["job_id"] for job in planned])

    def test_thirty_two_worker_bound_is_reached_without_exceeding(self):
        planned = jobs(32)
        barrier = threading.Barrier(32)

        def work(job):
            if job["arm"] == "prefix":
                barrier.wait(timeout=10)
            return job["job_id"]

        trace = execute(planned, work, lambda future, job: future.result(), 32)
        checked = verify_trace(trace, planned, 32)
        self.assertEqual(checked["peak_active_jobs"], 32)
        self.assertEqual(checked["peak_outstanding_jobs"], 32)

    def test_callback_failure_never_releases_children(self):
        called = []

        def failed_persist(future, job):
            future.result()
            raise OSError("fixture disk failure")

        with self.assertRaisesRegex(OSError, "fixture disk failure"):
            execute(jobs(1), lambda job: called.append(job["arm"]), failed_persist, 1)
        self.assertEqual(called, ["prefix"])

    def test_rejects_incomplete_arms_wrong_parent_duplicates_and_unsafe_workers(self):
        invalid = [jobs(1)[:-1], jobs(1) + [jobs(1)[0]]]
        wrong_parent = jobs(1)
        wrong_parent[1]["depends_on"] = "unrelated-prefix"
        invalid.append(wrong_parent)
        for planned in invalid:
            with self.subTest(planned=planned), self.assertRaises(ValueError):
                execute(planned, lambda job: None, lambda future, job: None, 2)
        for workers in (0, 33, True, 1.5):
            with self.subTest(workers=workers), self.assertRaises(ValueError):
                execute(jobs(1), lambda job: None, lambda future, job: None, workers)

    def test_trace_rejects_missing_event_wrong_schema_and_changed_bound(self):
        planned = jobs(1)
        trace = self.run_jobs(planned, 2)
        for field, value in (("schema", "rollback-v8-dependency-scheduler-trace-v1"),
                             ("peak_active_workers", 999), ("events", trace["events"][:-1])):
            changed = deepcopy(trace)
            changed[field] = value
            with self.subTest(field=field), self.assertRaises(ReplayMismatch):
                verify_trace(changed, planned, 2)


if __name__ == "__main__":
    unittest.main()
