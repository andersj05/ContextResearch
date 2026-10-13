"""The scheduler proof is checked independently of its own summary fields."""
from copy import deepcopy
import unittest

from experiments.dependency_memory.rollback_parallel_v8.scheduler import execute
from experiments.dependency_memory.rollback_parallel_v8.trace_audit import verify_trace


class TraceTests(unittest.TestCase):
    def test_rejects_missing_duplicate_tampered_time_and_bound(self):
        jobs = [{"task_id": "a", "job_id": "p", "arm": "prefix"},
                {"task_id": "a", "job_id": "k", "arm": "K", "depends_on": "p"},
                {"task_id": "a", "job_id": "r", "arm": "R", "depends_on": "p"}]
        trace = execute(jobs, lambda job: job, lambda future, job: future.result(), 2)
        self.assertTrue(verify_trace(trace, jobs, 2)["passed"])
        for mutate in (lambda t: t["events"].pop(),
                       lambda t: t["events"].append(t["events"][-1]),
                       lambda t: t["events"][0].update(seconds=float("nan")),
                       lambda t: t.update(max_outstanding=999),
                       lambda t: t["jobs"][1].update(started_seconds=-1),
                       lambda t: t.update(completion_order=[])):
            bad = deepcopy(trace)
            mutate(bad)
            with self.assertRaises(ValueError):
                verify_trace(bad, jobs, 2)


if __name__ == "__main__":
    unittest.main()
